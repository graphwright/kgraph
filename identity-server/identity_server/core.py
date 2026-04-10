"""Postgres-backed implementation of the identity server.

This module provides ``PostgresIdentityServer``, the reference implementation
of the identity server interface.  It uses SQLModel ``Session`` and the
``Entity`` ORM model in ``db_models``, and delegates all domain-specific
logic to a ``DomainClient`` HTTP client.

Locking strategy (mirrors CONCURRENCY.md):
  - resolve:  ``INSERT ... ON CONFLICT DO NOTHING`` — Postgres serialises
              concurrent inserts on the same entity_id naturally.
  - promote:  ``SELECT ... FOR UPDATE`` on the entity row, then conditional
              update inside the same transaction.
  - merge:    Postgres advisory lock keyed on the sorted frozenset of entity
              IDs prevents two workers merging the same pair in opposite orders.
  - on_entity_added: called synchronously inside the same session as the
              triggering entity write; synonym detection is read-only and fires
              only after the row is durable.

Synonym detection uses the ``embedding`` JSON column on the ``Entity`` table
via in-process cosine similarity for now.  Once pgvector is activated on the
column the ``find_synonyms`` implementation can be swapped to a native vector
query with no interface change.

Authority-lookup caching uses Redis when a client is provided.  If Redis is
unavailable the server degrades gracefully to uncached lookups.  See
``AuthorityCache`` in ``cache.py``.
"""

import hashlib
import json
import logging
import math
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import text
from sqlmodel import Session, select

from .cache import AuthorityCache, _NEGATIVE_SENTINEL
from .db_models import Entity
from .domain_client import DomainClient
from .models import DomainCandidateEntity

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# EntityStatus — copied from kgschema so this package is self-contained
# ---------------------------------------------------------------------------


class EntityStatus(str, Enum):
    """Lifecycle status of an entity in the knowledge graph.

    Entities progress through a lifecycle from provisional (newly discovered)
    to canonical (stable, authoritative). This status determines how the
    entity is treated in queries, exports, and merge operations.
    """

    CANONICAL = "canonical"
    """Entity has been assigned a stable ID from an authoritative source."""

    PROVISIONAL = "provisional"
    """Entity is awaiting promotion based on usage count and confidence."""

    MERGED = "merged"
    """Entity has been absorbed into another entity via a merge operation."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two equal-length vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot / (mag_a * mag_b)


def _advisory_lock_key(entity_ids: list[str]) -> int:
    """Derive a stable 64-bit advisory lock key from a sorted set of entity IDs.

    Sorting ensures two workers locking the same pair always produce the same
    key regardless of argument order, preventing deadlocks.
    """
    combined = "|".join(sorted(entity_ids))
    digest = hashlib.md5(combined.encode()).digest()
    # fold to signed 64-bit range Postgres accepts
    return int.from_bytes(digest[:8], "big") % (2**63)


class _CachedCanonicalId:
    """Minimal canonical-ID-like object reconstructed from a Redis-cached dict."""

    def __init__(self, data: dict) -> None:
        self.id: str = data.get("id", "")
        self.url: Optional[str] = data.get("url")
        self.synonyms: tuple = tuple(data.get("synonyms") or [])


def _dict_to_canonical_id(data: dict) -> _CachedCanonicalId:
    """Reconstruct a minimal canonical-ID-like object from a cached dict."""
    return _CachedCanonicalId(data)


def _row_to_candidate(row: Entity) -> DomainCandidateEntity:
    """Convert an ``Entity`` ORM row to a ``DomainCandidateEntity`` for domain calls."""
    return DomainCandidateEntity(
        entity_id=row.entity_id,
        name=row.name or "",
        entity_type=row.entity_type,
        status=row.status or EntityStatus.PROVISIONAL.value,
        usage_count=row.usage_count or 0,
        confidence=row.confidence or 1.0,
    )


# ---------------------------------------------------------------------------
# PostgresIdentityServer
# ---------------------------------------------------------------------------


class PostgresIdentityServer:
    """Postgres-backed identity server.

    Parameters
    ----------
    session:
        An open SQLModel ``Session`` bound to the Postgres engine.  The caller
        is responsible for the session lifecycle (commit / rollback / close).
    domain_client:
        HTTP client used to call the pluggable domain service for authority
        lookup, survivor selection, and synonym thresholds.
    authority_cache:
        Optional ``AuthorityCache`` instance backed by Redis.  If omitted,
        authority lookups are performed on every ``resolve`` call with no
        caching.  Construct one via ``AuthorityCache.from_env()`` or pass a
        pre-built instance.
    embedding_dim:
        Expected embedding dimension.  Reserved for future validation use.
    """

    def __init__(
        self,
        session: Session,
        domain_client: DomainClient,
        authority_cache: Optional[AuthorityCache] = None,
        embedding_dim: Optional[int] = None,
    ) -> None:
        self._session = session
        self._domain_client = domain_client
        self._authority_cache = authority_cache or AuthorityCache(None)
        self._embedding_dim = embedding_dim

    # ------------------------------------------------------------------
    # resolve
    # ------------------------------------------------------------------

    async def resolve(self, mention: str, entity_type: str, document_id: str, embedding: Optional[list[float]] = None) -> str:
        """Resolve a mention to an entity ID, creating a provisional one if needed.

        Performs domain authority lookup via the domain service and returns a
        canonical ID if one is found.  Otherwise creates and returns a new
        provisional ID.  The lookup result is cached (keyed on normalised
        mention + authority source version) so that transient API failures
        do not produce inconsistent IDs on retry.

        Uses ``INSERT ... ON CONFLICT DO NOTHING`` so concurrent workers
        resolving the same mention produce the same entity without races.

        Parameters
        ----------
        mention:
            Surface form of the entity mention.
        entity_type:
            Domain-specific entity type hint.
        document_id:
            Source document identifier for provenance.
        embedding:
            Pre-computed embedding vector for the mention.

        Returns
        -------
        str
            A canonical or provisional entity ID.
        """
        # Normalise mention (strip whitespace; keep original casing for now
        # since the domain service may be case-sensitive).
        mention = mention.strip()

        # Check whether an entity already exists with this name + type.
        # Use no_autoflush to avoid flushing pending ORM inserts which would
        # violate the (name, entity_type) unique constraint before our INSERT.
        with self._session.no_autoflush:
            existing = self._session.exec(select(Entity).where(Entity.name == mention, Entity.entity_type == entity_type)).first()
        if existing is not None:
            if existing.status == EntityStatus.MERGED.value and existing.merged_into:
                logger.debug("resolve: mention '%s' maps to merged entity %s → redirecting to %s", mention, existing.entity_id, existing.merged_into)
                return existing.merged_into
            return existing.entity_id

        # Authority lookup — check cache first, then call the domain service.
        canonical_id_result = None
        cached = self._authority_cache.get(entity_type, mention)
        if cached is _NEGATIVE_SENTINEL:
            logger.debug("resolve: cache negative hit for '%s' (%s)", mention, entity_type)
        elif cached is not None:
            logger.debug("resolve: cache positive hit for '%s' (%s)", mention, entity_type)
            canonical_id_result = _dict_to_canonical_id(cached if isinstance(cached, dict) else {})
        else:
            try:
                domain_result = await self._domain_client.resolve_authority(mention, entity_type, document_id)
                if domain_result is not None:
                    canonical_id_result = _CachedCanonicalId({"id": domain_result.id, "url": domain_result.url, "synonyms": list(domain_result.synonyms)})
            except Exception:  # pylint: disable=broad-except
                logger.debug("resolve: authority lookup failed for '%s'", mention, exc_info=True)
            if canonical_id_result is not None:
                self._authority_cache.put_positive(entity_type, mention, canonical_id_result)
            else:
                self._authority_cache.put_negative(entity_type, mention)

        if canonical_id_result is not None:
            entity_id = canonical_id_result.id
            status = EntityStatus.CANONICAL.value
        else:
            entity_id = f"prov:{uuid.uuid4().hex}"
            status = EntityStatus.PROVISIONAL.value

        now = datetime.now(timezone.utc).isoformat()
        # ON CONFLICT targets (name, entity_type) — requires a unique constraint
        # on those columns.  This eliminates the TOCTOU race between the SELECT
        # above and this INSERT: whichever worker wins the INSERT owns the row;
        # the loser gets DO NOTHING and re-reads the winner.
        stmt = text("""
            INSERT INTO entity (entity_id, entity_type, name, status, confidence, usage_count, source, synonyms, properties)
            VALUES (:entity_id, :entity_type, :name, :status, :confidence, :usage_count, :source,
                    CAST(:synonyms AS json), CAST(:properties AS json))
            ON CONFLICT DO NOTHING
        """)
        synonyms_json = "[]"
        if canonical_id_result and canonical_id_result.synonyms:
            synonyms_json = json.dumps(list(canonical_id_result.synonyms))

        self._session.execute(
            stmt,
            {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "name": mention,
                "status": status,
                "confidence": 1.0,
                "usage_count": 1,
                "source": document_id,
                "synonyms": synonyms_json,
                "properties": f'{{"created_at": "{now}"}}',
            },
        )

        # Re-read the winner: our row if we won the INSERT, or the concurrent
        # row that beat us.
        winner = self._session.exec(select(Entity).where(Entity.name == mention, Entity.entity_type == entity_type)).first()
        if winner is not None:
            entity_id = winner.entity_id

        # Store embedding if provided (JSON column for now).
        if embedding is not None:
            self._store_embedding(entity_id, embedding)

        return entity_id

    # ------------------------------------------------------------------
    # promote
    # ------------------------------------------------------------------

    async def promote(self, provisional_id: str) -> str:
        """Attempt to promote a provisional entity to canonical status.

        Uses ``SELECT FOR UPDATE`` to lock the row, then checks and updates
        inside the same implicit transaction.  Behaviour by status:
          - provisional: attempts canonical ID assignment via domain service;
            upgrades if a canonical ID is returned.
          - canonical: no-op; returns existing ID.
          - merged: logs warning; returns survivor ID.

        This operation must be idempotent.

        Parameters
        ----------
        provisional_id:
            The ID of the entity to promote.  May be provisional, canonical,
            or merged.

        Returns
        -------
        str
            The canonical ID (new or pre-existing), or the survivor ID if
            the entity was merged.
        """
        row = self._session.exec(select(Entity).where(Entity.entity_id == provisional_id).with_for_update()).first()

        if row is None:
            logger.warning("promote: entity '%s' not found", provisional_id)
            return provisional_id

        if row.status == EntityStatus.MERGED.value:
            survivor = row.merged_into or provisional_id
            logger.warning("promote: entity '%s' is already merged into '%s'; returning survivor", provisional_id, survivor)
            return survivor

        if row.status == EntityStatus.CANONICAL.value:
            logger.debug("promote: entity '%s' is already canonical; no-op", provisional_id)
            return provisional_id

        # Attempt canonical ID assignment via the domain service.
        try:
            domain_result = await self._domain_client.resolve_authority(row.name or "", row.entity_type, row.source or "unknown")
        except Exception:  # pylint: disable=broad-except
            logger.debug("promote: authority lookup failed for '%s'", provisional_id, exc_info=True)
            return provisional_id

        if domain_result is None:
            return provisional_id

        new_id = domain_result.id
        # Update relationship refs BEFORE mutating the PK so there is no window
        # where relationships reference a nonexistent entity_id.
        self._update_relationship_refs(provisional_id, new_id)
        self._session.execute(
            text("UPDATE entity SET entity_id = :new_id, status = 'canonical', canonical_url = :url WHERE entity_id = :old_id AND status = 'provisional'"),
            {"new_id": new_id, "url": domain_result.url, "old_id": provisional_id},
        )
        logger.info("promote: '%s' promoted to canonical '%s'", provisional_id, new_id)
        return new_id

    # ------------------------------------------------------------------
    # find_synonyms
    # ------------------------------------------------------------------

    async def find_synonyms(self, entity_id: str) -> list[str]:
        """Return IDs of entities with cosine similarity above the per-type threshold.

        Synonym criteria are fetched from the domain service
        (``GET /synonym-criteria``).  Falls back to 0.90 if the service is
        unreachable.

        Currently uses in-process comparison of the ``embedding`` JSON column.
        This is correct but O(n) — a pgvector index query can be substituted
        here with no interface change once the column type is migrated.

        Parameters
        ----------
        entity_id:
            The entity to find synonyms for.

        Returns
        -------
        list[str]
            IDs of synonym candidates, not including ``entity_id`` itself.
            Returns an empty list if no synonyms are found.
        """
        source_row = self._session.get(Entity, entity_id)
        if source_row is None or source_row.embedding is None:
            return []

        # Fetch similarity threshold from domain service.
        similarity_threshold = await self._domain_client.synonym_criteria(source_row.entity_type)

        source_vec: list[float] = source_row.embedding
        candidates = self._session.exec(
            select(Entity).where(
                Entity.entity_id != entity_id,
                Entity.status != EntityStatus.MERGED.value,
            )
        ).all()

        results = []
        for candidate in candidates:
            if candidate.embedding is None:
                continue
            sim = _cosine_similarity(source_vec, candidate.embedding)
            if sim >= similarity_threshold:
                results.append(candidate.entity_id)

        return results

    # ------------------------------------------------------------------
    # merge
    # ------------------------------------------------------------------

    async def merge(self, entity_ids: list[str], survivor_id: str) -> str:
        """Merge entities into survivor, redirecting all relationship references.

        Acquires a Postgres advisory lock keyed on the sorted set of IDs to
        prevent concurrent merges of the same pair in opposite directions.

        Status rules:
          - all provisional → survivor stays provisional
          - any canonical → survivor becomes canonical

        This operation must be idempotent: merging already-merged entities
        is a no-op that returns the survivor ID.

        Parameters
        ----------
        entity_ids:
            The full set of IDs to unify, including the survivor.
        survivor_id:
            The ID that will remain after the merge.  Must be a member of
            ``entity_ids``.

        Returns
        -------
        str
            The survivor ID.
        """
        if survivor_id not in entity_ids:
            raise ValueError(f"survivor_id '{survivor_id}' must be a member of entity_ids")

        absorbed_ids = [eid for eid in entity_ids if eid != survivor_id]
        if not absorbed_ids:
            return survivor_id

        lock_key = _advisory_lock_key(entity_ids)
        self._session.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock_key})

        # Fetch all rows under the lock.
        rows = {row.entity_id: row for row in self._session.exec(select(Entity).where(Entity.entity_id.in_(entity_ids))).all()}  # type: ignore[attr-defined]

        survivor_row = rows.get(survivor_id)
        if survivor_row is None:
            logger.warning("merge: survivor '%s' not found; aborting", survivor_id)
            return survivor_id

        # Determine final status: canonical wins.
        any_canonical = any(r.status == EntityStatus.CANONICAL.value for r in rows.values())
        final_status = EntityStatus.CANONICAL.value if any_canonical else EntityStatus.PROVISIONAL.value

        # Redirect relationship references and mark absorbed entities.
        for absorbed_id in absorbed_ids:
            absorbed_row = rows.get(absorbed_id)
            if absorbed_row is None:
                continue
            if absorbed_row.status == EntityStatus.MERGED.value:
                logger.debug("merge: '%s' is already merged; skipping", absorbed_id)
                continue
            self._update_relationship_refs(absorbed_id, survivor_id)
            self._session.execute(
                text("UPDATE entity SET status = 'merged', merged_into = :survivor WHERE entity_id = :absorbed"),
                {"survivor": survivor_id, "absorbed": absorbed_id},
            )

        # Update survivor status if it needs to change.
        if survivor_row.status != final_status:
            self._session.execute(
                text("UPDATE entity SET status = :status WHERE entity_id = :eid"),
                {"status": final_status, "eid": survivor_id},
            )

        logger.info("merge: absorbed %s into survivor '%s' (status=%s)", absorbed_ids, survivor_id, final_status)
        return survivor_id

    # ------------------------------------------------------------------
    # on_entity_added
    # ------------------------------------------------------------------

    async def on_entity_added(self, entity_id: str, context: dict) -> None:
        """Trigger synonym detection and merge for a newly added entity.

        Must be called inside the same session/transaction as the entity insert
        so that the row is visible.  Synonym detection is read-only; ``merge``
        acquires its own advisory lock.

        Typical implementation:
        1. Call ``find_synonyms`` to identify candidates.
        2. If candidates are found, call the domain service ``select_survivor``
           to determine the survivor.
        3. Call ``merge`` for the confirmed synonym group.

        Parameters
        ----------
        entity_id:
            The ID of the entity that was just added or updated.
        context:
            Domain-defined context forwarded from the triggering operation.
        """
        synonym_ids = await self.find_synonyms(entity_id)
        if not synonym_ids:
            return

        # Fetch the new entity and all synonym candidates for survivor selection.
        all_ids = [entity_id] + synonym_ids
        rows = self._session.exec(select(Entity).where(Entity.entity_id.in_(all_ids))).all()  # type: ignore[attr-defined]

        if len(rows) < 2:
            return

        # Convert to DomainCandidateEntity for the domain service call.
        candidates = [_row_to_candidate(r) for r in rows]
        survivor_id = await self._domain_client.select_survivor(candidates)

        # Log before merging — merges are irreversible, so this audit trail
        # is important for diagnosing miscalibrated similarity thresholds.
        logger.warning(
            "on_entity_added: auto-merging %d entities into survivor '%s' (candidates=%s)",
            len(all_ids),
            survivor_id,
            all_ids,
        )
        await self.merge(all_ids, survivor_id)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _update_relationship_refs(self, old_id: str, new_id: str) -> None:
        """Redirect all relationship subject/object references from old_id to new_id."""
        self._session.execute(
            text("UPDATE relationship SET subject_id = :new_id WHERE subject_id = :old_id"),
            {"new_id": new_id, "old_id": old_id},
        )
        self._session.execute(
            text("UPDATE relationship SET object_id = :new_id WHERE object_id = :old_id"),
            {"new_id": new_id, "old_id": old_id},
        )

    def _store_embedding(self, entity_id: str, embedding: list[float]) -> None:
        """Persist an embedding vector to the entity row (JSON column)."""
        self._session.execute(
            text("UPDATE entity SET embedding = CAST(:emb AS json) WHERE entity_id = :eid"),
            {"emb": json.dumps(embedding), "eid": entity_id},
        )

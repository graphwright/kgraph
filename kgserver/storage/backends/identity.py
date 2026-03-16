"""Postgres-backed implementation of the IdentityServer ABC.

This module provides ``PostgresIdentityServer``, the reference implementation
of ``kgschema.IdentityServer``.  It uses the existing SQLModel ``Session`` and
``Entity``/``Relationship`` models already in the kgserver stack.

Locking strategy (mirrors CONCURRENCY.md):
  - resolve:  ``INSERT ... ON CONFLICT DO NOTHING`` — Postgres serialises
              concurrent inserts on the same entity_id naturally.
  - promote:  ``SELECT ... WITH (UPDLOCK)`` equivalent via raw SQL
              ``SELECT ... FOR UPDATE`` on the entity row, then conditional
              update inside the same transaction.
  - merge:    Postgres advisory lock keyed on the sorted frozenset of entity
              IDs prevents two workers merging the same pair in opposite orders.
  - on_entity_added: called synchronously inside the same session as the
              triggering entity write; synonym detection is read-only and fires
              only after the row is durable.

Synonym detection uses the ``embedding`` JSON column on the ``Entity`` table
via in-process cosine similarity for now.  Once pgvector is activated on the
column (``ALTER TABLE entity ADD COLUMN embedding vector(N)``), the
``find_synonyms`` implementation can be swapped to a native vector query with
no interface change.

Authority-lookup caching uses Redis when a client is provided.  If Redis is
unavailable the server degrades gracefully to uncached lookups.  See
``AuthorityCache`` below.
"""

import json
import logging
import math
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import text
from sqlmodel import Session, select

from kgschema.domain import DomainSchema
from kgschema.entity import BaseEntity, EntityStatus
from kgschema.identity import IdentityServer
from storage.models.entity import Entity

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Authority-lookup cache
# ---------------------------------------------------------------------------

#: Sentinel stored in Redis to represent a confirmed negative result
#: (authority returned no canonical ID for this mention).
_NEGATIVE_SENTINEL = "__negative__"

#: Default TTL (seconds) for positive cache entries.
_POSITIVE_TTL = 86400  # 24 hours

#: Default TTL for negative entries — shorter so that a mention newly added
#: to an authority source stops being provisional within a reasonable window.
_NEGATIVE_TTL = 3600  # 1 hour


class AuthorityCache:
    """Redis cache for authority-lookup results in ``resolve``.

    Keys have the form ``resolve:{authority_version}:{entity_type}:{mention}``
    so that a UMLS/DBPedia release can be invalidated by bumping
    ``authority_version`` without touching unrelated entries.

    Values are JSON-serialised ``CanonicalId`` dicts (positive hit) or
    ``_NEGATIVE_SENTINEL`` (confirmed miss).

    Designed for graceful degradation: every public method catches Redis
    errors and logs at DEBUG level so a Redis outage never breaks ingestion.

    Parameters
    ----------
    redis_client:
        A ``redis.Redis`` (sync) client.  Pass ``None`` to disable caching.
    authority_version:
        Opaque version string for the authority source, e.g. ``"umls-2026AA"``.
        Bump this to invalidate all cached lookups for that source.
    positive_ttl:
        Seconds before a positive cache entry expires.
    negative_ttl:
        Seconds before a negative cache entry expires.
    """

    def __init__(
        self,
        redis_client: Optional[Any],
        authority_version: str = "v1",
        positive_ttl: int = _POSITIVE_TTL,
        negative_ttl: int = _NEGATIVE_TTL,
    ) -> None:
        self._redis: Optional[Any] = redis_client
        self._version = authority_version
        self._positive_ttl = positive_ttl
        self._negative_ttl = negative_ttl

    def _key(self, entity_type: str, mention: str) -> str:
        # Normalise mention to lower-case stripped form so that trivial
        # capitalisation differences share a cache entry.
        normalised = mention.strip().lower()
        return f"resolve:{self._version}:{entity_type}:{normalised}"

    def get(self, entity_type: str, mention: str) -> Optional[Any]:
        """Return cached ``CanonicalId``-like dict, ``None`` (miss), or
        ``_NEGATIVE_SENTINEL`` (confirmed negative).

        Returns ``None`` on any Redis error so the caller falls through to the
        live authority lookup.
        """
        if self._redis is None:
            return None
        try:
            raw = self._redis.get(self._key(entity_type, mention))  # type: ignore[union-attr]
            if raw is None:
                return None
            decoded = raw.decode() if isinstance(raw, bytes) else raw
            if decoded == _NEGATIVE_SENTINEL:
                return _NEGATIVE_SENTINEL
            return json.loads(decoded)
        except Exception:  # pylint: disable=broad-except
            logger.debug("AuthorityCache.get failed", exc_info=True)
            return None

    def put_positive(self, entity_type: str, mention: str, canonical_id: object) -> None:
        """Cache a positive authority result.  ``canonical_id`` must be
        JSON-serialisable (plain dict or object with ``__dict__``).
        """
        if self._redis is None:
            return
        try:
            payload = json.dumps(canonical_id.__dict__ if hasattr(canonical_id, "__dict__") else canonical_id)
            self._redis.setex(self._key(entity_type, mention), self._positive_ttl, payload)  # type: ignore[union-attr]
        except Exception:  # pylint: disable=broad-except
            logger.debug("AuthorityCache.put_positive failed", exc_info=True)

    def put_negative(self, entity_type: str, mention: str) -> None:
        """Cache a confirmed negative (no canonical ID found)."""
        if self._redis is None:
            return
        try:
            self._redis.setex(self._key(entity_type, mention), self._negative_ttl, _NEGATIVE_SENTINEL)  # type: ignore[union-attr]
        except Exception:  # pylint: disable=broad-except
            logger.debug("AuthorityCache.put_negative failed", exc_info=True)

    @classmethod
    def from_env(cls, authority_version: str = "v1") -> "AuthorityCache":
        """Build an ``AuthorityCache`` from the ``REDIS_URL`` environment variable.

        Returns a no-op cache (``redis_client=None``) if ``REDIS_URL`` is unset
        or if the ``redis`` package is not installed, so the server starts
        cleanly in environments without Redis.
        """
        import os

        redis_url = os.environ.get("REDIS_URL")
        if not redis_url:
            logger.debug("AuthorityCache.from_env: REDIS_URL not set; caching disabled")
            return cls(None, authority_version=authority_version)
        try:
            import redis as _redis

            client = _redis.Redis.from_url(redis_url, decode_responses=False)
            client.ping()
            logger.info("AuthorityCache: connected to Redis at %s", redis_url)
            return cls(client, authority_version=authority_version)
        except Exception:  # pylint: disable=broad-except
            logger.warning("AuthorityCache.from_env: could not connect to Redis; caching disabled", exc_info=True)
            return cls(None, authority_version=authority_version)


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
    # fold the full hash into a signed 64-bit range Postgres accepts
    return hash(combined) % (2**63)


class PostgresIdentityServer(IdentityServer):
    """Postgres-backed identity server using the existing kgserver SQLModel session.

    Parameters
    ----------
    session:
        An open SQLModel ``Session`` bound to the Postgres engine.  The caller
        is responsible for the session lifecycle (commit / rollback / close).
    domain:
        The active ``DomainSchema`` instance.  Used for ``preferred_entity``
        (survivor selection) and ``get_promotion_policy`` (canonical ID
        assignment during promotion).
    similarity_threshold:
        Minimum cosine similarity for two entities to be considered synonyms.
        Default 0.90 — intentionally conservative.
    embedding_dim:
        Expected embedding dimension.  Used for validation only.
    authority_cache:
        Optional ``AuthorityCache`` instance backed by Redis.  If omitted,
        authority lookups are performed on every ``resolve`` call with no
        caching.  Construct one via ``AuthorityCache.from_env()`` or pass a
        pre-built instance.
    """

    def __init__(
        self,
        session: Session,
        domain: DomainSchema,
        similarity_threshold: float = 0.90,
        embedding_dim: Optional[int] = None,
        authority_cache: Optional[AuthorityCache] = None,
    ) -> None:
        self._session = session
        self._domain = domain
        self._similarity_threshold = similarity_threshold
        self._embedding_dim = embedding_dim
        self._authority_cache = authority_cache or AuthorityCache(None)

    # ------------------------------------------------------------------
    # resolve
    # ------------------------------------------------------------------

    async def resolve(self, mention: str, context: dict) -> str:
        """Resolve a mention to an entity ID, creating a provisional one if needed.

        Uses ``INSERT ... ON CONFLICT DO NOTHING`` so concurrent workers
        resolving the same mention produce the same entity without races.

        Authority lookup (UMLS etc.) is attempted first via the domain's
        promotion policy.  If the authority returns a canonical ID, the entity
        is inserted as canonical.  Otherwise a provisional UUID is created.

        The ``context`` dict may contain:
          - ``entity_type`` (str): domain entity type hint
          - ``document_id`` (str): source document for provenance
          - ``embedding`` (list[float]): pre-computed embedding vector
        """
        entity_type = context.get("entity_type", "unknown")
        document_id = context.get("document_id", "unknown")
        embedding = context.get("embedding")

        # Check whether an entity already exists with this name + type.
        existing = self._session.exec(select(Entity).where(Entity.name == mention, Entity.entity_type == entity_type)).first()
        if existing is not None:
            if existing.status == EntityStatus.MERGED.value and existing.merged_into:
                logger.debug("resolve: mention '%s' maps to merged entity %s → redirecting to %s", mention, existing.entity_id, existing.merged_into)
                return existing.merged_into
            return existing.entity_id

        # Authority lookup — check cache first, then call the domain policy.
        canonical_id_result = None
        cached = self._authority_cache.get(entity_type, mention)
        if cached is _NEGATIVE_SENTINEL:
            # Confirmed miss: skip the live API call.
            logger.debug("resolve: cache negative hit for '%s' (%s)", mention, entity_type)
        elif cached is not None:
            # Positive hit: reconstruct a minimal CanonicalId-like object.
            logger.debug("resolve: cache positive hit for '%s' (%s)", mention, entity_type)
            canonical_id_result = _dict_to_canonical_id(cached if isinstance(cached, dict) else {})
        else:
            policy = self._domain.get_promotion_policy()
            if policy is not None:
                try:
                    stub = _make_stub_entity(mention, entity_type, document_id, embedding)
                    canonical_id_result = await policy.assign_canonical_id(stub)
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
        stmt = text("""
            INSERT INTO entity (entity_id, entity_type, name, status, confidence, usage_count, source, synonyms, properties)
            VALUES (:entity_id, :entity_type, :name, :status, :confidence, :usage_count, :source,
                    CAST(:synonyms AS json), CAST(:properties AS json))
            ON CONFLICT (entity_id) DO NOTHING
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
          - provisional: attempts canonical ID assignment; upgrades if found.
          - canonical: no-op; returns existing ID.
          - merged: logs warning; returns survivor ID.
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

        # Attempt canonical ID assignment.
        policy = self._domain.get_promotion_policy()
        if policy is None:
            return provisional_id

        stub = _entity_row_to_stub(row)
        if not policy.should_promote(stub):
            return provisional_id

        canonical_id_result = await policy.assign_canonical_id(stub)
        if canonical_id_result is None:
            return provisional_id

        new_id = canonical_id_result.id
        # Update the row in-place (entity_id is PK — we update via raw SQL to
        # change the PK and status atomically, then update relationship refs).
        self._session.execute(
            text("UPDATE entity SET entity_id = :new_id, status = 'canonical', canonical_url = :url WHERE entity_id = :old_id AND status = 'provisional'"),
            {"new_id": new_id, "url": canonical_id_result.url, "old_id": provisional_id},
        )
        self._update_relationship_refs(provisional_id, new_id)
        logger.info("promote: '%s' promoted to canonical '%s'", provisional_id, new_id)
        return new_id

    # ------------------------------------------------------------------
    # find_synonyms
    # ------------------------------------------------------------------

    async def find_synonyms(self, entity_id: str) -> list[str]:
        """Return IDs of entities with cosine similarity above the threshold.

        Currently uses in-process comparison of the ``embedding`` JSON column.
        This is correct but O(n) — a pgvector index query can be substituted
        here with no interface change once the column type is migrated.
        """
        source_row = self._session.get(Entity, entity_id)
        if source_row is None or source_row.embedding is None:
            return []

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
            if sim >= self._similarity_threshold:
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
        """
        synonym_ids = await self.find_synonyms(entity_id)
        if not synonym_ids:
            return

        # Fetch the new entity and all synonym candidates for survivor selection.
        all_ids = [entity_id] + synonym_ids
        rows = self._session.exec(select(Entity).where(Entity.entity_id.in_(all_ids))).all()  # type: ignore[attr-defined]

        if len(rows) < 2:
            return

        # Convert to kgschema BaseEntity stubs for preferred_entity.
        stubs = [_entity_row_to_stub(r) for r in rows]
        survivor_stub = self._domain.preferred_entity(stubs)
        await self.merge(all_ids, survivor_stub.entity_id)

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


# ---------------------------------------------------------------------------
# Helpers to bridge kgserver Entity rows ↔ kgschema BaseEntity stubs
# ---------------------------------------------------------------------------


class _StubEntity(BaseEntity):
    """Minimal BaseEntity subclass used to call domain policies from kgserver.

    Domain ``preferred_entity`` and ``PromotionPolicy`` methods require a
    ``BaseEntity`` instance.  We don't know the domain-specific subclass here,
    so we use a generic concrete subclass and bypass pydantic validation with
    ``model_construct`` to avoid requiring all optional fields.
    """

    def get_entity_type(self) -> str:
        return ""  # not needed for identity operations


def _entity_row_to_stub(row: Entity) -> _StubEntity:
    """Convert a kgserver ``Entity`` ORM row to a ``_StubEntity`` for domain calls."""
    canonical_ids: dict[str, str] = {}
    if row.canonical_url:
        canonical_ids["url"] = row.canonical_url
    return _StubEntity.model_construct(
        entity_id=row.entity_id,
        status=EntityStatus(row.status) if row.status else EntityStatus.PROVISIONAL,
        name=row.name or "",
        synonyms=tuple(row.synonyms or []),
        embedding=tuple(row.embedding) if row.embedding else None,
        canonical_ids=canonical_ids,
        confidence=row.confidence or 1.0,
        usage_count=row.usage_count or 0,
        created_at=datetime.now(timezone.utc),
        source=row.source or "",
        metadata={},
        merged_into=row.merged_into,
        promotable=True,
    )


def _make_stub_entity(mention: str, entity_type: str, document_id: str, embedding: Optional[list[float]]) -> _StubEntity:
    """Build a minimal stub for authority lookup (no DB row exists yet)."""
    return _StubEntity.model_construct(
        entity_id=f"prov:{uuid.uuid4().hex}",
        status=EntityStatus.PROVISIONAL,
        name=mention,
        synonyms=(),
        embedding=tuple(embedding) if embedding else None,
        canonical_ids={},
        confidence=1.0,
        usage_count=0,
        created_at=datetime.now(timezone.utc),
        source=document_id,
        metadata={},
        merged_into=None,
        promotable=True,
    )


class _CachedCanonicalId:
    """Minimal CanonicalId-like object reconstructed from a Redis-cached dict."""

    def __init__(self, data: dict) -> None:
        self.id: str = data.get("id", "")
        self.url: Optional[str] = data.get("url")
        self.synonyms: tuple = tuple(data.get("synonyms") or [])


def _dict_to_canonical_id(data: dict) -> _CachedCanonicalId:
    """Reconstruct a minimal CanonicalId-like object from a cached dict."""
    return _CachedCanonicalId(data)

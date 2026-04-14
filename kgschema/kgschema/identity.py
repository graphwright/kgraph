"""Identity server interface for the knowledge graph framework.

The identity server is the authoritative component for entity identity across
the knowledge graph. It handles the full entity identity lifecycle:

- **resolve**: Map a mention string to a canonical or provisional entity ID,
  creating a new provisional entity if no match is found.
- **promote**: Elevate a provisional entity to canonical status when
  domain-defined thresholds are met.
- **find_synonyms**: Detect entities that refer to the same real-world concept
  (read-only; does not perform merges).
- **merge**: Collapse duplicate entities into a single survivor, redirecting
  all references from absorbed entities to the survivor.
- **on_entity_added**: Event hook called after each entity insert, triggering
  synonym detection and merge for newly added entities.

Implementations must be correct under concurrent access from multiple worker
processes and multiple server replicas. All mutating operations must be
idempotent so that workers can safely retry after transient failures.

See CONCURRENCY.md (Identity Server Specification section) for the full
design rationale, locking strategy, and merge × promotion status rules.
"""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class IdentityServer(ABC):
    """Abstract interface for entity identity management.

    Implementations are responsible for resolving mentions to entity IDs,
    promoting provisional entities, detecting synonyms, and merging
    duplicates — all with correct behaviour under concurrent access.

    The recommended implementation is Postgres-backed, using:
    - ``INSERT ... ON CONFLICT DO NOTHING`` for idempotent creation
    - ``SELECT FOR UPDATE`` for atomic promotion
    - Postgres advisory locks (keyed on sorted entity ID pairs) for merge
    - pgvector cosine similarity for synonym detection
    - Redis for authority-lookup caching (shared across replicas)

    Domain-pluggable behaviour (authority lookup, synonym thresholds,
    survivor selection, promotion thresholds) is supplied by the domain
    schema and its ``PromotionPolicy``.
    """

    @abstractmethod
    async def resolve(self, mention: str, context: dict) -> str:
        """Resolve a mention string to an entity ID.

        Performs domain authority lookup (e.g. UMLS, Wikidata) and returns a
        canonical ID if one is found. Otherwise creates and returns a new
        provisional ID. The lookup result is cached (keyed on normalised
        mention + authority source version) so that transient API failures
        do not produce inconsistent IDs on retry.

        This operation must be idempotent: resolving the same mention twice
        returns the same ID.

        Parameters
        ----------
        mention:
            The surface form of the entity mention.
        context:
            Domain-defined context (e.g. document ID, domain name, entity
            type hint, extraction metadata) used by authority lookup and
            synonym detection.

        Returns
        -------
        str
            A canonical or provisional entity ID.
        """

    @abstractmethod
    async def promote(self, provisional_id: str) -> str:
        """Attempt to promote a provisional entity to canonical status.

        The domain ``PromotionPolicy`` determines whether promotion is
        warranted. Behaviour by current entity status:

        - **provisional**: checks policy; upgrades if thresholds are met.
        - **canonical**: no-op; returns the existing canonical ID.
          Promotion is a one-time transition.
        - **merged**: the entity has been absorbed. Logs a warning with the
          stale ID and returns the survivor's ID; does not raise an error.

        This operation must be idempotent.

        Parameters
        ----------
        provisional_id:
            The ID of the entity to promote. May be provisional, canonical,
            or merged.

        Returns
        -------
        str
            The canonical ID (new or pre-existing), or the survivor ID if
            the entity was merged.
        """

    @abstractmethod
    async def find_synonyms(self, entity_id: str) -> list[str]:
        """Return the IDs of entities considered synonymous with the given entity.

        Synonym criteria are domain-defined and may include:
        - Cosine similarity above a threshold (via pgvector)
        - Shared external identifier (same UMLS CUI, same MeSH term)
        - String normalisation match

        This method is read-only; it reports candidates without merging.
        Call ``merge`` to act on the results.

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

    @abstractmethod
    async def merge(self, entity_ids: list[str], survivor_id: str) -> str:
        """Merge a set of entities into a single survivor.

        All references (relationships, mentions, bundle edges) pointing to
        any absorbed entity are redirected to the survivor. Absorbed entities
        are marked ``status=MERGED`` with ``merged_into=survivor_id`` so
        that stale external references remain resolvable via a single lookup.

        Status rules for the survivor:
        - provisional + provisional → survivor remains **provisional**
          (promotable via normal policy)
        - canonical + anything → survivor remains **canonical**

        Locking: implementations should acquire an advisory lock keyed on
        the sorted set of entity IDs before the transaction to prevent
        two workers from merging the same pair in opposite orders.

        This operation must be idempotent: merging already-merged entities
        is a no-op that returns the survivor ID.

        Parameters
        ----------
        entity_ids:
            The full set of IDs to unify, including the survivor.
        survivor_id:
            The ID that will remain after the merge. Must be a member of
            ``entity_ids``. Determined by the caller via
            ``DomainSchema.preferred_entity``.

        Returns
        -------
        str
            The survivor ID.
        """

    @abstractmethod
    async def on_entity_added(self, entity_id: str, context: dict) -> None:
        """Event hook called after an entity is inserted or updated.

        Must be called inside the same transaction as the entity insert so
        that synonym detection fires only after the row is durably committed
        and visible. This prevents the race where two concurrent workers
        each see the other as a merge candidate before either insert
        completes.

        Typical implementation:
        1. Embed the entity (if not already embedded).
        2. Call ``find_synonyms`` to identify candidates.
        3. If candidates are found, call ``DomainSchema.preferred_entity``
           to select the survivor.
        4. Call ``merge`` for each confirmed synonym pair.

        This event-driven model subsumes batch synonym sweeps: a batch sweep
        is equivalent to replaying ``on_entity_added`` for every entity in
        the store.

        Parameters
        ----------
        entity_id:
            The ID of the entity that was just added or updated.
        context:
            Domain-defined context forwarded from the triggering operation.
        """

"""Entity system for the knowledge graph framework.

This module defines the core entity types for the knowledge graph:

- **BaseEntity**: Abstract base class for all domain entities (nodes in the graph)
- **EntityMention**: Raw entity extraction from a document (before resolution)
- **EntityStatus**: Enum distinguishing canonical vs provisional entities
- **PromotionConfig**: Configuration for promoting provisional → canonical

**Entity Lifecycle:**

1. **Extraction**: The entity extractor finds mentions in document text,
   producing `EntityMention` objects with text spans and confidence scores.

2. **Resolution**: The entity resolver maps mentions to `BaseEntity` instances,
   either matching existing entities or creating new provisional ones.

3. **Promotion**: Provisional entities that accumulate sufficient usage and
   confidence are promoted to canonical status with stable identifiers.

4. **Merging**: Duplicate canonical entities detected via embedding similarity
   can be merged to maintain a clean entity vocabulary.

Entities are immutable (frozen Pydantic models) to ensure consistency when
referenced by relationships and stored in multiple indices.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class EntityStatus(str, Enum):
    """Lifecycle status of an entity in the knowledge graph.

    Entities progress through a lifecycle from provisional (newly discovered)
    to canonical (stable, authoritative). This status determines how the
    entity is treated in queries, exports, and merge operations.
    """

    CANONICAL = "canonical"
    """Entity has been assigned a stable ID from an authoritative source.

    Canonical entities have verified identifiers from external authorities
    (UMLS CUIs, Wikidata QIDs, etc.) or have been promoted
    based on sufficient usage evidence. They are included in the primary
    entity export and are considered authoritative for relationship linking.
    """

    PROVISIONAL = "provisional"
    """Entity is awaiting promotion based on usage count and confidence.

    Provisional entities are newly discovered mentions that haven't yet
    accumulated enough evidence for canonical status. They have temporary
    UUIDs and are exported per-document rather than in the global entity
    collection. Once usage thresholds are met, they can be promoted.
    """

    MERGED = "merged"
    """Entity has been absorbed into another entity via a merge operation.

    Merged entities are retained (not deleted) so that stale external
    references can be resolved via a single redirect lookup using the
    `merged_into` field. They are excluded from normal queries but
    remain resolvable for provenance and backwards compatibility.
    """


class PromotionConfig(BaseModel, frozen=True):
    """Configuration for promoting provisional entities to canonical status.

    Controls the thresholds that determine when a provisional entity has
    accumulated enough evidence to be promoted. Different domains may
    require different thresholds based on data quality and the availability
    of external authority sources.

    Attributes:
        min_usage_count: Minimum times the entity must appear across documents.
        min_confidence: Minimum confidence score from entity resolution.
        require_embedding: Whether an embedding vector is required for promotion.
    """

    min_usage_count: int = Field(
        default=3,
        ge=1,
        description="Minimum number of appearances before promotion is considered.",
    )
    min_confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score required for promotion.",
    )
    require_embedding: bool = Field(
        default=True,
        description="Whether an embedding must be present for promotion.",
    )


class BaseEntity(ABC, BaseModel):
    """Abstract base class for all domain entities (knowledge graph nodes).

    Entities represent the nodes in the knowledge graph—the "things" that
    relationships connect. Each entity has a unique identifier, a primary
    name, optional synonyms, and domain-specific attributes.

    Entities are frozen (immutable) Pydantic models. To modify an entity,
    use `entity.model_copy(update={...})` to create a new instance with
    updated fields.

    Subclasses must implement:
        - `get_entity_type()`: Return the domain-specific type identifier

    Key fields:
        - `entity_id`: Unique identifier (canonical ID or provisional UUID)
        - `status`: CANONICAL or PROVISIONAL lifecycle state
        - `name`: Primary display name
        - `synonyms`: Alternative names for matching
        - `embedding`: Semantic vector for similarity operations
        - `usage_count`: Number of document references (for promotion)
        - `confidence`: Resolution confidence score

    Example:
        ```python
        class DrugEntity(BaseEntity):
            drug_class: str | None = None
            mechanism: str | None = None

            def get_entity_type(self) -> str:
                return "drug"
        ```
    """

    model_config = {"frozen": True}

    promotable: bool = Field(default=True, description="Whether this entity type can be promoted from provisional to canonical.")
    entity_id: str = Field(description="Domain-specific canonical ID or provisional UUID.")
    status: EntityStatus = Field(default=EntityStatus.PROVISIONAL, description="Whether entity is canonical or provisional.")
    name: str = Field(description="Primary name/label for the entity.")
    synonyms: tuple[str, ...] = Field(
        default=(),
        description="Alternative names or aliases for this entity.",
    )
    embedding: tuple[float, ...] | None = Field(
        default=None,
        description="Semantic vector embedding for similarity operations.",
    )
    canonical_ids: dict[str, str] = Field(
        default_factory=dict,
        description="Authoritative identifiers from various sources (e.g., {'wikidata': 'Q123', 'mesh': 'D001234'}).",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in the entity resolution and its attributes.",
    )
    usage_count: int = Field(
        default=0,
        ge=0,
        description="Number of times this entity has been referenced.",
    )
    created_at: datetime = Field(description="Timestamp when the entity was first created.")
    source: str = Field(description="Origin indicator (e.g., document ID, extraction pipeline).")
    merged_into: str | None = Field(
        default=None,
        description="If status is MERGED, the entity_id of the survivor. None otherwise.",
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Domain-specific metadata.",
    )

    @model_validator(mode="after")
    def _ensure_canonical_if_not_promotable(self) -> "BaseEntity":
        if not self.promotable and self.status != EntityStatus.CANONICAL:
            raise ValueError("Entities that are not promotable must be created with CANONICAL status.")
        return self

    @abstractmethod
    def get_entity_type(self) -> str:
        """Return domain-specific entity type identifier.
        Examples: 'drug', 'disease', 'gene' for medical domain;
        'case', 'statute', 'court' for legal domain.
        """


class EntityMention(BaseModel, frozen=True):
    """A raw entity mention extracted from document text.

    Represents the output of entity extraction (Pass 1) before resolution
    to a canonical or provisional entity. Captures the exact text span,
    its position in the document, and extraction confidence.

    Entity mentions are intermediate objects that flow from the extractor
    to the resolver. The resolver then maps each mention to an existing
    entity or creates a new provisional entity.

    Frozen (immutable) to ensure mentions can be safely passed through
    the pipeline without modification.

    Attributes:
        text: The exact text span that was identified as an entity.
        entity_type: Domain-specific type classification (e.g., "drug", "gene").
        start_offset: Character position where the mention begins.
        end_offset: Character position where the mention ends.
        confidence: Extraction confidence score (0.0 to 1.0).
        context: Optional surrounding text for disambiguation.
        metadata: Domain-specific extraction metadata.

    Example:
        ```python
        mention = EntityMention(
            text="aspirin",
            entity_type="drug",
            start_offset=42,
            end_offset=49,
            confidence=0.95,
            context="...patients taking aspirin showed improved...",
        )
        ```
    """

    text: str = Field(description="The exact text span mentioning the entity.")
    entity_type: str = Field(description="Domain-specific type classification.")
    start_offset: int = Field(
        ge=0,
        description="Character offset where mention starts in source text.",
    )
    end_offset: int = Field(
        ge=0,
        description="Character offset where mention ends in source text.",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Extraction confidence score.",
    )
    context: str | None = Field(
        default=None,
        description="Surrounding text for disambiguation.",
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Domain-specific extraction metadata.",
    )

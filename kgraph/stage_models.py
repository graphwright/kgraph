"""Pydantic models for ingestion pipeline stage outputs.

These models capture the state of the pipeline at each stage, enabling:
1. Validation of intermediate results
2. JSON serialization for debugging and testing
3. Stopping the pipeline at any stage and dumping state to stdout

Stage Flow:
    Stage 1 (entities): Per-paper entity extraction
    Stage 2 (promotion): Batch de-duplication and promotion across all papers
    Stage 3 (relationships): Per-paper relationship extraction

Each stage produces a model that can be serialized to JSON for inspection.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IngestionStage(str, Enum):
    """Pipeline stages where ingestion can be stopped."""

    ENTITIES = "entities"
    PROMOTION = "promotion"
    RELATIONSHIPS = "relationships"


# =============================================================================
# Stage 1: Entity Extraction (per-paper)
# =============================================================================


class ExtractedEntityRecord(BaseModel):
    """Record of a single extracted entity."""

    model_config = ConfigDict(frozen=True)

    entity_id: str = Field(description="Assigned entity ID (provisional or canonical)")
    name: str = Field(description="Primary entity name")
    entity_type: str = Field(description="Entity type (disease, gene, drug, etc.)")
    status: str = Field(description="Entity status (provisional or canonical)")
    confidence: float = Field(description="Extraction confidence score")
    source: str = Field(description="Source document ID")
    canonical_ids: dict[str, str] = Field(
        default_factory=dict,
        description="Canonical IDs from authoritative sources",
    )
    synonyms: tuple[str, ...] = Field(default=(), description="Known synonyms")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PaperEntityExtractionResult(BaseModel):
    """Result of entity extraction from a single paper."""

    model_config = ConfigDict(frozen=True)

    document_id: str = Field(description="Document ID")
    source_uri: str | None = Field(default=None, description="Source file path or URI")
    extracted_at: datetime = Field(description="Timestamp of extraction")
    entities_extracted: int = Field(description="Total entity mentions found")
    entities_new: int = Field(description="New entities created")
    entities_existing: int = Field(description="Existing entities matched")
    entities: tuple[ExtractedEntityRecord, ...] = Field(
        default=(),
        description="Extracted entity records",
    )
    errors: tuple[str, ...] = Field(default=(), description="Errors encountered")


class EntityExtractionStageResult(BaseModel):
    """Complete result of Stage 1: Entity Extraction across all papers.

    This model captures the state after all papers have been processed
    for entity extraction, but before promotion.
    """

    model_config = ConfigDict(frozen=True)

    stage: str = Field(default="entities", description="Stage identifier")
    completed_at: datetime = Field(description="Timestamp when stage completed")
    papers_processed: int = Field(description="Number of papers processed")
    papers_failed: int = Field(description="Number of papers with errors")
    total_entities_extracted: int = Field(description="Total entity mentions")
    total_entities_new: int = Field(description="Total new entities created")
    total_entities_existing: int = Field(description="Total existing entities matched")
    paper_results: tuple[PaperEntityExtractionResult, ...] = Field(
        default=(),
        description="Per-paper extraction results",
    )

    # Summary statistics
    entity_type_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Count of entities by type",
    )
    provisional_count: int = Field(default=0, description="Number of provisional entities")
    canonical_count: int = Field(default=0, description="Number of canonical entities")


# =============================================================================
# Stage 2: Promotion (batch across all papers)
# =============================================================================


class PromotedEntityRecord(BaseModel):
    """Record of an entity that was promoted to canonical status."""

    model_config = ConfigDict(frozen=True)

    old_entity_id: str = Field(description="Previous provisional entity ID")
    new_entity_id: str = Field(description="New canonical entity ID")
    name: str = Field(description="Entity name")
    entity_type: str = Field(description="Entity type")
    canonical_source: str = Field(description="Source of canonical ID (umls, hgnc, etc.)")
    canonical_url: str | None = Field(default=None, description="URL to canonical source")


class PromotionStageResult(BaseModel):
    """Complete result of Stage 2: Entity Promotion.

    This model captures the state after provisional entities have been
    de-duplicated and promoted to canonical status.
    """

    model_config = ConfigDict(frozen=True)

    stage: str = Field(default="promotion", description="Stage identifier")
    completed_at: datetime = Field(description="Timestamp when stage completed")

    # Promotion statistics
    candidates_evaluated: int = Field(description="Entities meeting promotion thresholds")
    entities_promoted: int = Field(description="Entities successfully promoted")
    entities_skipped_no_canonical_id: int = Field(
        default=0,
        description="Skipped because no canonical ID found",
    )
    entities_skipped_policy: int = Field(
        default=0,
        description="Skipped by promotion policy",
    )
    entities_skipped_storage_failure: int = Field(
        default=0,
        description="Skipped due to storage errors",
    )

    # Detailed records
    promoted_entities: tuple[PromotedEntityRecord, ...] = Field(
        default=(),
        description="Records of promoted entities",
    )

    # Post-promotion state
    total_canonical_entities: int = Field(description="Total canonical entities after promotion")
    total_provisional_entities: int = Field(description="Remaining provisional entities")


# =============================================================================
# Stage 3: Relationship Extraction (per-paper)
# =============================================================================


class ExtractedRelationshipRecord(BaseModel):
    """Record of a single extracted relationship."""

    model_config = ConfigDict(frozen=True)

    subject_id: str = Field(description="Subject entity ID")
    subject_name: str = Field(description="Subject entity name")
    subject_type: str = Field(description="Subject entity type")
    predicate: str = Field(description="Relationship predicate")
    object_id: str = Field(description="Object entity ID")
    object_name: str = Field(description="Object entity name")
    object_type: str = Field(description="Object entity type")
    confidence: float = Field(description="Extraction confidence")
    source_document: str = Field(description="Source document ID")
    evidence_quote: str | None = Field(default=None, description="Supporting evidence text")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PaperRelationshipExtractionResult(BaseModel):
    """Result of relationship extraction from a single paper."""

    model_config = ConfigDict(frozen=True)

    document_id: str = Field(description="Document ID")
    source_uri: str | None = Field(default=None, description="Source file path or URI")
    extracted_at: datetime = Field(description="Timestamp of extraction")
    relationships_extracted: int = Field(description="Number of relationships found")
    relationships: tuple[ExtractedRelationshipRecord, ...] = Field(
        default=(),
        description="Extracted relationship records",
    )
    errors: tuple[str, ...] = Field(default=(), description="Errors encountered")


class RelationshipExtractionStageResult(BaseModel):
    """Complete result of Stage 3: Relationship Extraction.

    This model captures the final state after relationship extraction.
    """

    model_config = ConfigDict(frozen=True)

    stage: str = Field(default="relationships", description="Stage identifier")
    completed_at: datetime = Field(description="Timestamp when stage completed")
    papers_processed: int = Field(description="Number of papers processed")
    papers_with_relationships: int = Field(description="Papers with at least one relationship")
    total_relationships_extracted: int = Field(description="Total relationships extracted")
    paper_results: tuple[PaperRelationshipExtractionResult, ...] = Field(
        default=(),
        description="Per-paper extraction results",
    )

    # Summary statistics
    predicate_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Count of relationships by predicate",
    )


# =============================================================================
# Complete Pipeline Result
# =============================================================================


class IngestionPipelineResult(BaseModel):
    """Complete result of the full ingestion pipeline.

    Combines results from all three stages for final output.
    """

    model_config = ConfigDict(frozen=True)

    pipeline_version: str = Field(default="1.0.0", description="Pipeline version")
    started_at: datetime = Field(description="Pipeline start timestamp")
    completed_at: datetime = Field(description="Pipeline completion timestamp")
    stopped_at_stage: str | None = Field(
        default=None,
        description="Stage where pipeline was stopped (if --stop-after used)",
    )

    # Stage results (None if stage not reached)
    entity_extraction: EntityExtractionStageResult | None = Field(
        default=None,
        description="Stage 1 results",
    )
    promotion: PromotionStageResult | None = Field(
        default=None,
        description="Stage 2 results",
    )
    relationship_extraction: RelationshipExtractionStageResult | None = Field(
        default=None,
        description="Stage 3 results",
    )

    # Final summary
    total_documents: int = Field(description="Total documents processed")
    total_entities: int = Field(description="Total entities in graph")
    total_relationships: int = Field(description="Total relationships in graph")

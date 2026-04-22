"""Pydantic schemas for the medlit domain service API."""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class FrozenModel(BaseModel):
    """Shared frozen base model."""

    model_config = ConfigDict(frozen=True)


class ResolveAuthorityRequest(FrozenModel):
    """Request body for POST /resolve-authority."""

    mention: str = Field(description="Surface form of the entity mention.")
    entity_type: str = Field(description="Domain-specific entity type hint (e.g. 'drug', 'disease').")
    document_id: Optional[str] = Field(default=None, description="Source document identifier.")


class CanonicalIdResponse(FrozenModel):
    """Canonical ID payload for authority resolution."""

    id: str = Field(description="Canonical ID string (e.g. 'UMLS:C0006142', 'HGNC:1100').")
    url: Optional[str] = Field(default=None, description="URL to the authoritative source page.")
    synonyms: tuple[str, ...] = Field(default=(), description="Alternative names that map to this canonical ID.")
    authority: Optional[str] = Field(default=None, description="Authority name that produced the canonical ID.")
    confidence: Optional[float] = Field(default=None, description="Authority match confidence [0.0, 1.0].")


class ResolveAuthorityResponse(FrozenModel):
    """Response body for POST /resolve-authority."""

    canonical_id: Optional[CanonicalIdResponse] = Field(
        default=None,
        description="Canonical ID if found; null means no authority match (entity stays provisional).",
    )
    authority: Optional[str] = Field(default=None, description="Authority name if a match is found.")
    confidence: Optional[float] = Field(default=None, description="Resolution confidence if a match is found.")


class CandidateEntity(FrozenModel):
    """A candidate entity sent by the identity server for survivor selection."""

    entity_id: str = Field(description="Entity ID.")
    name: str = Field(description="Primary name of the entity.")
    entity_type: str = Field(description="Domain-specific entity type.")
    status: str = Field(description="Entity status string ('canonical', 'provisional', 'merged').")
    usage_count: int = Field(description="Number of times this entity has been referenced.")
    confidence: float = Field(description="Resolution confidence score.")


class SelectSurvivorRequest(FrozenModel):
    """Request body for POST /select-survivor."""

    candidates: tuple[CandidateEntity, ...] = Field(default=(), description="All entities being considered for merge.")
    entity_a: Optional[CandidateEntity] = Field(default=None, description="First merge candidate (pairwise mode).")
    entity_b: Optional[CandidateEntity] = Field(default=None, description="Second merge candidate (pairwise mode).")


class SelectSurvivorResponse(FrozenModel):
    """Response body for POST /select-survivor."""

    survivor_id: str = Field(description="The entity ID that should survive the merge.")


class SynonymCriteriaRequest(FrozenModel):
    """Backward-compatible request body for POST /synonym-criteria."""

    entity_type: str = Field(description="Domain-specific entity type to fetch synonym criteria for.")


class SynonymCriteriaResponse(FrozenModel):
    """Backward-compatible response body for POST /synonym-criteria."""

    similarity_threshold: float = Field(description="Minimum cosine similarity for two entities to be considered synonyms.")


class PredicateContract(FrozenModel):
    """Predicate schema declaration."""

    name: str = Field(description="Predicate name.")
    domain: frozenset[str] = Field(default_factory=frozenset, description="Allowed subject entity types.")
    range: frozenset[str] = Field(default_factory=frozenset, description="Allowed object entity types.")
    description: str = Field(default="", description="Predicate description.")
    is_functional: bool = Field(default=False, description="Whether this predicate is functional.")
    negation_of: Optional[str] = Field(default=None, description="Name of a predicate this predicate negates.")


class DomainSchemaResponse(FrozenModel):
    """Response body for GET /schema."""

    version: str = Field(description="Domain schema version.")
    entity_types: frozenset[str] = Field(default_factory=frozenset, description="Entity type names supported by this domain.")
    predicates: tuple[PredicateContract, ...] = Field(default=(), description="Predicate contract declarations.")


class SynonymCriteriaConfig(FrozenModel):
    """Response body for GET /synonym-criteria."""

    fuzzy_threshold: float = Field(description="Default fuzzy threshold for lexical matching.")
    embedding_threshold: float = Field(description="Default embedding cosine threshold.")
    entity_type_overrides: dict[str, dict[str, float]] = Field(default_factory=dict, description="Per-entity-type threshold overrides.")


class AuthorityInfo(FrozenModel):
    """Authority metadata entry."""

    name: str = Field(description="Authority identifier.")
    entity_types: frozenset[str] = Field(default_factory=frozenset, description="Entity types this authority can resolve.")
    base_url: str = Field(description="Authority API base URL.")
    requires_api_key: bool = Field(description="Whether this authority requires an API key.")


class AuthoritiesResponse(FrozenModel):
    """Response body for GET /authorities."""

    authorities: tuple[AuthorityInfo, ...] = Field(default=(), description="External authorities available to this domain.")


class ProvenanceRecord(FrozenModel):
    """Provenance input record used for confidence aggregation."""

    paper_id: str = Field(description="Source paper identifier.")
    section_type: str = Field(description="Section type (abstract, methods, etc).")
    paragraph_idx: int = Field(description="Paragraph index in section.")
    extraction_method: str = Field(description="Extraction method identifier.")
    confidence: float = Field(description="Per-record confidence.")
    study_type: Optional[str] = Field(default=None, description="Study type hint used for weighting.")


class ComputeConfidenceRequest(FrozenModel):
    """Request body for POST /compute-confidence."""

    provenance_records: tuple[ProvenanceRecord, ...] = Field(default=(), description="Provenance records to aggregate.")


class ComputeConfidenceResponse(FrozenModel):
    """Response body for POST /compute-confidence."""

    confidence: float = Field(description="Aggregated confidence [0.0, 0.99].")


class HealthResponse(FrozenModel):
    """Response body for GET /health."""

    status: Literal["ok"] = Field(description="Service health status.")
    version: str = Field(description="Service version string.")

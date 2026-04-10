"""HTTP request/response schemas for the identity server and domain service contract.

This module defines two groups of Pydantic models:

1. **Identity server schemas** — what callers (kgserver, ingestion pipeline) send
   to and receive from the identity server endpoints.

2. **Domain service schemas** — what the identity server sends to and receives from
   the pluggable domain service (authority lookup, survivor selection, synonym criteria).
"""

from typing import Optional
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Identity server — inbound request / outbound response schemas
# ---------------------------------------------------------------------------


class ResolveRequest(BaseModel):
    """Request body for POST /resolve."""

    mention: str = Field(description="Surface form of the entity mention to resolve.")
    entity_type: str = Field(description="Domain-specific entity type hint (e.g. 'drug', 'disease').")
    document_id: str = Field(description="Source document identifier for provenance.")
    embedding: Optional[list[float]] = Field(default=None, description="Pre-computed embedding vector for the mention.")


class ResolveResponse(BaseModel):
    """Response body for POST /resolve."""

    entity_id: str = Field(description="Resolved canonical or provisional entity ID.")


class PromoteRequest(BaseModel):
    """Request body for POST /promote."""

    entity_id: str = Field(description="ID of the entity to promote (may be provisional, canonical, or merged).")


class PromoteResponse(BaseModel):
    """Response body for POST /promote."""

    entity_id: str = Field(description="Canonical entity ID after promotion (or survivor ID if merged).")


class FindSynonymsRequest(BaseModel):
    """Request body for POST /find-synonyms."""

    entity_id: str = Field(description="ID of the entity to find synonyms for.")


class FindSynonymsResponse(BaseModel):
    """Response body for POST /find-synonyms."""

    synonym_ids: list[str] = Field(description="IDs of entities considered synonymous with the given entity.")


class MergeRequest(BaseModel):
    """Request body for POST /merge."""

    entity_ids: list[str] = Field(description="Full set of entity IDs to unify, including the survivor.")
    survivor_id: str = Field(description="The entity ID that will remain after the merge; must be in entity_ids.")


class MergeResponse(BaseModel):
    """Response body for POST /merge."""

    survivor_id: str = Field(description="The surviving entity ID after merge.")


class OnEntityAddedRequest(BaseModel):
    """Request body for POST /on-entity-added."""

    entity_id: str = Field(description="ID of the entity that was just added or updated.")
    context: dict = Field(default_factory=dict, description="Domain-defined context forwarded from the triggering operation.")


class HealthResponse(BaseModel):
    """Response body for GET /health."""

    status: str = Field(description="Service health status string.")


# ---------------------------------------------------------------------------
# Domain service — schemas sent TO and received FROM the domain service
# ---------------------------------------------------------------------------


class DomainCanonicalId(BaseModel):
    """Canonical ID as returned by the domain service resolve-authority endpoint."""

    id: str = Field(description="Canonical ID string from authoritative source (e.g. 'UMLS:C12345').")
    url: Optional[str] = Field(default=None, description="URL to the authoritative source page for this ID.")
    synonyms: list[str] = Field(default_factory=list, description="Alternative names/terms that map to this canonical ID.")


class DomainResolveAuthorityRequest(BaseModel):
    """Request body sent by the identity server to POST /resolve-authority on the domain service."""

    mention: str = Field(description="Surface form of the entity mention.")
    entity_type: str = Field(description="Domain-specific entity type hint.")
    document_id: str = Field(description="Source document identifier.")


class DomainResolveAuthorityResponse(BaseModel):
    """Response body from POST /resolve-authority on the domain service."""

    canonical_id: Optional[DomainCanonicalId] = Field(default=None, description="Canonical ID if found; null means no authority match.")


class DomainCandidateEntity(BaseModel):
    """A candidate entity sent to the domain service for survivor selection."""

    entity_id: str = Field(description="Entity ID.")
    name: str = Field(description="Primary name of the entity.")
    entity_type: str = Field(description="Domain-specific entity type.")
    status: str = Field(description="Entity status string ('canonical', 'provisional', 'merged').")
    usage_count: int = Field(description="Number of times this entity has been referenced.")
    confidence: float = Field(description="Resolution confidence score.")


class DomainSelectSurvivorRequest(BaseModel):
    """Request body sent by the identity server to POST /select-survivor on the domain service."""

    candidates: list[DomainCandidateEntity] = Field(description="All entities being considered for merge, including the intended survivor.")


class DomainSelectSurvivorResponse(BaseModel):
    """Response body from POST /select-survivor on the domain service."""

    survivor_id: str = Field(description="The entity ID that should survive the merge.")


class DomainSynonymCriteriaRequest(BaseModel):
    """Request body sent by the identity server to POST /synonym-criteria on the domain service."""

    entity_type: str = Field(description="Domain-specific entity type to fetch synonym criteria for.")


class DomainSynonymCriteriaResponse(BaseModel):
    """Response body from POST /synonym-criteria on the domain service."""

    similarity_threshold: float = Field(description="Minimum cosine similarity for two entities to be considered synonyms.")

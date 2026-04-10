"""Pydantic schemas for the medlit domain service HTTP contract.

These match the schemas in identity-server/identity_server/models.py exactly —
the identity server is the caller; this service is the implementer.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ResolveAuthorityRequest(BaseModel):
    """Request body from the identity server for POST /resolve-authority."""

    mention: str = Field(description="Surface form of the entity mention.")
    entity_type: str = Field(description="Domain-specific entity type hint (e.g. 'drug', 'disease').")
    document_id: str = Field(description="Source document identifier.")


class CanonicalIdResponse(BaseModel):
    """A canonical ID returned in POST /resolve-authority response."""

    id: str = Field(description="Canonical ID string (e.g. 'UMLS:C0006142', 'HGNC:1100').")
    url: Optional[str] = Field(default=None, description="URL to the authoritative source page.")
    synonyms: list[str] = Field(default_factory=list, description="Alternative names that map to this canonical ID.")


class ResolveAuthorityResponse(BaseModel):
    """Response body for POST /resolve-authority."""

    canonical_id: Optional[CanonicalIdResponse] = Field(
        default=None,
        description="Canonical ID if found; null means no authority match (entity stays provisional).",
    )


class CandidateEntity(BaseModel):
    """A candidate entity sent by the identity server for survivor selection."""

    entity_id: str = Field(description="Entity ID.")
    name: str = Field(description="Primary name of the entity.")
    entity_type: str = Field(description="Domain-specific entity type.")
    status: str = Field(description="Entity status string ('canonical', 'provisional', 'merged').")
    usage_count: int = Field(description="Number of times this entity has been referenced.")
    confidence: float = Field(description="Resolution confidence score.")


class SelectSurvivorRequest(BaseModel):
    """Request body from the identity server for POST /select-survivor."""

    candidates: list[CandidateEntity] = Field(description="All entities being considered for merge.")


class SelectSurvivorResponse(BaseModel):
    """Response body for POST /select-survivor."""

    survivor_id: str = Field(description="The entity ID that should survive the merge.")


class SynonymCriteriaRequest(BaseModel):
    """Request body from the identity server for POST /synonym-criteria."""

    entity_type: str = Field(description="Domain-specific entity type to fetch synonym criteria for.")


class SynonymCriteriaResponse(BaseModel):
    """Response body for POST /synonym-criteria."""

    similarity_threshold: float = Field(description="Minimum cosine similarity for two entities to be considered synonyms.")


class HealthResponse(BaseModel):
    """Response body for GET /health."""

    status: str = Field(description="Service health status.")

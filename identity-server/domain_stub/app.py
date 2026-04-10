"""Stub domain service for development and testing.

Implements the domain service HTTP contract with neutral defaults:
  - ``POST /resolve-authority`` — always returns no canonical ID (entity stays provisional)
  - ``POST /select-survivor``   — returns the candidate with the highest usage_count
  - ``POST /synonym-criteria``  — returns similarity_threshold = 0.90
  - ``GET  /health``            — returns {"status": "ok"}

This stub lets the identity server run without a real domain service.
"""

from fastapi import FastAPI

from identity_server.models import (
    DomainResolveAuthorityRequest,
    DomainResolveAuthorityResponse,
    DomainSelectSurvivorRequest,
    DomainSelectSurvivorResponse,
    DomainSynonymCriteriaRequest,
    DomainSynonymCriteriaResponse,
    HealthResponse,
)

app = FastAPI(
    title="Domain Stub",
    description="Neutral stub domain service for development and testing of the identity server.",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return service health status."""
    return HealthResponse(status="ok")


@app.post("/resolve-authority", response_model=DomainResolveAuthorityResponse)
async def resolve_authority(request: DomainResolveAuthorityRequest) -> DomainResolveAuthorityResponse:
    """Always return no canonical ID — the entity will remain provisional."""
    return DomainResolveAuthorityResponse(canonical_id=None)


@app.post("/select-survivor", response_model=DomainSelectSurvivorResponse)
async def select_survivor(request: DomainSelectSurvivorRequest) -> DomainSelectSurvivorResponse:
    """Return the candidate with the highest usage_count (first if tied)."""
    if not request.candidates:
        raise ValueError("candidates list must not be empty")
    best = max(request.candidates, key=lambda c: c.usage_count)
    return DomainSelectSurvivorResponse(survivor_id=best.entity_id)


@app.post("/synonym-criteria", response_model=DomainSynonymCriteriaResponse)
async def synonym_criteria(request: DomainSynonymCriteriaRequest) -> DomainSynonymCriteriaResponse:
    """Return the default similarity threshold of 0.90."""
    return DomainSynonymCriteriaResponse(similarity_threshold=0.90)

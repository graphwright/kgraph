"""Medlit domain service — FastAPI application.

Implements the four HTTP endpoints that the identity server calls to delegate
domain-specific logic:

    POST /resolve-authority   — authority lookup (UMLS, HGNC, RxNorm, UniProt, DBPedia)
    POST /select-survivor     — merge survivor selection
    POST /synonym-criteria    — per-entity-type cosine similarity threshold
    GET  /health              — health check

Set environment variables before starting:
    UMLS_API_KEY              — UMLS API key (optional; falls back to MeSH if absent)
    CANONICAL_ID_CACHE_PATH   — path to JSON cache file (default: ./canonical_id_cache.json)

Run with:
    uvicorn domain_service.app:app --host 0.0.0.0 --port 8080
"""

import logging

from fastapi import FastAPI

from .authority import resolve_authority
from .models import (
    HealthResponse,
    ResolveAuthorityRequest,
    ResolveAuthorityResponse,
    SelectSurvivorRequest,
    SelectSurvivorResponse,
    SynonymCriteriaRequest,
    SynonymCriteriaResponse,
)
from .survivor import select_survivor
from .synonym_criteria import get_threshold

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Medlit Domain Service",
    description="Domain-specific plugin for the graphwright identity server — biomedical authority lookup, survivor selection, and synonym criteria.",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health() -> HealthResponse:
    """Return service health status."""
    return HealthResponse(status="ok")


@app.post(
    "/resolve-authority",
    response_model=ResolveAuthorityResponse,
    summary="Look up canonical ID from medical ontology authorities",
    description="""
Attempt to resolve the given mention to a canonical ID from an authoritative
medical ontology source.

Authority chain by entity type:
- **disease / symptom / procedure** → UMLS (CUI), fallback MeSH
- **gene** → HGNC
- **drug / hormone** → RxNorm
- **protein / enzyme** → UniProt
- **institution** → ROR
- **author** → ORCID
- **all others** → DBPedia fallback

Returns ``null`` for ``canonical_id`` if no authority match is found.
Results are cached on disk to avoid redundant API calls.
""",
    tags=["Domain"],
)
async def resolve_authority_endpoint(request: ResolveAuthorityRequest) -> ResolveAuthorityResponse:
    """Resolve a mention to a canonical ID from medical authorities."""
    canonical_id = await resolve_authority(mention=request.mention, entity_type=request.entity_type)
    return ResolveAuthorityResponse(canonical_id=canonical_id)


@app.post(
    "/select-survivor",
    response_model=SelectSurvivorResponse,
    summary="Select the merge survivor from candidate entities",
    description="""
Given a set of candidate entities that the identity server has determined are
synonymous, select which one should survive the merge.

Preference order:
1. Canonical status over provisional
2. Has an authoritative entity ID (not a provisional UUID)
3. Higher usage count
4. Lexically smallest entity ID (stable tie-breaker)
""",
    tags=["Domain"],
)
async def select_survivor_endpoint(request: SelectSurvivorRequest) -> SelectSurvivorResponse:
    """Select the preferred merge survivor."""
    survivor_id = select_survivor(request.candidates)
    return SelectSurvivorResponse(survivor_id=survivor_id)


@app.post(
    "/synonym-criteria",
    response_model=SynonymCriteriaResponse,
    summary="Return the cosine similarity threshold for synonym detection",
    description="""
Return the minimum cosine similarity required for two entities of the given
type to be considered synonyms. Thresholds are tighter for entity types where
false-positive merges are costly (gene, drug) and looser for types with high
surface-form variation (pathway, anatomical structure).
""",
    tags=["Domain"],
)
async def synonym_criteria_endpoint(request: SynonymCriteriaRequest) -> SynonymCriteriaResponse:
    """Return the synonym similarity threshold for an entity type."""
    threshold = get_threshold(request.entity_type)
    return SynonymCriteriaResponse(similarity_threshold=threshold)

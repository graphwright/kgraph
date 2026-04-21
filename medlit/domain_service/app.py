"""Medlit domain service — FastAPI application."""

import logging
from importlib.metadata import PackageNotFoundError, version

from fastapi import FastAPI

from medlit.domain_spec import ENTITY_TYPE_SPECS, PREDICATES

from .authority import get_authorities_info, resolve_authority
from .models import (
    AuthoritiesResponse,
    ComputeConfidenceRequest,
    ComputeConfidenceResponse,
    DomainSchemaResponse,
    HealthResponse,
    PredicateContract,
    ResolveAuthorityRequest,
    ResolveAuthorityResponse,
    SelectSurvivorRequest,
    SelectSurvivorResponse,
    SynonymCriteriaConfig,
    SynonymCriteriaRequest,
    SynonymCriteriaResponse,
)
from .survivor import select_survivor
from .synonym_criteria import get_threshold

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    _APP_VERSION = version("medlit")
except PackageNotFoundError:
    _APP_VERSION = "0.1.0"

_SCHEMA_VERSION = "medlit-domain-v1"

app = FastAPI(
    title="Medlit Domain Service",
    description="Domain-specific microservice for medlit schema, authority resolution, survivor selection, and confidence/synonym policy.",
    version=_APP_VERSION,
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health() -> HealthResponse:
    """Return service health status."""
    return HealthResponse(status="ok", version=app.version)


def _type_name_from_class(cls: type) -> str:
    return cls.__name__.replace("Entity", "").lower().replace("_", "")


@app.get("/schema", response_model=DomainSchemaResponse, tags=["Schema"])
async def get_schema() -> DomainSchemaResponse:
    """Return immutable domain schema contract."""
    entity_types = frozenset(t for t in ENTITY_TYPE_SPECS if t != "default")
    predicates = tuple(
        PredicateContract(
            name=name,
            domain=frozenset(_type_name_from_class(t) for t in (spec.subject_types or [])),
            range=frozenset(_type_name_from_class(t) for t in (spec.object_types or [])),
            description=spec.description,
            is_functional=False,
            negation_of=None,
        )
        for name, spec in sorted(PREDICATES.items())
    )
    return DomainSchemaResponse(version=_SCHEMA_VERSION, entity_types=entity_types, predicates=predicates)


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
    if canonical_id is None:
        return ResolveAuthorityResponse(canonical_id=None, authority=None, confidence=None)
    return ResolveAuthorityResponse(canonical_id=canonical_id, authority=canonical_id.authority, confidence=canonical_id.confidence)


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
    candidates = list(request.candidates)
    if not candidates and request.entity_a and request.entity_b:
        candidates = [request.entity_a, request.entity_b]
    survivor_id = select_survivor(candidates)
    return SelectSurvivorResponse(survivor_id=survivor_id)


@app.get("/synonym-criteria", response_model=SynonymCriteriaConfig, tags=["Domain"])
async def synonym_criteria_config_endpoint() -> SynonymCriteriaConfig:
    """Return aggregate synonym criteria for startup-time caching."""
    return SynonymCriteriaConfig(
        fuzzy_threshold=0.90,
        embedding_threshold=0.90,
        entity_type_overrides={entity_type: {"embedding_threshold": get_threshold(entity_type)} for entity_type in ENTITY_TYPE_SPECS if entity_type != "default"},
    )


@app.post("/synonym-criteria", response_model=SynonymCriteriaResponse, tags=["Domain"])
async def synonym_criteria_endpoint(request: SynonymCriteriaRequest) -> SynonymCriteriaResponse:
    """Backward-compatible per-entity-type synonym threshold endpoint."""
    return SynonymCriteriaResponse(similarity_threshold=get_threshold(request.entity_type))


@app.get("/authorities", response_model=AuthoritiesResponse, tags=["Domain"])
async def authorities_endpoint() -> AuthoritiesResponse:
    """Return authority metadata for diagnostics."""
    return AuthoritiesResponse(authorities=get_authorities_info())


_STUDY_TYPE_WEIGHT = {
    "meta_analysis": 1.0,
    "systematic_review": 0.98,
    "rct": 0.95,
    "observational": 0.85,
    "review": 0.80,
    "case_report": 0.70,
}

_SECTION_WEIGHT = {
    "results": 1.0,
    "abstract": 0.95,
    "methods": 0.92,
    "discussion": 0.85,
    "introduction": 0.80,
}

_EXTRACTION_METHOD_WEIGHT = {
    "curated": 1.0,
    "rules": 0.95,
    "llm": 0.90,
}


@app.post("/compute-confidence", response_model=ComputeConfidenceResponse, tags=["Domain"])
async def compute_confidence_endpoint(request: ComputeConfidenceRequest) -> ComputeConfidenceResponse:
    """Aggregate confidence over provenance records with medlit domain weights."""
    if not request.provenance_records:
        return ComputeConfidenceResponse(confidence=0.0)

    weighted_sum = 0.0
    weight_total = 0.0
    for record in request.provenance_records:
        study_weight = _STUDY_TYPE_WEIGHT.get((record.study_type or "").lower().strip(), 0.80)
        section_weight = _SECTION_WEIGHT.get(record.section_type.lower().strip(), 0.80)
        extraction_weight = _EXTRACTION_METHOD_WEIGHT.get(record.extraction_method.lower().strip(), 0.85)
        weight = study_weight * section_weight * extraction_weight
        bounded_conf = min(1.0, max(0.0, record.confidence))
        weighted_sum += bounded_conf * weight
        weight_total += weight

    aggregate = (weighted_sum / weight_total) if weight_total > 0 else 0.0
    return ComputeConfidenceResponse(confidence=min(0.99, round(aggregate, 4)))

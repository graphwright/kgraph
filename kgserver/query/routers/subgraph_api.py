"""
REST Subgraph API router.

Returns subgraphs as JSON (entities + relationships) with flexible entity
selection (ID, name glob) and filters (hops, min_confidence, predicates).
LLM-friendly alternative to GraphQL.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from storage.interfaces import StorageInterface
from storage.models.entity import Entity
from storage.models.relationship import Relationship

from ..storage_factory import get_storage
from ..subgraph import resolve_seeds, extract_subgraph_rest
from ..graph_traversal import MAX_HOPS, MAX_NODES_LIMIT, DEFAULT_MAX_NODES


class SubgraphQueryEcho(BaseModel):
    """Echo of query params for LLM consumer."""

    seeds: list[str] = Field(description="Resolved seed entity IDs")
    hops: int = Field(description="Hops traversed")
    filters: dict = Field(default_factory=dict, description="min_confidence, predicates")
    truncated: bool = Field(
        default=False,
        description="True when max_nodes cap was hit",
    )


class SubgraphResponse(BaseModel):
    """Subgraph as entities + relationships + query echo."""

    entities: list[Entity] = Field(description="Entities in the subgraph")
    relationships: list[Relationship] = Field(description="Relationships in the subgraph")
    query: SubgraphQueryEcho = Field(description="Query echo for LLM consumer")


router = APIRouter(prefix="/api/v1/subgraph", tags=["Subgraph"])


@router.get(
    "",
    response_model=SubgraphResponse,
    summary="Get subgraph by entity selection",
    description="""
Return a merged subgraph (entities + relationships) from seed entities.

**Entity selection:** Use `entity` and/or `name`:
- entity=C0221406 — exact entity_id
- entity=C0221406,C0001623 — multiple seeds
- entity=cushing* or name=cushing* — glob on name (* → substring match)

**Filters:** min_confidence, predicates (comma-separated) reduce noise.

**Truncation:** When max_nodes is hit, query.truncated is true so the LLM knows.
""",
)
async def get_subgraph(
    entity: Optional[str] = Query(
        default=None,
        description="Entity ID(s) or glob pattern (comma-separated)",
    ),
    name: Optional[str] = Query(
        default=None,
        description="Glob pattern on entity name (e.g. cushing*)",
    ),
    hops: int = Query(
        default=2,
        ge=1,
        le=MAX_HOPS,
        description=f"Hops from seeds (1-{MAX_HOPS})",
    ),
    min_confidence: Optional[float] = Query(
        default=None,
        ge=0.0,
        le=1.0,
        description="Filter relationships by confidence",
    ),
    predicates: Optional[str] = Query(
        default=None,
        description="Comma-separated predicate filter (e.g. TREATS,CAUSES)",
    ),
    max_nodes: int = Query(
        default=DEFAULT_MAX_NODES,
        ge=1,
        le=MAX_NODES_LIMIT,
        description=f"Max nodes (1-{MAX_NODES_LIMIT})",
    ),
    storage: StorageInterface = Depends(get_storage),
) -> SubgraphResponse:
    """Get subgraph from entity/name selection."""
    if not entity and not name:
        raise HTTPException(
            status_code=400,
            detail="At least one of entity or name is required",
        )

    seed_ids = resolve_seeds(storage, entity_param=entity, name_param=name)

    filters: dict = {}
    if min_confidence is not None:
        filters["min_confidence"] = min_confidence
    if predicates and predicates.strip():
        filters["predicates"] = [p.strip() for p in predicates.split(",")]

    if not seed_ids:
        return SubgraphResponse(
            entities=[],
            relationships=[],
            query=SubgraphQueryEcho(
                seeds=[],
                hops=hops,
                filters=filters,
                truncated=False,
            ),
        )

    predicate_list = [p.strip() for p in predicates.split(",") if p.strip()] if predicates and predicates.strip() else None

    entities, relationships, truncated = extract_subgraph_rest(
        storage,
        seed_ids=seed_ids,
        hops=hops,
        max_nodes=max_nodes,
        min_confidence=min_confidence,
        predicates=predicate_list,
    )

    return SubgraphResponse(
        entities=entities,
        relationships=relationships,
        query=SubgraphQueryEcho(
            seeds=seed_ids,
            hops=hops,
            filters=filters,
            truncated=truncated,
        ),
    )

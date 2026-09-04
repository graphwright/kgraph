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
from ..graph_traversal import (
    MAX_HOPS,
    MAX_NODES_LIMIT,
    DEFAULT_MAX_NODES,
    _sanitize_source_documents,
    extract_subgraph_bfs,
)


class BfsSubgraphRequest(BaseModel):
    """JSON body for BFS subgraph POST."""

    seeds: list[str]
    max_hops: int = Field(ge=1, le=5)
    max_nodes: int = Field(default=500, ge=1, le=MAX_NODES_LIMIT)
    # topology_filter is for programmatic callers only. It is intentionally omitted
    # from the MCP tool description and all LLM-facing prompt documentation, which
    # present a clean two-filter model (node_filter, edge_filter, both presentation-
    # only). This is a deliberate simplification, not an oversight -- do not add it
    # to the LLM-facing docs.
    topology_filter: Optional[dict] = None
    node_filter: Optional[dict] = None
    edge_filter: Optional[dict] = None


class BfsSubgraphResponse(BaseModel):
    """BFS subgraph response with nodes and edges (full or stub)."""

    seeds: list[str]
    max_hops: int
    node_count: int
    edge_count: int
    truncated: bool
    nodes: list[dict]
    edges: list[dict]


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


@router.post(
    "",
    response_model=BfsSubgraphResponse,
    summary="BFS subgraph with JSON body",
    description="""
Return a subgraph via BFS from seed entities. Accepts JSON body with seeds, max_hops,
and optional node_filter/edge_filter for full vs stub serialization.
If any seed ID does not exist, returns 400.
""",
)
async def post_bfs_subgraph(
    body: BfsSubgraphRequest,
    storage: StorageInterface = Depends(get_storage),
) -> BfsSubgraphResponse:
    """POST BFS subgraph with JSON body."""
    if not body.seeds:
        raise HTTPException(status_code=400, detail="seeds must not be empty")

    unknown: list[str] = []
    for eid in body.seeds:
        if storage.get_entity(eid) is None:
            unknown.append(eid)
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown seed ID(s): {unknown}",
        )

    min_confidence = None
    if body.topology_filter and "min_confidence" in body.topology_filter:
        min_confidence = body.topology_filter["min_confidence"]

    nodes, edges, truncated = extract_subgraph_bfs(
        storage,
        seed_ids=body.seeds,
        hops=body.max_hops,
        max_nodes=body.max_nodes,
        min_confidence=min_confidence,
        node_filter=body.node_filter,
        edge_filter=body.edge_filter,
    )

    return BfsSubgraphResponse(
        seeds=body.seeds,
        max_hops=body.max_hops,
        node_count=len(nodes),
        edge_count=len(edges),
        truncated=truncated,
        nodes=nodes,
        edges=edges,
    )


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

    # Filter placeholder values (e.g. "paper_id") from source_documents
    relationships = [rel.model_copy(update={"source_documents": _sanitize_source_documents(rel.source_documents or [])}) for rel in relationships]

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

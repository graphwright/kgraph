"""
Graph visualization API router for the Knowledge Graph Server.

Provides endpoints for extracting subgraphs suitable for D3.js force-directed
graph visualization.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from storage.interfaces import StorageInterface

from ..storage_factory import get_storage
from ..graph_traversal import (
    GraphNode,
    GraphEdge,
    SubgraphResponse,
    extract_subgraph,
    extract_full_graph,
    MAX_HOPS,
    MAX_NODES_LIMIT,
    DEFAULT_MAX_NODES,
    _sanitize_source_documents,
)


class SearchResult(BaseModel):
    """A single entity search result."""

    entity_id: str = Field(description="The entity's unique ID")
    name: str = Field(description="Display name")
    entity_type: str = Field(description="Entity type (disease, drug, gene, etc.)")


class SearchResponse(BaseModel):
    """Response from entity search."""

    results: list[SearchResult] = Field(description="Matching entities")
    total: int = Field(description="Total matches (may exceed returned results)")
    query: str = Field(description="The search query")


router = APIRouter(prefix="/api/v1/graph", tags=["Graph Visualization"])


def _get_entity_types_from_domain_spec() -> dict[str, dict[str, str]]:
    """
    Load entity type metadata (color, label) from domain_spec.
    Returns {entity_type: {color, label}}. Includes 'default' for unknown types.
    """
    try:
        from domain_spec import ENTITY_CLASSES

        result: dict[str, dict[str, str]] = {}
        for cls in ENTITY_CLASSES:
            entity_type = cls.__name__.replace("Entity", "").lower()
            spec = getattr(cls, "spec", None)
            if spec is not None:
                color = getattr(spec, "color", "#78909c") or "#78909c"
                label = getattr(spec, "label", entity_type) or entity_type
            else:
                color = "#78909c"
                label = entity_type
            result[entity_type] = {"color": color, "label": label}
        result["default"] = {"color": "#78909c", "label": "Other"}
        return result
    except ImportError:
        return {"default": {"color": "#78909c", "label": "Other"}}


class EntityTypeSpec(BaseModel):
    """Color and label for an entity type."""

    color: str = Field(description="Hex color for visualization")
    label: str = Field(description="Display label")


class EntityTypesResponse(BaseModel):
    """Entity type metadata for graph visualization."""

    entity_types: dict[str, EntityTypeSpec] = Field(description="Map of entity_type to {color, label} from domain_spec")


@router.get(
    "/entity-types",
    response_model=EntityTypesResponse,
    summary="Get entity type metadata",
    description="""
Return entity type metadata (color, label) from domain_spec for graph visualization.
Used by the graph-viz UI to render node colors and legend.
""",
)
async def get_entity_types() -> EntityTypesResponse:
    """Get entity type colors and labels from domain_spec."""
    return EntityTypesResponse(entity_types=_get_entity_types_from_domain_spec())  # type: ignore[arg-type]


@router.get(
    "/search",
    response_model=SearchResponse,
    summary="Search entities by name",
    description="""
Search for entities by partial name match. Returns up to `limit` results
sorted by relevance (exact matches first, then by usage count).

Use this to find entity IDs for the subgraph endpoint.
""",
)
async def search_entities(
    q: str = Query(
        ...,
        min_length=1,
        description="Search query (searches entity names, case-insensitive)",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of results to return",
    ),
    entity_type: Optional[str] = Query(
        default=None,
        description="Filter by entity type (e.g., 'disease', 'drug', 'gene')",
    ),
    storage: StorageInterface = Depends(get_storage),
) -> SearchResponse:
    """
    Search for entities by name.

    Returns entities whose names contain the query string (case-insensitive).
    Results are returned with exact matches prioritized.
    """
    # Get matching entities
    entities = storage.get_entities(
        name_contains=q,
        entity_type=entity_type,
        limit=limit,
    )

    # Get total count for this query
    total = storage.count_entities(
        name_contains=q,
        entity_type=entity_type,
    )

    # Convert to search results
    results = [
        SearchResult(
            entity_id=e.entity_id,
            name=e.name or e.entity_id,
            entity_type=e.entity_type,
        )
        for e in entities
    ]

    # Sort: exact matches first, then by name length (shorter = more relevant)
    query_lower = q.lower()
    results.sort(
        key=lambda r: (
            0 if r.name.lower() == query_lower else 1,  # Exact match first
            0 if r.name.lower().startswith(query_lower) else 1,  # Prefix match second
            len(r.name),  # Shorter names first
        )
    )

    return SearchResponse(
        results=results,
        total=total,
        query=q,
    )


@router.get(
    "/subgraph",
    response_model=SubgraphResponse,
    summary="Get a subgraph for visualization",
    description="""
Retrieve a subgraph suitable for D3.js force-directed graph visualization.

**Modes:**
- **Subgraph mode** (default): BFS traversal from `center_id` for `hops` levels
- **Full graph mode**: Set `include_all=true` to get entire graph (up to `max_nodes`)

**Response format:**
- `nodes`: Array of nodes with `id`, `label`, `entity_type`, and `properties`
- `edges`: Array of edges with `source`, `target`, `label`, `predicate`, and `properties`
- `truncated`: True if the result was limited by `max_nodes`
""",
)
async def get_subgraph(
    center_id: Optional[str] = Query(
        default=None,
        description="Entity ID to center the subgraph on (required unless include_all=true)",
    ),
    hops: int = Query(
        default=2,
        ge=1,
        le=MAX_HOPS,
        description=f"Number of hops from center entity (1-{MAX_HOPS})",
    ),
    max_nodes: int = Query(
        default=DEFAULT_MAX_NODES,
        ge=1,
        le=MAX_NODES_LIMIT,
        description=f"Maximum number of nodes to return (1-{MAX_NODES_LIMIT})",
    ),
    include_all: bool = Query(
        default=False,
        description="If true, return entire graph instead of subgraph around center_id",
    ),
    storage: StorageInterface = Depends(get_storage),
) -> SubgraphResponse:
    """
    Retrieve a subgraph for visualization.

    If include_all is True, returns the entire graph (up to max_nodes).
    Otherwise, performs BFS from center_id for the specified number of hops.
    """
    if include_all:
        return extract_full_graph(storage, max_nodes=max_nodes)

    if not center_id:
        raise HTTPException(
            status_code=400,
            detail="center_id is required when include_all is false",
        )

    return extract_subgraph(
        storage,
        center_id=center_id,
        hops=hops,
        max_nodes=max_nodes,
    )


@router.get(
    "/node/{entity_id}",
    response_model=GraphNode,
    summary="Get details for a single node",
    description="Retrieve full details for a single entity as a graph node.",
)
async def get_node_details(
    entity_id: str,
    storage: StorageInterface = Depends(get_storage),
) -> GraphNode:
    """Get full details for a single node."""
    entity = storage.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    props = {
        "entity_id": entity.entity_id,
        "entity_type": entity.entity_type,
        "name": entity.name,
        "status": entity.status,
        "confidence": entity.confidence,
        "usage_count": entity.usage_count,
        "source": entity.source,
        "canonical_url": entity.canonical_url,
        "synonyms": entity.synonyms or [],
    }
    if entity.properties:
        for key in ("first_seen_document", "first_seen_section", "total_mentions", "supporting_documents"):
            if key in entity.properties:
                props[key] = entity.properties[key]
    return GraphNode(
        id=entity.entity_id,
        label=entity.name or entity.entity_id,
        entity_type=entity.entity_type,
        properties=props,
    )


@router.get(
    "/edge",
    response_model=GraphEdge,
    summary="Get details for a single edge",
    description="Retrieve full details for a single relationship as a graph edge.",
)
async def get_edge_details(
    subject_id: str = Query(..., description="Subject entity ID"),
    predicate: str = Query(..., description="Relationship predicate"),
    object_id: str = Query(..., description="Object entity ID"),
    storage: StorageInterface = Depends(get_storage),
) -> GraphEdge:
    """Get full details for a single edge."""
    rel = storage.get_relationship(
        subject_id=subject_id,
        predicate=predicate,
        object_id=object_id,
    )
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")

    label = rel.predicate.replace("_", " ").lower()

    props = {
        "subject_id": rel.subject_id,
        "predicate": rel.predicate,
        "object_id": rel.object_id,
        "confidence": rel.confidence,
        "source_documents": _sanitize_source_documents(rel.source_documents or []),
    }
    if rel.properties:
        for key in ("evidence_count", "strongest_evidence_quote", "evidence_confidence_avg"):
            if key in rel.properties:
                props[key] = rel.properties[key]
    return GraphEdge(
        source=rel.subject_id,
        target=rel.object_id,
        label=label,
        predicate=rel.predicate,
        properties=props,
    )


class MentionsResponse(BaseModel):
    """Mentions (provenance) for an entity."""

    mentions: list[dict] = Field(description="List of mention records from bundle provenance")


@router.get(
    "/entity/{entity_id}/mentions",
    response_model=MentionsResponse,
    summary="Get mentions for an entity",
    description="Return all mention records (provenance) for the given entity.",
)
async def get_entity_mentions(
    entity_id: str,
    storage: StorageInterface = Depends(get_storage),
) -> MentionsResponse:
    """Get mention provenance for an entity."""
    rows = storage.get_mentions_for_entity(entity_id)
    return MentionsResponse(mentions=[r.model_dump() for r in rows])


class EvidenceResponse(BaseModel):
    """Evidence for a relationship."""

    evidence: list[dict] = Field(description="List of evidence records for the relationship")


@router.get(
    "/edge/evidence",
    response_model=EvidenceResponse,
    summary="Get evidence for an edge",
    description="Return evidence records for the relationship (subject_id, predicate, object_id).",
)
async def get_edge_evidence(
    subject_id: str = Query(..., description="Subject entity ID"),
    predicate: str = Query(..., description="Relationship predicate"),
    object_id: str = Query(..., description="Object entity ID"),
    storage: StorageInterface = Depends(get_storage),
) -> EvidenceResponse:
    """Get evidence for a relationship."""
    rows = storage.get_evidence_for_relationship(
        subject_id=subject_id,
        predicate=predicate,
        object_id=object_id,
    )
    return EvidenceResponse(evidence=[r.model_dump() for r in rows])

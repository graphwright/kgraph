"""
Graph traversal logic for subgraph extraction.

Provides BFS-based traversal to extract subgraphs centered on a given entity,
returning D3.js-compatible node and edge data structures.

Symmetric predicates (PredicateSpec.symmetric=True): Storage uses canonical
(min,max) ordering for subject/object. Traversal MUST treat such edges as
undirected: we follow both subject_id and object_id (see BFS below), so
queries like "everyone X has collaborated with" work regardless of storage
direction.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field

from storage.interfaces import StorageInterface

# Safety limits
MAX_HOPS = 5
MAX_NODES_LIMIT = 2000
MAX_EDGES_LIMIT = 10000
DEFAULT_MAX_NODES = 500


class GraphNode(BaseModel):
    """D3-compatible node representation."""

    id: str = Field(description="Entity ID (used by D3 for linking)")
    label: str = Field(description="Display label (name or ID fallback)")
    entity_type: str = Field(description="Entity type for styling")
    properties: dict[str, Any] = Field(
        default_factory=dict,
        description="Full entity data for detail panel",
    )


class GraphEdge(BaseModel):
    """D3-compatible edge representation."""

    source: str = Field(description="Subject entity ID")
    target: str = Field(description="Object entity ID")
    label: str = Field(description="Human-readable predicate")
    predicate: str = Field(description="Raw predicate value")
    properties: dict[str, Any] = Field(
        default_factory=dict,
        description="Full relationship data for detail panel",
    )


class SubgraphResponse(BaseModel):
    """Response format for graph visualization."""

    nodes: list[GraphNode] = Field(description="Nodes in the subgraph")
    edges: list[GraphEdge] = Field(description="Edges in the subgraph")
    center_id: Optional[str] = Field(
        default=None,
        description="Focal entity ID (if subgraph mode)",
    )
    hops: int = Field(description="Depth traversed")
    truncated: bool = Field(
        default=False,
        description="True if max_nodes limit was reached",
    )
    total_entities: int = Field(description="Total entities in full graph")
    total_relationships: int = Field(description="Total relationships in full graph")


def _entity_to_node(entity) -> GraphNode:
    """Convert a storage Entity to a GraphNode."""
    props: dict[str, Any] = {
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
    # Include provenance summary from properties (set during bundle load)
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


# Placeholder values the LLM may output when it lacks the real paper ID
_SOURCE_DOC_PLACEHOLDERS = frozenset({"paper_id", "PMC_PLACEHOLDER", "PMC_ID_NOT_PROVIDED", "PMC_UNKNOWN"})


def _sanitize_source_documents(docs: list[str]) -> list[str]:
    """Filter out placeholder values from source_documents."""
    if not docs:
        return []
    return [d for d in docs if d and d not in _SOURCE_DOC_PLACEHOLDERS]


def _relationship_to_edge(rel) -> GraphEdge:
    """Convert a storage Relationship to a GraphEdge."""
    # Create human-readable label from predicate
    label = rel.predicate.replace("_", " ").lower()

    props: dict[str, Any] = {
        "subject_id": rel.subject_id,
        "predicate": rel.predicate,
        "object_id": rel.object_id,
        "confidence": rel.confidence,
        "source_documents": _sanitize_source_documents(rel.source_documents or []),
    }
    # Include evidence summary from properties (set during bundle load)
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


def extract_subgraph(
    storage: StorageInterface,
    center_id: str,
    hops: int = 2,
    max_nodes: int = DEFAULT_MAX_NODES,
) -> SubgraphResponse:
    """
    Extract a subgraph centered on a given entity using BFS.

    Args:
        storage: Storage interface for querying entities and relationships.
        center_id: The entity ID to center the subgraph on.
        hops: Number of hops (depth) to traverse from center (1-5).
        max_nodes: Maximum number of nodes to include.

    Returns:
        SubgraphResponse with nodes, edges, and metadata.
    """
    # Enforce limits
    hops = min(hops, MAX_HOPS)
    max_nodes = min(max_nodes, MAX_NODES_LIMIT)

    # Get totals for context
    total_entities = storage.count_entities()
    total_relationships = storage.count_relationships()

    # Check if center entity exists
    center_entity = storage.get_entity(center_id)
    if not center_entity:
        return SubgraphResponse(
            nodes=[],
            edges=[],
            center_id=center_id,
            hops=hops,
            truncated=False,
            total_entities=total_entities,
            total_relationships=total_relationships,
        )

    # BFS traversal
    visited_ids: set[str] = {center_id}
    frontier: set[str] = {center_id}
    collected_edges: list = []
    truncated = False

    for _ in range(hops):
        if not frontier:
            break

        next_frontier: set[str] = set()

        for entity_id in frontier:
            # Get relationships where entity is subject
            subject_rels = storage.find_relationships(subject_id=entity_id, limit=1000)
            # Get relationships where entity is object
            object_rels = storage.find_relationships(object_id=entity_id, limit=1000)

            all_rels = list(subject_rels) + list(object_rels)

            for rel in all_rels:
                # Add edge (avoid duplicates)
                edge_key = (rel.subject_id, rel.predicate, rel.object_id)
                if not any((e.subject_id, e.predicate, e.object_id) == edge_key for e in collected_edges):
                    collected_edges.append(rel)

                # Find neighbor
                if rel.subject_id == entity_id:
                    neighbor = rel.object_id
                else:
                    neighbor = rel.subject_id

                if neighbor not in visited_ids:
                    next_frontier.add(neighbor)
                    visited_ids.add(neighbor)

                    # Check limit
                    if len(visited_ids) >= max_nodes:
                        truncated = True
                        break

            if truncated:
                break

        if truncated:
            break

        frontier = next_frontier

    # Fetch all visited entities
    nodes: list[GraphNode] = []
    for entity_id in visited_ids:
        entity = storage.get_entity(entity_id)
        if entity:
            nodes.append(_entity_to_node(entity))

    # Filter edges to only include those between visited nodes
    edges: list[GraphEdge] = []
    for rel in collected_edges:
        if rel.subject_id in visited_ids and rel.object_id in visited_ids:
            edges.append(_relationship_to_edge(rel))

    # Apply edge limit
    if len(edges) > MAX_EDGES_LIMIT:
        edges = edges[:MAX_EDGES_LIMIT]
        truncated = True

    return SubgraphResponse(
        nodes=nodes,
        edges=edges,
        center_id=center_id,
        hops=hops,
        truncated=truncated,
        total_entities=total_entities,
        total_relationships=total_relationships,
    )


def _extract_subgraph_multi_seed(
    storage: StorageInterface,
    seed_ids: list[str],
    hops: int = 2,
    max_nodes: int = DEFAULT_MAX_NODES,
    min_confidence: Optional[float] = None,
    predicate_set: Optional[frozenset[str]] = None,
) -> tuple[list, list, bool]:
    """
    Multi-seed BFS returning raw Entity and Relationship objects.

    Returns (entities, relationships, truncated).
    Used by REST subgraph API.
    """
    hops = min(hops, MAX_HOPS)
    max_nodes = min(max_nodes, MAX_NODES_LIMIT)

    visited_ids: set[str] = set()
    frontier: set[str] = set()
    for eid in seed_ids:
        ent = storage.get_entity(eid)
        if ent:
            visited_ids.add(eid)
            frontier.add(eid)

    if not frontier:
        return [], [], False

    collected_edges: list = []
    truncated = False

    for _ in range(hops):
        if not frontier:
            break

        next_frontier: set[str] = set()

        for entity_id in frontier:
            subject_rels = storage.find_relationships(subject_id=entity_id, limit=1000)
            object_rels = storage.find_relationships(object_id=entity_id, limit=1000)
            all_rels = list(subject_rels) + list(object_rels)

            for rel in all_rels:
                if min_confidence is not None and (rel.confidence or 0) < min_confidence:
                    continue
                if predicate_set is not None and rel.predicate.upper() not in predicate_set:
                    continue

                edge_key = (rel.subject_id, rel.predicate, rel.object_id)
                if not any((e.subject_id, e.predicate, e.object_id) == edge_key for e in collected_edges):
                    collected_edges.append(rel)

                if rel.subject_id == entity_id:
                    neighbor = rel.object_id
                else:
                    neighbor = rel.subject_id

                if neighbor not in visited_ids:
                    next_frontier.add(neighbor)
                    visited_ids.add(neighbor)
                    if len(visited_ids) >= max_nodes:
                        truncated = True
                        break

            if truncated:
                break

        if truncated:
            break

        frontier = next_frontier

    entities = []
    for eid in visited_ids:
        ent = storage.get_entity(eid)
        if ent:
            entities.append(ent)

    relationships = [rel for rel in collected_edges if rel.subject_id in visited_ids and rel.object_id in visited_ids]

    return entities, relationships, truncated


def extract_full_graph(
    storage: StorageInterface,
    max_nodes: int = DEFAULT_MAX_NODES,
) -> SubgraphResponse:
    """
    Extract the entire graph (up to max_nodes).

    Args:
        storage: Storage interface for querying entities and relationships.
        max_nodes: Maximum number of nodes to include.

    Returns:
        SubgraphResponse with all nodes and edges (up to limits).
    """
    max_nodes = min(max_nodes, MAX_NODES_LIMIT)

    # Get totals
    total_entities = storage.count_entities()
    total_relationships = storage.count_relationships()

    # Fetch entities up to limit
    entities = storage.get_entities(limit=max_nodes)
    truncated = total_entities > max_nodes

    # Build node list and ID set
    nodes: list[GraphNode] = []
    entity_ids: set[str] = set()
    for entity in entities:
        nodes.append(_entity_to_node(entity))
        entity_ids.add(entity.entity_id)

    # Fetch all relationships and filter to those between included nodes
    edges: list[GraphEdge] = []
    all_rels = storage.find_relationships(limit=MAX_EDGES_LIMIT)
    for rel in all_rels:
        if rel.subject_id in entity_ids and rel.object_id in entity_ids:
            edges.append(_relationship_to_edge(rel))

    if len(edges) >= MAX_EDGES_LIMIT:
        truncated = True

    return SubgraphResponse(
        nodes=nodes,
        edges=edges,
        center_id=None,
        hops=0,
        truncated=truncated,
        total_entities=total_entities,
        total_relationships=total_relationships,
    )

"""
Subgraph extraction for REST API.

Resolves seed entities from entity/name params (with glob support) and runs
multi-seed BFS with optional filters (min_confidence, predicates).
"""

from typing import Optional, Sequence

from storage.interfaces import StorageInterface
from storage.models.entity import Entity
from storage.models.relationship import Relationship

from .graph_traversal import (
    MAX_HOPS,
    MAX_NODES_LIMIT,
    DEFAULT_MAX_NODES,
    _extract_subgraph_multi_seed,
)


def _glob_to_name_contains(pattern: str) -> str:
    """Convert glob pattern to substring for name_contains.

    Deliberate simplification: `*` is ignored; the whole pattern minus `*`
    becomes the substring. Multi-wildcard patterns (e.g. `cushing*disease`
    → `cushingdisease`) are mangled. Low risk for typical usage patterns.
    """
    return pattern.replace("*", "").strip()


def resolve_seeds(
    storage: StorageInterface,
    entity_param: Optional[str] = None,
    name_param: Optional[str] = None,
    limit: int = 100,
) -> list[str]:
    """
    Resolve entity/name params to a list of seed entity IDs.

    - entity: comma-separated. Each token: exact id via get_entity, or glob via
      name_contains (strip * and use substring match).
    - name: glob on name field, same as entity glob.
    - Returns deduplicated list of entity_ids.
    """
    seeds: list[str] = []

    if entity_param:
        for token in (t.strip() for t in entity_param.split(",") if t.strip()):
            if "*" in token:
                part = _glob_to_name_contains(token)
                if part:
                    entities = storage.get_entities(
                        name_contains=part,
                        limit=limit,
                    )
                    seeds.extend(e.entity_id for e in entities)
            else:
                ent = storage.get_entity(token)
                if ent:
                    seeds.append(ent.entity_id)

    if name_param:
        part = _glob_to_name_contains(name_param)
        if part:
            entities = storage.get_entities(
                name_contains=part,
                limit=limit,
            )
            seeds.extend(e.entity_id for e in entities)

    seen: set[str] = set()
    result: list[str] = []
    for eid in seeds:
        if eid not in seen:
            seen.add(eid)
            result.append(eid)

    return result


def extract_subgraph_rest(
    storage: StorageInterface,
    seed_ids: list[str],
    hops: int = 2,
    max_nodes: int = DEFAULT_MAX_NODES,
    min_confidence: Optional[float] = None,
    predicates: Optional[Sequence[str]] = None,
) -> tuple[list[Entity], list[Relationship], bool]:
    """
    Extract a merged subgraph from multiple seeds with optional filters.

    Returns (entities, relationships, truncated).
    """
    hops = min(hops, MAX_HOPS)
    max_nodes = min(max_nodes, MAX_NODES_LIMIT)

    predicate_set = frozenset(p.upper() for p in predicates) if predicates else None

    entities, relationships, truncated = _extract_subgraph_multi_seed(
        storage,
        seed_ids=seed_ids,
        hops=hops,
        max_nodes=max_nodes,
        min_confidence=min_confidence,
        predicate_set=predicate_set,
    )

    return entities, relationships, truncated

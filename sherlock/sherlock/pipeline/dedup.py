"""Deduplication and alias resolution for Sherlock Holmes entities.

Reads PerStoryBundle JSON(s), resolves SAME_AS relationships (alias merges),
builds a canonical ID index, collapses entity fragments, and writes the
merged output as a unified bundle JSON.

Key differences vs medlit dedup:
- No external authority API lookup (fiction entities use synthetic IDs)
- Character alias handling is critical: "the King", "His Majesty",
  "Wilhelm Gottsreich Sigismond von Ormstein" → single canonical node
- SAME_AS edges extracted from LLM output drive merges
- Synonym-normalisation is also important: "Dr. Watson", "Watson",
  "Dr. John H. Watson", "the doctor" → Dr. Watson
"""

import json
import re
import uuid
from pathlib import Path
from typing import Any, Optional

from ..bundle_models import ExtractedEntityRow, PerStoryBundle, RelationshipRow

# ---------------------------------------------------------------------------
# Character alias normalisation map for "A Scandal in Bohemia"
# ---------------------------------------------------------------------------

_ALIAS_NORMALIZATIONS: dict[str, str] = {
    # Sherlock Holmes
    "holmes": "sherlock holmes",
    "the detective": "sherlock holmes",
    "the consulting detective": "sherlock holmes",
    "mr. holmes": "sherlock holmes",
    # Dr. Watson
    "watson": "dr. watson",
    "the doctor": "dr. watson",
    "dr. john h. watson": "dr. watson",
    "john watson": "dr. watson",
    "dr watson": "dr. watson",
    # Irene Adler
    "the woman": "irene adler",
    "miss adler": "irene adler",
    "the adventuress": "irene adler",
    # The King of Bohemia
    "the king": "king of bohemia",
    "his majesty": "king of bohemia",
    "the count von kramm": "king of bohemia",
    "count von kramm": "king of bohemia",
    "wilhelm gottsreich sigismond von ormstein": "king of bohemia",
    "his bohemian majesty": "king of bohemia",
    # Godfrey Norton
    "norton": "godfrey norton",
    "mr. norton": "godfrey norton",
    # Mrs. Hudson
    "mrs hudson": "mrs. hudson",
    # Locations
    "221b baker street": "221b baker street",
    "baker street": "baker street",
    "briony lodge": "briony lodge",
    "serpentine avenue": "briony lodge",  # address = lodge
}

SAME_AS_PREDICATE = "SAME_AS"


def _normalize_name(name: str) -> str:
    """Lowercase, strip, and apply alias normalisation."""
    n = name.lower().strip().rstrip(".")
    return _ALIAS_NORMALIZATIONS.get(n, n)


def _slug() -> str:
    """Synthetic merge key for entities without authoritative ID."""
    return "prov-" + uuid.uuid4().hex[:12]


def _build_name_type_index(bundle: PerStoryBundle) -> dict[tuple[str, str], str]:
    """Map (normalized_name, entity_class) -> canonical_id (first-pass index)."""
    index: dict[tuple[str, str], str] = {}

    for ent in bundle.entities:
        cid = ent.canonical_id or ent.id
        for name in [ent.name] + list(ent.synonyms):
            key = (_normalize_name(name), ent.entity_class)
            if key[0]:
                index.setdefault(key, cid)

    return index


def _resolve_same_as(bundle: PerStoryBundle) -> dict[str, str]:
    """Build entity_id -> canonical_id map by following SAME_AS edges.

    Also applies _ALIAS_NORMALIZATIONS to collapse well-known aliases.
    """
    # Step 1: id -> id union-find for SAME_AS
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent.get(x, x), parent.get(x, x))
            x = parent.get(x, x)
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    # Register all entity IDs
    id_to_name: dict[str, str] = {ent.id: ent.name for ent in bundle.entities}

    for rel in bundle.relationships:
        if rel.predicate.upper() == SAME_AS_PREDICATE:
            union(rel.subject, rel.object_id)

    # Build merge map: local_id -> canonical representative id
    merge_map: dict[str, str] = {eid: find(eid) for eid in id_to_name}

    return merge_map


def _collapse_entities(bundle: PerStoryBundle, merge_map: dict[str, str]) -> list[ExtractedEntityRow]:
    """Merge entity rows according to merge_map; accumulate synonyms and descriptions."""
    canonical_entities: dict[str, ExtractedEntityRow] = {}

    for ent in bundle.entities:
        cid = merge_map.get(ent.id, ent.id)
        if cid not in canonical_entities:
            canonical_entities[cid] = ent.model_copy(update={"id": cid})
        else:
            existing = canonical_entities[cid]
            # Merge synonyms
            merged_syns = list(dict.fromkeys(list(existing.synonyms) + [ent.name] + list(ent.synonyms)))
            # Keep better canonical_id if available
            best_cid = existing.canonical_id or ent.canonical_id
            update: dict[str, Any] = {"synonyms": merged_syns, "canonical_id": best_cid}
            # Prefer longer description
            if not existing.description and ent.description:
                update["description"] = ent.description
            canonical_entities[cid] = existing.model_copy(update=update)

    return list(canonical_entities.values())


def _remap_relationships(bundle: PerStoryBundle, merge_map: dict[str, str]) -> list[RelationshipRow]:
    """Remap subject/object IDs in relationships through merge_map.

    Drop SAME_AS edges (they've been consumed). Drop self-loops.
    Deduplicate (subject, predicate, object) triples.
    """
    seen: set[tuple[str, str, str]] = set()
    result: list[RelationshipRow] = []

    for rel in bundle.relationships:
        if rel.predicate.upper() == SAME_AS_PREDICATE:
            continue
        new_sub = merge_map.get(rel.subject, rel.subject)
        new_obj = merge_map.get(rel.object_id, rel.object_id)
        if new_sub == new_obj:
            continue  # drop self-loops
        triple = (new_sub, rel.predicate.upper(), new_obj)
        if triple in seen:
            continue
        seen.add(triple)
        result.append(rel.model_copy(update={"subject": new_sub, "object_id": new_obj}))

    return result


def run_dedup(bundle: PerStoryBundle) -> PerStoryBundle:
    """Run full dedup pipeline on a single PerStoryBundle.

    Steps:
    1. Resolve SAME_AS edges → merge_map
    2. Apply alias normalizations to find additional merges
    3. Collapse entity rows
    4. Remap relationship IDs
    5. Return clean merged bundle

    Returns:
        New PerStoryBundle with deduplicated entities and remapped relationships.
    """
    # Step 1: Build merge map from SAME_AS edges
    merge_map = _resolve_same_as(bundle)

    # Step 2: Apply alias normalization on top of merge_map
    name_type_index = _build_name_type_index(bundle)

    for ent in bundle.entities:
        norm = _normalize_name(ent.name)
        # Find if another entity has the same normalized name
        key = (norm, ent.entity_class)
        if key in name_type_index:
            canonical_rep_id = name_type_index[key]
            if canonical_rep_id != ent.id:
                # Merge ent.id into canonical_rep_id
                current_rep = merge_map.get(ent.id, ent.id)
                canonical_rep = merge_map.get(canonical_rep_id, canonical_rep_id)
                if current_rep != canonical_rep:
                    # Prefer the entity with lower id (alphabetically) as survivor
                    survivor = min(current_rep, canonical_rep)
                    loser = max(current_rep, canonical_rep)
                    merge_map[loser] = survivor
                    # Update all existing entries pointing to loser
                    for k in list(merge_map.keys()):
                        if merge_map[k] == loser:
                            merge_map[k] = survivor
        else:
            name_type_index[key] = merge_map.get(ent.id, ent.id)
            # Also register synonyms
            for syn in ent.synonyms:
                syn_key = (_normalize_name(syn), ent.entity_class)
                name_type_index.setdefault(syn_key, merge_map.get(ent.id, ent.id))

    # Step 3 & 4: Collapse and remap
    collapsed_entities = _collapse_entities(bundle, merge_map)
    remapped_rels = _remap_relationships(bundle, merge_map)

    return PerStoryBundle(
        story=bundle.story,
        entities=collapsed_entities,
        evidence_entities=bundle.evidence_entities,
        relationships=remapped_rels,
        notes=bundle.notes,
    )


def run_dedup_from_file(input_path: Path, output_path: Path) -> dict[str, int]:
    """Load a bundle JSON, run dedup, write to output_path. Returns summary stats."""
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)
    bundle = PerStoryBundle.from_bundle_dict(data)

    orig_entities = len(bundle.entities)
    orig_rels = len(bundle.relationships)

    deduped = run_dedup(bundle)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(deduped.to_bundle_dict(), f, indent=2)

    return {
        "entities_before": orig_entities,
        "entities_after": len(deduped.entities),
        "entities_merged": orig_entities - len(deduped.entities),
        "relationships_before": orig_rels,
        "relationships_after": len(deduped.relationships),
    }

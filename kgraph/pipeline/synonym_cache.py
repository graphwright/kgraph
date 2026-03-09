"""Synonym / identity cache for Pass 2: persist and reuse SAME_AS links across runs.

Pass 2 loads the cache on startup and saves it at the end so that (name, type) → canonical_id
and known SAME_AS ambiguities are reused, making Pass 2 idempotent.
"""

import json
from pathlib import Path
from typing import Any, Optional


def _normalize(name: str) -> str:
    return name.lower().strip()


def load_synonym_cache(path: Path) -> dict[str, list[dict[str, Any]]]:
    """Load synonym cache from JSON file. Returns dict keyed by normalized name."""
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def save_synonym_cache(path: Path, data: dict[str, list[dict[str, Any]]]) -> None:
    """Save synonym cache to JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def lookup_entity(
    cache: dict[str, list[dict[str, Any]]],
    name: str,
    entity_class: str,
) -> tuple[Optional[str], Optional[list[dict[str, Any]]]]:
    """Look up canonical_id or ambiguities for (name, class).

    Returns:
        (canonical_id, ambiguities). canonical_id is set if a high-confidence resolved
        link exists for this (name, class). ambiguities is the list of SAME_AS entries
        for the normalized name (for review or merging).
    """
    key = _normalize(name)
    entries = cache.get(key, [])
    for entry in entries:
        entity_a = entry.get("entity_a", {})
        entity_b = entry.get("entity_b", {})
        resolution = entry.get("resolution")
        confidence = entry.get("confidence", 0)
        if resolution == "merged" and confidence >= 0.85:
            if entity_a.get("name", "").lower() == key and entity_a.get("class") == entity_class:
                return (entity_a.get("canonical_id"), entries)
            if entity_b.get("name", "").lower() == key and entity_b.get("class") == entity_class:
                return (entity_b.get("canonical_id"), entries)
    return (None, entries if entries else None)


def add_same_as_to_cache(
    cache: dict[str, list[dict[str, Any]]],
    entity_a: dict[str, Any],
    entity_b: dict[str, Any],
    confidence: float,
    asserted_by: str,
    resolution: Optional[str],
    source_papers: list[str],
) -> None:
    """Append a SAME_AS link to the in-memory cache (indexed by normalized names)."""
    for name in (_normalize(entity_a.get("name", "")), _normalize(entity_b.get("name", ""))):
        if not name:
            continue
        entry = {
            "entity_a": entity_a,
            "entity_b": entity_b,
            "confidence": confidence,
            "asserted_by": asserted_by,
            "resolution": resolution,
            "source_papers": source_papers,
        }
        if name not in cache:
            cache[name] = []
        cache[name].append(entry)

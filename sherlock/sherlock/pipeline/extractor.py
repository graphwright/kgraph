"""LLM extraction pipeline for Sherlock Holmes stories.

For each story chunk (paragraph window), calls the LLM with the Sherlock domain
prompt and collects entities + relationships into a PerStoryBundle.

Follows the medlit pass1_llm pattern: generate_json() → normalize → validate → store.
"""

import json
import re
import time
from pathlib import Path
from typing import Any, Optional

from ..bundle_models import (
    EvidenceEntityRow,
    ExtractedEntityRow,
    PerStoryBundle,
    RelationshipRow,
    StoryInfo,
)
from ..domain_spec import NORMALIZED_TO_BUNDLE, PROMPT_INSTRUCTIONS

# Placeholder the LLM is instructed to use for story_id in evidence IDs.
_STORY_ID_PLACEHOLDER = "==CURRENT_STORY=="


def _fix_evidence_story_id(evidence_id: str, story_id: str) -> str:
    """Replace placeholder story_id in evidence ID with actual."""
    return evidence_id.replace(_STORY_ID_PLACEHOLDER, story_id)


def _replace_placeholder_in_obj(obj: Any, story_id: str) -> None:
    """Recursively replace ==CURRENT_STORY== with story_id (in place)."""
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if isinstance(v, str):
                obj[k] = v.replace(_STORY_ID_PLACEHOLDER, story_id)
            else:
                _replace_placeholder_in_obj(v, story_id)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, str):
                obj[i] = item.replace(_STORY_ID_PLACEHOLDER, story_id)
            else:
                _replace_placeholder_in_obj(item, story_id)


def normalize_entity_type(raw_type: str) -> str:
    """Map raw LLM entity type string to bundle entity_class (PascalCase)."""
    if not raw_type or not str(raw_type).strip():
        return "Other"
    normalized = str(raw_type).strip().lower().replace(" ", "").replace("_", "")
    return NORMALIZED_TO_BUNDLE.get(normalized, "Other")


def _build_extraction_prompt(chunk_text: str, section: str, paragraph_idx: int, story_id: str) -> str:
    """Build the user message for a single story chunk.

    The system prompt is PROMPT_INSTRUCTIONS (domain spec). The user message
    provides the text chunk with context metadata.
    """
    return f"""Story ID: {story_id}
Section: {section}
Paragraph index: {paragraph_idx}

Please extract entities and relationships from the following story passage.
Use evidence ID format: {story_id}:{section}:{paragraph_idx}:llm

--- PASSAGE ---
{chunk_text}
--- END PASSAGE ---

Return a JSON object with:
{{
  "entities": [
    {{
      "id": "local_entity_id",
      "class": "Character|Location|PhysicalObject|Event|Occupation|Organization|Story",
      "name": "canonical name",
      "synonyms": ["alias1", "alias2"],
      "description": "brief description"
    }}
  ],
  "evidence_entities": [
    {{
      "id": "{story_id}:{section}:{paragraph_idx}:llm",
      "class": "Evidence",
      "story_id": "{story_id}",
      "section": "{section}",
      "paragraph_idx": {paragraph_idx},
      "text": "quoted passage text (first 200 chars)",
      "confidence": 0.8
    }}
  ],
  "relationships": [
    {{
      "subject": "local_entity_id",
      "predicate": "PREDICATE_NAME",
      "object": "local_entity_id",
      "evidence_ids": ["{story_id}:{section}:{paragraph_idx}:llm"],
      "confidence": 0.8,
      "properties": {{
        "narrator_trust": "watson_direct",
        "story_time": "investigation"
      }}
    }}
  ]
}}

Extract 3-5 relationships per paragraph. Be specific with predicates.
All entity IDs in relationships must match an id in the entities list.
"""


async def extract_chunk(
    llm: Any,
    chunk: dict,
    story_id: str,
    *,
    temperature: float = 0.1,
    max_tokens: int = 8192,
) -> dict:
    """Call LLM on a single chunk, return raw JSON bundle dict."""
    chunk_text = chunk["text"]
    section = chunk.get("section", "body")
    para_idx = chunk.get("paragraph_idx", 0)

    user_message = _build_extraction_prompt(chunk_text, section, para_idx, story_id)

    raw = await llm.generate_json(
        system_prompt=PROMPT_INSTRUCTIONS,
        user_message=user_message,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if not isinstance(raw, dict):
        return {}
    _replace_placeholder_in_obj(raw, story_id)
    return raw


def _parse_entities(raw_entities: list, story_id: str) -> list[ExtractedEntityRow]:
    """Parse and normalize entity rows from LLM output."""
    result = []
    seen_ids: set[str] = set()
    for en in raw_entities:
        if not isinstance(en, dict):
            continue
        name = en.get("name", "").strip()
        if not name:
            continue
        # Normalize entity_class
        raw_class = en.get("class", "")
        en["class"] = normalize_entity_type(raw_class)
        entity_id = en.get("id", "").strip() or re.sub(r"[^a-z0-9_]", "_", name.lower())
        if entity_id in seen_ids:
            # Deduplicate within a chunk — add suffix
            entity_id = f"{entity_id}_{len(seen_ids)}"
        seen_ids.add(entity_id)
        en["id"] = entity_id
        try:
            result.append(ExtractedEntityRow.model_validate(en))
        except Exception:
            pass
    return result


def _parse_evidence(raw_evidence: list, story_id: str) -> list[EvidenceEntityRow]:
    """Parse evidence entity rows."""
    result = []
    for ev in raw_evidence:
        if not isinstance(ev, dict):
            continue
        ev_id = _fix_evidence_story_id(str(ev.get("id", "")), story_id)
        ev["id"] = ev_id
        ev["story_id"] = story_id
        try:
            result.append(EvidenceEntityRow.model_validate(ev))
        except Exception:
            pass
    return result


def _parse_relationships(raw_rels: list, story_id: str) -> list[RelationshipRow]:
    """Parse relationship rows."""
    result = []
    for r in raw_rels:
        if not isinstance(r, dict):
            continue
        # Fix evidence IDs
        r["evidence_ids"] = [_fix_evidence_story_id(eid, story_id) for eid in (r.get("evidence_ids") or [])]
        r["source_stories"] = [story_id]
        # Promote narrator_trust / story_time from properties to top-level fields
        props = r.get("properties") or {}
        if props.get("narrator_trust") and not r.get("narrator_trust"):
            r["narrator_trust"] = props.get("narrator_trust")
        if props.get("story_time") and not r.get("story_time"):
            r["story_time"] = props.get("story_time")
        try:
            result.append(RelationshipRow.model_validate(r))
        except Exception:
            pass
    return result


def merge_bundles(bundles: list[PerStoryBundle]) -> PerStoryBundle:
    """Merge multiple per-chunk bundles into one for the whole story.

    Entities with the same (id, class) are deduplicated by keeping the first
    occurrence and accumulating synonyms.
    """
    if not bundles:
        raise ValueError("Cannot merge empty bundle list")

    story_info = bundles[0].story
    entity_map: dict[str, ExtractedEntityRow] = {}
    evidence_map: dict[str, EvidenceEntityRow] = {}
    all_rels: list[RelationshipRow] = []

    for bundle in bundles:
        for ent in bundle.entities:
            key = f"{ent.entity_class}:{ent.id}"
            if key not in entity_map:
                entity_map[key] = ent
            else:
                # Merge synonyms
                existing = entity_map[key]
                merged_syns = list(dict.fromkeys(list(existing.synonyms) + list(ent.synonyms)))
                entity_map[key] = existing.model_copy(update={"synonyms": merged_syns})
        for ev in bundle.evidence_entities:
            evidence_map[ev.id] = ev
        all_rels.extend(bundle.relationships)

    return PerStoryBundle(
        story=story_info,
        entities=list(entity_map.values()),
        evidence_entities=list(evidence_map.values()),
        relationships=all_rels,
    )


async def extract_story(
    story_info: StoryInfo,
    chunks: list[dict],
    llm: Any,
    *,
    temperature: float = 0.1,
    max_tokens: int = 8192,
    verbose: bool = True,
) -> PerStoryBundle:
    """Run extraction over all chunks of a story, return merged PerStoryBundle.

    Args:
        story_info: Story metadata.
        chunks: List of chunk dicts (from parser.chunk_story_windowed).
        llm: LLM instance with generate_json(system_prompt, user_message, ...) method.
        temperature: LLM sampling temperature.
        max_tokens: Max tokens per LLM call.
        verbose: Print progress to stderr.
    """
    import sys

    story_id = story_info.story_id
    chunk_bundles: list[PerStoryBundle] = []

    for i, chunk in enumerate(chunks):
        if verbose:
            print(f"  Chunk {i + 1}/{len(chunks)} (para {chunk.get('paragraph_idx')})", file=sys.stderr)
        start = time.perf_counter()
        try:
            raw = await extract_chunk(llm, chunk, story_id, temperature=temperature, max_tokens=max_tokens)
        except Exception as e:
            if verbose:
                print(f"  ERROR chunk {i}: {e}", file=sys.stderr)
            continue
        elapsed = time.perf_counter() - start

        raw_entities = raw.get("entities", [])
        raw_evidence = raw.get("evidence_entities", [])
        raw_rels = raw.get("relationships", [])

        entities = _parse_entities(raw_entities, story_id)
        evidence = _parse_evidence(raw_evidence, story_id)
        relationships = _parse_relationships(raw_rels, story_id)

        if verbose:
            print(
                f"    → {len(entities)} entities, {len(relationships)} rels [{elapsed:.1f}s]",
                file=sys.stderr,
            )

        chunk_bundles.append(
            PerStoryBundle(
                story=story_info,
                entities=entities,
                evidence_entities=evidence,
                relationships=relationships,
            )
        )

    if not chunk_bundles:
        return PerStoryBundle(story=story_info)

    merged = merge_bundles(chunk_bundles)
    if verbose:
        print(
            f"  Merged: {len(merged.entities)} entities, {len(merged.relationships)} rels",
            file=sys.stderr,
        )
    return merged

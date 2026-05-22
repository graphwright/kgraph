"""Bundle builder for Sherlock Holmes knowledge graph.

Reads a deduplicated PerStoryBundle JSON and produces a kgbundle directory
(entities.jsonl, relationships.jsonl, evidence.jsonl, manifest.json) that
kgserver can load directly.

Also adds story-level provenance: the Story entity is automatically connected
to all Character/Location/Object entities via DESCRIBED_IN relationships.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kgbundle import (
    BundleFile,
    BundleManifestV1,
    EntityRow,
    EvidenceRow,
    RelationshipRow as BundleRelationshipRow,
)

from ..bundle_models import PerStoryBundle


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _section_from_evidence_id(ev_id: str) -> str | None:
    parts = ev_id.split(":")
    return parts[1] if len(parts) >= 3 else None


def _build_entity_rows(bundle: PerStoryBundle) -> list[EntityRow]:
    """Convert extracted entity rows to kgbundle EntityRow objects."""
    now = _now_iso()
    story_id = bundle.story.story_id

    # Build usage map: entity_id -> set of evidence IDs from relationships
    usage_map: dict[str, set[str]] = {}
    doc_map: dict[str, list[str]] = {}
    for rel in bundle.relationships:
        for eid in [rel.subject, rel.object_id]:
            usage_map.setdefault(eid, set())
            usage_map[eid].update(rel.evidence_ids or [])
            doc_map.setdefault(eid, [])
            if story_id not in doc_map[eid]:
                doc_map[eid].append(story_id)

    rows: list[EntityRow] = []
    for ent in bundle.entities:
        evidence_ids = usage_map.get(ent.id, set())
        first_section = None
        if evidence_ids:
            first_eid = sorted(evidence_ids)[0]
            first_section = _section_from_evidence_id(first_eid)

        properties: dict[str, Any] = {}
        if ent.synonyms:
            properties["synonyms"] = list(ent.synonyms)
        if ent.description:
            properties["description"] = ent.description

        canonical_url = ent.canonical_id or None

        rows.append(
            EntityRow(
                entity_id=ent.canonical_id or ent.id,
                entity_type=ent.entity_class.lower(),
                name=ent.name,
                status="canonical",
                confidence=0.8,
                usage_count=max(1, len(doc_map.get(ent.id, []))),
                created_at=now,
                source="sherlock:extracted",
                canonical_url=canonical_url,
                properties=properties,
                first_seen_document=story_id,
                first_seen_section=first_section,
                total_mentions=len(evidence_ids),
                supporting_documents=doc_map.get(ent.id, [story_id]),
            )
        )

    return rows


def _build_canonical_id_map(bundle: PerStoryBundle) -> dict[str, str]:
    """Build local_id -> canonical_id map from entity rows."""
    return {ent.id: (ent.canonical_id or ent.id) for ent in bundle.entities}


def _build_relationship_rows(bundle: PerStoryBundle, cid_map: dict[str, str]) -> list[BundleRelationshipRow]:
    """Convert bundle RelationshipRows to kgbundle format."""
    now = _now_iso()
    story_id = bundle.story.story_id
    rows: list[BundleRelationshipRow] = []
    seen: set[tuple[str, str, str]] = set()

    for rel in bundle.relationships:
        sub_cid = cid_map.get(rel.subject, rel.subject)
        obj_cid = cid_map.get(rel.object_id, rel.object_id)
        if sub_cid == obj_cid:
            continue  # drop self-loops
        triple = (sub_cid, rel.predicate.upper(), obj_cid)
        if triple in seen:
            continue
        seen.add(triple)

        properties: dict[str, Any] = dict(rel.properties or {})
        if rel.narrator_trust:
            properties["narrator_trust"] = rel.narrator_trust
        if rel.story_time:
            properties["story_time"] = rel.story_time
        if rel.narrative_position is not None:
            properties["narrative_position"] = rel.narrative_position
        if rel.known_by:
            properties["known_by"] = list(rel.known_by)

        strongest = None
        if rel.provenance:
            prov_sentences = [p.sentence for p in rel.provenance if p.sentence]
            if prov_sentences:
                strongest = prov_sentences[0][:500]

        rows.append(
            BundleRelationshipRow(
                subject_id=sub_cid,
                object_id=obj_cid,
                predicate=rel.predicate.upper(),
                confidence=rel.confidence,
                source_documents=[story_id],
                created_at=now,
                properties=properties,
                evidence_count=len(rel.evidence_ids or []),
                strongest_evidence_quote=strongest,
            )
        )

    return rows


def _build_evidence_rows(bundle: PerStoryBundle, cid_map: dict[str, str]) -> list[EvidenceRow]:
    """Build evidence rows from evidence_entities + relationships."""
    story_id = bundle.story.story_id
    rows: list[EvidenceRow] = []

    # Build evidence_id -> evidence entity text map
    ev_text_map: dict[str, str] = {ev.id: (ev.text or "") for ev in bundle.evidence_entities}
    ev_section_map: dict[str, str | None] = {ev.id: ev.section for ev in bundle.evidence_entities}

    for rel in bundle.relationships:
        sub_cid = cid_map.get(rel.subject, rel.subject)
        obj_cid = cid_map.get(rel.object_id, rel.object_id)
        rel_key = f"{sub_cid}:{rel.predicate.upper()}:{obj_cid}"

        for ev_id in rel.evidence_ids or []:
            text_span = ev_text_map.get(ev_id, "")[:500]
            section = ev_section_map.get(ev_id) or _section_from_evidence_id(ev_id)
            if not text_span:
                continue
            rows.append(
                EvidenceRow(
                    relationship_key=rel_key,
                    document_id=story_id,
                    section=section,
                    start_offset=0,
                    end_offset=len(text_span),
                    text_span=text_span,
                    confidence=rel.confidence,
                    supports=True,
                )
            )

    return rows


def _add_story_provenance_relationships(
    bundle: PerStoryBundle,
    entity_rows: list[EntityRow],
    rel_rows: list[BundleRelationshipRow],
    cid_map: dict[str, str],
) -> None:
    """Add DESCRIBED_IN edges from all non-Story entities to the Story entity.

    This provenance expansion is crucial for graph density: every entity
    extracted from a story is explicitly connected to the story node.
    """
    now = _now_iso()
    story_id = bundle.story.story_id

    # Find story entity canonical ID
    story_canonical: str | None = None
    for ent in bundle.entities:
        if ent.entity_class.lower() == "story":
            story_canonical = ent.canonical_id or ent.id
            break

    if not story_canonical:
        # Create a synthetic story entity ID
        story_canonical = f"holmes:story:{bundle.story.story_id}"

    existing_described = {(r.subject_id, r.predicate) for r in rel_rows}

    for ent_row in entity_rows:
        if ent_row.entity_type == "story":
            continue
        key = (ent_row.entity_id, "DESCRIBED_IN")
        if key in existing_described:
            continue
        rel_rows.append(
            BundleRelationshipRow(
                subject_id=ent_row.entity_id,
                object_id=story_canonical,
                predicate="DESCRIBED_IN",
                confidence=1.0,
                source_documents=[story_id],
                created_at=now,
                properties={"narrator_trust": "narrator"},
                evidence_count=0,
            )
        )


def build_bundle(
    bundle: PerStoryBundle,
    output_dir: Path,
    *,
    add_story_provenance: bool = True,
) -> Path:
    """Build kgbundle from a deduplicated PerStoryBundle.

    Writes:
        {output_dir}/entities.jsonl
        {output_dir}/relationships.jsonl
        {output_dir}/evidence.jsonl
        {output_dir}/manifest.json

    Returns output_dir.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    now = _now_iso()
    story_id = bundle.story.story_id

    cid_map = _build_canonical_id_map(bundle)
    entity_rows = _build_entity_rows(bundle)
    rel_rows = _build_relationship_rows(bundle, cid_map)
    ev_rows = _build_evidence_rows(bundle, cid_map)

    if add_story_provenance:
        _add_story_provenance_relationships(bundle, entity_rows, rel_rows, cid_map)

    # Write entities.jsonl
    entities_path = output_dir / "entities.jsonl"
    with open(entities_path, "w", encoding="utf-8") as f:
        for row in entity_rows:
            f.write(row.model_dump_json() + "\n")

    # Write relationships.jsonl
    rels_path = output_dir / "relationships.jsonl"
    with open(rels_path, "w", encoding="utf-8") as f:
        for row in rel_rows:
            f.write(row.model_dump_json() + "\n")

    # Write evidence.jsonl
    ev_path = output_dir / "evidence.jsonl"
    with open(ev_path, "w", encoding="utf-8") as f:
        for row in ev_rows:
            f.write(row.model_dump_json() + "\n")

    # Write manifest.json
    manifest = BundleManifestV1(
        bundle_id=str(uuid.uuid4()),
        domain="sherlock",
        label=bundle.story.title or story_id,
        created_at=now,
        entities=BundleFile(path="entities.jsonl", format="jsonl"),
        relationships=BundleFile(path="relationships.jsonl", format="jsonl"),
        evidence=BundleFile(path="evidence.jsonl", format="jsonl"),
        metadata={
            "story_id": story_id,
            "story_title": bundle.story.title,
            "author": bundle.story.author,
            "year": bundle.story.year,
            "entity_count": len(entity_rows),
            "relationship_count": len(rel_rows),
            "evidence_count": len(ev_rows),
        },
    )
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest.model_dump_json(indent=2))

    return output_dir


def build_bundle_from_files(
    bundle_json_path: Path,
    output_dir: Path,
    *,
    add_story_provenance: bool = True,
) -> dict[str, int]:
    """Load deduplicated bundle JSON, build kgbundle, return summary stats."""
    with open(bundle_json_path, encoding="utf-8") as f:
        data = json.load(f)
    bundle = PerStoryBundle.from_bundle_dict(data)
    build_bundle(bundle, output_dir, add_story_provenance=add_story_provenance)
    return {
        "entities": len(bundle.entities),
        "relationships": len(bundle.relationships),
        "evidence": len(bundle.evidence_entities),
    }

"""Tests for Pass 3 bundle builder (medlit_merged + pass1_bundles -> kgbundle)."""

import json

import pytest

from examples.medlit.bundle_models import PerPaperBundle
from examples.medlit.pipeline.bundle_builder import (
    load_merged_output,
    load_pass1_bundles,
    run_pass3,
    _entity_usage_from_bundles,
)
from kgbundle import BundleManifestV1


@pytest.fixture
def minimal_merged_dir(tmp_path):
    """Minimal merged dir: entities.json, relationships.json, id_map.json, synonym_cache.json."""
    entities = [
        {
            "entity_id": "HGNC:1100",
            "canonical_id": "HGNC:1100",
            "class": "Gene",
            "name": "BRCA2",
            "synonyms": [],
            "source": "extracted",
            "source_papers": ["PMC12756687"],
        },
        {
            "entity_id": "C0006142",
            "canonical_id": "C0006142",
            "class": "Disease",
            "name": "breast cancer",
            "synonyms": [],
            "source": "extracted",
            "source_papers": ["PMC12756687"],
        },
    ]
    relationships = [
        {
            "subject": "HGNC:1100",
            "predicate": "INCREASES_RISK",
            "object": "C0006142",
            "evidence_ids": ["PMC12756687:abstract:0:llm"],
            "source_papers": ["PMC12756687"],
            "confidence": 0.55,
        },
    ]
    id_map = {
        "PMC12756687": {
            "g01": "HGNC:1100",
            "e01": "C0006142",
        },
    }
    (tmp_path / "entities.json").write_text(json.dumps(entities, indent=2), encoding="utf-8")
    (tmp_path / "relationships.json").write_text(json.dumps(relationships, indent=2), encoding="utf-8")
    (tmp_path / "id_map.json").write_text(json.dumps(id_map, indent=2), encoding="utf-8")
    (tmp_path / "synonym_cache.json").write_text("{}", encoding="utf-8")
    return tmp_path


@pytest.fixture
def minimal_bundles_dir(tmp_path):
    """Minimal bundles dir: one paper_*.json with one relationship and matching evidence_entity."""
    bundle_data = {
        "paper": {"pmcid": "PMC12756687", "title": "Test", "authors": []},
        "entities": [
            {"id": "g01", "class": "Gene", "name": "BRCA2", "synonyms": [], "source": "extracted"},
            {"id": "e01", "class": "Disease", "name": "breast cancer", "synonyms": [], "source": "extracted"},
        ],
        "evidence_entities": [
            {
                "id": "PMC12756687:abstract:0:llm",
                "class": "Evidence",
                "paper_id": "PMC12756687",
                "text_span_id": "PMC12756687:abstract:0",
                "text": "BRCA2 increases risk of breast cancer",
                "confidence": 0.95,
                "extraction_method": "llm",
                "source": "extracted",
            },
        ],
        "relationships": [
            {
                "subject": "g01",
                "predicate": "INCREASES_RISK",
                "object": "e01",
                "evidence_ids": ["PMC12756687:abstract:0:llm"],
                "source_papers": ["PMC12756687"],
                "confidence": 0.55,
            },
        ],
        "notes": [],
    }
    bundles_dir = tmp_path / "bundles"
    bundles_dir.mkdir()
    (bundles_dir / "paper_PMC12756687.json").write_text(json.dumps(bundle_data, indent=2), encoding="utf-8")
    return bundles_dir


def test_run_pass3_produces_bundle_files(minimal_merged_dir, minimal_bundles_dir, tmp_path):
    """run_pass3 writes entities.jsonl, relationships.jsonl, evidence.jsonl, mentions.jsonl, manifest.json."""
    output_dir = tmp_path / "out"
    run_pass3(minimal_merged_dir, minimal_bundles_dir, output_dir)

    assert (output_dir / "entities.jsonl").exists()
    assert (output_dir / "relationships.jsonl").exists()
    assert (output_dir / "evidence.jsonl").exists()
    assert (output_dir / "mentions.jsonl").exists()
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "doc_assets.jsonl").exists()
    assert (output_dir / "docs" / "README.md").exists()

    with open(output_dir / "entities.jsonl", encoding="utf-8") as f:
        entity_lines = [line for line in f if line.strip()]
    assert len(entity_lines) >= 1

    with open(output_dir / "relationships.jsonl", encoding="utf-8") as f:
        rel_lines = [line for line in f if line.strip()]
    assert len(rel_lines) >= 1

    manifest_data = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    manifest = BundleManifestV1.model_validate(manifest_data)
    assert manifest.entities.path == "entities.jsonl"
    assert manifest.domain == "medlit"


def test_entity_row_has_usage_and_status(minimal_merged_dir, minimal_bundles_dir, tmp_path):
    """EntityRow in entities.jsonl has entity_id, status, usage_count/total_mentions from bundle scan."""
    output_dir = tmp_path / "out"
    run_pass3(minimal_merged_dir, minimal_bundles_dir, output_dir)

    with open(output_dir / "entities.jsonl", encoding="utf-8") as f:
        lines = [line for line in f if line.strip()]
    assert len(lines) >= 1
    ent = json.loads(lines[0])
    assert "entity_id" in ent
    assert ent["status"] in ("canonical", "provisional")
    assert "usage_count" in ent
    assert "total_mentions" in ent


def test_first_seen_section_populated_from_evidence_id(minimal_merged_dir, minimal_bundles_dir, tmp_path):
    """first_seen_section is parsed from evidence_id (format paper_id:section:paragraph_idx:method)."""
    output_dir = tmp_path / "out"
    run_pass3(minimal_merged_dir, minimal_bundles_dir, output_dir)

    with open(output_dir / "entities.jsonl", encoding="utf-8") as f:
        entities = [json.loads(line) for line in f if line.strip()]
    # minimal_bundles has evidence_id PMC12756687:abstract:0:llm -> section "abstract"
    entities_with_section = [e for e in entities if e.get("first_seen_section")]
    assert len(entities_with_section) >= 1, "At least one entity should have first_seen_section"
    assert any(e.get("first_seen_section") == "abstract" for e in entities_with_section)


def test_evidence_row_relationship_key_uses_merge_keys(minimal_merged_dir, minimal_bundles_dir, tmp_path):
    """EvidenceRow relationship_key uses merge keys (from id_map), not local ids."""
    output_dir = tmp_path / "out"
    run_pass3(minimal_merged_dir, minimal_bundles_dir, output_dir)

    with open(output_dir / "evidence.jsonl", encoding="utf-8") as f:
        lines = [line for line in f if line.strip()]
    assert len(lines) >= 1
    ev = json.loads(lines[0])
    # relationship_key must be subject:predicate:object with merge keys
    rk = ev["relationship_key"]
    parts = rk.split(":")
    assert len(parts) >= 3
    # Merge keys from id_map: g01 -> HGNC:1100, e01 -> C0006142
    assert "g01" not in rk and "e01" not in rk
    assert "HGNC:1100" in rk or "C0006142" in rk


def test_run_pass3_raises_when_id_map_missing(tmp_path, minimal_bundles_dir):
    """If id_map.json is missing in merged_dir, run_pass3 raises FileNotFoundError."""
    merged_dir = tmp_path / "merged"
    merged_dir.mkdir()
    (merged_dir / "entities.json").write_text("[]", encoding="utf-8")
    (merged_dir / "relationships.json").write_text("[]", encoding="utf-8")
    # No id_map.json

    output_dir = tmp_path / "out"
    with pytest.raises(FileNotFoundError) as exc_info:
        run_pass3(merged_dir, minimal_bundles_dir, output_dir)
    assert "id_map.json" in str(exc_info.value)


def test_load_merged_output_requires_id_map(tmp_path):
    """load_merged_output raises FileNotFoundError when id_map.json is missing."""
    merged_dir = tmp_path / "merged"
    merged_dir.mkdir()
    (merged_dir / "entities.json").write_text("[]", encoding="utf-8")
    (merged_dir / "relationships.json").write_text("[]", encoding="utf-8")

    with pytest.raises(FileNotFoundError) as exc_info:
        load_merged_output(merged_dir)
    assert "id_map.json" in str(exc_info.value)


def test_load_pass1_bundles(minimal_bundles_dir):
    """load_pass1_bundles returns list of (paper_id, PerPaperBundle)."""
    bundles = load_pass1_bundles(minimal_bundles_dir)
    assert len(bundles) == 1
    paper_id, bundle = bundles[0]
    assert paper_id == "PMC12756687"
    assert isinstance(bundle, PerPaperBundle)
    assert len(bundle.relationships) == 1
    assert len(bundle.evidence_entities) == 1


def test_provenance_denylist_excludes_pmc_placeholder(tmp_path):
    """Entities with only PMC_PLACEHOLDER in relationships get usage_count 0, first_seen_document None."""
    id_map = {"PMC_PLACEHOLDER": {"e1": "canon-abc123"}}
    bundle_data = {
        "paper": {"pmcid": "PMC_PLACEHOLDER", "title": "Placeholder", "authors": []},
        "entities": [{"id": "e1", "class": "Disease", "name": "pleural mesothelioma", "synonyms": [], "source": "extracted"}],
        "evidence_entities": [{"id": "PMC_PLACEHOLDER:results:0:llm", "class": "Evidence", "paper_id": "PMC_PLACEHOLDER", "text": "x", "confidence": 0.5, "source": "extracted"}],
        "relationships": [
            {"subject": "e1", "predicate": "ASSOCIATED_WITH", "object": "e1", "evidence_ids": ["PMC_PLACEHOLDER:results:0:llm"], "source_papers": ["PMC_PLACEHOLDER"]},
        ],
    }
    bundles_dir = tmp_path / "bundles"
    bundles_dir.mkdir()
    (bundles_dir / "paper_PMC_PLACEHOLDER.json").write_text(json.dumps(bundle_data, indent=2), encoding="utf-8")
    bundles = load_pass1_bundles(bundles_dir)
    usage = _entity_usage_from_bundles(bundles, id_map)
    rec = usage.get("canon-abc123", {})
    assert rec.get("usage_count", 0) == 0
    assert rec.get("first_seen_document") is None


def test_provenance_denylist_excludes_pmc_id_not_provided(tmp_path):
    """Entities with only PMC_ID_NOT_PROVIDED in relationships get usage_count 0, first_seen_document None."""
    id_map = {"PMC_ID_NOT_PROVIDED": {"e1": "canon-xyz789"}}
    bundle_data = {
        "paper": {"pmcid": "PMC_ID_NOT_PROVIDED", "title": "No ID", "authors": []},
        "entities": [{"id": "e1", "class": "Disease", "name": "foo", "synonyms": [], "source": "extracted"}],
        "evidence_entities": [{"id": "PMC_ID_NOT_PROVIDED:abstract:0:llm", "class": "Evidence", "paper_id": "PMC_ID_NOT_PROVIDED", "text": "x", "confidence": 0.5, "source": "extracted"}],
        "relationships": [
            {"subject": "e1", "predicate": "ASSOCIATED_WITH", "object": "e1", "evidence_ids": ["PMC_ID_NOT_PROVIDED:abstract:0:llm"], "source_papers": ["PMC_ID_NOT_PROVIDED"]},
        ],
    }
    bundles_dir = tmp_path / "bundles"
    bundles_dir.mkdir()
    (bundles_dir / "paper_PMC_ID_NOT_PROVIDED.json").write_text(json.dumps(bundle_data, indent=2), encoding="utf-8")
    bundles = load_pass1_bundles(bundles_dir)
    usage = _entity_usage_from_bundles(bundles, id_map)
    rec = usage.get("canon-xyz789", {})
    assert rec.get("usage_count", 0) == 0
    assert rec.get("first_seen_document") is None


def test_provenance_denylist_excludes_pmc_unknown(tmp_path):
    """Entities with only PMC_UNKNOWN in supporting_documents get usage_count 0."""
    id_map = {"PMC_UNKNOWN": {"e1": "canon-abc123"}}
    bundle_data = {
        "paper": {"pmcid": "PMC_UNKNOWN", "title": "Unknown", "authors": []},
        "entities": [{"id": "e1", "class": "Disease", "name": "foo", "synonyms": [], "source": "extracted"}],
        "evidence_entities": [],
        "relationships": [
            {"subject": "e1", "predicate": "ASSOCIATED_WITH", "object": "e2", "evidence_ids": ["ev1"], "source_papers": ["PMC_UNKNOWN"]},
        ],
    }
    # Need evidence_entities for the relationship to count
    bundle_data["evidence_entities"] = [{"id": "ev1", "class": "Evidence", "paper_id": "PMC_UNKNOWN", "text": "x", "confidence": 0.5, "source": "extracted"}]
    bundle_data["entities"].append({"id": "e2", "class": "Disease", "name": "bar", "synonyms": [], "source": "extracted"})
    id_map["PMC_UNKNOWN"]["e2"] = "canon-def456"
    bundles_dir = tmp_path / "bundles"
    bundles_dir.mkdir()
    (bundles_dir / "paper_PMC_UNKNOWN.json").write_text(json.dumps(bundle_data, indent=2), encoding="utf-8")
    bundles = load_pass1_bundles(bundles_dir)
    usage = _entity_usage_from_bundles(bundles, id_map)
    # canon-abc123 and canon-def456 get usage from evidence
    # But paper_id PMC_UNKNOWN is denylisted, so supporting_documents stays empty
    for _, rec in usage.items():
        assert "PMC_UNKNOWN" not in (rec.get("supporting_documents") or [])


def test_zero_mention_orphan_dropped(tmp_path):
    """Entity in relationship but with no evidence_ids gets usage_count 0 and is dropped."""
    entities = [
        {"entity_id": "canon-abc", "canonical_id": None, "class": "Drug", "name": "liproxstatin-1", "synonyms": [], "source": "extracted", "source_papers": []},
        {"entity_id": "HGNC:1100", "canonical_id": "HGNC:1100", "class": "Gene", "name": "BRCA2", "synonyms": [], "source": "extracted", "source_papers": []},
        {"entity_id": "C0006142", "canonical_id": "C0006142", "class": "Disease", "name": "breast cancer", "synonyms": [], "source": "extracted", "source_papers": []},
    ]
    relationships = [
        {"subject": "canon-abc", "predicate": "ASSOCIATED_WITH", "object": "HGNC:1100", "evidence_ids": [], "source_papers": ["PMC123"], "confidence": 0.5},
        {"subject": "HGNC:1100", "predicate": "INCREASES_RISK", "object": "C0006142", "evidence_ids": ["ev1"], "source_papers": ["PMC123"], "confidence": 0.8},
    ]
    id_map = {"PMC123": {"e1": "canon-abc", "g1": "HGNC:1100", "d1": "C0006142"}}
    bundle_data = {
        "paper": {"pmcid": "PMC123", "title": "T", "authors": []},
        "entities": [
            {"id": "e1", "class": "Drug", "name": "liproxstatin-1", "synonyms": [], "source": "extracted"},
            {"id": "g1", "class": "Gene", "name": "BRCA2", "synonyms": [], "source": "extracted"},
            {"id": "d1", "class": "Disease", "name": "breast cancer", "synonyms": [], "source": "extracted"},
        ],
        "evidence_entities": [{"id": "ev1", "class": "Evidence", "paper_id": "PMC123", "text": "BRCA2 increases risk", "confidence": 0.9, "source": "extracted"}],
        "relationships": [
            {"subject": "e1", "predicate": "ASSOCIATED_WITH", "object": "g1", "evidence_ids": [], "source_papers": ["PMC123"], "confidence": 0.5},
            {"subject": "g1", "predicate": "INCREASES_RISK", "object": "d1", "evidence_ids": ["ev1"], "source_papers": ["PMC123"], "confidence": 0.8},
        ],
        "notes": [],
    }
    merged_dir = tmp_path / "merged"
    merged_dir.mkdir()
    (merged_dir / "entities.json").write_text(json.dumps(entities, indent=2), encoding="utf-8")
    (merged_dir / "relationships.json").write_text(json.dumps(relationships, indent=2), encoding="utf-8")
    (merged_dir / "id_map.json").write_text(json.dumps(id_map, indent=2), encoding="utf-8")
    (merged_dir / "synonym_cache.json").write_text("{}", encoding="utf-8")
    bundles_dir = tmp_path / "bundles"
    bundles_dir.mkdir()
    (bundles_dir / "paper_PMC123.json").write_text(json.dumps(bundle_data, indent=2), encoding="utf-8")
    output_dir = tmp_path / "out"
    run_pass3(merged_dir, bundles_dir, output_dir)
    with open(output_dir / "entities.jsonl", encoding="utf-8") as f:
        entity_lines = [json.loads(line) for line in f if line.strip()]
    entity_ids = [e["entity_id"] for e in entity_lines]
    assert "canon-abc" not in entity_ids, "Zero-mention orphan should be dropped"
    assert "HGNC:1100" in entity_ids, "Entity with evidence should remain"
    # Orphan relationship guard: relationship referencing dropped canon-abc should not appear
    with open(output_dir / "relationships.jsonl", encoding="utf-8") as f:
        rel_lines = [json.loads(line) for line in f if line.strip()]
    rel_subjects = {r["subject_id"] for r in rel_lines}
    assert "canon-abc" not in rel_subjects, "Relationship referencing dropped entity should be filtered"


def test_phantom_document_id_raises(tmp_path):
    """Phantom document IDs (known LLM hallucinations) cause run_pass3 to raise ValueError."""
    from examples.medlit.pipeline.bundle_builder import PHANTOM_DOCUMENT_IDS

    phantom = next(iter(PHANTOM_DOCUMENT_IDS))  # e.g. "11362215"
    paper_id = f"PMC{phantom}"
    id_map = {paper_id: {"e1": "canon-phantom"}}
    entities = [{"entity_id": "canon-phantom", "canonical_id": None, "class": "Gene", "name": "YY1", "synonyms": [], "source": "extracted", "source_papers": []}]
    relationships = [{"subject": "canon-phantom", "predicate": "ASSOCIATED_WITH", "object": "canon-phantom", "evidence_ids": ["ev1"], "source_papers": [paper_id], "confidence": 0.9}]
    bundle_data = {
        "paper": {"pmcid": paper_id, "title": "Phantom", "authors": []},
        "entities": [{"id": "e1", "class": "Gene", "name": "YY1", "synonyms": [], "source": "extracted"}],
        "evidence_entities": [{"id": "ev1", "class": "Evidence", "paper_id": paper_id, "text": "YY1 in gastric cancer", "confidence": 0.9, "source": "extracted"}],
        "relationships": [{"subject": "e1", "predicate": "ASSOCIATED_WITH", "object": "e1", "evidence_ids": ["ev1"], "source_papers": [paper_id], "confidence": 0.9}],
        "notes": [],
    }
    merged_dir = tmp_path / "merged"
    merged_dir.mkdir()
    (merged_dir / "entities.json").write_text(json.dumps(entities, indent=2), encoding="utf-8")
    (merged_dir / "relationships.json").write_text(json.dumps(relationships, indent=2), encoding="utf-8")
    (merged_dir / "id_map.json").write_text(json.dumps(id_map, indent=2), encoding="utf-8")
    (merged_dir / "synonym_cache.json").write_text("{}", encoding="utf-8")
    bundles_dir = tmp_path / "bundles"
    bundles_dir.mkdir()
    (bundles_dir / f"paper_{paper_id}.json").write_text(json.dumps(bundle_data, indent=2), encoding="utf-8")
    output_dir = tmp_path / "out"
    with pytest.raises(ValueError) as exc_info:
        run_pass3(merged_dir, bundles_dir, output_dir)
    assert phantom in str(exc_info.value)
    assert "Phantom" in str(exc_info.value) or "hallucination" in str(exc_info.value).lower()

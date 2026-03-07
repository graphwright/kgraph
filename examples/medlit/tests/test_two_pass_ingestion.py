"""Integration test for Pass 2 (dedup) using pre-baked fixture bundles.

Uses fixture JSONs only; no live LLM calls. Pass 1 is tested separately
(manual run or --dry-run / mocked LLM).
"""

import json
import pytest
from pathlib import Path

from examples.medlit.bundle_models import PerPaperBundle
from examples.medlit.pipeline.dedup import _is_authoritative_id, run_pass2
from examples.medlit.pipeline.synonym_cache import load_synonym_cache

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "bundles"


@pytest.fixture
def fixture_bundle_dir(tmp_path):
    """Copy fixture bundles to a temp dir so Pass 2 can read them."""
    import shutil

    dest = tmp_path / "bundles"
    dest.mkdir()
    for f in FIXTURES_DIR.glob("paper_*.json"):
        shutil.copy(f, dest / f.name)
    return dest


def test_pass2_merges_same_name_class(fixture_bundle_dir, tmp_path):
    """Entities with same (name, class) across papers get the same canonical_id."""
    output_dir = tmp_path / "merged"
    result = run_pass2(
        bundle_dir=fixture_bundle_dir,
        output_dir=output_dir,
        synonym_cache_path=output_dir / "synonym_cache.json",
    )
    assert "error" not in result
    assert result["entities_count"] >= 1
    assert result["relationships_count"] >= 1

    with open(output_dir / "entities.json", encoding="utf-8") as f:
        entities = json.load(f)
    # "male breast cancer" (Disease) appears in both bundles → one canonical entity
    male_bc = [e for e in entities if e.get("name", "").lower() == "male breast cancer" and e.get("class") == "Disease"]
    assert len(male_bc) == 1, "male breast cancer (Disease) should merge to one entity"
    assert "canonical_id" in male_bc[0]
    assert len(male_bc[0].get("source_papers", [])) == 2, "merged entity should list both source papers"


def test_pass2_writes_synonym_cache(fixture_bundle_dir, tmp_path):
    """Pass 2 writes synonym_cache.json."""
    output_dir = tmp_path / "merged"
    run_pass2(
        bundle_dir=fixture_bundle_dir,
        output_dir=output_dir,
        synonym_cache_path=output_dir / "synonym_cache.json",
    )
    cache_path = output_dir / "synonym_cache.json"
    assert cache_path.exists()
    cache = load_synonym_cache(cache_path)
    assert isinstance(cache, dict)


def test_pass2_does_not_modify_input_bundles(fixture_bundle_dir, tmp_path):
    """Original bundle files are not modified (read-only)."""
    import os

    output_dir = tmp_path / "merged"
    path1 = fixture_bundle_dir / "paper_PMC12756687.json"
    mtime_before = os.path.getmtime(path1)
    run_pass2(
        bundle_dir=fixture_bundle_dir,
        output_dir=output_dir,
        synonym_cache_path=output_dir / "synonym_cache.json",
    )
    mtime_after = os.path.getmtime(path1)
    assert mtime_before == mtime_after, "Pass 2 must not modify input bundle files"


def test_pass2_writes_id_map(fixture_bundle_dir, tmp_path):
    """Pass 2 writes id_map.json so Pass 3 can resolve (paper_id, local_id) -> merge_key."""
    output_dir = tmp_path / "merged"
    run_pass2(
        bundle_dir=fixture_bundle_dir,
        output_dir=output_dir,
        synonym_cache_path=output_dir / "synonym_cache.json",
    )
    id_map_path = output_dir / "id_map.json"
    assert id_map_path.exists()
    with open(id_map_path, encoding="utf-8") as f:
        id_map = json.load(f)
    assert isinstance(id_map, dict)
    for paper_id, local_map in id_map.items():
        assert isinstance(paper_id, str)
        assert isinstance(local_map, dict)
        for local_id, merge_key in local_map.items():
            assert isinstance(local_id, str) and isinstance(merge_key, str)


def test_pass2_accumulates_relationship_sources(fixture_bundle_dir, tmp_path):
    """Merged relationships aggregate source_papers and evidence_ids."""
    output_dir = tmp_path / "merged"
    run_pass2(
        bundle_dir=fixture_bundle_dir,
        output_dir=output_dir,
        synonym_cache_path=output_dir / "synonym_cache.json",
    )
    with open(output_dir / "relationships.json", encoding="utf-8") as f:
        rels = json.load(f)
    assert len(rels) >= 1
    for r in rels:
        assert "subject" in r and "predicate" in r and "object" in r
        assert "source_papers" in r and isinstance(r["source_papers"], list)


def test_pass2_accumulates_provenance_from_evidence(fixture_bundle_dir, tmp_path):
    """Merged relationships have provenance built from evidence_entities (section, sentence)."""
    output_dir = tmp_path / "merged"
    run_pass2(
        bundle_dir=fixture_bundle_dir,
        output_dir=output_dir,
        synonym_cache_path=output_dir / "synonym_cache.json",
    )
    with open(output_dir / "relationships.json", encoding="utf-8") as f:
        rels = json.load(f)
    rels_with_evidence = [r for r in rels if r.get("evidence_ids")]
    assert len(rels_with_evidence) >= 1, "fixture bundles have relationships with evidence"
    for r in rels_with_evidence:
        assert "provenance" in r and isinstance(r["provenance"], list)
        assert len(r["provenance"]) >= 1, "each evidence_id should produce a provenance entry"
        entry = r["provenance"][0]
        assert "section" in entry
        assert "sentence" in entry


def test_fixture_bundles_load(fixture_bundle_dir):
    """Fixture bundles are valid PerPaperBundle."""
    for path in sorted(fixture_bundle_dir.glob("paper_*.json")):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        bundle = PerPaperBundle.from_bundle_dict(data)
        assert bundle.paper
        assert len(bundle.entities) >= 1
        assert isinstance(bundle.relationships, list)


def test_is_authoritative_id():
    """_is_authoritative_id returns True for ontology IDs, False for synthetic slugs."""
    assert _is_authoritative_id("C0006142") is True
    assert _is_authoritative_id("HGNC:1100") is True
    assert _is_authoritative_id("MeSH:D001943") is True
    assert _is_authoritative_id("RxNorm:161") is True
    assert _is_authoritative_id("P38398") is True
    assert _is_authoritative_id("DBPedia:Breast_cancer") is True
    assert _is_authoritative_id("prov-abc123") is False
    assert _is_authoritative_id("prov-960ca8acbab3") is False
    assert _is_authoritative_id("") is False


def test_pass2_output_has_entity_id_and_canonical_id_null_when_synthetic(fixture_bundle_dir, tmp_path):
    """Pass 2 output entities have entity_id (merge key) and canonical_id null when synthetic."""
    output_dir = tmp_path / "merged"
    run_pass2(
        bundle_dir=fixture_bundle_dir,
        output_dir=output_dir,
        synonym_cache_path=output_dir / "synonym_cache.json",
    )
    with open(output_dir / "entities.json", encoding="utf-8") as f:
        entities = json.load(f)
    for e in entities:
        assert "entity_id" in e, "every entity must have entity_id"
        if e["entity_id"].startswith("prov-"):
            assert e.get("canonical_id") is None, "synthetic entity_id must have canonical_id null"


def test_pass2_authoritative_id_from_bundle_preserved(tmp_path):
    """When a bundle entity has umls_id (or other authoritative ID), Pass 2 uses it as entity_id and canonical_id."""
    bundle_data = {
        "paper": {"pmcid": "PMCtest", "title": "Test", "authors": []},
        "entities": [
            {"id": "e1", "class": "Disease", "name": "breast cancer", "synonyms": [], "source": "extracted", "umls_id": "C0006142"},
        ],
        "evidence_entities": [],
        "relationships": [],
        "notes": [],
    }
    bundle_dir = tmp_path / "bundles"
    bundle_dir.mkdir()
    with open(bundle_dir / "paper_PMCtest.json", "w", encoding="utf-8") as f:
        json.dump(bundle_data, f, indent=2)
    output_dir = tmp_path / "merged"
    run_pass2(
        bundle_dir=bundle_dir,
        output_dir=output_dir,
        synonym_cache_path=output_dir / "synonym_cache.json",
    )
    with open(output_dir / "entities.json", encoding="utf-8") as f:
        entities = json.load(f)
    bc = [e for e in entities if e.get("name") == "breast cancer"]
    assert len(bc) == 1
    assert bc[0]["entity_id"] == "C0006142"
    assert bc[0]["canonical_id"] == "C0006142"

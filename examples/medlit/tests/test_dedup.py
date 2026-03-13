"""Tests for Pass 2 dedup: synonym indexing, namespace normalization, reconciliation."""

import json


from examples.medlit.bundle_models import ExtractedEntityRow, PerPaperBundle
from examples.medlit.pipeline.dedup import (
    _canonical_id_slug,
    _is_authoritative_id,
    _preferred_authoritative_id,
    run_pass2,
)


def test_synonym_indexing_merges_name_to_synonym(tmp_path):
    """Entity A has synonym X; entity B has name X (same class) -> merge to one canonical."""
    bundles = [
        (
            "paper1",
            PerPaperBundle(
                paper={"pmcid": "paper1", "title": "P1", "authors": []},
                entities=[
                    ExtractedEntityRow(
                        id="e1",
                        entity_class="Gene",
                        name="STAT3",
                        synonyms=["signal transducer and activator of transcription 3"],
                        source="extracted",
                    ),
                ],
                evidence_entities=[],
                relationships=[],
                notes=[],
            ),
        ),
        (
            "paper2",
            PerPaperBundle(
                paper={"pmcid": "paper2", "title": "P2", "authors": []},
                entities=[
                    ExtractedEntityRow(
                        id="e2",
                        entity_class="Gene",
                        name="signal transducer and activator of transcription 3",
                        synonyms=["STAT3"],
                        source="extracted",
                    ),
                ],
                evidence_entities=[],
                relationships=[],
                notes=[],
            ),
        ),
    ]
    bundle_dir = tmp_path / "bundles"
    bundle_dir.mkdir()
    for pid, b in bundles:
        (bundle_dir / f"paper_{pid}.json").write_text(
            json.dumps(b.to_bundle_dict(), indent=2),
            encoding="utf-8",
        )
    output_dir = tmp_path / "merged"
    result = run_pass2(bundle_dir=bundle_dir, output_dir=output_dir)
    assert "error" not in result
    with open(output_dir / "entities.json", encoding="utf-8") as f:
        entities = json.load(f)
    gene_entities = [e for e in entities if e.get("class") == "Gene"]
    assert len(gene_entities) == 1, "STAT3 and full name should merge via synonym indexing"
    assert len(gene_entities[0].get("source_papers", [])) == 2


def test_synonym_indexing_does_not_merge_different_classes(tmp_path):
    """Same name/synonym but different entity_class -> do not merge."""
    bundles = [
        (
            "paper1",
            PerPaperBundle(
                paper={"pmcid": "paper1", "title": "P1", "authors": []},
                entities=[
                    ExtractedEntityRow(
                        id="e1",
                        entity_class="Gene",
                        name="BRCA1",
                        synonyms=[],
                        source="extracted",
                    ),
                ],
                evidence_entities=[],
                relationships=[],
                notes=[],
            ),
        ),
        (
            "paper2",
            PerPaperBundle(
                paper={"pmcid": "paper2", "title": "P2", "authors": []},
                entities=[
                    ExtractedEntityRow(
                        id="e2",
                        entity_class="Protein",
                        name="BRCA1",
                        synonyms=[],
                        source="extracted",
                    ),
                ],
                evidence_entities=[],
                relationships=[],
                notes=[],
            ),
        ),
    ]
    bundle_dir = tmp_path / "bundles"
    bundle_dir.mkdir()
    for pid, b in bundles:
        (bundle_dir / f"paper_{pid}.json").write_text(
            json.dumps(b.to_bundle_dict(), indent=2),
            encoding="utf-8",
        )
    output_dir = tmp_path / "merged"
    result = run_pass2(bundle_dir=bundle_dir, output_dir=output_dir)
    assert "error" not in result
    with open(output_dir / "entities.json", encoding="utf-8") as f:
        entities = json.load(f)
    brca1_entities = [e for e in entities if (e.get("name") or "").upper() == "BRCA1"]
    assert len(brca1_entities) == 2, "Gene and Protein with same name should not merge"


def test_spelling_normalization_merges_hyperglycaemia_hyperglycemia(tmp_path):
    """British/American spelling variants (hyperglycaemia/hyperglycemia) merge to one canonical."""
    bundles = [
        (
            "paper1",
            PerPaperBundle(
                paper={"pmcid": "paper1", "title": "P1", "authors": []},
                entities=[
                    ExtractedEntityRow(
                        id="e1",
                        entity_class="Biomarker",
                        name="hyperglycaemia",
                        synonyms=[],
                        source="extracted",
                    ),
                ],
                evidence_entities=[],
                relationships=[],
                notes=[],
            ),
        ),
        (
            "paper2",
            PerPaperBundle(
                paper={"pmcid": "paper2", "title": "P2", "authors": []},
                entities=[
                    ExtractedEntityRow(
                        id="e2",
                        entity_class="Biomarker",
                        name="hyperglycemia",
                        synonyms=[],
                        source="extracted",
                    ),
                ],
                evidence_entities=[],
                relationships=[],
                notes=[],
            ),
        ),
    ]
    bundle_dir = tmp_path / "bundles"
    bundle_dir.mkdir()
    for pid, b in bundles:
        (bundle_dir / f"paper_{pid}.json").write_text(
            json.dumps(b.to_bundle_dict(), indent=2),
            encoding="utf-8",
        )
    output_dir = tmp_path / "merged"
    result = run_pass2(bundle_dir=bundle_dir, output_dir=output_dir)
    assert "error" not in result
    with open(output_dir / "entities.json", encoding="utf-8") as f:
        entities = json.load(f)
    biomarker_entities = [e for e in entities if e.get("class") == "Biomarker" and "hyperglyc" in (e.get("name") or "").lower()]
    assert len(biomarker_entities) == 1, "hyperglycaemia and hyperglycemia should merge via spelling normalization"


def test_preferred_authoritative_id_prefers_hgnc_for_gene():
    """When Gene has both umls_id and hgnc_id, prefer hgnc_id."""
    e = ExtractedEntityRow(
        id="e1",
        entity_class="Gene",
        name="TP53",
        synonyms=[],
        umls_id="C0079419",
        hgnc_id="11998",
        source="extracted",
    )
    result = _preferred_authoritative_id(e, None)
    assert result == "HGNC:11998"


def test_preferred_authoritative_id_returns_umls_when_only_umls():
    """When Gene has only umls_id, return umls_id (no lookup without lookup object)."""
    e = ExtractedEntityRow(
        id="e1",
        entity_class="Gene",
        name="TP53",
        synonyms=[],
        umls_id="C0079419",
        source="extracted",
    )
    result = _preferred_authoritative_id(e, None)
    assert result == "C0079419"


def test_is_authoritative_id():
    """_is_authoritative_id correctly identifies authoritative vs prov- slugs."""
    assert _is_authoritative_id("HGNC:11998") is True
    assert _is_authoritative_id("C0079419") is True
    assert _is_authoritative_id("prov-abc123def456") is False
    assert _is_authoritative_id("MeSH:D001943") is True
    assert _is_authoritative_id("PMC11795198") is True


def test_canonical_id_slug_format():
    """_canonical_id_slug produces prov- prefixed hex."""
    slug = _canonical_id_slug()
    assert slug.startswith("prov-")
    assert len(slug) == len("prov-") + 12
    assert all(c in "0123456789abcdef" for c in slug[5:])

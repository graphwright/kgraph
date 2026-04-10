"""Tests for provenance expansion (Author, Institution, Paper, derived relationships)."""

from medlit.bundle_models import (
    AuthorInfo,
    ExtractedEntityRow,
    PaperInfo,
    PerPaperBundle,
    RelationshipRow,
)
from medlit.pipeline.provenance_expansion import expand_provenance
from medlit.pipeline.utils import canonicalize_symmetric


def test_canonicalize_symmetric() -> None:
    """canonicalize_symmetric returns (min, max) for deterministic storage."""
    assert canonicalize_symmetric("b", "a") == ("a", "b")
    assert canonicalize_symmetric("a", "b") == ("a", "b")
    assert canonicalize_symmetric("smith_j", "jones_m") == ("jones_m", "smith_j")


def test_expand_provenance_creates_author_institution_paper() -> None:
    """expand_provenance produces Author, Institution, Paper entities and derived relationships."""
    bundle = PerPaperBundle(
        paper=PaperInfo(
            title="Test Paper",
            authors=["Alice Smith", "Bob Jones"],
            author_details=[
                AuthorInfo(name="Alice Smith", affiliations=["Harvard Medical School"]),
                AuthorInfo(name="Bob Jones", affiliations=["MIT"]),
            ],
            document_id="PMC123",
        ),
        entities=[
            ExtractedEntityRow(id="Disease:diabetes", entity_class="Disease", name="diabetes"),
        ],
        relationships=[],
    )
    exp_entities, exp_rels = expand_provenance(bundle)

    entity_ids = {e.id for e in exp_entities}
    assert "Paper:PMC123" in entity_ids
    paper_entity = next(e for e in exp_entities if e.id == "Paper:PMC123")
    assert paper_entity.canonical_id == "PMC123"
    assert any("Author:" in eid and "smith" in eid.lower() for eid in entity_ids)
    assert any("Author:" in eid and "jones" in eid.lower() for eid in entity_ids)
    assert any("Institution:" in eid for eid in entity_ids)

    preds = {r.predicate for r in exp_rels}
    assert "AUTHORED" in preds
    assert "AFFILIATED_WITH" in preds
    assert "DESCRIBED" in preds
    assert "COAUTHORED_WITH" not in preds


def test_expand_provenance_described_top_two_by_relationship_count() -> None:
    """DESCRIBED is limited to top 2 domain entities by relationship count."""
    bundle = PerPaperBundle(
        paper=PaperInfo(title="Test", authors=["A"], document_id="P1"),
        entities=[
            ExtractedEntityRow(id="d1", entity_class="Disease", name="diabetes"),
            ExtractedEntityRow(id="g1", entity_class="Gene", name="BRCA2"),
            ExtractedEntityRow(id="d2", entity_class="Drug", name="metformin"),
        ],
        relationships=[
            RelationshipRow(subject="d1", predicate="TREATS", object_id="d2"),
            RelationshipRow(subject="g1", predicate="INCREASES_RISK", object_id="d1"),
            RelationshipRow(subject="d1", predicate="ASSOCIATED_WITH", object_id="g1"),
        ],
    )
    _, exp_rels = expand_provenance(bundle)
    described = [r for r in exp_rels if r.predicate == "DESCRIBED"]
    assert len(described) == 2
    described_ids = {r.object_id for r in described}
    assert "d1" in described_ids
    assert "g1" in described_ids
    assert "d2" not in described_ids


def test_expand_provenance_skips_author_institution_evidence() -> None:
    """DESCRIBED excludes Author, Institution, Evidence; only domain entities considered."""
    bundle = PerPaperBundle(
        paper=PaperInfo(
            title="Test",
            authors=["Alice"],
            document_id="P1",
        ),
        entities=[
            ExtractedEntityRow(id="Author:a1", entity_class="Author", name="Alice"),
            ExtractedEntityRow(id="Disease:d1", entity_class="Disease", name="diabetes"),
        ],
        relationships=[],
    )
    _, exp_rels = expand_provenance(bundle)
    described = [r for r in exp_rels if r.predicate == "DESCRIBED"]
    assert len(described) == 1
    assert described[0].object_id == "Disease:d1"

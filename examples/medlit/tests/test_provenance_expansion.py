"""Tests for provenance expansion (Author, Institution, Paper, derived relationships)."""

import pytest

from examples.medlit.bundle_models import (
    AuthorInfo,
    ExtractedEntityRow,
    PaperInfo,
    PerPaperBundle,
    RelationshipRow,
)
from examples.medlit.pipeline.provenance_expansion import expand_provenance
from examples.medlit.pipeline.utils import canonicalize_symmetric


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
    assert any("Author:" in eid and "smith" in eid.lower() for eid in entity_ids)
    assert any("Author:" in eid and "jones" in eid.lower() for eid in entity_ids)
    assert any("Institution:" in eid for eid in entity_ids)

    preds = {r.predicate for r in exp_rels}
    assert "AUTHORED" in preds
    assert "AFFILIATED_WITH" in preds
    assert "DESCRIBED" in preds
    assert "COAUTHORED_WITH" in preds
    assert "IS_COLLEAGUE" not in preds


def test_expand_provenance_skips_author_institution_evidence() -> None:
    """DESCRIBED is not created for Author, Institution, Evidence entities."""
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

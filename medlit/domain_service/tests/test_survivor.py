"""Tests for survivor selection logic."""

import pytest

from domain_service.survivor import select_survivor
from domain_service.models import CandidateEntity


def _make(entity_id: str, status: str = "provisional", usage_count: int = 1, confidence: float = 0.8) -> CandidateEntity:
    return CandidateEntity(
        entity_id=entity_id,
        name="test entity",
        entity_type="disease",
        status=status,
        usage_count=usage_count,
        confidence=confidence,
    )


def test_canonical_beats_provisional():
    candidates = [
        _make("prov:aaa", status="provisional", usage_count=10),
        _make("C0006142", status="canonical", usage_count=1),
    ]
    assert select_survivor(candidates) == "C0006142"


def test_authority_id_beats_provisional_uuid():
    candidates = [
        _make("prov:aaa", status="provisional", usage_count=5),
        _make("C0012345", status="provisional", usage_count=1),
    ]
    assert select_survivor(candidates) == "C0012345"


def test_higher_usage_count_wins_among_canonicals():
    candidates = [
        _make("C0001111", status="canonical", usage_count=3),
        _make("C0002222", status="canonical", usage_count=7),
    ]
    assert select_survivor(candidates) == "C0002222"


def test_lexical_tiebreak_among_equal_candidates():
    candidates = [
        _make("C0002222", status="canonical", usage_count=5),
        _make("C0001111", status="canonical", usage_count=5),
    ]
    # Lexically smallest ID wins the stable tie-breaker.
    assert select_survivor(candidates) == "C0001111"


def test_single_candidate_returned():
    candidates = [_make("prov:only", status="provisional")]
    assert select_survivor(candidates) == "prov:only"


def test_empty_raises():
    with pytest.raises(ValueError):
        select_survivor([])

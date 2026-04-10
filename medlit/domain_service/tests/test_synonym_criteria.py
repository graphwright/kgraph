"""Tests for per-entity-type synonym thresholds."""

from domain_service.synonym_criteria import get_threshold


def test_gene_is_tight():
    assert get_threshold("gene") >= 0.93


def test_drug_is_tight():
    assert get_threshold("drug") >= 0.92


def test_pathway_is_looser():
    assert get_threshold("pathway") < get_threshold("gene")


def test_unknown_type_returns_default():
    assert get_threshold("unknowntype") == 0.90


def test_case_insensitive():
    assert get_threshold("Disease") == get_threshold("disease")


def test_all_thresholds_in_valid_range():
    from domain_service.synonym_criteria import _THRESHOLDS

    for entity_type, threshold in _THRESHOLDS.items():
        assert 0.0 <= threshold <= 1.0, f"{entity_type}: {threshold} out of range"

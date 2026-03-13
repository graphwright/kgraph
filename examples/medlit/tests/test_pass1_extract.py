"""Unit tests for Pass 1 extract helpers: vocab-in-prompt and type normalization."""

import examples.medlit.domain_spec as _ds
from examples.medlit.scripts.pass1_extract import (
    _default_system_prompt,
    _fix_evidence_paper_id,
    _replace_current_paper_in_bundle,
    normalize_entity_type,
)


class TestNormalizeEntityType:
    """Test raw LLM type string -> bundle class (PascalCase)."""

    def test_biological_process_to_biological_process(self):
        """'biological process' (with space) normalizes to BiologicalProcess."""
        assert normalize_entity_type("biological process", _ds.NORMALIZED_TO_BUNDLE) == "BiologicalProcess"

    def test_gene_to_gene(self):
        """'gene' -> Gene."""
        assert normalize_entity_type("gene", _ds.NORMALIZED_TO_BUNDLE) == "Gene"

    def test_disease_lowercase(self):
        """'disease' -> Disease."""
        assert normalize_entity_type("disease", _ds.NORMALIZED_TO_BUNDLE) == "Disease"

    def test_hormone_and_enzyme(self):
        """PLAN3: hormone -> Hormone, enzyme -> Enzyme."""
        ntb = _ds.NORMALIZED_TO_BUNDLE
        assert normalize_entity_type("hormone", ntb) == "Hormone"
        assert normalize_entity_type("enzyme", ntb) == "Enzyme"

    def test_biological_process_underscore(self):
        """'biological_process' -> BiologicalProcess."""
        assert normalize_entity_type("biological_process", _ds.NORMALIZED_TO_BUNDLE) == "BiologicalProcess"

    def test_unknown_maps_to_other(self):
        """Unknown type maps to Other."""
        ntb = _ds.NORMALIZED_TO_BUNDLE
        assert normalize_entity_type("foo", ntb) == "Other"
        assert normalize_entity_type("", ntb) == "Other"

    def test_whitespace_stripped(self):
        """Whitespace is stripped before mapping."""
        assert normalize_entity_type("  gene  ", _ds.NORMALIZED_TO_BUNDLE) == "Gene"


class TestBuildSystemPromptWithVocab:
    """Test that vocab section is appended when vocab_entries provided."""

    def test_empty_vocab_returns_base(self):
        """None or empty vocab returns base prompt without vocab section."""
        base = _default_system_prompt(None, domain_spec=_ds)
        base_empty = _default_system_prompt([], domain_spec=_ds)
        assert base == base_empty
        assert "pasireotide" not in base

    def test_vocab_entries_included_in_prompt(self):
        """Short vocab list is included in the prompt with names and types."""
        vocab = [
            {"name": "pasireotide", "type": "drug"},
            {"name": "Cushing syndrome", "type": "disease"},
        ]
        out = _default_system_prompt(vocab, domain_spec=_ds)
        assert "pasireotide" in out
        assert "drug" in out
        assert "Cushing syndrome" in out
        assert "disease" in out
        assert "already been identified" in out or "exact names and types" in out


class TestFixEvidencePaperId:
    """Replace LLM placeholder paper IDs in evidence with actual paper_id."""

    def test_pmc_unknown_replaced(self):
        """PMC_UNKNOWN in evidence ID is replaced with actual paper_id."""
        assert _fix_evidence_paper_id("PMC_UNKNOWN:abstract:1:llm", "PMC11128938") == "PMC11128938:abstract:1:llm"

    def test_paper_id_literal_replaced(self):
        """'paper_id' literal is replaced."""
        assert _fix_evidence_paper_id("paper_id:results:2:llm", "PMC12757875") == "PMC12757875:results:2:llm"

    def test_real_paper_id_unchanged(self):
        """Real paper IDs are left as-is."""
        assert _fix_evidence_paper_id("PMC11128938:abstract:1:llm", "PMC11128938") == "PMC11128938:abstract:1:llm"

    def test_no_colon_unchanged(self):
        """Evidence IDs without colon are returned unchanged."""
        assert _fix_evidence_paper_id("ev1", "PMC11128938") == "ev1"

    def test_pmc11000000_replaced(self):
        """PMC11000000 placeholder is replaced."""
        assert _fix_evidence_paper_id("PMC11000000:abstract:0:llm", "PMC123") == "PMC123:abstract:0:llm"

    def test_current_paper_replaced(self):
        """==CURRENT_PAPER== placeholder is replaced."""
        assert _fix_evidence_paper_id("==CURRENT_PAPER==:results:1:llm", "PMC456") == "PMC456:results:1:llm"

    def test_hallucinated_pmc_replaced(self):
        """PMC ID from citation/hallucination (not current paper) is replaced."""
        assert _fix_evidence_paper_id("PMC99999999:abstract:0:llm", "PMC123") == "PMC123:abstract:0:llm"

    def test_current_paper_unchanged(self):
        """Evidence with correct current paper_id is left as-is."""
        assert _fix_evidence_paper_id("PMC123:abstract:0:llm", "PMC123") == "PMC123:abstract:0:llm"


class TestReplaceCurrentPaperInBundle:
    """Global replace of ==CURRENT_PAPER== in raw bundle before parsing."""

    def test_replaces_in_evidence_ids(self):
        """==CURRENT_PAPER== in evidence_entities and relationships is replaced."""
        bundle = {
            "evidence_entities": [
                {"id": "==CURRENT_PAPER==:abstract:0:llm", "text": "x"},
            ],
            "relationships": [
                {"evidence_ids": ["==CURRENT_PAPER==:results:1:llm"]},
            ],
        }
        _replace_current_paper_in_bundle(bundle, "PMC123")
        assert bundle["evidence_entities"][0]["id"] == "PMC123:abstract:0:llm"
        assert bundle["relationships"][0]["evidence_ids"] == ["PMC123:results:1:llm"]

    def test_leaves_other_strings_unchanged(self):
        """Strings without ==CURRENT_PAPER== are unchanged."""
        bundle = {"paper": {"pmcid": "PMC456"}, "entities": []}
        _replace_current_paper_in_bundle(bundle, "PMC123")
        assert bundle["paper"]["pmcid"] == "PMC456"

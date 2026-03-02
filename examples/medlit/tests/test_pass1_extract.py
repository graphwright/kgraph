"""Unit tests for Pass 1 extract helpers: vocab-in-prompt and type normalization."""

from examples.medlit.scripts.pass1_extract import (
    _build_system_prompt_with_vocab,
    _default_system_prompt,
    normalize_entity_type,
)


class TestNormalizeEntityType:
    """Test raw LLM type string -> bundle class (PascalCase)."""

    def test_biological_process_to_biological_process(self):
        """'biological process' (with space) normalizes to BiologicalProcess."""
        assert normalize_entity_type("biological process") == "BiologicalProcess"

    def test_gene_to_gene(self):
        """'gene' -> Gene."""
        assert normalize_entity_type("gene") == "Gene"

    def test_disease_lowercase(self):
        """'disease' -> Disease."""
        assert normalize_entity_type("disease") == "Disease"

    def test_biological_process_underscore(self):
        """'biological_process' -> BiologicalProcess."""
        assert normalize_entity_type("biological_process") == "BiologicalProcess"

    def test_unknown_maps_to_other(self):
        """Unknown type maps to Other."""
        assert normalize_entity_type("foo") == "Other"
        assert normalize_entity_type("") == "Other"

    def test_whitespace_stripped(self):
        """Whitespace is stripped before mapping."""
        assert normalize_entity_type("  gene  ") == "Gene"


class TestBuildSystemPromptWithVocab:
    """Test that vocab section is appended when vocab_entries provided."""

    def test_empty_vocab_returns_base(self):
        """None or empty vocab returns base prompt unchanged."""
        base = _default_system_prompt()
        assert _build_system_prompt_with_vocab(base, None) == base
        assert _build_system_prompt_with_vocab(base, []) == base

    def test_vocab_entries_included_in_prompt(self):
        """Short vocab list is included in the prompt with names and types."""
        base = "You are an expert."
        vocab = [
            {"name": "pasireotide", "type": "drug"},
            {"name": "Cushing syndrome", "type": "disease"},
        ]
        out = _build_system_prompt_with_vocab(base, vocab)
        assert "pasireotide" in out
        assert "drug" in out
        assert "Cushing syndrome" in out
        assert "disease" in out
        assert "already been identified" in out or "exact names and types" in out

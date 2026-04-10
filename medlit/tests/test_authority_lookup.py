"""Tests for canonical ID authority lookup.

Tests the matching logic for DBPedia and other ontology lookups,
and UMLS type validation (validate_umls_type).
"""

import pytest

from medlit.pipeline.authority_lookup import CanonicalIdLookup, validate_umls_type


class TestDBPediaLabelMatching:
    """Test the DBPedia label matching logic."""

    @pytest.fixture
    def lookup(self):
        """Create a CanonicalIdLookup instance for testing."""
        return CanonicalIdLookup()

    # --- Tests for matches that SHOULD succeed ---

    def test_exact_match(self, lookup):
        """Exact match should succeed."""
        assert lookup._dbpedia_label_matches("breast cancer", "Breast Cancer")  # pylint: disable=protected-access

    def test_term_contained_in_label(self, lookup):
        """Term contained in label should succeed."""
        assert lookup._dbpedia_label_matches("mitochondria", "<B>Mitochondria</B> (song)")  # pylint: disable=protected-access

    def test_label_contained_in_term(self, lookup):
        """Label contained in term should succeed."""
        assert lookup._dbpedia_label_matches("breast cancer syndrome", "Breast Cancer")  # pylint: disable=protected-access

    def test_label_starts_with_term(self, lookup):
        """Label starting with term should succeed."""
        assert lookup._dbpedia_label_matches("breast", "Breast cancer")  # pylint: disable=protected-access

    def test_common_prefix_singular_plural(self, lookup):
        """Common 6-char prefix should succeed (handles singular/plural)."""
        # mitochondria vs mitochondrion - same first 6 chars "mitoch"
        assert lookup._dbpedia_label_matches("mitochondria", "<B>Mitochondrion</B>")  # pylint: disable=protected-access

    def test_html_tags_stripped(self, lookup):
        """HTML bold tags should be stripped from labels."""
        assert lookup._dbpedia_label_matches("mitochondria", "<B>Mitochondria</B>")  # pylint: disable=protected-access
        assert lookup._dbpedia_label_matches("cancer", "<B>Cancer</B>")  # pylint: disable=protected-access

    def test_case_insensitive(self, lookup):
        """Matching should be case-insensitive."""
        assert lookup._dbpedia_label_matches("BRCA1", "brca1")  # pylint: disable=protected-access
        assert lookup._dbpedia_label_matches("brca1", "BRCA1")  # pylint: disable=protected-access

    # --- Tests for matches that SHOULD fail ---

    def test_garbage_match_insect(self, lookup):
        """Garbage match 'HER2-enriched' → 'Insect' should fail."""
        assert not lookup._dbpedia_label_matches("HER2-enriched", "Insect")  # pylint: disable=protected-access

    def test_garbage_match_animal(self, lookup):
        """Garbage match 'basal-like' → 'Animal' should fail."""
        assert not lookup._dbpedia_label_matches("basal-like", "Animal")  # pylint: disable=protected-access

    def test_unrelated_terms(self, lookup):
        """Completely unrelated terms should fail."""
        assert not lookup._dbpedia_label_matches("diabetes", "Python programming")  # pylint: disable=protected-access
        assert not lookup._dbpedia_label_matches("gene", "Music")  # pylint: disable=protected-access

    def test_substring_match_allowed(self, lookup):
        """Substring matching is allowed (term in label)."""
        # "test" is contained in "testing" - this is accepted
        assert lookup._dbpedia_label_matches("test", "Testing framework")  # pylint: disable=protected-access
        # "car" is contained in "cardinal" - this is accepted
        # (for medical terms, coincidental substrings are rare)
        assert lookup._dbpedia_label_matches("car", "Cardinal")  # pylint: disable=protected-access

    def test_no_overlap_fails(self, lookup):
        """Terms with no overlap should fail."""
        # No substring match, no common prefix
        assert not lookup._dbpedia_label_matches("xyz", "abc")  # pylint: disable=protected-access
        assert not lookup._dbpedia_label_matches("hello", "world")  # pylint: disable=protected-access


class TestMeSHTermNormalization:
    """Test MeSH term normalization (cancer → neoplasms)."""

    @pytest.fixture
    def lookup(self):
        """Create a CanonicalIdLookup instance for testing."""
        return CanonicalIdLookup()

    def test_mesh_id_extraction(self, lookup):
        """Test extracting MeSH ID from API results."""
        # Simulated API response
        data = [
            {"resource": "http://id.nlm.nih.gov/mesh/D001943", "label": "Breast Neoplasms"},
            {"resource": "http://id.nlm.nih.gov/mesh/D018567", "label": "Breast Neoplasms, Male"},
        ]

        # Should find D001943 for "breast neoplasms"
        result = lookup._extract_mesh_id_from_results(data, "breast neoplasms")  # pylint: disable=protected-access
        assert result == "MeSH:D001943"

    def test_mesh_id_extraction_word_order(self, lookup):
        """Test MeSH extraction handles word order differences."""
        data = [
            {"resource": "http://id.nlm.nih.gov/mesh/D001943", "label": "Breast Neoplasms"},
        ]

        # "neoplasms breast" should still match "Breast Neoplasms"
        result = lookup._extract_mesh_id_from_results(data, "neoplasms breast")  # pylint: disable=protected-access
        assert result == "MeSH:D001943"

    def test_mesh_id_extraction_no_match(self, lookup):
        """Test MeSH extraction returns None for no match."""
        data = [
            {"resource": "http://id.nlm.nih.gov/mesh/D001943", "label": "Breast Neoplasms"},
        ]

        # "lung cancer" should not match "Breast Neoplasms"
        result = lookup._extract_mesh_id_from_results(data, "lung cancer")  # pylint: disable=protected-access
        assert result is None

    def test_mesh_id_extraction_empty_data(self, lookup):
        """Test MeSH extraction handles empty data."""
        result = lookup._extract_mesh_id_from_results([], "anything")  # pylint: disable=protected-access
        assert result is None

    def test_mesh_id_extraction_prefers_general_over_complication(self, lookup):
        """Test that general terms are preferred over complications.

        "breast cancer" should match "Breast Neoplasms" (D001943)
        rather than "Breast Cancer Lymphedema" (D000072656).
        """
        data = [
            {"resource": "http://id.nlm.nih.gov/mesh/D000072656", "label": "Breast Cancer Lymphedema"},
            {"resource": "http://id.nlm.nih.gov/mesh/D001943", "label": "Breast Neoplasms"},
        ]

        # Should prefer "Breast Neoplasms" (shorter, more general)
        result = lookup._extract_mesh_id_from_results(data, "breast cancer")  # pylint: disable=protected-access
        assert result == "MeSH:D001943", f"Expected MeSH:D001943 (Breast Neoplasms), got {result}"

    def test_mesh_id_extraction_exact_match_priority(self, lookup):
        """Test that exact matches get highest priority."""
        data = [
            {"resource": "http://id.nlm.nih.gov/mesh/D000072656", "label": "Breast Cancer Lymphedema"},
            {"resource": "http://id.nlm.nih.gov/mesh/D001943", "label": "Breast Neoplasms"},
            {"resource": "http://id.nlm.nih.gov/mesh/D999999", "label": "Breast Cancer"},  # Exact match
        ]

        # Exact match should win even if it appears later
        result = lookup._extract_mesh_id_from_results(data, "breast cancer")  # pylint: disable=protected-access
        assert result == "MeSH:D999999", f"Expected MeSH:D999999 (exact match), got {result}"


class TestValidateUmlsType:
    """Test validate_umls_type with injected semantic type mapping (no live API)."""

    def test_cortisol_gene_misclassified_returns_correction(self):
        """Cortisol (C0020268) as hormone/drug; assigned type 'gene' should return (False, correct_type)."""
        override = {"C0020268": ["Pharmacologic Substance"]}  # cortisol -> drug
        ok, correct = validate_umls_type("C0020268", "gene", _semantic_types_override=override)
        assert ok is False
        assert correct == "drug"

    def test_pasireotide_drug_compatible_returns_ok(self):
        """Pasireotide (or any CUI) mapped to Pharmacologic Substance with type drug returns (True, None)."""
        override = {"C2975503": ["Pharmacologic Substance"]}
        ok, correct = validate_umls_type("C2975503", "drug", _semantic_types_override=override)
        assert ok is True
        assert correct is None

    def test_unknown_cui_returns_ok_no_correction(self):
        """Unknown CUI (not in override, or empty override) returns (True, None)."""
        override = {}
        ok, correct = validate_umls_type("C9999999", "gene", _semantic_types_override=override)
        assert ok is True
        assert correct is None

    def test_cache_reused(self):
        """Results are cached when _cache dict is passed; second call does not recompute."""
        override = {"C0020268": ["Pharmacologic Substance"]}
        cache = {}
        ok1, correct1 = validate_umls_type("C0020268", "gene", _cache=cache, _semantic_types_override=override)
        ok2, correct2 = validate_umls_type("C0020268", "gene", _cache=cache, _semantic_types_override=override)
        assert ok1 is ok2 is False
        assert correct1 == correct2 == "drug"
        assert len(cache) == 1

    def test_ambiguous_multiple_allowed_returns_false_none(self):
        """When UMLS maps to multiple allowed types (e.g. drug or biomarker), return (False, None)."""
        override = {"C1234567": ["Steroid"]}  # Steroid -> ["drug", "biomarker"]
        ok, correct = validate_umls_type("C1234567", "gene", _semantic_types_override=override)
        assert ok is False
        assert correct is None  # ambiguous

"""Tests for entity type normalization in MedLitEntityExtractor.

Tests the _normalize_entity_type() method which handles:
- Pipe-separated types from LLM output
- Common LLM mistakes (test → procedure)
- Invalid type filtering
"""

# pylint: disable=protected-access

import pytest

from medlit.domain import MedLitDomainSchema
from medlit.pipeline.mentions import (
    MedLitEntityExtractor,
    TYPE_MAPPING,
    _is_type_masquerading_as_name,
)


class TestTypeNormalizationWithDomain:
    """Test entity type normalization with domain schema validation."""

    @pytest.fixture
    def extractor(self):
        """Create extractor with domain for full validation."""
        domain = MedLitDomainSchema()
        return MedLitEntityExtractor(llm_client=None, domain=domain)

    def test_valid_type_passes_through(self, extractor):
        """Valid entity types should pass through unchanged."""
        assert extractor._normalize_entity_type("disease") == "disease"
        assert extractor._normalize_entity_type("gene") == "gene"
        assert extractor._normalize_entity_type("drug") == "drug"
        assert extractor._normalize_entity_type("protein") == "protein"
        assert extractor._normalize_entity_type("symptom") == "symptom"
        assert extractor._normalize_entity_type("procedure") == "procedure"
        assert extractor._normalize_entity_type("biomarker") == "biomarker"
        assert extractor._normalize_entity_type("pathway") == "pathway"
        assert extractor._normalize_entity_type("location") == "location"
        assert extractor._normalize_entity_type("ethnicity") == "ethnicity"

    def test_case_normalization(self, extractor):
        """Types should be normalized to lowercase."""
        assert extractor._normalize_entity_type("Disease") == "disease"
        assert extractor._normalize_entity_type("GENE") == "gene"
        assert extractor._normalize_entity_type("DrUg") == "drug"

    def test_whitespace_stripped(self, extractor):
        """Whitespace should be stripped from types."""
        assert extractor._normalize_entity_type("  disease  ") == "disease"
        assert extractor._normalize_entity_type("\tgene\n") == "gene"

    def test_pipe_separated_takes_first_valid(self, extractor):
        """Pipe-separated types should return first valid type."""
        assert extractor._normalize_entity_type("drug|protein") == "drug"
        assert extractor._normalize_entity_type("protein|drug") == "protein"
        assert extractor._normalize_entity_type("gene|disease|protein") == "gene"

    def test_pipe_separated_skips_invalid(self, extractor):
        """Pipe-separated types should skip invalid types."""
        assert extractor._normalize_entity_type("invalid|disease") == "disease"
        assert extractor._normalize_entity_type("foo|bar|gene") == "gene"

    def test_pipe_separated_all_invalid_returns_none(self, extractor):
        """Pipe-separated with all invalid types should return None."""
        assert extractor._normalize_entity_type("invalid|foo|bar") is None

    def test_common_mistake_test_to_procedure(self, extractor):
        """'test' should be normalized to 'procedure'."""
        assert extractor._normalize_entity_type("test") == "procedure"

    def test_common_mistake_diagnostic_to_procedure(self, extractor):
        """'diagnostic' should be normalized to 'procedure'."""
        assert extractor._normalize_entity_type("diagnostic") == "procedure"

    def test_common_mistake_imaging_to_procedure(self, extractor):
        """'imaging' should be normalized to 'procedure'."""
        assert extractor._normalize_entity_type("imaging") == "procedure"

    def test_common_mistake_assay_to_biomarker(self, extractor):
        """'assay' should be normalized to 'biomarker'."""
        assert extractor._normalize_entity_type("assay") == "biomarker"

    def test_common_mistake_marker_to_biomarker(self, extractor):
        """'marker' should be normalized to 'biomarker'."""
        assert extractor._normalize_entity_type("marker") == "biomarker"

    def test_skip_system_type(self, extractor):
        """'system' should be skipped (returns None)."""
        assert extractor._normalize_entity_type("system") is None

    def test_skip_organization_type(self, extractor):
        """'organization' should be skipped (returns None)."""
        assert extractor._normalize_entity_type("organization") is None

    def test_invalid_type_returns_none(self, extractor):
        """Unknown types should return None."""
        assert extractor._normalize_entity_type("unknown") is None
        assert extractor._normalize_entity_type("foobar") is None
        assert extractor._normalize_entity_type("chemical") is None


class TestTypeNormalizationWithoutDomain:
    """Test entity type normalization without domain (basic mode)."""

    @pytest.fixture
    def extractor(self):
        """Create extractor without domain for basic normalization."""
        return MedLitEntityExtractor(llm_client=None, domain=None)

    def test_basic_type_passes_through(self, extractor):
        """Types pass through in basic mode (no validation)."""
        # Even unknown types pass through without domain validation
        assert extractor._normalize_entity_type("disease") == "disease"
        assert extractor._normalize_entity_type("unknown") == "unknown"

    def test_basic_pipe_takes_first(self, extractor):
        """Pipe-separated takes first part in basic mode."""
        assert extractor._normalize_entity_type("drug|protein") == "drug"
        assert extractor._normalize_entity_type("foo|bar") == "foo"

    def test_basic_mapping_applied(self, extractor):
        """TYPE_MAPPING is still applied in basic mode."""
        assert extractor._normalize_entity_type("test") == "procedure"
        assert extractor._normalize_entity_type("system") is None


class TestTypeMappingConstants:
    """Test the TYPE_MAPPING constant has expected entries."""

    def test_procedure_mappings_exist(self):
        """Procedure mappings should exist."""
        assert TYPE_MAPPING.get("test") == "procedure"
        assert TYPE_MAPPING.get("diagnostic") == "procedure"
        assert TYPE_MAPPING.get("imaging") == "procedure"

    def test_biomarker_mappings_exist(self):
        """Biomarker mappings should exist."""
        assert TYPE_MAPPING.get("assay") == "biomarker"
        assert TYPE_MAPPING.get("marker") == "biomarker"

    def test_skip_mappings_exist(self):
        """Skip mappings (None values) should exist."""
        assert TYPE_MAPPING.get("system") is None
        assert TYPE_MAPPING.get("organization") is None
        assert "system" in TYPE_MAPPING  # Key exists with None value
        assert "organization" in TYPE_MAPPING


class TestTypeMasqueradingAsName:
    """Reject entity names that are actually type labels (e.g. LLM returns entity='disease', type='disease')."""

    def test_name_equals_type_rejected(self):
        """When name equals type, treat as type masquerading as name."""
        assert _is_type_masquerading_as_name("disease", "disease") is True
        assert _is_type_masquerading_as_name("gene", "gene") is True
        assert _is_type_masquerading_as_name("variant", "gene") is True  # variant is a type label

    def test_known_type_labels_rejected_as_name(self):
        """Known type labels must not be used as entity names."""
        assert _is_type_masquerading_as_name("disease", "disease") is True
        assert _is_type_masquerading_as_name("gene", "drug") is True  # "gene" as name with any type
        assert _is_type_masquerading_as_name("procedure", "procedure") is True

    def test_real_entity_names_allowed(self):
        """Real entity names should not be rejected."""
        assert _is_type_masquerading_as_name("breast cancer", "disease") is False
        assert _is_type_masquerading_as_name("BRCA1", "gene") is False
        assert _is_type_masquerading_as_name("aspirin", "drug") is False
        assert _is_type_masquerading_as_name("p.Arg2336His", "gene") is False

    def test_empty_name_rejected(self):
        """Empty or whitespace-only name is rejected."""
        assert _is_type_masquerading_as_name("", "disease") is True
        assert _is_type_masquerading_as_name("   ", "gene") is True

    @pytest.mark.asyncio
    async def test_pre_extracted_type_as_name_dropped(self):
        """Pre-extracted entities with name=type (e.g. name='disease', type='disease') produce no mention."""
        from datetime import datetime, timezone

        from medlit.documents import JournalArticle

        domain = MedLitDomainSchema()
        extractor = MedLitEntityExtractor(llm_client=None, domain=domain)
        doc = JournalArticle(
            document_id="test-doc",
            content="",
            content_type="text/plain",
            abstract="",
            created_at=datetime.now(timezone.utc),
            metadata={
                "entities": [
                    {"id": "C001", "name": "disease", "type": "disease"},
                    {"id": "C002", "name": "male breast cancer", "type": "disease"},
                    {"id": "C003", "name": "gene", "type": "gene"},
                ],
            },
        )
        mentions = await extractor.extract(doc)
        # Only "male breast cancer" should appear; "disease" and "gene" as names are dropped
        assert len(mentions) == 1
        assert mentions[0].text == "male breast cancer"
        assert mentions[0].entity_type == "disease"

"""Tests for NER-based entity extraction (PLAN3)."""

import pytest
from datetime import datetime, timezone

from medlit.domain import MedLitDomainSchema
from medlit.documents import JournalArticle
from medlit.pipeline.ner_extractor import (
    LABEL_TO_MEDLIT_TYPE,
    MedLitNEREntityExtractor,
    _chunk_text,
    _get_document_text,
    _merge_and_dedupe,
    _normalize_entity_group,
)


class TestNormalizeEntityGroup:
    """Test label normalization for NER pipeline output."""

    def test_lowercase(self):
        assert _normalize_entity_group("Chemical") == "chemical"
        assert _normalize_entity_group("DISEASE") == "disease"

    def test_strip_b_i_prefix(self):
        assert _normalize_entity_group("B-Chemical") == "chemical"
        assert _normalize_entity_group("I-Disease") == "disease"
        assert _normalize_entity_group("O-Something") == "something"

    def test_empty(self):
        assert _normalize_entity_group("") == ""
        assert _normalize_entity_group("   ") == ""


class TestLabelMapping:
    """Test default label -> medlit type mapping."""

    def test_chemical_maps_to_drug(self):
        assert LABEL_TO_MEDLIT_TYPE.get("chemical") == "drug"

    def test_disease_maps_to_disease(self):
        assert LABEL_TO_MEDLIT_TYPE.get("disease") == "disease"

    def test_known_types_present(self):
        assert "drug" in LABEL_TO_MEDLIT_TYPE.values()
        assert "disease" in LABEL_TO_MEDLIT_TYPE.values()
        assert "gene" in LABEL_TO_MEDLIT_TYPE.values()


class TestChunkText:
    """Test long-document chunking."""

    def test_short_text_single_chunk(self):
        text = "Short."
        chunks = _chunk_text(text, chunk_size=100, overlap=10)
        assert len(chunks) == 1
        assert chunks[0] == (0, "Short.")

    def test_long_text_multiple_chunks(self):
        text = "a" * 500
        chunks = _chunk_text(text, chunk_size=200, overlap=50)
        assert len(chunks) >= 2
        assert chunks[0][0] == 0
        assert len(chunks[0][1]) == 200
        assert chunks[1][0] == 150  # 200 - 50 overlap

    def test_merge_and_dedupe_adjusts_offsets(self):
        # Chunk 0: 0-100, Chunk 1: 80-180 (overlap 20). Simulate NER found at chunk1 start
        chunk_results = [
            (0, [{"start": 0, "end": 10, "entity_group": "Disease", "score": 0.9, "word": "diabetes"}]),
            (80, [{"start": 0, "end": 8, "entity_group": "Chemical", "score": 0.85, "word": "aspirin"}]),
        ]
        merged = _merge_and_dedupe(chunk_results)
        assert len(merged) == 2
        by_label = {m["entity_group"]: m for m in merged}
        assert by_label["Disease"]["start"] == 0 and by_label["Disease"]["end"] == 10
        assert by_label["Chemical"]["start"] == 80 and by_label["Chemical"]["end"] == 88

    def test_merge_dedupes_overlapping_span_keeps_higher_score(self):
        chunk_results = [
            (0, [{"start": 10, "end": 18, "entity_group": "Disease", "score": 0.8, "word": "diabetes"}]),
            (0, [{"start": 10, "end": 18, "entity_group": "Disease", "score": 0.95, "word": "diabetes"}]),
        ]
        merged = _merge_and_dedupe(chunk_results)
        assert len(merged) == 1
        assert merged[0]["score"] == 0.95


class TestGetDocumentText:
    """Test document text extraction."""

    def test_uses_content(self):
        doc = JournalArticle(
            document_id="d1",
            content="Patient had diabetes.",
            content_type="text/plain",
            abstract="",
            created_at=datetime.now(timezone.utc),
            metadata={},
        )
        assert _get_document_text(doc) == "Patient had diabetes."

    def test_falls_back_to_abstract_when_content_empty(self):
        doc = JournalArticle(
            document_id="d1",
            content="",
            content_type="text/plain",
            abstract="Abstract text here.",
            created_at=datetime.now(timezone.utc),
            metadata={},
        )
        assert _get_document_text(doc) == "Abstract text here."


class TestMedLitNEREntityExtractorWithMock:
    """Test NER extractor with a mock pipeline (no real model load)."""

    @pytest.fixture
    def mock_pipeline(self):
        """Pipeline that returns fixed entities for testing."""

        def run(text):
            if not text or len(text) < 10:
                return []
            # Return mock NER output: "diabetes" at 11-19, "aspirin" at 24-31
            result = []
            if "diabetes" in text.lower():
                idx = text.lower().index("diabetes")
                result.append(
                    {
                        "start": idx,
                        "end": idx + 8,
                        "entity_group": "Disease",
                        "score": 0.92,
                        "word": "diabetes",
                    }
                )
            if "aspirin" in text.lower():
                idx = text.lower().index("aspirin")
                result.append(
                    {
                        "start": idx,
                        "end": idx + 7,
                        "entity_group": "Chemical",
                        "score": 0.88,
                        "word": "aspirin",
                    }
                )
            return result

        return run

    @pytest.fixture
    def extractor_with_mock(self, mock_pipeline):
        domain = MedLitDomainSchema()
        return MedLitNEREntityExtractor(
            model_name_or_path="test-model",
            domain=domain,
            pipeline=mock_pipeline,
        )

    @pytest.mark.asyncio
    async def test_extract_returns_mentions_with_correct_types(self, extractor_with_mock):
        doc = JournalArticle(
            document_id="d1",
            content="Patient with diabetes took aspirin.",
            content_type="text/plain",
            abstract="",
            created_at=datetime.now(timezone.utc),
            metadata={},
        )
        mentions = await extractor_with_mock.extract(doc)
        assert len(mentions) == 2
        by_type = {m.entity_type: m for m in mentions}
        assert "disease" in by_type
        assert by_type["disease"].text == "diabetes"
        assert by_type["disease"].start_offset == 13  # "Patient with " is 13 chars
        assert by_type["disease"].end_offset == 21
        assert "drug" in by_type
        assert by_type["drug"].text == "aspirin"
        assert by_type["drug"].metadata.get("extraction_method") == "ner"

    @pytest.mark.asyncio
    async def test_extract_empty_text_returns_empty_list(self, extractor_with_mock):
        doc = JournalArticle(
            document_id="d1",
            content="",
            content_type="text/plain",
            abstract="",
            created_at=datetime.now(timezone.utc),
            metadata={},
        )
        mentions = await extractor_with_mock.extract(doc)
        assert mentions == []

    @pytest.mark.asyncio
    async def test_extract_short_text_returns_empty_list(self, extractor_with_mock):
        doc = JournalArticle(
            document_id="d1",
            content="Hi",
            content_type="text/plain",
            abstract="",
            created_at=datetime.now(timezone.utc),
            metadata={},
        )
        mentions = await extractor_with_mock.extract(doc)
        assert mentions == []

    @pytest.mark.asyncio
    async def test_type_as_name_filtered_out(self, mock_pipeline):
        """When mock returns entity with word 'disease' (type label), it should be filtered out."""

        def mock_return_disease_word(text):
            if len(text) < 10:
                return []
            # Span must match the word "disease" in "The disease progressed." (start=4, end=11)
            idx = text.lower().index("disease")
            return [{"start": idx, "end": idx + 7, "entity_group": "Disease", "score": 0.9, "word": "disease"}]

        domain = MedLitDomainSchema()
        extractor = MedLitNEREntityExtractor(
            model_name_or_path="test",
            domain=domain,
            pipeline=mock_return_disease_word,
        )
        doc = JournalArticle(
            document_id="d1",
            content="The disease progressed.",
            content_type="text/plain",
            abstract="",
            created_at=datetime.now(timezone.utc),
            metadata={},
        )
        mentions = await extractor.extract(doc)
        # "disease" as span text is type-as-name and should be dropped
        assert len(mentions) == 0


class TestMedLitNEREntityExtractorImportError:
    """Test that NER extractor raises clear ImportError when transformers not installed."""

    def test_instantiation_without_pipeline_raises_import_error_when_no_transformers(self):
        """When transformers is not installed, constructing without pipeline= raises ImportError."""
        try:
            import transformers  # noqa: F401

            pytest.skip("transformers is installed; cannot test ImportError path")
        except ImportError:
            pass

        with pytest.raises(ImportError) as exc_info:
            MedLitNEREntityExtractor(
                model_name_or_path="tner/roberta-base-bc5cdr",
                pipeline=None,
            )
        assert "ner" in str(exc_info.value).lower() or "install" in str(exc_info.value).lower()

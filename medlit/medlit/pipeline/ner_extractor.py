"""
NER-based entity extraction for medical literature (PLAN3).

Uses a HuggingFace token-classification (NER) model for fast, local entity
extraction instead of an LLM. Default model: tner/roberta-base-bc5cdr (BC5CDR
chemical and disease entities). Install with: pip install -e ".[ner]"

Label mapping (BC5CDR-style): Chemical -> drug, Disease -> disease.
Gene/protein entities are not covered by this model; use a second model or
hybrid with LLM for full coverage.
"""

import asyncio
from typing import Any

from kgschema.document import BaseDocument
from kgschema.domain import DomainSchema
from kgschema.entity import EntityMention
from kgraph.pipeline.interfaces import EntityExtractorInterface

from .mentions import _is_type_masquerading_as_name

# Default: map NER pipeline entity_group (after normalization) to medlit entity_type
LABEL_TO_MEDLIT_TYPE: dict[str, str] = {
    "chemical": "drug",
    "disease": "disease",
    "drug": "drug",
    "gene": "gene",
    "protein": "protein",
    "symptom": "symptom",
    "procedure": "procedure",
    "biomarker": "biomarker",
    "pathway": "pathway",
    "location": "location",
    "ethnicity": "ethnicity",
}

# Chunking for long documents (pipeline has max_length)
CHUNK_CHARS = 4000
CHUNK_OVERLAP = 200
MIN_TEXT_LEN = 10


def _normalize_entity_group(label: str) -> str:
    """Normalize pipeline entity_group to lowercase, strip B-/I- prefix if present."""
    s = (label or "").strip().lower()
    for prefix in ("b-", "i-", "o-"):
        if s.startswith(prefix):
            s = s[len(prefix) :].strip()
            break
    return s


def _get_document_text(document: BaseDocument) -> str:
    """Get text to run NER on: content or abstract."""
    text = (document.content or "").strip()
    if not text and hasattr(document, "abstract"):
        text = (getattr(document, "abstract") or "").strip()
    return text


def _run_ner_sync(pipeline: Any, text: str) -> list[dict]:
    """Run NER pipeline on text; returns list of dicts with start, end, entity_group, score."""
    if not text or len(text) < MIN_TEXT_LEN:
        return []
    try:
        out = pipeline(text)
        return out if isinstance(out, list) else []
    except Exception:
        return []


def _chunk_text(text: str, chunk_size: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP) -> list[tuple[int, str]]:
    """Split text into overlapping chunks; returns [(start_offset, chunk_text), ...]."""
    if len(text) <= chunk_size:
        return [(0, text)]
    chunks: list[tuple[int, str]] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append((start, chunk))
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def _merge_and_dedupe(
    chunk_results: list[tuple[int, list[dict]]],
) -> list[dict]:
    """Merge NER results from chunks: adjust offsets and dedupe by span (keep higher score)."""
    by_span: dict[tuple[int, int], dict] = {}
    for chunk_start, entities in chunk_results:
        for e in entities:
            s = e.get("start")
            end = e.get("end")
            if s is None or end is None:
                continue
            global_start = chunk_start + s
            global_end = chunk_start + end
            key = (global_start, global_end)
            score = float(e.get("score") or 0.0)
            if key not in by_span or score > float((by_span[key].get("score") or 0)):
                by_span[key] = {
                    "start": global_start,
                    "end": global_end,
                    "entity_group": e.get("entity_group") or e.get("entity"),
                    "score": score,
                    "word": e.get("word", ""),
                }
    return list(by_span.values())


class MedLitNEREntityExtractor(EntityExtractorInterface):
    """Extract entity mentions using a local NER model (e.g. BC5CDR).

    Much faster than LLM-based extraction. Supports disease and chemical (drug)
    out of the box with the default model; other types can be added via
    label mapping or a different model.
    """

    def __init__(
        self,
        model_name_or_path: str = "tner/roberta-base-bc5cdr",
        domain: DomainSchema | None = None,
        device: str | None = None,
        max_length: int = 512,
        label_to_type: dict[str, str] | None = None,
        pipeline: Any = None,
    ):
        """Initialize the NER extractor.

        Args:
            model_name_or_path: HuggingFace model id or local path.
            domain: Medlit domain for type filtering; if None, all mapped types kept.
            device: "cuda", "cpu", or None for auto.
            max_length: Tokenizer max length.
            label_to_type: Override label -> medlit type map; default LABEL_TO_MEDLIT_TYPE.
            pipeline: Optional pre-built NER pipeline (for testing); if set, model is not loaded.

        Raises:
            ImportError: If transformers/torch are not installed (install with pip install -e ".[ner]").
        """
        self._model_name = model_name_or_path
        self._domain = domain
        self._max_length = max_length
        self._label_to_type = label_to_type or dict(LABEL_TO_MEDLIT_TYPE)

        if pipeline is not None:
            self._pipeline = pipeline
            return

        try:
            from transformers import pipeline as hf_pipeline
        except ImportError as e:
            raise ImportError('NER entity extraction requires the "ner" extra. Install with: pip install -e ".[ner]"') from e

        if device == "cpu":
            pipeline_device = -1
        elif device == "cuda":
            pipeline_device = 0
        else:
            try:
                import torch

                pipeline_device = 0 if torch.cuda.is_available() else -1
            except ImportError:
                pipeline_device = -1

        self._pipeline = hf_pipeline(  # type: ignore[call-overload]
            "ner",
            model=model_name_or_path,
            aggregation_strategy="simple",
            device=pipeline_device,
        )

    async def extract(self, document: BaseDocument) -> list[EntityMention]:
        """Extract entity mentions from document text using the NER model."""
        text = _get_document_text(document)
        if not text or len(text) < MIN_TEXT_LEN:
            return []

        # Chunk long documents
        chunks = _chunk_text(text)
        loop = asyncio.get_event_loop()
        chunk_results: list[tuple[int, list[dict]]] = []
        for chunk_start, chunk_text in chunks:

            def run_chunk(t: str = chunk_text) -> list[dict]:
                return _run_ner_sync(self._pipeline, t)

            raw = await loop.run_in_executor(None, run_chunk)
            chunk_results.append((chunk_start, raw))

        merged = _merge_and_dedupe(chunk_results)
        allowed_types = set(self._domain.entity_types) if self._domain else None
        mentions: list[EntityMention] = []

        for e in merged:
            entity_group = e.get("entity_group") or e.get("entity") or ""
            norm_label = _normalize_entity_group(str(entity_group))
            entity_type = self._label_to_type.get(norm_label)
            if not entity_type:
                continue
            if allowed_types is not None and entity_type not in allowed_types:
                continue

            start_offset = int(e.get("start", 0))
            end_offset = int(e.get("end", 0))
            span_text = text[start_offset:end_offset] if start_offset < len(text) else (e.get("word") or "")
            span_text = span_text.strip() or (e.get("word") or "").strip()
            if not span_text:
                continue
            if _is_type_masquerading_as_name(span_text, entity_type):
                continue

            confidence = float(e.get("score") or 0.5)
            confidence = max(0.0, min(1.0, confidence))

            context_start = max(0, start_offset - 50)
            context_end = min(len(text), end_offset + 50)
            context = text[context_start:context_end] if context_end > context_start else None

            mentions.append(
                EntityMention(
                    text=span_text,
                    entity_type=entity_type,
                    start_offset=start_offset,
                    end_offset=end_offset,
                    confidence=confidence,
                    context=context,
                    metadata={
                        "extraction_method": "ner",
                        "model": self._model_name,
                    },
                )
            )

        return mentions

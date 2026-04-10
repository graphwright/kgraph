"""Relationship extraction from journal articles.

Extracts relationships from Paper JSON format (from med-lit-schema).
Since the papers already have extracted relationships, we convert those to BaseRelationship objects.
Can also use Ollama LLM for relationship extraction from text.
"""

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Sequence

from kgraph.pipeline.interfaces import RelationshipExtractorInterface
from kgraph.pipeline.llm_client import LLMClientInterface
from kgraph.storage.memory import _cosine_similarity

from kgschema.document import BaseDocument
from kgschema.domain import Evidence, Provenance
from kgschema.entity import BaseEntity
from kgschema.relationship import BaseRelationship

from ..relationships import MedicalClaimRelationship

# Default directory for relationship extraction trace files
DEFAULT_TRACE_DIR = Path("/tmp/kgraph-relationship-traces")

# Predicate specificity for deduplication: when the same (subject_id, object_id) has multiple
# predicates, we keep the one with highest specificity (e.g. indicates > associated_with).
# Predicates not listed have specificity 0.
PREDICATE_SPECIFICITY: dict[str, int] = {
    "indicates": 2,
    "associated_with": 1,
}

if TYPE_CHECKING:
    from ..domain import MedLitDomainSchema


def _normalize_entity_name(e: str) -> str:
    return "".join(ch for ch in e.casefold() if ch.isalnum())


def _build_entity_index(entities: Sequence[BaseEntity]) -> dict[str, list[BaseEntity]]:
    idx: dict[str, list[BaseEntity]] = defaultdict(list)
    for e in entities:
        keys = [e.name, *getattr(e, "synonyms", [])]
        for k in keys:
            nk = _normalize_entity_name(k)
            if nk:
                idx[nk].append(e)
    return idx


def _deduplicate_relationships_by_predicate_specificity(
    relationships: list[BaseRelationship],
) -> list[BaseRelationship]:
    """For each (subject_id, object_id), keep only the relationship with highest predicate specificity."""
    if not relationships:
        return relationships
    key_to_best: dict[tuple[str, str], BaseRelationship] = {}
    for rel in relationships:
        key = (rel.subject_id, rel.object_id)
        pred = (getattr(rel, "predicate", "") or "").strip().lower()
        specificity = PREDICATE_SPECIFICITY.get(pred, 0)
        existing = key_to_best.get(key)
        if existing is None:
            key_to_best[key] = rel
            continue
        existing_pred = (getattr(existing, "predicate", "") or "").strip().lower()
        existing_spec = PREDICATE_SPECIFICITY.get(existing_pred, 0)
        if specificity > existing_spec:
            key_to_best[key] = rel
    return list(key_to_best.values())


def _normalize_evidence_for_match(text: str) -> str:
    """Normalize evidence text for substring matching: lowercase, strip, collapse whitespace."""
    return " ".join(text.strip().lower().split()) if text else ""


# Words that suggest evidence is about disease/marker context (IHC, staining, tumor, etc.)
_EVIDENCE_DISEASE_CONTEXT_WORDS = frozenset(
    {"tumor", "cancer", "cell", "cells", "positive", "negativity", "negative", "staining", "ihc", "immunohisto", "immunoreactivity", "positivity", "neoplastic"}
)


def _evidence_has_disease_context(evidence: str) -> bool:
    """Return True if evidence text suggests disease/marker context (IHC, tumor, etc.)."""
    if not evidence:
        return False
    norm = " ".join(evidence.strip().lower().split())
    return any(w in norm for w in _EVIDENCE_DISEASE_CONTEXT_WORDS)


def _evidence_contains_both_entities(
    evidence: str,
    subject_name: str,
    object_name: str,
    subject_entity: BaseEntity | None,
    object_entity: BaseEntity | None,
) -> tuple[bool, str | None, dict[str, Any]]:
    """Check that both subject and object (or synonyms) appear in the evidence text.

    Returns:
        (ok, drop_reason, detail): ok is True only if both entities appear;
        drop_reason is set when ok is False; detail has subject_in_evidence, object_in_evidence.
    """
    detail: dict[str, Any] = {"subject_in_evidence": False, "object_in_evidence": False}
    norm_evidence = _normalize_evidence_for_match(evidence)

    if not norm_evidence:
        return False, "evidence_empty", detail

    def _name_or_synonyms_appear_in_text(name: str, entity: BaseEntity | None) -> bool:
        candidates = [name]
        if entity is not None:
            candidates.append(entity.name)
            candidates.extend(getattr(entity, "synonyms", []))
        for c in candidates:
            if not c or not isinstance(c, str):
                continue
            norm = c.strip().lower()
            if norm and norm in norm_evidence:
                return True
        return False

    subject_ok = _name_or_synonyms_appear_in_text(subject_name, subject_entity)
    object_ok = _name_or_synonyms_appear_in_text(object_name, object_entity)
    detail["subject_in_evidence"] = subject_ok
    detail["object_in_evidence"] = object_ok

    if not subject_ok and not object_ok:
        return False, "evidence_missing_subject_and_object", detail
    if not subject_ok:
        return False, "evidence_missing_subject", detail
    if not object_ok:
        return False, "evidence_missing_object", detail
    return True, None, detail


async def _evidence_contains_both_entities_semantic(
    evidence: str,
    subject_entity: BaseEntity,
    object_entity: BaseEntity,
    embedding_generator: Any,
    threshold: float,
    evidence_cache: dict[str, tuple[float, ...]],
    entity_name_cache: dict[str, tuple[float, ...]],
) -> tuple[bool, str | None, dict[str, Any]]:
    """Check that evidence semantically contains both entities via embedding similarity.

    Uses evidence_cache and entity_name_cache to avoid duplicate embedding API calls
    within a document. Returns same shape as _evidence_contains_both_entities.
    """
    if not evidence or not evidence.strip():
        detail: dict[str, Any] = {
            "subject_in_evidence": False,
            "object_in_evidence": False,
            "subject_similarity": 0.0,
            "object_similarity": 0.0,
        }
        return False, "evidence_empty", detail

    # Evidence embedding (cached)
    if evidence not in evidence_cache:
        evidence_emb = await embedding_generator.generate(evidence)
        evidence_cache[evidence] = evidence_emb if isinstance(evidence_emb, tuple) else tuple(evidence_emb)
    evidence_emb = evidence_cache[evidence]

    # Subject embedding: use entity.embedding or generate and cache by name
    subject_emb = getattr(subject_entity, "embedding", None)
    if subject_emb is None or (hasattr(subject_emb, "__len__") and len(subject_emb) == 0):
        if subject_entity.name not in entity_name_cache:
            raw = await embedding_generator.generate(subject_entity.name)
            entity_name_cache[subject_entity.name] = raw if isinstance(raw, tuple) else tuple(raw)
        subject_emb = entity_name_cache[subject_entity.name]
    subject_emb = subject_emb if isinstance(subject_emb, tuple) else tuple(subject_emb)

    # Object embedding: same
    object_emb = getattr(object_entity, "embedding", None)
    if object_emb is None or (hasattr(object_emb, "__len__") and len(object_emb) == 0):
        if object_entity.name not in entity_name_cache:
            raw = await embedding_generator.generate(object_entity.name)
            entity_name_cache[object_entity.name] = raw if isinstance(raw, tuple) else tuple(raw)
        object_emb = entity_name_cache[object_entity.name]
    object_emb = object_emb if isinstance(object_emb, tuple) else tuple(object_emb)

    subject_sim = _cosine_similarity(evidence_emb, subject_emb)
    object_sim = _cosine_similarity(evidence_emb, object_emb)

    subject_ok = subject_sim >= threshold
    object_ok = object_sim >= threshold
    detail = {
        "subject_in_evidence": subject_ok,
        "object_in_evidence": object_ok,
        "subject_similarity": round(subject_sim, 4),
        "object_similarity": round(object_sim, 4),
    }
    if not subject_ok and not object_ok:
        return False, "evidence_missing_subject_and_object", detail
    if not subject_ok:
        return False, "evidence_missing_subject", detail
    if not object_ok:
        return False, "evidence_missing_object", detail
    return True, None, detail


class MedLitRelationshipExtractor(RelationshipExtractorInterface):
    """Extract relationships from journal articles.

    This extractor works with Paper JSON format from med-lit-schema, which
    already contains extracted relationships. We convert those to BaseRelationship objects.

    Can also use Ollama LLM to extract relationships directly from text if llm_client is provided.
    """

    def __init__(
        self,
        llm_client: Optional[LLMClientInterface] = None,
        domain: Optional["MedLitDomainSchema"] = None,
        trace_dir: Optional[Path] = None,
        embedding_generator: Any = None,
        evidence_similarity_threshold: float = 0.5,
    ):
        """Initialize relationship extractor.

        Args:
            llm_client: Optional LLM client for extracting relationships from text.
                        If None, only uses pre-extracted relationships from Paper JSON.
            domain: Optional domain schema for type validation and predicate constraints.
                    If provided, will attempt to swap subject/object on type mismatches.
            trace_dir: Optional directory for writing trace files. If None, uses default.
            embedding_generator: Optional embedding generator for semantic evidence validation.
                                When set, failed string evidence check is retried with cosine similarity.
            evidence_similarity_threshold: Minimum cosine similarity (0-1) for semantic evidence pass. Default 0.5.
        """
        self._llm = llm_client
        self._trace_dir = trace_dir or DEFAULT_TRACE_DIR
        self._embedding_generator = embedding_generator
        self._evidence_similarity_threshold = evidence_similarity_threshold
        # Per-document caches; reset at start of each _extract_with_llm call
        self._evidence_embedding_cache: dict[str, tuple[float, ...]] = {}
        self._entity_name_embedding_cache: dict[str, tuple[float, ...]] = {}
        if domain is None:
            # Import at runtime to avoid circular import
            from ..domain import MedLitDomainSchema

            domain = MedLitDomainSchema()
        self._domain = domain

    @property
    def trace_dir(self) -> Path:
        """Get the trace directory."""
        return self._trace_dir

    @trace_dir.setter
    def trace_dir(self, value: Path) -> None:
        """Set the trace directory."""
        self._trace_dir = value

    def _should_swap_subject_object(self, predicate: str, subject_entity: BaseEntity, object_entity: BaseEntity) -> bool:
        """Check if subject and object should be swapped based on type constraints.

        Args:
            predicate: The relationship predicate
            subject_entity: The subject entity
            object_entity: The object entity

        Returns:
            True if swapping subject and object would satisfy type constraints, False otherwise.
        """
        if predicate not in self._domain.predicate_constraints:
            return False  # No constraints to check

        constraints = self._domain.predicate_constraints[predicate]
        subject_type = subject_entity.get_entity_type()
        object_type = object_entity.get_entity_type()

        # Check if current order violates constraints
        subject_valid = subject_type in constraints.subject_types
        object_valid = object_type in constraints.object_types

        if subject_valid and object_valid:
            return False  # Current order is fine

        # Check if swapping would fix it
        swapped_subject_valid = object_type in constraints.subject_types
        swapped_object_valid = subject_type in constraints.object_types

        return swapped_subject_valid and swapped_object_valid

    def _validate_predicate_semantics(self, predicate: str, evidence: str) -> bool:
        """Validate that predicate semantics match the evidence text.

        Checks for semantic mismatches like:
        - "increases_risk" with positive therapeutic language
        - "treats" with negative/harmful language

        Args:
            predicate: The relationship predicate (e.g., "treats", "increases_risk")
            evidence: The evidence text supporting the relationship

        Returns:
            True if predicate matches evidence semantics, False if there's a mismatch.
        """
        if not evidence:
            return True  # No evidence to validate against

        evidence_lower = evidence.lower()

        # Positive therapeutic language
        positive_words = {
            "therapy",
            "therapeutic",
            "treatment",
            "treats",
            "treating",
            "beneficial",
            "benefit",
            "improves",
            "improvement",
            "reduces",
            "reduction",
            "relieves",
            "relief",
            "effective",
            "efficacy",
            "efficacious",
            "cures",
            "curing",
            "heals",
            "healing",
            "complementary therapy",
            "potential",
            "promising",
        }

        # Negative/harmful language
        negative_words = {
            "risk",
            "risks",
            "increases risk",
            "raises risk",
            "elevates risk",
            "causes",
            "causing",
            "harmful",
            "harm",
            "worsens",
            "worsening",
            "adverse",
            "adversely",
            "damages",
            "damage",
            "detrimental",
            "predisposes",
            "predisposition",
            "leads to",
            "results in",
        }

        has_positive = any(word in evidence_lower for word in positive_words)
        has_negative = any(word in evidence_lower for word in negative_words)

        # Check for semantic mismatches
        if predicate == "increases_risk":
            # "increases_risk" should have negative language, not positive
            if has_positive and not has_negative:
                return False  # Evidence is positive but predicate is negative

        elif predicate == "treats":
            # "treats" should have positive language, not negative
            if has_negative and not has_positive:
                return False  # Evidence is negative but predicate is positive

        # Other predicates are less strict, but we can add more checks if needed
        return True

    async def extract(
        self,
        document: BaseDocument,
        entities: Sequence[BaseEntity],
    ) -> list[BaseRelationship]:
        """Extract relationships from a journal article.

        If the document metadata contains pre-extracted relationships (from med-lit-schema),
        we convert those to BaseRelationship objects. Otherwise, if llm_client is provided,
        extracts relationships from document text using LLM.

        Args:
            document: The journal article document.
            entities: The resolved entities from this document.

        Returns:
            List of BaseRelationship objects representing relationships in the paper.
        """
        relationships: list[BaseRelationship] = []

        # Check if document has pre-extracted relationships in metadata
        # (from med-lit-schema's Paper format)
        relationships_data = document.metadata.get("relationships", [])

        if relationships_data:
            # Convert pre-extracted relationships to BaseRelationship objects
            entity_by_id: dict[str, BaseEntity] = {e.entity_id: e for e in entities}

            for rel_data in relationships_data:
                # Handle both dict format and AssertedRelationship format
                if isinstance(rel_data, dict):
                    subject_id = rel_data.get("subject_id", "")
                    predicate = rel_data.get("predicate", "")
                    object_id = rel_data.get("object_id", "")
                    confidence = rel_data.get("confidence", 0.5)
                    evidence_text = rel_data.get("evidence", "")
                    section = rel_data.get("section", "")
                    paragraph = rel_data.get("paragraph")  # Optional paragraph index

                    # Validate that entities exist
                    if subject_id not in entity_by_id or object_id not in entity_by_id:
                        # Skip relationships where entities weren't resolved
                        continue

                    # Normalize predicate (lowercase, handle enum values)
                    if isinstance(predicate, str):
                        predicate = predicate.lower()
                    else:
                        # If it's an enum, get its value
                        predicate = str(predicate).lower()

                    # Create structured provenance
                    provenance = Provenance(
                        document_id=document.document_id,
                        source_uri=document.source_uri,
                        section=section if section else None,
                        paragraph=paragraph if paragraph is not None else None,
                    )

                    # Create structured evidence
                    evidence_obj = Evidence(
                        kind="extracted",
                        source_documents=(document.document_id,),
                        primary=provenance,
                        mentions=(provenance,),
                        notes={"evidence_text": evidence_text} if evidence_text else {},
                    )

                    # Add any additional metadata from the relationship
                    metadata: dict[str, Any] = {}
                    if "metadata" in rel_data and isinstance(rel_data["metadata"], dict):
                        metadata.update(rel_data["metadata"])

                    relationship = MedicalClaimRelationship(
                        subject_id=subject_id,
                        predicate=predicate,
                        object_id=object_id,
                        confidence=float(confidence),
                        source_documents=(document.document_id,),
                        evidence=evidence_obj,
                        created_at=datetime.now(timezone.utc),
                        last_updated=None,
                        metadata=metadata,
                    )

                    relationships.append(relationship)
            return relationships

        # No pre-extracted relationships - try LLM extraction if available
        if self._llm and entities and document.content:
            try:
                print(f"  Extracting relationships with LLM from {len(entities)} entities...")
                extracted = await self._extract_with_llm(document, entities)
                relationships.extend(extracted)
                print(f"  LLM extracted {len(extracted)} relationships")
            except Exception as e:
                print(f"Warning: LLM relationship extraction failed: {e}")
                import traceback

                traceback.print_exc()

        return relationships

    def _build_llm_prompt(self, text_sample: str, entity_list: str) -> str:
        """
        Build the prompt for the LLM.

        Notes:
        - This prompt is driven by the domain schema:
          - self._domain.relationship_types (vocabulary)
          - self._domain.predicate_constraints (allowed subject/object types)
        - Predicates must be returned in *lowercase* (e.g. "treats"), because downstream
          code currently normalizes and stores predicates as lowercase. :contentReference[oaicite:3]{index=3}
        """
        # 1) Predicate inventory from domain schema
        # Domain keys are like "treats"; we ask LLM for lowercase strings like "treats"
        predicate_keys = sorted(self._domain.relationship_types.keys())
        # Put associated_with last, not first
        allowed_predicates = [k.lower() for k in predicate_keys if k != "associated_with"]
        allowed_predicates.append("associated_with")  # associated_with goes last to reduce LLM anchor bias

        # Optional: a tiny bit of extra guidance for a few high-frequency predicates
        extra_guidance = [
            "- Prefer the *most specific* predicate that matches the evidence.",
            '- Use "associated_with" ONLY if no other predicate fits the evidence.',
            "- Each relationship MUST include a short evidence quote where BOTH entities appear.",
            "- Skip speculative relationships not supported by explicit text.",
            '- "treats" means ONLY (drug) -> (disease). A disease never "treats" a procedure or protein.',
            "- When a procedure (e.g. IHC, biopsy) is used to work up a disease, use diagnosed_by: (disease) -> (procedure).",
            "- When a protein/marker is positive in a disease context, use indicates (marker -> disease) or associated_with, not treats.",
            "- When the text lists multiple markers (e.g. 'positivity for BerEp4, CAM5.2, Ki67'), extract (marker, indicates, disease) or (disease, associated_with, marker) for EACH marker listed; do not skip markers just because there are many.",
            "- For marker-disease relationships, the evidence quote must include the marker; the disease may be inferred from document context (e.g. 'tumor cells' in a paper about that cancer) and need not appear in the same quote.",
            '- Use "cites" ONLY between two paper entities: (paper) -> cites -> (paper). When the text references another publication by title or author (e.g. "Smith et al. reported...", "as shown in [12]"), extract (current_paper, cites, cited_paper).',
        ]

        examples_section = """
EXAMPLES (follow subject/object order and use allowed predicates):
- Text: "IHC was performed; tumor cells were positive for BerEp4." → (BerEp4, indicates, Disease); NOT (Disease, treats, BerEp4).
- Text: "positivity for BerEp4, CAM5.2, Ki67" in a paper about a cancer → extract (BerEp4, indicates, Disease), (CAM5.2, indicates, Disease), (Ki67, indicates, Disease) (one per marker).
- Text: "Immunohistochemistry was performed on cell blocks." for disease + procedure → (Disease, diagnosed_by, Immunohistochemical staining).
"""

        return f"""You extract medical relationships from biomedical text.

You are given:
1) A list of entities (name, type, id) already extracted from this document.
2) A text snippet from the document.

Your job:
- Find relationships between the listed entities that are explicitly supported by the text.
- We validate subject/object types server-side; use entity names from the list.
- Output ONLY valid JSON: a JSON array of relationship objects.
- Use ONLY the allowed predicates listed below (lowercase strings).

ALLOWED PREDICATES:
{", ".join(allowed_predicates)}

GUIDELINES:
{chr(10).join(extra_guidance)}
{examples_section}
ENTITIES IN DOCUMENT (name (type): id):
{entity_list}

TEXT:
{text_sample}

OUTPUT FORMAT (JSON ARRAY ONLY):
[
  {{
    "subject": "entity_name_exactly_as_listed",
    "predicate": "treats",
    "object": "entity_name_exactly_as_listed",
    "confidence": 0.0,
    "evidence": "short exact quote from text"
  }}
]

IMPORTANT:
- Use entity names from the list; do not invent entities.
- confidence is a float in [0, 1].
- If confidence would be below 0.5, OMIT the relationship entirely.
- If the only predicate that fits is "associated_with", OMIT the relationship unless
  the text explicitly says something like "is associated with" or "was associated with".
  Do NOT use it as a fallback for unclear relationships.
- Return ONLY the JSON array, no prose, no markdown fences.
"""

    async def _extract_with_llm(
        self,
        document: BaseDocument,
        entities: Sequence[BaseEntity],
    ) -> list[BaseRelationship]:
        """Extract relationships using LLM.

        Also writes a trace file to /tmp/kgraph-relationship-traces/ for debugging.
        The trace captures: prompt, raw LLM output, parsed JSON, and per-item decisions.
        """
        if not self._llm:
            return []

        # Reset per-document caches for semantic evidence validation
        self._evidence_embedding_cache = {}
        self._entity_name_embedding_cache = {}

        # Initialize trace for debugging
        trace: dict[str, Any] = {
            "document_id": document.document_id,
            "source_uri": getattr(document, "source_uri", None),
            "llm_model": getattr(self._llm, "model", None),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "entity_count": len(entities),
            "prompt": None,
            "raw_llm_output": None,
            "parsed_json": None,
            "decisions": [],
            "final_relationships": [],
            "error": None,
        }

        """
        Removing the limit on the size of the entities list......

        This may help recall in some cases, but it can also **tank
        relationship quality** (LLMs get overwhelmed and start producing
        generic or spurious edges). If you notice regressions, the “best of
        both worlds” is:

        - include **all entities** in the *matching index* (which you do)
        - but include a **curated subset** in the prompt list:

            - all canonicals
            - plus entities that appear in the abstract
            - plus top-N by usage_count/confidence

        This will reduce prompt bloat without sacrificing matching coverage.
        """
        # entity_list = "\n".join(f"- {e.name} ({e.get_entity_type()}): {e.entity_id}" for e in entities[:50])  # Limit to avoid huge prompts
        entity_list = "\n".join(f"- {e.name} ({e.get_entity_type()}): {e.entity_id}" for e in entities)

        # Use abstract for extraction (shorter, more focused)
        text = document.abstract if hasattr(document, "abstract") and document.abstract else document.content
        text_sample = text[:2000]  # Limit text size for faster processing

        prompt = self._build_llm_prompt(text_sample, entity_list)

        trace["prompt"] = prompt

        try:
            # Use generate_json_with_raw to capture both parsed and raw output
            print("  Calling LLM for relationships (window may take 1–2 min)...", flush=True)
            if hasattr(self._llm, "generate_json_with_raw"):
                response, raw_output = await self._llm.generate_json_with_raw(prompt)
                trace["raw_llm_output"] = raw_output
            else:
                response = await self._llm.generate_json(prompt)
                trace["raw_llm_output"] = "<raw unavailable - method not supported>"

            n_items = len(response) if isinstance(response, list) else 0
            print(f"  LLM returned {n_items} candidate relationship(s), validating...", flush=True)
            trace["parsed_json"] = response
            relationships: list[BaseRelationship] = []

            if isinstance(response, list):
                entity_index = _build_entity_index(entities)
                for i, item in enumerate(response):
                    if n_items > 5 and (i + 1) % 5 == 0:
                        print(f"  Validated {i + 1}/{n_items} items...", flush=True)
                    relationship, decision = await self._process_llm_item(item, entity_index, document)
                    trace["decisions"].append(decision)
                    if relationship:
                        relationships.append(relationship)

            relationships = _deduplicate_relationships_by_predicate_specificity(relationships)

            # Record final relationships in trace
            trace["final_relationships"] = [
                {
                    "subject_id": r.subject_id,
                    "predicate": r.predicate,
                    "object_id": r.object_id,
                    "confidence": getattr(r, "confidence", None),
                }
                for r in relationships
            ]

            # Write trace file
            self._write_trace(document.document_id, trace)

            return relationships

        except Exception as e:
            print(f"Warning: LLM relationship extraction failed: {e}")
            trace["error"] = repr(e)
            # Still write trace on error so we can debug
            self._write_trace(document.document_id, trace)
            return []

    async def _process_llm_item(  # pylint: disable=too-many-statements
        self,
        item: Any,
        entity_index: dict[str, list[BaseEntity]],
        document: BaseDocument,
    ) -> tuple[BaseRelationship | None, dict[str, Any]]:
        """Process a single item from the LLM response."""
        if not isinstance(item, dict):
            return None, {"item": item, "accepted": False, "drop_reason": "item_not_a_dict"}

        subject_name = item.get("subject", "").strip()
        predicate = item.get("predicate", "").lower()
        object_name = item.get("object", "").strip()
        confidence = float(item.get("confidence", 0.5))
        evidence = item.get("evidence", "")

        decision: dict[str, Any] = {
            "item": item,
            "subject_name": subject_name,
            "object_name": object_name,
            "predicate": predicate,
            "confidence": confidence,
            "matched_subject": False,
            "matched_object": False,
            "semantic_ok": None,
            "swap_applied": False,
            "accepted": False,
            "drop_reason": None,
            "resolved": {
                "subject_id": None,
                "subject_type": None,
                "object_id": None,
                "object_type": None,
            },
        }

        def _pick_unique(cands: list[BaseEntity]) -> BaseEntity | None:
            if not cands:
                return None
            if len(cands) == 1:
                return cands[0]
            # collision: prefer canonical, else highest usage_count/confidence if you have them
            cands2 = sorted(
                cands,
                key=lambda e: (
                    getattr(e, "status", "") == "canonical",
                    getattr(e, "usage_count", 0),
                    getattr(e, "confidence", 0.0),
                ),
                reverse=True,
            )
            return cands2[0]

        subject_entity = _pick_unique(entity_index.get(_normalize_entity_name(subject_name), []))
        object_entity = _pick_unique(entity_index.get(_normalize_entity_name(object_name), []))

        decision["matched_subject"] = subject_entity is not None
        decision["matched_object"] = object_entity is not None

        if not subject_entity or not object_entity:
            if not subject_entity and not object_entity:
                decision["drop_reason"] = "subject_and_object_unmatched"
            elif not subject_entity:
                decision["drop_reason"] = "subject_unmatched"
            else:
                decision["drop_reason"] = "object_unmatched"
            return None, decision

        evidence_ok, evidence_drop_reason, evidence_detail = _evidence_contains_both_entities(evidence, subject_name, object_name, subject_entity, object_entity)
        if evidence_ok:
            evidence_detail["method"] = "string_match"
        if not evidence_ok and evidence_drop_reason in ("evidence_missing_subject", "evidence_missing_object"):
            decision["evidence_check"] = evidence_detail
            decision["drop_reason"] = evidence_drop_reason
            return None, decision
        if not evidence_ok and self._embedding_generator is not None:
            evidence_ok, evidence_drop_reason, evidence_detail = await _evidence_contains_both_entities_semantic(
                evidence,
                subject_entity,
                object_entity,
                self._embedding_generator,
                self._evidence_similarity_threshold,
                self._evidence_embedding_cache,
                self._entity_name_embedding_cache,
            )
            if evidence_ok:
                evidence_detail["method"] = "semantic_match"
                evidence_detail["threshold"] = self._evidence_similarity_threshold
        # Marker-disease (indicates/associated_with): allow evidence that names the marker
        # and has disease context (tumor, IHC, etc.) when the disease appears elsewhere in the window.
        if not evidence_ok and predicate in ("indicates", "associated_with"):
            if object_entity.get_entity_type() == "disease" and evidence_detail.get("subject_in_evidence"):
                window_text = getattr(document, "content", "") or ""
                if window_text and object_entity.name.lower() in window_text.lower():
                    if _evidence_has_disease_context(evidence):
                        evidence_ok = True
                        evidence_detail["object_in_evidence"] = True
                        evidence_detail["method"] = "context_inferred"
        decision["evidence_check"] = evidence_detail
        if not evidence_ok:
            decision["drop_reason"] = evidence_drop_reason
            return None, decision

        semantic_ok = self._validate_predicate_semantics(predicate, evidence)
        decision["semantic_ok"] = semantic_ok
        if not semantic_ok:
            print(f"  Warning: Semantic mismatch - predicate '{predicate}' " f"does not match evidence: {evidence[:100]}...")
            decision["drop_reason"] = "semantic_mismatch"
            return None, decision

        if self._should_swap_subject_object(predicate, subject_entity, object_entity):
            print(
                f"  Swapping subject/object for predicate '{predicate}': "
                f"({subject_entity.name} [{subject_entity.get_entity_type()}] ↔ "
                f"{object_entity.name} [{object_entity.get_entity_type()}])"
            )
            subject_entity, object_entity = object_entity, subject_entity
            decision["swap_applied"] = True

        decision["resolved"] = {
            "subject_id": subject_entity.entity_id,
            "subject_type": subject_entity.get_entity_type(),
            "object_id": object_entity.entity_id,
            "object_type": object_entity.get_entity_type(),
        }

        constraint = self._domain.predicate_constraints.get(predicate)

        if constraint:
            s_type = subject_entity.get_entity_type()
            o_type = object_entity.get_entity_type()

            ok = (s_type in constraint.subject_types) and (o_type in constraint.object_types)
            if not ok:
                decision["accepted"] = False
                decision["drop_reason"] = "type_constraint_mismatch"
                decision["type_check"] = {
                    "predicate_key": predicate,
                    "got_subject_type": s_type,
                    "got_object_type": o_type,
                    "expected_subject_types": sorted(constraint.subject_types),
                    "expected_object_types": sorted(constraint.object_types),
                }
                return None, decision

        provenance = Provenance(
            document_id=document.document_id,
            source_uri=document.source_uri,
            section="abstract" if hasattr(document, "abstract") and document.abstract else None,
        )

        evidence_obj = Evidence(
            kind="llm_extracted",
            source_documents=(document.document_id,),
            primary=provenance,
            mentions=(provenance,),
            notes={"evidence_text": evidence, "extraction_method": "llm"},
        )

        rel = MedicalClaimRelationship(
            subject_id=subject_entity.entity_id,
            predicate=predicate,
            object_id=object_entity.entity_id,
            confidence=confidence,
            source_documents=(document.document_id,),
            evidence=evidence_obj,
            created_at=datetime.now(timezone.utc),
            last_updated=None,
            metadata={"extraction_method": "llm"},
        )

        decision["accepted"] = True
        return rel, decision

    def write_skip_trace(
        self,
        document_id: str,
        reason: str,
        entity_count: int,
    ) -> None:
        """Write a minimal trace file when a window is skipped (e.g. fewer than 2 entities).

        Uses the same path convention as _write_trace so skip and full traces
        appear in the same directory. Call from WindowedRelationshipExtractor
        when a chunk is skipped so --trace-all still produces a trace per window.
        """
        trace: dict[str, Any] = {
            "document_id": document_id,
            "skipped": True,
            "reason": reason,
            "entity_count": entity_count,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._write_trace(document_id, trace)

    def _write_trace(self, document_id: str, trace: dict[str, Any]) -> None:
        """Write trace file for debugging relationship extraction.

        When document_id is from a windowed run (e.g. PMC12770061_window_5),
        the filename includes the window index so each window gets its own file
        (e.g. PMC12770061.5.relationships.trace.json) and earlier windows are
        not overwritten.
        """
        try:
            self._trace_dir.mkdir(parents=True, exist_ok=True)
            base_id = document_id
            window_suffix = ""
            if "_window_" in document_id:
                base_id, _, window_index = document_id.partition("_window_")
                window_suffix = f".{window_index}"
            trace_path = self._trace_dir / f"{base_id}{window_suffix}.relationships.trace.json"
            trace_path.write_text(json.dumps(trace, indent=2, ensure_ascii=False))
            print(f"  Wrote relationship trace: {trace_path}")
        except Exception as e:
            print(f"  Warning: Failed to write trace file: {e}")

"""Entity mention extraction from journal articles.

Extracts entity mentions from Paper JSON format (from med-lit-schema).
Since the papers already have extracted entities, we convert those to EntityMention objects.
Can also use Ollama LLM for NER extraction from text.
"""

from kgschema.document import BaseDocument
from kgschema.domain import DomainSchema
from kgschema.entity import EntityMention
from kgraph.pipeline.interfaces import EntityExtractorInterface

from kgraph.pipeline.llm_client import LLMClientInterface


def _normalize_mention_key(name: str, entity_type: str) -> tuple[str, str]:
    """Normalized key for deduping mentions: (alphanumeric lower name, type)."""
    key_name = "".join(c for c in name.strip().casefold() if c.isalnum() or c.isspace()).strip() or name.strip().casefold()
    return (key_name, entity_type)


# Type mapping for common LLM mistakes
TYPE_MAPPING: dict[str, str | None] = {
    # Common mistakes → correct types
    "test": "procedure",
    "diagnostic": "procedure",
    "imaging": "procedure",
    "assay": "biomarker",
    "marker": "biomarker",
    # Genetic variants → gene (polymorphisms, mutations, variants are genetic entities)
    "polymorphism": "gene",
    "mutation": "gene",
    "variant": "gene",
    # Non-medical entities (skip these)
    "system": None,
    "organization": None,
}

# Entity type labels that must not be used as entity names (LLM sometimes returns type in "entity" field)
KNOWN_TYPE_LABELS: frozenset[str] = frozenset(
    {
        "disease",
        "gene",
        "drug",
        "protein",
        "symptom",
        "procedure",
        "biomarker",
        "pathway",
        "location",
        "ethnicity",
        "variant",
        "polymorphism",
        "mutation",
        "test",
        "diagnostic",
        "imaging",
        "assay",
        "marker",
        "system",
        "organization",
    }
)


def _is_type_masquerading_as_name(name: str, entity_type: str) -> bool:
    """Return True if the name is just the entity type (or a type label), not a real entity name.

    When the LLM (or pre-extracted data) puts the type in the 'entity'/'name' field,
    we get e.g. name='disease', type='disease'. Reject these so we never create
    entities whose name is the type.
    """
    n = name.strip().lower()
    t = entity_type.strip().lower()
    if not n:
        return True
    if n == t:
        return True
    if n in KNOWN_TYPE_LABELS:
        return True
    return False


class MedLitEntityExtractor(EntityExtractorInterface):
    """Extract entity mentions from journal articles.

    This extractor works with Paper JSON format from med-lit-schema, which
    already contains extracted entities. We convert those to EntityMention objects.

    Can also use Ollama LLM to extract entities directly from text if llm_client is provided.
    Note: Canonical ID lookup is handled during the promotion phase, not during extraction.
    """

    OLLAMA_NER_PROMPT = """Extract medical entities from the following text. Return a JSON array.

Valid entity types (use EXACTLY ONE per entity):
- disease: Medical conditions, disorders, syndromes (diabetes, breast cancer)
- gene: Genes, genetic variants, mutations, polymorphisms (BRCA1, TP53, EGFR, Q223R, K109R)
- drug: Medications, therapeutic substances (aspirin, paclitaxel)
- protein: Proteins (p53, EGFR protein, insulin)
- symptom: Clinical signs and symptoms (fever, pain, fatigue)
- procedure: Medical tests, diagnostics, treatments (MRI, CT scan, biopsy, surgery)
- biomarker: Measurable indicators (PSA, CA-125, blood glucose)
- pathway: Biological pathways (apoptosis, glycolysis, MAPK signaling)
- location: Geographic locations (China, United States, Inner Mongolia, Boston)
- ethnicity: Ethnic or population groups (Han, Mongolian, Caucasian, African American)

Rules:
1. Use EXACTLY ONE type per entity (no pipes like "drug|protein")
2. Choose the most specific type that fits
3. Format: [{{"entity": "name", "type": "disease", "confidence": 0.95}}]
4. Return ONLY the JSON array, no explanation

Text:
{text}

JSON:"""

    def __init__(
        self,
        llm_client: LLMClientInterface | None = None,
        domain: DomainSchema | None = None,
    ):
        """Initialize entity extractor.

        Args:
            llm_client: Optional LLM client for extracting entities from text.
                        If None, only uses pre-extracted entities from Paper JSON.
            domain: Domain schema for entity type validation (needed for normalization).
        """
        self._llm = llm_client
        self._domain = domain

    def _normalize_entity_type(self, entity_type_raw: str) -> str | None:
        """Normalize LLM entity types to schema types.

        Handles:
        - Multi-type format (drug|protein) → takes first valid type
        - Common mistakes (test → procedure)
        - Invalid types → returns None (skip entity)

        Args:
            entity_type_raw: Raw entity type string from LLM

        Returns:
            Normalized type string if valid, None if invalid/non-medical
        """
        if not self._domain:
            # No domain provided - basic normalization only
            entity_type = entity_type_raw.lower().strip()
            if "|" in entity_type:
                entity_type = entity_type.split("|")[0].strip()
            return TYPE_MAPPING.get(entity_type, entity_type)

        # Handle multi-type format (drug|protein)
        if "|" in entity_type_raw:
            # Take first valid type
            for type_part in entity_type_raw.split("|"):
                type_part = type_part.strip().lower()
                # Check if it's a valid schema type
                if type_part in self._domain.entity_types:
                    return type_part
            # No valid types found in pipe-separated list
            return None

        # Normalize single type
        entity_type = entity_type_raw.lower().strip()

        # Check mapping for common mistakes
        if entity_type in TYPE_MAPPING:
            mapped = TYPE_MAPPING[entity_type]
            if mapped is None:
                return None  # Explicitly skip this type
            entity_type = mapped

        # Validate against schema
        if entity_type in self._domain.entity_types:
            return entity_type

        # Unknown type - skip this entity
        return None

    async def extract(self, document: BaseDocument) -> list[EntityMention]:
        """Extract entity mentions from a journal article (single chunk).

        If the document metadata contains pre-extracted entities (from med-lit-schema),
        we convert those to EntityMention objects. Otherwise, if llm_client is provided,
        extracts entities from document text using LLM (one prompt per document/chunk).

        When used behind BatchingEntityExtractor, this is called once per chunk;
        the orchestrator handles streaming and deduplication across chunks.

        Args:
            document: The journal article document (or a chunk document).

        Returns:
            List of EntityMention objects for this document/chunk.
        """
        mentions: list[EntityMention] = []

        # Check if document has pre-extracted entities in metadata
        # (from med-lit-schema's Paper format)
        entities_data = document.metadata.get("entities", [])

        if entities_data:
            # Convert pre-extracted entities to EntityMention objects
            for entity_ref in entities_data:
                # Handle both dict format and EntityReference format
                if isinstance(entity_ref, dict):
                    entity_id = entity_ref.get("id", "")
                    entity_name = entity_ref.get("name", "")
                    entity_type = entity_ref.get("type", "")

                    # Map med-lit-schema entity types to kgraph entity types
                    # (they should match, but normalize just in case)
                    entity_type = entity_type.lower() if entity_type else ""

                    # Skip if name is actually the type (e.g. name="disease", type="disease")
                    if _is_type_masquerading_as_name(entity_name, entity_type):
                        continue

                    # Create mention (we don't have exact text spans, so use 0 offsets)
                    # The text is the name as it appeared in the paper
                    mention = EntityMention(
                        text=entity_name,
                        entity_type=entity_type,
                        start_offset=0,  # Unknown from pre-extracted format
                        end_offset=0,  # Unknown from pre-extracted format
                        confidence=0.9,  # Assume high confidence for pre-extracted
                        context=None,
                        metadata={
                            "canonical_id_hint": entity_id,
                            "document_id": document.document_id,
                            "pre_extracted": True,
                        },
                    )
                    mentions.append(mention)
            return mentions

        # No pre-extracted entities - try LLM extraction if available
        if not self._llm:
            return mentions

        text = document.abstract if hasattr(document, "abstract") and document.abstract else document.content
        if not text or len(text) < 50:
            return mentions

        try:
            text_sample = text[:8000]  # Single chunk may be up to window size
            prompt = self.OLLAMA_NER_PROMPT.format(text=text_sample)
            response = await self._llm.generate_json(prompt)
            if isinstance(response, list):
                for item in response:
                    if not isinstance(item, dict):
                        continue
                    entity_name = (item.get("entity") or item.get("name", "")).strip()
                    entity_type_raw = item.get("type", "disease")
                    entity_type = self._normalize_entity_type(entity_type_raw)
                    if entity_type is None or len(entity_name) < 3:
                        continue
                    # Skip if LLM put the type in the "entity" field (e.g. entity="disease", type="disease")
                    if _is_type_masquerading_as_name(entity_name, entity_type):
                        continue
                    confidence = float(item.get("confidence", 0.5))
                    if confidence < 0.5:
                        continue
                    mention = EntityMention(
                        text=entity_name,
                        entity_type=entity_type,
                        start_offset=0,
                        end_offset=0,
                        confidence=confidence,
                        context=None,
                        metadata={
                            "document_id": document.document_id,
                            "extraction_method": "llm",
                        },
                    )
                    mentions.append(mention)
        except Exception as e:
            print(f"Warning: LLM entity extraction failed: {e}")
            import traceback

            traceback.print_exc()

        return mentions

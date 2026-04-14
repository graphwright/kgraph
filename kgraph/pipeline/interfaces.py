"""Pipeline interface definitions for document processing and extraction.

This module defines the abstract interfaces for the two-pass ingestion pipeline:

- **Pass 1 (Entity Extraction)**: Parse documents, extract entity mentions,
  and resolve them to canonical or provisional entities.
- **Pass 2 (Relationship Extraction)**: Identify relationships/edges between
  the resolved entities within each document.

The pipeline components are designed to be pluggable, allowing different
implementations for different domains (medical literature, legal documents,
academic papers, etc.) or different underlying technologies (LLMs, NER models,
rule-based extractors).

Typical flow:
    1. DocumentParserInterface converts raw bytes to BaseDocument
    2. EntityExtractorInterface identifies EntityMention instances
    3. EntityResolverInterface maps mentions to BaseEntity instances
    4. RelationshipExtractorInterface finds relationships between entities
"""

from abc import ABC, abstractmethod
from typing import Sequence

from kgschema.document import BaseDocument
from kgschema.entity import BaseEntity, EntityMention
from kgschema.relationship import BaseRelationship
from kgschema.storage import EntityStorageInterface


class DocumentParserInterface(ABC):
    """Parse raw documents into structured BaseDocument instances.

    Implementations handle format-specific parsing (PDF, HTML, plain text, etc.)
    and extract document metadata such as title, author, publication date, and
    structural elements like sections and paragraphs.

    This is the entry point for the ingestion pipeline. The parsed document
    provides the content that subsequent extractors process.

    Example implementations might use:
        - PDF parsing libraries (PyMuPDF, pdfplumber)
        - HTML parsing (BeautifulSoup, lxml)
        - LLMs for structure extraction from unstructured text
    """

    @abstractmethod
    async def parse(
        self,
        raw_content: bytes,
        content_type: str,
        source_uri: str | None = None,
    ) -> BaseDocument:
        """Parse raw content into a structured document.

        Args:
            raw_content: Raw document bytes (may be UTF-8 text, PDF binary, etc.)
            content_type: MIME type or format indicator (e.g., 'text/plain',
                'application/pdf', 'text/html') used to select parsing strategy
            source_uri: Optional URI identifying the document's origin, useful
                for deduplication and provenance tracking

        Returns:
            A BaseDocument instance with extracted content and metadata,
            ready for entity and relationship extraction.

        Raises:
            ValueError: If content_type is unsupported or content is malformed.
        """


class EntityExtractorInterface(ABC):
    """Extract entity mentions from documents (Pass 1 of ingestion).

    This interface handles the first pass of document processing: identifying
    spans of text that refer to entities of interest. The output is a list of
    EntityMention objects representing raw extractions that have not yet been
    resolved to canonical or provisional entities.

    Entity mentions capture:
        - The exact text span and its position in the document
        - The inferred entity type (domain-specific, e.g., 'drug', 'gene', 'person')
        - Extraction confidence score
        - Surrounding context for disambiguation

    Implementations may use:
        - Named Entity Recognition (NER) models (spaCy, Hugging Face transformers)
        - Large Language Models with structured extraction prompts
        - Rule-based pattern matching for domain-specific entities
        - Hybrid approaches combining multiple techniques
    """

    @abstractmethod
    async def extract(self, document: BaseDocument) -> list[EntityMention]:
        """Extract entity mentions from a document.

        Scans the document content to identify text spans that refer to
        entities of interest. Does not perform resolution—that is handled
        separately by EntityResolverInterface.

        Args:
            document: The parsed document to extract entities from.

        Returns:
            List of EntityMention objects, each representing a detected
            entity reference with its text, position, type, and confidence.
            Returns an empty list if no entities are found.
        """


class EntityResolverInterface(ABC):
    """Resolve entity mentions to canonical or provisional entities.

    After extraction, entity mentions must be resolved to determine whether
    they refer to existing known entities or represent new discoveries. This
    interface handles the resolution process through multiple strategies:

    1. **Name/synonym matching**: Check if the mention text matches known
       entity names or synonyms in storage.
    2. **Embedding similarity**: Use semantic vector similarity to find
       entities with similar meaning but different surface forms.
    3. **External authority lookup**: Query authoritative sources (UMLS for
       medical terms, Wikidata for general knowledge, etc.) to obtain
       canonical identifiers.
    4. **Provisional creation**: If no match is found, create a provisional
       entity that may later be promoted to canonical status based on
       usage frequency and confidence scores.

    The confidence score returned with each resolution indicates the certainty
    of the match, enabling downstream filtering and quality control.
    """

    @abstractmethod
    async def resolve(
        self,
        mention: EntityMention,
        existing_storage: EntityStorageInterface,
    ) -> tuple[BaseEntity, float]:
        """Resolve a single entity mention to an entity.

        Attempts to match the mention to existing canonical entities using
        name matching, embedding similarity, or external authority lookup.
        If no suitable match is found, creates a new provisional entity.

        Args:
            mention: The extracted entity mention to resolve.
            existing_storage: Storage interface to query for existing entities.
                Used for name lookups and embedding similarity searches.

        Returns:
            A tuple of (resolved_entity, confidence_score) where:
                - resolved_entity: Either an existing entity from storage,
                  a newly created canonical entity from an authority lookup,
                  or a newly created provisional entity.
                - confidence_score: Float between 0 and 1 indicating the
                  certainty of the resolution. Higher scores indicate stronger
                  matches; provisional entities typically have lower scores.
        """

    @abstractmethod
    async def resolve_batch(
        self,
        mentions: Sequence[EntityMention],
        existing_storage: EntityStorageInterface,
    ) -> list[tuple[BaseEntity, float]]:
        """Resolve multiple entity mentions efficiently.

        Batch resolution enables optimizations such as:
            - Batched embedding generation (single API call for all mentions)
            - Batched similarity searches against vector storage
            - Parallel authority lookups
            - Deduplication within the batch

        Args:
            mentions: Sequence of entity mentions to resolve.
            existing_storage: Storage interface to query for existing entities.

        Returns:
            List of (entity, confidence) tuples in the same order as input
            mentions. Each tuple follows the same semantics as resolve().
        """


class RelationshipExtractorInterface(ABC):
    """Extract relationships between entities from documents (Pass 2 of ingestion).

    After entities have been extracted and resolved, this interface identifies
    the relationships (edges) between them within the document context. This
    is the second pass of the ingestion pipeline.

    Relationships are typically expressed as (subject, predicate, object) triples
    with additional metadata such as:
        - Source document reference for provenance
        - Confidence score for the extraction
        - Supporting evidence (text spans, context)

    The predicate vocabulary is typically domain-specific:
        - Medical: 'treats', 'causes', 'interacts_with', 'inhibits'
        - Legal: 'cites', 'overrules', 'amends', 'references'
        - Academic: 'authored_by', 'cites', 'builds_upon', 'contradicts'

    Implementations may use:
        - LLMs with structured prompts listing entities and requesting triples
        - Dependency parsing to identify syntactic relationships
        - Pattern-based extraction using domain-specific templates
        - Pre-trained relation extraction models
    """

    @abstractmethod
    async def extract(
        self,
        document: BaseDocument,
        entities: Sequence[BaseEntity],
    ) -> list[BaseRelationship]:
        """Extract relationships between entities in a document.

        Analyzes the document content in the context of the provided entities
        to identify relationships. Only considers relationships between the
        given entities (not arbitrary text spans).

        Args:
            document: The source document providing context for extraction.
            entities: The resolved entities from this document. Relationships
                will only be extracted between entities in this sequence.

        Returns:
            List of BaseRelationship objects representing the extracted
            relationships. Each relationship includes subject/object entity
            references, predicate type, confidence score, and source document
            reference. Returns an empty list if no relationships are found.
        """

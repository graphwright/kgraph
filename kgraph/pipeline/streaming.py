"""Streaming extraction interfaces for large-document processing.

This module provides abstractions for processing documents in a streaming fashion,
breaking them into manageable chunks (windows) that can be processed incrementally.
This is essential for:

- **Large documents**: Processing documents that exceed LLM context windows
- **Memory efficiency**: Avoiding loading entire documents into memory
- **Incremental processing**: Starting extraction before full document is parsed
- **Context preservation**: Using overlapping windows to maintain entity/relationship
  context across chunk boundaries

The design follows the patterns established in the plod branch for PMC XML streaming,
providing generic abstractions that work across different document formats.

Key abstractions:
    - DocumentChunker: Splits documents into overlapping chunks/windows
    - StreamingEntityExtractor: Extracts entities from document chunks with deduplication
    - StreamingRelationshipExtractor: Extracts relationships within windows

Typical usage:
    ```python
    chunker = WindowedDocumentChunker(chunk_size=2000, overlap=200)
    chunks = await chunker.chunk(document)

    extractor = BatchingEntityExtractor(base_extractor, batch_size=10)
    all_mentions = []
    async for chunk_mentions in extractor.extract_streaming(chunks):
        all_mentions.extend(chunk_mentions)
    ```

Based on the streaming extraction patterns from:
    - medlit/medlit/pipeline/pmc_streaming.py (plod branch)
    - medlit/medlit/pipeline/mentions.py (windowed entity extraction)
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Sequence

from pydantic import BaseModel, Field

from kgschema.document import BaseDocument
from kgschema.entity import BaseEntity, EntityMention
from kgschema.relationship import BaseRelationship

import logging

from .interfaces import EntityExtractorInterface, RelationshipExtractorInterface

logger = logging.getLogger(__name__)


class DocumentChunk(BaseModel):
    """Represents a chunk/window of a document.

    Chunks may overlap to preserve context across boundaries. For example,
    a document split with 2000-character chunks and 200-character overlap
    ensures entities mentioned near chunk boundaries aren't missed.

    Attributes:
        content: The text content of this chunk
        start_offset: Character offset where this chunk starts in the original document
        end_offset: Character offset where this chunk ends in the original document
        chunk_index: Sequential index of this chunk (0-based)
        document_id: ID of the parent document
        metadata: Optional chunk-specific metadata (section name, page number, etc.)
    """

    model_config = {"frozen": True}

    content: str = Field(..., description="Text content of this chunk")
    start_offset: int = Field(..., ge=0, description="Starting character offset in original document")
    end_offset: int = Field(..., gt=0, description="Ending character offset in original document")
    chunk_index: int = Field(..., ge=0, description="Sequential index of this chunk (0-based)")
    document_id: str = Field(..., description="ID of the parent document")
    metadata: dict[str, str] = Field(default_factory=dict, description="Optional chunk-specific metadata")


class ChunkingConfig(BaseModel):
    """Configuration for document chunking strategies.

    Attributes:
        chunk_size: Target size of each chunk in characters
        overlap: Number of characters to overlap between consecutive chunks
        respect_boundaries: Whether to respect sentence/paragraph boundaries
        min_chunk_size: Minimum size for a chunk (to avoid tiny trailing chunks)
    """

    model_config = {"frozen": True}

    chunk_size: int = Field(2000, gt=0, description="Target size of each chunk in characters")
    overlap: int = Field(200, ge=0, description="Number of characters to overlap between chunks")
    respect_boundaries: bool = Field(True, description="Respect sentence/paragraph boundaries when chunking")
    min_chunk_size: int = Field(500, gt=0, description="Minimum size for a chunk")


class DocumentChunkerInterface(ABC):
    """Interface for splitting documents into processable chunks.

    Implementations handle different chunking strategies:
        - Fixed-size chunks with overlap
        - Semantic chunking (paragraph/section boundaries)
        - Token-based chunking (for LLM token limits)
        - Hybrid approaches

    The chunker preserves document structure and maintains metadata for
    reconstructing entity positions in the original document.

    Optional: implement chunk_from_raw() for memory-efficient chunking from
    raw bytes (e.g. PMC XML via iterparse) without loading the full document.
    """

    @abstractmethod
    async def chunk(self, document: BaseDocument) -> list[DocumentChunk]:
        """Split a document into chunks.

        Args:
            document: The document to split into chunks

        Returns:
            List of DocumentChunk objects in document order
        """

    async def chunk_from_raw(
        self,
        raw_content: bytes,
        content_type: str,
        document_id: str,
        source_uri: str | None = None,
    ) -> list[DocumentChunk]:
        """Chunk from raw bytes without parsing the full document (optional).

        Override this to support memory-efficient chunking (e.g. PMC XML
        via iterparse). Default implementation raises NotImplementedError.

        Args:
            raw_content: Raw byte content of the document.
            content_type: MIME type (e.g. "application/xml").
            document_id: Document ID to assign to produced chunks.
            source_uri: Optional source URI (e.g. file path).

        Returns:
            List of DocumentChunk objects in order.

        Raises:
            NotImplementedError: If this chunker does not support raw chunking.
        """
        raise NotImplementedError("This chunker does not support chunk_from_raw")


class WindowedDocumentChunker(DocumentChunkerInterface):
    """Chunks documents into overlapping fixed-size windows.

    This implementation uses a simple sliding window approach with configurable
    overlap. Optionally respects sentence boundaries to avoid breaking entities
    mid-sentence.

    Example:
        ```python
        chunker = WindowedDocumentChunker(
            config=ChunkingConfig(chunk_size=2000, overlap=200)
        )
        chunks = await chunker.chunk(document)
        ```
    """

    def __init__(self, config: ChunkingConfig | None = None):
        """Initialize the windowed chunker.

        Args:
            config: Chunking configuration. If None, uses default config.
        """
        self.config = config or ChunkingConfig()

    async def chunk(self, document: BaseDocument) -> list[DocumentChunk]:
        """Split document into overlapping fixed-size chunks.

        Args:
            document: The document to chunk

        Returns:
            List of DocumentChunk objects with overlapping windows
        """
        content = document.content
        doc_id = document.document_id
        chunks: list[DocumentChunk] = []

        if len(content) <= self.config.chunk_size:
            # Document fits in a single chunk
            return [
                DocumentChunk(
                    content=content,
                    start_offset=0,
                    end_offset=len(content),
                    chunk_index=0,
                    document_id=doc_id,
                    metadata={},
                )
            ]

        current_offset = 0
        chunk_index = 0

        while current_offset < len(content):
            # Calculate chunk boundaries
            chunk_end = min(current_offset + self.config.chunk_size, len(content))

            # If respecting boundaries and not at document end, try to break at sentence boundary
            if self.config.respect_boundaries and chunk_end < len(content):
                # Look for sentence-ending punctuation within the last 20% of the chunk
                search_start = chunk_end - int(self.config.chunk_size * 0.2)
                search_region = content[search_start:chunk_end]

                # Find last sentence boundary (., !, ?)
                for punct in [".", "!", "?"]:
                    last_idx = search_region.rfind(punct)
                    if last_idx != -1:
                        chunk_end = search_start + last_idx + 1
                        break

            chunk_content = content[current_offset:chunk_end]

            # Skip if chunk is too small (unless it's the last chunk)
            if len(chunk_content) >= self.config.min_chunk_size or chunk_end >= len(content):
                chunks.append(
                    DocumentChunk(
                        content=chunk_content,
                        start_offset=current_offset,
                        end_offset=chunk_end,
                        chunk_index=chunk_index,
                        document_id=doc_id,
                        metadata={},
                    )
                )
                chunk_index += 1

            # Move forward by chunk_size - overlap
            current_offset += self.config.chunk_size - self.config.overlap

            # Ensure we make progress even with large overlap
            if current_offset <= chunks[-1].start_offset if chunks else False:
                current_offset = chunks[-1].start_offset + 1

        return chunks


class StreamingEntityExtractorInterface(ABC):
    """Interface for extracting entities from document chunks in streaming fashion.

    Extends EntityExtractorInterface with streaming capabilities for processing
    large documents chunk by chunk. Implementations should:
        - Deduplicate entities found in overlapping chunks (by normalized key)
        - Adjust entity offsets to match the original document
        - Batch API calls for efficiency
        - Merge mentions with highest confidence when duplicates found

    This follows the pattern from plod branch's windowed entity extraction which
    deduplicates by (normalized_name, entity_type) and keeps the highest confidence
    mention when duplicates are found across windows.
    """

    @abstractmethod
    def extract_streaming(self, chunks: Sequence[DocumentChunk]) -> AsyncIterator[list[EntityMention]]:
        """Extract entities from document chunks, yielding results as they're processed.

        Note: This method is not async - it returns an AsyncIterator that can be
        iterated with `async for`. This is the correct pattern for async generators.

        Args:
            chunks: Sequence of document chunks to process

        Yields:
            Lists of EntityMention objects for each processed chunk
        """


def normalize_mention_key(name: str, entity_type: str) -> tuple[str, str]:
    """Normalize mention key for deduplication across windows.

    Removes non-alphanumeric characters, collapses whitespace, and lowercases
    for consistent matching. This ensures "Breast Cancer", "breast cancer",
    and "BREAST  CANCER" are all treated as the same entity.

    Based on _normalize_mention_key from plod branch medlit/pipeline/mentions.py.

    Args:
        name: Entity name/mention text
        entity_type: Entity type (e.g., "disease", "gene", "drug")

    Returns:
        Tuple of (normalized_name, entity_type) for use as dictionary key
    """
    # Keep only alphanumeric and spaces, then strip and collapse multiple spaces
    key_name = "".join(c for c in name.strip().casefold() if c.isalnum() or c.isspace())
    # Collapse multiple spaces into single space
    key_name = " ".join(key_name.split())
    # Fallback to original if normalization produces empty string
    if not key_name:
        key_name = name.strip().casefold()
    return (key_name, entity_type)


class BatchingEntityExtractor(StreamingEntityExtractorInterface):
    """Wraps an EntityExtractorInterface to provide streaming extraction with batching.

    This adapter enables any EntityExtractorInterface implementation to work with
    document chunks. It handles:
        - Converting chunks back to temporary BaseDocument objects
        - Batching extraction calls for efficiency
        - Adjusting entity mention offsets to match original document positions
        - Deduplicating mentions across overlapping windows (keeping highest confidence)

    The deduplication approach follows the plod branch pattern: normalize entity names
    to alphanumeric lowercase, then keep the highest confidence mention when duplicates
    are found across windows.

    Example:
        ```python
        base_extractor = MyEntityExtractor()
        streaming_extractor = BatchingEntityExtractor(
            base_extractor=base_extractor,
            batch_size=10,
            deduplicate=True
        )

        async for mentions in streaming_extractor.extract_streaming(chunks):
            # Process mentions as they arrive
            await process_mentions(mentions)
        ```
    """

    def __init__(self, base_extractor: EntityExtractorInterface, batch_size: int = 5, deduplicate: bool = True):
        """Initialize the batching extractor.

        Args:
            base_extractor: The underlying extractor to use for each chunk
            batch_size: Number of chunks to process in parallel (not yet implemented)
            deduplicate: Whether to deduplicate mentions across windows
        """
        self.base_extractor = base_extractor
        self.batch_size = batch_size
        self.deduplicate = deduplicate
        self._seen_mentions: dict[tuple[str, str], EntityMention] = {}

    async def extract_streaming(self, chunks: Sequence[DocumentChunk]) -> AsyncIterator[list[EntityMention]]:  # pylint: disable=invalid-overridden-method
        """Extract entities from chunks, yielding results incrementally.

        When deduplicate=True, tracks mentions across windows and yields only
        unique mentions (by normalized name+type), keeping the highest confidence
        version of each entity.

        Note: This is an async generator method. Pylint incorrectly flags async
        generators that override methods returning AsyncIterator. The pattern is
        correct: ABCs declare non-async methods returning AsyncIterator, while
        implementations use async def to create the async generator.

        Args:
            chunks: Sequence of document chunks to process

        Yields:
            Lists of EntityMention objects for each chunk (deduplicated if enabled)
        """
        from kgschema.document import BaseDocument
        from datetime import datetime, timezone

        # Simple temporary document class for chunk processing
        class ChunkDocument(BaseDocument):
            def get_document_type(self) -> str:
                return "chunk"

            def get_sections(self) -> list[tuple[str, str]]:
                return [("body", self.content)]

        for chunk in chunks:
            # Convert chunk to temporary document
            chunk_doc = ChunkDocument(
                document_id=f"{chunk.document_id}_chunk_{chunk.chunk_index}",
                content=chunk.content,
                content_type="text/plain",
                created_at=datetime.now(timezone.utc),
                metadata={},
            )

            # Extract entities from this chunk
            mentions = await self.base_extractor.extract(chunk_doc)

            # Adjust mention offsets to match original document
            adjusted_mentions = []
            for mention in mentions:
                adjusted_mention = EntityMention(
                    text=mention.text,
                    entity_type=mention.entity_type,
                    start_offset=mention.start_offset + chunk.start_offset,
                    end_offset=mention.end_offset + chunk.start_offset,
                    confidence=mention.confidence,
                    context=mention.context,
                    metadata=mention.metadata,
                )

                if self.deduplicate:
                    # Deduplicate by normalized (name, type) key
                    key = normalize_mention_key(mention.text, mention.entity_type)

                    # Keep highest confidence version
                    if key not in self._seen_mentions or self._seen_mentions[key].confidence < adjusted_mention.confidence:
                        self._seen_mentions[key] = adjusted_mention

                    # Only yield if this is new or updated
                    adjusted_mentions.append(adjusted_mention)
                else:
                    adjusted_mentions.append(adjusted_mention)

            yield adjusted_mentions

    def get_unique_mentions(self) -> list[EntityMention]:
        """Get all unique mentions after deduplication.

        Only meaningful when deduplicate=True. Returns the highest confidence
        version of each unique entity across all processed windows.

        Returns:
            List of unique EntityMention objects
        """
        return list(self._seen_mentions.values())


class StreamingRelationshipExtractorInterface(ABC):
    """Interface for extracting relationships from document chunks in streaming fashion.

    Extends RelationshipExtractorInterface with windowed processing. This is useful for:
        - Large documents that exceed LLM context windows
        - Processing relationships as entities are discovered
        - Limiting relationship extraction to relevant windows (entities nearby)

    Implementations should consider:
        - Only extracting relationships between entities within the same window
        - Using overlapping windows to catch cross-boundary relationships
        - Deduplicating relationships found in multiple overlapping windows
    """

    @abstractmethod
    def extract_windowed(
        self,
        chunks: Sequence[DocumentChunk],
        entities: Sequence[BaseEntity],
        window_size: int = 2000,
    ) -> AsyncIterator[list[BaseRelationship]]:
        """Extract relationships from windowed chunks.

        Note: This method is not async - it returns an AsyncIterator that can be
        iterated with `async for`. This is the correct pattern for async generators.

        Args:
            chunks: Document chunks to process
            entities: All entities found in the document (with position info)
            window_size: Size of context window for relationship extraction

        Yields:
            Lists of BaseRelationship objects found in each window
        """


class WindowedRelationshipExtractor(StreamingRelationshipExtractorInterface):
    """Extracts relationships using sliding windows over document chunks.

    This implementation wraps a standard RelationshipExtractorInterface and applies
    it to overlapping windows of the document. Only entities that appear within
    the same window are considered for relationship extraction.

    This approach is particularly useful for:
        - LLM-based extractors with limited context windows
        - Reducing false positives by focusing on nearby entities
        - Improving performance by limiting entity combinations

    Example:
        ```python
        base_extractor = MyRelationshipExtractor()
        windowed_extractor = WindowedRelationshipExtractor(
            base_extractor=base_extractor,
            window_size=2000
        )

        async for relationships in windowed_extractor.extract_windowed(
            chunks, entities, window_size=2000
        ):
            await store_relationships(relationships)
        ```
    """

    def __init__(self, base_extractor: RelationshipExtractorInterface):
        """Initialize the windowed relationship extractor.

        Args:
            base_extractor: The underlying relationship extractor
        """
        self.base_extractor = base_extractor

    async def extract_windowed(  # pylint: disable=invalid-overridden-method
        self,
        chunks: Sequence[DocumentChunk],
        entities: Sequence[BaseEntity],
        window_size: int = 2000,
    ) -> AsyncIterator[list[BaseRelationship]]:
        """Extract relationships within overlapping windows.

        Note: This is an async generator method. Pylint incorrectly flags async
        generators that override methods returning AsyncIterator. See extract_streaming
        comment for details on this pattern.

        Args:
            chunks: Document chunks to process
            entities: All entities found in the document
            window_size: Size of context window for relationship extraction

        Yields:
            Lists of BaseRelationship objects found in each window
        """
        from kgschema.document import BaseDocument
        from datetime import datetime, timezone

        # Simple temporary document class for window processing
        class WindowDocument(BaseDocument):
            def get_document_type(self) -> str:
                return "window"

            def get_sections(self) -> list[tuple[str, str]]:
                return [("body", self.content)]

        # Track seen relationships to deduplicate across windows
        seen_relationships: set[tuple[str, str, str]] = set()

        doc_hint = chunks[0].document_id if chunks else "unknown"
        logger.info(
            "Relationship extraction: %d chunks, %d entities (document hint: %s)",
            len(chunks),
            len(entities),
            doc_hint,
        )

        for window_num, chunk in enumerate(chunks, start=1):
            # Find entities that appear in this chunk
            # Note: This assumes entities have position information
            # In practice, you'd need to match entity mentions to chunk boundaries
            chunk_entities = []
            for entity in entities:
                # Simple heuristic: check if entity name appears in chunk
                # Real implementation would use actual position data from mentions
                if entity.name.lower() in chunk.content.lower():
                    chunk_entities.append(entity)

            window_id = f"{chunk.document_id}_window_{chunk.chunk_index}"
            logger.debug(
                "Chunk %s (index %s): %d entities in window",
                chunk.document_id,
                chunk.chunk_index,
                len(chunk_entities),
            )

            if len(chunk_entities) < 2:
                # Need at least 2 entities for a relationship; write skip trace when supported
                if hasattr(self.base_extractor, "write_skip_trace"):
                    self.base_extractor.write_skip_trace(
                        window_id,
                        reason="fewer_than_2_entities",
                        entity_count=len(chunk_entities),
                    )
                logger.debug(
                    "Skipping window %s: fewer than 2 entities (%d)",
                    window_id,
                    len(chunk_entities),
                )
                continue

            logger.info(
                "Relationship window %d/%d: %s (%d entities)",
                window_num,
                len(chunks),
                window_id,
                len(chunk_entities),
            )
            logger.debug("Running relationship LLM for window %s (%d entities)", window_id, len(chunk_entities))

            # Create temporary document for this window
            window_doc = WindowDocument(
                document_id=window_id,
                content=chunk.content,
                content_type="text/plain",
                created_at=datetime.now(timezone.utc),
                metadata={},
            )

            # Extract relationships for this window
            relationships = await self.base_extractor.extract(window_doc, chunk_entities)

            # Deduplicate and yield
            new_relationships = []
            for rel in relationships:
                # Create a unique key for deduplication
                rel_key = (rel.subject_id, rel.predicate, rel.object_id)
                if rel_key not in seen_relationships:
                    seen_relationships.add(rel_key)
                    new_relationships.append(rel)

            if new_relationships:
                yield new_relationships

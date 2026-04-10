"""PMC-specific document chunker using iter_pmc_windows for memory-efficient streaming.

Produces DocumentChunks from raw PMC/JATS XML bytes without loading the full
document into memory. Implements DocumentChunkerInterface with chunk_from_raw()
for the streaming path and chunk(document) as a fallback for parsed documents.
"""

from __future__ import annotations

from pathlib import Path

from kgschema.document import BaseDocument

from kgraph.pipeline.streaming import (
    ChunkingConfig,
    DocumentChunk,
    DocumentChunkerInterface,
    WindowedDocumentChunker,
)

from .pmc_streaming import (
    DEFAULT_OVERLAP,
    DEFAULT_WINDOW_SIZE,
    iter_pmc_windows,
)


def _content_type_is_xml(content_type: str) -> bool:
    """Return True if content_type is XML (strip parameters like ; charset=utf-8)."""
    base = (content_type or "").split(";")[0].strip().lower()
    return base in ("application/xml", "text/xml")


class PMCStreamingChunker(DocumentChunkerInterface):
    """Chunker for PMC/JATS XML that uses iter_pmc_windows for memory-efficient chunking.

    When chunk_from_raw() is used with XML content type, yields overlapping
    windows from raw bytes without parsing the full document. For chunk(document)
    (e.g. already-parsed document or non-XML), delegates to a windowed chunker
    over document.content.
    """

    def __init__(
        self,
        window_size: int = DEFAULT_WINDOW_SIZE,
        overlap: int = DEFAULT_OVERLAP,
        include_abstract_separately: bool = True,
        document_chunk_config: ChunkingConfig | None = None,
    ):
        """Initialize the PMC streaming chunker.

        Args:
            window_size: Target characters per window (used for chunk_from_raw).
            overlap: Overlap between consecutive windows.
            include_abstract_separately: If True, first window is abstract alone.
            document_chunk_config: Config for chunk(document) fallback. If None,
                uses window_size and overlap for the windowed chunker.
        """
        self._window_size = window_size
        self._overlap = overlap
        self._include_abstract_separately = include_abstract_separately
        config = document_chunk_config or ChunkingConfig(
            chunk_size=window_size,
            overlap=overlap,
            respect_boundaries=True,
            min_chunk_size=500,
        )
        self._document_chunker = WindowedDocumentChunker(config=config)

    async def chunk(self, document: BaseDocument) -> list[DocumentChunk]:
        """Split a parsed document into chunks (fallback when no raw bytes).

        Delegates to WindowedDocumentChunker over document.content.
        """
        return await self._document_chunker.chunk(document)

    async def chunk_from_raw(
        self,
        raw_content: bytes,
        content_type: str,
        document_id: str,
        source_uri: str | None = None,
    ) -> list[DocumentChunk]:
        """Chunk from raw PMC XML bytes without loading the full document.

        Uses iter_pmc_windows for memory-efficient streaming. If content_type
        is not XML, returns a single chunk with decoded text (for non-PMC use).
        """
        if not _content_type_is_xml(content_type):
            text = raw_content.decode("utf-8", errors="replace")
            return [
                DocumentChunk(
                    content=text,
                    start_offset=0,
                    end_offset=len(text),
                    chunk_index=0,
                    document_id=document_id,
                    metadata={},
                )
            ]

        step = max(1, self._window_size - self._overlap)
        chunks: list[DocumentChunk] = []
        for window_index, text in iter_pmc_windows(
            raw_content,
            window_size=self._window_size,
            overlap=self._overlap,
            include_abstract_separately=self._include_abstract_separately,
        ):
            start_offset = window_index * step
            end_offset = start_offset + len(text)
            metadata: dict[str, str] = {"window_index": str(window_index)}
            if window_index == 0 and self._include_abstract_separately:
                metadata["section"] = "abstract"
            chunks.append(
                DocumentChunk(
                    content=text,
                    start_offset=start_offset,
                    end_offset=end_offset,
                    chunk_index=window_index,
                    document_id=document_id,
                    metadata=metadata,
                )
            )
        return chunks


def document_id_from_source_uri(source_uri: str | None) -> str:
    """Derive a document ID from source_uri (e.g. file stem). Used when parsing is deferred."""
    if source_uri:
        return Path(source_uri).stem
    return ""

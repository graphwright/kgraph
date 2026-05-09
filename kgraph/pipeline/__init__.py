"""Public exports for extraction pipeline building blocks.

This package-level module re-exports the core interfaces and commonly used
implementations needed to assemble ingestion/extraction flows:

- Base parser/extractor/resolver interfaces from ``kgraph.pipeline.interfaces``
- Embedding interfaces and cache adapters used by resolution/promotions
- Streaming chunking/extraction utilities for large-document processing

Import from ``kgraph.pipeline`` when composing pipelines so downstream code can
depend on a stable, centralized surface area instead of deep module paths.
"""

from kgraph.pipeline.caching import (
    CachedEmbeddingGenerator,
    EmbeddingCacheConfig,
    EmbeddingsCacheInterface,
    FileBasedEmbeddingsCache,
    InMemoryEmbeddingsCache,
)
from kgraph.pipeline.embedding import EmbeddingGeneratorInterface
from kgraph.pipeline.interfaces import (
    DocumentParserInterface,
    EntityExtractorInterface,
    EntityResolverInterface,
    RelationshipExtractorInterface,
)
from kgraph.pipeline.streaming import (
    BatchingEntityExtractor,
    ChunkingConfig,
    DocumentChunk,
    DocumentChunkerInterface,
    StreamingEntityExtractorInterface,
    StreamingRelationshipExtractorInterface,
    WindowedDocumentChunker,
    WindowedRelationshipExtractor,
)

__all__ = [
    # Core interfaces
    "DocumentParserInterface",
    "EntityExtractorInterface",
    "EntityResolverInterface",
    "RelationshipExtractorInterface",
    "EmbeddingGeneratorInterface",
    # Streaming interfaces and implementations
    "DocumentChunkerInterface",
    "StreamingEntityExtractorInterface",
    "StreamingRelationshipExtractorInterface",
    "DocumentChunk",
    "ChunkingConfig",
    "WindowedDocumentChunker",
    "BatchingEntityExtractor",
    "WindowedRelationshipExtractor",
    # Caching interfaces and implementations
    "EmbeddingsCacheInterface",
    "EmbeddingCacheConfig",
    "InMemoryEmbeddingsCache",
    "FileBasedEmbeddingsCache",
    "CachedEmbeddingGenerator",
]

"""Caching primitives for extraction-time embedding reuse.

Uses asyncio.Lock in concrete caches so that concurrent get/put/save/load
do not corrupt in-memory state. Lock is held only around critical sections
to avoid deadlock (e.g. get_batch calling get, put calling save).

This module provides abstractions for caching expensive computations, especially
embedding vectors generated during entity extraction and resolution. Caching is
critical for:

- **Cost reduction**: Avoiding repeated API calls to embedding providers
- **Performance**: Eliminating redundant computation for frequently-seen entities
- **Consistency**: Ensuring the same text always produces the same embedding
- **Offline operation**: Working with pre-computed embeddings without API access

Key abstractions:
    - EmbeddingsCacheInterface: Generic cache for text→embedding mappings
    - InMemoryEmbeddingsCache: Fast in-memory LRU cache
    - FileBasedEmbeddingsCache: Persistent JSON-based cache

Typical usage:
    ```python
    # Create cache with persistence
    cache = FileBasedEmbeddingsCache(cache_file="embeddings.json")
    await cache.load()

    # Wrap embedding generator with caching
    generator = CachedEmbeddingGenerator(
        base_generator=ollama_embedder,
        cache=cache
    )

    # Subsequent calls with same text use cached embeddings
    emb1 = await generator.generate("aspirin")  # API call
    emb2 = await generator.generate("aspirin")  # Cached, no API call
    ```
"""

import asyncio
import json
import logging
import os
from abc import ABC, abstractmethod
from collections import OrderedDict
from pathlib import Path
from typing import Optional, Sequence

from pydantic import BaseModel, Field

from .embedding import EmbeddingGeneratorInterface


class EmbeddingCacheConfig(BaseModel):
    """Configuration for embedding caching strategies.

    Attributes:
        max_cache_size: Maximum number of embeddings to store in memory (for LRU eviction)
        cache_file: Path to persistent cache file (for file-based caches)
        auto_save_interval: Number of cache updates before auto-saving (0 = manual save only)
        normalize_keys: Whether to normalize cache keys (lowercase, strip whitespace)
        normalize_collapse_whitespace: When True, collapse internal whitespace to one space (optional).
    """

    model_config = {"frozen": True}

    max_cache_size: int = Field(10000, gt=0, description="Maximum number of embeddings in memory cache")
    cache_file: Path | None = Field(None, description="Path to persistent cache file")
    auto_save_interval: int = Field(100, ge=0, description="Auto-save every N updates (0 = manual only)")
    normalize_keys: bool = Field(True, description="Normalize cache keys for consistent lookups")
    normalize_collapse_whitespace: bool = Field(False, description="Collapse internal whitespace to single space when normalizing keys")


class EmbeddingsCacheInterface(ABC):
    """Abstract interface for caching text embeddings.

    Implementations provide different storage backends (memory, disk, database)
    with consistent semantics. All implementations should:
        - Be thread-safe for concurrent access
        - Support batch operations for efficiency
        - Provide cache statistics (hits, misses, size)
        - Handle cache invalidation gracefully

    Cache keys are text strings; values are embedding vectors (tuples of floats).
    """

    @abstractmethod
    async def get(self, text: str) -> Optional[tuple[float, ...]]:
        """Retrieve a cached embedding for the given text.

        Args:
            text: The text to look up

        Returns:
            Embedding vector if found in cache, None otherwise
        """

    @abstractmethod
    async def get_batch(self, texts: Sequence[str]) -> list[Optional[tuple[float, ...]]]:
        """Retrieve multiple cached embeddings.

        Args:
            texts: Sequence of texts to look up

        Returns:
            List of embeddings (or None for cache misses) in same order as texts
        """

    @abstractmethod
    async def put(self, text: str, embedding: tuple[float, ...]) -> None:
        """Store an embedding in the cache.

        Args:
            text: The text this embedding represents
            embedding: The embedding vector to store
        """

    @abstractmethod
    async def put_batch(self, texts: Sequence[str], embeddings: Sequence[tuple[float, ...]]) -> None:
        """Store multiple embeddings efficiently.

        Args:
            texts: Sequence of texts
            embeddings: Sequence of embedding vectors (same order as texts)
        """

    @abstractmethod
    async def clear(self) -> None:
        """Clear all cached embeddings and reset statistics.

        Implementations should reset hit/miss counters in addition to clearing
        the cache contents to provide a clean slate for fresh cache usage tracking.
        """

    @abstractmethod
    def get_stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with metrics like:
                - "hits": Number of successful cache lookups
                - "misses": Number of cache misses
                - "size": Current number of cached embeddings
                - "evictions": Number of items evicted (for LRU caches)
        """

    @abstractmethod
    async def save(self) -> None:
        """Persist cache to storage (for persistent implementations).

        No-op for in-memory-only caches.
        """

    @abstractmethod
    async def load(self) -> None:
        """Load cache from storage (for persistent implementations).

        No-op for in-memory-only caches.
        """

    def _normalize_key(self, text: str) -> str:
        """Normalize cache key for consistent lookups.

        Args:
            text: The text to normalize

        Returns:
            Normalized text (lowercase, stripped whitespace)
        """
        return text.lower().strip()


class InMemoryEmbeddingsCache(EmbeddingsCacheInterface):
    """In-memory LRU cache for embeddings.

    Uses an OrderedDict to maintain LRU semantics with O(1) lookups and updates.
    When the cache exceeds max_cache_size, the least recently used items are evicted.

    This implementation is fast but non-persistent. Suitable for:
        - Short-lived processes
        - Testing
        - Hot cache layer in front of persistent storage

    Example:
        ```python
        cache = InMemoryEmbeddingsCache(
            config=EmbeddingCacheConfig(max_cache_size=5000)
        )

        await cache.put("aspirin", embedding_vector)
        result = await cache.get("aspirin")  # Fast O(1) lookup
        ```
    """

    def __init__(self, config: EmbeddingCacheConfig | None = None):
        """Initialize the in-memory cache.

        Args:
            config: Cache configuration. If None, uses default config.
        """
        self.config = config or EmbeddingCacheConfig()
        self._cache: OrderedDict[str, tuple[float, ...]] = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._lock = asyncio.Lock()

    def _normalize_key(self, text: str) -> str:
        """Normalize cache key; optionally collapse internal whitespace."""
        base = text.lower().strip()
        if getattr(self.config, "normalize_collapse_whitespace", False):
            return " ".join(base.split())
        return base

    async def get(self, text: str) -> Optional[tuple[float, ...]]:
        """Retrieve embedding from memory cache.

        Args:
            text: The text to look up

        Returns:
            Embedding vector if found, None otherwise
        """
        key = self._normalize_key(text) if self.config.normalize_keys else text
        async with self._lock:
            if key in self._cache:
                self._hits += 1
                self._cache.move_to_end(key)
                result: Optional[tuple[float, ...]] = self._cache[key]
            else:
                self._misses += 1
                result = None
        if os.environ.get("KG_EMBED_CACHE_DEBUG"):
            log = logging.getLogger(__name__)
            if result is not None:
                log.info("CACHE HIT %s", (key[:40] + "..") if len(key) > 40 else key)
            else:
                log.info("CACHE MISS %s", (key[:40] + "..") if len(key) > 40 else key)
        return result

    async def get_batch(self, texts: Sequence[str]) -> list[Optional[tuple[float, ...]]]:
        """Retrieve multiple embeddings from cache.

        Args:
            texts: Sequence of texts to look up

        Returns:
            List of embeddings (or None for misses) in same order
        """
        results = []
        for text in texts:
            results.append(await self.get(text))
        return results

    async def put(self, text: str, embedding: tuple[float, ...]) -> None:
        """Store embedding in memory cache.

        Args:
            text: The text this embedding represents
            embedding: The embedding vector to store
        """
        key = self._normalize_key(text) if self.config.normalize_keys else text
        async with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = embedding
            while len(self._cache) > self.config.max_cache_size:
                self._cache.popitem(last=False)
                self._evictions += 1

    async def put_batch(self, texts: Sequence[str], embeddings: Sequence[tuple[float, ...]]) -> None:
        """Store multiple embeddings efficiently.

        Args:
            texts: Sequence of texts
            embeddings: Sequence of embedding vectors (same order)
        """
        async with self._lock:
            for text, embedding in zip(texts, embeddings):
                key = self._normalize_key(text) if self.config.normalize_keys else text
                if key in self._cache:
                    self._cache.move_to_end(key)
                self._cache[key] = embedding
                while len(self._cache) > self.config.max_cache_size:
                    self._cache.popitem(last=False)
                    self._evictions += 1

    async def clear(self) -> None:
        """Clear all cached embeddings and reset statistics.

        Note: This method resets hit/miss/eviction counters in addition to
        clearing the cache contents. Use get_stats() before calling clear()
        if you need to preserve statistics.
        """
        async with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0

    def get_stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with hits, misses, size, and evictions
        """
        return {
            "hits": self._hits,
            "misses": self._misses,
            "size": len(self._cache),
            "evictions": self._evictions,
        }

    async def save(self) -> None:
        """No-op for in-memory cache (non-persistent)."""
        pass

    async def load(self) -> None:
        """No-op for in-memory cache (non-persistent)."""
        pass


class FileBasedEmbeddingsCache(EmbeddingsCacheInterface):
    """Persistent file-based embeddings cache using JSON.

    Stores embeddings in a JSON file with optional in-memory LRU cache for
    hot data. The file format is:
        ```json
        {
            "aspirin": [0.1, 0.2, ..., 0.9],
            "ibuprofen": [0.3, 0.4, ..., 0.8],
            ...
        }
        ```

    Features:
        - Persistent storage survives process restarts
        - Optional auto-save on every N updates
        - In-memory LRU cache for hot data
        - Atomic writes to prevent corruption

    Example:
        ```python
        cache = FileBasedEmbeddingsCache(
            config=EmbeddingCacheConfig(
                cache_file=Path("embeddings.json"),
                max_cache_size=5000,
                auto_save_interval=100
            )
        )

        await cache.load()  # Load existing cache
        await cache.put("aspirin", embedding)
        # Auto-saves every 100 updates
        ```
    """

    def __init__(self, config: EmbeddingCacheConfig):
        """Initialize the file-based cache.

        Args:
            config: Cache configuration including cache_file path

        Raises:
            ValueError: If config.cache_file is None
        """
        if config.cache_file is None:
            raise ValueError("cache_file must be specified for FileBasedEmbeddingsCache")

        self.config = config
        self._cache: OrderedDict[str, tuple[float, ...]] = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._updates_since_save = 0
        self._dirty = False
        self._lock = asyncio.Lock()

    def _normalize_key(self, text: str) -> str:
        """Normalize cache key; optionally collapse internal whitespace."""
        base = text.lower().strip()
        if getattr(self.config, "normalize_collapse_whitespace", False):
            return " ".join(base.split())
        return base

    async def get(self, text: str) -> Optional[tuple[float, ...]]:
        """Retrieve embedding from cache.

        Args:
            text: The text to look up

        Returns:
            Embedding vector if found, None otherwise
        """
        key = self._normalize_key(text) if self.config.normalize_keys else text
        async with self._lock:
            if key in self._cache:
                self._hits += 1
                self._cache.move_to_end(key)
                result: Optional[tuple[float, ...]] = self._cache[key]
            else:
                self._misses += 1
                result = None
        if os.environ.get("KG_EMBED_CACHE_DEBUG"):
            log = logging.getLogger(__name__)
            if result is not None:
                log.info("CACHE HIT %s", (key[:40] + "..") if len(key) > 40 else key)
            else:
                log.info("CACHE MISS %s", (key[:40] + "..") if len(key) > 40 else key)
        return result

    async def get_batch(self, texts: Sequence[str]) -> list[Optional[tuple[float, ...]]]:
        """Retrieve multiple embeddings from cache.

        Args:
            texts: Sequence of texts to look up

        Returns:
            List of embeddings (or None for misses) in same order
        """
        results = []
        for text in texts:
            results.append(await self.get(text))
        return results

    async def put(self, text: str, embedding: tuple[float, ...]) -> None:
        """Store embedding in cache.

        Args:
            text: The text this embedding represents
            embedding: The embedding vector to store
        """
        key = self._normalize_key(text) if self.config.normalize_keys else text
        async with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = embedding
            self._dirty = True
            while len(self._cache) > self.config.max_cache_size:
                self._cache.popitem(last=False)
                self._evictions += 1
            self._updates_since_save += 1
            do_save = self.config.auto_save_interval > 0 and self._updates_since_save >= self.config.auto_save_interval
            if do_save:
                self._updates_since_save = 0
        if do_save:
            await self.save()

    async def put_batch(self, texts: Sequence[str], embeddings: Sequence[tuple[float, ...]]) -> None:
        """Store multiple embeddings efficiently.

        Args:
            texts: Sequence of texts
            embeddings: Sequence of embedding vectors (same order)
        """
        do_save = False
        async with self._lock:
            for text, embedding in zip(texts, embeddings):
                key = self._normalize_key(text) if self.config.normalize_keys else text
                if key in self._cache:
                    self._cache.move_to_end(key)
                self._cache[key] = embedding
                self._dirty = True
                while len(self._cache) > self.config.max_cache_size:
                    self._cache.popitem(last=False)
                    self._evictions += 1
            self._updates_since_save += len(texts)
            if self.config.auto_save_interval > 0 and self._updates_since_save >= self.config.auto_save_interval:
                self._updates_since_save = 0
                do_save = True
        if do_save:
            await self.save()

    async def clear(self) -> None:
        """Clear all cached embeddings and reset statistics.

        Note: This method resets hit/miss/eviction counters in addition to
        clearing the cache contents. Use get_stats() before calling clear()
        if you need to preserve statistics.
        """
        async with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0
            self._updates_since_save = 0
            self._dirty = True

    def get_stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with hits, misses, size, and evictions
        """
        return {
            "hits": self._hits,
            "misses": self._misses,
            "size": len(self._cache),
            "evictions": self._evictions,
        }

    async def save(self) -> None:
        """Persist cache to JSON file.

        Uses atomic write (write to temp file, then rename) to prevent corruption.
        """
        async with self._lock:
            if not self._dirty:
                return
            if self.config.cache_file is None:
                return
            data = {key: list(value) for key, value in self._cache.items()}
            self._dirty = False
        # I/O outside lock
        temp_file = self.config.cache_file.with_suffix(".tmp")
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=2)
        temp_file.replace(self.config.cache_file)

    async def load(self) -> None:
        """Load cache from JSON file.

        If file doesn't exist, starts with empty cache.
        Keys are normalized on load when normalize_keys is True so lookups match.
        """
        if self.config.cache_file is None or not self.config.cache_file.exists():
            return
        with open(self.config.cache_file, "r") as f:
            data = json.load(f)
        # Normalize keys on load so in-memory keys match get()/put() convention
        async with self._lock:
            self._cache = OrderedDict((self._normalize_key(k) if self.config.normalize_keys else k, tuple(v)) for k, v in data.items())
            self._dirty = False


class CachedEmbeddingGenerator(EmbeddingGeneratorInterface):
    """Wraps an embedding generator with transparent caching.

    This adapter provides a cache layer in front of any EmbeddingGeneratorInterface
    implementation. Cache hits avoid API calls entirely, providing:
        - Significant cost savings for frequently-seen texts
        - Faster response times
        - Consistent embeddings (no variation from API)
        - Offline operation for cached texts

    The cache is transparent to callers - the interface is identical to the
    underlying generator.

    Example:
        ```python
        # Wrap any embedding generator with caching
        cache = FileBasedEmbeddingsCache(
            config=EmbeddingCacheConfig(cache_file=Path("cache.json"))
        )
        await cache.load()

        cached_gen = CachedEmbeddingGenerator(
            base_generator=ollama_embedder,
            cache=cache
        )

        # First call hits API and caches result
        emb1 = await cached_gen.generate("aspirin")

        # Second call uses cached result
        emb2 = await cached_gen.generate("aspirin")  # No API call!
        ```
    """

    def __init__(self, base_generator: EmbeddingGeneratorInterface, cache: EmbeddingsCacheInterface):
        """Initialize the cached generator.

        Args:
            base_generator: The underlying embedding generator
            cache: The cache to use for storing/retrieving embeddings
        """
        self.base_generator = base_generator
        self.cache = cache

    @property
    def dimension(self) -> int:
        """Return embedding dimension from base generator.

        Returns:
            Embedding dimension (e.g., 1536, 1024)
        """
        return self.base_generator.dimension

    async def generate(self, text: str) -> tuple[float, ...]:
        """Generate embedding with caching.

        Checks cache first. If miss, generates embedding and caches it.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        # Check cache first
        cached = await self.cache.get(text)
        if cached is not None:
            return cached

        # Cache miss - generate and store
        embedding = await self.base_generator.generate(text)
        await self.cache.put(text, embedding)
        return embedding

    async def generate_batch(self, texts: Sequence[str]) -> list[tuple[float, ...]]:
        """Generate embeddings in batch with caching.

        Checks cache for all texts first, then only generates embeddings
        for cache misses. This minimizes API calls.

        Args:
            texts: Sequence of texts to embed

        Returns:
            List of embedding vectors in same order as texts
        """
        # Check cache for all texts
        cached_results = await self.cache.get_batch(texts)

        # Identify cache misses
        misses_indices = [i for i, result in enumerate(cached_results) if result is None]

        if not misses_indices:
            # All hits - return cached results (filter out None values that shouldn't exist)
            return [r for r in cached_results if r is not None]

        # Generate embeddings for misses
        miss_texts = [texts[i] for i in misses_indices]
        new_embeddings = await self.base_generator.generate_batch(miss_texts)

        # Store new embeddings in cache
        await self.cache.put_batch(miss_texts, new_embeddings)

        # Merge cached and new results
        results: list[tuple[float, ...]] = []
        for idx, cached_result in enumerate(cached_results):
            if cached_result is not None:
                results.append(cached_result)
            else:
                # This is a miss - find it in misses_indices and get corresponding new embedding
                miss_position = misses_indices.index(idx)
                results.append(new_embeddings[miss_position])

        return results

    async def save_cache(self) -> None:
        """Persist cache to storage.

        Convenience method for explicit cache persistence.
        """
        await self.cache.save()

    def get_cache_stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with cache metrics
        """
        return self.cache.get_stats()

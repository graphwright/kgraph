"""JSON file-based implementation of CanonicalIdCacheInterface.

This implementation stores canonical ID lookups in a JSON file, with support for
backward compatibility with the old cache format (dict[str, str]).
"""

import json
import os
from pathlib import Path
from typing import Optional

from kgraph.pprint_logging import setup_logging

from .models import CanonicalId, CanonicalIdCacheInterface


class JsonFileCanonicalIdCache(CanonicalIdCacheInterface):
    """JSON file-based implementation of CanonicalIdCacheInterface.

    Stores canonical ID lookups in a JSON file. The cache format is:
    {
        "cache_key": {
            "id": "UMLS:C12345",
            "url": "https://...",
            "synonyms": ["term1", "term2"]
        },
        ...
    }

    Known bad entries are stored with `"id": null` to distinguish them from
    successful lookups.

    Attributes:
        cache_file: Path to the JSON cache file
        _cache: In-memory cache dictionary mapping cache keys to CanonicalId objects
        _known_bad: Set of cache keys marked as "known bad"
        _cache_dirty: Whether the cache has been modified since last save
        _hits: Number of cache hits
        _misses: Number of cache misses
    """

    def __init__(self, cache_file: Optional[Path] = None):
        """Initialize the JSON file-based cache.

        Args:
            cache_file: Path to the JSON cache file. If None, defaults to
                       "canonical_id_cache.json" in the current directory.
        """
        self.cache_file = cache_file or Path("canonical_id_cache.json")
        self._cache: dict[str, CanonicalId] = {}
        self._known_bad: set[str] = set()
        self._cache_dirty = False
        self._hits = 0
        self._misses = 0
        self.logger = setup_logging()

    def load(self, tag: str) -> None:
        """Load cache from JSON file.

        Args:
            tag: Path to the cache file (overrides self.cache_file if provided).
                 If tag is a relative path, it's used as-is.
                 If tag is an absolute path, it overrides self.cache_file.
        """
        # If tag looks like a path, use it; otherwise use self.cache_file
        cache_path = Path(tag) if tag and Path(tag).is_absolute() else self.cache_file
        if tag and not Path(tag).is_absolute() and tag != str(self.cache_file):
            # Relative path provided as tag - use it
            cache_path = Path(tag)

        if not cache_path.exists():
            self.logger.debug(
                {
                    "message": f"Cache file does not exist: {cache_path}",
                    "cache_file": str(cache_path),
                },
                pprint=True,
            )
            return

        try:
            with open(cache_path, "r") as f:
                data = json.load(f)

            # Handle backward compatibility: old format was dict[str, str]
            # where values were either canonical ID strings or "NULL"
            if data and isinstance(next(iter(data.values())), str):
                self.logger.info(
                    {
                        "message": "Migrating old cache format to new format",
                        "cache_file": str(cache_path),
                        "entries": len(data),
                    },
                    pprint=True,
                )
                self._migrate_old_format(data)
            else:
                # New format: dict[str, dict] with CanonicalId data
                for cache_key, entry in data.items():
                    if entry is None or entry.get("id") is None:
                        # Known bad entry
                        self._known_bad.add(cache_key)
                    else:
                        # Successful lookup
                        canonical_id = CanonicalId(
                            id=entry.get("id", ""),
                            url=entry.get("url"),
                            synonyms=tuple(entry.get("synonyms", [])),
                        )
                        self._cache[cache_key] = canonical_id

            self.logger.debug(
                {
                    "message": f"Loaded {len(self._cache)} cached lookups from {cache_path}",
                    "cache_file": str(cache_path),
                    "cache_size": len(self._cache),
                    "known_bad_count": len(self._known_bad),
                },
                pprint=True,
            )
        except Exception as e:
            self.logger.warning(
                {
                    "message": f"Failed to load cache from {cache_path}",
                    "cache_file": str(cache_path),
                    "error": str(e),
                },
                pprint=True,
            )
            self._cache = {}
            self._known_bad = set()

    def _migrate_old_format(self, old_data: dict[str, str]) -> None:
        """Migrate old cache format (dict[str, str]) to new format.

        Args:
            old_data: Old cache data where values are either canonical ID strings or "NULL"
        """
        for cache_key, value in old_data.items():
            if value == "NULL":
                # Known bad entry
                self._known_bad.add(cache_key)
            else:
                # Successful lookup - create CanonicalId with just the ID
                canonical_id = CanonicalId(id=value, url=None, synonyms=())
                self._cache[cache_key] = canonical_id

    def save(self, tag: str) -> None:
        """Save cache to JSON file.

        Args:
            tag: Path to the cache file (overrides self.cache_file if provided).
                 If tag is a path, it's used as-is.
        """
        # If tag looks like a path, use it; otherwise use self.cache_file
        cache_path = Path(tag) if tag and Path(tag).is_absolute() else self.cache_file
        if tag and not Path(tag).is_absolute() and tag != str(self.cache_file):
            # Relative path provided as tag - use it
            cache_path = Path(tag)

        if not self._cache_dirty and not self._known_bad:
            return

        try:
            # Build data structure: only persist successful lookups
            # Known bad entries are kept in memory only (like old "NULL" behavior)
            data: dict[str, dict] = {}
            for cache_key, canonical_id in self._cache.items():
                data[cache_key] = {
                    "id": canonical_id.id,
                    "url": canonical_id.url,
                    "synonyms": list(canonical_id.synonyms),
                }

            # Ensure parent directory exists
            cache_path.parent.mkdir(parents=True, exist_ok=True)

            # Write cache file with explicit flush/fsync for reliability
            with open(cache_path, "w") as f:
                json.dump(data, f, indent=2)
                f.flush()  # Flush Python buffer
                os.fsync(f.fileno())  # Force OS to write to disk

            # Verify file was actually created
            if not cache_path.exists():
                raise RuntimeError(f"Cache file was not created at {cache_path.absolute()}")

            file_size = cache_path.stat().st_size
            if file_size == 0 and len(data) > 0:
                raise RuntimeError(f"Cache file is empty but should have {len(data)} entries")

            self._cache_dirty = False
            self.logger.debug(
                {
                    "message": f"Saved {len(data)} cached lookups to {cache_path}",
                    "cache_file": str(cache_path.absolute()),
                    "persistent_count": len(data),
                    "known_bad_memory_only": len(self._known_bad),
                },
                pprint=True,
            )
        except Exception as e:
            self.logger.error(
                {
                    "message": f"Failed to save cache to {cache_path}",
                    "cache_file": str(cache_path.absolute()),
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                pprint=True,
            )
            # Don't raise - let caller handle if needed

    def store(self, term: str, entity_type: str, canonical_id: CanonicalId) -> None:
        """Store a canonical ID in the cache.

        Args:
            term: The entity name/mention text
            entity_type: Type of entity (e.g., "disease", "gene", "drug")
            canonical_id: The CanonicalId object to store
        """
        cache_key = self._normalize_key(term, entity_type)
        self._cache[cache_key] = canonical_id
        # Remove from known_bad if it was there
        self._known_bad.discard(cache_key)
        self._cache_dirty = True

    def fetch(self, term: str, entity_type: str) -> Optional[CanonicalId]:
        """Fetch a canonical ID from the cache.

        Args:
            term: The entity name/mention text
            entity_type: Type of entity (e.g., "disease", "gene", "drug")

        Returns:
            CanonicalId if found in cache, None if not found or marked as "known bad"
        """
        cache_key = self._normalize_key(term, entity_type)

        if cache_key in self._known_bad:
            # Known bad - don't retry
            self._hits += 1
            return None

        if cache_key in self._cache:
            self._hits += 1
            return self._cache[cache_key]

        self._misses += 1
        return None

    def mark_known_bad(self, term: str, entity_type: str) -> None:
        """Mark a term as "known bad" (failed lookup, don't retry).

        Args:
            term: The entity name/mention text
            entity_type: Type of entity (e.g., "disease", "gene", "drug")
        """
        cache_key = self._normalize_key(term, entity_type)
        self._known_bad.add(cache_key)
        # Remove from cache if it was there (shouldn't happen, but be safe)
        self._cache.pop(cache_key, None)
        self._cache_dirty = True

    def is_known_bad(self, term: str, entity_type: str) -> bool:
        """Check if a term is marked as "known bad".

        Args:
            term: The entity name/mention text
            entity_type: Type of entity (e.g., "disease", "gene", "drug")

        Returns:
            True if the term is marked as "known bad", False otherwise
        """
        cache_key = self._normalize_key(term, entity_type)
        return cache_key in self._known_bad

    def get_metrics(self) -> dict[str, int]:
        """Get cache performance metrics.

        Returns:
            Dictionary with metrics:
            - "hits": Number of cache hits
            - "misses": Number of cache misses
            - "known_bad": Number of known bad entries
            - "total_entries": Total number of successful entries in cache
        """
        return {
            "hits": self._hits,
            "misses": self._misses,
            "known_bad": len(self._known_bad),
            "total_entries": len(self._cache),
        }

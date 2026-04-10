"""Authority-lookup cache backed by Redis.

Copied verbatim from kgraph/kgserver/storage/backends/identity.py and made
self-contained (no kgschema dependency).
"""

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

#: Sentinel stored in Redis to represent a confirmed negative result
#: (authority returned no canonical ID for this mention).
_NEGATIVE_SENTINEL = "__negative__"

#: Default TTL (seconds) for positive cache entries.
_POSITIVE_TTL = 86400  # 24 hours

#: Default TTL for negative entries — shorter so that a mention newly added
#: to an authority source stops being provisional within a reasonable window.
_NEGATIVE_TTL = 3600  # 1 hour


class AuthorityCache:
    """Redis cache for authority-lookup results in ``resolve``.

    Keys have the form ``resolve:{authority_version}:{entity_type}:{mention}``
    so that a UMLS/DBPedia release can be invalidated by bumping
    ``authority_version`` without touching unrelated entries.

    Values are JSON-serialised ``CanonicalId`` dicts (positive hit) or
    ``_NEGATIVE_SENTINEL`` (confirmed miss).

    Designed for graceful degradation: every public method catches Redis
    errors and logs at DEBUG level so a Redis outage never breaks ingestion.

    Parameters
    ----------
    redis_client:
        A ``redis.Redis`` (sync) client.  Pass ``None`` to disable caching.
    authority_version:
        Opaque version string for the authority source, e.g. ``"umls-2026AA"``.
        Bump this to invalidate all cached lookups for that source.
    positive_ttl:
        Seconds before a positive cache entry expires.
    negative_ttl:
        Seconds before a negative cache entry expires.
    """

    def __init__(
        self,
        redis_client: Optional[Any],
        authority_version: str = "v1",
        positive_ttl: int = _POSITIVE_TTL,
        negative_ttl: int = _NEGATIVE_TTL,
    ) -> None:
        self._redis: Optional[Any] = redis_client
        self._version = authority_version
        self._positive_ttl = positive_ttl
        self._negative_ttl = negative_ttl

    def _key(self, entity_type: str, mention: str) -> str:
        # Normalise mention to lower-case stripped form so that trivial
        # capitalisation differences share a cache entry.
        normalised = mention.strip().lower()
        return f"resolve:{self._version}:{entity_type}:{normalised}"

    def get(self, entity_type: str, mention: str) -> Optional[Any]:
        """Return cached ``CanonicalId``-like dict, ``None`` (miss), or
        ``_NEGATIVE_SENTINEL`` (confirmed negative).

        Returns ``None`` on any Redis error so the caller falls through to the
        live authority lookup.
        """
        if self._redis is None:
            return None
        try:
            raw = self._redis.get(self._key(entity_type, mention))  # type: ignore[union-attr]
            if raw is None:
                return None
            decoded = raw.decode() if isinstance(raw, bytes) else raw
            if decoded == _NEGATIVE_SENTINEL:
                return _NEGATIVE_SENTINEL
            return json.loads(decoded)
        except Exception:  # pylint: disable=broad-except
            logger.debug("AuthorityCache.get failed", exc_info=True)
            return None

    def put_positive(self, entity_type: str, mention: str, canonical_id: object) -> None:
        """Cache a positive authority result.  ``canonical_id`` must be
        JSON-serialisable (plain dict or object with ``__dict__``).
        """
        if self._redis is None:
            return
        try:
            payload = json.dumps(canonical_id.__dict__ if hasattr(canonical_id, "__dict__") else canonical_id)
            self._redis.setex(self._key(entity_type, mention), self._positive_ttl, payload)  # type: ignore[union-attr]
        except Exception:  # pylint: disable=broad-except
            logger.debug("AuthorityCache.put_positive failed", exc_info=True)

    def put_negative(self, entity_type: str, mention: str) -> None:
        """Cache a confirmed negative (no canonical ID found)."""
        if self._redis is None:
            return
        try:
            self._redis.setex(self._key(entity_type, mention), self._negative_ttl, _NEGATIVE_SENTINEL)  # type: ignore[union-attr]
        except Exception:  # pylint: disable=broad-except
            logger.debug("AuthorityCache.put_negative failed", exc_info=True)

    @classmethod
    def from_env(cls, authority_version: str = "v1") -> "AuthorityCache":
        """Build an ``AuthorityCache`` from the ``REDIS_URL`` environment variable.

        Returns a no-op cache (``redis_client=None``) if ``REDIS_URL`` is unset
        or if the ``redis`` package is not installed, so the server starts
        cleanly in environments without Redis.
        """
        import os

        redis_url = os.environ.get("REDIS_URL")
        if not redis_url:
            logger.debug("AuthorityCache.from_env: REDIS_URL not set; caching disabled")
            return cls(None, authority_version=authority_version)
        try:
            import redis as _redis

            client = _redis.Redis.from_url(redis_url, decode_responses=False)
            client.ping()
            logger.info("AuthorityCache: connected to Redis at %s", redis_url)
            return cls(client, authority_version=authority_version)
        except Exception:  # pylint: disable=broad-except
            logger.warning("AuthorityCache.from_env: could not connect to Redis; caching disabled", exc_info=True)
            return cls(None, authority_version=authority_version)

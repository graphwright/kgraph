"""Tests for AuthorityCache (identity_server/cache.py).

Uses a mock Redis client (unittest.mock.MagicMock) so no real Redis is needed.
Tests cover:
  - cache miss (key not in Redis)
  - positive hit (canonical ID dict returned)
  - negative hit (_NEGATIVE_SENTINEL returned)
  - put_positive stores correct JSON
  - put_negative stores sentinel value
  - Redis errors degrade gracefully (no exception raised)
  - no-op when redis_client is None
"""

import json
from unittest.mock import MagicMock

import pytest

from identity_server.cache import AuthorityCache, _NEGATIVE_SENTINEL


@pytest.fixture()
def mock_redis():
    """Return a MagicMock simulating a redis.Redis sync client."""
    return MagicMock()


@pytest.fixture()
def cache(mock_redis):
    """AuthorityCache wired to the mock Redis client."""
    return AuthorityCache(redis_client=mock_redis, authority_version="test-v1")


# ---------------------------------------------------------------------------
# get — cache miss
# ---------------------------------------------------------------------------


def test_get_miss_returns_none(cache, mock_redis):
    """When Redis has no entry for the key, get() must return None."""
    mock_redis.get.return_value = None
    result = cache.get("drug", "aspirin")
    assert result is None
    mock_redis.get.assert_called_once()


# ---------------------------------------------------------------------------
# get — positive hit
# ---------------------------------------------------------------------------


def test_get_positive_hit_returns_dict(cache, mock_redis):
    """When Redis has a cached canonical ID, get() returns the parsed dict."""
    payload = json.dumps({"id": "UMLS:C001", "url": "http://example.com", "synonyms": ["ASA"]})
    mock_redis.get.return_value = payload.encode()
    result = cache.get("drug", "aspirin")
    assert isinstance(result, dict)
    assert result["id"] == "UMLS:C001"
    assert result["synonyms"] == ["ASA"]


# ---------------------------------------------------------------------------
# get — negative hit
# ---------------------------------------------------------------------------


def test_get_negative_hit_returns_sentinel(cache, mock_redis):
    """When Redis has the negative sentinel, get() returns _NEGATIVE_SENTINEL."""
    mock_redis.get.return_value = _NEGATIVE_SENTINEL.encode()
    result = cache.get("drug", "aspirin")
    assert result is _NEGATIVE_SENTINEL


# ---------------------------------------------------------------------------
# put_positive
# ---------------------------------------------------------------------------


def test_put_positive_stores_json(cache, mock_redis):
    """put_positive() serialises the canonical ID and calls Redis setex."""

    class FakeCanonicalId:
        def __init__(self):
            self.id = "UMLS:C002"
            self.url = None
            self.synonyms = ("ibuprofen",)

    canonical_id = FakeCanonicalId()
    cache.put_positive("drug", "ibuprofen", canonical_id)
    mock_redis.setex.assert_called_once()
    args = mock_redis.setex.call_args
    # Third positional arg is the payload
    payload_str = args[0][2]
    data = json.loads(payload_str)
    assert data["id"] == "UMLS:C002"


def test_put_positive_with_plain_dict(cache, mock_redis):
    """put_positive() works when given a plain dict (no __dict__ attribute)."""
    cache.put_positive("disease", "diabetes", {"id": "UMLS:C003", "url": None, "synonyms": []})
    mock_redis.setex.assert_called_once()


# ---------------------------------------------------------------------------
# put_negative
# ---------------------------------------------------------------------------


def test_put_negative_stores_sentinel(cache, mock_redis):
    """put_negative() writes _NEGATIVE_SENTINEL to Redis."""
    cache.put_negative("disease", "unknown-entity")
    mock_redis.setex.assert_called_once()
    args = mock_redis.setex.call_args[0]
    assert args[2] == _NEGATIVE_SENTINEL


# ---------------------------------------------------------------------------
# Graceful degradation on Redis errors
# ---------------------------------------------------------------------------


def test_get_redis_error_returns_none(cache, mock_redis):
    """If Redis raises an exception, get() returns None (no crash)."""
    mock_redis.get.side_effect = RuntimeError("connection refused")
    result = cache.get("drug", "aspirin")
    assert result is None


def test_put_positive_redis_error_silent(cache, mock_redis):
    """If Redis raises during put_positive, no exception is propagated."""
    mock_redis.setex.side_effect = RuntimeError("connection refused")
    # Must not raise
    cache.put_positive("drug", "aspirin", {"id": "UMLS:C001", "url": None, "synonyms": []})


def test_put_negative_redis_error_silent(cache, mock_redis):
    """If Redis raises during put_negative, no exception is propagated."""
    mock_redis.setex.side_effect = RuntimeError("connection refused")
    cache.put_negative("drug", "aspirin")


# ---------------------------------------------------------------------------
# No-op when redis_client is None
# ---------------------------------------------------------------------------


def test_noop_cache_get_returns_none():
    """AuthorityCache with redis_client=None always returns None from get()."""
    noop = AuthorityCache(redis_client=None)
    assert noop.get("drug", "aspirin") is None


def test_noop_cache_put_does_not_raise():
    """AuthorityCache with redis_client=None accepts put_positive and put_negative silently."""
    noop = AuthorityCache(redis_client=None)
    noop.put_positive("drug", "aspirin", {"id": "X", "url": None, "synonyms": []})
    noop.put_negative("drug", "aspirin")

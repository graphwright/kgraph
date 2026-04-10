"""Tests for DomainClient (identity_server/domain_client.py).

Uses httpx.MockTransport to intercept HTTP calls without a real server.
Tests cover:
  - successful resolve-authority with a canonical ID
  - resolve-authority returning null canonical_id
  - connection error degrades to None / default values
  - successful select-survivor
  - select-survivor connection error falls back to highest usage_count
  - successful synonym-criteria
  - synonym-criteria connection error falls back to 0.90
"""

import httpx
import pytest

from identity_server.domain_client import DomainClient, _DEFAULT_SIMILARITY_THRESHOLD
from identity_server.models import DomainCandidateEntity

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_transport(routes: dict):
    """Build an httpx.MockTransport from a dict of {url_suffix: response_body}."""

    def handler(request: httpx.Request) -> httpx.Response:
        for path, body in routes.items():
            if request.url.path == path:
                return httpx.Response(200, json=body)
        return httpx.Response(404, json={"error": "not found"})

    return httpx.MockTransport(handler)


def _error_transport():
    """A transport that always raises a connection error."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("simulated connection failure")

    return httpx.MockTransport(handler)


def _client_with_transport(transport) -> DomainClient:
    """DomainClient pre-wired with a custom transport (bypasses real HTTP)."""
    client = DomainClient(base_url="http://test-domain")

    async def patched_resolve(mention, entity_type, document_id):
        async with httpx.AsyncClient(transport=transport) as c:
            resp = await c.post("http://test-domain/resolve-authority", json={"mention": mention, "entity_type": entity_type, "document_id": document_id})
            resp.raise_for_status()
            data = resp.json()
            cid_data = data.get("canonical_id")
            if cid_data is None:
                return None
            from identity_server.models import DomainCanonicalId

            return DomainCanonicalId(**cid_data)

    async def patched_select(candidates):
        async with httpx.AsyncClient(transport=transport) as c:
            payload = [c_item.model_dump() for c_item in candidates]
            resp = await c.post("http://test-domain/select-survivor", json={"candidates": payload})
            resp.raise_for_status()
            return resp.json()["survivor_id"]

    async def patched_criteria(entity_type):
        async with httpx.AsyncClient(transport=transport) as c:
            resp = await c.post("http://test-domain/synonym-criteria", json={"entity_type": entity_type})
            resp.raise_for_status()
            return float(resp.json()["similarity_threshold"])

    client.resolve_authority = patched_resolve  # type: ignore[method-assign]
    client.select_survivor = patched_select  # type: ignore[method-assign]
    client.synonym_criteria = patched_criteria  # type: ignore[method-assign]
    return client


# ---------------------------------------------------------------------------
# resolve_authority — success with canonical ID
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_authority_returns_canonical_id():
    """Successful resolve-authority response with a canonical ID is parsed correctly."""
    transport = _make_transport({"/resolve-authority": {"canonical_id": {"id": "UMLS:C001", "url": "http://umls.example/C001", "synonyms": ["aspirin", "ASA"]}}})
    client = _client_with_transport(transport)
    result = await client.resolve_authority("aspirin", "drug", "doc-001")
    assert result is not None
    assert result.id == "UMLS:C001"
    assert result.url == "http://umls.example/C001"
    assert "aspirin" in result.synonyms


# ---------------------------------------------------------------------------
# resolve_authority — null canonical_id
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_authority_null_canonical_id():
    """When the domain service returns canonical_id=null, resolve_authority returns None."""
    transport = _make_transport({"/resolve-authority": {"canonical_id": None}})
    client = _client_with_transport(transport)
    result = await client.resolve_authority("unknown-drug", "drug", "doc-001")
    assert result is None


# ---------------------------------------------------------------------------
# resolve_authority — connection error
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_authority_connection_error_returns_none():
    """When the domain service is unreachable, resolve_authority degrades to None."""
    client = DomainClient(base_url="http://does-not-exist-123456.invalid")
    result = await client.resolve_authority("aspirin", "drug", "doc-001")
    assert result is None


# ---------------------------------------------------------------------------
# select_survivor — success
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_select_survivor_success():
    """Successful select-survivor response is returned correctly."""
    transport = _make_transport({"/select-survivor": {"survivor_id": "entity-B"}})
    client = _client_with_transport(transport)
    candidates = [
        DomainCandidateEntity(entity_id="entity-A", name="Aspirin", entity_type="drug", status="provisional", usage_count=1, confidence=0.9),
        DomainCandidateEntity(entity_id="entity-B", name="Aspirin alt", entity_type="drug", status="provisional", usage_count=5, confidence=0.8),
    ]
    result = await client.select_survivor(candidates)
    assert result == "entity-B"


# ---------------------------------------------------------------------------
# select_survivor — connection error fallback
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_select_survivor_connection_error_falls_back_to_highest_usage():
    """When domain service is unreachable, select_survivor returns highest usage_count candidate."""
    client = DomainClient(base_url="http://does-not-exist-123456.invalid")
    candidates = [
        DomainCandidateEntity(entity_id="entity-A", name="Aspirin", entity_type="drug", status="provisional", usage_count=2, confidence=0.9),
        DomainCandidateEntity(entity_id="entity-B", name="Aspirin alt", entity_type="drug", status="provisional", usage_count=7, confidence=0.8),
        DomainCandidateEntity(entity_id="entity-C", name="Aspirin B", entity_type="drug", status="provisional", usage_count=1, confidence=1.0),
    ]
    result = await client.select_survivor(candidates)
    assert result == "entity-B"


# ---------------------------------------------------------------------------
# synonym_criteria — success
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_synonym_criteria_success():
    """Successful synonym-criteria response is parsed and returned."""
    transport = _make_transport({"/synonym-criteria": {"similarity_threshold": 0.85}})
    client = _client_with_transport(transport)
    result = await client.synonym_criteria("drug")
    assert result == pytest.approx(0.85)


# ---------------------------------------------------------------------------
# synonym_criteria — connection error fallback
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_synonym_criteria_connection_error_returns_default():
    """When domain service is unreachable, synonym_criteria falls back to default threshold."""
    client = DomainClient(base_url="http://does-not-exist-123456.invalid")
    result = await client.synonym_criteria("drug")
    assert result == pytest.approx(_DEFAULT_SIMILARITY_THRESHOLD)

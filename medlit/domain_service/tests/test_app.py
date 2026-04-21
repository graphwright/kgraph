"""Integration tests for the domain service FastAPI endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from domain_service.app import app
from domain_service.models import CanonicalIdResponse

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    assert "version" in resp.json()


def test_resolve_authority_no_match():
    """When authority lookup returns None, response has canonical_id=null."""
    with patch("domain_service.app.resolve_authority", new=AsyncMock(return_value=None)):
        resp = client.post("/resolve-authority", json={"mention": "unknown thing", "entity_type": "disease", "document_id": "doc1"})
    assert resp.status_code == 200
    assert resp.json()["canonical_id"] is None


def test_resolve_authority_match():
    """When authority lookup returns a canonical ID, it is included in the response."""
    mock_result = CanonicalIdResponse(id="UMLS:C0006142", url="https://uts.nlm.nih.gov/uts/umls/concept/C0006142", synonyms=["breast cancer"])
    with patch("domain_service.app.resolve_authority", new=AsyncMock(return_value=mock_result)):
        resp = client.post("/resolve-authority", json={"mention": "breast cancer", "entity_type": "disease", "document_id": "doc1"})
    assert resp.status_code == 200
    data = resp.json()["canonical_id"]
    assert data["id"] == "UMLS:C0006142"
    assert data["url"] is not None


def test_select_survivor_canonical_wins():
    resp = client.post(
        "/select-survivor",
        json={
            "candidates": [
                {"entity_id": "prov:abc", "name": "breast cancer", "entity_type": "disease", "status": "provisional", "usage_count": 10, "confidence": 0.8},
                {"entity_id": "C0006142", "name": "breast cancer", "entity_type": "disease", "status": "canonical", "usage_count": 1, "confidence": 0.9},
            ]
        },
    )
    assert resp.status_code == 200
    assert resp.json()["survivor_id"] == "C0006142"


def test_synonym_criteria_known_type():
    resp = client.post("/synonym-criteria", json={"entity_type": "gene"})
    assert resp.status_code == 200
    assert resp.json()["similarity_threshold"] >= 0.93


def test_synonym_criteria_unknown_type():
    resp = client.post("/synonym-criteria", json={"entity_type": "widget"})
    assert resp.status_code == 200
    assert resp.json()["similarity_threshold"] == 0.90


def test_schema_endpoint():
    resp = client.get("/schema")
    assert resp.status_code == 200
    data = resp.json()
    assert "version" in data
    assert "entity_types" in data
    assert "predicates" in data
    assert "disease" in data["entity_types"]
    assert any(p["name"] == "TREATS" for p in data["predicates"])


def test_authorities_endpoint():
    resp = client.get("/authorities")
    assert resp.status_code == 200
    data = resp.json()
    assert "authorities" in data
    assert any(a["name"] == "UMLS" for a in data["authorities"])


def test_synonym_criteria_get_config():
    resp = client.get("/synonym-criteria")
    assert resp.status_code == 200
    data = resp.json()
    assert "fuzzy_threshold" in data
    assert "embedding_threshold" in data
    assert "entity_type_overrides" in data
    assert "gene" in data["entity_type_overrides"]


def test_compute_confidence():
    resp = client.post(
        "/compute-confidence",
        json={
            "provenance_records": [
                {
                    "paper_id": "PMC1",
                    "section_type": "results",
                    "paragraph_idx": 1,
                    "extraction_method": "llm",
                    "confidence": 0.9,
                    "study_type": "rct",
                },
                {
                    "paper_id": "PMC1",
                    "section_type": "discussion",
                    "paragraph_idx": 2,
                    "extraction_method": "llm",
                    "confidence": 0.7,
                    "study_type": "case_report",
                },
            ]
        },
    )
    assert resp.status_code == 200
    # Domain service intentionally caps aggregate confidence below 1.0.
    assert 0.0 <= resp.json()["confidence"] <= 0.99

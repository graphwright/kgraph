"""Tests for the /admin/dump, /admin/load, and /admin/wipe endpoints."""

import json

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from identity_server.app import app
from identity_server.db_models import Entity


@pytest.fixture
def client(session: Session, engine):
    """TestClient with the session dependency overridden and lifespan bypassed."""
    import identity_server.database as db_module
    from identity_server.database import get_session

    # Point the module-level engine at the test engine so the lifespan's
    # create_db_and_tables() call is a no-op (tables already exist).
    original_engine = db_module.engine
    db_module.engine = engine

    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    db_module.engine = original_engine


def _make_entity(entity_id: str, name: str = "test", status: str = "provisional") -> dict:
    return {
        "entity_id": entity_id,
        "entity_type": "disease",
        "name": name,
        "status": status,
        "confidence": 0.9,
        "usage_count": 1,
        "source": "doc1",
        "canonical_url": None,
        "synonyms": [],
        "properties": {},
        "merged_into": None,
        "embedding": None,
    }


# ---------------------------------------------------------------------------
# dump
# ---------------------------------------------------------------------------


def test_dump_empty(client):
    resp = client.get("/admin/dump")
    assert resp.status_code == 200
    assert resp.text == ""


def test_dump_returns_ndjson(client, session):
    session.add(Entity(**_make_entity("e1", name="breast cancer")))
    session.add(Entity(**_make_entity("e2", name="lung cancer")))
    session.commit()

    resp = client.get("/admin/dump")
    assert resp.status_code == 200

    lines = [ln for ln in resp.text.splitlines() if ln.strip()]
    assert len(lines) == 2
    ids = {json.loads(ln)["entity_id"] for ln in lines}
    assert ids == {"e1", "e2"}


def test_dump_content_disposition(client, session):
    session.add(Entity(**_make_entity("e1")))
    session.commit()
    resp = client.get("/admin/dump")
    assert "entities.ndjson" in resp.headers.get("content-disposition", "")


# ---------------------------------------------------------------------------
# load
# ---------------------------------------------------------------------------


def test_load_inserts_rows(client, session):
    rows = [_make_entity("e1", name="diabetes"), _make_entity("e2", name="hypertension")]
    body = "\n".join(json.dumps(r) for r in rows)

    resp = client.post("/admin/load", content=body.encode(), headers={"Content-Type": "application/x-ndjson"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["inserted"] == 2
    assert data["skipped"] == 0
    assert data["errors"] == 0

    assert session.get(Entity, "e1") is not None
    assert session.get(Entity, "e2") is not None


def test_load_skips_existing(client, session):
    session.add(Entity(**_make_entity("e1")))
    session.commit()

    body = json.dumps(_make_entity("e1", name="updated name"))
    resp = client.post("/admin/load", content=body.encode(), headers={"Content-Type": "application/x-ndjson"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["inserted"] == 0
    assert data["skipped"] == 1

    # Original name preserved
    entity = session.get(Entity, "e1")
    assert entity.name == "test"


def test_load_handles_invalid_json_line(client):
    body = b'{"entity_id": "e1", "entity_type": "disease", "name": "ok"}\nnot-json\n'
    resp = client.post("/admin/load", content=body, headers={"Content-Type": "application/x-ndjson"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["inserted"] == 1
    assert data["errors"] == 1


def test_load_skips_missing_entity_id(client):
    body = json.dumps({"entity_type": "disease", "name": "no id"}).encode()
    resp = client.post("/admin/load", content=body, headers={"Content-Type": "application/x-ndjson"})
    assert resp.status_code == 200
    assert resp.json()["errors"] == 1


def test_dump_load_roundtrip(client, session):
    """Dump → wipe → load should restore the same rows."""
    session.add(Entity(**_make_entity("e1", name="diabetes", status="canonical")))
    session.add(Entity(**_make_entity("e2", name="hypertension")))
    session.commit()

    dump_resp = client.get("/admin/dump")
    assert dump_resp.status_code == 200
    ndjson = dump_resp.content

    # Wipe
    wipe_resp = client.delete("/admin/wipe", headers={"X-Confirm-Wipe": "yes"})
    assert wipe_resp.json()["deleted"] == 2

    # Load
    load_resp = client.post("/admin/load", content=ndjson, headers={"Content-Type": "application/x-ndjson"})
    assert load_resp.json()["inserted"] == 2

    assert session.get(Entity, "e1").name == "diabetes"
    assert session.get(Entity, "e2").name == "hypertension"


# ---------------------------------------------------------------------------
# wipe
# ---------------------------------------------------------------------------


def test_wipe_requires_confirmation(client, session):
    session.add(Entity(**_make_entity("e1")))
    session.commit()

    resp = client.delete("/admin/wipe")
    assert resp.status_code == 400
    assert session.get(Entity, "e1") is not None


def test_wipe_deletes_all(client, session):
    session.add(Entity(**_make_entity("e1")))
    session.add(Entity(**_make_entity("e2")))
    session.commit()

    resp = client.delete("/admin/wipe", headers={"X-Confirm-Wipe": "yes"})
    assert resp.status_code == 200
    assert resp.json()["deleted"] == 2
    assert session.get(Entity, "e1") is None

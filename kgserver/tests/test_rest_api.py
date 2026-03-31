"""
Tests for query/routers/rest_api.py REST API endpoints.

Tests cover:
- GET /api/v1/entities/{entity_id}
- GET /api/v1/entities
- GET /api/v1/relationships
"""

# pylint: disable=protected-access
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from query.routers import rest_api


@pytest.fixture
def app():
    """Create FastAPI app with REST API router."""
    app = FastAPI()
    app.include_router(rest_api.router)
    return app


@pytest.fixture
def file_storage(tmp_path, sample_entities, sample_relationships):
    """Create SQLite storage for thread-safe testing with FastAPI TestClient.

    Uses tmp_path which automatically cleans up files after tests.
    Uses check_same_thread=False for TestClient threading compatibility.
    """
    from storage.backends.sqlite import SQLiteStorage

    # tmp_path is automatically cleaned up by pytest, so no files left behind
    db_path = tmp_path / "test.db"
    # Use check_same_thread=False for TestClient threading compatibility
    storage = SQLiteStorage(str(db_path), check_same_thread=False)

    # Add entities and relationships
    for entity in sample_entities:
        storage._session.add(entity)
    for rel in sample_relationships:
        storage._session.add(rel)
    storage._session.commit()

    try:
        yield storage
    finally:
        # Ensure cleanup even if test fails
        storage.close()
        # Explicitly remove the database file (tmp_path cleanup should handle this,
        # but being explicit ensures no files are left behind)
        if db_path.exists():
            db_path.unlink()


@pytest.fixture
def client(app, file_storage):
    """Create test client with storage dependency override."""
    from query.storage_factory import get_storage

    def override_get_storage():
        yield file_storage

    # Override the dependency
    app.dependency_overrides[get_storage] = override_get_storage
    client = TestClient(app)
    yield client
    # Cleanup
    app.dependency_overrides.clear()


class TestGetEntityById:
    """Test GET /api/v1/entities/{entity_id} endpoint."""

    def test_get_existing_entity(self, client):
        """Test retrieving an existing entity."""
        response = client.get("/api/v1/entities/test:entity:1")
        assert response.status_code == 200
        data = response.json()
        assert data["entity_id"] == "test:entity:1"
        assert data["name"] == "Test Character 1"
        assert data["entity_type"] == "character"

    def test_get_nonexistent_entity(self, client):
        """Test retrieving a non-existent entity returns 404."""
        response = client.get("/api/v1/entities/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestListEntities:
    """Test GET /api/v1/entities endpoint."""

    def test_list_entities_default(self, client):
        """Test listing entities with default parameters."""
        response = client.get("/api/v1/entities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3  # All entities in test data

    def test_list_entities_with_limit(self, client):
        """Test listing entities with limit."""
        response = client.get("/api/v1/entities?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_entities_with_offset(self, client):
        """Test listing entities with offset."""
        response = client.get("/api/v1/entities?limit=2&offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Should skip first entity (ordered by usage_count DESC, so entity:3 is first)
        assert data[0]["entity_id"] != "test:entity:3"

    def test_list_entities_empty_result(self, client):
        """Test listing entities with offset beyond available."""
        response = client.get("/api/v1/entities?limit=10&offset=100")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


class TestFindRelationships:
    """Test GET /api/v1/relationships endpoint."""

    def test_find_all_relationships(self, client):
        """Test finding all relationships."""
        response = client.get("/api/v1/relationships")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3  # All relationships in test data

    def test_find_relationships_by_subject(self, client):
        """Test filtering relationships by subject_id."""
        response = client.get("/api/v1/relationships?subject_id=test:entity:1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for rel in data:
            assert rel["subject_id"] == "test:entity:1"

    def test_find_relationships_by_object(self, client):
        """Test filtering relationships by object_id."""
        response = client.get("/api/v1/relationships?object_id=test:entity:3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for rel in data:
            assert rel["object_id"] == "test:entity:3"

    def test_find_relationships_by_predicate(self, client):
        """Test filtering relationships by predicate."""
        response = client.get("/api/v1/relationships?predicate=co_occurs_with")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for rel in data:
            assert rel["predicate"] == "co_occurs_with"

    def test_find_relationships_combined_filters(self, client):
        """Test filtering relationships with multiple filters."""
        response = client.get("/api/v1/relationships?subject_id=test:entity:1&predicate=co_occurs_with")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        rel = data[0]
        assert rel["subject_id"] == "test:entity:1"
        assert rel["predicate"] == "co_occurs_with"
        assert rel["object_id"] == "test:entity:2"

    def test_find_relationships_with_limit(self, client):
        """Test limiting relationship results."""
        response = client.get("/api/v1/relationships?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_find_relationships_no_matches(self, client):
        """Test finding relationships with no matches."""
        response = client.get("/api/v1/relationships?subject_id=nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

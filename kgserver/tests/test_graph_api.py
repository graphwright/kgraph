"""
Tests for graph visualization API and traversal logic.
"""

import pytest
from fastapi.testclient import TestClient

from query.graph_traversal import (
    SubgraphResponse,
    extract_subgraph,
    extract_full_graph,
)


@pytest.fixture
def app():
    """Create FastAPI app with Graph API and Subgraph API routers."""
    from fastapi import FastAPI
    from query.routers import graph_api
    from query.routers import subgraph_api

    _app = FastAPI()
    _app.include_router(graph_api.router)
    _app.include_router(subgraph_api.router)
    return _app


class TestGraphTraversal:
    """Tests for BFS graph traversal logic."""

    def test_extract_subgraph_single_hop(self, populated_storage):
        """Test extracting a subgraph with 1 hop from center."""
        result = extract_subgraph(
            populated_storage,
            center_id="test:entity:1",
            hops=1,
            max_nodes=100,
        )

        assert isinstance(result, SubgraphResponse)
        assert result.center_id == "test:entity:1"
        assert result.hops == 1
        assert not result.truncated

        # Should include center + direct neighbors
        node_ids = {n.id for n in result.nodes}
        assert "test:entity:1" in node_ids
        assert "test:entity:2" in node_ids  # Connected via co_occurs_with
        assert "test:entity:3" in node_ids  # Connected via appears_in

        # Should have edges
        assert len(result.edges) >= 2

    def test_extract_subgraph_two_hops(self, populated_storage):
        """Test extracting a subgraph with 2 hops."""
        result = extract_subgraph(
            populated_storage,
            center_id="test:entity:1",
            hops=2,
            max_nodes=100,
        )

        # With 2 hops, should get all 3 entities and all relationships
        assert len(result.nodes) == 3
        assert len(result.edges) == 3

    def test_extract_subgraph_nonexistent_center(self, populated_storage):
        """Test extracting subgraph with non-existent center returns empty."""
        result = extract_subgraph(
            populated_storage,
            center_id="nonexistent:entity",
            hops=2,
            max_nodes=100,
        )

        assert len(result.nodes) == 0
        assert len(result.edges) == 0
        assert result.center_id == "nonexistent:entity"

    def test_extract_subgraph_respects_max_nodes(self, populated_storage):
        """Test that max_nodes limit is respected."""
        result = extract_subgraph(
            populated_storage,
            center_id="test:entity:1",
            hops=5,  # High hop count
            max_nodes=2,  # But limit to 2 nodes
        )

        assert len(result.nodes) <= 2
        assert result.truncated or len(result.nodes) <= 2

    def test_extract_full_graph(self, populated_storage):
        """Test extracting the full graph."""
        result = extract_full_graph(populated_storage, max_nodes=100)

        assert result.center_id is None
        assert result.hops == 0
        assert len(result.nodes) == 3
        assert len(result.edges) == 3
        assert result.total_entities == 3
        assert result.total_relationships == 3

    def test_graph_node_structure(self, populated_storage):
        """Test that GraphNode has correct structure."""
        result = extract_subgraph(
            populated_storage,
            center_id="test:entity:1",
            hops=1,
        )

        node = next(n for n in result.nodes if n.id == "test:entity:1")
        assert node.id == "test:entity:1"
        assert node.label == "Test Character 1"
        assert node.entity_type == "character"
        assert "entity_id" in node.properties
        assert "name" in node.properties

    def test_graph_edge_structure(self, populated_storage):
        """Test that GraphEdge has correct structure."""
        result = extract_subgraph(
            populated_storage,
            center_id="test:entity:1",
            hops=1,
        )

        # Find the co_occurs_with edge
        edge = next(
            (e for e in result.edges if e.predicate == "co_occurs_with"),
            None,
        )
        assert edge is not None
        assert edge.source == "test:entity:1"
        assert edge.target == "test:entity:2"
        assert edge.label == "co occurs with"  # Human-readable
        assert "confidence" in edge.properties


class TestGraphAPI:
    """Tests for graph visualization REST API."""

    @pytest.fixture
    def file_storage(self, tmp_path, sample_entities, sample_relationships):
        """Create SQLite storage for thread-safe testing."""
        from storage.backends.sqlite import SQLiteStorage

        db_path = tmp_path / "test_graph.db"
        # Use check_same_thread=False for TestClient threading compatibility
        storage = SQLiteStorage(str(db_path), check_same_thread=False)

        # Add test data
        for entity in sample_entities:
            storage.add_entity(entity)
        for rel in sample_relationships:
            storage.add_relationship(rel)

        try:
            yield storage
        finally:
            storage.close()
            if db_path.exists():
                db_path.unlink()

    @pytest.fixture
    def client(self, app, file_storage):
        """Create test client with storage dependency override."""
        from query.storage_factory import get_storage

        def override_get_storage():
            yield file_storage

        app.dependency_overrides[get_storage] = override_get_storage
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    def test_get_subgraph_with_center(self, client):
        """Test GET /api/v1/graph/subgraph with center_id."""
        response = client.get(
            "/api/v1/graph/subgraph",
            params={"center_id": "test:entity:1", "hops": 1},
        )

        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert data["center_id"] == "test:entity:1"
        assert len(data["nodes"]) >= 1

    def test_get_subgraph_include_all(self, client):
        """Test GET /api/v1/graph/subgraph with include_all=true."""
        response = client.get(
            "/api/v1/graph/subgraph",
            params={"include_all": True},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["center_id"] is None
        assert len(data["nodes"]) == 3

    def test_get_subgraph_missing_center_id(self, client):
        """Test that missing center_id returns 400 when include_all is false."""
        response = client.get("/api/v1/graph/subgraph")

        assert response.status_code == 400
        assert "center_id is required" in response.json()["detail"]

    def test_get_node_details(self, client):
        """Test GET /api/v1/graph/node/{entity_id}."""
        response = client.get("/api/v1/graph/node/test:entity:1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test:entity:1"
        assert data["label"] == "Test Character 1"
        assert data["entity_type"] == "character"

    def test_get_node_details_not_found(self, client):
        """Test GET /api/v1/graph/node with non-existent entity."""
        response = client.get("/api/v1/graph/node/nonexistent:entity")

        assert response.status_code == 404

    def test_get_edge_details(self, client):
        """Test GET /api/v1/graph/edge."""
        response = client.get(
            "/api/v1/graph/edge",
            params={
                "subject_id": "test:entity:1",
                "predicate": "co_occurs_with",
                "object_id": "test:entity:2",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "test:entity:1"
        assert data["target"] == "test:entity:2"
        assert data["predicate"] == "co_occurs_with"

    def test_get_edge_details_not_found(self, client):
        """Test GET /api/v1/graph/edge with non-existent relationship."""
        response = client.get(
            "/api/v1/graph/edge",
            params={
                "subject_id": "test:entity:1",
                "predicate": "nonexistent",
                "object_id": "test:entity:2",
            },
        )

        assert response.status_code == 404

    def test_hops_parameter_validation(self, client):
        """Test that hops parameter is validated."""
        # Hops too high should be clamped or rejected
        response = client.get(
            "/api/v1/graph/subgraph",
            params={"center_id": "test:entity:1", "hops": 10},
        )
        # Should either return 422 (validation error) or succeed with clamped value
        assert response.status_code in [200, 422]

    def test_max_nodes_parameter(self, client):
        """Test max_nodes parameter."""
        response = client.get(
            "/api/v1/graph/subgraph",
            params={"center_id": "test:entity:1", "hops": 2, "max_nodes": 2},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["nodes"]) <= 2

    def test_search_entities(self, client):
        """Test GET /api/v1/graph/search."""
        response = client.get(
            "/api/v1/graph/search",
            params={"q": "Test"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert "query" in data
        assert data["query"] == "Test"
        # Should find entities with "Test" in their name (e.g., "Test Character 1")
        assert len(data["results"]) > 0

        # Check result structure
        result = data["results"][0]
        assert "entity_id" in result
        assert "name" in result
        assert "entity_type" in result

    def test_search_entities_no_results(self, client):
        """Test search with no matching entities."""
        response = client.get(
            "/api/v1/graph/search",
            params={"q": "xyznonexistent123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []
        assert data["total"] == 0

    def test_search_entities_with_type_filter(self, client):
        """Test search with entity_type filter."""
        response = client.get(
            "/api/v1/graph/search",
            params={"q": "Test", "entity_type": "character"},
        )

        assert response.status_code == 200
        data = response.json()
        # All results should be of type "character"
        assert len(data["results"]) > 0
        for result in data["results"]:
            assert result["entity_type"] == "character"

    def test_get_entity_types(self, client):
        """Test GET /api/v1/graph/entity-types returns colors and labels from domain_spec."""
        response = client.get("/api/v1/graph/entity-types")

        assert response.status_code == 200
        data = response.json()
        assert "entity_types" in data
        types = data["entity_types"]
        assert "default" in types
        assert types["default"]["color"] == "#78909c"
        assert types["default"]["label"] == "Other"
        for _, val in types.items():
            assert "color" in val
            assert "label" in val
            assert isinstance(val["color"], str)
            assert isinstance(val["label"], str)

    def test_get_entity_mentions_empty_without_provenance(self, client):
        """GET /entity/{id}/mentions returns 200 and empty list when no mentions stored."""
        response = client.get("/api/v1/graph/entity/test:entity:1/mentions")
        assert response.status_code == 200
        data = response.json()
        assert "mentions" in data
        assert data["mentions"] == []

    def test_get_edge_evidence_empty_without_provenance(self, client):
        """GET /edge/evidence returns 200 and empty list when no evidence stored."""
        response = client.get(
            "/api/v1/graph/edge/evidence",
            params={
                "subject_id": "test:entity:1",
                "predicate": "co_occurs_with",
                "object_id": "test:entity:2",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "evidence" in data
        assert data["evidence"] == []


class TestSubgraphAPI:
    """Tests for REST Subgraph API."""

    @pytest.fixture
    def file_storage(self, tmp_path, sample_entities, sample_relationships):
        """Create SQLite storage for thread-safe testing."""
        from storage.backends.sqlite import SQLiteStorage

        db_path = tmp_path / "test_subgraph.db"
        storage = SQLiteStorage(str(db_path), check_same_thread=False)
        for entity in sample_entities:
            storage.add_entity(entity)
        for rel in sample_relationships:
            storage.add_relationship(rel)
        try:
            yield storage
        finally:
            storage.close()
            if db_path.exists():
                db_path.unlink()

    @pytest.fixture
    def client(self, app, file_storage):
        """Create test client with storage dependency override."""
        from query.storage_factory import get_storage

        def override_get_storage():
            yield file_storage

        app.dependency_overrides[get_storage] = override_get_storage
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    def test_subgraph_requires_entity_or_name(self, client):
        """GET /api/v1/subgraph with no params returns 400."""
        response = client.get("/api/v1/subgraph")
        assert response.status_code == 400
        assert "entity or name" in response.json()["detail"].lower()

    def test_subgraph_by_entity_id(self, client):
        """entity=test:entity:1&hops=1 returns 200, entities non-empty, query.seeds correct."""
        response = client.get(
            "/api/v1/subgraph",
            params={"entity": "test:entity:1", "hops": 1},
        )
        assert response.status_code == 200
        data = response.json()
        assert "entities" in data
        assert len(data["entities"]) > 0
        assert data["query"]["seeds"] == ["test:entity:1"]
        assert "relationships" in data

    def test_subgraph_by_name_glob(self, client):
        """name=Test&hops=1 resolves seeds from name match."""
        response = client.get(
            "/api/v1/subgraph",
            params={"name": "Test", "hops": 1},
        )
        assert response.status_code == 200
        data = response.json()
        assert "entities" in data
        assert len(data["entities"]) > 0
        assert len(data["query"]["seeds"]) > 0

    def test_subgraph_empty_seeds(self, client):
        """entity=nonexistent123 returns 200 with empty entities and relationships."""
        response = client.get(
            "/api/v1/subgraph",
            params={"entity": "nonexistent123", "hops": 1},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["entities"] == []
        assert data["relationships"] == []
        assert data["query"]["seeds"] == []

    def test_subgraph_query_echo(self, client):
        """Response includes query with seeds, hops, filters, truncated."""
        response = client.get(
            "/api/v1/subgraph",
            params={"entity": "test:entity:1", "hops": 2},
        )
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "seeds" in data["query"]
        assert "hops" in data["query"]
        assert "filters" in data["query"]
        assert "truncated" in data["query"]


class TestGraphAPIProvenance:
    """Graph API includes provenance/evidence in node and edge payloads when present."""

    @pytest.fixture
    def storage_with_provenance_properties(self, tmp_path):
        """Storage with entities and relationships that have provenance in properties."""
        from storage.backends.sqlite import SQLiteStorage
        from storage.models import Entity, Relationship

        db_path = tmp_path / "provenance.db"
        storage = SQLiteStorage(str(db_path), check_same_thread=False)
        storage.add_entity(
            Entity(
                entity_id="prov:entity:1",
                entity_type="drug",
                name="Aspirin",
                status="canonical",
                confidence=0.95,
                usage_count=5,
                source="test",
                synonyms=[],
                properties={
                    "first_seen_document": "doc-1",
                    "first_seen_section": "abstract",
                    "total_mentions": 3,
                    "supporting_documents": ["doc-1", "doc-2"],
                },
            )
        )
        storage.add_entity(
            Entity(
                entity_id="prov:entity:2",
                entity_type="disease",
                name="Headache",
                status="canonical",
                confidence=0.9,
                usage_count=1,
                source="test",
                synonyms=[],
                properties={},
            )
        )
        storage.add_relationship(
            Relationship(
                subject_id="prov:entity:1",
                predicate="treats",
                object_id="prov:entity:2",
                confidence=0.88,
                source_documents=["doc-1"],
                properties={
                    "evidence_count": 2,
                    "strongest_evidence_quote": "Aspirin treats headache.",
                    "evidence_confidence_avg": 0.85,
                },
            )
        )
        try:
            yield storage
        finally:
            storage.close()

    @pytest.fixture
    def client_provenance(self, app, storage_with_provenance_properties):
        """Test client with storage that has provenance in entity/relationship properties."""
        from query.storage_factory import get_storage

        def override():
            yield storage_with_provenance_properties

        app.dependency_overrides[get_storage] = override
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    def test_node_details_include_provenance(self, client_provenance):
        """GET /node/{id} includes first_seen_document, total_mentions, supporting_documents in properties."""
        response = client_provenance.get("/api/v1/graph/node/prov:entity:1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "prov:entity:1"
        props = data["properties"]
        assert props.get("first_seen_document") == "doc-1"
        assert props.get("first_seen_section") == "abstract"
        assert props.get("total_mentions") == 3
        assert props.get("supporting_documents") == ["doc-1", "doc-2"]

    def test_edge_details_include_evidence_summary(self, client_provenance):
        """GET /edge includes evidence_count, strongest_evidence_quote, evidence_confidence_avg in properties."""
        response = client_provenance.get(
            "/api/v1/graph/edge",
            params={
                "subject_id": "prov:entity:1",
                "predicate": "treats",
                "object_id": "prov:entity:2",
            },
        )
        assert response.status_code == 200
        data = response.json()
        props = data["properties"]
        assert props.get("evidence_count") == 2
        assert props.get("strongest_evidence_quote") == "Aspirin treats headache."
        assert props.get("evidence_confidence_avg") == 0.85

    def test_subgraph_node_properties_include_provenance(self, client_provenance):
        """Subgraph nodes include provenance fields in properties when present."""
        response = client_provenance.get(
            "/api/v1/graph/subgraph",
            params={"center_id": "prov:entity:1", "hops": 1},
        )
        assert response.status_code == 200
        data = response.json()
        node = next(n for n in data["nodes"] if n["id"] == "prov:entity:1")
        assert node["properties"].get("first_seen_document") == "doc-1"
        assert node["properties"].get("total_mentions") == 3

    def test_subgraph_edge_properties_include_evidence(self, client_provenance):
        """Subgraph edges include evidence summary in properties when present."""
        response = client_provenance.get(
            "/api/v1/graph/subgraph",
            params={"center_id": "prov:entity:1", "hops": 1},
        )
        assert response.status_code == 200
        data = response.json()
        edge = next(
            (e for e in data["edges"] if e["predicate"] == "treats"),
            None,
        )
        assert edge is not None
        assert edge["properties"].get("evidence_count") == 2
        assert edge["properties"].get("strongest_evidence_quote") == "Aspirin treats headache."


class TestGraphAPIMentionsEvidenceEndpoints:
    """GET /entity/{id}/mentions and GET /edge/evidence return stored provenance."""

    @pytest.fixture
    def client_with_mentions_evidence(self, app, storage_with_provenance_bundle):
        """Test client with storage that has mentions and evidence from a loaded bundle."""
        from query.storage_factory import get_storage

        def override():
            yield storage_with_provenance_bundle

        app.dependency_overrides[get_storage] = override
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    def test_get_entity_mentions_returns_mentions(self, client_with_mentions_evidence):
        """GET /entity/{id}/mentions returns mention rows when bundle had mentions.jsonl."""
        response = client_with_mentions_evidence.get("/api/v1/graph/entity/e1/mentions")
        assert response.status_code == 200
        data = response.json()
        assert "mentions" in data
        assert len(data["mentions"]) == 1
        m = data["mentions"][0]
        assert m["entity_id"] == "e1"
        assert m["document_id"] == "doc-1"
        assert m["text_span"] == "Aspirin"

    def test_get_edge_evidence_returns_evidence(self, client_with_mentions_evidence):
        """GET /edge/evidence returns evidence rows when bundle had evidence.jsonl."""
        response = client_with_mentions_evidence.get(
            "/api/v1/graph/edge/evidence",
            params={"subject_id": "e1", "predicate": "treats", "object_id": "e2"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "evidence" in data
        assert len(data["evidence"]) == 1
        e = data["evidence"][0]
        assert e["relationship_key"] == "e1:treats:e2"
        assert e["text_span"] == "Aspirin treats headache."

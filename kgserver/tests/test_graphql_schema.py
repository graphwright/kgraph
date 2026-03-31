"""
Tests for GraphQL schema queries and types.

Tests cover:
- Entity queries (by ID, list with pagination and filtering)
- Relationship queries (by triple, list with pagination and filtering)
- Bundle introspection query
- Pagination types and metadata
- Filter functionality
- Max limit enforcement
"""


def execute_query(schema, query: str, context: dict):
    """Helper to execute a GraphQL query."""
    result = schema.execute_sync(query, context_value=context)
    if result.errors:
        raise RuntimeError(f"GraphQL errors: {result.errors}")  # pylint: disable=broad-exception-raised
    return result.data


class TestEntityQueries:
    """Test entity-related GraphQL queries."""

    def test_entity_by_id(self, graphql_schema, graphql_context):
        """Test retrieving a single entity by ID."""
        query = """
        query {
            entity(id: "test:entity:1") {
                entityId
                name
                entityType
                status
                confidence
                usageCount
                source
                synonyms
                properties
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        assert result["entity"] is not None
        assert result["entity"]["entityId"] == "test:entity:1"
        assert result["entity"]["name"] == "Test Character 1"
        assert result["entity"]["entityType"] == "character"
        assert result["entity"]["status"] == "canonical"
        assert result["entity"]["confidence"] == 0.95
        assert result["entity"]["usageCount"] == 10
        assert result["entity"]["source"] == "test"
        assert len(result["entity"]["synonyms"]) == 2

    def test_entity_not_found(self, graphql_schema, graphql_context):
        """Test querying for non-existent entity."""
        query = """
        query {
            entity(id: "nonexistent:entity") {
                entityId
                name
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)
        assert result["entity"] is None

    def test_entities_pagination(self, graphql_schema, graphql_context):
        """Test entities query with pagination."""
        query = """
        query {
            entities(limit: 2, offset: 0) {
                items {
                    entityId
                    name
                }
                total
                limit
                offset
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        assert result["entities"]["total"] == 3
        assert result["entities"]["limit"] == 2
        assert result["entities"]["offset"] == 0
        assert len(result["entities"]["items"]) == 2

    def test_entities_pagination_offset(self, graphql_schema, graphql_context):
        """Test entities query with offset."""
        query = """
        query {
            entities(limit: 2, offset: 1) {
                items {
                    entityId
                }
                total
                limit
                offset
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        assert result["entities"]["total"] == 3
        assert result["entities"]["limit"] == 2
        assert result["entities"]["offset"] == 1
        assert len(result["entities"]["items"]) == 2
        # Should skip first entity (ordered by usage_count DESC, so entity:3 is first)
        assert result["entities"]["items"][0]["entityId"] != "test:entity:3"

    def test_entities_filter_by_type(self, graphql_schema, graphql_context):
        """Test filtering entities by entity type."""
        query = """
        query {
            entities(limit: 10, filter: { entityType: "character" }) {
                items {
                    entityId
                    entityType
                }
                total
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        assert result["entities"]["total"] == 2
        assert len(result["entities"]["items"]) == 2
        for item in result["entities"]["items"]:
            assert item["entityType"] == "character"

    def test_entities_filter_by_name(self, graphql_schema, graphql_context):
        """Test filtering entities by exact name."""
        query = """
        query {
            entities(limit: 10, filter: { name: "Test Character 1" }) {
                items {
                    entityId
                    name
                }
                total
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        assert result["entities"]["total"] == 1
        assert result["entities"]["items"][0]["name"] == "Test Character 1"

    def test_entities_filter_name_contains(self, graphql_schema, graphql_context):
        """Test filtering entities by name containing string."""
        query = """
        query {
            entities(limit: 10, filter: { nameContains: "Character" }) {
                items {
                    entityId
                    name
                }
                total
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        assert result["entities"]["total"] == 2
        for item in result["entities"]["items"]:
            assert "Character" in item["name"]

    def test_entities_filter_by_source(self, graphql_schema, graphql_context):
        """Test filtering entities by source."""
        query = """
        query {
            entities(limit: 10, filter: { source: "test" }) {
                items {
                    entityId
                    source
                }
                total
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        assert result["entities"]["total"] == 3
        for item in result["entities"]["items"]:
            assert item["source"] == "test"

    def test_entities_filter_by_status(self, graphql_schema, graphql_context):
        """Test filtering entities by status."""
        query = """
        query {
            entities(limit: 10, filter: { status: "canonical" }) {
                items {
                    entityId
                    status
                }
                total
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        assert result["entities"]["total"] == 3
        for item in result["entities"]["items"]:
            assert item["status"] == "canonical"

    def test_entities_filter_combined(self, graphql_schema, graphql_context):
        """Test combining multiple filters."""
        query = """
        query {
            entities(limit: 10, filter: {
                entityType: "character"
                nameContains: "1"
            }) {
                items {
                    entityId
                    name
                }
                total
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        assert result["entities"]["total"] == 1
        assert result["entities"]["items"][0]["entityId"] == "test:entity:1"

    def test_entities_max_limit_enforcement(self, graphql_schema, graphql_context, monkeypatch):
        """Test that max limit is enforced."""
        import query.graphql_schema as gql_module

        original_max = gql_module.MAX_LIMIT
        gql_module.MAX_LIMIT = 5  # Set low for testing

        query = """
        query {
            entities(limit: 100) {
                limit
                items {
                    entityId
                }
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        # Limit should be capped at MAX_LIMIT
        assert result["entities"]["limit"] == 5

        # Restore original
        gql_module.MAX_LIMIT = original_max


class TestRelationshipQueries:
    """Test relationship-related GraphQL queries."""

    def test_relationship_by_triple(self, graphql_schema, graphql_context):
        """Test retrieving a single relationship by triple."""
        query = """
        query {
            relationship(
                subjectId: "test:entity:1"
                predicate: "co_occurs_with"
                objectId: "test:entity:2"
            ) {
                subjectId
                predicate
                objectId
                confidence
                sourceDocuments
                properties
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        assert result["relationship"] is not None
        assert result["relationship"]["subjectId"] == "test:entity:1"
        assert result["relationship"]["predicate"] == "co_occurs_with"
        assert result["relationship"]["objectId"] == "test:entity:2"
        assert result["relationship"]["confidence"] == 0.85
        assert len(result["relationship"]["sourceDocuments"]) == 2

    def test_relationship_not_found(self, graphql_schema, graphql_context):
        """Test querying for non-existent relationship."""
        query = """
        query {
            relationship(
                subjectId: "nonexistent"
                predicate: "test"
                objectId: "also_nonexistent"
            ) {
                subjectId
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)
        assert result["relationship"] is None

    def test_relationships_pagination(self, graphql_schema, graphql_context):
        """Test relationships query with pagination."""
        query = """
        query {
            relationships(limit: 2, offset: 0) {
                items {
                    subjectId
                    predicate
                    objectId
                }
                total
                limit
                offset
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        assert result["relationships"]["total"] == 3
        assert result["relationships"]["limit"] == 2
        assert result["relationships"]["offset"] == 0
        assert len(result["relationships"]["items"]) == 2

    def test_relationships_filter_by_subject(self, graphql_schema, graphql_context):
        """Test filtering relationships by subject ID."""
        query = """
        query {
            relationships(limit: 10, filter: { subjectId: "test:entity:1" }) {
                items {
                    subjectId
                    predicate
                    objectId
                }
                total
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        assert result["relationships"]["total"] == 2
        for item in result["relationships"]["items"]:
            assert item["subjectId"] == "test:entity:1"

    def test_relationships_filter_by_object(self, graphql_schema, graphql_context):
        """Test filtering relationships by object ID."""
        query = """
        query {
            relationships(limit: 10, filter: { objectId: "test:entity:3" }) {
                items {
                    subjectId
                    objectId
                }
                total
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        assert result["relationships"]["total"] == 2
        for item in result["relationships"]["items"]:
            assert item["objectId"] == "test:entity:3"

    def test_relationships_filter_by_predicate(self, graphql_schema, graphql_context):
        """Test filtering relationships by predicate."""
        query = """
        query {
            relationships(limit: 10, filter: { predicate: "co_occurs_with" }) {
                items {
                    predicate
                }
                total
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        assert result["relationships"]["total"] == 2
        for item in result["relationships"]["items"]:
            assert item["predicate"] == "co_occurs_with"

    def test_relationships_filter_combined(self, graphql_schema, graphql_context):
        """Test combining multiple relationship filters."""
        query = """
        query {
            relationships(limit: 10, filter: {
                subjectId: "test:entity:1"
                predicate: "co_occurs_with"
            }) {
                items {
                    subjectId
                    predicate
                    objectId
                }
                total
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        assert result["relationships"]["total"] == 1
        item = result["relationships"]["items"][0]
        assert item["subjectId"] == "test:entity:1"
        assert item["predicate"] == "co_occurs_with"

    def test_relationships_max_limit_enforcement(self, graphql_schema, graphql_context, monkeypatch):
        """Test that max limit is enforced for relationships."""
        import query.graphql_schema as gql_module

        original_max = gql_module.MAX_LIMIT
        gql_module.MAX_LIMIT = 5  # Set low for testing

        query = """
        query {
            relationships(limit: 100) {
                limit
                items {
                    subjectId
                }
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        # Limit should be capped at MAX_LIMIT
        assert result["relationships"]["limit"] == 5

        # Restore original
        gql_module.MAX_LIMIT = original_max


class TestBundleQuery:
    """Test bundle introspection query."""

    def test_bundle_query(self, graphql_schema, storage_with_bundle):
        """Test bundle introspection query."""
        context = {"storage": storage_with_bundle}
        query = """
        query {
            bundle {
                bundleId
                domain
                createdAt
                metadata
            }
        }
        """
        result = execute_query(graphql_schema, query, context)

        assert result["bundle"] is not None
        assert result["bundle"]["bundleId"] == "test-bundle-123"
        assert result["bundle"]["domain"] == "test"
        assert result["bundle"]["createdAt"] is not None

    def test_bundle_query_no_bundle(self, graphql_schema, graphql_context):
        """Test bundle query when no bundle is loaded."""
        query = """
        query {
            bundle {
                bundleId
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)
        assert result["bundle"] is None


class TestFieldNaming:
    """Test that GraphQL field names use camelCase."""

    def test_entity_camelcase_fields(self, graphql_schema, graphql_context):
        """Test that entity fields are camelCase in GraphQL."""
        query = """
        query {
            entity(id: "test:entity:1") {
                entityId
                entityType
                usageCount
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        # Verify camelCase field names work
        assert result["entity"]["entityId"] == "test:entity:1"
        assert result["entity"]["entityType"] == "character"
        assert result["entity"]["usageCount"] == 10

    def test_relationship_camelcase_fields(self, graphql_schema, graphql_context):
        """Test that relationship fields are camelCase in GraphQL."""
        query = """
        query {
            relationship(
                subjectId: "test:entity:1"
                predicate: "co_occurs_with"
                objectId: "test:entity:2"
            ) {
                subjectId
                objectId
                sourceDocuments
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        # Verify camelCase field names work
        assert result["relationship"]["subjectId"] == "test:entity:1"
        assert result["relationship"]["objectId"] == "test:entity:2"
        assert len(result["relationship"]["sourceDocuments"]) == 2

    def test_relationship_id_field(self, graphql_schema, graphql_context):
        """Test that relationship id field is exposed and is a string (UUID)."""
        query = """
        query {
            relationship(
                subjectId: "test:entity:1"
                predicate: "co_occurs_with"
                objectId: "test:entity:2"
            ) {
                id
                subjectId
                predicate
                objectId
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        assert "id" in result["relationship"]
        assert isinstance(result["relationship"]["id"], str)
        assert result["relationship"]["subjectId"] == "test:entity:1"
        assert result["relationship"]["objectId"] == "test:entity:2"


class TestPaginationMetadata:
    """Test pagination metadata correctness."""

    def test_entities_pagination_metadata(self, graphql_schema, graphql_context):
        """Test that pagination metadata is correct."""
        query = """
        query {
            entities(limit: 1, offset: 1) {
                items {
                    entityId
                }
                total
                limit
                offset
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        page = result["entities"]
        assert page["total"] == 3  # Total entities
        assert page["limit"] == 1  # Requested limit
        assert page["offset"] == 1  # Requested offset
        assert len(page["items"]) == 1  # Actual items returned

    def test_relationships_pagination_metadata(self, graphql_schema, graphql_context):
        """Test that relationship pagination metadata is correct."""
        query = """
        query {
            relationships(limit: 2, offset: 1) {
                items {
                    subjectId
                }
                total
                limit
                offset
            }
        }
        """
        result = execute_query(graphql_schema, query, graphql_context)

        page = result["relationships"]
        assert page["total"] == 3  # Total relationships
        assert page["limit"] == 2  # Requested limit
        assert page["offset"] == 1  # Requested offset
        assert len(page["items"]) == 2  # Actual items returned

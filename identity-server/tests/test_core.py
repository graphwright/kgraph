"""Tests for PostgresIdentityServer (identity_server/core.py).

Uses SQLite in-memory (via the session fixture from conftest.py) for
portability — SQLModel works with SQLite for all non-Postgres-specific
operations.  Advisory locks and ON CONFLICT are skipped/adapted in SQLite:
  - pg_advisory_xact_lock is not available; merge tests that need it are
    tested at the logic level with a pre-existing DB state.
  - ON CONFLICT DO NOTHING falls back gracefully in SQLite (different syntax;
    we test the resolve semantics instead).

Tests cover:
  - resolve creates a provisional entity when no authority match is found
  - resolve returns the existing entity_id for a repeated mention
  - resolve returns canonical entity_id when domain client finds a match
  - resolve redirects through merged entities
  - promote is a no-op on a canonical entity
  - promote handles merged entity (returns survivor)
  - merge marks absorbed entities as MERGED and sets merged_into
  - merge raises ValueError when survivor_id is not in entity_ids
  - find_synonyms returns empty list when entity has no embedding
  - find_synonyms returns matching entities above similarity threshold
  - on_entity_added triggers merge when synonyms are detected
"""

from unittest.mock import AsyncMock

import pytest
from sqlmodel import select

from identity_server.core import EntityStatus, PostgresIdentityServer, _cosine_similarity
from identity_server.db_models import Entity
from identity_server.models import DomainCanonicalId

# ---------------------------------------------------------------------------
# Helper to insert an entity row directly
# ---------------------------------------------------------------------------


def _insert_entity(session, entity_id, name, entity_type, status=EntityStatus.PROVISIONAL.value, usage_count=1, confidence=1.0, merged_into=None, embedding=None):
    entity = Entity(entity_id=entity_id, entity_type=entity_type, name=name, status=status, usage_count=usage_count, confidence=confidence, merged_into=merged_into, embedding=embedding)
    session.add(entity)
    session.commit()
    session.refresh(entity)
    return entity


# ---------------------------------------------------------------------------
# _cosine_similarity unit tests
# ---------------------------------------------------------------------------


def test_cosine_similarity_identical():
    """Cosine similarity of a vector with itself is 1.0."""
    v = [1.0, 0.0, 0.0]
    assert _cosine_similarity(v, v) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal():
    """Orthogonal vectors have cosine similarity of 0.0."""
    assert _cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_cosine_similarity_zero_vector():
    """Zero vector produces 0.0 (no division by zero)."""
    assert _cosine_similarity([0.0, 0.0], [1.0, 2.0]) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# resolve — creates provisional entity
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_creates_provisional_entity(session, mock_domain_client):
    """Resolve creates a new provisional entity when no authority match is found."""
    server = PostgresIdentityServer(session=session, domain_client=mock_domain_client)
    entity_id = await server.resolve(mention="aspirin", entity_type="drug", document_id="doc-001")

    assert entity_id.startswith("prov:")
    row = session.exec(select(Entity).where(Entity.entity_id == entity_id)).first()
    assert row is not None
    assert row.name == "aspirin"
    assert row.entity_type == "drug"
    assert row.status == EntityStatus.PROVISIONAL.value


# ---------------------------------------------------------------------------
# resolve — returns existing entity on repeat call
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_returns_existing_entity(session, mock_domain_client):
    """Resolving the same mention twice returns the same entity ID."""
    server = PostgresIdentityServer(session=session, domain_client=mock_domain_client)
    id1 = await server.resolve(mention="ibuprofen", entity_type="drug", document_id="doc-001")
    id2 = await server.resolve(mention="ibuprofen", entity_type="drug", document_id="doc-002")
    assert id1 == id2


# ---------------------------------------------------------------------------
# resolve — canonical entity when domain client returns a canonical ID
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_returns_canonical_when_authority_found(session, mock_domain_client):
    """When the domain client returns a canonical ID, the entity is inserted as canonical."""
    mock_domain_client.resolve_authority = AsyncMock(return_value=DomainCanonicalId(id="UMLS:C001", url="http://umls.example/C001", synonyms=("aspirin",)))

    server = PostgresIdentityServer(session=session, domain_client=mock_domain_client)
    entity_id = await server.resolve(mention="aspirin", entity_type="drug", document_id="doc-001")

    assert entity_id == "UMLS:C001"
    row = session.exec(select(Entity).where(Entity.entity_id == entity_id)).first()
    assert row is not None
    assert row.status == EntityStatus.CANONICAL.value


# ---------------------------------------------------------------------------
# resolve — redirects through merged entity
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolve_redirects_merged_entity(session, mock_domain_client):
    """When the existing row is merged, resolve returns the survivor ID."""
    _insert_entity(session, "prov:old", "metformin", "drug", status=EntityStatus.MERGED.value, merged_into="prov:survivor")
    _insert_entity(session, "prov:survivor", "metformin", "drug", status=EntityStatus.PROVISIONAL.value)

    # The name+type match maps to "prov:old" which is merged — expect survivor.
    server = PostgresIdentityServer(session=session, domain_client=mock_domain_client)
    result = await server.resolve(mention="metformin", entity_type="drug", document_id="doc-001")
    assert result == "prov:survivor"


# ---------------------------------------------------------------------------
# promote — no-op on canonical
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_promote_noop_on_canonical(session, mock_domain_client):
    """Promoting a canonical entity is a no-op that returns the same ID."""
    _insert_entity(session, "UMLS:C001", "aspirin", "drug", status=EntityStatus.CANONICAL.value)

    server = PostgresIdentityServer(session=session, domain_client=mock_domain_client)
    result = await server.promote("UMLS:C001")
    assert result == "UMLS:C001"
    # Domain client must not be called for canonical entities.
    mock_domain_client.resolve_authority.assert_not_called()


# ---------------------------------------------------------------------------
# promote — merged entity returns survivor
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_promote_merged_entity_returns_survivor(session, mock_domain_client):
    """Promoting a merged entity logs a warning and returns the survivor ID."""
    _insert_entity(session, "prov:old", "aspirin", "drug", status=EntityStatus.MERGED.value, merged_into="prov:survivor")

    server = PostgresIdentityServer(session=session, domain_client=mock_domain_client)
    result = await server.promote("prov:old")
    assert result == "prov:survivor"


# ---------------------------------------------------------------------------
# promote — provisional entity with no authority match stays provisional
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_promote_provisional_no_authority_stays_provisional(session, mock_domain_client):
    """Promoting a provisional entity stays provisional when no canonical ID is returned."""
    _insert_entity(session, "prov:abc", "unknown-drug", "drug", status=EntityStatus.PROVISIONAL.value)
    mock_domain_client.resolve_authority = AsyncMock(return_value=None)

    server = PostgresIdentityServer(session=session, domain_client=mock_domain_client)
    result = await server.promote("prov:abc")
    assert result == "prov:abc"


# ---------------------------------------------------------------------------
# merge — basic merge marks absorbed as MERGED
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_merge_marks_absorbed_entities(session, mock_domain_client):
    """Merge marks the absorbed entity as MERGED with merged_into set to survivor."""
    _insert_entity(session, "prov:A", "aspirin", "drug")
    _insert_entity(session, "prov:B", "aspirin alt", "drug")

    server = PostgresIdentityServer(session=session, domain_client=mock_domain_client)

    # SQLite does not have pg_advisory_xact_lock; patch it to be a no-op.
    original_execute = session.execute

    def patched_execute(statement, *args, **kwargs):
        stmt_str = str(statement) if hasattr(statement, "__str__") else ""
        if "pg_advisory_xact_lock" in stmt_str:
            return None
        if "relationship" in stmt_str:
            return None  # no relationship table in SQLite test DB
        return original_execute(statement, *args, **kwargs)

    session.execute = patched_execute

    try:
        survivor_id = await server.merge(entity_ids=["prov:A", "prov:B"], survivor_id="prov:A")
    finally:
        session.execute = original_execute

    assert survivor_id == "prov:A"
    absorbed = session.exec(select(Entity).where(Entity.entity_id == "prov:B")).first()
    assert absorbed is not None
    assert absorbed.status == EntityStatus.MERGED.value
    assert absorbed.merged_into == "prov:A"


# ---------------------------------------------------------------------------
# merge — raises ValueError when survivor_id not in entity_ids
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_merge_raises_when_survivor_not_in_entity_ids(session, mock_domain_client):
    """merge() raises ValueError if survivor_id is not a member of entity_ids."""
    server = PostgresIdentityServer(session=session, domain_client=mock_domain_client)
    with pytest.raises(ValueError, match="survivor_id"):
        await server.merge(entity_ids=["prov:A", "prov:B"], survivor_id="prov:C")


# ---------------------------------------------------------------------------
# merge — single-element list is a no-op
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_merge_single_entity_is_noop(session, mock_domain_client):
    """Merging a single entity into itself returns survivor_id immediately."""
    server = PostgresIdentityServer(session=session, domain_client=mock_domain_client)
    result = await server.merge(entity_ids=["prov:solo"], survivor_id="prov:solo")
    assert result == "prov:solo"


# ---------------------------------------------------------------------------
# find_synonyms — empty when no embedding
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_find_synonyms_empty_without_embedding(session, mock_domain_client):
    """find_synonyms returns an empty list when the entity has no embedding."""
    _insert_entity(session, "prov:E1", "aspirin", "drug")

    server = PostgresIdentityServer(session=session, domain_client=mock_domain_client)
    result = await server.find_synonyms("prov:E1")
    assert result == []


# ---------------------------------------------------------------------------
# find_synonyms — returns matches above threshold
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_find_synonyms_returns_similar_entities(session, mock_domain_client):
    """find_synonyms returns entities whose cosine similarity exceeds the threshold."""
    vec_a = [1.0, 0.0, 0.0]
    vec_b = [0.999, 0.001, 0.0]  # nearly identical — above 0.90 threshold
    vec_c = [0.0, 1.0, 0.0]  # orthogonal — below threshold

    _insert_entity(session, "prov:A", "aspirin", "drug", embedding=vec_a)
    _insert_entity(session, "prov:B", "aspirin-b", "drug", embedding=vec_b)
    _insert_entity(session, "prov:C", "aspirin-c", "drug", embedding=vec_c)

    mock_domain_client.synonym_criteria = AsyncMock(return_value=0.90)

    server = PostgresIdentityServer(session=session, domain_client=mock_domain_client)
    result = await server.find_synonyms("prov:A")
    assert "prov:B" in result
    assert "prov:C" not in result


# ---------------------------------------------------------------------------
# on_entity_added — triggers merge when synonyms detected
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_on_entity_added_merges_synonyms(session, mock_domain_client):
    """on_entity_added triggers merge when synonym candidates are found."""
    vec_a = [1.0, 0.0, 0.0]
    vec_b = [0.999, 0.001, 0.0]

    _insert_entity(session, "prov:A", "drug-a", "drug", embedding=vec_a)
    _insert_entity(session, "prov:B", "drug-b", "drug", embedding=vec_b)

    mock_domain_client.synonym_criteria = AsyncMock(return_value=0.90)
    # select_survivor picks prov:A
    mock_domain_client.select_survivor = AsyncMock(return_value="prov:A")

    server = PostgresIdentityServer(session=session, domain_client=mock_domain_client)

    # Patch advisory lock and relationship table calls (not available in SQLite test DB)
    original_execute = session.execute

    def patched_execute(statement, *args, **kwargs):
        stmt_str = str(statement) if hasattr(statement, "__str__") else ""
        if "pg_advisory_xact_lock" in stmt_str:
            return None
        if "relationship" in stmt_str:
            return None  # no relationship table in SQLite test DB
        return original_execute(statement, *args, **kwargs)

    session.execute = patched_execute
    try:
        await server.on_entity_added("prov:A", {})
    finally:
        session.execute = original_execute

    absorbed = session.exec(select(Entity).where(Entity.entity_id == "prov:B")).first()
    assert absorbed is not None
    assert absorbed.status == EntityStatus.MERGED.value
    assert absorbed.merged_into == "prov:A"

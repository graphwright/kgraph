"""Shared pytest fixtures for the identity server test suite.

Fixtures provided
-----------------
engine
    SQLite in-memory engine with all tables created.
session
    Open SQLModel Session bound to the in-memory engine.  Rolled back after
    each test to keep tests independent.
mock_domain_client
    A ``DomainClient`` instance whose HTTP methods are replaced with
    ``unittest.mock.AsyncMock`` so tests can control domain service responses
    without a real network connection.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

# Import db_models to register the Entity table with SQLModel metadata before
# create_all is called.
from identity_server import db_models  # noqa: F401  (side-effect import)
from identity_server.domain_client import DomainClient


@pytest.fixture(name="engine")
def engine_fixture():
    """SQLite in-memory engine with all identity server tables created.

    StaticPool ensures all connections (including those made inside FastAPI's
    thread-pool for sync endpoints) share the same in-memory database, so
    tables created here are visible to every connection throughout the test.
    """
    _engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(_engine)
    yield _engine
    SQLModel.metadata.drop_all(_engine)


@pytest.fixture(name="session")
def session_fixture(engine):
    """Open SQLModel Session.  Each test gets a fresh, isolated session."""
    with Session(engine) as _session:
        yield _session


@pytest.fixture(name="mock_domain_client")
def mock_domain_client_fixture():
    """DomainClient with all async methods replaced by AsyncMock.

    Default behaviour (can be overridden per-test):
      - resolve_authority → None  (no canonical ID found)
      - select_survivor   → first candidate's entity_id
      - synonym_criteria  → 0.90
    """
    client = MagicMock(spec=DomainClient)
    client.resolve_authority = AsyncMock(return_value=None)
    client.select_survivor = AsyncMock(side_effect=lambda candidates: candidates[0].entity_id)
    client.synonym_criteria = AsyncMock(return_value=0.90)
    return client

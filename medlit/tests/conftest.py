"""Conftest for medlit tests — provides shared fixtures."""

import pytest

from kgraph.storage.memory import (
    InMemoryDocumentStorage,
    InMemoryEntityStorage,
    InMemoryRelationshipStorage,
)


@pytest.fixture
def entity_storage() -> InMemoryEntityStorage:
    """Provide a fresh in-memory entity storage instance."""
    return InMemoryEntityStorage()


@pytest.fixture
def relationship_storage() -> InMemoryRelationshipStorage:
    """Provide a fresh in-memory relationship storage instance."""
    return InMemoryRelationshipStorage()


@pytest.fixture
def document_storage() -> InMemoryDocumentStorage:
    """Provide a fresh in-memory document storage instance."""
    return InMemoryDocumentStorage()

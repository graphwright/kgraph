"""
Storage layer for medical literature knowledge graph.

This package provides a clean abstraction for data persistence, separating
infrastructure concerns from domain logic.

Key Components:

- **interfaces**: Abstract base classes defining storage contracts
- **backends**: Concrete implementations (SQLite, PostgreSQL)
- **models**: SQLModel schemas for database persistence

Example:

    >>> from storage.interfaces import StorageInterface
    >>> from storage.backends.sqlite import SQLiteStorage
    >>>
    >>> # Create an in-memory SQLite storage
    >>> storage = SQLiteStorage(":memory:")
    >>>
    >>> # Add entities, papers, relationships
    >>> storage.entities.add_disease(disease)
    >>> storage.add_paper(paper)
    >>> storage.add_relationship(relationship)

For more information, see the README.md in this directory.
"""

from storage.backends.identity import AuthorityCache, PostgresIdentityServer

__all__ = [
    "interfaces",
    "backends",
    "models",
    "AuthorityCache",
    "PostgresIdentityServer",
]

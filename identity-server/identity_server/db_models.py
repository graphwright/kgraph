"""
Generic Entity ORM model for the identity server.

Adapted from kgraph/kgserver/storage/models/entity.py.
"""

from typing import Any, List, Optional

from sqlmodel import JSON, Column, Field, SQLModel


class Entity(SQLModel, table=True):
    """
    A generic entity in the knowledge graph.
    """

    __tablename__ = "entity"

    entity_id: str = Field(primary_key=True)
    entity_type: str = Field(index=True)
    name: Optional[str] = Field(default=None, index=True)
    status: Optional[str] = Field(default=None)
    confidence: Optional[float] = Field(default=None)
    usage_count: Optional[int] = Field(default=None)
    source: Optional[str] = Field(default=None)
    canonical_url: Optional[str] = Field(default=None, description="URL to the authoritative source for this entity")
    synonyms: List[str] = Field(default=[], sa_column=Column(JSON))
    properties: dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    merged_into: Optional[str] = Field(
        default=None,
        description="If status='merged', the entity_id of the survivor. NULL otherwise.",
    )
    embedding: Optional[List[float]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Semantic embedding vector for pgvector similarity search.",
    )

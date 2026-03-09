"""
Knowledge Graph Schema - Base Models and Interfaces

This package contains only Pydantic models and ABC interfaces with no
functional code. It defines:

- Entity, relationship, and document base classes
- Domain schema interface
- Storage interfaces
- Canonical ID model
- Promotion policy interface

These are used by both kgraph (ingestion) and can be referenced by
domain implementations.
"""

from kgschema.canonical_id import CanonicalId
from kgschema.document import BaseDocument
from kgschema.spec import EntitySpec, EvidenceSpec, MentionsSpec, PredicateSpec
from kgschema.domain import DomainSchema
from kgschema.entity import BaseEntity, EntityMention, EntityStatus, PromotionConfig
from kgschema.promotion import PromotionPolicy
from kgschema.relationship import BaseRelationship
from kgschema.storage import (
    DocumentStorageInterface,
    EntityStorageInterface,
    RelationshipStorageInterface,
)

__all__ = [
    "EntitySpec",
    "EvidenceSpec",
    "MentionsSpec",
    "PredicateSpec",
    "BaseDocument",
    "BaseEntity",
    "BaseRelationship",
    "CanonicalId",
    "DocumentStorageInterface",
    "DomainSchema",
    "EntityMention",
    "EntityStatus",
    "EntityStorageInterface",
    "PromotionConfig",
    "PromotionPolicy",
    "RelationshipStorageInterface",
]

__version__ = "0.1.0"

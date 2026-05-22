"""Sherlock Holmes entity types.

All entity classes import their spec from domain_spec.py (single source of truth).
They are re-exported here for convenience.
"""

from .domain_spec import (
    CharacterEntity,
    EventEntity,
    LocationEntity,
    OccupationEntity,
    OrganizationEntity,
    PhysicalObjectEntity,
    StoryEntity,
)

__all__ = [
    "CharacterEntity",
    "EventEntity",
    "LocationEntity",
    "OccupationEntity",
    "OrganizationEntity",
    "PhysicalObjectEntity",
    "StoryEntity",
]

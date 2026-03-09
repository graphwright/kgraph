"""Domain spec models for entity types, predicates, evidence, and mentions.

Used by domain_spec.py modules to define schema in Python as single source of truth.
"""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class EntitySpec(BaseModel):
    """Display and prompt metadata for an entity type."""

    model_config = ConfigDict(frozen=True)

    description: str = Field(description="Short definition for schema/prompt")
    prompt_guidance: str = Field(default="", description="Richer prompt text for extraction")
    color: str = Field(default="#78909c", description="Hex color for graph-viz")
    label: str = Field(description="Display name (e.g. 'Disease')")


class PredicateSpec(BaseModel):
    """Validity and dedup metadata for a predicate.

    subject_types/object_types: when None, means any entity type.
    specificity: for dedup; higher = prefer when (s,o) has multiple predicates.
    """

    model_config = ConfigDict(frozen=True)

    description: str = Field(description="Predicate definition")
    subject_types: Optional[list[type]] = Field(
        default=None,
        description="Entity classes valid as subject. None = any.",
    )
    object_types: Optional[list[type]] = Field(
        default=None,
        description="Entity classes valid as object. None = any.",
    )
    specificity: int = Field(default=0, description="Dedup priority; higher = prefer")


class EvidenceSpec(BaseModel):
    """Evidence ID format and extraction methods."""

    model_config = ConfigDict(frozen=True)

    id_format: str = Field(description="Format string for evidence IDs")
    methods: list[str] = Field(default_factory=lambda: ["llm"])
    section_names: list[str] = Field(default_factory=list)


class MentionsSpec(BaseModel):
    """Rules for entity mention extraction."""

    model_config = ConfigDict(frozen=True)

    mentionable_types: list[type] = Field(description="Entity classes that produce mentions")
    skip_name_equals_type: bool = Field(default=True)

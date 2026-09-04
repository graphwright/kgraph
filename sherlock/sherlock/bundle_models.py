"""Pydantic models for the per-story bundle JSON (Pass 1 output / Pass 2 input).

Mirrors medlit's bundle_models.py but adapted for fiction:
- StoryInfo instead of PaperInfo
- NarratorTrust and story_time fields on RelationshipRow (Sherlock-specific epistemic metadata)
- Evidence IDs use {story_id}:{section}:{paragraph_idx}:{method}
"""

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Story metadata
# ---------------------------------------------------------------------------


class StoryInfo(BaseModel):
    """Metadata for a Sherlock Holmes story."""

    story_id: str
    "Stable short identifier, e.g. 'scandal_in_bohemia'."

    title: str = ""
    "Full story title."

    collection: Optional[str] = None
    "Collection/book the story belongs to, e.g. 'Adventures of Sherlock Holmes'."

    author: str = "Arthur Conan Doyle"

    year: Optional[int] = None
    "Publication year."

    source_uri: Optional[str] = None
    "Project Gutenberg or other source URL."

    document_id: str = ""
    "Unique document ID used in evidence IDs."


# ---------------------------------------------------------------------------
# Entity rows
# ---------------------------------------------------------------------------


class ExtractedEntityRow(BaseModel):
    """Minimal entity record in the story bundle. JSON key 'class' via alias."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    entity_class: str = Field(alias="class", description="Entity type, e.g. Character, Location, PhysicalObject")
    name: str
    synonyms: list[str] = Field(default_factory=list)
    canonical_id: Optional[str] = None
    source: Literal["extracted", "curated"] = "extracted"
    description: Optional[str] = None
    "Short description from story context (e.g. 'operatic contralto and adventuress')."


class EvidenceEntityRow(BaseModel):
    """Evidence entity in the story bundle.

    id format: {story_id}:{section}:{paragraph_idx}:{method}
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    entity_class: Literal["Evidence"] = Field(default="Evidence", alias="class")
    entity_id: Optional[str] = None
    story_id: str
    section: Optional[str] = None
    paragraph_idx: Optional[int] = None
    text: Optional[str] = None
    confidence: float = 0.5
    extraction_method: str = "llm"
    source: Literal["extracted"] = "extracted"


# ---------------------------------------------------------------------------
# Relationship rows
# ---------------------------------------------------------------------------

NarratorTrustLiteral = Literal[
    "watson_direct",
    "watson_inference",
    "watson_speculation",
    "watson_retrospective",
    "holmes_assertion",
    "holmes_inference",
    "third_party",
    "narrator",
]

StoryTimeLiteral = Literal[
    "backstory",
    "before_crime",
    "day_of",
    "immediate_aftermath",
    "investigation",
    "revelation",
    "denouement",
    "unknown",
]


class ProvenanceEntry(BaseModel):
    """One provenance record for a relationship."""

    section: Optional[str] = None
    sentence: Optional[str] = None
    paragraph_idx: Optional[int] = None


class RelationshipRow(BaseModel):
    """One relationship in the story bundle."""

    model_config = ConfigDict(populate_by_name=True)

    subject: str
    predicate: str
    object_id: str = Field(alias="object", description="Object entity ID")
    evidence_ids: list[str] = Field(default_factory=list)
    provenance: list[ProvenanceEntry] = Field(default_factory=list)
    source_stories: list[str] = Field(default_factory=list)
    confidence: float = 0.5
    narrator_trust: Optional[NarratorTrustLiteral] = None
    story_time: Optional[StoryTimeLiteral] = None
    narrative_position: Optional[int] = None
    "Paragraph index in story order."
    known_by: Optional[list[str]] = None
    "Characters who knew this fact at narrative_position."
    properties: dict[str, Any] = Field(default_factory=dict)
    section: Optional[str] = None
    asserted_by: str = "llm"
    resolution: Optional[Literal["merged", "distinct"]] = None
    note: Optional[str] = None


# ---------------------------------------------------------------------------
# Top-level per-story bundle
# ---------------------------------------------------------------------------


class PerStoryBundle(BaseModel):
    """Per-story bundle: Pass 1 output and Pass 2 input."""

    story: StoryInfo
    entities: list[ExtractedEntityRow] = Field(default_factory=list)
    evidence_entities: list[EvidenceEntityRow] = Field(default_factory=list)
    relationships: list[RelationshipRow] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    def to_bundle_dict(self) -> dict:
        """Serialize for JSON with alias 'class' used for entity type."""
        return self.model_dump(mode="json", by_alias=True)

    @classmethod
    def from_bundle_dict(cls, data: dict) -> "PerStoryBundle":
        """Load from dict/JSON (accepts key 'class' for entity type)."""
        return cls.model_validate(data)

"""Tests for bundle_models — serialization, Pydantic validation, etc."""

from sherlock.bundle_models import (
    EvidenceEntityRow,
    ExtractedEntityRow,
    PerStoryBundle,
    RelationshipRow,
    StoryInfo,
)


def test_story_info_defaults():
    info = StoryInfo(story_id="test", title="Test Story")
    assert info.author == "Arthur Conan Doyle"
    assert info.year is None


def test_extracted_entity_row_alias():
    """entity_class must be serialized as 'class' via alias."""
    row = ExtractedEntityRow(id="x", **{"class": "Character"}, name="Holmes")
    d = row.model_dump(by_alias=True)
    assert "class" in d
    assert d["class"] == "Character"
    assert "entity_class" not in d


def test_extracted_entity_row_roundtrip():
    """ExtractedEntityRow must survive serialization round-trip."""
    row = ExtractedEntityRow(id="x", **{"class": "Character"}, name="Holmes", synonyms=["Holmes"])
    d = row.model_dump(by_alias=True)
    restored = ExtractedEntityRow.model_validate(d)
    assert restored.name == "Holmes"
    assert restored.entity_class == "Character"


def test_relationship_row_alias():
    """object_id must serialize as 'object' via alias."""
    rel = RelationshipRow(subject="a", predicate="ALLY_OF", **{"object": "b"})
    d = rel.model_dump(by_alias=True)
    assert "object" in d
    assert d["object"] == "b"


def test_relationship_narrator_trust_valid():
    """narrator_trust must accept valid enum values."""
    for trust in ["watson_direct", "watson_inference", "holmes_assertion", "narrator"]:
        rel = RelationshipRow(subject="a", predicate="ALLY_OF", **{"object": "b"}, narrator_trust=trust)
        assert rel.narrator_trust == trust


def test_relationship_story_time_valid():
    """story_time must accept valid values."""
    for st in ["backstory", "investigation", "revelation", "unknown"]:
        rel = RelationshipRow(subject="a", predicate="TEST", **{"object": "b"}, story_time=st)
        assert rel.story_time == st


def test_evidence_entity_row_class_literal():
    """Evidence entity_class must be 'Evidence'."""
    ev = EvidenceEntityRow(id="ev1", story_id="test", **{"class": "Evidence"})
    assert ev.entity_class == "Evidence"


def test_per_story_bundle_roundtrip(story_info: StoryInfo, minimal_bundle: PerStoryBundle):
    """PerStoryBundle must survive to_bundle_dict/from_bundle_dict round-trip."""
    d = minimal_bundle.to_bundle_dict()
    restored = PerStoryBundle.from_bundle_dict(d)

    assert restored.story.story_id == minimal_bundle.story.story_id
    assert len(restored.entities) == len(minimal_bundle.entities)
    assert len(restored.relationships) == len(minimal_bundle.relationships)


def test_per_story_bundle_empty():
    """PerStoryBundle with no entities/rels must serialize without error."""
    info = StoryInfo(story_id="empty", title="Empty")
    bundle = PerStoryBundle(story=info)
    d = bundle.to_bundle_dict()
    assert d["entities"] == []
    assert d["relationships"] == []

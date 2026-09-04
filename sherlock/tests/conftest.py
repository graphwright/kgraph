"""Test fixtures for Sherlock Holmes pipeline tests."""

import pytest

from sherlock.bundle_models import (
    EvidenceEntityRow,
    ExtractedEntityRow,
    PerStoryBundle,
    RelationshipRow,
    StoryInfo,
)

STORY_ID = "scandal_in_bohemia"


@pytest.fixture
def story_info() -> StoryInfo:
    return StoryInfo(
        story_id=STORY_ID,
        title="A Scandal in Bohemia",
        collection="The Adventures of Sherlock Holmes",
        author="Arthur Conan Doyle",
        year=1891,
        document_id=STORY_ID,
    )


@pytest.fixture
def minimal_bundle(story_info: StoryInfo) -> PerStoryBundle:
    """A minimal bundle for testing dedup and builder."""
    entities = [
        ExtractedEntityRow(
            id="holmes",
            entity_class="Character",
            name="Sherlock Holmes",
            synonyms=["Holmes", "the detective"],
        ),
        ExtractedEntityRow(
            id="watson",
            entity_class="Character",
            name="Dr. Watson",
            synonyms=["Watson"],
        ),
        ExtractedEntityRow(
            id="irene",
            entity_class="Character",
            name="Irene Adler",
            synonyms=["the woman", "Miss Adler"],
        ),
        ExtractedEntityRow(
            id="scandal_story",
            entity_class="Story",
            name="A Scandal in Bohemia",
        ),
        ExtractedEntityRow(
            id="baker_street",
            entity_class="Location",
            name="221B Baker Street",
        ),
        ExtractedEntityRow(
            id="photograph",
            entity_class="PhysicalObject",
            name="The Photograph",
            synonyms=["the compromising photograph"],
        ),
    ]

    evidence = [
        EvidenceEntityRow(
            id=f"{STORY_ID}:opening:0:llm",
            entity_class="Evidence",
            story_id=STORY_ID,
            section="opening",
            paragraph_idx=0,
            text="To Sherlock Holmes she is always THE woman.",
            confidence=0.9,
        ),
    ]

    relationships = [
        RelationshipRow(
            subject="holmes",
            predicate="LIVES_AT",
            object_id="baker_street",
            evidence_ids=[f"{STORY_ID}:opening:0:llm"],
            confidence=0.9,
            narrator_trust="watson_direct",
            story_time="backstory",
        ),
        RelationshipRow(
            subject="watson",
            predicate="ALLY_OF",
            object_id="holmes",
            evidence_ids=[f"{STORY_ID}:opening:0:llm"],
            confidence=0.9,
            narrator_trust="watson_direct",
            story_time="backstory",
        ),
        RelationshipRow(
            subject="holmes",
            predicate="ANTAGONIST_OF",
            object_id="irene",
            evidence_ids=[f"{STORY_ID}:opening:0:llm"],
            confidence=0.7,
            narrator_trust="watson_retrospective",
            story_time="investigation",
        ),
        RelationshipRow(
            subject="irene",
            predicate="OWNS",
            object_id="photograph",
            evidence_ids=[f"{STORY_ID}:opening:0:llm"],
            confidence=0.9,
            narrator_trust="holmes_assertion",
            story_time="day_of",
        ),
        RelationshipRow(
            subject="holmes",
            predicate="APPEARS_IN",
            object_id="scandal_story",
            evidence_ids=[],
            confidence=1.0,
            narrator_trust="narrator",
            story_time="unknown",
        ),
    ]

    return PerStoryBundle(
        story=story_info,
        entities=entities,
        evidence_entities=evidence,
        relationships=relationships,
    )

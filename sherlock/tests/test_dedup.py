"""Tests for the dedup pipeline."""

from sherlock.bundle_models import ExtractedEntityRow, PerStoryBundle, RelationshipRow, StoryInfo
from sherlock.pipeline.dedup import _normalize_name, run_dedup


def test_normalize_name_aliases():
    """Key character aliases must normalize correctly."""
    assert _normalize_name("Watson") == "dr. watson"
    assert _normalize_name("Holmes") == "sherlock holmes"
    assert _normalize_name("the woman") == "irene adler"
    assert _normalize_name("the King") == "king of bohemia"
    assert _normalize_name("Count von Kramm") == "king of bohemia"


def test_same_as_resolution(minimal_bundle: PerStoryBundle):
    """SAME_AS edges must cause entity merges."""
    # Add a SAME_AS edge linking 'irene' to 'the_woman' alias entity
    story_info = minimal_bundle.story
    entities = list(minimal_bundle.entities) + [
        ExtractedEntityRow(
            id="the_woman",
            entity_class="Character",
            name="The Woman",
        )
    ]
    rels = list(minimal_bundle.relationships) + [
        RelationshipRow(
            subject="irene",
            predicate="SAME_AS",
            object_id="the_woman",
            confidence=1.0,
        )
    ]
    bundle_with_alias = PerStoryBundle(
        story=story_info,
        entities=entities,
        evidence_entities=minimal_bundle.evidence_entities,
        relationships=rels,
    )

    deduped = run_dedup(bundle_with_alias)

    # After dedup, 'the_woman' should be merged into 'irene' (or vice versa)
    entity_ids = {e.id for e in deduped.entities}
    # Both IDs should not be present — one of them merged
    assert not ("irene" in entity_ids and "the_woman" in entity_ids), "SAME_AS entities should have been merged"


def test_same_as_edges_removed(minimal_bundle: PerStoryBundle):
    """SAME_AS edges must not appear in deduped relationships."""
    story_info = minimal_bundle.story
    rels = list(minimal_bundle.relationships) + [
        RelationshipRow(
            subject="holmes",
            predicate="SAME_AS",
            object_id="watson",
            confidence=1.0,
        )
    ]
    bundle = PerStoryBundle(
        story=story_info,
        entities=minimal_bundle.entities,
        evidence_entities=minimal_bundle.evidence_entities,
        relationships=rels,
    )
    deduped = run_dedup(bundle)
    for rel in deduped.relationships:
        assert rel.predicate.upper() != "SAME_AS", "SAME_AS edges should be removed after merge"


def test_no_self_loops(minimal_bundle: PerStoryBundle):
    """Dedup must not produce self-loop relationships."""
    deduped = run_dedup(minimal_bundle)
    for rel in deduped.relationships:
        assert rel.subject != rel.object_id, f"Self-loop found: {rel.subject} --{rel.predicate}-> {rel.object_id}"


def test_entity_synonyms_merged(minimal_bundle: PerStoryBundle):
    """When two entity rows share a canonical ID (via SAME_AS), synonyms should be merged."""
    story_info = minimal_bundle.story
    entities = list(minimal_bundle.entities) + [
        ExtractedEntityRow(
            id="baker_street_alt",
            entity_class="Location",
            name="221B Baker Street",
            synonyms=["Holmes's lodgings"],
        )
    ]
    rels = list(minimal_bundle.relationships) + [
        RelationshipRow(
            subject="baker_street",
            predicate="SAME_AS",
            object_id="baker_street_alt",
            confidence=1.0,
        )
    ]
    bundle = PerStoryBundle(
        story=story_info,
        entities=entities,
        evidence_entities=minimal_bundle.evidence_entities,
        relationships=rels,
    )
    deduped = run_dedup(bundle)

    # The merged entity should have synonyms from both
    baker_entities = [e for e in deduped.entities if "Baker" in e.name or "baker" in e.name.lower()]
    assert baker_entities, "Baker Street entity missing after dedup"
    merged_syns = set(baker_entities[0].synonyms)
    assert "Holmes's lodgings" in merged_syns, "Synonyms from alias should be merged"


def test_run_dedup_reduces_duplicate_relationships(story_info: StoryInfo):
    """Duplicate (subject, predicate, object) triples must be deduplicated."""
    entities = [
        ExtractedEntityRow(id="a", entity_class="Character", name="Alice"),
        ExtractedEntityRow(id="b", entity_class="Character", name="Bob"),
    ]
    rels = [
        RelationshipRow(subject="a", predicate="ALLY_OF", object_id="b", confidence=0.8),
        RelationshipRow(subject="a", predicate="ALLY_OF", object_id="b", confidence=0.9),
    ]
    bundle = PerStoryBundle(story=story_info, entities=entities, relationships=rels)
    deduped = run_dedup(bundle)
    ally_rels = [r for r in deduped.relationships if r.predicate == "ALLY_OF"]
    assert len(ally_rels) == 1, "Duplicate relationships should be deduplicated"

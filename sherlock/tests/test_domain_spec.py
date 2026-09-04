"""Tests for domain_spec.py — entity types, predicates, and prompt instructions."""

from sherlock.domain_spec import (
    ALL_PREDICATES,
    ENTITY_CLASSES,
    NORMALIZED_TO_BUNDLE,
    PREDICATES,
    PROMPT_INSTRUCTIONS,
    CharacterEntity,
    LocationEntity,
    NarratorTrust,
    PhysicalObjectEntity,
    StoryEntity,
    get_valid_predicates,
    make_canonical_id,
)


def test_entity_classes_registered():
    """All entity classes must be in ENTITY_CLASSES."""
    class_names = {cls.__name__.replace("Entity", "") for cls in ENTITY_CLASSES}
    assert "Character" in class_names
    assert "Location" in class_names
    assert "Story" in class_names
    assert "PhysicalObject" in class_names
    assert "Event" in class_names
    assert "Occupation" in class_names
    assert "Organization" in class_names


def test_normalized_to_bundle():
    """NORMALIZED_TO_BUNDLE must map lowercase class names to PascalCase."""
    assert NORMALIZED_TO_BUNDLE.get("character") == "Character"
    assert NORMALIZED_TO_BUNDLE.get("location") == "Location"
    assert NORMALIZED_TO_BUNDLE.get("physicalobject") == "PhysicalObject"
    assert NORMALIZED_TO_BUNDLE.get("story") == "Story"


def test_all_predicates_defined():
    """ALL_PREDICATES must include core Sherlock predicates."""
    expected = {
        "LIVES_AT",
        "VISITS",
        "OWNS",
        "ALLY_OF",
        "ANTAGONIST_OF",
        "HIRED",
        "APPEARS_IN",
        "SAME_AS",
        "HAS_OCCUPATION",
        "DISGUISED_AS",
        "IMPLICATES",
        "EXONERATES",
        "DECEIVES",
        "TRUSTS",
    }
    for pred in expected:
        assert pred in ALL_PREDICATES, f"Expected predicate {pred!r} missing"


def test_predicate_specs_have_descriptions():
    """All predicates must have non-empty descriptions."""
    for pred, spec in PREDICATES.items():
        assert spec.description, f"Predicate {pred!r} has empty description"


def test_same_as_is_merge_signal():
    """SAME_AS must be flagged as a merge signal."""
    assert PREDICATES["SAME_AS"].is_merge_signal
    assert PREDICATES["SAME_AS"].symmetric


def test_ally_of_is_symmetric():
    """ALLY_OF should be symmetric."""
    assert PREDICATES["ALLY_OF"].symmetric


def test_get_valid_predicates_character_location():
    """get_valid_predicates(character, location) must include spatial predicates."""
    preds = get_valid_predicates("character", "location")
    assert "LIVES_AT" in preds
    assert "VISITS" in preds


def test_get_valid_predicates_character_character():
    """get_valid_predicates(character, character) must include social predicates."""
    preds = get_valid_predicates("character", "character")
    assert "ALLY_OF" in preds
    assert "ANTAGONIST_OF" in preds
    assert "HIRED" in preds


def test_get_valid_predicates_character_story():
    """get_valid_predicates(character, story) must include APPEARS_IN."""
    preds = get_valid_predicates("character", "story")
    assert "APPEARS_IN" in preds


def test_narrator_trust_enum_values():
    """NarratorTrust must have all 8 required values."""
    values = {v.value for v in NarratorTrust}
    assert "watson_direct" in values
    assert "watson_inference" in values
    assert "holmes_assertion" in values
    assert "holmes_inference" in values
    assert "third_party" in values
    assert "narrator" in values


def test_make_canonical_id_character():
    cid = make_canonical_id("character", "IreneAdler", story_slug="scandal")
    assert cid == "holmes:scandal:char:IreneAdler"


def test_make_canonical_id_story():
    cid = make_canonical_id("story", "AScandalonInBohemia")
    assert cid == "holmes:story:AScandalonInBohemia"


def test_prompt_instructions_non_empty():
    """PROMPT_INSTRUCTIONS must be a non-trivial string."""
    assert len(PROMPT_INSTRUCTIONS) > 500
    assert "Character" in PROMPT_INSTRUCTIONS
    assert "narrator_trust" in PROMPT_INSTRUCTIONS
    assert "story_time" in PROMPT_INSTRUCTIONS


def test_entity_spec_has_colors():
    """All entity classes with specs must have hex color."""
    for cls in ENTITY_CLASSES:
        spec = getattr(cls, "spec", None)
        if spec is not None:
            assert spec.color.startswith("#"), f"{cls.__name__} missing hex color"


def test_entity_get_entity_type():
    """Entity classes must return correct type strings."""
    from sherlock.domain_spec import (
        EventEntity,
        OccupationEntity,
        OrganizationEntity,
    )
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    base_kwargs = {
        "entity_id": "test",
        "name": "Test",
        "created_at": now,
        "source": "test",
    }

    assert CharacterEntity(**base_kwargs).get_entity_type() == "character"
    assert LocationEntity(**base_kwargs).get_entity_type() == "location"
    assert StoryEntity(**base_kwargs).get_entity_type() == "story"
    assert PhysicalObjectEntity(**base_kwargs).get_entity_type() == "physicalobject"
    assert EventEntity(**base_kwargs).get_entity_type() == "event"
    assert OccupationEntity(**base_kwargs).get_entity_type() == "occupation"
    assert OrganizationEntity(**base_kwargs).get_entity_type() == "organization"

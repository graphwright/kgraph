"""Domain spec for Sherlock Holmes knowledge graph extraction.

Single source of truth for entity types, predicates, evidence, and mentions.
Follows the medlit pattern: consumers import from this module.

Design goals:
- Rich typed schema (not just generic co_occurs_with) → dense graph
- Epistemic metadata: narrator trust, narrative position, story time
- Strong predicate constraints → semantically specific edges
- Alias/coreference handling via SAME_AS → merged canonical nodes
"""

from enum import Enum
from typing import ClassVar, Optional

from kgschema.entity import BaseEntity
from kgschema.spec import EntitySpec, EvidenceSpec, MentionsSpec, PredicateSpec


# ---------------------------------------------------------------------------
# Narrator trust — epistemic metadata attached to every relationship
# ---------------------------------------------------------------------------


class NarratorTrust(str, Enum):
    """Epistemic source/reliability of an assertion in the narrative.

    In fiction, all assertions have an epistemic source. Watson narrates
    retrospectively, Holmes deduces, characters speak and act. This enum
    captures *who* asserts a fact and *how reliably*, so the graph can be
    filtered to e.g. only Holmes-inference edges for "solve the case" queries.
    """

    WATSON_DIRECT = "watson_direct"
    "Watson directly observed this (most reliable first-person account)."

    WATSON_INFERENCE = "watson_inference"
    "Watson's own deduction — often wrong; treat skeptically."

    WATSON_SPECULATION = "watson_speculation"
    "Watson explicitly hedges: 'I fancied', 'it seemed to me'."

    WATSON_RETROSPECTIVE = "watson_retrospective"
    "Watson narrating with knowledge he didn't have at the time."

    HOLMES_ASSERTION = "holmes_assertion"
    "Holmes stated this directly."

    HOLMES_INFERENCE = "holmes_inference"
    "Holmes's deduction — high trust."

    THIRD_PARTY = "third_party"
    "Reported by another character (variable reliability)."

    NARRATOR = "narrator"
    "Authorial/frame-level fact (e.g. story title, publication metadata)."


# ---------------------------------------------------------------------------
# Story-time vocabulary — used in narrative_position metadata
# ---------------------------------------------------------------------------

STORY_TIME_VALUES = [
    "backstory",
    "before_crime",
    "day_of",
    "immediate_aftermath",
    "investigation",
    "revelation",
    "denouement",
    "unknown",
]


# ---------------------------------------------------------------------------
# Entity classes with specs
# ---------------------------------------------------------------------------


class CharacterEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="A person who appears in the story: protagonist, antagonist, minor character.",
        prompt_guidance=(
            "Extract all named and unnamed characters. For Holmes stories always include: "
            "Sherlock Holmes, Dr. Watson, any named persons, any titled persons (the King, etc.). "
            "Use the most canonical name as the entity name; add aliases as synonyms."
        ),
        color="#ef5350",
        label="Character",
    )

    def get_entity_type(self) -> str:
        return "character"


class LocationEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="A physical place, address, or geographic location mentioned in the story.",
        prompt_guidance=(
            "Extract specific addresses (221B Baker Street), named buildings (Briony Lodge), "
            "districts, cities, and countries. Include unnamed locations when they are story-relevant "
            "(e.g. 'a house in Serpentine Avenue')."
        ),
        color="#42a5f5",
        label="Location",
    )

    def get_entity_type(self) -> str:
        return "location"


class StoryEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="A Holmes story, novel, or collection serving as a narrative container.",
        prompt_guidance="Typically one per ingestion run. Extract the story title.",
        color="#9e9e9e",
        label="Story",
        metadata_only=True,
    )

    def get_entity_type(self) -> str:
        return "story"


class PhysicalObjectEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="A tangible object that plays a role in the plot: clues, weapons, documents, disguises.",
        prompt_guidance=(
            "Extract objects that are plot-relevant: photographs, letters, disguises, walking sticks, "
            "telegrams, rings, carriages, revolvers, etc. Do NOT extract objects mentioned only in passing."
        ),
        color="#ffb300",
        label="Object",
    )

    def get_entity_type(self) -> str:
        return "physicalobject"


class EventEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="A discrete event or happening in the story: crime, meeting, deception, reveal.",
        prompt_guidance=(
            "Extract named events and significant happenings: the King's visit to Baker Street, "
            "the staged fire alarm at Briony Lodge, Holmes's disguise as a clergyman, etc. "
            "Events are the narrative skeleton; extract generously."
        ),
        color="#ef9a9a",
        label="Event",
    )

    def get_entity_type(self) -> str:
        return "event"


class OccupationEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="A social role, occupation, or title that characterises how Holmes reasons about a character.",
        prompt_guidance=(
            "Extract occupations and social roles: detective, king, governess, adventuress, "
            "retired sergeant-major, groom, etc. Holmes's reasoning often depends on these."
        ),
        color="#ce93d8",
        label="Occupation",
    )

    def get_entity_type(self) -> str:
        return "occupation"


class OrganizationEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="An organization, institution, royal house, or named group.",
        prompt_guidance=(
            "Extract kingdoms, secret services, clubs, households, etc. "
            "E.g. 'The Royal House of Bohemia', 'Scotland Yard'."
        ),
        color="#80cbc4",
        label="Organization",
    )

    def get_entity_type(self) -> str:
        return "organization"


# ---------------------------------------------------------------------------
# Entity registry
# ---------------------------------------------------------------------------

ENTITY_CLASSES = [
    CharacterEntity,
    LocationEntity,
    StoryEntity,
    PhysicalObjectEntity,
    EventEntity,
    OccupationEntity,
    OrganizationEntity,
]

BUNDLE_CLASS_TO_ENTITY: dict[str, type[BaseEntity]] = {}
for _cls in ENTITY_CLASSES:
    _name = _cls.__name__.replace("Entity", "")
    BUNDLE_CLASS_TO_ENTITY[_name] = _cls  # type: ignore[type-abstract]

NORMALIZED_TO_BUNDLE: dict[str, str] = {
    k.lower().replace(" ", "").replace("_", ""): k for k in BUNDLE_CLASS_TO_ENTITY
}

ENTITY_TYPE_SPECS: dict[str, dict[str, str]] = {
    _cls.__name__.replace("Entity", "").lower(): {"color": _cls.spec.color, "label": _cls.spec.label}
    for _cls in ENTITY_CLASSES
    if hasattr(_cls, "spec")
}
ENTITY_TYPE_SPECS["default"] = {"color": "#78909c", "label": "Other"}


# ---------------------------------------------------------------------------
# Predicates
# ---------------------------------------------------------------------------

PREDICATES: dict[str, PredicateSpec] = {
    # Narrative / containment
    "APPEARS_IN": PredicateSpec(
        description="Character appears in a story.",
        subject_types=[CharacterEntity],
        object_types=[StoryEntity],
        specificity=1,
    ),
    "DESCRIBED_IN": PredicateSpec(
        description="Entity is described/mentioned in a story.",
        subject_types=None,
        object_types=[StoryEntity],
        specificity=1,
    ),
    # Spatial / temporal
    "LIVES_AT": PredicateSpec(
        description="Character's permanent or habitual residence.",
        subject_types=[CharacterEntity],
        object_types=[LocationEntity],
        specificity=2,
    ),
    "VISITS": PredicateSpec(
        description="Character visits or travels to a location during the story.",
        subject_types=[CharacterEntity],
        object_types=[LocationEntity],
        specificity=2,
    ),
    "LOCATED_AT": PredicateSpec(
        description="A physical object is located at a place (at some story time).",
        subject_types=[PhysicalObjectEntity],
        object_types=[LocationEntity],
        specificity=2,
    ),
    "PRESENT_AT": PredicateSpec(
        description="Character is present at an event or location.",
        subject_types=[CharacterEntity],
        object_types=[EventEntity, LocationEntity],
        specificity=2,
    ),
    "CONTAINS": PredicateSpec(
        description="A location contains an object.",
        subject_types=[LocationEntity],
        object_types=[PhysicalObjectEntity],
        specificity=2,
    ),
    # Possession / ownership
    "OWNS": PredicateSpec(
        description="Character owns or controls a physical object.",
        subject_types=[CharacterEntity],
        object_types=[PhysicalObjectEntity],
        specificity=2,
    ),
    "POSSESSED_BY": PredicateSpec(
        description="Physical object is in a character's possession at story time.",
        subject_types=[PhysicalObjectEntity],
        object_types=[CharacterEntity],
        specificity=2,
    ),
    # Knowledge / concealment
    "KNOWS_ABOUT": PredicateSpec(
        description="Character has knowledge of an event, object, or fact.",
        subject_types=[CharacterEntity],
        object_types=[EventEntity, PhysicalObjectEntity],
        specificity=2,
    ),
    "CONCEALS": PredicateSpec(
        description="Character deliberately hides or withholds information about something.",
        subject_types=[CharacterEntity],
        object_types=[EventEntity, PhysicalObjectEntity],
        specificity=2,
    ),
    "WITNESSES": PredicateSpec(
        description="Character directly witnesses an event.",
        subject_types=[CharacterEntity],
        object_types=[EventEntity],
        specificity=2,
    ),
    # Social relationships
    "ALLY_OF": PredicateSpec(
        description="Character is an ally, friend, or collaborator of another.",
        subject_types=[CharacterEntity],
        object_types=[CharacterEntity],
        specificity=2,
        symmetric=True,
    ),
    "ANTAGONIST_OF": PredicateSpec(
        description="Character is an antagonist or adversary of another.",
        subject_types=[CharacterEntity],
        object_types=[CharacterEntity],
        specificity=2,
    ),
    "TRUSTS": PredicateSpec(
        description="Character trusts another character.",
        subject_types=[CharacterEntity],
        object_types=[CharacterEntity],
        specificity=2,
    ),
    "DECEIVES": PredicateSpec(
        description="Character deceives or misleads another.",
        subject_types=[CharacterEntity],
        object_types=[CharacterEntity],
        specificity=2,
    ),
    "HIRED": PredicateSpec(
        description="Character hired or engaged another character for a task.",
        subject_types=[CharacterEntity],
        object_types=[CharacterEntity],
        specificity=2,
    ),
    "ROMANTICALLY_LINKED_TO": PredicateSpec(
        description="Characters have a romantic relationship or past.",
        subject_types=[CharacterEntity],
        object_types=[CharacterEntity],
        specificity=2,
        symmetric=True,
    ),
    "MEMBER_OF": PredicateSpec(
        description="Character is a member of an organization.",
        subject_types=[CharacterEntity],
        object_types=[OrganizationEntity],
        specificity=2,
    ),
    "SAME_AS": PredicateSpec(
        description="Coreference or alias: entity A is the same as entity B (for merge).",
        subject_types=None,
        object_types=None,
        specificity=0,
        symmetric=True,
        is_merge_signal=True,
    ),
    # Occupation / identity
    "HAS_OCCUPATION": PredicateSpec(
        description="Character has a particular occupation or social role.",
        subject_types=[CharacterEntity],
        object_types=[OccupationEntity],
        specificity=2,
    ),
    "DISGUISED_AS": PredicateSpec(
        description="Character adopts a disguise as another person or role.",
        subject_types=[CharacterEntity],
        object_types=[CharacterEntity, OccupationEntity],
        specificity=2,
    ),
    # Events / causation
    "CAUSES": PredicateSpec(
        description="Character or object causes an event.",
        subject_types=[CharacterEntity, PhysicalObjectEntity],
        object_types=[EventEntity],
        specificity=2,
    ),
    "PARTICIPATES_IN": PredicateSpec(
        description="Character participates in an event.",
        subject_types=[CharacterEntity],
        object_types=[EventEntity],
        specificity=2,
    ),
    "PRECEDES": PredicateSpec(
        description="Event A occurs before event B in story time.",
        subject_types=[EventEntity],
        object_types=[EventEntity],
        specificity=2,
    ),
    # Inference / implication
    "IMPLICATES": PredicateSpec(
        description="Clue, object, or evidence implicates a character in an event.",
        subject_types=[PhysicalObjectEntity, EventEntity],
        object_types=[CharacterEntity],
        specificity=2,
    ),
    "EXONERATES": PredicateSpec(
        description="Evidence or alibi exonerates a character from suspicion.",
        subject_types=[PhysicalObjectEntity, EventEntity],
        object_types=[CharacterEntity],
        specificity=2,
    ),
    "HAS_MOTIVE": PredicateSpec(
        description="Character has a motive related to an event.",
        subject_types=[CharacterEntity],
        object_types=[EventEntity],
        specificity=2,
    ),
    # Generic fallback
    "ASSOCIATED_WITH": PredicateSpec(
        description="General association; use only when no more specific predicate applies.",
        subject_types=None,
        object_types=None,
        specificity=1,
        symmetric=True,
    ),
}

ALL_PREDICATES: set[str] = set(PREDICATES.keys())


def _entity_class_matches_type(cls: type, entity_type: str) -> bool:
    """Return True if an entity class's type string matches entity_type."""
    return issubclass(cls, BaseEntity) and cls.__name__.replace("Entity", "").lower() == entity_type


def get_valid_predicates(subject_type: str, object_type: str) -> list[str]:
    """Return predicates valid between two entity types.

    Checks each predicate's subject_types/object_types constraints.
    When a predicate has None constraints it accepts any type.
    """
    result = []
    for pred, spec in PREDICATES.items():
        sub_ok = spec.subject_types is None or any(_entity_class_matches_type(c, subject_type) for c in spec.subject_types)
        obj_ok = spec.object_types is None or any(_entity_class_matches_type(c, object_type) for c in spec.object_types)
        if sub_ok and obj_ok:
            result.append(pred)
    return result


# ---------------------------------------------------------------------------
# Prompt instructions
# ---------------------------------------------------------------------------

PROMPT_INSTRUCTIONS = """
This domain covers Sherlock Holmes fiction. Extract entities and relationships to build
a DENSE, TYPED knowledge graph of the story. The goal is maximum edge density with
semantically specific predicates — NOT generic co-occurrence.

## Entity types (use "class" field)
- Character: Any person in the story (Holmes, Watson, Irene Adler, the King, etc.)
- Location: Physical places (221B Baker Street, Briony Lodge, Serpentine Avenue, etc.)
- Story: The containing narrative (use for the story being ingested)
- PhysicalObject: Plot-relevant tangible items (photograph, disguise, telegram, revolver, etc.)
- Event: Discrete happenings (the staged fire, Holmes's disguise, the King's visit, etc.)
- Occupation: Roles and titles (detective, king, governess, adventuress, groom, etc.)
- Organization: Institutions and groups (Royal House of Bohemia, Scotland Yard, etc.)

## Predicate selection — BE SPECIFIC
Use the most specific applicable predicate. Avoid ASSOCIATED_WITH unless nothing else fits.

Priority predicates for dense graphs:
- LIVES_AT / VISITS: characters ↔ locations
- OWNS / POSSESSED_BY / LOCATED_AT: objects ↔ characters/locations
- PRESENT_AT / WITNESSES / PARTICIPATES_IN: characters ↔ events
- KNOWS_ABOUT / CONCEALS: characters ↔ objects or events
- HIRED / ALLY_OF / TRUSTS / DECEIVES / ANTAGONIST_OF: character ↔ character
- HAS_OCCUPATION / DISGUISED_AS: character ↔ occupation
- HAS_MOTIVE: character ↔ event
- IMPLICATES / EXONERATES: object/event ↔ character
- APPEARS_IN: character ↔ story
- SAME_AS: for aliases (e.g. "Irene Adler" SAME_AS "The Woman")

## Narrator trust (narrator_trust field on each relationship)
Classify epistemic source for every relationship:
- watson_direct: Watson directly observed/experienced this
- watson_inference: Watson's own deduction (often wrong)
- watson_speculation: Watson hedges ("I fancied", "it seemed")
- watson_retrospective: Watson narrates with later knowledge
- holmes_assertion: Holmes stated this explicitly
- holmes_inference: Holmes's reasoning/deduction (reliable)
- third_party: Another character said this
- narrator: Frame-level authorial fact (story title, etc.)

## Story time (story_time field)
Classify each relationship's temporal position:
- backstory: before the story's events
- before_crime: early in the narrative
- day_of: day of the key event
- immediate_aftermath: just after the key event
- investigation: during the main investigation
- revelation: at the reveal/climax
- denouement: after the resolution
- unknown: cannot be determined

## Evidence format
id format: {story_id}:{section}:{paragraph_idx}:llm
Use ==CURRENT_STORY== as story_id placeholder.

## Output structure
Return ONLY valid JSON, no markdown or commentary.
Every "subject" and "object" in a relationship MUST be an "id" of an entry in "entities".
Extract relationships GENEROUSLY — aim for 3-5 relationships per paragraph.
Use SAME_AS to link aliases and ensure coreference; e.g. "the King" and "Wilhelm Gottsreich Sigismond von Ormstein".

## Relationship metadata (properties field)
Include narrator_trust and story_time in every relationship's properties dict:
  "properties": {"narrator_trust": "watson_direct", "story_time": "investigation"}
""".strip()


# ---------------------------------------------------------------------------
# Evidence and mentions
# ---------------------------------------------------------------------------

EVIDENCE = EvidenceSpec(
    id_format="{story_id}:{section}:{paragraph_idx}:{method}",
    methods=["llm"],
    section_names=["opening", "setting", "rising_action", "climax", "denouement"],
)

MENTIONS = MentionsSpec(
    mentionable_types=[
        CharacterEntity,
        LocationEntity,
        PhysicalObjectEntity,
        EventEntity,
        OccupationEntity,
        OrganizationEntity,
    ],
    skip_name_equals_type=True,
)


# ---------------------------------------------------------------------------
# Canonical ID scheme for fiction (no external authority APIs needed)
# ---------------------------------------------------------------------------
# Characters: holmes:<story_slug>:char:<SafeName>  e.g. holmes:scandal:char:IreneAdler
# Locations:  holmes:<story_slug>:loc:<SafeName>
# Stories:    holmes:story:<SafeName>
# Objects:    holmes:<story_slug>:obj:<SafeName>
# Events:     holmes:<story_slug>:evt:<SafeName>
# Occupations: holmes:occ:<SafeName>
# Organizations: holmes:org:<SafeName>


def make_canonical_id(entity_type: str, safe_name: str, story_slug: Optional[str] = None) -> str:
    """Build a stable canonical ID for a Sherlock entity.

    Args:
        entity_type: One of the entity type strings from domain_spec.
        safe_name: Name with spaces/special chars removed (PascalCase recommended).
        story_slug: Short story identifier, e.g. 'scandal'. Required for per-story types.
    """
    slug = story_slug or "unknown"
    mapping = {
        "character": f"holmes:{slug}:char:{safe_name}",
        "location": f"holmes:{slug}:loc:{safe_name}",
        "physicalobject": f"holmes:{slug}:obj:{safe_name}",
        "event": f"holmes:{slug}:evt:{safe_name}",
        "story": f"holmes:story:{safe_name}",
        "occupation": f"holmes:occ:{safe_name}",
        "organization": f"holmes:org:{safe_name}",
    }
    return mapping.get(entity_type, f"holmes:{slug}:other:{safe_name}")

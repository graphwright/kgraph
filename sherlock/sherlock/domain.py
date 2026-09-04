"""Domain schema for Sherlock Holmes knowledge graph."""

from kgschema.document import BaseDocument
from kgschema.domain import DomainSchema, PredicateConstraint, ValidationIssue
from kgschema.entity import BaseEntity, PromotionConfig
from kgschema.relationship import BaseRelationship
from kgschema.storage import EntityStorageInterface

from .documents import SherlockStory
from .domain_spec import ALL_PREDICATES, get_valid_predicates
from .entities import (
    CharacterEntity,
    EventEntity,
    LocationEntity,
    OccupationEntity,
    OrganizationEntity,
    PhysicalObjectEntity,
    StoryEntity,
)
from .promotion import SherlockPromotionPolicy
from .relationships import SherlockRelationship


class SherlockDomainSchema(DomainSchema):
    """Domain schema for Sherlock Holmes fiction extraction.

    Defines entity types, predicates, and validation rules for extracting
    a dense typed knowledge graph from Holmes stories.

    Key design choices:
    - No external authority APIs: canonical IDs from curated DBPedia map + synthetic scheme
    - All entities promoted immediately (fiction = no provisional/canonical gap)
    - Rich predicate vocabulary (28 predicates vs. 3 generic ones in old approach)
    - NarratorTrust and story_time metadata on every relationship
    """

    _predicate_constraints: dict[str, PredicateConstraint] | None = None

    def __init__(self, story_slug: str = "unknown", **kwargs):
        super().__init__(**kwargs)
        self._story_slug = story_slug

    @property
    def name(self) -> str:
        return "sherlock"

    @property
    def entity_types(self) -> dict[str, type[BaseEntity]]:
        return {
            "character": CharacterEntity,
            "location": LocationEntity,
            "story": StoryEntity,
            "physicalobject": PhysicalObjectEntity,
            "event": EventEntity,
            "occupation": OccupationEntity,
            "organization": OrganizationEntity,
        }

    @property
    def relationship_types(self) -> dict[str, type[BaseRelationship]]:
        return {predicate: SherlockRelationship for predicate in ALL_PREDICATES}

    @property
    def predicate_constraints(self) -> dict[str, PredicateConstraint]:
        if self._predicate_constraints is None:
            constraints: dict[str, set[str]] = {p: set() for p in ALL_PREDICATES}
            reverse_constraints: dict[str, set[str]] = {p: set() for p in ALL_PREDICATES}

            entity_type_names = list(self.entity_types.keys())
            for sub_type in entity_type_names:
                for obj_type in entity_type_names:
                    for pred in get_valid_predicates(sub_type, obj_type):
                        if pred in ALL_PREDICATES:
                            constraints[pred].add(sub_type)
                            reverse_constraints[pred].add(obj_type)

            self._predicate_constraints = {
                pred: PredicateConstraint(subject_types=constraints[pred], object_types=reverse_constraints[pred]) for pred in ALL_PREDICATES if constraints[pred] and reverse_constraints[pred]
            }
        return self._predicate_constraints

    @property
    def document_types(self) -> dict[str, type[BaseDocument]]:
        return {"sherlock_story": SherlockStory}

    @property
    def promotion_config(self) -> PromotionConfig:
        return PromotionConfig(
            min_usage_count=1,
            min_confidence=0.4,
            require_embedding=False,
        )

    def normalize_mention(self, mention: str) -> str:
        """Normalize character mention for dedup (lowercase, strip, common alias expansion)."""
        n = mention.lower().strip()
        # Common Victorian/Holmes abbreviation normalizations
        alias_map = {
            "holmes": "sherlock holmes",
            "the detective": "sherlock holmes",
            "watson": "dr. watson",
            "the doctor": "dr. watson",
            "the woman": "irene adler",
            "miss adler": "irene adler",
            "the king": "king of bohemia",
            "his majesty": "king of bohemia",
        }
        return alias_map.get(n, n)

    def validate_entity(self, entity: BaseEntity) -> list[ValidationIssue]:
        issues = []
        if entity.get_entity_type() not in self.entity_types:
            issues.append(
                ValidationIssue(
                    field="entity_type",
                    message=f"Unknown entity type: {entity.get_entity_type()}",
                    value=entity.get_entity_type(),
                    code="UNKNOWN_TYPE",
                )
            )
        return issues

    async def validate_relationship(
        self,
        relationship: BaseRelationship,
        entity_storage: EntityStorageInterface | None = None,
    ) -> bool:
        return await super().validate_relationship(relationship, entity_storage)

    def get_valid_predicates(self, subject_type: str, object_type: str) -> list[str]:
        return get_valid_predicates(subject_type, object_type)

    def preferred_entity(self, candidates: list[BaseEntity]) -> BaseEntity:
        """Select merge survivor: prefer canonical, then curated, then higher usage."""
        from kgschema.entity import EntityStatus

        def sort_key(e: BaseEntity) -> tuple:
            is_canonical = e.status == EntityStatus.CANONICAL
            has_dbpedia = "dbpedia" in (e.canonical_ids or {})
            return (is_canonical, has_dbpedia, e.usage_count, -e.created_at.timestamp())

        return max(candidates, key=sort_key)

    def get_promotion_policy(self, story_slug: str | None = None):
        slug = story_slug or self._story_slug
        return SherlockPromotionPolicy(config=self.promotion_config, story_slug=slug)

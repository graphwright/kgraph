"""Domain schema for medical literature knowledge graph."""

from kgraph.promotion import PromotionPolicy

from kgschema.document import BaseDocument
from kgschema.domain import DomainSchema, PredicateConstraint, ValidationIssue
from kgschema.entity import BaseEntity, PromotionConfig
from kgschema.relationship import BaseRelationship
from kgschema.storage import EntityStorageInterface

from .documents import JournalArticle
from .domain_spec import AnatomicalStructureEntity, HormoneEntity
from .entities import (
    BiomarkerEntity,
    DiseaseEntity,
    DrugEntity,
    EthnicityEntity,
    GeneEntity,
    LocationEntity,
    PathwayEntity,
    ProcedureEntity,
    ProteinEntity,
    SymptomEntity,
)
from .pipeline.authority_lookup import CanonicalIdLookup
from .promotion import MedLitPromotionPolicy
from .relationships import MedicalClaimRelationship
from .vocab import ALL_PREDICATES, get_valid_predicates


class MedLitDomainSchema(DomainSchema):
    """Domain schema for medical literature extraction.

    Defines the vocabulary and validation rules for extracting medical knowledge
    from journal articles. Uses canonical IDs (UMLS, HGNC, RxNorm, UniProt) for
    entity identification and supports rich relationship metadata with evidence
    and provenance tracking.
    """

    _predicate_constraints: dict[str, PredicateConstraint] | None = None

    @property
    def name(self) -> str:
        return "medlit"

    @property
    def entity_types(self) -> dict[str, type[BaseEntity]]:
        return {
            "disease": DiseaseEntity,
            "gene": GeneEntity,
            "drug": DrugEntity,
            "protein": ProteinEntity,
            "symptom": SymptomEntity,
            "procedure": ProcedureEntity,
            "biomarker": BiomarkerEntity,
            "pathway": PathwayEntity,
            "location": LocationEntity,
            "ethnicity": EthnicityEntity,
            "hormone": HormoneEntity,
            "anatomicalstructure": AnatomicalStructureEntity,
        }

    @property
    def relationship_types(self) -> dict[str, type[BaseRelationship]]:
        # Pattern A: All predicates map to the same relationship class
        # The predicate field distinguishes the relationship type
        return {predicate: MedicalClaimRelationship for predicate in ALL_PREDICATES}

    @property
    def predicate_constraints(self) -> dict[str, PredicateConstraint]:
        if self._predicate_constraints is None:
            # Dynamically build predicate constraints based on vocab.py's get_valid_predicates
            constraints: dict[str, set[str]] = {p: set() for p in ALL_PREDICATES}
            reverse_constraints: dict[str, set[str]] = {p: set() for p in ALL_PREDICATES}

            entity_type_names = list(self.entity_types.keys())
            for sub_type in entity_type_names:
                for obj_type in entity_type_names:
                    valid_preds_for_pair = get_valid_predicates(sub_type, obj_type)
                    for pred in valid_preds_for_pair:
                        if pred not in ALL_PREDICATES:
                            raise ValueError(f"get_valid_predicates returned unknown predicate: {pred}")
                        constraints.setdefault(pred, set()).add(sub_type)
                        reverse_constraints.setdefault(pred, set()).add(obj_type)

            self._predicate_constraints = {
                pred: PredicateConstraint(subject_types=constraints[pred], object_types=reverse_constraints[pred]) for pred in ALL_PREDICATES if constraints[pred] and reverse_constraints[pred]
            }

        return self._predicate_constraints

    @property
    def document_types(self) -> dict[str, type[BaseDocument]]:
        return {"journal_article": JournalArticle}

    @property
    def promotion_config(self) -> PromotionConfig:
        """Medical domain promotion configuration.

        Lowered thresholds to match LLM extraction characteristics:
        - min_usage_count=1: Entities appear once per paper
        - min_confidence=0.4: LLM typically returns ~0.47 confidence
        - require_embedding=False: Don't block promotion if embeddings not ready
        """
        return PromotionConfig(
            min_usage_count=1,  # Appear in at least 1 paper
            min_confidence=0.4,  # 40% confidence threshold (LLM typically ~0.47)
            require_embedding=False,  # Don't require embeddings (we have them but don't block)
        )

    # British → American spelling normalizations for entity mention resolution.
    _SPELLING_NORMALIZATIONS: dict[str, str] = {
        "hyperglycaemia": "hyperglycemia",
        "haemoglobin": "hemoglobin",
        "tumour": "tumor",
        "oesophagus": "esophagus",
        "leukaemia": "leukemia",
    }

    def normalize_mention(self, mention: str) -> str:
        """Lowercase, strip, and apply British→American spelling normalization."""
        n = mention.lower().strip()
        return self._SPELLING_NORMALIZATIONS.get(n, n)

    def validate_entity(self, entity: BaseEntity) -> list[ValidationIssue]:
        """Validate an entity against medical domain rules.

        Rules:
        - Entity type must be registered
        - Canonical entities should have canonical IDs in entity_id or canonical_ids
        - Provisional entities are allowed (they'll be promoted later)
        """
        issues = []

        entity_type = entity.get_entity_type()
        if entity_type not in self.entity_types:
            issues.append(
                ValidationIssue(
                    field="entity_type",
                    message=f"Unknown entity type: {entity_type}",
                    value=entity_type,
                    code="UNKNOWN_TYPE",
                )
            )

        # Canonical entities should have meaningful IDs
        if entity.status.value == "canonical":
            # Allow IDs like "C0006142" (UMLS), "HGNC:1100", "RxNorm:1187832", etc.
            if not entity.entity_id or entity.entity_id.startswith("prov:"):
                # Provisional prefix suggests this should be provisional
                issues.append(
                    ValidationIssue(
                        field="entity_id",
                        message="Canonical entities must have a meaningful ID, not provisional prefix",
                        value=entity.entity_id,
                        code="INVALID_CANONICAL_ID",
                    )
                )

        return issues

    async def validate_relationship(
        self,
        relationship: BaseRelationship,
        entity_storage: EntityStorageInterface | None = None,
    ) -> bool:
        """Validate a relationship against medical domain rules.

        Rules:
        - Predicate must be registered
        - Subject and object entity types must be compatible with predicate
        - Confidence must be in valid range (enforced by BaseRelationship)
        """
        # First, run the base class validation which includes predicate constraints
        if not await super().validate_relationship(relationship, entity_storage):
            return False

        # Add any MedLit-specific relationship validation here if needed
        return True

    def get_valid_predicates(self, subject_type: str, object_type: str) -> list[str]:
        """Return predicates valid between two entity types.

        Uses the vocabulary validation function to enforce domain-specific
        constraints on which relationships are semantically valid.
        """
        return get_valid_predicates(subject_type, object_type)

    def preferred_entity(self, candidates: list[BaseEntity]) -> BaseEntity:
        """Select the merge survivor from a set of synonym candidates.

        Preference order (highest wins):
        1. Canonical status over provisional
        2. Presence of an authoritative ``canonical_ids`` entry (UMLS, HGNC, etc.)
        3. Higher ``usage_count`` (more evidence)
        4. Earlier ``created_at`` (stable, long-lived entity)
        """
        from kgschema.entity import EntityStatus

        def sort_key(e: BaseEntity) -> tuple:
            is_canonical = e.status == EntityStatus.CANONICAL
            has_authority = bool(e.canonical_ids)
            return (is_canonical, has_authority, e.usage_count, -e.created_at.timestamp())

        return max(candidates, key=sort_key)

    def get_promotion_policy(self, lookup: CanonicalIdLookup | None = None) -> PromotionPolicy:
        """Return the promotion policy for medical literature domain.

        Uses MedLitPromotionPolicy which assigns canonical IDs based on
        authoritative medical ontologies (UMLS, HGNC, RxNorm, UniProt).

        Args:
            lookup: Optional canonical ID lookup service. If None, a new
                    instance will be created (without UMLS API key unless
                    set in environment).
        """
        return MedLitPromotionPolicy(config=self.promotion_config, lookup=lookup)

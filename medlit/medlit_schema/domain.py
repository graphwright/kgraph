"""Domain schema for the Medical Literature domain."""

from typing import Optional
from kgschema.domain import DomainSchema, PredicateConstraint, ValidationIssue
from kgschema.entity import BaseEntity
from kgschema.relationship import BaseRelationship
from kgschema.document import BaseDocument
from kgschema.canonical_id import CanonicalId
from kgschema.promotion import PromotionPolicy


from medlit_schema.entity import (
    Disease,
    Gene,
    Drug,
    Protein,
    Mutation,
    Symptom,
    Biomarker,
    Pathway,
    Procedure,
    Paper,
    Author,
    ClinicalTrial,
    Institution,
    Hypothesis,
    StudyDesign,
    StatisticalMethod,
    EvidenceLine,
    Evidence,
)
from medlit_schema.relationship import (
    Treats,
    Causes,
    Prevents,
    IncreasesRisk,
    SideEffect,
    AssociatedWith,
    InteractsWith,
    ContraindicatedFor,
    DiagnosedBy,
    ParticipatesIn,
    Encodes,
    BindsTo,
    Inhibits,
    Upregulates,
    Downregulates,
    AuthoredBy,
    Cites,
    StudiedIn,
    PartOf,
    SameAs,
    Indicates,
    Predicts,
    TestedBy,
    Supports,
    Refutes,
    Generates,
    SubtypeOf,
)
from medlit_schema.document import PaperDocument


class MedlitPromotionPolicy(PromotionPolicy):
    async def assign_canonical_id(self, entity: BaseEntity) -> Optional[CanonicalId]:
        return None


class MedlitDomain(DomainSchema):
    """Domain schema for medical literature."""

    @property
    def name(self) -> str:
        return "medlit"

    @property
    def entity_types(self) -> dict[str, type[BaseEntity]]:
        return {
            "disease": Disease,
            "gene": Gene,
            "drug": Drug,
            "protein": Protein,
            "mutation": Mutation,
            "symptom": Symptom,
            "biomarker": Biomarker,
            "pathway": Pathway,
            "procedure": Procedure,
            "paper": Paper,
            "author": Author,
            "clinical_trial": ClinicalTrial,
            "institution": Institution,
            "hypothesis": Hypothesis,
            "study_design": StudyDesign,
            "statistical_method": StatisticalMethod,
            "evidence_line": EvidenceLine,
            "evidence": Evidence,
        }

    @property
    def relationship_types(self) -> dict[str, type[BaseRelationship]]:
        return {
            "TREATS": Treats,
            "CAUSES": Causes,
            "PREVENTS": Prevents,
            "INCREASES_RISK": IncreasesRisk,
            "SIDE_EFFECT": SideEffect,
            "ASSOCIATED_WITH": AssociatedWith,
            "INTERACTS_WITH": InteractsWith,
            "CONTRAINDICATED_FOR": ContraindicatedFor,
            "DIAGNOSED_BY": DiagnosedBy,
            "PARTICIPATES_IN": ParticipatesIn,
            "ENCODES": Encodes,
            "BINDS_TO": BindsTo,
            "INHIBITS": Inhibits,
            "UPREGULATES": Upregulates,
            "DOWNREGULATES": Downregulates,
            "AUTHORED_BY": AuthoredBy,
            "CITES": Cites,
            "STUDIED_IN": StudiedIn,
            "PART_OF": PartOf,
            "PREDICTS": Predicts,
            "TESTED_BY": TestedBy,
            "SUPPORTS": Supports,
            "REFUTES": Refutes,
            "GENERATES": Generates,
            "SUBTYPE_OF": SubtypeOf,
            "INDICATES": Indicates,
            "SAME_AS": SameAs,
        }

    @property
    def predicate_constraints(self) -> dict[str, PredicateConstraint]:
        return {
            "TREATS": PredicateConstraint(subject_types={"drug"}, object_types={"disease"}),
            "CAUSES": PredicateConstraint(subject_types={"gene", "mutation"}, object_types={"disease"}),
            "PREVENTS": PredicateConstraint(subject_types={"drug"}, object_types={"disease"}),
            "INCREASES_RISK": PredicateConstraint(subject_types={"gene", "mutation"}, object_types={"disease"}),
            "SIDE_EFFECT": PredicateConstraint(subject_types={"drug"}, object_types={"symptom", "disease"}),
            "ASSOCIATED_WITH": PredicateConstraint(subject_types={"disease", "gene", "biomarker"}, object_types={"disease"}),
            "INTERACTS_WITH": PredicateConstraint(subject_types={"drug"}, object_types={"drug"}),
            "CONTRAINDICATED_FOR": PredicateConstraint(subject_types={"drug"}, object_types={"disease"}),
            "DIAGNOSED_BY": PredicateConstraint(subject_types={"disease"}, object_types={"procedure", "biomarker"}),
            "PARTICIPATES_IN": PredicateConstraint(subject_types={"gene", "protein"}, object_types={"pathway"}),
            "ENCODES": PredicateConstraint(subject_types={"gene"}, object_types={"protein"}),
            "BINDS_TO": PredicateConstraint(subject_types={"drug", "protein"}, object_types={"protein"}),
            "INHIBITS": PredicateConstraint(subject_types={"drug", "protein"}, object_types={"protein", "pathway"}),
            "UPREGULATES": PredicateConstraint(subject_types={"drug", "gene"}, object_types={"gene", "pathway"}),
            "DOWNREGULATES": PredicateConstraint(subject_types={"drug", "gene"}, object_types={"gene", "pathway"}),
            "AUTHORED_BY": PredicateConstraint(subject_types={"paper"}, object_types={"author"}),
            "CITES": PredicateConstraint(subject_types={"paper"}, object_types={"paper"}),
            "STUDIED_IN": PredicateConstraint(subject_types={"disease", "drug"}, object_types={"clinical_trial"}),
            "PART_OF": PredicateConstraint(subject_types={"paper"}, object_types={"clinical_trial"}),
            "PREDICTS": PredicateConstraint(subject_types={"hypothesis"}, object_types={"disease"}),
            "TESTED_BY": PredicateConstraint(subject_types={"hypothesis"}, object_types={"study_design"}),
            "SUPPORTS": PredicateConstraint(subject_types={"evidence"}, object_types={"hypothesis"}),
            "REFUTES": PredicateConstraint(subject_types={"evidence"}, object_types={"hypothesis"}),
            "GENERATES": PredicateConstraint(subject_types={"clinical_trial", "paper"}, object_types={"evidence"}),
            "SUBTYPE_OF": PredicateConstraint(subject_types={"disease"}, object_types={"disease"}),
            "INDICATES": PredicateConstraint(subject_types={"biomarker", "evidence"}, object_types={"disease"}),
            "SAME_AS": PredicateConstraint(
                subject_types={"disease", "gene", "drug", "protein", "biomarker", "symptom", "mutation"},
                object_types={"disease", "gene", "drug", "protein", "biomarker", "symptom", "mutation"},
            ),
        }

    @property
    def document_types(self) -> dict[str, type[BaseDocument]]:
        return {"paper_document": PaperDocument}

    def validate_entity(self, entity: BaseEntity) -> list[ValidationIssue]:
        issues = []
        # Check entity type is registered
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
        # Run Pydantic validation
        try:
            entity.model_validate(entity.model_dump())
        except ValueError as e:
            issues.append(
                ValidationIssue(
                    field="model",
                    message=str(e),
                    code="PYDANTIC_VALIDATION",
                )
            )
        return issues

    async def validate_relationship(self, relationship: BaseRelationship, entity_storage=None) -> bool:
        try:
            relationship.model_validate(relationship.model_dump())
            return True
        except ValueError:
            return False

    def preferred_entity(self, candidates: list[BaseEntity]) -> BaseEntity:
        from kgschema.entity import EntityStatus

        def sort_key(e: BaseEntity) -> tuple:
            is_canonical = e.status == EntityStatus.CANONICAL
            has_authority = bool(e.canonical_ids)
            return (is_canonical, has_authority, e.usage_count, -e.created_at.timestamp())

        return max(candidates, key=sort_key)

    def get_promotion_policy(self, lookup=None) -> PromotionPolicy:
        return MedlitPromotionPolicy(self.promotion_config)

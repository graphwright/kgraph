"""Domain spec for medical literature extraction.

Single source of truth for entity types, predicates, evidence, and mentions.
Consumers import from this module instead of loading YAML config.
"""

from typing import ClassVar

from kgschema.entity import BaseEntity
from kgschema.spec import EntitySpec, EvidenceSpec, MentionsSpec, PredicateSpec

# -----------------------------------------------------------------------------
# Entity classes with specs (from entity_types.yaml + entities.py)
#
# These classes are schema metadata holders for prompts, predicates, and bundle
# mapping — NOT the runtime classes used during ingestion. Runtime entity
# instantiation uses entities.py via MedLitDomainSchema.entity_types.
# -----------------------------------------------------------------------------


class DiseaseEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Diseases, conditions, syndromes. Use the most specific term.",
        prompt_guidance="Use the most specific term.",
        color="#ef5350",
        label="Disease",
    )

    def get_entity_type(self) -> str:
        return "disease"


class GeneEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Genes by symbol or name. Prefer HGNC symbol when known.",
        prompt_guidance="Prefer HGNC symbol when known.",
        color="#66bb6a",
        label="Gene",
    )

    def get_entity_type(self) -> str:
        return "gene"


class DrugEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Drugs, compounds, therapeutic agents.",
        color="#4fc3f7",
        label="Drug",
    )

    def get_entity_type(self) -> str:
        return "drug"


class ProteinEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Structural or signaling proteins NOT better classified as Enzyme, Hormone, Receptor, or Antibody.",
        color="#ab47bc",
        label="Protein",
    )

    def get_entity_type(self) -> str:
        return "protein"


class HormoneEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Peptide or steroid hormones (e.g. ACTH, cortisol, catecholamines).",
        color="#ffa726",
        label="Hormone",
    )

    def get_entity_type(self) -> str:
        return "hormone"


class EnzymeEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Proteins with catalytic function (e.g. aldosterone synthase, kinases).",
        color="#7e57c2",
        label="Enzyme",
    )

    def get_entity_type(self) -> str:
        return "enzyme"


class BiomarkerEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Measurable indicators of biological state.",
        color="#26a69a",
        label="Biomarker",
    )

    def get_entity_type(self) -> str:
        return "biomarker"


class SymptomEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Symptoms, signs, clinical manifestations.",
        color="#ef5350",
        label="Symptom",
    )

    def get_entity_type(self) -> str:
        return "symptom"


class ProcedureEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Medical procedures, diagnostic tests, interventions.",
        color="#ffa726",
        label="Procedure",
    )

    def get_entity_type(self) -> str:
        return "procedure"


class MutationEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Genetic mutations, variants.",
        color="#5c6bc0",
        label="Mutation",
    )

    def get_entity_type(self) -> str:
        return "mutation"


class PathwayEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Biological pathways (e.g. STING pathway).",
        color="#7e57c2",
        label="Pathway",
    )

    def get_entity_type(self) -> str:
        return "pathway"


class BiologicalProcessEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Biological processes or phenomena.",
        color="#5c6bc0",
        label="Biological process",
    )

    def get_entity_type(self) -> str:
        return "biologicalprocess"


class AnatomicalStructureEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Anatomical structures, cell types.",
        color="#8d6e63",
        label="Anatomy",
    )

    def get_entity_type(self) -> str:
        return "anatomicalstructure"


class AuthorEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Authors.",
        color="#795548",
        label="Author",
    )

    def get_entity_type(self) -> str:
        return "author"


class InstitutionEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Institutions, organizations.",
        color="#78909c",
        label="Institution",
    )

    def get_entity_type(self) -> str:
        return "institution"


class HypothesisEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Hypotheses.",
        color="#78909c",
        label="Hypothesis",
    )

    def get_entity_type(self) -> str:
        return "hypothesis"


class EvidenceEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Evidence span (internal use).",
        color="#78909c",
        label="Evidence",
    )

    def get_entity_type(self) -> str:
        return "evidence"


class LocationEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Geographic locations for epidemiological analysis.",
        color="#78909c",
        label="Location",
    )

    def get_entity_type(self) -> str:
        return "location"


class EthnicityEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="Ethnic or population groups for epidemiological analysis.",
        color="#78909c",
        label="Ethnicity",
    )

    def get_entity_type(self) -> str:
        return "ethnicity"


# -----------------------------------------------------------------------------
# Entity registry: bundle_class (PascalCase) -> entity class
# -----------------------------------------------------------------------------
ENTITY_CLASSES = [
    DiseaseEntity,
    GeneEntity,
    DrugEntity,
    ProteinEntity,
    HormoneEntity,
    EnzymeEntity,
    BiomarkerEntity,
    SymptomEntity,
    ProcedureEntity,
    MutationEntity,
    PathwayEntity,
    BiologicalProcessEntity,
    AnatomicalStructureEntity,
    AuthorEntity,
    InstitutionEntity,
    HypothesisEntity,
    EvidenceEntity,
    LocationEntity,
    EthnicityEntity,
]

BUNDLE_CLASS_TO_ENTITY: dict[str, type[BaseEntity]] = {}
for cls in ENTITY_CLASSES:
    # PascalCase bundle_class: Disease, Gene, Drug, etc.
    name = cls.__name__.replace("Entity", "")
    BUNDLE_CLASS_TO_ENTITY[name] = cls

# Normalized (lowercase, no spaces) -> bundle_class for raw LLM type mapping
NORMALIZED_TO_BUNDLE: dict[str, str] = {
    k.lower().replace(" ", "").replace("_", ""): k for k in BUNDLE_CLASS_TO_ENTITY
}


# -----------------------------------------------------------------------------
# Predicates (from predicates.yaml)
# -----------------------------------------------------------------------------
PREDICATES: dict[str, PredicateSpec] = {
    "TREATS": PredicateSpec(
        description="Drug or procedure used therapeutically to address a disease.",
        subject_types=[DrugEntity, ProcedureEntity],
        object_types=[DiseaseEntity],
        specificity=2,
    ),
    "INCREASES_RISK": PredicateSpec(
        description="Gene, mutation, or factor that raises risk of a disease.",
        subject_types=[GeneEntity, MutationEntity],
        object_types=[DiseaseEntity],
        specificity=2,
    ),
    "INDICATES": PredicateSpec(
        description="Biomarker or test that indicates presence or status of a condition.",
        subject_types=[BiomarkerEntity, EvidenceEntity],
        object_types=[DiseaseEntity],
        specificity=2,
    ),
    "ASSOCIATED_WITH": PredicateSpec(
        description="General association; use when more specific predicate does not apply.",
        subject_types=None,
        object_types=None,
        specificity=1,
    ),
    "SAME_AS": PredicateSpec(
        description="Entity A is the same as entity B (for coreference/merge).",
        subject_types=None,
        object_types=None,
        specificity=0,
    ),
    "SUBTYPE_OF": PredicateSpec(
        description="Entity A is a subtype of entity B.",
        subject_types=[DiseaseEntity],
        object_types=[DiseaseEntity],
        specificity=2,
    ),
    "CAUSES": PredicateSpec(
        description="Entity causes or contributes to a disease or condition.",
        subject_types=[GeneEntity, MutationEntity],
        object_types=[DiseaseEntity],
        specificity=2,
    ),
    "INHIBITS": PredicateSpec(
        description="Entity inhibits a protein or pathway.",
        subject_types=[DrugEntity, ProteinEntity],
        object_types=[ProteinEntity, PathwayEntity],
        specificity=2,
    ),
    "REGULATES": PredicateSpec(
        description="Entity regulates a gene, pathway, or process.",
        subject_types=[DrugEntity, GeneEntity],
        object_types=[GeneEntity, PathwayEntity],
        specificity=2,
    ),
    "PREVENTS": PredicateSpec(
        description="Drug prevents a disease.",
        subject_types=[DrugEntity],
        object_types=[DiseaseEntity],
        specificity=2,
    ),
    "INTERACTS_WITH": PredicateSpec(
        description="Drug interacts with another drug.",
        subject_types=[DrugEntity],
        object_types=[DrugEntity],
        specificity=2,
    ),
    "ENCODES": PredicateSpec(
        description="Gene encodes a protein.",
        subject_types=[GeneEntity],
        object_types=[ProteinEntity],
        specificity=2,
    ),
}

# -----------------------------------------------------------------------------
# Prompt instructions (from domain_instructions.md)
# -----------------------------------------------------------------------------
PROMPT_INSTRUCTIONS = """
This domain covers peer-reviewed medical literature. Prefer established terminology over colloquial.
When in doubt about entity type, prefer the more specific type.
Connect Author and Institution to the graph via relationships; do not leave them as standalone entities.

## Entity type classification
Classify at the most specific functional role. If an entity is both a hormone and a protein, classify it as Hormone.
Enzymes should be typed Enzyme, not Protein.

## Predicates
Use the predicate list from the config. For SAME_AS relationships, use "resolution": null and "note" in the output.

## Linguistic trust
For each relationship, classify linguistic trust: asserted (direct statement), suggested (soft language), speculative (hedged).
Use linguistic_trust: "asserted" | "suggested" | "speculative" in the JSON.

## Evidence format
Evidence id format: {paper_id}:{section}:{paragraph_idx}:llm

## Output structure
Use "class" for entity type. Return ONLY valid JSON, no markdown or commentary.
""".strip()

# -----------------------------------------------------------------------------
# Evidence and mentions
# -----------------------------------------------------------------------------
EVIDENCE = EvidenceSpec(
    id_format="{paper_id}:{section}:{paragraph_idx}:{method}",
    methods=["llm"],
    section_names=["abstract", "introduction", "methods", "results", "discussion"],
)

MENTIONS = MentionsSpec(
    mentionable_types=[
        DiseaseEntity,
        GeneEntity,
        DrugEntity,
        ProteinEntity,
        BiomarkerEntity,
        SymptomEntity,
        ProcedureEntity,
        PathwayEntity,
        AuthorEntity,
        InstitutionEntity,
    ],
    skip_name_equals_type=True,
)

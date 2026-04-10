"""Medlit relationship definitions."""

from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from kgschema.relationship import BaseRelationship
from medlit_schema.base import Measurement


class EvidenceItem(BaseModel):
    """
    Lightweight evidence reference for relationships.

    Attributes:
        paper_id: PMC ID of source paper
        study_type: Type of study (observational, rct, meta_analysis, case_report, review)
        sample_size: Number of subjects in the study
        confidence: Confidence score (0.0-1.0)
    """

    paper_id: str
    study_type: str
    sample_size: Optional[int] = None
    confidence: float = 0.5


class BaseMedicalRelationship(BaseRelationship):
    """
    Base class for all medical relationships with comprehensive provenance tracking.

    All medical relationships inherit from this class and include evidence-based
    provenance fields to support confidence scoring, contradiction detection,
    and temporal tracking of medical knowledge.

    Combines lightweight tracking (just paper IDs) with optional rich provenance
    (detailed Evidence objects) and quantitative measurements.

    Schema Rules:
    - Medical assertion relationships MUST have non-empty evidence_ids
    - Bibliographic relationships (AuthoredBy, Cites) do NOT require evidence

    Attributes:
        subject_id: Entity ID of the subject (source node)
        predicate: Relationship type
        object_id: Entity ID of the object (target node)
        evidence_ids: REQUIRED list of Evidence entity IDs (for medical assertions)
        confidence: Confidence score (0.0-1.0) based on evidence strength
        source_papers: List of PMC IDs supporting this relationship (lightweight)
        evidence_count: Number of papers providing supporting evidence
        contradicted_by: List of PMC IDs with contradicting findings
        first_reported: Date when this relationship was first observed
        last_updated: Date of most recent supporting evidence
        evidence: List of detailed EvidenceItem objects (optional, for rich provenance)
        measurements: List of quantitative measurements (optional)
        properties: Flexible dict for relationship-specific properties

    Example (lightweight):
        >>> relationship = Treats(
        ...     subject_id="RxNorm:1187832",
        ...     predicate="TREATS",
        ...     object_id="C0006142",
        ...     evidence_ids=["PMC123:results:5:llm", "PMC456:abstract:2:llm"],
        ...     source_papers=["PMC123", "PMC456"],
        ...     confidence=0.85,
        ...     evidence_count=2,
        ...     response_rate=0.59
        ... )

    Example (rich provenance):
        >>> relationship = Treats(
        ...     subject_id="RxNorm:1187832",
        ...     predicate="TREATS",
        ...     object_id="C0006142",
        ...     evidence_ids=["PMC123:results:5:rct"],
        ...     confidence=0.85,
        ...     evidence=[EvidenceItem(paper_id="PMC123", study_type="rct", sample_size=302)],
        ...     measurements=[Measurement(value=0.59, value_type="response_rate")],
        ...     response_rate=0.59
        ... )
    """

    # Required: References to Evidence entities
    evidence_ids: list[str] = Field(default_factory=list)

    # Core provenance (always present)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)

    # Lightweight tracking
    source_papers: list[str] = Field(default_factory=list)
    evidence_count: int = 0
    contradicted_by: list[str] = Field(default_factory=list)
    first_reported_date: Optional[str] = None  # String date to avoid shadowing BaseRelationship

    # Rich provenance (optional)
    evidence: list[EvidenceItem] = Field(default_factory=list)

    # Measurements (optional)
    measurements: list[Measurement] = Field(default_factory=list)

    # Relationship-specific properties (flexible)
    properties: dict = Field(default_factory=dict)

    @field_validator("evidence_ids")
    def evidence_required_for_medical_assertions(cls, v):  # pylint: disable=no-self-argument
        """
        Medical assertion relationships must include evidence.

        This validator is overridden in non-medical relationship classes
        (like ResearchRelationship) that don't require evidence.
        """
        if not v or len(v) == 0:
            raise ValueError("Medical relationships must include evidence")
        return v


# Medical
class Treats(BaseMedicalRelationship):
    """
    Represents a therapeutic relationship between a drug and a disease.

    Direction: Drug → Disease

    Attributes:
        efficacy: Effectiveness measure or description
        response_rate: Percentage of patients responding (0.0-1.0)
        line_of_therapy: Treatment sequence (first-line, second-line, etc.)
        indication: Specific approved use or condition

    Example:
        >>> treats = Treats(
        ...     subject_id="RxNorm:1187832",  # Olaparib
        ...     object_id="C0006142",  # Breast Cancer
        ...     predicate="TREATS",
        ...     evidence_ids=["PMC999:results:5:rct", "PMC888:abstract:2:rct"],
        ...     efficacy="significant improvement in PFS",
        ...     response_rate=0.59,
        ...     line_of_therapy="second-line",
        ...     indication="BRCA-mutated breast cancer",
        ...     source_papers=["PMC999", "PMC888"],
        ...     confidence=0.85
        ... )
    """

    efficacy: Optional[str] = None
    response_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    line_of_therapy: Optional[Literal["first-line", "second-line", "third-line", "maintenance", "salvage"]] = None
    indication: Optional[str] = None

    def get_edge_type(self) -> str:
        return "TREATS"


class Causes(BaseMedicalRelationship):
    """
    Represents a causal relationship between a disease and a symptom.

    Direction: Disease → Symptom (or Gene/Mutation → Disease)

    Attributes:
        frequency: How often the symptom occurs (always, often, sometimes, rarely)
        onset: When the symptom typically appears (early, late)
        severity: Typical severity of the symptom (mild, moderate, severe)

    Example:
        >>> causes = Causes(
        ...     subject_id="C0006142",  # Breast Cancer
        ...     object_id="C0030193",  # Pain
        ...     predicate="CAUSES",
        ...     evidence_ids=["PMC123:results:3:llm"],
        ...     frequency="often",
        ...     onset="late",
        ...     severity="moderate",
        ...     source_papers=["PMC123"],
        ...     confidence=0.75
        ... )
    """

    frequency: Optional[Literal["always", "often", "sometimes", "rarely"]] = None
    onset: Optional[Literal["early", "late"]] = None
    severity: Optional[Literal["mild", "moderate", "severe"]] = None

    def get_edge_type(self) -> str:
        return "CAUSES"


class Prevents(BaseMedicalRelationship):
    """
    Drug prevents disease relationship.

    Direction: Drug → Disease

    Attributes:
        efficacy: Effectiveness measure or description
        risk_reduction: Risk reduction percentage (0.0-1.0)
    """

    efficacy: Optional[str] = None
    risk_reduction: Optional[float] = Field(None, ge=0.0, le=1.0)

    def get_edge_type(self) -> str:
        return "PREVENTS"


class IncreasesRisk(BaseMedicalRelationship):
    """
    Represents genetic risk factors for diseases.

    Direction: Gene/Mutation → Disease

    Attributes:
        risk_ratio: Numeric risk increase (e.g., 2.5 means 2.5x higher risk)
        penetrance: Percentage who develop condition (0.0-1.0)
        age_of_onset: Typical age when disease manifests
        population: Studied population or ethnic group

    Example:
        >>> risk = IncreasesRisk(
        ...     subject_id="HGNC:1100",  # BRCA1
        ...     object_id="C0006142",  # Breast Cancer
        ...     predicate="INCREASES_RISK",
        ...     evidence_ids=["PMC123:results:7:llm", "PMC456:discussion:2:llm"],
        ...     risk_ratio=5.0,
        ...     penetrance=0.72,
        ...     age_of_onset="40-50 years",
        ...     population="Ashkenazi Jewish",
        ...     source_papers=["PMC123", "PMC456"],
        ...     confidence=0.92
        ... )
    """

    risk_ratio: Optional[float] = Field(None, gt=0.0)
    penetrance: Optional[float] = Field(None, ge=0.0, le=1.0)
    age_of_onset: Optional[str] = None
    population: Optional[str] = None

    def get_edge_type(self) -> str:
        return "INCREASES_RISK"


class SideEffect(BaseMedicalRelationship):
    """
    Represents adverse effects of medications.

    Direction: Drug → Symptom

    Attributes:
        frequency: How often it occurs (common, uncommon, rare)
        severity: Severity level (mild, moderate, severe)
        reversible: Whether the side effect resolves after stopping the drug

    Example:
        >>> side_effect = SideEffect(
        ...     subject_id="RxNorm:1187832",  # Olaparib
        ...     object_id="C0027497",  # Nausea
        ...     predicate="SIDE_EFFECT",
        ...     evidence_ids=["PMC999:results:8:llm"],
        ...     frequency="common",
        ...     severity="mild",
        ...     reversible=True,
        ...     source_papers=["PMC999"],
        ...     confidence=0.75
        ... )
    """

    frequency: Optional[Literal["common", "uncommon", "rare"]] = None
    severity: Optional[Literal["mild", "moderate", "severe"]] = None
    reversible: bool = True

    def get_edge_type(self) -> str:
        return "SIDE_EFFECT"


class AssociatedWith(BaseMedicalRelationship):
    """
    Represents a general association between entities.

    This is used for relationships where causality is not established but
    statistical association exists.

    Valid directions:
        - Disease → Disease (comorbidities)
        - Gene → Disease
        - Biomarker → Disease

    Attributes:
        association_type: Nature of association (positive, negative, neutral)
        strength: Association strength (strong, moderate, weak)
        statistical_significance: p-value from statistical tests

    Example:
        >>> assoc = AssociatedWith(
        ...     subject_id="C0011849",  # Diabetes
        ...     object_id="C0020538",  # Hypertension
        ...     predicate="ASSOCIATED_WITH",
        ...     evidence_ids=["PMC111:results:4:llm"],
        ...     association_type="positive",
        ...     strength="strong",
        ...     statistical_significance=0.001,
        ...     source_papers=["PMC111"],
        ...     confidence=0.80
        ... )
    """

    association_type: Optional[Literal["positive", "negative", "neutral"]] = None
    strength: Optional[Literal["strong", "moderate", "weak"]] = None
    statistical_significance: Optional[float] = Field(None, ge=0.0, le=1.0)

    def get_edge_type(self) -> str:
        return "ASSOCIATED_WITH"


class InteractsWith(BaseMedicalRelationship):
    """
    Represents drug-drug interactions.

    Direction: Drug ↔ Drug (bidirectional)

    Attributes:
        interaction_type: Nature of interaction (synergistic, antagonistic, additive)
        severity: Clinical severity (major, moderate, minor)
        mechanism: Pharmacological mechanism of interaction
        clinical_significance: Description of clinical implications

    Example:
        >>> interaction = InteractsWith(
        ...     subject_id="RxNorm:123",  # Warfarin
        ...     object_id="RxNorm:456",  # Aspirin
        ...     predicate="INTERACTS_WITH",
        ...     evidence_ids=["PMC789:discussion:3:llm"],
        ...     interaction_type="synergistic",
        ...     severity="major",
        ...     mechanism="Additive anticoagulant effect",
        ...     clinical_significance="Increased bleeding risk",
        ...     source_papers=["PMC789"],
        ...     confidence=0.90
        ... )
    """

    interaction_type: Optional[Literal["synergistic", "antagonistic", "additive"]] = None
    severity: Optional[Literal["major", "moderate", "minor"]] = None
    mechanism: Optional[str] = None
    clinical_significance: Optional[str] = None

    def get_edge_type(self) -> str:
        return "INTERACTS_WITH"


class ContraindicatedFor(BaseMedicalRelationship):
    """
    Drug -[CONTRAINDICATED_FOR]-> Disease/Condition

    Attributes:
        severity: Contraindication severity (absolute, relative)
        reason: Why contraindicated
    """

    severity: Optional[Literal["absolute", "relative"]] = None
    reason: Optional[str] = None

    def get_edge_type(self) -> str:
        return "CONTRAINDICATED_FOR"


class DiagnosedBy(BaseMedicalRelationship):
    """
    Represents diagnostic tests or biomarkers used to diagnose a disease.

    Direction: Disease → Procedure/Biomarker

    Attributes:
        sensitivity: True positive rate (0.0-1.0)
        specificity: True negative rate (0.0-1.0)
        standard_of_care: Whether this is standard clinical practice

    Example:
        >>> diagnosis = DiagnosedBy(
        ...     subject_id="C0006142",  # Breast Cancer
        ...     object_id="LOINC:123",  # Mammography
        ...     predicate="DIAGNOSED_BY",
        ...     evidence_ids=["PMC555:methods:2:llm"],
        ...     sensitivity=0.87,
        ...     specificity=0.91,
        ...     standard_of_care=True,
        ...     source_papers=["PMC555"],
        ...     confidence=0.88
        ... )
    """

    sensitivity: Optional[float] = Field(None, ge=0.0, le=1.0)
    specificity: Optional[float] = Field(None, ge=0.0, le=1.0)
    standard_of_care: bool = False

    def get_edge_type(self) -> str:
        return "DIAGNOSED_BY"


class ParticipatesIn(BaseMedicalRelationship):
    """
    Gene/Protein -[PARTICIPATES_IN]-> Pathway

    Attributes:
        role: Function in pathway
        regulatory_effect: Type of regulation (activates, inhibits, modulates)
    """

    role: Optional[str] = None
    regulatory_effect: Optional[Literal["activates", "inhibits", "modulates"]] = None

    def get_edge_type(self) -> str:
        return "PARTICIPATES_IN"


# Biological
class Encodes(BaseRelationship):
    def get_edge_type(self) -> str:
        return "ENCODES"


class BindsTo(BaseRelationship):
    def get_edge_type(self) -> str:
        return "BINDS_TO"


class Inhibits(BaseRelationship):
    def get_edge_type(self) -> str:
        return "INHIBITS"


class Upregulates(BaseRelationship):
    def get_edge_type(self) -> str:
        return "UPREGULATES"


class Downregulates(BaseRelationship):
    def get_edge_type(self) -> str:
        return "DOWNREGULATES"


class SubtypeOf(BaseMedicalRelationship):
    """
    When one disease is a subtype of another disease
    """

    def get_edge_type(self) -> str:
        return "SUBTYPE_OF"


# Research Metadata Relationships
class ResearchRelationship(BaseRelationship):
    """
    Base class for research metadata relationships.

    These relationships connect papers, authors, and clinical trials.
    Unlike medical relationships, they don't require provenance tracking
    since they represent bibliographic metadata rather than medical claims.

    Attributes:
        subject_id: ID of the subject entity
        predicate: Relationship type
        object_id: ID of the object entity
        properties: Flexible dict for relationship-specific properties
    """

    properties: dict = Field(default_factory=dict)


class Cites(ResearchRelationship):
    """
    Represents a citation from one paper to another.

    Direction: Paper → Paper (citing → cited)

    Attributes:
        context: Section where citation appears
        sentiment: How the citation is used (supports, contradicts, mentions)
    """

    context: Optional[Literal["introduction", "methods", "results", "discussion"]] = None
    sentiment: Optional[Literal["supports", "contradicts", "mentions"]] = None

    def get_edge_type(self) -> str:
        return "CITES"


class StudiedIn(ResearchRelationship):
    """
    Links medical entities to papers that study them.

    Direction: Any medical entity → Paper

    Attributes:
        role: Importance in the paper (primary_focus, secondary_finding, mentioned)
        section: Where discussed (results, methods, discussion, introduction)
    """

    role: Optional[Literal["primary_focus", "secondary_finding", "mentioned"]] = None
    section: Optional[Literal["results", "methods", "discussion", "introduction"]] = None

    def get_edge_type(self) -> str:
        return "STUDIED_IN"


class AuthoredBy(ResearchRelationship):
    """
    Paper -[AUTHORED_BY]-> Author

    Attributes:
        position: Author position (first, last, corresponding, middle)
    """

    position: Optional[Literal["first", "last", "corresponding", "middle"]] = None

    def get_edge_type(self) -> str:
        return "AUTHORED_BY"


class PartOf(ResearchRelationship):
    """
    Paper -[PART_OF]-> ClinicalTrial

    Attributes:
        publication_type: Type of publication (protocol, results, analysis)
    """

    publication_type: Optional[Literal["protocol", "results", "analysis"]] = None

    def get_edge_type(self) -> str:
        return "PART_OF"


class SameAs(ResearchRelationship):
    """
    Provisional identity link between two entities.

    Not a BaseMedicalRelationship — no evidence_ids required.
    Direction: conventionally lower bundle ID → higher bundle ID.

    Attributes:
        confidence: Strength of identity claim (0.0-1.0)
        resolution: Outcome after review ("merged", "distinct", null = unreviewed)
        note: Free text explaining the ambiguity
    """

    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    resolution: Optional[Literal["merged", "distinct"]] = None
    note: Optional[str] = None

    def get_edge_type(self) -> str:
        return "SAME_AS"


class Indicates(BaseMedicalRelationship):
    """
    Biomarker or test result indicates disease or condition.

    Direction: Biomarker / Evidence → Disease
    """

    def get_edge_type(self) -> str:
        return "INDICATES"


# Hypothesis Relationships
class Predicts(BaseMedicalRelationship):
    """
    Represents a hypothesis predicting an observable outcome.

    Direction: Hypothesis → Entity (Disease, Outcome, etc.)

    Attributes:
        prediction_type: Nature of prediction (positive, negative, conditional)
        conditions: Conditions under which prediction holds
        testable: Whether the prediction is empirically testable
    """

    prediction_type: Optional[Literal["positive", "negative", "conditional"]] = None
    conditions: Optional[str] = None
    testable: bool = True

    def get_edge_type(self) -> str:
        return "PREDICTS"


class Refutes(BaseMedicalRelationship):
    """
    Represents evidence that refutes a hypothesis.

    Direction: Evidence/Paper → Hypothesis

    Attributes:
        refutation_strength: Strength of refutation (strong, moderate, weak)
        alternative_explanation: Alternative explanation for observations
        limitations: Limitations of the refuting evidence
    """

    refutation_strength: Optional[Literal["strong", "moderate", "weak"]] = None
    alternative_explanation: Optional[str] = None
    limitations: Optional[str] = None

    def get_edge_type(self) -> str:
        return "REFUTES"


class TestedBy(BaseMedicalRelationship):
    """
    Represents a hypothesis being tested by a study or clinical trial.

    Direction: Hypothesis → Paper/ClinicalTrial

    Attributes:
        test_outcome: Result of the test (supported, refuted, inconclusive)
        methodology: Study methodology used
        study_design_id: OBI study design ID
    """

    test_outcome: Optional[Literal["supported", "refuted", "inconclusive"]] = None
    methodology: Optional[str] = None
    study_design_id: Optional[str] = None

    def get_edge_type(self) -> str:
        return "TESTED_BY"


class Supports(BaseMedicalRelationship):
    """
    Evidence supports a hypothesis or claim.

    Direction: Evidence → Hypothesis

    Attributes:
        support_strength: Strength of support (strong, moderate, weak)
    """

    support_strength: Optional[Literal["strong", "moderate", "weak"]] = None

    def get_edge_type(self) -> str:
        return "SUPPORTS"


class Generates(BaseMedicalRelationship):
    """
    Represents a study generating evidence for analysis.

    Direction: ClinicalTrial/Paper → Evidence

    Attributes:
        evidence_type: Type of evidence generated (experimental, observational, etc.)
        eco_type: ECO evidence type ID
        quality_score: Quality assessment score
    """

    evidence_type: Optional[str] = None
    eco_type: Optional[str] = None
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)

    def get_edge_type(self) -> str:
        return "GENERATES"


# Relationship Factory
# Map predicate strings to relationship classes
RELATIONSHIP_TYPE_MAP = {
    # Medical - Therapeutic
    "TREATS": Treats,
    "PREVENTS": Prevents,
    "CONTRAINDICATED_FOR": ContraindicatedFor,
    "SIDE_EFFECT": SideEffect,
    # Medical - Causal
    "CAUSES": Causes,
    "INCREASES_RISK": IncreasesRisk,
    # Medical - General
    "ASSOCIATED_WITH": AssociatedWith,
    "INTERACTS_WITH": InteractsWith,
    "DIAGNOSED_BY": DiagnosedBy,
    "PARTICIPATES_IN": ParticipatesIn,
    "INDICATES": Indicates,
    "SUBTYPE_OF": SubtypeOf,
    # Identity
    "SAME_AS": SameAs,
    # Biological
    "ENCODES": Encodes,
    "BINDS_TO": BindsTo,
    "INHIBITS": Inhibits,
    "UPREGULATES": Upregulates,
    "DOWNREGULATES": Downregulates,
    # Research Metadata
    "CITES": Cites,
    "STUDIED_IN": StudiedIn,
    "AUTHORED_BY": AuthoredBy,
    "PART_OF": PartOf,
    # Hypothesis
    "PREDICTS": Predicts,
    "REFUTES": Refutes,
    "TESTED_BY": TestedBy,
    "SUPPORTS": Supports,
    "GENERATES": Generates,
}


def create_relationship(predicate: str, subject_id: str, object_id: str, **kwargs) -> BaseRelationship:
    """
    Factory function for creating typed relationship instances.

    Provides type-safe relationship creation with predicate validation.
    Returns the appropriate relationship subclass based on predicate.

    Args:
        predicate: Relationship type (must match RELATIONSHIP_TYPE_MAP keys)
        subject_id: Entity ID of the subject
        object_id: Entity ID of the object
        **kwargs: Relationship-specific fields (evidence_ids, confidence, etc.)

    Returns:
        Typed relationship instance (Treats, Causes, Cites, etc.)

    Raises:
        ValueError: If predicate is not recognized

    Example:
        >>> rel = create_relationship(
        ...     predicate="TREATS",
        ...     subject_id="RxNorm:1187832",
        ...     object_id="C0006142",
        ...     evidence_ids=["PMC123:results:5:rct"],
        ...     response_rate=0.59,
        ...     confidence=0.85
        ... )
        >>> isinstance(rel, Treats)
        True
    """
    if predicate not in RELATIONSHIP_TYPE_MAP:
        raise ValueError(f"Unknown predicate: {predicate}. " f"Valid predicates: {sorted(RELATIONSHIP_TYPE_MAP.keys())}")

    relationship_class = RELATIONSHIP_TYPE_MAP[predicate]
    return relationship_class(subject_id=subject_id, predicate=predicate, object_id=object_id, **kwargs)

"""Base models for the medlit schema."""

from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class ModelInfo(BaseModel):
    """Information about the model used for extraction."""

    name: str
    version: str


class ExtractionProvenance(BaseModel):
    """
    Complete provenance metadata for an extraction.

    This is the complete audit trail of how extraction was performed.
    Enables:
    - Reproducing exact extraction with same code/models/prompts
    - Comparing outputs from different pipeline versions
    - Debugging quality issues
    - Tracking pipeline evolution over time
    - Meeting reproducibility requirements for research

    Example queries enabled by provenance:
    - "Find all papers extracted with prompt v1 so I can re-extract with v2"
    - "Which papers were extracted with uncommitted code changes?"
    - "Compare entity extraction quality between llama3.1:70b and claude-4"

    Attributes:
        extraction_pipeline: Pipeline version info
        models: Models used, keyed by role (e.g., 'llm', 'embeddings')
        prompt: Prompt version info
        execution: Execution environment info
        entity_resolution: Entity resolution details if applicable
    """

    extraction_pipeline: Optional["ExtractionPipelineInfo"] = None
    models: dict[str, ModelInfo] = Field(default_factory=dict)
    prompt: Optional["PromptInfo"] = None
    execution: Optional["ExecutionInfo"] = None
    entity_resolution: Optional["EntityResolutionInfo"] = None

    # Legacy support - keep model_info for backward compatibility
    model_info: Optional[ModelInfo] = None


class SectionType(str, Enum):
    """Type of section in a paper."""

    ABSTRACT = "abstract"
    INTRODUCTION = "introduction"
    METHODS = "methods"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"


class TextSpanRef(BaseModel):
    """A structural locator for text within a parsed document.

    This is a parser/segmentation address that uses structural coordinates
    (section type, paragraph index, sentence index) to locate text. It is
    distinct from TextSpan (entity.py), which is a graph entity anchor with
    precise character offsets.

    Use this for:
    - Intermediate parsing stages before final offsets are computed
    - Structural navigation within documents
    - Creating TextSpan entities once offsets are finalized

    Attributes:
        paper_id: The ID of the paper this span belongs to.
        section_type: The type of section (abstract, introduction, etc.).
        paragraph_idx: Zero-based paragraph index within the section.
        sentence_idx: Optional sentence index within the paragraph.
        text_span: Optional text snippet for reference.
        start_offset: Optional character offset (for when computed).
        end_offset: Optional character offset (for when computed).
    """

    paper_id: str

    section_type: SectionType

    paragraph_idx: int

    sentence_idx: Optional[int] = None

    text_span: Optional[str] = None

    start_offset: Optional[int] = None

    end_offset: Optional[int] = None


class ExtractionMethod(str, Enum):
    """Method used for extraction."""

    SCISPACY_NER = "scispacy_ner"

    LLM = "llm"

    TABLE_PARSER = "table_parser"

    PATTERN_MATCH = "pattern_match"

    MANUAL = "manual"


class StudyType(str, Enum):
    """Type of study."""

    OBSERVATIONAL = "observational"

    RCT = "rct"

    META_ANALYSIS = "meta_analysis"

    CASE_REPORT = "case_report"

    REVIEW = "review"


class PredicateType(str, Enum):
    """
    All possible predicates (relationship types) in the medical literature knowledge graph.

    This enum provides type safety for relationship categorization and enables
    validation of entity-relationship compatibility.
    """

    # Research/Bibliographic
    AUTHORED_BY = "authored_by"
    CITES = "cites"
    STUDIED_IN = "studied_in"

    # Medical - Causal
    CAUSES = "causes"
    PREVENTS = "prevents"
    INCREASES_RISK = "increases_risk"
    DECREASES_RISK = "decreases_risk"

    # Medical - Therapeutic
    TREATS = "treats"
    MANAGES = "manages"
    CONTRAINDICATED_FOR = "contraindicated_for"
    SIDE_EFFECT = "side_effect"

    # Biological - Molecular
    BINDS_TO = "binds_to"
    INHIBITS = "inhibits"
    ACTIVATES = "activates"
    UPREGULATES = "upregulates"
    DOWNREGULATES = "downregulates"
    ENCODES = "encodes"
    METABOLIZES = "metabolizes"
    PARTICIPATES_IN = "participates_in"

    # Diagnostic
    DIAGNOSES = "diagnoses"
    DIAGNOSED_BY = "diagnosed_by"
    INDICATES = "indicates"

    # Relationships
    PRECEDES = "precedes"
    CO_OCCURS_WITH = "co_occurs_with"
    ASSOCIATED_WITH = "associated_with"
    INTERACTS_WITH = "interacts_with"
    SUBTYPE_OF = "subtype_of"

    # Identity (provisional same-entity links)
    SAME_AS = "same_as"

    # Location
    LOCATED_IN = "located_in"
    AFFECTS = "affects"

    # Scientific Method
    PREDICTS = "predicts"
    REFUTES = "refutes"
    TESTED_BY = "tested_by"
    SUPPORTS = "supports"

    # Research Metadata
    CITED_BY = "cited_by"
    CONTRADICTS = "contradicts"
    PART_OF = "part_of"
    GENERATES = "generates"


class EntityType(str, Enum):
    """
    All possible entity types in the knowledge graph.

    This enum provides type safety for entity categorization and enables
    validation of entity-relationship compatibility.
    """

    # Core medical entities
    DISEASE = "disease"
    SYMPTOM = "symptom"
    DRUG = "drug"
    GENE = "gene"
    MUTATION = "mutation"
    PROTEIN = "protein"
    PATHWAY = "pathway"
    ANATOMICAL_STRUCTURE = "anatomical_structure"
    PROCEDURE = "procedure"
    TEST = "test"
    BIOMARKER = "biomarker"

    # Research metadata
    PAPER = "paper"
    AUTHOR = "author"
    INSTITUTION = "institution"
    CLINICAL_TRIAL = "clinical_trial"

    # Scientific method entities (ontology-based)
    HYPOTHESIS = "hypothesis"  # IAO:0000018
    STUDY_DESIGN = "study_design"  # OBI study designs
    STATISTICAL_METHOD = "statistical_method"  # STATO methods
    EVIDENCE_LINE = "evidence_line"  # SEPIO evidence structures


class ClaimPredicate(BaseModel):
    """
    Describes the nature of a claim made in a paper.

    Examples:
        - "Olaparib significantly improved progression-free survival" (TREATS)
        - "BRCA1 mutations increase breast cancer risk by 5-fold" (INCREASES_RISK)
        - "Warfarin and aspirin interact synergistically" (INTERACTS_WITH)

    Attributes:
        predicate_type: The type of relationship asserted in the claim
        description: A natural language description of the predicate as it appears in the text
    """

    predicate_type: PredicateType
    description: str


class Provenance(BaseModel):
    """
    Information about the origin of a piece of data.

    Attributes:
        source_type: The type of source (e.g., 'paper', 'database', 'model_extraction')
        source_id: An identifier for the source (e.g., DOI, database record ID)
        source_version: The version of the source, if applicable
        notes: Additional notes about the provenance
    """

    source_type: str
    source_id: str
    source_version: Optional[str] = None
    notes: Optional[str] = None


class EvidenceType(BaseModel):
    """
    The type of evidence supporting a relationship, linked to evidence ontologies.

    Examples:
        - RCT: ontology_id="ECO:0007673", ontology_label="randomized controlled trial evidence"
        - Observational: ontology_id="ECO:0000203", ontology_label="observational study evidence"
        - Case report: ontology_id="ECO:0006016", ontology_label="case study evidence"

    Attributes:
        ontology_id: Identifier from an evidence ontology (ECO, SEPIO)
        ontology_label: Human-readable label for the ontology term
        description: A fuller description of the evidence type
    """

    ontology_id: str
    ontology_label: str
    description: Optional[str] = None


class EntityReference(BaseModel):
    """
    Reference to an entity in the knowledge graph.

    Lightweight pointer to a canonical entity (Disease, Drug, Gene, etc.)
    with the name as it appeared in this specific paper.

    Attributes:
        id: Canonical entity ID
        name: Entity name as mentioned in paper
        type: Entity type (drug, disease, gene, protein, etc.)
    """

    id: str = Field(..., description="Canonical entity ID")
    name: str = Field(..., description="Entity name as mentioned in paper")
    type: EntityType = Field(..., description="Entity type")


class Polarity(str, Enum):
    """Polarity of evidence relative to a claim."""

    SUPPORTS = "supports"
    REFUTES = "refutes"
    NEUTRAL = "neutral"


# Edge type hierarchy
PaperId = uuid.UUID
EdgeId = uuid.UUID


class Edge(BaseModel):
    """Base edge in the knowledge graph."""

    id: EdgeId
    subject: EntityReference
    object: EntityReference
    provenance: Provenance


class ExtractionEdge(Edge):
    """Edge from automated extraction."""

    extractor: ModelInfo
    confidence: float


class ClaimEdge(Edge):
    """Edge representing a claim from a paper."""

    predicate: ClaimPredicate
    asserted_by: PaperId
    polarity: Polarity


class EvidenceEdge(Edge):
    """Edge representing evidence for a claim."""

    evidence_type: EvidenceType
    strength: float


# Provenance Metadata Classes
class ExtractionPipelineInfo(BaseModel):
    """
    Information about the extraction pipeline version.

    Tracks the exact code version that performed entity/relationship extraction.
    Essential for reproducibility and debugging extraction quality issues.

    Attributes:
        name: Pipeline name (e.g., 'ollama_langchain_ingest')
        version: Semantic version of the pipeline
        git_commit: Full git commit hash
        git_commit_short: Short git commit hash (7 chars)
        git_branch: Git branch name
        git_dirty: Whether working directory had uncommitted changes
        repo_url: Repository URL
    """

    name: str
    version: str
    git_commit: str
    git_commit_short: str
    git_branch: str
    git_dirty: bool
    repo_url: str


class PromptInfo(BaseModel):
    """
    Information about the prompt used.

    Tracks prompt evolution. Critical for understanding extraction behavior changes.

    Attributes:
        version: Prompt version identifier
        template: Prompt template name
        checksum: SHA256 of actual prompt text for exact reproduction
        schema_version: 8-char hex hash of config (entity_types, predicates, domain_instructions)
    """

    version: str
    template: str
    checksum: Optional[str] = None
    schema_version: Optional[str] = None


class ExecutionInfo(BaseModel):
    """
    Information about when and where extraction was performed.

    Useful for debugging issues related to specific machines or time periods.

    Attributes:
        timestamp: ISO 8601 UTC timestamp
        hostname: Hostname of machine that ran extraction
        python_version: Python version
        duration_seconds: Extraction duration in seconds
    """

    timestamp: str
    hostname: str
    python_version: str
    duration_seconds: Optional[float] = None


class EntityResolutionInfo(BaseModel):
    """
    Information about entity resolution process.

    Tracks how entities were matched to canonical IDs. Helps identify when
    entity deduplication is working poorly.

    Attributes:
        canonical_entities_matched: Number of entities matched to existing canonical IDs
        new_entities_created: Number of new canonical entities created
        similarity_threshold: Similarity threshold used for matching
        embedding_model: Embedding model used for similarity
    """

    canonical_entities_matched: int
    new_entities_created: int
    similarity_threshold: float
    embedding_model: str


class Measurement(BaseModel):
    """
    Quantitative measurements associated with relationships.

    Stores numerical data with appropriate metadata for statistical
    analysis and evidence quality assessment.

    Attributes:
        value: The numerical value
        unit: Unit of measurement (if applicable)
        value_type: Type of measurement (effect_size, p_value, etc.)
        p_value: Statistical significance
        confidence_interval: 95% confidence interval
        study_population: Description of study population
        measurement_context: Additional context about the measurement

    Example:
        >>> measurement = Measurement(
        ...     value=0.59,
        ...     value_type="response_rate",
        ...     p_value=0.001,
        ...     confidence_interval=(0.52, 0.66),
        ...     study_population="BRCA-mutated breast cancer patients"
        ... )
    """

    value: float
    unit: Optional[str] = None
    value_type: str
    p_value: Optional[float] = None
    confidence_interval: Optional[tuple[float, float]] = None
    study_population: Optional[str] = None
    measurement_context: Optional[str] = None

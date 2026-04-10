"""Medlit entity definitions."""

from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, field_validator, model_validator
from kgschema.entity import BaseEntity, EntityStatus
from medlit_schema.base import ExtractionProvenance, ExtractionMethod, StudyType


# Base for medical entities
class BaseMedicalEntity(BaseEntity):
    """Base for all medical entities."""

    name: str
    synonyms: tuple[str, ...] = ()
    abbreviations: List[str] = []
    embedding: Optional[tuple[float, ...]] = None
    source: Literal["umls", "mesh", "rxnorm", "hgnc", "uniprot", "extracted"]

    @model_validator(mode="after")
    def canonical_entities_have_ontology_ids(self):
        if self.source != "extracted":
            # This is not a comprehensive list of all possible id fields.
            # It's a sample of the most common ones.
            ontology_id_fields = ["umls_id", "mesh_id", "rxnorm_id", "hgnc_id", "uniprot_id"]
            if not any(getattr(self, field) for field in ontology_id_fields if hasattr(self, field)):
                raise ValueError("Canonical entities must have an ontology ID")
        return self


# Biomedical Core
class Disease(BaseMedicalEntity):
    """
    Represents medical conditions, disorders, and syndromes.

    Uses UMLS as the primary identifier system with additional mappings to
    MeSH and ICD-10 for interoperability with clinical systems.

    Attributes:
        umls_id: UMLS Concept ID (e.g., "C0006142" for Breast Cancer)
        mesh_id: Medical Subject Heading ID for literature indexing
        icd10_codes: List of ICD-10 diagnostic codes
        category: Disease classification (genetic, infectious, autoimmune, etc.)

    Example:
        >>> breast_cancer = Disease(
        ...     entity_id="C0006142",
        ...     name="Breast Cancer",
        ...     synonyms=("Breast Carcinoma", "Mammary Cancer"),
        ...     umls_id="C0006142",
        ...     mesh_id="D001943",
        ...     icd10_codes=["C50.9"],
        ...     category="genetic",
        ...     source="umls"
        ... )
    """

    umls_id: Optional[str] = None
    mesh_id: Optional[str] = None
    icd10_codes: List[str] = []
    category: Optional[str] = None

    def get_entity_type(self) -> str:
        return "disease"


class Gene(BaseMedicalEntity):
    """
    Represents human genes.

    Uses HGNC (HUGO Gene Nomenclature Committee) as the primary identifier
    with additional mappings to Entrez Gene for cross-reference.

    Attributes:
        symbol: Official gene symbol (e.g., "BRCA1")
        hgnc_id: HGNC identifier (e.g., "HGNC:1100")
        chromosome: Chromosomal location (e.g., "17q21.31")
        entrez_id: NCBI Entrez Gene ID

    Example:
        >>> brca1 = Gene(
        ...     entity_id="HGNC:1100",
        ...     name="BRCA1",
        ...     symbol="BRCA1",
        ...     hgnc_id="HGNC:1100",
        ...     chromosome="17q21.31",
        ...     entrez_id="672",
        ...     source="hgnc"
        ... )
    """

    symbol: Optional[str] = None
    hgnc_id: Optional[str] = None
    chromosome: Optional[str] = None
    entrez_id: Optional[str] = None

    def get_entity_type(self) -> str:
        return "gene"


class Drug(BaseMedicalEntity):
    """
    Represents pharmaceutical drugs and medications.

    Uses RxNorm as the primary identifier system for standardized drug names.

    Attributes:
        rxnorm_id: RxNorm concept identifier (e.g., "1187832" for Olaparib)
        brand_names: Commercial brand names (e.g., ["Lynparza"])
        drug_class: Pharmacological class (e.g., "PARP inhibitor")
        mechanism: Mechanism of action description

    Example:
        >>> olaparib = Drug(
        ...     entity_id="RxNorm:1187832",
        ...     name="Olaparib",
        ...     rxnorm_id="1187832",
        ...     brand_names=["Lynparza"],
        ...     drug_class="PARP inhibitor",
        ...     mechanism="Inhibits PARP enzymes",
        ...     source="rxnorm"
        ... )
    """

    rxnorm_id: Optional[str] = None
    brand_names: List[str] = []
    drug_class: Optional[str] = None
    mechanism: Optional[str] = None

    def get_entity_type(self) -> str:
        return "drug"


class Protein(BaseMedicalEntity):
    """
    Represents proteins and protein complexes.

    Uses UniProt as the primary identifier system.

    Attributes:
        uniprot_id: UniProt accession (e.g., "P38398" for BRCA1 protein)
        gene_id: Associated gene identifier
        function: Protein function description
        pathways: List of pathway IDs this protein participates in

    Example:
        >>> brca1_protein = Protein(
        ...     entity_id="UniProt:P38398",
        ...     name="BRCA1",
        ...     uniprot_id="P38398",
        ...     gene_id="HGNC:1100",
        ...     function="DNA repair",
        ...     pathways=["R-HSA-5685942"],
        ...     source="uniprot"
        ... )
    """

    uniprot_id: Optional[str] = None
    gene_id: Optional[str] = None
    function: Optional[str] = None
    pathways: List[str] = []

    def get_entity_type(self) -> str:
        return "protein"


class Mutation(BaseMedicalEntity):
    """
    Represents genetic mutations and variants.

    Attributes:
        variant_notation: HGVS notation (e.g., "c.68_69delAG")
        consequence: Effect of mutation (e.g., "frameshift", "missense")
        clinical_significance: ClinVar significance (pathogenic, benign, etc.)

    Example:
        >>> brca1_mutation = Mutation(
        ...     entity_id="BRCA1_c.68_69delAG",
        ...     name="BRCA1 c.68_69delAG",
        ...     variant_notation="c.68_69delAG",
        ...     consequence="frameshift",
        ...     clinical_significance="pathogenic",
        ...     source="extracted"
        ... )
    """

    variant_notation: Optional[str] = None
    consequence: Optional[str] = None
    clinical_significance: Optional[str] = None

    def get_entity_type(self) -> str:
        return "mutation"


class Symptom(BaseMedicalEntity):
    """
    Represents clinical signs and symptoms.

    Attributes:
        severity_scale: Measurement scale if applicable (e.g., "0-10", "mild/moderate/severe")
        onset_pattern: Typical onset (acute, chronic, intermittent)

    Example:
        >>> pain = Symptom(
        ...     entity_id="C0030193",
        ...     name="Pain",
        ...     umls_id="C0030193",
        ...     severity_scale="0-10",
        ...     onset_pattern="varies",
        ...     source="umls"
        ... )
    """

    severity_scale: Optional[str] = None
    onset_pattern: Optional[str] = None

    def get_entity_type(self) -> str:
        return "symptom"


class Biomarker(BaseMedicalEntity):
    """
    Represents biological markers used for diagnosis or prognosis.

    Attributes:
        loinc_code: LOINC code for lab tests
        measurement_type: Type of measurement (protein, metabolite, imaging, etc.)
        clinical_use: Primary clinical application

    Example:
        >>> ca125 = Biomarker(
        ...     entity_id="LOINC:10334-1",
        ...     name="CA-125",
        ...     loinc_code="10334-1",
        ...     measurement_type="protein",
        ...     clinical_use="ovarian cancer screening",
        ...     source="extracted"
        ... )
    """

    loinc_code: Optional[str] = None
    measurement_type: Optional[str] = None
    clinical_use: Optional[str] = None

    def get_entity_type(self) -> str:
        return "biomarker"


class Pathway(BaseMedicalEntity):
    """
    Represents biological pathways.

    Attributes:
        kegg_id: KEGG pathway identifier
        reactome_id: Reactome pathway identifier
        pathway_type: Type of pathway (signaling, metabolic, etc.)

    Example:
        >>> dna_repair = Pathway(
        ...     entity_id="R-HSA-5685942",
        ...     name="HDR through Homologous Recombination",
        ...     reactome_id="R-HSA-5685942",
        ...     pathway_type="DNA repair",
        ...     source="extracted"
        ... )
    """

    kegg_id: Optional[str] = None
    reactome_id: Optional[str] = None
    pathway_type: Optional[str] = None

    def get_entity_type(self) -> str:
        return "pathway"


class Procedure(BaseMedicalEntity):
    """
    Represents medical tests, diagnostics, treatments.

    Attributes:
        type: Procedure category (diagnostic, therapeutic, preventive)
        invasiveness: Invasiveness level (non-invasive, minimally invasive, invasive)
    """

    type: Optional[str] = None
    invasiveness: Optional[str] = None

    def get_entity_type(self) -> str:
        return "procedure"


# Paper/Bibliographic
class PaperMetadata(BaseModel):
    """
    Extended metadata about the research paper.

    Combines study characteristics (for evidence quality assessment) with
    bibliographic information (for citations and filtering).

    This is MORE than just storage - these fields enable critical queries:
    - "Show me only RCT evidence for this drug-disease relationship"
    - "What's the sample size distribution for studies on this topic?"
    - "Find papers from high-impact journals on this mutation"

    Attributes:
        study_type: Type of study (observational, rct, meta_analysis, case_report, review)
        sample_size: Study sample size - larger = more reliable
        study_population: Description of study population
        primary_outcome: Primary outcome measured
        clinical_phase: Clinical trial phase if applicable
        mesh_terms: Medical Subject Headings - NLM's controlled vocabulary for indexing

    Example:
        >>> metadata = PaperMetadata(
        ...     study_type="rct",
        ...     sample_size=302,
        ...     study_population="Women with BRCA1/2-mutated metastatic breast cancer",
        ...     primary_outcome="Progression-free survival",
        ...     clinical_phase="III",
        ...     mesh_terms=["Breast Neoplasms", "BRCA1 Protein", "PARP Inhibitors"]
        ... )
    """

    study_type: Optional[str] = None
    sample_size: Optional[int] = None
    study_population: Optional[str] = None
    primary_outcome: Optional[str] = None
    clinical_phase: Optional[str] = None
    mesh_terms: List[str] = []


class TextSpan(BaseEntity):
    """
    Represents a specific span of text within a document, acting as an anchor for evidence.

    This entity provides fine-grained provenance for assertions by linking them
    to exact locations within a source paper. It serves as a first-class entity
    that can be referenced by Evidence.

    TextSpan is canonical-only (not promotable) because:
    - Character offsets are stable only relative to a specific text representation
    - The combination of paper_id + section + offsets provides a natural canonical ID
    - There is no meaningful "provisional" state for a text location

    Note: This is distinct from TextSpanRef (base.py), which is a structural locator
    using paragraph/sentence indices for parsing stages before final offsets are computed.

    Attributes:
        paper_id: The ID of the paper this text span belongs to.
        section: The section of the paper (e.g., "abstract", "introduction", "results").
        start_offset: The character offset where the span starts in the section content (required).
        end_offset: The character offset where the span ends in the section content (required).
        text_content: The actual text content of the span (optional, for convenience and caching).
    """

    promotable: bool = False
    status: EntityStatus = EntityStatus.CANONICAL

    paper_id: str
    section: str
    start_offset: int
    end_offset: int
    text_content: Optional[str] = None

    @field_validator("end_offset")
    def end_must_be_greater_than_start(cls, v, info):  # pylint: disable=no-self-argument
        """Validate that end_offset > start_offset."""
        start = info.data.get("start_offset")
        if start is not None and v <= start:
            raise ValueError(f"end_offset ({v}) must be greater than start_offset ({start})")
        return v

    def get_entity_type(self) -> str:
        return "text_span"


class Paper(BaseEntity):
    """
    A research paper with extracted entities, relationships, and full provenance.

    This is the COMPLETE representation of a paper in the knowledge graph, combining:

    1. Bibliographic metadata (authors, journal, identifiers)
    2. Text content (title, abstract)
    3. Study metadata (study type, sample size, etc.)
    4. Extraction provenance (how extraction was performed)

    Design philosophy:

    - Top-level fields are FREQUENTLY QUERIED (paper_id, title, authors, publication_date)
    - Nested objects group related data (paper_metadata for study info, extraction_provenance for pipeline info)

    Why certain fields are top-level:

    - paper_id: Primary key, referenced everywhere
    - title, abstract: Core content, always displayed
    - authors: Essential for citations, frequently filtered
    - publication_date: Frequently used for filtering by recency
    - journal: Frequently used for quality filtering

    Why other fields are nested:

    - paper_metadata: Study details, accessed together for evidence assessment
    - extraction_provenance: Technical details, only for debugging/reproducibility

    Attributes:
        paper_id: Unique identifier - PMC ID preferred, but can be DOI or PMID
        pmid: PubMed ID - different from PMC ID
        doi: Digital Object Identifier
        title: Full paper title
        abstract: Complete abstract text
        authors: List of author names in citation order
        publication_date: Publication date in ISO format (YYYY-MM-DD)
        journal: Journal name
        paper_metadata: Extended metadata including study type, sample size, MeSH terms
        extraction_provenance: Complete provenance of how extraction was performed

    Example:
        >>> paper = Paper(
        ...     entity_id="PMC8437152",
        ...     paper_id="PMC8437152",
        ...     pmid="34567890",
        ...     doi="10.1234/nejm.2023.001",
        ...     title="Efficacy of Olaparib in BRCA-Mutated Breast Cancer",
        ...     abstract="Background: PARP inhibitors have shown promise...",
        ...     authors=["Smith J", "Johnson A", "Williams K"],
        ...     publication_date=datetime(2023, 6, 15),
        ...     journal="New England Journal of Medicine",
        ...     paper_metadata=PaperMetadata(
        ...         study_type="rct",
        ...         sample_size=302,
        ...         mesh_terms=["Breast Neoplasms", "PARP Inhibitors"]
        ...     )
        ... )
    """

    paper_id: str  # PMC ID
    pmid: Optional[str] = None
    doi: Optional[str] = None
    title: Optional[str] = None
    abstract: Optional[str] = None
    authors: List[str] = []
    publication_date: Optional[datetime] = None
    journal: Optional[str] = None
    paper_metadata: PaperMetadata = PaperMetadata()
    extraction_provenance: Optional[ExtractionProvenance] = None

    def get_entity_type(self) -> str:
        return "paper"


class Author(BaseEntity):
    """
    Represents a researcher or author of scientific publications.

    Attributes:
        orcid: ORCID identifier (unique researcher ID)
        affiliations: List of institutional affiliations
        h_index: Citation metric indicating research impact

    Example:
        >>> author = Author(
        ...     entity_id="0000-0001-2345-6789",
        ...     name="Jane Smith",
        ...     orcid="0000-0001-2345-6789",
        ...     affiliations=["Harvard Medical School", "Massachusetts General Hospital"],
        ...     h_index=45,
        ...     source="orcid",
        ...     created_at=datetime.now()
        ... )
    """

    orcid: Optional[str] = None
    affiliations: List[str] = []
    h_index: Optional[int] = None

    def get_entity_type(self) -> str:
        return "author"


class ClinicalTrial(BaseEntity):
    """
    Represents a clinical trial registered on ClinicalTrials.gov.

    Attributes:
        nct_id: ClinicalTrials.gov identifier (e.g., "NCT01234567")
        title: Official trial title
        phase: Trial phase (I, II, III, IV)
        trial_status: Current status (recruiting, completed, terminated, etc.)
        intervention: Description of treatment being tested

    Example:
        >>> trial = ClinicalTrial(
        ...     entity_id="NCT01234567",
        ...     name="Study of Drug X in Patients with Disease Y",
        ...     nct_id="NCT01234567",
        ...     title="Study of Drug X in Patients with Disease Y",
        ...     phase="III",
        ...     trial_status="completed",
        ...     intervention="Drug X 100mg daily",
        ...     source="clinicaltrials.gov",
        ...     created_at=datetime.now()
        ... )
    """

    nct_id: Optional[str] = None
    title: Optional[str] = None
    phase: Optional[str] = None
    trial_status: Optional[str] = None
    intervention: Optional[str] = None

    def get_entity_type(self) -> str:
        return "clinical_trial"


class Institution(BaseEntity):
    """
    Represents research institutions and affiliations.

    Attributes:
        country: Country location
        department: Department or division

    Example:
        >>> institution = Institution(
        ...     entity_id="INST:harvard_med",
        ...     name="Harvard Medical School",
        ...     country="USA",
        ...     department="Oncology",
        ...     source="extracted",
        ...     created_at=datetime.now()
        ... )
    """

    country: Optional[str] = None
    department: Optional[str] = None

    def get_entity_type(self) -> str:
        return "institution"


# Scientific Method
class Hypothesis(BaseEntity):
    """
    Represents a scientific hypothesis tracked across the literature.

    Uses IAO (Information Artifact Ontology) for standardized representation
    of hypotheses as information content entities. Enables tracking of
    hypothesis evolution: from proposal through testing to acceptance/refutation.

    Attributes:
        iao_id: IAO identifier (typically IAO:0000018 for hypothesis)
        sepio_id: SEPIO identifier for assertions (SEPIO:0000001)
        proposed_by: Paper ID where hypothesis was first proposed
        proposed_date: Date when hypothesis was first proposed
        hypothesis_status: Current status (proposed, supported, controversial, refuted)
        description: Natural language description of the hypothesis
        predicts: List of entity IDs that this hypothesis predicts outcomes for

    Example:
        >>> hypothesis = Hypothesis(
        ...     entity_id="HYPOTHESIS:amyloid_cascade_alzheimers",
        ...     name="Amyloid Cascade Hypothesis",
        ...     iao_id="IAO:0000018",
        ...     sepio_id="SEPIO:0000001",
        ...     proposed_by="PMC123456",
        ...     proposed_date="1992",
        ...     hypothesis_status="controversial",
        ...     description="Beta-amyloid accumulation drives Alzheimer's disease pathology",
        ...     predicts=["C0002395"],
        ...     source="extracted",
        ...     created_at=datetime.now()
        ... )
    """

    iao_id: Optional[str] = None
    sepio_id: Optional[str] = None
    proposed_by: Optional[str] = None
    proposed_date: Optional[str] = None
    hypothesis_status: Optional[str] = None
    description: Optional[str] = None
    predicts: List[str] = []

    def get_entity_type(self) -> str:
        return "hypothesis"


class StudyDesign(BaseEntity):
    """
    Represents a study design or experimental protocol.

    Uses OBI (Ontology for Biomedical Investigations) to standardize
    study design classifications. Enables filtering by evidence quality
    based on study design.

    Attributes:
        obi_id: OBI identifier for study design type
        stato_id: STATO identifier for study design (if applicable)
        design_type: Human-readable design type
        description: Description of the study design
        evidence_level: Quality level (1-5, where 1 is highest quality)

    Example:
        >>> rct = StudyDesign(
        ...     entity_id="OBI:0000008",
        ...     name="Randomized Controlled Trial",
        ...     obi_id="OBI:0000008",
        ...     stato_id="STATO:0000402",
        ...     design_type="interventional",
        ...     evidence_level=1,
        ...     source="obi",
        ...     created_at=datetime.now()
        ... )
    """

    obi_id: Optional[str] = None
    stato_id: Optional[str] = None
    design_type: Optional[str] = None
    description: Optional[str] = None
    evidence_level: Optional[int] = None

    def get_entity_type(self) -> str:
        return "study_design"


class StatisticalMethod(BaseEntity):
    """
    Represents a statistical method or test used in analysis.

    Uses STATO (Statistics Ontology) to standardize statistical method
    classifications. Enables tracking of analytical approaches across studies.

    Attributes:
        stato_id: STATO identifier for the statistical method
        method_type: Category of method (hypothesis_test, regression, etc.)
        description: Description of the method
        assumptions: Key assumptions of the method

    Example:
        >>> ttest = StatisticalMethod(
        ...     entity_id="STATO:0000288",
        ...     name="Student's t-test",
        ...     stato_id="STATO:0000288",
        ...     method_type="hypothesis_test",
        ...     description="Parametric test comparing means of two groups",
        ...     source="stato",
        ...     created_at=datetime.now()
        ... )
    """

    stato_id: Optional[str] = None
    method_type: Optional[str] = None
    description: Optional[str] = None
    assumptions: List[str] = []

    def get_entity_type(self) -> str:
        return "statistical_method"


class EvidenceLine(BaseEntity):
    """
    Represents a line of evidence using SEPIO framework.

    Uses SEPIO (Scientific Evidence and Provenance Information Ontology)
    to represent structured evidence chains. Links evidence items to
    assertions they support or refute.

    Attributes:
        sepio_type: SEPIO evidence line type ID
        eco_type: ECO evidence type ID
        assertion_id: ID of the assertion this evidence supports
        supports_ids: List of hypothesis IDs this evidence supports
        refutes_ids: List of hypothesis IDs this evidence refutes
        evidence_items: List of paper IDs providing evidence
        strength: Evidence strength classification
        provenance_info: Provenance information

    Example:
        >>> evidence = EvidenceLine(
        ...     entity_id="EVIDENCE_LINE:olaparib_brca_001",
        ...     name="Clinical evidence for Olaparib in BRCA-mutated breast cancer",
        ...     sepio_type="SEPIO:0000084",
        ...     eco_type="ECO:0007673",
        ...     assertion_id="ASSERTION:olaparib_brca",
        ...     supports_ids=["HYPOTHESIS:parp_inhibitor_synthetic_lethality"],
        ...     evidence_items=["PMC999888", "PMC888777"],
        ...     strength="strong",
        ...     source="extracted",
        ...     created_at=datetime.now()
        ... )
    """

    sepio_type: Optional[str] = None
    eco_type: Optional[str] = None
    assertion_id: Optional[str] = None
    supports_ids: List[str] = []
    refutes_ids: List[str] = []
    evidence_items: List[str] = []
    strength: Optional[str] = None
    provenance_info: Optional[str] = None

    def get_entity_type(self) -> str:
        return "evidence_line"


class Evidence(BaseEntity):
    """
    Evidence for a relationship, treated as a first-class entity.

    Evidence entities have immediate canonical ID promotion using format:
    {paper_id}:{section}:{paragraph}:{method}

    Example canonical ID: "PMC8437152:results:5:llm"

    This format enables:
    - Immediate promotion (no provisional state needed)
    - Efficient lookups by paper/section
    - Deduplication across extraction runs
    - Database indexing for queries like "all evidence from Section 2"

    Attributes:
        entity_id: Canonical ID in format {paper_id}:{section}:{paragraph}:{method}
        paper_id: PMC ID of source paper
        text_span_id: Reference to TextSpan entity (for exact location)
        confidence: Confidence score 0.0-1.0
        extraction_method: Method used (scispacy_ner, llm, table_parser, pattern_match, manual)
        study_type: Type of study (observational, rct, meta_analysis, case_report, review)
        sample_size: Number of subjects in the study
        eco_type: ECO evidence type ID (e.g., "ECO:0007673" for RCT)
        obi_study_design: OBI study design ID (e.g., "OBI:0000008" for RCT)
        stato_methods: List of STATO statistical method IDs used

    Schema Rules:
    - entity_id MUST follow canonical ID format
    - paper_id and text_span_id MUST be non-empty
    - Evidence entities are immediately promotable (no usage threshold)

    Example:
        >>> evidence = Evidence(
        ...     entity_id="PMC999888:results:3:llm",
        ...     name="Evidence from Olaparib RCT results",
        ...     paper_id="PMC999888",
        ...     text_span_id="PMC999888:results:3",
        ...     confidence=0.92,
        ...     extraction_method=ExtractionMethod.LLM,
        ...     study_type=StudyType.RCT,
        ...     sample_size=302,
        ...     eco_type="ECO:0007673",
        ...     obi_study_design="OBI:0000008",
        ...     stato_methods=["STATO:0000288"],
        ...     source="extracted",
        ...     created_at=datetime.now()
        ... )
    """

    promotable: bool = False
    status: EntityStatus = EntityStatus.CANONICAL

    paper_id: str
    text_span_id: str
    confidence: float
    extraction_method: "ExtractionMethod"
    study_type: "StudyType"
    sample_size: Optional[int] = None
    eco_type: Optional[str] = None
    obi_study_design: Optional[str] = None
    stato_methods: List[str] = []

    @field_validator("paper_id", "text_span_id")
    def ids_must_not_be_empty(cls, v):  # pylint: disable=no-self-argument
        if not v:
            raise ValueError("paper_id and text_span_id must not be empty")
        return v

    def get_entity_type(self) -> str:
        return "evidence"

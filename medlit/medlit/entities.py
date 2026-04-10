"""Medical entity types for the knowledge graph."""

from kgschema.entity import BaseEntity


class DiseaseEntity(BaseEntity):
    """Represents medical conditions, disorders, and syndromes.

    Uses UMLS as the primary identifier system with additional mappings to
    MeSH and ICD-10 for interoperability with clinical systems.

    Mapping from med-lit-schema:
    - Disease.entity_id (UMLS ID) → BaseEntity.entity_id
    - Disease.umls_id → BaseEntity.canonical_ids["umls"]
    - Disease.mesh_id → BaseEntity.canonical_ids["mesh"]
    - Disease.icd10_codes → BaseEntity.metadata["icd10_codes"]
    - Disease.category → BaseEntity.metadata["category"]
    """

    def get_entity_type(self) -> str:
        return "disease"


class GeneEntity(BaseEntity):
    """Represents genes and their genomic information.

    Uses HGNC (HUGO Gene Nomenclature Committee) as the primary identifier
    with additional mappings to NCBI Entrez Gene.

    Mapping from med-lit-schema:
    - Gene.entity_id (HGNC ID) → BaseEntity.entity_id
    - Gene.hgnc_id → BaseEntity.canonical_ids["hgnc"]
    - Gene.entrez_id → BaseEntity.canonical_ids["entrez"]
    - Gene.symbol → BaseEntity.metadata["symbol"]
    - Gene.chromosome → BaseEntity.metadata["chromosome"]
    """

    def get_entity_type(self) -> str:
        return "gene"


class DrugEntity(BaseEntity):
    """Represents medications and therapeutic substances.

    Uses RxNorm as the primary identifier for standardized medication naming.

    Mapping from med-lit-schema:
    - Drug.entity_id (RxNorm ID) → BaseEntity.entity_id
    - Drug.rxnorm_id → BaseEntity.canonical_ids["rxnorm"]
    - Drug.brand_names → BaseEntity.metadata["brand_names"]
    - Drug.drug_class → BaseEntity.metadata["drug_class"]
    - Drug.mechanism → BaseEntity.metadata["mechanism"]
    """

    def get_entity_type(self) -> str:
        return "drug"


class ProteinEntity(BaseEntity):
    """Represents proteins and their biological functions.

    Uses UniProt as the primary identifier for protein sequences and annotations.

    Mapping from med-lit-schema:
    - Protein.entity_id (UniProt ID) → BaseEntity.entity_id
    - Protein.uniprot_id → BaseEntity.canonical_ids["uniprot"]
    - Protein.gene_id → BaseEntity.metadata["gene_id"]
    - Protein.function → BaseEntity.metadata["function"]
    - Protein.pathways → BaseEntity.metadata["pathways"]
    """

    def get_entity_type(self) -> str:
        return "protein"


class SymptomEntity(BaseEntity):
    """Represents clinical signs and symptoms."""

    def get_entity_type(self) -> str:
        return "symptom"


class ProcedureEntity(BaseEntity):
    """Represents medical tests, diagnostics, treatments."""

    def get_entity_type(self) -> str:
        return "procedure"


class BiomarkerEntity(BaseEntity):
    """Represents measurable indicators."""

    def get_entity_type(self) -> str:
        return "biomarker"


class PathwayEntity(BaseEntity):
    """Represents biological pathways."""

    def get_entity_type(self) -> str:
        return "pathway"


class LocationEntity(BaseEntity):
    """Represents geographic locations relevant to epidemiological analysis.

    Used for tracking disease prevalence by region, endemic diseases, and
    geographic health disparities. Uses provisional IDs initially; canonical
    IDs could come from GeoNames or ISO country codes in the future.
    """

    def get_entity_type(self) -> str:
        return "location"


class EthnicityEntity(BaseEntity):
    """Represents ethnic or population groups for epidemiological analysis.

    Used for tracking genetic predispositions, health disparities, and
    population-specific disease risk factors. Uses provisional IDs initially;
    canonical IDs could come from standardized ethnicity codes in the future.
    """

    def get_entity_type(self) -> str:
        return "ethnicity"

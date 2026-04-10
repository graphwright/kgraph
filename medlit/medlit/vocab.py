"""Vocabulary and validation for medical literature domain.

Defines valid predicates and their constraints (which entity types
can participate in which relationships).
"""

# Valid predicate strings (matching med-lit-schema's PredicateType enum)
predicate_treats = "treats"
predicate_causes = "causes"
predicate_increases_risk = "increases_risk"
predicate_decreases_risk = "decreases_risk"
predicate_associated_with = "associated_with"
predicate_interacts_with = "interacts_with"
predicate_diagnosed_by = "diagnosed_by"
predicate_side_effect = "side_effect"
predicate_encodes = "encodes"
predicate_participates_in = "participates_in"
predicate_contraindicated_for = "contraindicated_for"
predicate_prevents = "prevents"
predicate_manages = "manages"
predicate_binds_to = "binds_to"
predicate_inhibits = "inhibits"
predicate_activates = "activates"
predicate_upregulates = "upregulates"
predicate_downregulates = "downregulates"
predicate_metabolizes = "metabolizes"
predicate_diagnoses = "diagnoses"
predicate_indicates = "indicates"
predicate_precedes = "precedes"
predicate_co_occurs_with = "co_occurs_with"
predicate_located_in = "located_in"
predicate_affects = "affects"
predicate_supports = "supports"
predicate_targets = "targets"
predicate_subtype_of = "subtype_of"

# Research metadata predicates (less common, but included for completeness)
predicate_cites = "cites"
predicate_studied_in = "studied_in"
predicate_authored_by = "authored_by"
predicate_authored = "authored"
predicate_affiliated_with = "affiliated_with"
predicate_described = "described"
predicate_coauthored_with = "coauthored_with"
predicate_is_colleague = "is_colleague"
predicate_part_of = "part_of"
predicate_predicts = "predicts"
predicate_refutes = "refutes"
predicate_tested_by = "tested_by"
predicate_generates = "generates"

# Epidemiological predicates (for location and ethnicity relationships)
predicate_prevalent_in = "prevalent_in"
predicate_endemic_to = "endemic_to"
predicate_originates_from = "originates_from"

# All valid predicates
ALL_PREDICATES = {
    predicate_treats,
    predicate_causes,
    predicate_increases_risk,
    predicate_decreases_risk,
    predicate_associated_with,
    predicate_interacts_with,
    predicate_diagnosed_by,
    predicate_side_effect,
    predicate_encodes,
    predicate_participates_in,
    predicate_contraindicated_for,
    predicate_prevents,
    predicate_manages,
    predicate_binds_to,
    predicate_inhibits,
    predicate_activates,
    predicate_upregulates,
    predicate_downregulates,
    predicate_metabolizes,
    predicate_diagnoses,
    predicate_indicates,
    predicate_precedes,
    predicate_co_occurs_with,
    predicate_located_in,
    predicate_affects,
    predicate_supports,
    predicate_targets,  # Added
    predicate_cites,
    predicate_studied_in,
    predicate_authored_by,
    predicate_authored,
    predicate_affiliated_with,
    predicate_described,
    predicate_coauthored_with,
    predicate_is_colleague,
    predicate_part_of,
    predicate_predicts,
    predicate_refutes,
    predicate_tested_by,
    predicate_generates,
    # Epidemiological predicates
    predicate_prevalent_in,
    predicate_endemic_to,
    predicate_originates_from,
    predicate_subtype_of,
}


def get_valid_predicates(subject_type: str, object_type: str) -> list[str]:
    """Return predicates valid between two entity types.

    This implements domain-specific constraints. For example:
    - Drug → Disease: treats, prevents, contraindicated_for, side_effect
    - Gene → Disease: increases_risk, decreases_risk, associated_with
    - Gene → Protein: encodes
    - Drug → Drug: interacts_with
    - Disease → Symptom: causes
    - Disease → Procedure: diagnosed_by

    Args:
        subject_type: The entity type of the relationship subject.
        object_type: The entity type of the relationship object.

    Returns:
        List of predicate names that are valid for this entity type pair.
    """
    # Drug → Disease relationships
    if subject_type == "drug" and object_type == "disease":
        return [
            predicate_treats,
            predicate_prevents,
            predicate_manages,
            predicate_contraindicated_for,
        ]

    # Procedure → Disease relationships (procedure treats disease)
    if subject_type == "procedure" and object_type == "disease":
        return [predicate_treats, predicate_manages]

    # Biomarker → Disease (marker indicates disease)
    if subject_type == "biomarker" and object_type == "disease":
        return [predicate_indicates]

    # Disease → Symptom relationships
    if subject_type == "disease" and object_type == "symptom":
        return [predicate_causes]

    # Hormone → Symptom relationships (physiological causation, e.g. ACTH causes hyperplasia)
    if subject_type == "hormone" and object_type == "symptom":
        return [predicate_causes]

    # Symptom/Disease → AnatomicalStructure (pathology located in structure, e.g. hyperplasia of adrenal cortex)
    if subject_type in ("symptom", "disease") and object_type == "anatomicalstructure":
        return [predicate_located_in]

    # Drug → Symptom relationships
    if subject_type == "drug" and object_type == "symptom":
        return [predicate_side_effect]

    # Gene → Disease relationships
    if subject_type == "gene" and object_type == "disease":
        return [
            predicate_increases_risk,
            predicate_decreases_risk,
            predicate_associated_with,
        ]

    # Gene → Protein relationships
    if subject_type == "gene" and object_type == "protein":
        return [predicate_encodes]

    # Drug → Drug relationships
    if subject_type == "drug" and object_type == "drug":
        return [predicate_interacts_with]

    # Disease → Procedure/Biomarker relationships
    if subject_type == "disease" and object_type in ("procedure", "biomarker"):
        return [predicate_diagnosed_by]

    # Gene/Protein → Pathway relationships
    if subject_type in ("gene", "protein") and object_type == "pathway":
        return [predicate_participates_in]

    # Disease → Location relationships (epidemiological)
    if subject_type == "disease" and object_type == "location":
        return [
            predicate_prevalent_in,
            predicate_endemic_to,
            predicate_associated_with,
        ]

    # Location → Disease relationships
    if subject_type == "location" and object_type == "disease":
        return [predicate_associated_with]

    # Gene → Ethnicity relationships (genetic predispositions)
    if subject_type == "gene" and object_type == "ethnicity":
        return [
            predicate_prevalent_in,
            predicate_associated_with,
        ]

    # Ethnicity → Disease relationships (health disparities)
    if subject_type == "ethnicity" and object_type == "disease":
        return [
            predicate_increases_risk,
            predicate_decreases_risk,
            predicate_associated_with,
        ]

    # Disease → Ethnicity relationships
    if subject_type == "disease" and object_type == "ethnicity":
        return [
            predicate_prevalent_in,
            predicate_associated_with,
        ]

    # Paper → Paper (citation)
    if subject_type == "paper" and object_type == "paper":
        return [predicate_cites]

    # Disease → Disease
    if subject_type == "disease" and object_type == "disease":
        return [predicate_associated_with, predicate_increases_risk, predicate_subtype_of]

    # Drug/Procedure → Disease
    if subject_type in ("drug", "procedure") and object_type in ("disease"):
        return [predicate_manages]

    # Drug/Procedure → Gene/Protein targets relationships
    if subject_type in ("drug", "procedure") and object_type in ("gene", "protein"):
        return [predicate_targets, predicate_associated_with]

    # General associations (many entity type pairs)
    if subject_type != object_type:  # No self-loops for associated_with
        return [predicate_associated_with]

    # If no specific rules match, return empty list (no predicates valid)
    return []

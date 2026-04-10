"""Per-entity-type similarity thresholds for synonym detection.

The identity server calls POST /synonym-criteria before running cosine similarity
to get the right threshold for each entity type. Tighter thresholds for entity
types where false positives are costly (gene, drug); looser for types where
surface-form variation is high (anatomicalstructure, biologicalprocess).
"""

# Per-entity-type cosine similarity thresholds.
# 0.92+ : very conservative (gene, drug — wrong merge is expensive)
# 0.90  : default
# 0.88  : slightly looser (anatomical structures, pathways have many synonyms)
_THRESHOLDS: dict[str, float] = {
    "gene": 0.95,
    "drug": 0.93,
    "protein": 0.92,
    "disease": 0.90,
    "symptom": 0.90,
    "procedure": 0.90,
    "biomarker": 0.90,
    "hormone": 0.92,
    "enzyme": 0.92,
    "mutation": 0.93,
    "pathway": 0.88,
    "biologicalprocess": 0.88,
    "anatomicalstructure": 0.88,
    "author": 0.95,
    "institution": 0.90,
    "paper": 0.95,
    "hypothesis": 0.90,
    "location": 0.90,
    "ethnicity": 0.90,
}

_DEFAULT_THRESHOLD = 0.90


def get_threshold(entity_type: str) -> float:
    """Return the cosine similarity threshold for synonym detection for this entity type."""
    return _THRESHOLDS.get(entity_type.lower().strip(), _DEFAULT_THRESHOLD)

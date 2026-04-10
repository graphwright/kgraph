"""Medical relationship types for the knowledge graph.

Following Pattern A (simple, scalable): many predicates → one relationship class.
This allows fast implementation without class explosion, while the predicate
still stays in the `predicate` field for clear queries.
"""

from kgschema.relationship import BaseRelationship


class MedicalClaimRelationship(BaseRelationship):
    """Base class for all medical claim relationships.

    This single class handles all medical predicates (treats, causes,
    increases_risk, etc.). The predicate field distinguishes the relationship
    type, and domain-specific metadata can be stored in the metadata dict.

    Mapping from med-lit-schema:
    - AssertedRelationship.subject_id → BaseRelationship.subject_id
    - AssertedRelationship.predicate → BaseRelationship.predicate
    - AssertedRelationship.object_id → BaseRelationship.object_id
    - AssertedRelationship.confidence → BaseRelationship.confidence
    - AssertedRelationship.evidence → BaseRelationship.metadata["evidence"]
    - AssertedRelationship.section → BaseRelationship.metadata["section"]
    - AssertedRelationship.metadata → BaseRelationship.metadata (merged)

    For multi-paper aggregation:
    - source_documents includes all paper IDs that assert this relationship
    - metadata["assertions"][paper_id] = {"evidence": "...", "section": "...", ...}
    """

    def get_edge_type(self) -> str:
        """Return edge type category.

        For Pattern A, we return a generic "medical_claim" since all
        predicates use the same class. If we later split into typed classes,
        each would return its specific type.
        """
        return "medical_claim"

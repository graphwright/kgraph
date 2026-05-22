"""Sherlock Holmes relationship class.

Single relationship class with a `predicate` field, following the medlit pattern.
Sherlock-specific metadata (narrator_trust, narrative_position, story_time, known_by)
is stored in the `metadata` dict.
"""

from kgschema.relationship import BaseRelationship


class SherlockRelationship(BaseRelationship):
    """A typed relationship in the Sherlock Holmes knowledge graph.

    Uses Pattern A (single class, many predicates) for simplicity.
    Sherlock-specific epistemic metadata is stored in metadata dict:
        narrator_trust: One of NarratorTrust enum values
        story_time: One of STORY_TIME_VALUES
        narrative_position: Optional int paragraph index
        known_by: Optional comma-separated character list (who knew this at story time)
    """

    def get_edge_type(self) -> str:
        return "sherlock_claim"

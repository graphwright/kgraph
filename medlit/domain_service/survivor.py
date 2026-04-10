"""Survivor selection logic for the medlit domain service.

Implements the ``preferred_entity`` preference order from ``MedLitDomainSchema``:

1. Canonical status over provisional
2. Presence of any canonical_ids (non-empty ``entity_id`` that isn't a provisional UUID)
3. Higher ``usage_count`` (more evidence)
4. Lower (earlier) creation order — approximated here by entity_id lexical order
   since we don't have ``created_at`` in the HTTP contract.

The identity server sends a flat list of ``CandidateEntity`` dicts; this module
selects and returns the survivor's ``entity_id``.
"""

from .models import CandidateEntity


def _has_authority_id(entity_id: str) -> bool:
    """Return True if entity_id looks like an authoritative ID (not a provisional UUID)."""
    return not entity_id.startswith("prov:")


def select_survivor(candidates: list[CandidateEntity]) -> str:
    """Return the entity_id of the preferred merge survivor.

    Preference order (highest priority first):
    1. Canonical status ('canonical' > 'provisional' > 'merged')
    2. Has an authoritative ID (entity_id does not start with 'prov:')
    3. Higher usage_count
    4. Lexically smallest entity_id (stable tie-breaker)

    Parameters
    ----------
    candidates:
        All entities being considered for merge (must be non-empty).

    Returns
    -------
    str
        The ``entity_id`` of the selected survivor.
    """
    if not candidates:
        raise ValueError("select_survivor requires at least one candidate")

    _STATUS_RANK = {"canonical": 2, "provisional": 1, "merged": 0}

    def sort_key(c: CandidateEntity) -> tuple:
        # All terms ascending; larger tuple = preferred survivor.
        # entity_id: we want the lexically *smallest*, so negate by wrapping in a
        # comparable that sorts reversed — use a tuple with a flag instead.
        return (
            _STATUS_RANK.get(c.status, 0),
            int(_has_authority_id(c.entity_id)),
            c.usage_count,
        )

    # Primary sort: highest rank last (we take [-1]).
    # Secondary stable sort on entity_id ascending first, so that among ties the
    # lexically smallest entity_id ends up last after the primary sort preserves order.
    by_id = sorted(candidates, key=lambda c: c.entity_id, reverse=True)
    ranked = sorted(by_id, key=sort_key)
    return ranked[-1].entity_id

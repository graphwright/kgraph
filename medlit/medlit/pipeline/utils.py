"""Shared utilities for medlit pipeline."""


def canonicalize_symmetric(subject_id: str, object_id: str) -> tuple[str, str]:
    """Return (min, max) of subject and object for deterministic symmetric edge storage.

    Used by dedup so symmetric predicates (e.g. ASSOCIATED_WITH) produce
    identical (subject, object_id) regardless of order.
    """
    return (min(subject_id, object_id), max(subject_id, object_id))

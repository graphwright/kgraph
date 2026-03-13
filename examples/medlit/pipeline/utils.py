"""Shared utilities for medlit pipeline."""


def canonicalize_symmetric(subject_id: str, object_id: str) -> tuple[str, str]:
    """Return (min, max) of subject and object for deterministic symmetric edge storage.

    Used by provenance_expansion and dedup so COAUTHORED_WITH(A,B) and
    COAUTHORED_WITH(B,A) produce identical (subject, object_id).
    """
    return (min(subject_id, object_id), max(subject_id, object_id))

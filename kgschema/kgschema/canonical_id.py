"""Canonical ID model for knowledge graph entities.

This module provides the CanonicalId model representing stable identifiers
from authoritative sources (UMLS, MeSH, HGNC, etc.).
"""

from typing import Optional

from pydantic import BaseModel, Field


class CanonicalId(BaseModel):
    """Represents a canonical identifier from an authoritative source.

    A canonical ID uniquely identifies an entity in an authoritative ontology
    (e.g., UMLS, MeSH, HGNC, RxNorm, UniProt, Wikidata). This model stores
    the ID, its URL (if available), and synonyms that map to this ID.

    Attributes:
        id: The canonical ID string (e.g., "UMLS:C12345", "MeSH:D000570", "HGNC:1100")
        url: Optional URL to the authoritative source page for this ID
        synonyms: List of alternative names/terms that map to this canonical ID
    """

    model_config = {"frozen": True}

    id: str = Field(description="Canonical ID string from authoritative source (e.g., 'UMLS:C12345', 'MeSH:D000570')")
    url: Optional[str] = Field(
        default=None,
        description="URL to the authoritative source page for this ID, if available",
    )
    synonyms: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Alternative names/terms that map to this canonical ID",
    )

    def __str__(self) -> str:
        """String representation of the canonical ID."""
        return self.id

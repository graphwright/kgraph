"""Journal article document representation for medical literature domain."""

from pydantic import Field

from kgschema.document import BaseDocument


class JournalArticle(BaseDocument):
    """A journal article (research paper) as a source document for extraction.

    Maps from med-lit-schema's Paper model to kgraph's BaseDocument.
    Papers are NOT the same as doc_assets.jsonl (which is for documentation assets).
    Papers are the source of information for building the knowledge graph, taken
    from sources like PubMed, PLOS ONE, or medical journals if available.

    Key mappings:
    - Paper.paper_id → BaseDocument.document_id (prefer doi:, else pmid:, else stable hash)
    - Paper.title → BaseDocument.title
    - Paper.abstract + (optional full text) → BaseDocument.content
    - PaperMetadata → BaseDocument.metadata (study type, sample size, journal, etc.)
    - Paper.extraction_provenance → BaseDocument.metadata["extraction"]
    """

    # Bibliographic fields (frequently queried, so top-level)
    authors: tuple[str, ...] = Field(default=(), description="List of author names in citation order")
    abstract: str = Field(description="Complete abstract text")
    publication_date: str | None = Field(default=None, description="Publication date in ISO format (YYYY-MM-DD)")
    journal: str | None = Field(default=None, description="Journal name")
    doi: str | None = Field(default=None, description="Digital Object Identifier")
    pmid: str | None = Field(default=None, description="PubMed ID")

    # Study metadata (in metadata dict for structured access)
    # These will be stored in metadata["study_type"], metadata["sample_size"], etc.

    def get_document_type(self) -> str:
        """Return domain-specific document type."""
        return "journal_article"

    def get_sections(self) -> list[tuple[str, str]]:
        """Return document sections as (section_name, content) tuples.

        For journal articles, we typically have:
        - title: The paper title
        - abstract: The abstract text
        - body: The full text content (if available)
        """
        sections: list[tuple[str, str]] = []

        if self.title:
            sections.append(("title", self.title))

        if self.abstract:
            sections.append(("abstract", self.abstract))

        # Full text content (may include abstract again, but that's okay for extraction)
        if self.content:
            sections.append(("body", self.content))

        return sections

    @property
    def study_type(self) -> str | None:
        """Convenience property for accessing study_type from metadata."""
        return self.metadata.get("study_type")

    @property
    def sample_size(self) -> int | None:
        """Convenience property for accessing sample_size from metadata."""
        return self.metadata.get("sample_size")

    @property
    def mesh_terms(self) -> list[str]:
        """Convenience property for accessing mesh_terms from metadata."""
        return self.metadata.get("mesh_terms", [])

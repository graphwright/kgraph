"""Sherlock Holmes story document representation."""

from kgschema.document import BaseDocument
from pydantic import Field


class SherlockStory(BaseDocument):
    """A Sherlock Holmes short story or novel as a source document for extraction.

    The story is split into paragraphs by the parser; each paragraph becomes
    an evidence entity with a stable index.

    Fields:
        collection: The collection title (e.g. 'Adventures of Sherlock Holmes').
        story_slug: Short identifier used in evidence IDs (e.g. 'scandal_in_bohemia').
        author: Typically 'Arthur Conan Doyle'.
        year: Publication year.
    """

    collection: str | None = Field(default=None, description="Collection/anthology title")
    story_slug: str = Field(description="Short stable identifier for evidence IDs")
    author: str = Field(default="Arthur Conan Doyle")
    year: int | None = Field(default=None)

    def get_document_type(self) -> str:
        return "sherlock_story"

    def get_sections(self) -> list[tuple[str, str]]:
        """Return story as a single 'body' section."""
        sections: list[tuple[str, str]] = []
        if self.title:
            sections.append(("title", self.title))
        if self.content:
            sections.append(("body", self.content))
        return sections

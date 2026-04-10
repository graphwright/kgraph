"""Medlit document definitions."""

from kgschema.document import BaseDocument


class PaperDocument(BaseDocument):
    def get_document_type(self) -> str:
        return "paper_document"

    def get_sections(self) -> list[tuple[str, str]]:
        return [("body", self.content)]

"""Document parser for journal articles.

Converts raw paper input (PMC XML, JSON, etc.) into JournalArticle documents.
"""

from datetime import datetime, timezone
from typing import Any

from kgraph.pipeline.interfaces import DocumentParserInterface

from ..documents import JournalArticle


class JournalArticleParser(DocumentParserInterface):
    """Parse raw journal article content into JournalArticle documents.

    This parser handles various input formats (PMC XML, JSON from med-lit-schema,
    etc.) and converts them to kgraph's JournalArticle format.

    For now, this is a minimal implementation. A full implementation would:
    1. Parse PMC XML (using existing med-lit-schema parser logic)
    2. Parse JSON from med-lit-schema's Paper format
    3. Extract metadata and map to JournalArticle fields
    """

    async def parse(
        self,
        raw_content: bytes,
        content_type: str,
        source_uri: str | None = None,
    ) -> JournalArticle:
        """Parses raw document content into a structured `JournalArticle`.

        This method acts as a dispatcher, routing the raw content to the
        appropriate parsing logic based on its `content_type`. It supports
        JSON (conforming to `med-lit-schema`) and PMC XML formats.

        Args:
            raw_content: The raw byte content of the document.
            content_type: The MIME type of the document, used to select the
                          correct parser (e.g., "application/json", "application/xml").
            source_uri: An optional URI for the document's origin, which can be
                        used to infer a document ID.

        Returns:
            A `JournalArticle` instance populated with the parsed data.

        Raises:
            ValueError: If the `content_type` is not supported or if the
                        content is malformed and cannot be parsed.
        """
        if content_type == "application/json":
            # Parse JSON (e.g., from med-lit-schema's Paper format)
            import json

            data = json.loads(raw_content.decode("utf-8"))
            return self._parse_from_dict(data, source_uri)

        elif content_type in {"application/xml", "text/xml"}:
            # Parse PMC XML
            import xml.etree.ElementTree as ET
            import io

            try:
                tree = ET.parse(io.BytesIO(raw_content))
                root = tree.getroot()
                data = self._parse_xml_to_dict(root, source_uri)
                return self._parse_from_dict(data, source_uri)
            except ET.ParseError as e:
                raise ValueError(f"Failed to parse XML: {e}") from e

        else:
            raise ValueError(f"Unsupported content_type: {content_type}")

    def _parse_xml_to_dict(self, root: Any, source_uri: str | None) -> dict[str, Any]:
        """Converts a PMC XML structure into a dictionary.

        This method traverses the XML element tree of a PubMed Central article
        and extracts key information, mapping it to a dictionary that loosely
        conforms to the `med-lit-schema` Paper format. This intermediate
        dictionary is then passed to `_parse_from_dict`.

        Args:
            root: The root element of the parsed XML tree.
            source_uri: An optional source URI, used as a fallback to derive
                        the paper's ID from its filename.

        Returns:
            A dictionary containing the extracted title, abstract, authors,
            and other metadata.
        """
        # Extract basic metadata
        article_meta = root.find(".//article-meta")

        # Determine paper_id from source_uri or XML
        paper_id = ""
        if source_uri:
            # Try to extract from filename (e.g., "PMC12757604.xml")
            from pathlib import Path

            paper_id = Path(source_uri).stem
        else:
            # Try to extract from XML
            article_id = article_meta.find(".//article-id[@pub-id-type='pmc']") if article_meta else None
            if article_id is not None and article_id.text:
                paper_id = article_id.text

        # Title
        title = ""
        title_elem = article_meta.find(".//article-title") if article_meta else None
        if title_elem is not None:
            title = "".join(title_elem.itertext()).strip()

        # Abstract - convert to object with "text" key
        abstract_text = ""
        abstract_elem = root.find(".//abstract")
        if abstract_elem is not None:
            abstract_text = "".join(abstract_elem.itertext()).strip()
        abstract = {"text": abstract_text} if abstract_text else {"text": ""}

        # Body text - use as "full_text"
        full_text = ""
        body_elem = root.find(".//body")
        if body_elem is not None:
            full_text = "".join(body_elem.itertext()).strip()

        # Affiliations: aff id -> text
        aff_id_to_text: dict[str, str] = {}
        for aff in root.findall(".//aff"):
            aff_id = aff.get("id", "")
            inst_elem = aff.find("institution[@content-type='orgname']") or aff.find("institution")
            if inst_elem is not None and inst_elem.text:
                text = inst_elem.text.strip()
            else:
                text = "".join(aff.itertext()).strip()
            if aff_id:
                aff_id_to_text[aff_id] = text
                aff_id_to_text[aff_id.lstrip("#")] = text

        # Authors with affiliations
        authors: list[str] = []
        author_details: list[dict[str, Any]] = []
        for contrib in root.findall('.//contrib[@contrib-type="author"]'):
            name_elem = contrib.find(".//name")
            if name_elem is not None:
                surname = name_elem.find("surname")
                given = name_elem.find("given-names")
                if surname is not None:
                    author = surname.text or ""
                    if given is not None and given.text:
                        author = f"{given.text} {author}"
                    authors.append(author)
                    # Affiliations for this author
                    affs: list[str] = []
                    for xref in contrib.findall("xref[@ref-type='aff']"):
                        rid = (xref.get("rid") or "").lstrip("#")
                        aff_text = aff_id_to_text.get(rid) or aff_id_to_text.get(xref.get("rid", ""))
                        if aff_text:
                            affs.append(aff_text)
                    author_details.append({"name": author, "affiliations": affs})

        # Keywords
        keywords: list[str] = []
        for kwd in root.findall(".//kwd"):
            if kwd.text:
                keywords.append(kwd.text.strip())

        # Build Paper schema structure
        paper: dict[str, Any] = {
            "paper_id": paper_id,
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "author_details": author_details,
        }

        # Add full_text if it exists
        if full_text:
            paper["full_text"] = full_text

        # Add metadata if keywords exist
        if keywords:
            paper["metadata"] = {"keywords": keywords}

        return paper

    def _parse_from_dict(self, data: dict[str, Any], source_uri: str | None) -> JournalArticle:
        """Constructs a `JournalArticle` from a dictionary.

        This method takes a dictionary (conforming to `med-lit-schema`'s Paper
        format or the output of `_parse_xml_to_dict`) and maps its fields to
        the `JournalArticle` document model.

        Key mapping logic:
        -   `document_id` is chosen in order of preference: DOI, then PMID,
            then the original `paper_id`.
        -   `content` is created by combining the abstract and full text.
        -   Pre-existing `entities` and `relationships` from the input data
            are moved into the `metadata` dictionary, so that downstream
            extractors in the kgraph pipeline can find them.
        -   Other fields like authors, publication date, and journal are
            mapped directly.

        Args:
            data: A dictionary containing the paper's data.
            source_uri: The original source URI of the document.

        Returns:
            A fully populated `JournalArticle` object.

        Raises:
            ValueError: If no valid identifier (paper_id, doi, or pmid)
                        can be found in the input data.
        """
        # Determine document_id (prefer DOI, else PMID, else paper_id)
        paper_id = data.get("paper_id", "")
        doi = data.get("doi")
        pmid = data.get("pmid")

        if doi:
            document_id = f"doi:{doi}"
        elif pmid:
            document_id = f"pmid:{pmid}"
        elif paper_id:
            document_id = paper_id
        else:
            raise ValueError("No valid identifier found (paper_id, doi, or pmid required)")

        ## Extract content (abstract + optional full text)
        # abstract = data.get("abstract", "")
        # full_text = data.get("full_text", "")  # May not be present
        # content = abstract
        # if full_text:
        #    content = f"{abstract}\n\n{full_text}" if abstract else full_text

        # NEW CODE (fixed):
        # Extract content (abstract + optional full text)
        abstract_obj = data.get("abstract", "")
        # Handle both dict {"text": "..."} and plain string formats
        if isinstance(abstract_obj, dict):
            abstract = abstract_obj.get("text", "")
        else:
            abstract = str(abstract_obj) if abstract_obj else ""
        full_text = data.get("full_text", "")
        content = abstract
        if full_text:
            content = f"{abstract}\n\n{full_text}" if abstract else full_text

        # Extract metadata
        metadata: dict[str, Any] = {}
        metadata["author_details"] = data.get("author_details", [])

        # Map PaperMetadata fields
        paper_metadata = data.get("metadata", {})
        if isinstance(paper_metadata, dict):
            metadata.update(paper_metadata)
        else:
            # If metadata is a PaperMetadata object (already parsed), extract its fields
            if hasattr(paper_metadata, "study_type"):
                metadata["study_type"] = paper_metadata.study_type
            if hasattr(paper_metadata, "sample_size"):
                metadata["sample_size"] = paper_metadata.sample_size
            if hasattr(paper_metadata, "mesh_terms"):
                metadata["mesh_terms"] = paper_metadata.mesh_terms

        # Store extraction provenance if present
        extraction_provenance = data.get("extraction_provenance")
        if extraction_provenance:
            metadata["extraction"] = extraction_provenance

        # Store entities and relationships in metadata so extractors can find them
        # (they're at top level in Paper JSON, but we put them in metadata for extractors)
        if "entities" in data:
            metadata["entities"] = data["entities"]
        if "relationships" in data:
            metadata["relationships"] = data["relationships"]

        # Extract authors (handle both list and string formats)
        authors = data.get("authors", [])
        if isinstance(authors, str):
            authors = [authors]
        elif not isinstance(authors, list):
            authors = []

        return JournalArticle(
            document_id=document_id,
            title=data.get("title", ""),
            content=content,
            content_type="text/plain",  # Processed text
            source_uri=source_uri,
            created_at=datetime.now(timezone.utc),
            authors=tuple(authors),
            abstract=abstract,
            publication_date=data.get("publication_date"),
            journal=data.get("journal"),
            doi=doi,
            pmid=pmid,
            metadata=metadata,
        )

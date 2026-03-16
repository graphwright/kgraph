"""Utility functions for constructing canonical URLs from entity canonical IDs."""

from typing import Optional


def build_canonical_url(canonical_id: str, entity_type: Optional[str] = None) -> Optional[str]:
    """Build a canonical URL for an entity based on its canonical ID.

    Supports:
    - DBPedia: https://dbpedia.org/page/{entity_name}
    - MeSH: https://meshb.nlm.nih.gov/record/ui?ui={ID}
    - UniProt: https://www.uniprot.org/uniprotkb/{ID}
    - HGNC: https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/{ID}
    - UMLS: https://uts.nlm.nih.gov/uts/umls/concept/{ID}
    - RxNorm: https://www.nlm.nih.gov/research/umls/rxnorm/overview.html (no direct link, returns None)

    Args:
        canonical_id: The canonical ID (e.g., "MeSH:D000570", "UniProt:P38398", "HGNC:1100")
        entity_type: Optional entity type hint (e.g., "disease", "gene", "protein")

    Returns:
        URL string if a link can be constructed, None otherwise.
    """
    if not canonical_id:
        return None

    # Handle DBPedia IDs (format: "DBPedia:Entity_Name" or "DBPedia:Entity_Name_with_underscores")
    if canonical_id.startswith("DBPedia:"):
        entity_name = canonical_id.replace("DBPedia:", "")
        # DBPedia uses underscores in URLs - ensure spaces are converted
        url_entity_name = entity_name.replace(" ", "_")
        return f"https://dbpedia.org/page/{url_entity_name}"

    # Handle MeSH IDs (format: "MeSH:D000570" or "D000570")
    if canonical_id.startswith("MeSH:"):
        mesh_id = canonical_id.replace("MeSH:", "")
        return f"https://meshb.nlm.nih.gov/record/ui?ui={mesh_id}"
    elif canonical_id.startswith("D") and len(canonical_id) > 1 and canonical_id[1:].isdigit():
        # MeSH format without prefix (D followed by digits)
        if entity_type == "disease" or entity_type is None:
            return f"https://meshb.nlm.nih.gov/record/ui?ui={canonical_id}"

    # Handle UniProt IDs (format: "UniProt:P38398" or "P38398")
    if canonical_id.startswith("UniProt:"):
        uniprot_id = canonical_id.replace("UniProt:", "")
        return f"https://www.uniprot.org/uniprotkb/{uniprot_id}"
    elif canonical_id.startswith("P") or canonical_id.startswith("Q"):
        # UniProt format without prefix (P/Q followed by alphanumeric)
        if entity_type == "protein" or entity_type is None:
            # Check if it looks like a UniProt ID (P/Q + 5-6 alphanumeric chars)
            if len(canonical_id) >= 6 and canonical_id[1:].isalnum():
                return f"https://www.uniprot.org/uniprotkb/{canonical_id}"

    # Handle HGNC IDs (format: "HGNC:1100" or just "1100")
    if canonical_id.startswith("HGNC:"):
        hgnc_id = canonical_id.replace("HGNC:", "")
        return f"https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/{hgnc_id}"
    elif canonical_id.isdigit():
        # Just a number - could be HGNC if entity type is gene
        if entity_type == "gene":
            return f"https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/{canonical_id}"

    # Handle UMLS IDs (format: "C0006142" - C followed by digits)
    if canonical_id.startswith("C") and len(canonical_id) > 1 and canonical_id[1:].isdigit():
        return f"https://uts.nlm.nih.gov/uts/umls/concept/{canonical_id}"

    # Handle RxNorm IDs (format: "RxNorm:1187832")
    # Note: RxNorm doesn't have direct entity URLs, so we return None
    if canonical_id.startswith("RxNorm:"):
        # RxNorm doesn't provide direct entity links
        return None

    # Handle ROR IDs (format: "ROR:04aj4c181" or full URL "https://ror.org/04aj4c181")
    if canonical_id.startswith("ROR:"):
        ror_id = canonical_id.replace("ROR:", "")
        return f"https://ror.org/{ror_id}"
    if canonical_id.startswith("https://ror.org/"):
        return canonical_id

    # Handle ORCID iDs (format: "ORCID:0000-0001-2345-6789")
    if canonical_id.startswith("ORCID:"):
        orcid_id = canonical_id.replace("ORCID:", "")
        return f"https://orcid.org/{orcid_id}"

    return None


def build_canonical_urls_from_dict(canonical_ids: dict[str, str], entity_type: Optional[str] = None) -> dict[str, str]:
    """Build canonical URLs for all canonical IDs in a dictionary.

    Args:
        canonical_ids: Dictionary mapping source names to canonical IDs
            (e.g., {"umls": "C0006142", "mesh": "MeSH:D000570"})
        entity_type: Optional entity type hint

    Returns:
        Dictionary mapping source names to URLs (e.g., {"umls": "https://...", "mesh": "https://..."})
    """
    urls: dict[str, str] = {}

    for source, canonical_id in canonical_ids.items():
        url = build_canonical_url(canonical_id, entity_type=entity_type)
        if url:
            urls[source] = url

    return urls

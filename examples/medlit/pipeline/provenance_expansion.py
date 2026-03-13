"""Provenance expansion: derive Author, Institution, Paper entities and relationships from metadata."""

import re

from examples.medlit.bundle_models import AuthorInfo, ExtractedEntityRow, PerPaperBundle, RelationshipRow


def normalize_author_id(name: str, paper_id: str) -> str:
    """Return Author:{normalized} where normalized = last word + first initial, lowercased, alphanumeric only."""
    parts = name.strip().split()
    if not parts:
        return f"Author:unknown_{paper_id[:8]}"
    last = parts[-1].lower()
    first = parts[0][0].lower() if parts[0] else ""
    normalized = re.sub(r"[^a-z0-9]", "", f"{last}_{first}")
    if not normalized:
        normalized = "unknown"
    return f"Author:{normalized}"


def normalize_institution_id(affiliation: str) -> str:
    """Return Institution:{normalized} where normalized = first 50 chars, lowercased, non-alphanumeric -> underscore."""
    text = affiliation.strip()[:50].lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    if not normalized:
        normalized = "unknown"
    return f"Institution:{normalized}"


def expand_provenance(bundle: PerPaperBundle) -> tuple[list[ExtractedEntityRow], list[RelationshipRow]]:
    """Derive Author, Institution, Paper entities and AUTHORED, AFFILIATED_WITH, DESCRIBED from metadata.

    DESCRIBED is limited to the top 2 domain entities by relationship count (central to the paper).
    COAUTHORED_WITH is omitted; derive via AUTHORED hops (Author -> Paper <- Author).
    """
    new_entities: list[ExtractedEntityRow] = []
    new_relationships: list[RelationshipRow] = []
    seen_entity_ids: set[str] = set()

    # Resolve author list
    if bundle.paper.author_details:
        authors = [a if isinstance(a, AuthorInfo) else AuthorInfo(**a) for a in bundle.paper.author_details]
    else:
        authors = [AuthorInfo(name=a, affiliations=[]) for a in (bundle.paper.authors or [])]

    document_id = bundle.paper.document_id or bundle.paper.pmcid or "unknown"
    paper_entity_id = f"Paper:{document_id}"

    # Authors and institutions
    author_ids: list[str] = []
    for author in authors:
        aid = normalize_author_id(author.name, document_id)
        if aid not in seen_entity_ids:
            new_entities.append(ExtractedEntityRow(id=aid, entity_class="Author", name=author.name))
            seen_entity_ids.add(aid)
        author_ids.append(aid)

        for aff in author.affiliations:
            iid = normalize_institution_id(aff)
            if iid not in seen_entity_ids:
                new_entities.append(ExtractedEntityRow(id=iid, entity_class="Institution", name=aff))
                seen_entity_ids.add(iid)
            new_relationships.append(
                RelationshipRow(
                    subject=aid,
                    predicate="AFFILIATED_WITH",
                    object_id=iid,
                    source_papers=[document_id],
                    confidence=0.9,
                    asserted_by="derived",
                )
            )

    # Paper entity (set canonical_id when document_id is a PMC ID so dedup uses it)
    if paper_entity_id not in seen_entity_ids:
        canonical = document_id if document_id.startswith("PMC") and document_id[3:].isdigit() else None
        new_entities.append(
            ExtractedEntityRow(
                id=paper_entity_id,
                entity_class="Paper",
                name=bundle.paper.title,
                canonical_id=canonical,
            )
        )
        seen_entity_ids.add(paper_entity_id)

    # AUTHORED(Author, Paper)
    for aid in author_ids:
        new_relationships.append(
            RelationshipRow(
                subject=aid,
                predicate="AUTHORED",
                object_id=paper_entity_id,
                source_papers=[document_id],
                confidence=0.9,
                asserted_by="derived",
            )
        )

    # DESCRIBED(Paper, entity) for top 2 domain entities by relationship count (Option A)
    entity_rel_count: dict[str, int] = {}
    for rel in bundle.relationships:
        for eid in (rel.subject, rel.object_id):
            entity_rel_count[eid] = entity_rel_count.get(eid, 0) + 1
    domain_entity_ids = [e.id for e in bundle.entities if e.entity_class not in ("Author", "Institution", "Evidence")]
    top_entities = sorted(
        domain_entity_ids,
        key=lambda x: entity_rel_count.get(x, 0),
        reverse=True,
    )[:2]
    for entity_id in top_entities:
        new_relationships.append(
            RelationshipRow(
                subject=paper_entity_id,
                predicate="DESCRIBED",
                object_id=entity_id,
                source_papers=[document_id],
                confidence=0.9,
                asserted_by="derived",
            )
        )

    return new_entities, new_relationships

"""Provenance expansion: derive Author, Institution, Paper entities and relationships from metadata."""

import re

from examples.medlit.bundle_models import AuthorInfo, ExtractedEntityRow, PerPaperBundle, RelationshipRow
from examples.medlit.pipeline.utils import canonicalize_symmetric


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
    """Derive Author, Institution, Paper entities and AUTHORED, AFFILIATED_WITH, DESCRIBED, COAUTHORED_WITH from metadata."""
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

    # Paper entity
    if paper_entity_id not in seen_entity_ids:
        new_entities.append(ExtractedEntityRow(id=paper_entity_id, entity_class="Paper", name=bundle.paper.title))
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

    # DESCRIBED(Paper, entity) for domain entities only
    for entity in bundle.entities:
        if entity.entity_class in ("Author", "Institution", "Evidence"):
            continue
        new_relationships.append(
            RelationshipRow(
                subject=paper_entity_id,
                predicate="DESCRIBED",
                object_id=entity.id,
                source_papers=[document_id],
                confidence=0.9,
                asserted_by="derived",
            )
        )

    # COAUTHORED_WITH with canonical ordering
    seen_pairs: set[tuple[str, str]] = set()
    for i, a1 in enumerate(author_ids):
        for a2 in author_ids[i + 1 :]:
            sub, obj = canonicalize_symmetric(a1, a2)
            if (sub, obj) not in seen_pairs:
                seen_pairs.add((sub, obj))
                new_relationships.append(
                    RelationshipRow(
                        subject=sub,
                        predicate="COAUTHORED_WITH",
                        object_id=obj,
                        source_papers=[document_id],
                        confidence=0.9,
                        asserted_by="derived",
                    )
                )

    return new_entities, new_relationships

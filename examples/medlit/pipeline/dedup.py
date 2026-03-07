"""Pass 2: Deduplication and promotion over per-paper bundles.

Reads all PerPaperBundle JSONs from a directory, builds name/type index (with
synonym cache), resolves high-confidence SAME_AS, assigns canonical IDs,
updates relationship refs, accumulates triples, and saves the synonym cache.
Original bundle files are never modified; output is written to a separate
directory (overlay or merged graph).
"""

import asyncio
import json
import uuid
from pathlib import Path
from typing import Any, Optional

from examples.medlit.bundle_models import ExtractedEntityRow, PerPaperBundle, ProvenanceEntry
from examples.medlit.pipeline.config_loader import load_entity_types
from examples.medlit.pipeline.synonym_cache import (
    add_same_as_to_cache,
    load_synonym_cache,
    lookup_entity,
    save_synonym_cache,
)

# British → American spelling for dedup (hyperglycaemia/hyperglycemia, etc.)
SPELLING_NORMALIZATIONS: dict[str, str] = {
    "hyperglycaemia": "hyperglycemia",
    "haemoglobin": "hemoglobin",
    "tumour": "tumor",
    "oesophagus": "esophagus",
    "leukaemia": "leukemia",
}


def _normalize_for_dedup(name: str) -> str:
    """Lowercase, strip, and apply British→American spelling map for dedup lookups."""
    n = name.lower().strip()
    return SPELLING_NORMALIZATIONS.get(n, n)


def _is_authoritative_id(s: str) -> bool:
    """Return True if s looks like an authoritative ontology ID, not a synthetic slug."""
    if not s or not s.strip():
        return False
    if s.startswith("prov-"):
        return False
    # MeSH (D + digits or MeSH:...)
    if s.startswith("MeSH:"):
        return True
    if len(s) > 1 and s[0] == "D" and s[1:].isdigit():
        return True
    # UMLS (C + digits)
    if s.startswith("C") and len(s) > 1 and s[1:].isdigit():
        return True
    # HGNC
    if s.startswith("HGNC:"):
        return True
    if s.isdigit():
        return True  # numeric HGNC
    # RxNorm
    if s.startswith("RxNorm:"):
        return True
    # UniProt (P/Q + alphanumeric)
    if (s.startswith("P") or s.startswith("Q")) and len(s) >= 6 and s[1:].isalnum():
        return True
    if s.startswith("UniProt:"):
        return True
    # DBPedia
    if s.startswith("DBPedia:"):
        return True
    return False


def _format_hgnc_id(val: str) -> str:
    """Ensure HGNC ID has HGNC: prefix if numeric."""
    v = val.strip()
    if v.isdigit():
        return f"HGNC:{v}"
    return v


def _preferred_authoritative_id(
    e: ExtractedEntityRow,
    lookup: Any,
) -> Optional[str]:
    """Return the best authoritative ID for merge key, preferring HGNC for genes.

    For Gene: if both umls_id and hgnc_id present, prefer hgnc_id. If only umls_id,
    resolve via UMLS→HGNC cross-lookup when lookup is available.
    For other classes: first match in canonical_id, umls_id, hgnc_id, rxnorm_id, uniprot_id.
    """
    if e.entity_class == "Gene":
        if e.hgnc_id and e.hgnc_id.strip() and _is_authoritative_id(e.hgnc_id.strip()):
            return _format_hgnc_id(e.hgnc_id)
        if e.umls_id and e.umls_id.strip() and _is_authoritative_id(e.umls_id.strip()):
            if lookup is not None and hasattr(lookup, "lookup_hgnc_by_cui_sync"):
                resolved = lookup.lookup_hgnc_by_cui_sync(e.umls_id.strip())
                if resolved:
                    return resolved
            return e.umls_id.strip()
        if e.canonical_id and e.canonical_id.strip() and _is_authoritative_id(e.canonical_id.strip()):
            return e.canonical_id.strip()
        return None
    for val in (e.canonical_id, e.umls_id, e.hgnc_id, e.rxnorm_id, e.uniprot_id):
        if val and val.strip() and _is_authoritative_id(val):
            return val.strip()
    return None


# Authority lookup type overrides: bundle_class -> lookup_type when authority APIs
# use a different type (e.g. Hormone->drug, Enzyme->protein). Base mapping from config.
_AUTHORITY_LOOKUP_OVERRIDES: dict[str, str] = {
    "Hormone": "drug",
    "Enzyme": "protein",
    "Biomarker": "disease",
}

# Fallback when config is missing. Must match entity_types.yaml bundle_class -> lookup.
_FALLBACK_ENTITY_CLASS_TO_LOOKUP: dict[str, str] = {
    "Disease": "disease",
    "Gene": "gene",
    "Drug": "drug",
    "Protein": "protein",
    "Hormone": "drug",
    "Enzyme": "protein",
    "Biomarker": "disease",
}


def _entity_class_to_lookup_type(entity_class: str, entity_class_to_lookup: dict[str, str]) -> Optional[str]:
    """Map bundle entity_class to CanonicalIdLookup entity_type (lowercase)."""
    m = entity_class_to_lookup if entity_class_to_lookup else _FALLBACK_ENTITY_CLASS_TO_LOOKUP
    if entity_class in _AUTHORITY_LOOKUP_OVERRIDES:
        return _AUTHORITY_LOOKUP_OVERRIDES[entity_class]
    return m.get(entity_class)


def _build_entity_class_to_lookup_type(config_dir: Path) -> dict[str, str]:
    """Derive bundle_class -> lookup_type from entity_types.yaml."""
    entity_types = load_entity_types(config_dir)
    out: dict[str, str] = {}
    for config_key, val in entity_types.items():
        if isinstance(val, dict) and "bundle_class" in val:
            bc = val["bundle_class"]
            out[bc] = str(config_key).lower()
    out.update(_AUTHORITY_LOOKUP_OVERRIDES)
    return out


# SAME_AS predicate; defined in predicates.yaml. Used for merge resolution.
SAME_AS_PREDICATE = "SAME_AS"


def _canonical_id_slug() -> str:
    """Generate a short synthetic merge key for entities without authoritative ID."""
    return "prov-" + uuid.uuid4().hex[:12]


def run_pass2(  # pylint: disable=too-many-statements
    bundle_dir: Path,
    output_dir: Path,
    synonym_cache_path: Optional[Path] = None,
    canonical_id_cache_path: Optional[Path] = None,
    embedding_generator: Any = None,
    similarity_threshold: float = 0.88,
    cross_type_threshold: float = 0.90,
    config_dir: Optional[Path] = None,
) -> dict[str, Any]:
    """Run Pass 2: dedup and promotion. Reads bundles from bundle_dir, writes to output_dir.

    Original bundle files in bundle_dir are never modified.
    Returns summary dict (entities_count, relationships_count, etc.).

    Args:
        embedding_generator: Optional; if set, used for embedding-based dedup of provisional
            entities and cross-type candidate detection. Must have generate(text) -> vector.
        similarity_threshold: Min cosine similarity for same-class provisional merge (default 0.88).
        cross_type_threshold: Min similarity for cross-type candidate flagging (default 0.90).
    """
    synonym_cache_path = synonym_cache_path or output_dir / "synonym_cache.json"
    cache = load_synonym_cache(synonym_cache_path)

    # Optional authority lookup for resolving canonical IDs (save cache at end)
    lookup = None
    if canonical_id_cache_path is not None:
        from examples.medlit.pipeline.authority_lookup import CanonicalIdLookup

        lookup = CanonicalIdLookup(cache_file=canonical_id_cache_path)

    if config_dir is None:
        config_dir = Path(__file__).resolve().parents[2] / "config"
    entity_class_to_lookup = _build_entity_class_to_lookup_type(config_dir) if config_dir.exists() else {}

    try:
        return _run_pass2_impl(
            bundle_dir=bundle_dir,
            output_dir=output_dir,
            synonym_cache_path=synonym_cache_path,
            cache=cache,
            lookup=lookup,
            embedding_generator=embedding_generator,
            similarity_threshold=similarity_threshold,
            cross_type_threshold=cross_type_threshold,
            entity_class_to_lookup=entity_class_to_lookup,
        )
    finally:
        if lookup is not None:
            lookup._save_cache(force=True)  # Save lookup cache so results persist across runs.  # pylint: disable=protected-access


def _run_pass2_impl(  # pylint: disable=too-many-statements
    bundle_dir: Path,
    output_dir: Path,
    synonym_cache_path: Path,
    cache: dict,
    lookup: Any,
    embedding_generator: Any = None,
    similarity_threshold: float = 0.88,
    cross_type_threshold: float = 0.90,
    entity_class_to_lookup: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    """Inner Pass 2 implementation (lookup created and saved by caller)."""
    if entity_class_to_lookup is None:
        entity_class_to_lookup = {}
    # Load all bundles
    bundle_files = sorted(bundle_dir.glob("paper_*.json"))
    if not bundle_files:
        return {"error": "no bundle files", "entities_count": 0, "relationships_count": 0}

    # Use filename as ground truth for paper_id. Never trust bundle.paper.pmcid — the LLM
    # can hallucinate wrong IDs (e.g. from citations), causing document_id mix-ups.
    bundles: list[tuple[str, PerPaperBundle]] = []
    for path in bundle_files:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        bundle = PerPaperBundle.from_bundle_dict(data)
        paper_id = path.stem.replace("paper_", "")
        bundles.append((paper_id, bundle))

    # (name_lower, entity_class) -> merge key (authoritative or synthetic)
    name_type_to_canonical: dict[tuple[str, str], str] = {}
    # (paper_id, bundle_local_id) -> merge key
    local_to_canonical: dict[tuple[str, str], str] = {}

    def _populate_name_index(cid: str, n: str, ec: str) -> None:
        """Add (normalized_name, entity_class) -> cid for name, synonyms, and spelling-normalized forms."""
        key = (n.lower().strip(), ec)
        if key[0]:
            name_type_to_canonical[key] = cid
        norm = _normalize_for_dedup(n)
        if norm and (norm, ec) != key:
            name_type_to_canonical[(norm, ec)] = cid

    def get_or_assign_canonical(
        paper_id: str,
        local_id: str,
        name: str,
        entity_class: str,
        entity_row: Optional[ExtractedEntityRow] = None,
    ) -> str:
        key_nt = (name.lower(), entity_class)
        key_local = (paper_id, local_id)
        if key_local in local_to_canonical:
            return local_to_canonical[key_local]
        # Check index first: incoming name matches prior entity's name or synonym (name↔synonym only)
        if key_nt in name_type_to_canonical:
            cid = name_type_to_canonical[key_nt]
            local_to_canonical[key_local] = cid
            return cid
        key_norm = (_normalize_for_dedup(name), entity_class)
        if key_norm in name_type_to_canonical:
            cid = name_type_to_canonical[key_norm]
            local_to_canonical[key_local] = cid
            return cid
        # Prefer authoritative ID from bundle entity (with UMLS→HGNC for genes)
        if entity_row is not None:
            auth = _preferred_authoritative_id(entity_row, lookup)
            if auth:
                for n in {name} | set(entity_row.synonyms or []):
                    _populate_name_index(auth, n, entity_class)
                local_to_canonical[key_local] = auth
                return auth
        # Authority lookup before synonym cache (prefer ontology IDs over fuzzy matches)
        if lookup is not None:
            lookup_type = _entity_class_to_lookup_type(entity_class, entity_class_to_lookup)
            if lookup_type:
                resolved = lookup.lookup_canonical_id_sync(name, lookup_type)
                if resolved:
                    for n in {name} | set((entity_row.synonyms or []) if entity_row else []):
                        _populate_name_index(resolved, n, entity_class)
                    local_to_canonical[key_local] = resolved
                    return resolved
        existing, _ = lookup_entity(cache, name, entity_class)
        if existing:
            for n in {name} | set((entity_row.synonyms or []) if entity_row else []):
                _populate_name_index(existing, n, entity_class)
            local_to_canonical[key_local] = existing
            return existing
        cid = _canonical_id_slug()
        for n in {name} | set((entity_row.synonyms or []) if entity_row else []):
            _populate_name_index(cid, n, entity_class)
        local_to_canonical[key_local] = cid
        return cid

    # 1) Build initial name/type index from all entities (use cache when available)
    for paper_id, bundle in bundles:
        for e in bundle.entities:
            name = e.name
            entity_class = e.entity_class
            cid = get_or_assign_canonical(paper_id, e.id, name, entity_class, entity_row=e)
            local_to_canonical[(paper_id, e.id)] = cid

    # 2) Auto-resolve high-confidence SAME_AS: merge entities
    def _entity_name_class(bundle: PerPaperBundle, local_id: str) -> tuple[str, str]:
        for e in bundle.entities:
            if e.id == local_id:
                return (e.name, e.entity_class)
        return (local_id, "?")

    for paper_id, bundle in bundles:
        for rel in bundle.relationships:
            if rel.predicate != SAME_AS_PREDICATE or rel.confidence < 0.85:
                continue
            sub_id = local_to_canonical.get((paper_id, rel.subject))
            obj_id = local_to_canonical.get((paper_id, rel.object_id))
            if sub_id and obj_id and sub_id != obj_id:
                # Prefer authoritative ID as winner so merged entity has canonical_id when possible
                winner = sub_id
                if _is_authoritative_id(obj_id) and not _is_authoritative_id(sub_id):
                    winner = obj_id
                for (pid, bid), cid in list(local_to_canonical.items()):
                    if cid in (obj_id, sub_id):
                        local_to_canonical[(pid, bid)] = winner
                for key_nt, cid in list(name_type_to_canonical.items()):
                    if cid in (obj_id, sub_id):
                        name_type_to_canonical[key_nt] = winner
                name_a, class_a = _entity_name_class(bundle, rel.subject)
                name_b, class_b = _entity_name_class(bundle, rel.object_id)
                add_same_as_to_cache(
                    cache,
                    {"name": name_a, "class": class_a, "canonical_id": winner},
                    {"name": name_b, "class": class_b, "canonical_id": winner},
                    rel.confidence,
                    "automated",
                    "merged",
                    list(rel.source_papers) if rel.source_papers else [paper_id],
                )

    # 3) Assign merge keys to any entity not yet assigned
    for paper_id, bundle in bundles:
        for e in bundle.entities:
            if (paper_id, e.id) not in local_to_canonical:
                cid = get_or_assign_canonical(paper_id, e.id, e.name, e.entity_class, entity_row=e)
                local_to_canonical[(paper_id, e.id)] = cid

    # 4) Ontology stub: leave all source="extracted", no ontology id changes

    # 5) Build merged entities: one row per merge key (entity_id); canonical_id only when authoritative
    canonical_entities: dict[str, dict[str, Any]] = {}
    for paper_id, bundle in bundles:
        for e in bundle.entities:
            merge_key = local_to_canonical.get((paper_id, e.id))
            if merge_key is None:
                continue
            if merge_key not in canonical_entities:
                canonical_entities[merge_key] = {
                    "entity_id": merge_key,
                    "canonical_id": merge_key if _is_authoritative_id(merge_key) else None,
                    "class": e.entity_class,
                    "name": e.name,
                    "synonyms": list(e.synonyms),
                    "source": e.source,
                    "source_papers": [],
                }
            if paper_id not in canonical_entities[merge_key]["source_papers"]:
                canonical_entities[merge_key]["source_papers"].append(paper_id)

    # 6) Accumulate relationships: (sub_canonical, predicate, obj_canonical) -> union source_papers, evidence_ids, max confidence
    triple_to_rel: dict[tuple[str, str, str], dict[str, Any]] = {}
    for paper_id, bundle in bundles:
        for rel in bundle.relationships:
            if rel.predicate == SAME_AS_PREDICATE and rel.confidence >= 0.85:
                continue  # already merged
            sub_c = local_to_canonical.get((paper_id, rel.subject))
            obj_c = local_to_canonical.get((paper_id, rel.object_id))
            if not sub_c or not obj_c:
                continue
            key = (sub_c, rel.predicate, obj_c)
            if key not in triple_to_rel:
                triple_to_rel[key] = {
                    "subject": sub_c,
                    "predicate": rel.predicate,
                    "object": obj_c,
                    "evidence_ids": [],
                    "provenance": [],
                    "source_papers": [],
                    "confidence": rel.confidence,
                    "linguistic_trust": getattr(rel, "linguistic_trust", None),
                }
            r = triple_to_rel[key]
            ev_by_id = {ev.id: ev for ev in bundle.evidence_entities}
            for eid in rel.evidence_ids or []:
                if eid not in r["evidence_ids"]:
                    r["evidence_ids"].append(eid)
                    ev = ev_by_id.get(eid)
                    # Evidence ID format: paper_id:section:paragraph_idx:method (e.g. PMC12756687:abstract:0:llm)
                    parts = eid.split(":")
                    section = parts[1] if len(parts) >= 2 else None
                    sentence = ev.text if ev else None
                    r["provenance"].append(ProvenanceEntry(section=section, sentence=sentence, citation_markers=[]).model_dump())
            for sp in rel.source_papers or [paper_id]:
                if sp not in r["source_papers"]:
                    r["source_papers"].append(sp)
            if rel.confidence > r["confidence"]:
                r["confidence"] = rel.confidence
                if getattr(rel, "linguistic_trust", None):
                    r["linguistic_trust"] = rel.linguistic_trust

    # 6b) Post-dedup reconciliation: group by (normalized_name, entity_class), merge duplicates
    by_name_class: dict[tuple[str, str], list[str]] = {}
    for ent in canonical_entities.values():
        n = (ent.get("name") or "").lower().strip()
        ec = ent.get("class") or "?"
        if n:
            by_name_class.setdefault((n, ec), []).append(ent["entity_id"])
    for (_name_key, ec_key), ids in list(by_name_class.items()):
        if len(ids) <= 1:
            continue
        # Pick winner: prefer authoritative ID, else first by deterministic sort
        ids_sorted = sorted(ids)
        winner_id: Optional[str] = None
        for eid in ids_sorted:
            if _is_authoritative_id(eid):
                winner_id = eid
                break
        if winner_id is None:
            winner_id = ids_sorted[0]
        losers = [i for i in ids_sorted if i != winner_id]
        for loser in losers:
            # Merge loser into winner
            if loser in canonical_entities and winner_id in canonical_entities:
                w_ent = canonical_entities[winner_id]
                l_ent = canonical_entities[loser]
                w_ent["synonyms"] = list(set((w_ent.get("synonyms") or []) + (l_ent.get("synonyms") or [])))
                for sp in l_ent.get("source_papers") or []:
                    if sp not in (w_ent.get("source_papers") or []):
                        w_ent.setdefault("source_papers", []).append(sp)
            # Rewrite triple_to_rel: replace loser with winner, merge on collision
            keys_to_del: list[tuple[str, str, str]] = []
            new_triples: dict[tuple[str, str, str], dict[str, Any]] = {}
            for (s, p, o), rel_data in list(triple_to_rel.items()):
                if loser not in (s, o):
                    continue
                new_s = winner_id if s == loser else s
                new_o = winner_id if o == loser else o
                new_key = (new_s, p, new_o)
                keys_to_del.append((s, p, o))

                def _pick_linguistic_trust(a: dict, b: dict) -> Any:
                    ca, cb = a.get("confidence", 0), b.get("confidence", 0)
                    if cb > ca and b.get("linguistic_trust"):
                        return b.get("linguistic_trust")
                    return a.get("linguistic_trust")

                if new_key in triple_to_rel and new_key != (s, p, o):
                    # Merge on collision
                    existing = triple_to_rel[new_key]
                    conf = max(existing.get("confidence", 0), rel_data.get("confidence", 0))
                    merged: dict[str, Any] = {
                        "subject": new_s,
                        "predicate": p,
                        "object": new_o,
                        "evidence_ids": list(set((existing.get("evidence_ids") or []) + (rel_data.get("evidence_ids") or []))),
                        "source_papers": list(set((existing.get("source_papers") or []) + (rel_data.get("source_papers") or []))),
                        "confidence": conf,
                        "linguistic_trust": _pick_linguistic_trust(existing, rel_data),
                    }
                    new_triples[new_key] = merged
                elif new_key in new_triples:
                    existing = new_triples[new_key]
                    conf = max(existing.get("confidence", 0), rel_data.get("confidence", 0))
                    merged = {
                        "subject": new_s,
                        "predicate": p,
                        "object": new_o,
                        "evidence_ids": list(set((existing.get("evidence_ids") or []) + (rel_data.get("evidence_ids") or []))),
                        "source_papers": list(set((existing.get("source_papers") or []) + (rel_data.get("source_papers") or []))),
                        "confidence": conf,
                        "linguistic_trust": _pick_linguistic_trust(existing, rel_data),
                    }
                    new_triples[new_key] = merged
                else:
                    new_triples[new_key] = {
                        **rel_data,
                        "subject": new_s,
                        "object": new_o,
                    }
            for k in keys_to_del:
                del triple_to_rel[k]
            for k, v in new_triples.items():
                triple_to_rel[k] = v
            # Update local_to_canonical and name_type_to_canonical
            for (pid, bid), cid in list(local_to_canonical.items()):
                if cid == loser:
                    local_to_canonical[(pid, bid)] = winner_id
            for nt_key, cid in list(name_type_to_canonical.items()):
                if cid == loser:
                    name_type_to_canonical[nt_key] = winner_id
            loser_name = canonical_entities.get(loser, {}).get("name", loser)
            winner_name = canonical_entities.get(winner_id, {}).get("name", winner_id)
            del canonical_entities[loser]
            # Add to synonym cache
            add_same_as_to_cache(
                cache,
                {"name": winner_name, "class": ec_key, "canonical_id": winner_id},
                {"name": loser_name, "class": ec_key, "canonical_id": winner_id},
                0.9,
                "automated",
                "reconciled",
                canonical_entities.get(winner_id, {}).get("source_papers", []),
            )

    # 7) Add all SAME_AS to synonym cache for persistence
    for paper_id, bundle in bundles:
        for rel in bundle.relationships:
            if rel.predicate != SAME_AS_PREDICATE:
                continue
            sub_c = local_to_canonical.get((paper_id, rel.subject))
            obj_c = local_to_canonical.get((paper_id, rel.object_id))
            if sub_c and obj_c:
                name_a, class_a = _entity_name_class(bundle, rel.subject)
                name_b, class_b = _entity_name_class(bundle, rel.object_id)
                add_same_as_to_cache(
                    cache,
                    {"name": name_a, "class": class_a, "canonical_id": sub_c},
                    {"name": name_b, "class": class_b, "canonical_id": obj_c},
                    rel.confidence,
                    "llm" if rel.asserted_by == "llm" else "automated",
                    rel.resolution,
                    list(rel.source_papers) if rel.source_papers else [paper_id],
                )

    # 7b) Embedding-based dedup for provisional entities (optional)
    cross_type_candidates: list[dict[str, Any]] = []
    if embedding_generator is not None:
        prov_entities = [e for e in canonical_entities.values() if (e.get("entity_id") or "").startswith("prov-")]
        if prov_entities:
            from kgraph.storage.memory import _cosine_similarity

            def _merge_entity_into(
                loser: str,
                winner: str,
                ce: dict,
                ttr: dict,
                ltc: dict,
                ntc: dict,
            ) -> None:
                if loser in ce and winner in ce:
                    w_ent, l_ent = ce[winner], ce[loser]
                    w_ent["synonyms"] = list(set((w_ent.get("synonyms") or []) + (l_ent.get("synonyms") or [])))
                    for sp in l_ent.get("source_papers") or []:
                        if sp not in (w_ent.get("source_papers") or []):
                            w_ent.setdefault("source_papers", []).append(sp)
                keys_to_del = []
                to_add: dict[tuple[str, str, str], dict[str, Any]] = {}
                for (s, p, o), rel in list(ttr.items()):
                    if loser not in (s, o):
                        continue
                    ns, no = winner if s == loser else s, winner if o == loser else o
                    nk = (ns, p, no)
                    keys_to_del.append((s, p, o))
                    if nk in to_add:
                        ex = to_add[nk]
                        to_add[nk] = {
                            "subject": ns,
                            "predicate": p,
                            "object": no,
                            "evidence_ids": list(set((ex.get("evidence_ids") or []) + (rel.get("evidence_ids") or []))),
                            "source_papers": list(set((ex.get("source_papers") or []) + (rel.get("source_papers") or []))),
                            "confidence": max(ex.get("confidence", 0), rel.get("confidence", 0)),
                        }
                    elif nk in ttr:
                        ex = ttr[nk]
                        to_add[nk] = {
                            "subject": ns,
                            "predicate": p,
                            "object": no,
                            "evidence_ids": list(set((ex.get("evidence_ids") or []) + (rel.get("evidence_ids") or []))),
                            "source_papers": list(set((ex.get("source_papers") or []) + (rel.get("source_papers") or []))),
                            "confidence": max(ex.get("confidence", 0), rel.get("confidence", 0)),
                        }
                    else:
                        to_add[nk] = {**rel, "subject": ns, "object": no}
                for k in keys_to_del:
                    del ttr[k]
                for k, v in to_add.items():
                    ttr[k] = v
                for (pid, bid), cid in list(ltc.items()):
                    if cid == loser:
                        ltc[(pid, bid)] = winner
                for k, cid in list(ntc.items()):
                    if cid == loser:
                        ntc[k] = winner
                del ce[loser]

            async def _embedding_pass() -> None:
                # Same-class merge
                by_class: dict[str, list[dict[str, Any]]] = {}
                for e in prov_entities:
                    ec = e.get("class") or "?"
                    by_class.setdefault(ec, []).append(e)
                for ec, ents in by_class.items():
                    if len(ents) < 2:
                        continue
                    texts = [x.get("name") or "" for x in ents]
                    if hasattr(embedding_generator, "generate_batch"):
                        embs = await embedding_generator.generate_batch(texts)
                    else:
                        embs = [await embedding_generator.generate(t) for t in texts]
                    merged_ids: set[str] = set()
                    for i, a in enumerate(ents):
                        if a["entity_id"] in merged_ids:
                            continue
                        for j, b in enumerate(ents):
                            if i >= j or b["entity_id"] in merged_ids:
                                continue
                            sim = _cosine_similarity(embs[i], embs[j])
                            if sim >= similarity_threshold:
                                winner, loser = a["entity_id"], b["entity_id"]
                                if _is_authoritative_id(winner) or (not _is_authoritative_id(loser) and winner < loser):
                                    winner, loser = loser, winner
                                _merge_entity_into(loser, winner, canonical_entities, triple_to_rel, local_to_canonical, name_type_to_canonical)
                                merged_ids.add(loser)
                # Cross-type candidates (flag-only)
                prov_remaining = [e for e in canonical_entities.values() if (e.get("entity_id") or "").startswith("prov-")]
                for i, a in enumerate(prov_remaining):
                    for j, b in enumerate(prov_remaining):
                        if i >= j or (a.get("class") or "") == (b.get("class") or ""):
                            continue
                        texts = [a.get("name") or "", b.get("name") or ""]
                        if hasattr(embedding_generator, "generate_batch"):
                            embs = await embedding_generator.generate_batch(texts)
                        else:
                            embs = [await embedding_generator.generate(t) for t in texts]
                        sim = _cosine_similarity(embs[0], embs[1])
                        if sim >= cross_type_threshold:
                            cross_type_candidates.append(
                                {
                                    "entity_id": a["entity_id"],
                                    "name": a.get("name", ""),
                                    "entity_class": a.get("class", ""),
                                    "source_papers": list(a.get("source_papers") or []),
                                    "similar_entity_id": b["entity_id"],
                                    "similar_name": b.get("name", ""),
                                    "similar_class": b.get("class", ""),
                                    "similar_source_papers": list(b.get("source_papers") or []),
                                    "similarity_score": round(sim, 4),
                                }
                            )

            try:
                asyncio.run(_embedding_pass())
            except Exception:  # pylint: disable=broad-except
                pass  # Embedding pass is best-effort

    # 8) Save synonym cache
    output_dir.mkdir(parents=True, exist_ok=True)
    save_synonym_cache(synonym_cache_path, cache)

    if cross_type_candidates:
        with open(output_dir / "cross_type_candidates.json", "w", encoding="utf-8") as f:
            json.dump(cross_type_candidates, f, indent=2)

    # 9) Write merged output (do not touch original bundles)
    by_paper: dict[str, dict[str, str]] = {}
    for (paper_id, local_id), merge_key in local_to_canonical.items():
        by_paper.setdefault(paper_id, {})[local_id] = merge_key
    id_map_path = output_dir / "id_map.json"
    with open(id_map_path, "w", encoding="utf-8") as f:
        json.dump(by_paper, f, indent=2)

    entities_path = output_dir / "entities.json"
    relationships_path = output_dir / "relationships.json"
    with open(entities_path, "w", encoding="utf-8") as f:
        json.dump(list(canonical_entities.values()), f, indent=2)
    with open(relationships_path, "w", encoding="utf-8") as f:
        json.dump(list(triple_to_rel.values()), f, indent=2)

    return {
        "entities_count": len(canonical_entities),
        "relationships_count": len(triple_to_rel),
        "bundles_processed": len(bundles),
        "entities_path": str(entities_path),
        "relationships_path": str(relationships_path),
    }

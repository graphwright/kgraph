#!/usr/bin/env python3
"""fetch_vocab: Fast vocabulary extraction across papers → vocab.json + seeded synonym cache.

Runs a cheap LLM prompt per paper (entities only, no relationships), merges results
into a shared vocabulary, runs UMLS type validation on entities with umls_id, and
writes vocab.json plus an ingest-compatible seeded_synonym_cache.json. extract and
ingest consume these for consistent names/types and dedup seeding.

Usage:
  python -m examples.medlit.scripts.fetch_vocab --input-dir pmc_xmls/ --output-dir vocab --llm-backend anthropic
  python -m examples.medlit.scripts.fetch_vocab --input-dir pmc_xmls/ --output-dir vocab --llm-backend ollama --papers "PMC115*.xml"
"""

import argparse
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

import examples.medlit.domain_spec as _ds  # noqa: E402  # pylint: disable=wrong-import-position


def _pass1a_system_prompt() -> str:
    """Build fetch_vocab system prompt from domain_spec."""
    type_enum = sorted(_ds.NORMALIZED_TO_BUNDLE.keys())
    return (
        """Extract all named biomedical entities from this paper.
For each entity return:
  - name: canonical form (not an abbreviation)
  - type: one of ["""
        + ", ".join(type_enum)
        + """]
  - abbreviations: list of abbreviations or alternate names used in this paper
  - umls_id: UMLS CUI if you are confident, else null

Return a single JSON object with key "entities" containing an array of these objects. No other keys. Valid JSON only."""
    )


def _normalize_name(name: str) -> str:
    return name.lower().strip()


def _vocab_key(entry: dict[str, Any]) -> tuple[str, str]:
    """Key for merging: (normalized name, type)."""
    return (_normalize_name(entry.get("name", "")), (entry.get("type") or "").strip().lower())


async def _paper_content(path: Path, input_dir: Path) -> tuple[str, str]:
    """Return (content_text, paper_id) for a paper file."""
    from examples.medlit.scripts.extract import _paper_content_fallback, _paper_content_from_parser

    content_type = "application/xml" if path.suffix.lower() == ".xml" else "application/json"
    with open(path, "rb") as f:
        raw = f.read()
    try:
        content, paper_info = await _paper_content_from_parser(raw, content_type, str(path))
    except Exception:
        content, paper_info = _paper_content_fallback(raw, str(path))
    if paper_info is None:
        content, paper_info = _paper_content_fallback(raw, str(path))
    paper_id = paper_info.pmcid or path.stem
    return content or "(no content)", paper_id


def _merge_vocab_into(existing: list[dict[str, Any]], new_entries: list[dict[str, Any]], source_paper: str) -> None:
    """Merge new_entries into existing in place; same (name, type) adds source_paper to source_papers."""
    by_key: dict[tuple[str, str], dict[str, Any]] = {_vocab_key(e): e for e in existing}
    for e in new_entries:
        key = _vocab_key(e)
        if key in by_key:
            papers = set(by_key[key].get("source_papers") or [])
            papers.add(source_paper)
            by_key[key]["source_papers"] = sorted(papers)
            # Keep existing umls_id if new doesn't have one
            if not by_key[key].get("umls_id") and e.get("umls_id"):
                by_key[key]["umls_id"] = e["umls_id"]
            if e.get("abbreviations"):
                abbr = set(by_key[key].get("abbreviations") or [])
                abbr.update(e.get("abbreviations") or [])
                by_key[key]["abbreviations"] = sorted(abbr)
        else:
            entry = {
                "name": e.get("name", ""),
                "type": (e.get("type") or "").strip().lower(),
                "abbreviations": list(e.get("abbreviations") or []),
                "umls_id": e.get("umls_id"),
                "source_papers": [source_paper],
                "umls_type_validated": False,
                "umls_type_conflict": None,
            }
            by_key[key] = entry
            existing.append(entry)


def _run_umls_validation(vocab_entries: list[dict[str, Any]]) -> None:
    """Run UMLS type validation on entries with umls_id; update type and set umls_type_validated/umls_type_conflict."""
    from examples.medlit.pipeline.authority_lookup import validate_umls_type

    from kgraph.logging import setup_logging

    logger = setup_logging()
    cache: dict[tuple[str, str], tuple[bool, str | None]] = {}
    for entry in vocab_entries:
        umls_id = entry.get("umls_id") if isinstance(entry.get("umls_id"), str) else None
        if not umls_id or not umls_id.strip():
            continue
        assigned = (entry.get("type") or "").strip().lower()
        ok, correct_type = validate_umls_type(umls_id, assigned, _cache=cache)
        entry["umls_type_validated"] = True
        if ok:
            entry["umls_type_conflict"] = None
            continue
        if correct_type:
            logger.warning(
                {
                    "message": "UMLS type correction",
                    "name": entry.get("name"),
                    "umls_id": umls_id,
                    "assigned_type": assigned,
                    "expected_type": correct_type,
                },
                pprint=True,
            )
            entry["type"] = correct_type
            entry["umls_type_conflict"] = None
        else:
            entry["umls_type_conflict"] = "ambiguous"
            # Leave type as-is for human review


def _vocab_to_seeded_cache(
    vocab_entries: list[dict[str, Any]],
    normalized_to_bundle: dict[str, str],
) -> dict[str, list[dict[str, Any]]]:
    """Build ingest synonym cache format from vocab list so lookup_entity returns canonical_id."""
    from kgraph.pipeline.synonym_cache import _normalize

    cache: dict[str, list[dict[str, Any]]] = {}
    for e in vocab_entries:
        name = e.get("name", "")
        if not name:
            continue
        etype_normalized = (e.get("type") or "").strip().lower()
        bundle_class = normalized_to_bundle.get(etype_normalized) or etype_normalized or "Other"
        canonical_id = e.get("umls_id") or None
        source_papers = e.get("source_papers") or []
        entity_snapshot = {
            "name": name,
            "class": bundle_class,
            "canonical_id": canonical_id,
        }
        entry = {
            "entity_a": entity_snapshot,
            "entity_b": entity_snapshot,
            "resolution": "merged",
            "confidence": 1.0,
            "asserted_by": "fetch_vocab",
            "source_papers": source_papers,
        }
        key = _normalize(name)
        if key not in cache:
            cache[key] = []
        cache[key].append(entry)
    return cache


def _atomic_write_json(path: Path, data: Any) -> None:
    """Write JSON to path via temp file then rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


async def run_fetch_vocab(
    input_dir: Path,
    output_dir: Path,
    llm_backend: str,
    papers: Optional[list[str]] = None,
    limit: Optional[int] = None,
) -> None:
    """Run fetch_vocab: extract vocabulary from papers, merge, validate UMLS types, write vocab + seeded cache."""
    from kgraph.pipeline.pass1_llm import get_pass1_llm

    normalized_to_bundle = _ds.NORMALIZED_TO_BUNDLE

    llm = get_pass1_llm(llm_backend)
    output_dir.mkdir(parents=True, exist_ok=True)
    vocab_path = output_dir / "vocab.json"
    seed_cache_path = output_dir / "seeded_synonym_cache.json"

    # Discover files
    files: list[Path] = []
    if papers is not None:
        for pattern in papers:
            pattern = pattern.strip()
            if not pattern:
                continue
            files.extend(input_dir.glob(pattern))
        files = sorted(set(files))
    else:
        for ext in ("*.xml", "*.json"):
            files.extend(input_dir.glob(ext))
        files = sorted(set(files))
    if limit is not None:
        files = files[:limit]
    if not files:
        print(f"No XML/JSON files in {input_dir}", file=sys.stderr)
        return

    # Load existing vocab if present (merge mode)
    vocab_entries: list[dict[str, Any]] = []
    if vocab_path.exists():
        try:
            with open(vocab_path, encoding="utf-8") as f:
                data = json.load(f)
            vocab_entries = list(data) if isinstance(data, list) else []
        except Exception as e:
            print(f"Warning: could not load existing vocab: {e}", file=sys.stderr)

    print(f"fetch_vocab: {len(files)} paper(s), backend={llm_backend}, output={output_dir}", file=sys.stderr)
    for path in files:
        content, paper_id = await _paper_content(path, input_dir)
        try:
            raw = await llm.generate_json(
                system_prompt=_pass1a_system_prompt(),
                user_message=content[:500000],
                temperature=0.0,
                max_tokens=8192,
            )
        except Exception as e:
            print(f"  ERROR {path.name}: {e}", file=sys.stderr)
            continue
        entities = raw.get("entities") if isinstance(raw, dict) else []
        if not isinstance(entities, list):
            entities = []
        # Normalize type to lowercase
        for en in entities:
            if en.get("type"):
                en["type"] = str(en["type"]).strip().lower()
        _merge_vocab_into(vocab_entries, entities, paper_id)
        print(f"  {path.name} -> paper_id={paper_id}, entities={len(entities)}", file=sys.stderr)

    _run_umls_validation(vocab_entries)
    seeded_cache = _vocab_to_seeded_cache(vocab_entries, normalized_to_bundle)
    _atomic_write_json(vocab_path, vocab_entries)
    _atomic_write_json(seed_cache_path, seeded_cache)
    print(f"Wrote {vocab_path} ({len(vocab_entries)} entries), {seed_cache_path}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="fetch_vocab: Fast vocabulary extraction → vocab.json + seeded_synonym_cache.json",
    )
    parser.add_argument("--input-dir", type=Path, required=True, help="Directory containing paper XML/JSON files")
    parser.add_argument("--output-dir", type=Path, default=Path("vocab"), help="Output directory for vocab.json and seeded_synonym_cache.json")
    parser.add_argument("--llm-backend", type=str, choices=("anthropic", "openai", "ollama"), default=os.environ.get("LLM_BACKEND", "anthropic"))
    parser.add_argument("--papers", type=str, default=None, metavar="GLOB[,GLOB,...]", help="Comma-separated glob patterns for input files")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of papers to process")
    args = parser.parse_args()
    papers_list: Optional[list[str]] = None
    if args.papers is not None:
        papers_list = [p.strip() for p in args.papers.split(",") if p.strip()]
    asyncio.run(
        run_fetch_vocab(
            args.input_dir,
            args.output_dir,
            args.llm_backend,
            papers_list,
            args.limit,
        )
    )


if __name__ == "__main__":
    main()

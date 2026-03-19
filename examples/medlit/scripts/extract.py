#!/usr/bin/env python3
"""extract: Extract entities and relationships from papers via LLM → per-paper bundle JSON.

Reads papers from --input-dir (JATS XML or JSON), calls the configured LLM once per paper,
and writes one JSON file per paper to --output-dir. These bundles are immutable;
ingest reads them and writes overlays or a merged graph elsewhere.

Requires an LLM backend: --llm-backend anthropic | openai | ollama.
Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or run Ollama locally. See LLM_SETUP.md.

Usage:
  python -m examples.medlit.scripts.extract --input-dir pmc_xmls/ --output-dir bundles/ --llm-backend anthropic
  python -m examples.medlit.scripts.extract --input-dir pmc_xmls/ --output-dir bundles/ --llm-backend ollama --limit 1
  python -m examples.medlit.scripts.extract --input-dir pmc_xmls/ --output-dir bundles/ --papers "PMC127*.xml,PMC128*.json"
"""

import argparse
import hashlib
import inspect
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Add repo root for imports
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Load .env from repo root so ANTHROPIC_API_KEY etc. are available
try:
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

from examples.medlit.bundle_models import (  # noqa: E402  # pylint: disable=wrong-import-position
    AuthorInfo,
    EvidenceEntityRow,
    ExtractedEntityRow,
    PaperInfo,
    PerPaperBundle,
    RelationshipRow,
    StudyDesignMetadata,
)
from examples.medlit_schema.base import (  # noqa: E402  # pylint: disable=wrong-import-position
    ExecutionInfo,
    ExtractionPipelineInfo,
    ExtractionProvenance,
    ModelInfo,
    PromptInfo,
)

# Placeholders the LLM outputs when it lacks the real paper ID; replace with actual paper_id
_EVIDENCE_PAPER_ID_PLACEHOLDERS = frozenset(
    {
        "paper_id",
        "PMC_PLACEHOLDER",
        "PMC_ID_NOT_PROVIDED",
        "PMC_UNKNOWN",
        "PMC11000000",
        "==CURRENT_PAPER==",
    }
)


def _fix_evidence_paper_id(evidence_id: str, paper_id: str) -> str:
    """Replace placeholder or hallucinated paper_id in evidence ID with actual.

    When processing paper X, the only valid paper_id in evidence is X. Replace:
    - Placeholders (PMC_UNKNOWN, paper_id, PMC11000000, etc.)
    - PMC IDs that are not the current paper (hallucinated citations)
    """
    if ":" not in evidence_id:
        return evidence_id
    first, rest = evidence_id.split(":", 1)
    if first in _EVIDENCE_PAPER_ID_PLACEHOLDERS:
        return f"{paper_id}:{rest}"
    # PMC[0-9]+ that is not the current paper → hallucinated citation, replace
    if re.match(r"^PMC\d+$", first) and first != paper_id:
        return f"{paper_id}:{rest}"
    return evidence_id


def _replace_current_paper_in_bundle(obj: Any, paper_id: str) -> None:
    """Recursively replace ==CURRENT_PAPER== with paper_id in dict/list/str (mutates in place)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and "==CURRENT_PAPER==" in v:
                obj[k] = v.replace("==CURRENT_PAPER==", paper_id)
            else:
                _replace_current_paper_in_bundle(v, paper_id)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, str) and "==CURRENT_PAPER==" in item:
                obj[i] = item.replace("==CURRENT_PAPER==", paper_id)
            else:
                _replace_current_paper_in_bundle(item, paper_id)


def _git_info() -> dict:
    """Return git_commit, git_commit_short, git_branch, git_dirty, repo_url."""
    out = {
        "git_commit": "",
        "git_commit_short": "",
        "git_branch": "",
        "git_dirty": False,
        "repo_url": "https://github.com/org/medlit",
    }
    try:
        out["git_commit"] = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5.0,
            cwd=REPO_ROOT,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    try:
        out["git_commit_short"] = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5.0,
            cwd=REPO_ROOT,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    try:
        out["git_branch"] = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5.0,
            cwd=REPO_ROOT,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5.0,
            cwd=REPO_ROOT,
            check=False,
        )
        out["git_dirty"] = bool(r.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return out


def build_provenance(
    llm_name: str,
    llm_version: str,
    prompt_version: str = "v1",
    prompt_template: str = "medlit_extraction_v1",
    prompt_checksum: Optional[str] = None,
    duration_seconds: Optional[float] = None,
    schema_version: Optional[str] = None,
) -> ExtractionProvenance:
    """Build extraction_provenance for extract output."""
    git = _git_info()
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return ExtractionProvenance(
        models={"llm": ModelInfo(name=llm_name, version=llm_version)},
        extraction_pipeline=ExtractionPipelineInfo(
            name="medlit_extract",
            version="0.1.0",
            git_commit=git["git_commit"] or "unknown",
            git_commit_short=git["git_commit_short"] or "unknown",
            git_branch=git["git_branch"] or "unknown",
            git_dirty=git["git_dirty"],
            repo_url=git["repo_url"],
        ),
        prompt=PromptInfo(
            version=prompt_version,
            template=prompt_template,
            checksum=prompt_checksum,
            schema_version=schema_version,
        ),
        execution=ExecutionInfo(
            timestamp=now,
            hostname=os.environ.get("HOSTNAME", "unknown"),
            python_version=sys.version.split()[0],
            duration_seconds=duration_seconds,
        ),
        entity_resolution=None,
    )


def normalize_entity_type(raw_type: str, normalized_to_bundle: dict[str, str]) -> str:
    """Map raw LLM type string to bundle entity_class (PascalCase). Unknown types -> 'Other'."""
    if not raw_type or not str(raw_type).strip():
        return "Other"
    normalized = str(raw_type).strip().lower().replace(" ", "").replace("_", "")
    return normalized_to_bundle.get(normalized, "Other")


def _default_system_prompt(
    vocab_entries: Optional[list[dict]] = None,
    domain_spec: Optional[Any] = None,
) -> str:
    """Build system prompt from domain_spec via Jinja2 template."""
    from kgraph.templates import render_extraction_prompt

    return render_extraction_prompt(
        config_dir=None,
        vocab_entries=vocab_entries,
        domain_spec=domain_spec,
    )


async def _paper_content_from_parser(raw_content: bytes, content_type: str, source_uri: str) -> tuple[str, Optional[PaperInfo]]:
    """Extract text and minimal PaperInfo from raw content using existing parser."""
    from examples.medlit.pipeline.parser import JournalArticleParser

    parser = JournalArticleParser()
    doc = await parser.parse(raw_content, content_type, source_uri)
    # Build content for LLM: title + abstract + body
    parts = [doc.title or ""]
    if getattr(doc, "content", None):
        parts.append(str(doc.content))
    text = "\n\n".join(p for p in parts if p)
    paper_id = doc.document_id or Path(source_uri).stem
    author_details_raw = doc.metadata.get("author_details", []) if doc.metadata else []
    author_details = [AuthorInfo(**a) if isinstance(a, dict) else a for a in author_details_raw] if author_details_raw else None
    cited_pmc_ids = doc.metadata.get("cited_pmc_ids", []) if doc.metadata else []
    info = PaperInfo(
        pmcid=paper_id if paper_id.startswith("PMC") else None,
        title=doc.title or "",
        authors=list(getattr(doc, "authors", [])) or [],
        author_details=author_details,
        document_id=doc.document_id or "",
        cited_pmc_ids=cited_pmc_ids,
    )
    return text or "(no content)", info


STUDY_DESIGN_PROMPT = """Extract study design metadata from this biomedical paper. Focus on the Methods section and abstract.

Return a single JSON object with exactly these keys:
- "study_type": string or null (e.g. "RCT", "observational", "case_report", "meta_analysis", "review")
- "sample_size": integer or null (number of participants/subjects)
- "multicenter": boolean (true if multi-site study)
- "held_out_validation": boolean (true if held-out/test set used for validation)

Return ONLY valid JSON, no markdown or commentary."""


async def _extract_study_design(llm: Any, content: str) -> Optional[StudyDesignMetadata]:
    """Second LLM call: extract study design from Methods/abstract. Returns None on failure."""
    try:
        raw = await llm.generate_json(
            system_prompt=STUDY_DESIGN_PROMPT,
            user_message=content[:50000],
            temperature=0.0,
            max_tokens=512,
        )
        if not isinstance(raw, dict):
            return None
        return StudyDesignMetadata(
            study_type=raw.get("study_type"),
            sample_size=raw.get("sample_size"),
            multicenter=bool(raw.get("multicenter", False)),
            held_out_validation=bool(raw.get("held_out_validation", False)),
        )
    except Exception:  # pylint: disable=broad-except
        return None


def _paper_content_fallback(raw_content: bytes, source_uri: str) -> tuple[str, PaperInfo]:
    """Fallback: use raw text and filename for paper id."""
    text = raw_content.decode("utf-8", errors="replace")
    stem = Path(source_uri).stem
    return text or "(no content)", PaperInfo(pmcid=stem if stem.startswith("PMC") else None, title=stem, authors=[])


async def run_extract(  # pylint: disable=too-many-statements
    input_dir: Path,
    output_dir: Path,
    llm_backend: str,
    limit: Optional[int] = None,
    papers: Optional[list[str]] = None,
    system_prompt: Optional[str] = None,
    vocab_file: Optional[Path] = None,
) -> None:
    """Run extract: for each paper in input_dir, call LLM and write bundle JSON to output_dir."""
    from kgraph.pipeline.pass1_llm import get_pass1_llm

    import examples.medlit.domain_spec as _ds

    normalized_to_bundle = _ds.NORMALIZED_TO_BUNDLE
    schema_version = hashlib.sha256(inspect.getsource(_ds).encode()).hexdigest()[:8]

    vocab_entries: Optional[list[dict]] = None
    if vocab_file is not None and vocab_file.exists():
        try:
            import json

            with open(vocab_file, encoding="utf-8") as f:
                data = json.load(f)
            vocab_entries = data if isinstance(data, list) else None
        except Exception:
            vocab_entries = None

    llm = get_pass1_llm(llm_backend)
    prompt = system_prompt or _default_system_prompt(vocab_entries, domain_spec=_ds)
    prompt_checksum = hashlib.sha256(prompt.encode()).hexdigest()[:16]

    # Discover input files: by glob patterns or all *.xml/*.json
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

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"extract: {len(files)} paper(s), backend={llm_backend}, output={output_dir}", file=sys.stderr)

    for _, path in enumerate(files):
        content_type = "application/xml" if path.suffix.lower() in (".xml",) else "application/json"
        with open(path, "rb") as f:
            raw = f.read()
        try:
            content, paper_info = await _paper_content_from_parser(raw, content_type, str(path))
        except Exception:
            content, paper_info = _paper_content_fallback(raw, str(path))
        if paper_info is None:
            content, paper_info = _paper_content_fallback(raw, str(path))

        paper_id = paper_info.pmcid or path.stem
        out_path = output_dir / f"paper_{paper_id}.json"
        if out_path.exists():
            print(f"  Skip (exists): {out_path.name}", file=sys.stderr)
            continue

        start = time.perf_counter()
        try:
            raw_bundle = await llm.generate_json(
                system_prompt=prompt,
                user_message=content[:500000],  # cap size
                temperature=0.1,
                max_tokens=16384,
            )
            _replace_current_paper_in_bundle(raw_bundle, paper_id)
        except Exception as e:
            print(f"  ERROR {path.name}: {e}", file=sys.stderr)
            continue
        duration = time.perf_counter() - start

        # Normalize entity types to bundle PascalCase, then parse rows
        raw_entities = raw_bundle.get("entities", [])
        for en in raw_entities:
            if isinstance(en, dict) and "class" in en:
                en["class"] = normalize_entity_type(en.get("class") or "", normalized_to_bundle)
        valid_entities = []
        for en in raw_entities:
            if isinstance(en, dict) and not en.get("name"):
                print(f"  SKIP entity missing name: {en}", file=sys.stderr)
                continue
            try:
                valid_entities.append(ExtractedEntityRow.model_validate(en))
            except Exception as ve:
                print(f"  SKIP invalid entity ({ve}): {en}", file=sys.stderr)
        entities = valid_entities
        evidence_entities = [EvidenceEntityRow.model_validate(ev) for ev in raw_bundle.get("evidence_entities", [])]
        relationships = [RelationshipRow.model_validate(r) for r in raw_bundle.get("relationships", [])]
        # Override source_papers with actual paper_id — LLM often outputs "paper_id" literally
        for rel in relationships:
            rel.source_papers = [paper_id]
        # Replace placeholder paper IDs in evidence (LLM outputs PMC_UNKNOWN, paper_id, etc.)
        for ev in evidence_entities:
            if ev.paper_id in _EVIDENCE_PAPER_ID_PLACEHOLDERS:
                ev.paper_id = paper_id
            ev.id = _fix_evidence_paper_id(ev.id, paper_id)
        for rel in relationships:
            rel.evidence_ids = [_fix_evidence_paper_id(eid, paper_id) for eid in (rel.evidence_ids or [])]

        # Use paper from LLM if present and valid, else parser
        raw_paper = raw_bundle.get("paper") or {}
        raw_authors = raw_paper.get("authors", paper_info.authors)
        if isinstance(raw_authors, list):
            authors = raw_authors
        elif isinstance(raw_authors, str):
            authors = [raw_authors] if raw_authors.strip() else []
        else:
            authors = list(paper_info.authors) if paper_info.authors else []
        # Never use raw_paper.get("pmcid") — the LLM can hallucinate wrong IDs (e.g. from
        # citations or training). Use only parser/file-derived IDs for document provenance.
        study_design = await _extract_study_design(llm, content)
        author_details = paper_info.author_details or [AuthorInfo(name=a, affiliations=[]) for a in (authors or [])]
        paper = PaperInfo(
            doi=raw_paper.get("doi") or paper_info.doi,
            pmcid=paper_info.pmcid or (paper_id if str(paper_id).startswith("PMC") else None),
            title=raw_paper.get("title") or paper_info.title,
            authors=authors,
            author_details=author_details,
            document_id=paper_id,
            journal=raw_paper.get("journal"),
            year=raw_paper.get("year"),
            study_type=raw_paper.get("study_type"),
            eco_type=raw_paper.get("eco_type"),
            study_design=study_design,
            cited_pmc_ids=paper_info.cited_pmc_ids,
        )
        llm_name = getattr(llm, "model", llm_backend)
        provenance = build_provenance(
            llm_name=llm_name,
            llm_version="",
            prompt_checksum=f"sha256:{prompt_checksum}",
            duration_seconds=round(duration, 2),
            schema_version=schema_version,
        )
        bundle = PerPaperBundle(
            paper=paper,
            extraction_provenance=provenance,
            entities=entities,
            evidence_entities=evidence_entities,
            relationships=relationships,
            notes=raw_bundle.get("notes", []),
        )
        # Provenance expansion: Author, Institution, Paper + AUTHORED, AFFILIATED_WITH, DESCRIBED (top 2)
        from examples.medlit.pipeline.provenance_expansion import expand_provenance

        exp_entities, exp_rels = expand_provenance(bundle)
        bundle.entities.extend(exp_entities)
        bundle.relationships.extend(exp_rels)
        with open(out_path, "w", encoding="utf-8") as f:
            import json

            json.dump(bundle.to_bundle_dict(), f, indent=2)
        print(f"  Wrote {out_path.name} ({len(entities)} entities, {len(relationships)} rels)", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="extract: Extract per-paper bundle JSON via LLM (immutable output).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input-dir", type=Path, required=True, help="Directory containing paper XML/JSON files")
    parser.add_argument("--output-dir", type=Path, default=Path("extracted"), help="Output directory for bundle JSONs")
    parser.add_argument(
        "--llm-backend",
        type=str,
        choices=("anthropic", "openai", "ollama"),
        default=os.environ.get("LLM_BACKEND", "ollama"),
        help="LLM backend (default: LLM_BACKEND or ollama)",
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit number of papers to process")
    parser.add_argument(
        "--papers",
        type=str,
        default=None,
        metavar="GLOB[,GLOB,...]",
        help="Comma-separated glob patterns for input files (e.g. PMC127*.xml,PMC128*.json). Resolved under --input-dir. If omitted, all *.xml and *.json are used.",
    )
    parser.add_argument(
        "--vocab-file",
        type=Path,
        default=None,
        help="Path to vocab.json (fetch_vocab output). If present, entity list is included in the extraction prompt and types are normalized.",
    )
    args = parser.parse_args()
    import asyncio

    papers_list: Optional[list[str]] = None
    if args.papers is not None:
        papers_list = [p.strip() for p in args.papers.split(",") if p.strip()]

    asyncio.run(
        run_extract(
            args.input_dir,
            args.output_dir,
            args.llm_backend,
            args.limit,
            papers_list,
            vocab_file=args.vocab_file,
        )
    )


if __name__ == "__main__":
    main()

"""
Background worker for paper ingestion jobs.

Processes jobs from a queue: fetch URL, run Pass 1/2/3 pipeline, load bundle incrementally.
"""

import asyncio
import fcntl
import logging
import os
import re
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable

import httpx
from sqlmodel import Session

from query.storage_factory import get_engine
from storage.backends.postgres import PostgresStorage
from storage.backends.sqlite import SQLiteStorage
from storage.interfaces import StorageInterface

logger = logging.getLogger(__name__)

_job_queue: asyncio.Queue[str] = asyncio.Queue()
_worker_tasks: list[asyncio.Task] = []
_shutdown = False

# PMC article URL pattern (e.g. https://www.ncbi.nlm.nih.gov/articles/PMC12345/)
_PMC_URL_RE = re.compile(r"PMC(\d+)", re.IGNORECASE)
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def _storage_for_worker() -> tuple[StorageInterface, Callable[[], None]]:
    """Return (storage, close_fn) for use in the worker. Caller must call close_fn when done."""
    engine, db_url = get_engine()
    if db_url.startswith("postgresql://"):
        session = Session(engine)
        storage: StorageInterface = PostgresStorage(session)
        return storage, session.close
    db_path = db_url.replace("sqlite:///", "").strip() or "./test.db"
    if db_path == ":memory:" or not db_path:
        db_path = "./test.db"
    storage = SQLiteStorage(db_path)
    return storage, storage.close


def _workspace_root() -> Path:
    """Persistent workspace root from env, defaulting to ./ingest_workspace."""
    root = Path(os.environ.get("INGEST_WORKSPACE_ROOT", "./ingest_workspace")).resolve()
    return root


def _ensure_workspace_dirs(root: Path) -> tuple[Path, Path, Path, Path]:
    """Create and return (bundles_dir, merged_dir, output_dir, vocab_dir). These persist across jobs.

    Note: output_dir (medlit_bundle/) is always fully rebuilt by Pass 3.
    The true incremental state is bundles_dir + merged_dir + vocab_dir (especially synonym_cache.json).
    """
    bundles_dir = root / "pass1_bundles"
    merged_dir = root / "medlit_merged"
    output_dir = root / "medlit_bundle"
    vocab_dir = root / "pass1_vocab"
    for d in (bundles_dir, merged_dir, output_dir, vocab_dir):
        d.mkdir(parents=True, exist_ok=True)
    return bundles_dir, merged_dir, output_dir, vocab_dir


@contextmanager
def _workspace_lock(workspace_root: Path):
    """File lock serializing Pass 2 → Pass 3 → load_bundle_incremental across workers."""
    lock_path = workspace_root / ".ingest.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "w", encoding="utf-8") as fh:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def _run_pass2_pass3_load(
    workspace_root: Path,
    bundles_dir: Path,
    merged_dir: Path,
    output_dir: Path,
) -> None:
    """Run Pass 2, Pass 3, and load_bundle_incremental under workspace lock. Raises on failure."""
    from kgbundle import BundleManifestV1

    from examples.medlit.pipeline.bundle_builder import run_pass3  # pylint: disable=import-error
    from examples.medlit.pipeline.dedup import run_pass2  # pylint: disable=import-error

    seeded_cache = workspace_root / "pass1_vocab" / "seeded_synonym_cache.json"
    synonym_cache_path = seeded_cache if seeded_cache.exists() else merged_dir / "synonym_cache.json"

    with _workspace_lock(workspace_root):
        run_pass2(
            bundle_dir=bundles_dir,
            output_dir=merged_dir,
            synonym_cache_path=synonym_cache_path,
            canonical_id_cache_path=None,
        )
        run_pass3(merged_dir, bundles_dir, output_dir)
        manifest_path = output_dir / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Pass 3 did not produce {manifest_path}")
        manifest_data = manifest_path.read_text()
        manifest = BundleManifestV1.model_validate_json(manifest_data)
        load_storage, load_close = _storage_for_worker()
        try:
            load_storage.load_bundle_incremental(manifest, str(output_dir))
        finally:
            load_close()


async def start_worker(max_workers: int = 1) -> None:
    """Start background worker tasks that process the ingest job queue."""
    global _shutdown
    _shutdown = False
    for _ in range(max_workers):
        task = asyncio.create_task(_worker_loop())
        _worker_tasks.append(task)
    logger.info("Started %s ingest worker(s)", max_workers)


async def stop_worker() -> None:
    """Cancel worker tasks and stop processing new jobs."""
    global _shutdown
    _shutdown = True
    for task in _worker_tasks:
        task.cancel()
    for task in _worker_tasks:
        try:
            await task
        except asyncio.CancelledError:
            pass
    _worker_tasks.clear()
    logger.info("Stopped ingest workers")


async def enqueue_job(job_id: str) -> None:
    """Add a job id to the queue. Non-blocking."""
    await _job_queue.put(job_id)


async def _worker_loop() -> None:
    """Pull job IDs from the queue and run ingestion."""
    while not _shutdown:
        try:
            job_id = await _job_queue.get()
            try:
                await _run_ingest_job(job_id)
            finally:
                _job_queue.task_done()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.exception("Worker loop error: %s", e)


async def _run_ingest_job(job_id: str) -> None:
    """Fetch job, run pipeline (Pass 1 → 2 → 3), load bundle incrementally, update job."""
    storage, close_storage = _storage_for_worker()
    try:
        job = storage.get_ingest_job(job_id)
        if job is None:
            logger.warning("Ingest job not found: %s", job_id)
            return

        timeout_seconds = int(os.environ.get("INGEST_TIMEOUT", "600"))
        try:
            await asyncio.wait_for(_run_ingest_job_impl(job_id, storage, job), timeout=timeout_seconds)
        except asyncio.TimeoutError:
            storage.update_ingest_job(
                job_id,
                status="failed",
                completed_at=datetime.now(timezone.utc),
                error=f"Job timed out after {timeout_seconds}s",
            )
            logger.error("Ingest job %s timed out", job_id)
        except Exception as e:
            logger.exception("Ingest job %s failed: %s", job_id, e)
            storage.update_ingest_job(
                job_id,
                status="failed",
                completed_at=datetime.now(timezone.utc),
                error=str(e),
            )
    finally:
        close_storage()


async def _run_ingest_job_impl(job_id: str, storage: StorageInterface, job) -> None:  # pylint: disable=too-many-statements
    """Core implementation: fetch URL, run pipeline, load bundle."""
    import json

    from kgbundle import BundleManifestV1

    from examples.medlit.scripts.pass1_extract import run_pass1  # pylint: disable=import-error
    from examples.medlit.scripts.pass1a_vocab import run_pass1a  # pylint: disable=import-error

    url = job.url
    logger.info("Ingest job %s starting: url=%s", job_id, url)
    storage.update_ingest_job(job_id, status="running", started_at=datetime.now(timezone.utc))

    pmcid = None
    paper_title = None
    entities_added = 0
    relationships_added = 0

    workspace = _workspace_root()
    bundles_dir, merged_dir, output_dir, vocab_dir = _ensure_workspace_dirs(workspace)

    with TemporaryDirectory(prefix="ingest_input_") as tmp_input:
        input_dir = Path(tmp_input)

        # Fetch URL content
        t_fetch_start = time.perf_counter()
        match = _PMC_URL_RE.search(url)
        if match:
            pmcid_num = match.group(1)
            pmcid = f"PMC{pmcid_num}"
            efetch_url = f"{EFETCH_URL}?db=pmc&id={pmcid_num}&rettype=xml"
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.get(efetch_url)
                resp.raise_for_status()
                input_path = input_dir / f"{pmcid}.xml"
                input_path.write_bytes(resp.content)
            logger.info(
                "Ingest job %s: fetched PMC XML in %.1fs, %s bytes",
                job_id,
                time.perf_counter() - t_fetch_start,
                len(resp.content),
            )
        else:
            async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                suffix = ".xml" if "xml" in (resp.headers.get("content-type") or "").lower() else ".json"
                url_stem = re.sub(r"[^\w-]", "_", url.rstrip("/").split("/")[-1]) or "paper"
                input_path = input_dir / f"{url_stem}{suffix}"
                input_path.write_bytes(resp.content)
            logger.info(
                "Ingest job %s: fetched URL in %.1fs, %s bytes -> %s",
                job_id,
                time.perf_counter() - t_fetch_start,
                len(resp.content),
                input_path.name,
            )

        # No-op guard: paper already in workspace
        if pmcid is not None and (bundles_dir / f"paper_{pmcid}.json").exists():
            storage.update_ingest_job(
                job_id,
                status="complete",
                completed_at=datetime.now(timezone.utc),
                paper_title=paper_title or None,
                pmcid=pmcid,
                entities_added=0,
                relationships_added=0,
                error=None,
            )
            logger.info("Ingest job %s: skipped (paper %s already in workspace)", job_id, pmcid)
            return

        # Pass 1a: merge this paper's vocab into workspace vocab (outside lock)
        llm_backend = os.environ.get("PASS1_LLM_BACKEND", "anthropic")
        logger.info("Ingest job %s: starting Pass 1a (backend=%s)", job_id, llm_backend)
        await run_pass1a(input_dir, vocab_dir, llm_backend, papers=None, limit=1)
        # Pass 1b: full extraction with vocabulary context
        logger.info("Ingest job %s: starting Pass 1 (backend=%s)", job_id, llm_backend)
        t0 = time.perf_counter()
        await run_pass1(
            input_dir,
            bundles_dir,
            llm_backend,
            limit=1,
            vocab_file=vocab_dir / "vocab.json",
        )
        pass1_sec = time.perf_counter() - t0

        bundle_files = sorted(bundles_dir.glob("paper_*.json"))
        logger.info(
            "Ingest job %s: Pass 1 done in %.1fs, bundle_files=%s",
            job_id,
            pass1_sec,
            [p.name for p in bundle_files],
        )
        if not bundle_files:
            logger.warning("Ingest job %s: Pass 1 produced no bundle files", job_id)
            storage.update_ingest_job(
                job_id,
                status="failed",
                completed_at=datetime.now(timezone.utc),
                error="Pass 1 produced no bundle files (LLM may have failed, timed out, or returned invalid JSON).",
            )
            return

        if pmcid is not None:
            target_bundle = bundles_dir / f"paper_{pmcid}.json"
        elif bundle_files:
            target_bundle = bundle_files[-1]  # most recently written
        else:
            target_bundle = None
        if target_bundle is not None and target_bundle.exists():
            try:
                data = json.loads(target_bundle.read_text(encoding="utf-8"))
                paper = data.get("paper") or {}
                if paper.get("title"):
                    paper_title = paper["title"]
            except Exception:
                pass

        # Pass 2 + Pass 3 + load (under lock, in thread)
        logger.info("Ingest job %s: starting Pass 2 + Pass 3 + load", job_id)
        t_pass23_start = time.perf_counter()
        try:
            await asyncio.to_thread(
                _run_pass2_pass3_load,
                workspace,
                bundles_dir,
                merged_dir,
                output_dir,
            )
        except Exception as e:
            logger.exception("Ingest job %s: Pass 2/3/load failed: %s", job_id, e)
            storage.update_ingest_job(
                job_id,
                status="failed",
                completed_at=datetime.now(timezone.utc),
                error=f"Pass 2/3/load failed: {e}",
            )
            return
        pass23_sec = time.perf_counter() - t_pass23_start
        logger.info("Ingest job %s: Pass 2+3+load done in %.1fs", job_id, pass23_sec)

        manifest_path = output_dir / "manifest.json"
        if not manifest_path.exists():
            storage.update_ingest_job(
                job_id,
                status="failed",
                completed_at=datetime.now(timezone.utc),
                error="Pass 3 did not produce manifest.json",
            )
            return

        manifest_data = manifest_path.read_text()
        manifest = BundleManifestV1.model_validate_json(manifest_data)
        if manifest.entities and manifest.entities.path:
            entities_file = output_dir / manifest.entities.path
            if entities_file.exists():
                entities_added = sum(1 for _ in entities_file.open())
        if manifest.relationships and manifest.relationships.path:
            rels_file = output_dir / manifest.relationships.path
            if rels_file.exists():
                relationships_added = sum(1 for _ in rels_file.open())

        storage.update_ingest_job(
            job_id,
            status="complete",
            completed_at=datetime.now(timezone.utc),
            paper_title=paper_title,
            pmcid=pmcid,
            entities_added=entities_added,
            relationships_added=relationships_added,
            error=None,
        )
        logger.info(
            "Ingest job %s complete: %s entities, %s relationships (Pass1=%.1fs Pass2+3+load=%.1fs)",
            job_id,
            entities_added,
            relationships_added,
            pass1_sec,
            pass23_sec,
        )

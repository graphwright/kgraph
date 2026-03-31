"""
MCP Server implementation using bfsql (BFS-QL) as the core graph query engine.

Provides the five standard BFS-QL tools (describe_schema, search_entities,
bfs_query, intersect_subgraphs, describe_entity) via PostgresBackend, plus kgserver-specific tools
for ingestion, bundle inspection, and paper source retrieval.
"""

import os
import zipfile
from pathlib import Path
from typing import Optional, Any

from bfsql.backends.postgres import PostgresBackend
from bfsql.server import create_server

# ------------------------------------------------------------------
# Core BFS-QL MCP server (four tools: describe_schema, search_entities,
# bfs_query, describe_entity) backed by Postgres.
# ------------------------------------------------------------------

mcp_server = create_server(
    backend_or_factory=PostgresBackend.create,
    graph_description="Knowledge graph extracted from medical and scientific literature. "
    "Contains entities (diseases, genes, drugs, proteins, papers, ...) and "
    "relationships extracted by an LLM pipeline from PubMed/PMC papers.",
)


# ------------------------------------------------------------------
# kgserver-specific tools added on top of the BFS-QL base.
# ------------------------------------------------------------------


def _get_storage():
    """Context manager yielding a storage instance. Extracted for testability."""
    from contextlib import contextmanager, closing
    from query.storage_factory import get_engine, get_storage as _storage_factory

    @contextmanager
    def _cm():
        get_engine()
        with closing(_storage_factory()) as storage_gen:
            storage = next(storage_gen, None)
            if storage is None:
                raise RuntimeError("Failed to get storage instance")
            yield storage

    return _cm()


def _get_bundle_path() -> Path:
    """Resolve BUNDLE_PATH; raise ValueError if unset or invalid."""
    path_str = os.getenv("BUNDLE_PATH")
    if not path_str:
        raise ValueError("BUNDLE_PATH is not set")
    path = Path(path_str)
    if not path.exists():
        raise ValueError(f"BUNDLE_PATH '{path_str}' does not exist")
    return path


def _read_from_bundle(relative_path: str) -> str:
    """Read file from bundle (directory or ZIP). Returns file contents as string."""
    bundle_path = _get_bundle_path()
    if bundle_path.suffix == ".zip":
        with zipfile.ZipFile(bundle_path, "r") as zf:
            with zf.open(relative_path) as f:
                return f.read().decode("utf-8", errors="replace")
    file_path = Path(bundle_path) / relative_path
    if not file_path.exists():
        raise FileNotFoundError(f"File not found in bundle: {relative_path}")
    return file_path.read_text(encoding="utf-8", errors="replace")


@mcp_server.tool()
async def ingest_paper(url: str) -> dict:
    """
    Ingest a medical paper from a URL into the knowledge graph.

    Kicks off a background job. Returns immediately with a job_id.
    Poll check_ingest_status(job_id) to track progress.
    Supports PMC full-text URLs and direct XML/JSON URLs.

    Returns:
        Dict with job_id, status, url, message.
    """
    from contextlib import closing
    from query.storage_factory import get_engine, get_storage
    from mcp_server.ingest_worker import enqueue_job

    get_engine()
    with closing(get_storage()) as storage_gen:
        storage = next(storage_gen, None)
        if storage is None:
            raise RuntimeError("Failed to get storage instance")
        job = storage.create_ingest_job(url)
    await enqueue_job(job.id)
    return {
        "job_id": job.id,
        "status": "queued",
        "url": url,
        "message": "Job queued. Use check_ingest_status(job_id) to track progress.",
    }


@mcp_server.tool()
def check_ingest_status(job_id: str) -> dict:
    """
    Check the status of a paper ingestion job.

    Returns:
        Dict with job_id, status, url, paper_title, pmcid, entities_added,
        relationships_added, error, created_at, started_at, completed_at.
    Status values: queued | running | complete | failed | not_found
    """
    from contextlib import closing
    from query.storage_factory import get_engine, get_storage

    get_engine()
    with closing(get_storage()) as storage_gen:
        storage = next(storage_gen, None)
        if storage is None:
            raise RuntimeError("Failed to get storage instance")
        job = storage.get_ingest_job(job_id)
    if job is None:
        return {
            "job_id": job_id,
            "status": "not_found",
            "url": "",
            "paper_title": None,
            "pmcid": None,
            "entities_added": 0,
            "relationships_added": 0,
            "error": "No such job",
            "created_at": None,
            "started_at": None,
            "completed_at": None,
        }
    return {
        "job_id": job.id,
        "status": job.status,
        "url": job.url,
        "paper_title": job.paper_title,
        "pmcid": job.pmcid,
        "entities_added": job.entities_added,
        "relationships_added": job.relationships_added,
        "error": job.error,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }


@mcp_server.tool()
def get_paper_source(paper_id: str, max_chars: Optional[int] = None) -> str:
    """
    Retrieve the raw JATS-XML source of a paper for mention-inspection diagnostics.

    Reads from bundle sources/ directory (or inside a ZIP bundle). Use with
    get_mentions to verify that extracted mentions match the source text.

    Args:
        paper_id: Paper identifier (e.g. PMC12345). Accepts with or without .xml suffix.
        max_chars: If set, truncate the returned string to this length.

    Returns:
        Raw XML string. Raises ValueError if BUNDLE_PATH unset or paper not found.
    """
    base_id = paper_id.removesuffix(".xml") if paper_id.endswith(".xml") else paper_id
    relative_path = f"sources/{base_id}.xml"
    try:
        content = _read_from_bundle(relative_path)
    except FileNotFoundError:
        raise ValueError(f"Paper {paper_id} not found in sources/") from None
    if max_chars is not None:
        content = content[:max_chars]
    return content


@mcp_server.tool()
def get_mentions(paper_id: Optional[str] = None) -> list[dict]:
    """
    Retrieve entity mentions from the bundle for mention-inspection diagnostics.

    Reads mentions.jsonl (MentionRow schema). Filter by document_id when paper_id
    is provided. Use with get_paper_source to verify extracted mentions against
    the source text.

    Args:
        paper_id: If provided, filter to mentions where document_id matches.
            For medlit, values are like PMC12345. If None, return all mentions.

    Returns:
        List of mention dicts (entity_id, document_id, text_span, etc.).
        Empty list if mentions.jsonl missing or no matches.
    """
    try:
        content = _read_from_bundle("mentions.jsonl")
    except FileNotFoundError:
        return []
    from kgbundle import MentionRow

    filter_doc_id = None
    if paper_id is not None:
        filter_doc_id = paper_id.removesuffix(".xml") if paper_id.endswith(".xml") else paper_id

    rows: list[dict] = []
    for line in content.strip().splitlines():
        if not line.strip():
            continue
        try:
            row = MentionRow.model_validate_json(line)
            d = row.model_dump()
            if filter_doc_id is not None and d.get("document_id") != filter_doc_id:
                continue
            rows.append(d)
        except Exception:
            continue
    return rows


@mcp_server.tool()
def get_bundle_info() -> dict | None:
    """
    Get bundle metadata for debugging and provenance.

    Returns information about the currently loaded knowledge graph bundle,
    including bundle ID, domain, creation timestamp, and metadata.

    Returns:
        Bundle dictionary with fields: bundleId, domain, createdAt, metadata.
        Returns None if no bundle is loaded.
    """
    from contextlib import closing
    from query.storage_factory import get_engine, get_storage

    get_engine()
    with closing(get_storage()) as storage_gen:
        storage = next(storage_gen, None)
        if storage is None:
            raise RuntimeError("Failed to get storage instance")
        bundle = storage.get_bundle_info()
    if bundle is None:
        return None
    return {
        "bundleId": bundle.bundle_id,
        "domain": bundle.domain,
        "createdAt": bundle.created_at.isoformat() if bundle.created_at else None,
        "metadata": bundle.metadata,
    }


@mcp_server.tool()
def graphql_query(query: str, variables: Optional[dict[str, Any]] = None) -> dict:
    """
    Run an arbitrary GraphQL query against the knowledge graph.

    Uses the same schema as the HTTP /graphql endpoint. Use this for custom
    query shapes, multiple roots in one request, or when the discrete tools
    are not enough. The schema supports: entity(id), entities(limit, offset,
    filter), relationship(subjectId, predicate, objectId), relationships(limit,
    offset, filter), bundle.

    Args:
        query: GraphQL query string (e.g. "{ entity(id: \"MeSH:D001943\") { name } }").
        variables: Optional map of variable names to values for parameterized queries.

    Returns:
        Dictionary with "data" (result payload, or None if errors) and "errors"
        (list of error dicts, or None if successful).
    """
    import strawberry
    from query.graphql_schema import Query

    graphql_schema = strawberry.Schema(query=Query)
    with _get_storage() as storage:
        context = {"storage": storage}
        result = graphql_schema.execute_sync(
            query,
            variable_values=variables or {},
            context_value=context,
        )
    return {
        "data": result.data,
        "errors": [{"message": e.message, "path": getattr(e, "path", None)} for e in (result.errors or [])] if result.errors else None,
    }

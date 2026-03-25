"""
Standalone MCP server entrypoint (SSE on port 8001).

Run with: uvicorn mcp_main:app --host 0.0.0.0 --port 8001

SSE endpoint: http://localhost:8001/sse (mount at root so path stays /sse).
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from mcp_server import mcp_server
from mcp_server import ingest_worker
from query.storage_factory import get_engine
from storage.models import IngestJob

sse_app = mcp_server.http_app(path="/sse", transport="sse")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create ingest_jobs table and start/stop the background ingest worker."""
    engine, _ = get_engine()
    SQLModel.metadata.create_all(engine, tables=[IngestJob.__table__])
    max_workers = int(os.environ.get("INGEST_MAX_WORKERS", "1"))
    await ingest_worker.start_worker(max_workers=max_workers)
    yield
    await ingest_worker.stop_worker()


app = FastAPI(title="Knowledge Graph MCP", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health():
    """Health check for container/orchestration."""
    return {"status": "ok"}


# Mount at root so FastMCP's /sse route is exposed as /sse (not /sse/sse)
app.mount("/", sse_app)

"""FastAPI application entry point for the identity server.

The identity server is a domain-agnostic microservice that handles entity
identity for knowledge graphs: resolving mentions to canonical IDs, detecting
synonyms, merging duplicate entities, and managing the
provisional → canonical → merged lifecycle.

API documentation is available at ``/docs`` (Swagger UI) and ``/redoc``.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import create_db_and_tables
from .models import HealthResponse
from .routers.dump import router as dump_router
from .routers.identity import router as identity_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    logger.info("Identity server starting up — creating database tables if needed")
    create_db_and_tables()
    yield
    logger.info("Identity server shutting down")


app = FastAPI(
    title="Identity Server",
    description=(
        "Domain-agnostic microservice for entity identity management in knowledge graphs. "
        "Resolves mentions to canonical IDs, detects synonyms, merges duplicates, and manages "
        "the provisional → canonical → merged entity lifecycle."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(identity_router)
app.include_router(dump_router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    """Return service health status."""
    return HealthResponse(status="ok")

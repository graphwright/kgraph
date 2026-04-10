"""FastAPI router implementing the identity server HTTP endpoints.

Each endpoint creates a ``PostgresIdentityServer`` instance with the
injected session and domain client, calls the appropriate method, and
returns the result.

Endpoints
---------
POST /resolve          Resolve a mention to a canonical or provisional entity ID.
POST /promote          Attempt to promote a provisional entity to canonical status.
POST /find-synonyms    Detect entities synonymous with the given entity.
POST /merge            Merge a set of entities into a single survivor.
POST /on-entity-added  Event hook: trigger synonym detection after an entity insert.
"""

import logging

from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..cache import AuthorityCache
from ..core import PostgresIdentityServer
from ..database import get_session
from ..domain_client import DomainClient
from ..models import (
    FindSynonymsRequest,
    FindSynonymsResponse,
    MergeRequest,
    MergeResponse,
    OnEntityAddedRequest,
    PromoteRequest,
    PromoteResponse,
    ResolveRequest,
    ResolveResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Shared dependency: DomainClient (one per request, stateless)
# ---------------------------------------------------------------------------


def get_domain_client() -> DomainClient:
    """FastAPI dependency that provides a ``DomainClient`` instance."""
    return DomainClient()


def get_authority_cache() -> AuthorityCache:
    """FastAPI dependency that provides a Redis-backed ``AuthorityCache``."""
    return AuthorityCache.from_env()


def get_identity_server(
    session: Session = Depends(get_session),
    domain_client: DomainClient = Depends(get_domain_client),
    authority_cache: AuthorityCache = Depends(get_authority_cache),
) -> PostgresIdentityServer:
    """FastAPI dependency that assembles a ``PostgresIdentityServer``."""
    return PostgresIdentityServer(session=session, domain_client=domain_client, authority_cache=authority_cache)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/resolve", response_model=ResolveResponse)
async def resolve(
    request: ResolveRequest,
    identity_server: PostgresIdentityServer = Depends(get_identity_server),
) -> ResolveResponse:
    """Resolve a mention string to a canonical or provisional entity ID.

    Creates a new provisional entity if no existing entity or authority match
    is found.  Idempotent: resolving the same mention twice returns the same ID.
    """
    entity_id = await identity_server.resolve(
        mention=request.mention,
        entity_type=request.entity_type,
        document_id=request.document_id,
        embedding=request.embedding,
    )
    return ResolveResponse(entity_id=entity_id)


@router.post("/promote", response_model=PromoteResponse)
async def promote(
    request: PromoteRequest,
    identity_server: PostgresIdentityServer = Depends(get_identity_server),
) -> PromoteResponse:
    """Attempt to promote a provisional entity to canonical status.

    Returns the canonical ID (new or pre-existing), or the survivor ID if
    the entity was already merged.  Idempotent.
    """
    entity_id = await identity_server.promote(provisional_id=request.entity_id)
    return PromoteResponse(entity_id=entity_id)


@router.post("/find-synonyms", response_model=FindSynonymsResponse)
async def find_synonyms(
    request: FindSynonymsRequest,
    identity_server: PostgresIdentityServer = Depends(get_identity_server),
) -> FindSynonymsResponse:
    """Return the IDs of entities considered synonymous with the given entity.

    Read-only — reports candidates without merging.  Call ``/merge`` to act
    on the results.
    """
    synonym_ids = await identity_server.find_synonyms(entity_id=request.entity_id)
    return FindSynonymsResponse(synonym_ids=synonym_ids)


@router.post("/merge", response_model=MergeResponse)
async def merge(
    request: MergeRequest,
    identity_server: PostgresIdentityServer = Depends(get_identity_server),
) -> MergeResponse:
    """Merge a set of entities into a single survivor.

    All references from absorbed entities are redirected to the survivor.
    Absorbed entities are marked ``status=MERGED`` with ``merged_into`` set.
    Idempotent: already-merged entities are skipped.
    """
    survivor_id = await identity_server.merge(entity_ids=request.entity_ids, survivor_id=request.survivor_id)
    return MergeResponse(survivor_id=survivor_id)


@router.post("/on-entity-added", status_code=200)
async def on_entity_added(
    request: OnEntityAddedRequest,
    identity_server: PostgresIdentityServer = Depends(get_identity_server),
) -> dict:
    """Event hook called after an entity is inserted or updated.

    Triggers synonym detection and, if synonyms are found, calls the domain
    service to select a survivor and performs the merge automatically.
    """
    await identity_server.on_entity_added(entity_id=request.entity_id, context=request.context)
    return {}

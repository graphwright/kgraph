"""Export and import endpoints for identity server state serialization.

Provides a simple dump/load mechanism for development and deployment workflows,
equivalent to ``pg_dump``/``pg_restore`` but scoped to just the entity table
and expressed as line-delimited JSON (NDJSON) for portability and diffability.

Endpoints
---------
GET  /dump         Stream all entity rows as NDJSON.
POST /load         Load NDJSON entity rows, skipping rows that already exist.
DELETE /wipe       Delete all entity rows (dev only; requires confirmation header).
"""

import json
import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from ..database import get_session
from ..db_models import Entity

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


def _entities_to_ndjson(session: Session) -> bytes:
    """Return all entity rows serialised as NDJSON bytes, ordered by entity_id."""
    entities = session.exec(select(Entity).order_by(Entity.entity_id)).all()
    lines = []
    for entity in entities:
        row = {
            "entity_id": entity.entity_id,
            "entity_type": entity.entity_type,
            "name": entity.name,
            "status": entity.status,
            "confidence": entity.confidence,
            "usage_count": entity.usage_count,
            "source": entity.source,
            "canonical_url": entity.canonical_url,
            "synonyms": entity.synonyms,
            "properties": entity.properties,
            "merged_into": entity.merged_into,
            "embedding": entity.embedding,
        }
        lines.append(json.dumps(row, separators=(",", ":")))
    return ("\n".join(lines) + ("\n" if lines else "")).encode()


@router.get(
    "/dump",
    summary="Export all entity rows as NDJSON",
    description="""
Export all entity rows as newline-delimited JSON (one JSON object per line).
Suitable for piping to a file for backup or transfer between environments.

Usage::

    curl http://identity-server:8080/admin/dump > entities.ndjson

Each line is a complete entity record. Rows are ordered by ``entity_id``
for reproducible diffs.
""",
    response_class=StreamingResponse,
)
def dump(session: Session = Depends(get_session)) -> StreamingResponse:
    """Export all entity rows as NDJSON."""
    content = _entities_to_ndjson(session)
    return StreamingResponse(
        iter([content]),
        media_type="application/x-ndjson",
        headers={"Content-Disposition": "attachment; filename=entities.ndjson"},
    )


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------


@router.post(
    "/load",
    summary="Load entity rows from NDJSON",
    description="""
Load entity rows from a newline-delimited JSON request body. Rows whose
``entity_id`` already exists in the database are skipped (upsert-on-conflict
is intentionally absent — existing data is authoritative).

Usage::

    curl -X POST http://identity-server:8080/admin/load \\
         -H 'Content-Type: application/x-ndjson' \\
         --data-binary @entities.ndjson

Returns a summary of rows inserted and skipped.
""",
)
async def load(
    request: Request,
    session: Session = Depends(get_session),
) -> dict:
    """Load NDJSON entity rows, skipping existing entity_ids."""
    inserted = 0
    skipped = 0
    errors = 0

    request_body = await request.body()
    lines = request_body.splitlines()
    for lineno, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            logger.warning("load: line %d: invalid JSON: %s", lineno, exc)
            errors += 1
            continue

        entity_id = row.get("entity_id")
        if not entity_id:
            logger.warning("load: line %d: missing entity_id", lineno)
            errors += 1
            continue

        existing = session.get(Entity, entity_id)
        if existing is not None:
            skipped += 1
            continue

        try:
            entity = Entity(
                entity_id=entity_id,
                entity_type=row.get("entity_type", "unknown"),
                name=row.get("name"),
                status=row.get("status"),
                confidence=row.get("confidence"),
                usage_count=row.get("usage_count"),
                source=row.get("source"),
                canonical_url=row.get("canonical_url"),
                synonyms=row.get("synonyms") or [],
                properties=row.get("properties") or {},
                merged_into=row.get("merged_into"),
                embedding=row.get("embedding"),
            )
            session.add(entity)
            session.commit()
            inserted += 1
        except Exception as exc:
            session.rollback()
            logger.warning("load: line %d: failed to insert entity_id=%s: %s", lineno, entity_id, exc)
            errors += 1

    logger.info("load: inserted=%d skipped=%d errors=%d", inserted, skipped, errors)
    return {"inserted": inserted, "skipped": skipped, "errors": errors}


# ---------------------------------------------------------------------------
# Wipe (dev only)
# ---------------------------------------------------------------------------


@router.delete(
    "/wipe",
    summary="Delete all entity rows",
    description="""
**Development use only.** Delete all rows from the entity table.

Requires the ``X-Confirm-Wipe: yes`` header to prevent accidental invocation.

Usage::

    curl -X DELETE http://identity-server:8080/admin/wipe \\
         -H 'X-Confirm-Wipe: yes'
""",
)
def wipe(
    session: Session = Depends(get_session),
    x_confirm_wipe: str = Header(default=""),
) -> dict:
    """Delete all entity rows. Requires X-Confirm-Wipe: yes header."""
    if x_confirm_wipe.strip().lower() != "yes":
        raise HTTPException(
            status_code=400,
            detail="Set header X-Confirm-Wipe: yes to confirm deletion of all entity rows.",
        )
    result = session.exec(select(Entity)).all()
    count = len(result)
    for entity in result:
        session.delete(entity)
    session.commit()
    logger.warning("wipe: deleted %d entity rows", count)
    return {"deleted": count}

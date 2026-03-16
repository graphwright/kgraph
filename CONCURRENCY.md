# Concurrency Issues in `ingest_paper` at Scale

This document identifies concurrency hazards in the `ingest_paper` MCP tool and
proposes mitigations for each. The context is a future production system with
thousands of simultaneous users, each potentially triggering paper ingestion at
the same time.

## Background

The `ingest_paper` MCP tool (implemented in `kgserver/mcp_server/ingest_worker.py`)
runs a multi-pass pipeline for each paper:

- **Pass 1a:** Fast vocabulary extraction — reads and writes `pass1_vocab/vocab.json`
  and `pass1_vocab/seeded_synonym_cache.json` in a shared workspace directory.
- **Pass 1b:** Full LLM extraction — writes one JSON bundle per paper to
  `pass1_bundles/paper_{pmcid}.json` in the shared workspace.
- **Pass 2:** Deduplication — reads *all* files in `pass1_bundles/` and writes
  merged output to `medlit_merged/`.
- **Pass 3:** Bundle build — reads `medlit_merged/` and writes the final bundle.
- **Load:** Calls `load_bundle_incremental` to upsert into Postgres.

Pass 2 → Pass 3 → Load are already serialized by a `fcntl.flock` file lock
(`_workspace_lock`). Pass 1a and Pass 1b are currently unprotected.

The default worker count is 1 (`start_worker(max_workers=1)`), which serializes
all jobs end-to-end and masks these issues in the current demo. They will surface
if worker count is increased or multiple server replicas are deployed.

---

## Issue 1: Pass 1a Vocab File Race

**Problem:** Pass 1a reads `vocab.json` and `seeded_synonym_cache.json`, merges
in vocabulary from the new paper, and writes them back. With concurrent workers,
two workers can read the same stale file, independently merge their updates, and
the last writer silently discards the other's changes.

**Proposed fix — Redis distributed lock:**

Add Redis to the stack (one line in `docker-compose.yml`, official image, zero
configuration needed for basic use). Before Pass 1a runs, each worker acquires a
Redis lock keyed on the workspace path, e.g. `lock:vocab:{workspace_root}`. The
lock should have a TTL (e.g. 120s) so a crashed worker cannot leave it
permanently held.

```python
async with redis_lock("vocab:ingest_workspace"):
    await run_pass1a(input_dir, vocab_dir, llm_backend, papers=None, limit=1)
```

Redis is preferred over extending the existing `fcntl.flock` for two reasons:

1. `fcntl.flock` only works within a single host. Redis works correctly across
   multiple replicas of `mcpserver`.
2. Redis locks automatically expire on worker crash; file locks do not.

**Alternative — Postgres table for vocab:**

Replace `vocab.json` and `seeded_synonym_cache.json` with Postgres tables (JSONB
columns work fine for the existing data structures). Reads and writes become
atomic transactions with no explicit locking needed. This is the right long-term
answer if vocab data needs to be queryable, auditable, or part of the same
transactional boundary as entities and relationships. It requires schema changes
and a migration step, making it higher-effort than the Redis approach.

Redis and Postgres are not mutually exclusive: Redis for coordination, Postgres
for persistent vocab state, is a valid combination.

---

## Issue 2: Pass 1b Output Collision (Same PMC ID, Two Workers)

**Problem:** If two jobs are simultaneously ingesting the same PMC ID, both pass
the "already exists" guard and both write to `pass1_bundles/paper_{pmcid}.json`.
This is a classic TOCTOU (time-of-check/time-of-use) race. The guard currently
reads:

```python
if pmcid is not None and (bundles_dir / f"paper_{pmcid}.json").exists():
    # skip
```

Two workers can both evaluate the condition as False before either writes the
file.

**Proposed fix — Redis per-pmcid lock:**

Use Redis `SET NX EX` (set-if-not-exists with expiry) keyed on the pmcid, e.g.
`lock:pmcid:PMC12345`. The first worker acquires it and proceeds; the second
either waits or fast-fails with "already in progress." This is more explicit and
reliable than the file-existence check.

```python
async with redis_lock(f"pmcid:{pmcid}"):
    if not (bundles_dir / f"paper_{pmcid}.json").exists():
        await run_pass1b(...)
```

**Alternative — Postgres unique constraint:**

Add a `pmcid` unique constraint to the `ingest_jobs` table (or a separate
`ingest_lock` table). Use `INSERT ... ON CONFLICT DO NOTHING` or `SELECT FOR
UPDATE` to serialize access. Works without Redis but is slightly more verbose.

---

## Issue 3: Pass 2 Reading a Partial Bundle File

**Problem:** Pass 2 scans `pass1_bundles/` and reads every `paper_*.json` file
it finds. If worker A is mid-write to its bundle file at the moment worker B
acquires the workspace lock and starts Pass 2, Pass 2 may read a truncated or
partially-written JSON file, causing a parse error or silently dropping data.

**Proposed fix — atomic write-then-rename in Pass 1b:**

This is a standard POSIX idiom and requires no new infrastructure. Pass 1b writes
to a temp file in the same directory (same filesystem, so the rename is atomic),
then renames it into the final path:

```python
tmp_path = bundles_dir / f".tmp_{pmcid}_{os.getpid()}.json"
tmp_path.write_text(json.dumps(bundle_data))
tmp_path.rename(bundles_dir / f"paper_{pmcid}.json")
```

`os.rename()` is atomic on Linux/POSIX — Pass 2 either sees the complete file or
nothing. This fix is orthogonal to the Redis vs. Postgres choice and should be
implemented regardless.

The relevant write is in `examples/medlit/scripts/pass1_extract.py` around the
line that writes `output_dir / f"paper_{paper_id}.json"`.

---

## Summary

| Issue | Root cause | Recommended fix | Effort |
|---|---|---|---|
| Pass 1a vocab race | Concurrent read-modify-write of JSON files | Redis distributed lock (cross-replica safe) | Low |
| Pass 1b same-pmcid collision | TOCTOU on file-existence check | Redis `SET NX EX` per pmcid | Low |
| Pass 2 reads partial bundle | File written concurrently with Pass 2 scan | Atomic write-then-rename in Pass 1b | Very low |

All three fixes are independent and can be implemented incrementally. The
write-then-rename fix (Issue 3) is the cheapest and most impactful and should be
done first. The Redis fixes (Issues 1 and 2) depend on adding Redis to the stack,
which is a small infrastructure change but unlocks correct behavior across
multiple replicas.

## Infrastructure Change: Adding Redis

Add to `docker-compose.yml`:

```yaml
redis:
  image: redis:7-alpine
  restart: unless-stopped
  networks:
    - kgserver-network
  profiles: ["api"]
```

Add `REDIS_URL: redis://redis:6379` to the `mcpserver` environment. Use
`redis.asyncio` (included in the `redis` Python package) for async lock
acquisition in the worker.

---

## Identity Server Specification

### Purpose

The identity server is the authoritative component for entity identity across
the knowledge graph. Its responsibilities are:

1. **Canonical ID assignment** — resolving a mention to a canonical entity,
   creating a provisional entity if no canonical match is found.
2. **Promotion** — elevating a provisional entity to canonical status when
   domain-defined thresholds are met.
3. **Synonym recognition** — detecting when two entities refer to the same
   real-world concept.
4. **Merging** — collapsing two canonical entities into one, redirecting all
   references from the absorbed entity to the survivor.

The identity server must be correct under concurrent access from multiple
worker processes and multiple server replicas. It must be available at both
ingestion time (during MCP tool calls) and query time (during chat sessions,
where ingestion may also be occurring simultaneously).

---

### Abstract Interface

```python
from abc import ABC, abstractmethod
from typing import Optional

class IdentityServer(ABC):

    @abstractmethod
    async def resolve(self, mention: str, context: dict) -> str:
        """
        Resolve a mention string to an entity ID.

        Performs authority lookup (domain-defined) and returns a canonical ID
        if one is found, otherwise creates and returns a new provisional ID.
        This operation must be idempotent: resolving the same mention twice
        returns the same ID.

        Parameters
        ----------
        mention:
            The surface form of the entity mention.
        context:
            Domain-defined context (e.g. document ID, domain name, metadata)
            used by authority lookup and synonym detection.

        Returns
        -------
        str
            A canonical or provisional entity ID.
        """

    @abstractmethod
    async def promote(self, provisional_id: str) -> str:
        """
        Attempt to promote a provisional entity to canonical status.

        The domain-defined promotion policy determines whether promotion is
        warranted. If the entity is already canonical, this is a no-op and
        returns the existing canonical ID. This operation must be idempotent.

        Returns
        -------
        str
            The canonical ID (new or pre-existing).
        """

    @abstractmethod
    async def find_synonyms(self, entity_id: str) -> list[str]:
        """
        Return the IDs of entities considered synonymous with the given entity.

        Synonym criteria are domain-defined (e.g. semantic vector similarity,
        shared external identifier, string normalization). This method does not
        perform any merges; it only reports candidates.
        """

    @abstractmethod
    async def merge(self, entity_ids: list[str], survivor_id: str) -> str:
        """
        Merge a set of entities into a single survivor.

        All references (relationships, mentions, bundle edges) that point to
        any absorbed entity must be redirected to the survivor. Absorbed
        entities are marked as merged (not deleted) so that incoming external
        references remain resolvable via redirect.

        The choice of survivor is determined by the caller (typically the
        domain's merge policy). This operation must be idempotent: merging
        already-merged entities is a no-op.

        Parameters
        ----------
        entity_ids:
            The full set of IDs to unify, including the survivor.
        survivor_id:
            The ID that will remain canonical after the merge. Must be a
            member of entity_ids.

        Returns
        -------
        str
            The survivor ID.
        """

    @abstractmethod
    async def on_entity_added(self, entity_id: str, context: dict) -> None:
        """
        Event hook called whenever an entity is added or updated.

        Implementations use this to trigger synonym detection and, if
        candidates are found, to call find_synonyms and (if the domain
        policy approves) merge. This event-driven model subsumes batch
        synonym sweeps: a batch sweep is equivalent to replaying
        on_entity_added for every entity in the store.
        """
```

---

### Domain-Defined Pluggable Behavior

The identity server ABC deliberately leaves the following decisions to the
domain:

| Concern | Where it lives | Notes |
|---|---|---|
| Authority lookup | Domain implementation | e.g. UMLS API, DBPedia SPARQL, no-op |
| Synonym criteria | Domain implementation | e.g. cosine similarity threshold, shared CUI |
| Merge survivor selection | Domain schema `preferred_entity` method | See below |
| Promotion thresholds | Domain promotion policy | Reuses existing `PromotionPolicy` ABC |

#### Survivor selection via domain schema

The domain schema (a pydantic model) should declare an abstract method for
survivor selection:

```python
@abstractmethod
def preferred_entity(self, candidates: list[Entity]) -> Entity:
    """
    Given a list of synonym candidates, return the preferred survivor.

    Domain implementations encode their own preference rules, e.g.:
    - prefer canonical over provisional
    - prefer the entity with the most mentions
    - prefer the entity with an external CUI / authoritative ID
    """
```

`on_entity_added` calls `preferred_entity` to determine `survivor_id` before
calling `merge`. This keeps survivor policy out of the identity server ABC and
fully domain-controlled.

---

### Recommended Implementation: Postgres-Backed

The reference implementation should use Postgres as the backing store. Postgres
is preferred because:

- It is already in the stack.
- Row-level locking (`SELECT FOR UPDATE`) and advisory locks provide
  cross-replica atomicity without an additional service.
- Transactions give free idempotency for insert/update operations via
  `INSERT ... ON CONFLICT DO NOTHING` and `UPDATE ... WHERE status != 'merged'`.

#### Locking strategy

- **`resolve`**: use `INSERT ... ON CONFLICT DO NOTHING` on the entity table's
  unique mention/domain key. No explicit lock needed; Postgres serializes
  conflicting inserts.
- **`promote`**: use `SELECT FOR UPDATE` on the provisional entity row, then
  check-and-update within the same transaction.
- **`merge`**: acquire a Postgres advisory lock keyed on the sorted pair of
  entity IDs before beginning the merge transaction. This prevents two workers
  from merging the same pair in opposite orders.
- **`on_entity_added`**: must be called inside the same transaction as the
  entity insert, so synonym detection is triggered only after the row is
  durably committed and visible. This prevents the race where two workers both
  see each other as merge candidates before either is fully written. Synonym
  detection itself is read-only; `merge` acquires its own lock.

#### Authority lookup caching in `resolve`

Authority lookup (e.g. UMLS API, DBPedia SPARQL) is an external network call
and therefore not idempotent in the face of transient failures. Caching the
result mitigates this:

1. Check cache keyed on normalized mention string → hit: use cached ID, skip
   API call entirely.
2. Miss: call the authority API, store result in cache, then do the DB insert.

**Cache backend**: Redis (already proposed for Issues 1 and 2) is preferred
over an in-process dict so the cache is shared across replicas.

**Negative caching**: a "no canonical match" result should also be cached,
with a shorter TTL, so a mention that later gets added to the authority source
doesn't stay provisional forever.

**Cache key versioning**: prefix keys with the authority source version, e.g.
`resolve:umls:v2026.01:{mention}`, so a UMLS release can be handled by
flushing or re-keying without invalidating unrelated entries.

**Residual risk**: if the API call succeeds but the process crashes before the
DB insert commits, a retry will hit the cache and get the canonical ID, then
re-attempt the insert. `ON CONFLICT DO NOTHING` handles this correctly.

#### Schema notes (deferred to implementer)

The distinction between canonical and provisional entities may be represented
as a status column on a single `entities` table (preferred: simpler joins,
single index) or as two separate tables. That decision is left to the
implementer, but the single-table approach is recommended.

Merged entities should be retained with `status = 'merged'` and a
`merged_into` foreign key, so that stale external references can be resolved
via a single lookup.

#### Synonym detection via pgvector

`find_synonyms` uses vector embeddings and cosine similarity, which is exactly
what the `pgvector` extension (already in the stack) is optimized for.
Approximate nearest-neighbor search at scale is its core capability, and
keeping similarity queries inside Postgres means they share the same
transaction boundary as entity operations with no additional service.

`on_entity_added` embeds the new entity and queries pgvector for neighbors
above a domain-defined similarity threshold. The result list is passed to
`preferred_entity` and then to `merge`.

#### Merge × promotion status rules

The status of the survivor after a merge is determined as follows:

- **provisional + provisional → provisional**: the merged entity is
  promotable via the normal promotion policy.
- **canonical + anything → canonical**: the survivor retains canonical
  status regardless of the absorbed entity's status.

`promote` behavior by status:

- **provisional**: check promotion policy, upgrade if warranted.
- **canonical**: no-op; returns the existing canonical ID (promotion is a
  one-time transition).
- **merged**: the entity has been absorbed into another. Redirect to the
  survivor and emit a log statement for tracking; do not raise an error, as
  the caller likely holds a stale ID.

#### Idempotency contract

Every mutating operation must be safe to call more than once with the same
arguments, as workers may retry after transient failures. The Postgres
implementation satisfies this via:

- `ON CONFLICT DO NOTHING` for creation.
- Conditional updates (`WHERE status = 'provisional'`) for promotion.
- Advisory lock + existence check before merge transactions.

---

### Relationship to Existing Concurrency Issues

The identity server subsumes the root causes of Issues 1 and 2 in this
document. Once canonical ID assignment and provisional entity tracking move
into Postgres under this interface, the `vocab.json` file and its associated
race (Issue 1) can be eliminated. Issue 2 (same-pmcid collision) becomes a
special case of `resolve` idempotency. Issue 3 (partial bundle write) remains
a file-layer concern and is addressed independently by the atomic
write-then-rename fix.

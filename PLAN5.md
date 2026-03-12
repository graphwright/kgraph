# PLAN5: REST Subgraph API

**Status:** Implemented. Run `./lint.sh` to verify.

**Goal:** Add `GET /api/v1/subgraph` returning `{entities, relationships, query}` with entity selection (ID, name glob) and filters (hops, min_confidence, predicates).

---

## Design Decisions (Locked)

- Use storage Entity/Relationship shapes as-is (JSON-serializable).
- Glob only (no regex). For `cushing*`, use `name_contains="cushing"` (substring match).
- New router at `/api/v1/subgraph`. Keep all existing endpoints.
- Keep GraphQL. No removal.
- One merged subgraph from multiple seeds.
- `query.truncated: true` when `max_nodes` cap hit.
- Synonym match deferred. No storage changes.

---

## Step 1: Add multi-seed BFS to graph_traversal.py

**File:** `kgserver/query/graph_traversal.py`

**1.1** Add `Sequence` to the typing import (line 8):
```python
from typing import Any, Optional, Sequence
```

**1.2** Add new function `_extract_subgraph_multi_seed` immediately after `extract_subgraph` (before `extract_full_graph`). Copy the BFS loop from `extract_subgraph` (lines 156–203) and adapt:

- **Signature:**
  ```python
  def _extract_subgraph_multi_seed(
      storage: StorageInterface,
      seed_ids: list[str],
      hops: int = 2,
      max_nodes: int = DEFAULT_MAX_NODES,
      min_confidence: Optional[float] = None,
      predicate_set: Optional[frozenset[str]] = None,
  ) -> tuple[list, list, bool]:
  ```
  Returns `(entities, relationships, truncated)` — raw storage models, not GraphNode/GraphEdge.

- **Logic:**
  - `hops = min(hops, MAX_HOPS)`, `max_nodes = min(max_nodes, MAX_NODES_LIMIT)`.
  - Initialize `visited_ids` and `frontier` from seed_ids: for each `eid`, call `storage.get_entity(eid)`; if found, add to both. If no seeds resolve, return `([], [], False)`.
  - BFS loop: same structure as `extract_subgraph`. For each `entity_id` in `frontier`, build `all_rels` from `list(storage.find_relationships(subject_id=entity_id, limit=1000)) + list(storage.find_relationships(object_id=entity_id, limit=1000))`. For each `rel` in `all_rels`:
    - Skip if `min_confidence is not None` and `(rel.confidence or 0) < min_confidence`.
    - Skip if `predicate_set is not None` and `rel.predicate.upper() not in predicate_set`.
    - Otherwise add edge and expand frontier as in `extract_subgraph`.
  - After loop: fetch entities for `visited_ids` via `storage.get_entity`, filter relationships to those with both endpoints in `visited_ids`.
  - Return `(entities, relationships, truncated)`.

**Verification:** `cd kgserver && uv run pytest tests/test_graph_api.py -v -q` (existing tests must still pass).

---

## Step 2: Create subgraph.py

**File:** `kgserver/query/subgraph.py` (new)

**2.1** Implement `_glob_to_name_contains(pattern: str) -> str`: return `pattern.replace("*", "").strip()`. Used to convert glob to substring for `name_contains`. Add a docstring/comment: *"Deliberate simplification: `*` is ignored; the whole pattern minus `*` becomes the substring. Multi-wildcard patterns (e.g. `cushing*disease` → `cushingdisease`) are mangled. Low risk for typical usage patterns."*

**2.2** Implement `resolve_seeds(storage, entity_param, name_param, limit=100) -> list[str]`:
- If `entity_param`: split by comma, strip each token. For each token:
  - If `"*" in token`: call `_glob_to_name_contains(token)`; if non-empty, `storage.get_entities(name_contains=part, limit=limit)` and extend seeds with `e.entity_id`.
  - Else: `storage.get_entity(token)`; if found, append `entity_id`.
- If `name_param`: same as entity glob — `part = _glob_to_name_contains(name_param)`; if non-empty, `get_entities(name_contains=part, limit=limit)` and extend seeds.
- Deduplicate while preserving order. Return list of entity_ids.

**2.3** Implement `extract_subgraph_rest(storage, seed_ids, hops=2, max_nodes=DEFAULT_MAX_NODES, min_confidence=None, predicates=None) -> tuple[list[Entity], list[Relationship], bool]`:
- Build `predicate_set = frozenset(p.upper() for p in predicates)` if predicates else None.
- Call `_extract_subgraph_multi_seed(storage, seed_ids, hops, max_nodes, min_confidence, predicate_set)`.
- Return its result.

**Verification:** `cd kgserver && uv run pytest tests/ -v -q` (no new tests yet; must not break existing).

---

## Step 3: Create subgraph_api.py router

**File:** `kgserver/query/routers/subgraph_api.py` (new)

**3.1** Define Pydantic models. Entity and Relationship are SQLModel (Pydantic BaseModel) — FastAPI serializes them automatically. No conversion needed.
```python
class SubgraphQueryEcho(BaseModel):
    seeds: list[str]
    hops: int
    filters: dict = Field(default_factory=dict)
    truncated: bool = False

class SubgraphResponse(BaseModel):
    entities: list[Entity]
    relationships: list[Relationship]
    query: SubgraphQueryEcho
```

**3.2** Create router: `router = APIRouter(prefix="/api/v1/subgraph", tags=["Subgraph"])`

**3.3** Add `GET ""` endpoint (empty path so full path is `/api/v1/subgraph`):
- **Query params:** `entity: Optional[str]`, `name: Optional[str]`, `hops: int = 2` (ge=1, le=MAX_HOPS), `min_confidence: Optional[float]` (ge=0, le=1), `predicates: Optional[str]`, `max_nodes: int = DEFAULT_MAX_NODES` (ge=1, le=MAX_NODES_LIMIT).
- **Validation:** If both `entity` and `name` are None/empty, raise `HTTPException(400, "At least one of entity or name is required")`.
- **Logic:**
  - `seed_ids = resolve_seeds(storage, entity_param=entity, name_param=name)`.
  - If `seed_ids` empty: return `SubgraphResponse(entities=[], relationships=[], query=SubgraphQueryEcho(seeds=[], hops=hops, filters={...}, truncated=False))`. Build filters dict from min_confidence and predicates (split by comma, strip).
  - Else: `predicate_list = [p.strip() for p in predicates.split(",")] if predicates else None`.
  - Call `extract_subgraph_rest(storage, seed_ids, hops, max_nodes, min_confidence, predicate_list)`.
  - Build `filters` dict: include `min_confidence` if not None, include `predicates` list if provided.
  - Return `SubgraphResponse(entities=..., relationships=..., query=SubgraphQueryEcho(seeds=seed_ids, hops=hops, filters=filters, truncated=truncated))`.

**3.4** Imports: `storage.interfaces.StorageInterface`, `storage.models.Entity`, `storage.models.Relationship`, `..storage_factory.get_storage`, `..subgraph.resolve_seeds`, `..subgraph.extract_subgraph_rest`, `..graph_traversal.MAX_HOPS`, `MAX_NODES_LIMIT`, `DEFAULT_MAX_NODES`.

**Verification:** `cd kgserver && uv run pytest tests/ -v -q`.

---

## Step 4: Mount router in server.py

**File:** `kgserver/query/server.py`

**4.1** Add import: `from .routers import subgraph_api`

**4.2** After `app.include_router(graph_api.router)`, add:
```python
app.include_router(subgraph_api.router)
```

**Verification:** `cd kgserver && uv run pytest tests/ -v -q`.

---

## Step 5: Add tests

**File:** `kgserver/tests/test_graph_api.py`

**5.1** Update `app` fixture to include subgraph router. (The fixture is shared with `TestGraphAPI`; adding the subgraph router affects all tests using it — fine, subgraph is additive.)
```python
from query.routers import subgraph_api
_app.include_router(subgraph_api.router)
```

**5.2** Add new test class `TestSubgraphAPI` with `client` fixture (same pattern as `TestGraphAPI` — `file_storage`, `client` with `get_storage` override).

**5.3** Add tests:
- `test_subgraph_requires_entity_or_name`: GET `/api/v1/subgraph` with no params → 400.
- `test_subgraph_by_entity_id`: `entity=test:entity:1&hops=1` → 200, `entities` non-empty, `query.seeds == ["test:entity:1"]`.
- `test_subgraph_by_name_glob`: `name=Test&hops=1` → 200, seeds resolved from name match.
- `test_subgraph_empty_seeds`: `entity=nonexistent123&hops=1` → 200, `entities=[]`, `relationships=[]`, `query.seeds=[]`.
- `test_subgraph_query_echo`: Response includes `query` with `seeds`, `hops`, `filters`, `truncated`.

**Verification:** `cd kgserver && uv run pytest tests/test_graph_api.py -v`.

---

## Step 6: Run lint.sh

**Command:** From repo root, `./lint.sh`

Fix any failures before considering the work complete.

---

## API Reference (for implementer)

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| entity | str | None | Comma-separated. **Bare token** (e.g. `C0221406`) → `get_entity` (ID lookup). **Token with `*`** (e.g. `cushing*`) → `name_contains` with stripped `*`. Note: `C0221406*` would strip `*` and search name_contains for `C0221406` — unexpected but documented. |
| name | str | None | Glob on name. Same as entity glob. |
| hops | int | 2 | 1–5. |
| min_confidence | float | None | Filter relationships. |
| predicates | str | None | Comma-separated, e.g. `TREATS,CAUSES`. |
| max_nodes | int | 500 | Cap. |

**Response:** `{entities: [...], relationships: [...], query: {seeds, hops, filters, truncated}}`

---

## Example Requests

```
GET /api/v1/subgraph?entity=C0221406&hops=2&min_confidence=0.8&predicates=TREATS,CAUSES
GET /api/v1/subgraph?name=cushing*&hops=1
GET /api/v1/subgraph?entity=C0221406,C0001623&hops=2
```

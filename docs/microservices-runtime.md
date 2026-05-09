# Microservices: Runtime Architecture and Interactions

> This document is derived from the source code and deployment configuration.
> Where the existing Markdown docs disagree with the code, the code wins.

---

## 1. Deployed Services

### 1.1 Edge and Ingress

| Service | Image / Source | Role |
|---------|---------------|------|
| `nginx-proxy` | `nginxproxy/nginx-proxy` | TLS termination + reverse proxy |
| `acme-companion` | `nginxproxy/acme-companion` | Let's Encrypt cert issuance / renewal |

Path routing is driven by `deploy/vhost.d/graphwright.io`:

| Incoming path | Upstream service:port |
|---------------|-----------------------|
| `/sse`, `/mcp/`, `/messages/` | `mcpserver:8001` |
| `/chat` | `gwchat:3000` |
| `/api/`, `/graphql`, `/graphiql` | `api:8000` |
| `/graph-viz/`, `/docs`, `/redoc`, `/openapi.json`, `/health` | `api:8000` |
| `/` and `/site/` | `api:8000` (static MkDocs site) |

### 1.2 Application Services

#### `api` — Query Server (`kgserver/query/server.py`)

FastAPI application. Entrypoint: `main:app` (port 8000).

- Loads a pre-built bundle at startup when `BUNDLE_PATH` is set
  (`kgserver/query/bundle_loader.py`).
- Exposes:
  - **REST** — `GET /api/v1/entities`, `GET /api/v1/relationships`
  - **GraphQL** — `POST /graphql`; custom GraphiQL at `/graphiql/`
  - **Graph visualisation** — `/graph-viz/` (static JS + graph API)
  - **Subgraph REST** — `/api/v1/subgraph` (LLM-friendly N-hop result)
  - **OpenAPI docs** — `/docs`, `/redoc`
  - **Health** — `GET /health`
- Storage backend is selected by `DATABASE_URL`:
  - `postgresql://…` → `PostgresStorage`
  - `sqlite:///…` (default: `./test.db`) → `SQLiteStorage`
- Optionally mounts a Chainlit chat UI at `/chat/` if `kgserver/chainlit/app.py`
  is present (legacy; primary chat UI is now `gwchat`).

#### `mcpserver` — MCP Ingest + Query Server (`kgserver/mcp_main.py`)

FastAPI application wrapping FastMCP. Entrypoint: `mcp_main:app` (port 8001).

- SSE endpoint: `/sse`
- On startup, creates all SQLModel tables and starts one or more background
  ingest worker tasks (`INGEST_MAX_WORKERS`, default 1).
- Exposes **BFS-QL tools** (from `bfsql`, backed by `PostgresBackend`):
  - `describe_schema` — return graph schema
  - `search_entities` — semantic search over entity names
  - `bfs_query` — BFS graph traversal
  - `intersect_subgraphs` — subgraph intersection
  - `describe_entity` — full entity record
- Exposes **kgserver-specific tools** (`kgserver/mcp_server/server.py`):
  - `ingest_paper(url)` — queue a paper ingestion job, return `job_id`
  - `check_ingest_status(job_id)` — poll job progress / result
  - `get_paper_source(paper_id)` — read raw JATS XML from bundle `sources/`
  - `get_mentions(paper_id?)` — read `mentions.jsonl` from bundle
  - `get_bundle_info()` — bundle metadata (id, domain, created_at)
  - `graphql_query(query, variables?)` — run arbitrary GraphQL against the
    graph schema (same schema as `api`'s `/graphql`)

#### `gwchat` — Next.js Chat Frontend (`gwchat/`)

Next.js 14 app (port 3000). Served at `/chat`.

- `POST /api/chat` drives a two-phase LLM loop:
  1. **Phase A — Orchestrator**: `ORCHESTRATOR_MODEL` (default `claude-haiku-4-5`)
     calls MCP tools up to `ORCHESTRATOR_MAX_ITERATIONS` (8) times to gather
     graph data.
  2. **Phase B — Synthesis**: `SYNTHESIS_MODEL` (default `claude-sonnet-4-6`)
     writes the final answer from the tool outputs + truncated conversation history.
- Connects to `mcpserver` via SSE transport at `MCP_SSE_URL`
  (default `http://localhost:8001/sse`) using `@modelcontextprotocol/sdk`.
- Supports Anthropic, OpenAI, and Ollama providers (selected by `LLM_PROVIDER`).
- Multi-key load balancing: reads `ANTHROPIC_API_KEY`, `ANTHROPIC_API_KEY_1`,
  `ANTHROPIC_API_KEY_2`, … (or `OPENAI_API_KEY_*`) and picks a random key per
  request.

#### `identity-server` — Entity Identity Service (`identity-server/`)

FastAPI application (port configurable). Source: `identity_server/app.py`.

A **domain-agnostic** HTTP microservice for the entity lifecycle:

| Endpoint | Purpose |
|----------|---------|
| `POST /resolve` | Resolve mention → canonical or provisional entity ID |
| `POST /promote` | Attempt provisional → canonical promotion |
| `POST /find-synonyms` | Return IDs of embedding-similar entities (read-only) |
| `POST /merge` | Merge a set of entities into one survivor |
| `POST /on-entity-added` | Event hook: trigger synonym detection + auto-merge |
| `GET /health` | Health check |

Calls the **domain service** (via `DomainClient`, pointed at `DOMAIN_SERVICE_URL`)
for all domain-specific decisions. Degrades gracefully if the domain service is
unreachable (entity stays provisional, highest-usage survivor wins merge, threshold
defaults to 0.90).

Uses:
- **Postgres** (`DATABASE_URL`) for durable entity storage.
- **Redis** (`REDIS_URL`, optional) to cache authority lookup results.

#### `medlit-domain` — Domain Service (`medlit/domain_service/app.py`)

FastAPI application. Implements medlit-specific policy for the identity server.

| Endpoint | Purpose |
|----------|---------|
| `POST /resolve-authority` | Look up canonical ID from UMLS / HGNC / RxNorm / UniProt / ROR / ORCID |
| `POST /select-survivor` | Choose merge survivor (canonical > authoritative ID > usage\_count > lex) |
| `GET /synonym-criteria` | Return per-entity-type embedding similarity thresholds |
| `POST /synonym-criteria` | Same (backward-compat POST form) |
| `POST /compute-confidence` | Aggregate confidence over provenance records (study type × section × method weights) |
| `GET /schema` | Return immutable entity type + predicate contract |
| `GET /authorities` | Authority metadata for diagnostics |
| `GET /health` | Health check |

### 1.3 Data and Support Services

| Service | Role |
|---------|------|
| `postgres` (`pgvector/pgvector`) | Primary persistence for bundle data, ingest jobs, and optionally identity |
| `redis` | Authority-lookup cache (TTL-based; positive 24 h, negative 1 h) |
| `bundle-init` | One-shot container that downloads the initial bundle into a shared volume at first deploy |
| `ollama` (optional profile) | Self-hosted LLM backend; used when `LLM_PROVIDER=ollama` |

---

## 2. Extraction (Ingestion) Interactions

### 2.1 On-demand ingestion via MCP tool

```
gwchat (orchestrator)
  │
  │  MCP call: ingest_paper(url)           (SSE transport)
  ▼
mcpserver
  │ create IngestJob row in postgres
  │ enqueue job_id in in-process asyncio.Queue
  │ return { job_id, status:"queued" }
  │
  ▼ (background worker task)
ingest_worker._run_ingest_job(job_id)
  │
  ├─ Fetch paper content
  │     PMC URL → NCBI efetch API (xml)
  │     other URL → direct HTTP fetch
  │
  ├─ pipeline.fetch_vocab(input_dir, vocab_dir, llm_backend)
  │     (Pass 0) LLM reads paper, merges entity vocabulary into vocab.json
  │
  ├─ pipeline.extract(input_dir, bundles_dir, llm_backend, vocab_file)
  │     (Pass 1+2) LLM receives extraction prompt + vocab context,
  │     returns entities + relationships as structured JSON per paper
  │     → written to bundles_dir/paper_<PMCID>.json
  │
  ├─ pipeline.run_ingest(bundles_dir, merged_dir, ...)  ← under file lock
  │     (Pass 2 post-processing)
  │     Name/type index, synonym cache, SAME_AS resolution,
  │     optional authority lookup, embedding-based dedup of provisional entities
  │     → merged_dir/entities.json, relationships.json, id_map.json
  │
  ├─ pipeline.build_bundle(merged_dir, bundles_dir, output_dir)  ← under file lock
  │     Assembles kgbundle: manifest.json + entities.jsonl +
  │     relationships.jsonl + mentions.jsonl + sources/
  │
  └─ storage.load_bundle_incremental(manifest, output_dir)  ← under file lock
        Upserts entities and relationships into postgres
```

The file lock (`ingest_workspace/.ingest.lock`) serialises the
`run_ingest → build_bundle → load_bundle_incremental` critical section; the
`fetch_vocab` and `extract` steps run outside the lock.

The pipeline implementation loaded by the worker is determined by `INGEST_PIPELINE_CLASS`
(e.g. `medlit.pipeline.MedlitPipeline`). If the variable is unset the worker raises a
`RuntimeError` at the point of use.

### 2.2 Alternative path: ingest with identity-server

`medlit.pipeline.dedup.run_ingest_with_identity_server` provides a path where the
hand-built dedup logic is replaced by calls to the identity server's HTTP API.
This is not the default path in the MCP worker; it must be explicitly selected
(e.g. via the `--use-identity-server` flag on the CLI `ingest.py` script).

When active, for each extracted entity mention the pipeline calls:

```
ingest script / pipeline
  │
  │  POST /resolve  { mention, entity_type, document_id }
  ▼
identity-server
  │ normalise mention (DomainSchema.normalize_mention)
  │ check existing entity by (name, entity_type)
  │ check authority cache (Redis)
  │
  │  POST /resolve-authority  { mention, entity_type, document_id }
  ▼
medlit-domain
  │ query UMLS / HGNC / RxNorm / UniProt / … (with disk cache)
  └─ return canonical_id or null
  │
identity-server (continued)
  │ INSERT entity (canonical if authority matched, else provisional prov:uuid)
  │ store embedding
  └─ return entity_id
  │
  │  POST /on-entity-added  { entity_id, entity_type, document_id }
  ▼
identity-server
  │ find_synonyms: cosine similarity scan of embedding column
  │ if synonyms found:
  │   POST /select-survivor → medlit-domain selects survivor by policy
  │   merge absorbed entities into survivor in postgres
  └─ return (no content)
```

---

## 3. Query Interactions

### 3.1 Direct HTTP querying

```
external client
  │
  │  HTTPS → nginx-proxy
  ▼
api (port 8000)
  │
  ├─ GET  /api/v1/entities?...           → RestAPI router → PostgresStorage
  ├─ GET  /api/v1/relationships?...
  ├─ POST /graphql  { query, variables } → Strawberry GraphQL → storage
  ├─ GET  /graphiql/                     → custom GraphiQL UI
  ├─ GET  /api/v1/subgraph?...           → graph traversal → storage
  └─ GET  /graph-viz/                    → static JS + graph API
```

Storage queries read from the postgres tables loaded at startup from the bundle.

### 3.2 LLM-assisted querying via gwchat

```
Browser
  │  HTTPS /chat → nginx-proxy → gwchat:3000
  │
  │  POST /api/chat  { messages }
  ▼
gwchat  (Next.js API route)
  │
  │ 1. connectMcp()  →  SSE to mcpserver:8001/sse
  │    listTools()   ←  { describe_schema, search_entities, bfs_query,
  │                       intersect_subgraphs, describe_entity,
  │                       ingest_paper, check_ingest_status, … }
  │
  │ 2. Phase A — Orchestrator LLM (claude-haiku-4-5 / gpt-4o-mini)
  │    generateText() with tools, up to 8 steps
  │    for each tool call:
  │      callMcpTool(name, args)
  │          │
  │          ▼
  │        mcpserver executes BFS-QL/GraphQL/storage query
  │        returns structured JSON result
  │
  │ 3. Phase B — Synthesis LLM (claude-sonnet-4-6 / gpt-4o)
  │    generateText(system, history + tool results)
  │    → final answer text
  │
  └─ SSE stream final answer back to browser
```

### 3.3 Direct MCP querying (Cursor / Claude Code / other MCP clients)

MCP clients connect to `https://graphwright.io/sse` (or `http://mcpserver:8001/sse`
locally). The same BFS-QL + kgserver-specific tool set is available:

```
MCP client (Cursor, Claude Code, …)
  │
  │  SSE  →  nginx-proxy  →  mcpserver:8001/sse
  │
  │  tool: bfs_query / search_entities / describe_entity
  ▼
mcpserver → PostgresBackend (bfsql) → postgres
  └─ return subgraph JSON

  │  tool: graphql_query
  ▼
mcpserver → strawberry.Schema(Query).execute_sync → postgres
  └─ return { data, errors }

  │  tool: ingest_paper
  ▼
mcpserver → enqueue → ingest_worker → LLM APIs + postgres
  └─ return { job_id }
```

---

## 4. Key Environment Variables

| Variable | Service(s) | Purpose |
|----------|-----------|---------|
| `DATABASE_URL` | `api`, `mcpserver`, `identity-server` | Postgres or SQLite connection string |
| `BUNDLE_PATH` | `api`, `mcpserver` | Path to pre-built bundle dir or ZIP |
| `INGEST_PIPELINE_CLASS` | `mcpserver` | Dotted import path of `IngestPipeline` subclass |
| `PASS1_LLM_BACKEND` | `mcpserver` ingest worker | `anthropic` / `openai` / `ollama` |
| `REDIS_URL` | `mcpserver`, `identity-server` | Redis for authority-lookup cache (optional) |
| `DOMAIN_SERVICE_URL` | `identity-server` | URL of domain service (default `http://domain-stub:8080`) |
| `MCP_SSE_URL` | `gwchat` | URL of MCP SSE endpoint (default `http://localhost:8001/sse`) |
| `LLM_PROVIDER` | `gwchat` | `anthropic` / `openai` / `ollama` |
| `ORCHESTRATOR_MODEL` | `gwchat` | Model for tool-calling phase |
| `SYNTHESIS_MODEL` | `gwchat` | Model for final answer phase |
| `ANTHROPIC_API_KEY[_N]` / `OPENAI_API_KEY[_N]` | `gwchat` | LLM API keys (load-balanced across numbered variants) |
| `INGEST_MAX_WORKERS` | `mcpserver` | Number of background ingest worker tasks (default 1) |
| `INGEST_TIMEOUT` | `mcpserver` | Per-job timeout in seconds (default 600) |
| `INGEST_WORKSPACE_ROOT` | `mcpserver` | Persistent workspace for in-progress bundles |

---

## 5. Service Dependency Summary

```
nginx-proxy
├── api             ← postgres, (bundle volume)
├── mcpserver       ← postgres, redis, (bundle volume), LLM APIs
│     └── ingest pipeline (medlit) ← LLM APIs, NCBI efetch
└── gwchat          ← mcpserver (MCP/SSE), LLM APIs

identity-server     ← postgres, redis, medlit-domain
medlit-domain       ← external authority APIs (UMLS, HGNC, RxNorm, UniProt, ROR, ORCID)

bundle-init         → (bundle volume) → api, mcpserver
```

`identity-server` and `medlit-domain` are fully implemented and deployed, but are
not wired into the default MCP ingest worker path. They are invoked when the
pipeline's `--use-identity-server` mode is selected, or when `PostgresIdentityServer`
is instantiated directly.

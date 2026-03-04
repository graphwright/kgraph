# Deployment and Operations

## kgserver

The **kgserver** is a FastAPI application that loads a knowledge graph bundle (read-only) and exposes:

- **Health** — `GET /health`
- **REST** — `GET /api/v1/entities`, `GET /api/v1/relationships` (with limit, filters)
- **GraphQL** — `POST /graphql`; GraphiQL UI at `/graphiql/`
- **API docs** — OpenAPI at `/docs`
- **MCP** — Model Context Protocol server for LLM/agent tooling (entity search, relationships, traversal)
- **Chat** — Optional Chainlit UI at `/chat/` (medical literature chat with MCP tools)
- **Graph visualization** — At `/graph-viz/` (when enabled)

The server does **not** ingest raw documents; it only loads a pre-built bundle. Build the bundle with your domain pipeline (e.g. medlit pass1 → pass2 → pass3), then point the server at the bundle path.

## Running the server

- **Minimal (SQLite, single bundle)**  
  `BUNDLE_PATH=/path/to/bundle.zip uv run uvicorn main:app --host 0.0.0.0 --port 8000`  
  (Run from the kgserver directory or set PYTHONPATH so kgserver and kgbundle are importable.)

- **PostgreSQL**  
  Set `DATABASE_URL=postgresql://...`. Use the same bundle env; the server loads the bundle into the configured backend.

- **Docker**  
  Build the image (see below); mount the bundle and set `BUNDLE_PATH` and `DATABASE_URL` in the container. Use docker-compose for postgres + api if needed.

## Docker build

The Dockerfile (multi-stage) installs dependencies, copies the docs tree and `kgserver/index.md` into the image, builds the MkDocs site, and runs the FastAPI app. Build from repo root:

```bash
docker build -f kgserver/Dockerfile .
```

Ensure the bundle is available at the path given by `BUNDLE_PATH` inside the container (e.g. volume mount or COPY).

## MCP integration

The server can run an MCP server so that LLMs and agents can call tools (e.g. entity search, relationship lookup, find entities within N hops). Configure the MCP endpoint and any auth as required by your deployment. The Chainlit chat at `/chat/` uses MCP to give the assistant access to the graph.

## Chainlit chat — LLM configuration

The chat uses a two-tier model architecture (orchestrator for tool planning, synthesis for final answers) and supports:

- **Multi-key load balancing**: Set `ANTHROPIC_API_KEY`, `ANTHROPIC_API_KEY_1`, `ANTHROPIC_API_KEY_2`, … (or `OPENAI_API_KEY`, `OPENAI_API_KEY_1`, …) to spread requests across keys.
- **Model selection**: `ORCHESTRATOR_MODEL` (default: claude-haiku-4-5 / gpt-4o-mini), `SYNTHESIS_MODEL` (default: claude-sonnet-4-6 / gpt-4o).
- **Prompt caching**: Anthropic requests use `cache_control_injection_points` for system prompts when supported.
- **Throttling**: `LLM_MIN_REQUEST_INTERVAL_SECONDS`, `LLM_RATE_LIMIT_RETRY_DELAY_SECONDS` for rate-limit mitigation.

See the docstring in `kgserver/chainlit/app.py` for the full list of environment variables.

## Running at scale

- Use **PostgreSQL** for production; tune connection pool and timeouts.
- **Bundle size**: Large graphs (millions of entities/relationships) may require more memory and load time; consider sharding or multiple read replicas if needed.
- **MCP/LLM rate limits**: Throttle or queue requests if you hit provider limits; the medlit Chainlit app supports retry delays for rate limits.

## Local MkDocs

To serve the docs locally (without Docker), copy `kgserver/index.md` to `docs/index.md` so MkDocs has a home page, then run `mkdocs serve` from the directory that contains `mkdocs.yml` (e.g. after copying it from kgserver). See PLAN12 for the note on repo vs image `docs/index.md`.

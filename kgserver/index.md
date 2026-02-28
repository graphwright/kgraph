# KGserver

A **read-only server** for a loaded knowledge graph. It does not ingest raw documents; domain pipelines build a bundle (entities + relationships), and the server loads that bundle at startup.

**Quick links:**

- [Medical literature chat](/chat/)
- [OpenAPI spec](/docs/)
- [Graph visualization](/graph-viz/) — currently focused on medical literature
- [GraphQL GUI](/graphiql/)
- **Jupyter notebook:** Use an SSH tunnel, then open the lab in your browser:

  ```bash
  ssh -L 8888:127.0.0.1:8888 root@SERVER_IP
  ```

  Then go to [http://localhost:8888/jupyter/lab](http://localhost:8888/jupyter/lab).

## What it exposes

| Resource | Path |
|----------|------|
| Health | `GET /health` |
| REST entities | `GET /api/v1/entities` |
| REST relationships | `GET /api/v1/relationships` |
| GraphQL | `POST /graphql` |
| GraphiQL (playground) | `GET /graphiql/` |
| OpenAPI docs | `GET /docs` |
| Chat (Chainlit, when enabled) | `GET /chat/` |
| Graph visualization | `GET /graph-viz/` |

## How to connect

Use the server base URL (e.g. `http://localhost:8000`). Auth is not required unless you configure it. GraphQL and REST use the same origin.

## How to run

Minimal (SQLite, single bundle):

```bash
BUNDLE_PATH=/path/to/bundle.zip uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

Run from the kgserver directory (or set `PYTHONPATH` so `kgserver` and `kgbundle` are importable). For PostgreSQL, Docker, and MCP setup, see **[Deployment and Operations](deployment-and-operations.md)** in the docs.

## Where to read more

- **Bundle format, pipeline, and operations** — Use the docs nav (Overview, Architecture, Pipeline, Storage and Export, Deployment and Operations).
- **Building a bundle** — See the medlit and Sherlock examples and [Adapting to Your Domain](adapting-to-your-domain.md).

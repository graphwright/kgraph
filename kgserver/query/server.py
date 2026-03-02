import logging
import os
import subprocess
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import strawberry
from strawberry.fastapi import GraphQLRouter

from .storage_factory import close_storage, get_engine, get_storage
from .bundle_loader import load_bundle_at_startup
from .routers import rest_api
from .routers import graphiql_custom
from .routers import graph_api
from .graphql_schema import Query
from storage.interfaces import StorageInterface

# Let's take this opportunity to do the zensical build
logging.basicConfig(format="%(levelname)s:     %(asctime)s - %(message)s", level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger()
result = subprocess.run(["uv", "run", "zensical", "build"], check=False)
if result.returncode != 0:
    logger.error("MKDOCS BUILD FAILED")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Initializes storage on startup, loads bundle if configured, and closes on shutdown.
    """
    engine, db_url = get_engine()  # Initialize storage
    load_bundle_at_startup(engine, db_url)  # Load bundle if BUNDLE_PATH is set
    yield
    close_storage()  # Close storage connections


app = FastAPI(
    title="Medical Literature Knowledge Graph API",
    description="A read-only API for querying the medical literature knowledge graph.",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount REST API
app.include_router(rest_api.router)

# Mount Graph Visualization API
app.include_router(graph_api.router)


# Create a context getter that uses your dependency
async def get_context(
    storage: StorageInterface = Depends(get_storage),
):
    return {
        "storage": storage,
    }


# Mount GraphQL with context (no built-in GraphiQL)
graphql_schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(
    graphql_schema,
    graphiql=False,  # Disable built-in GraphiQL
    context_getter=get_context,
)

app.include_router(graphql_app, prefix="/graphql")

# Mount custom GraphiQL interface with example queries
app.include_router(graphiql_custom.router, prefix="/graphiql", tags=["GraphQL"])


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify that the server is running.
    """
    return {"status": "ok"}


# Mount Graph Visualization static files
_graph_viz_static = Path(__file__).parent / "static"
if _graph_viz_static.exists():
    app.mount("/graph-viz", StaticFiles(directory=_graph_viz_static, html=True), name="graph-viz")

# Mount Chainlit chat UI at /chat (optional: only if chainlit app is present)
_chainlit_app = os.environ.get("CHAINLIT_APP_PATH") or next(
    (p for p in [Path(__file__).resolve().parent.parent / "chainlit" / "app.py"] if p.exists()),
    None,
)
if _chainlit_app is not None:
    try:
        from chainlit.utils import mount_chainlit  # pylint: disable=no-name-in-module

        mount_chainlit(app=app, target=str(_chainlit_app), path="/chat")
        logger.info("Chainlit mounted at /chat (app=%s)", _chainlit_app)
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.warning("Chainlit mount failed (app=%s): %s", _chainlit_app, e)
else:
    logger.info("Chainlit not mounted: no app at CHAINLIT_APP_PATH or kgserver/chainlit/app.py")

# Mount MkDocs static site at /site (not at /) so FastAPI's /docs and /openapi.json
# are never shadowed. On Docker the site is pre-built; locally the dir may be missing.
_mkdocs_site = Path(__file__).parent.parent / "site"
if _mkdocs_site.exists():
    # Zensical generates nav links with .md but the built output is .html. Rewrite .md -> .html.
    @app.middleware("http")
    async def _site_md_rewrite(request, call_next):
        path = request.scope.get("path", "")
        if path.startswith("/site/") and path.endswith(".md"):
            request.scope["path"] = path[:-3] + ".html"
        return await call_next(request)

    app.mount("/site", StaticFiles(directory=_mkdocs_site, html=True), name="mkdocs")

    @app.get("/", include_in_schema=False)
    async def _root_redirect():
        """Send root to the docs site so / still lands somewhere useful."""
        return RedirectResponse(url="/site/", status_code=302)

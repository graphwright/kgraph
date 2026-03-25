"""
MCP (Model Context Protocol) server for Knowledge Graph.

Uses bfsql (BFS-QL) as the core graph query engine, exposing four standard
tools (describe_schema, search_entities, bfs_query, describe_entity) plus
kgserver-specific tools for ingestion and bundle inspection.
"""

from .server import mcp_server
from . import ingest_worker

__all__ = ["mcp_server", "ingest_worker"]

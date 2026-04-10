# MCP Server

> **Placeholder** — content to be expanded from
> [`../deployment-and-operations.md`](../deployment-and-operations.md).

You want to expose a Model Context Protocol (MCP) endpoint that allows LLMs and
agents to query the knowledge graph as a tool. When working in Python, the
FastMCP library is good for this.

## What MCP provides

MCP gives an LLM structured access to the graph without requiring it to write raw
GraphQL or SQL. The server exposes a set of named tools that the LLM can call by
name with typed arguments.

## Available tools (draft)

- `search_entities(query, type?, limit?)` — semantic search over entity names and
  descriptions. Returns ranked entity records with canonical IDs.
- `get_entity(entity_id)` — retrieve a single entity by ID, including all attributes
  and provenance.
- `get_relationships(entity_id, predicate?, direction?)` — return edges connected to
  an entity, optionally filtered by predicate or direction.
- `traverse(start_id, max_hops?, predicate_filter?)` — walk the graph outward from
  a starting entity and return the subgraph.

## Configuration

MCP is enabled by default in kgserver. The endpoint is at `/mcp/sse` (Server-Sent
Events transport). Configure it in your Claude Desktop or agent client:

```json
{
  "mcpServers": {
    "kgraph": {
      "type": "sse",
      "url": "http://localhost:8000/mcp/sse"
    }
  }
}
```

## See also

- [Querying with LLMs](querying.md)
- [Deployment and Operations](../deployment-and-operations.md)
- [MCP Troubleshooting](mcp-troubleshooting.md)

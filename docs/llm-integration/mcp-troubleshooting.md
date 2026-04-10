# MCP Troubleshooting

> **Placeholder** — this page needs to be written.

Things that go wrong with MCP connections, and how to fix them.

## Connection issues

**The client says "server not found" or times out.**

- Confirm the server is running: `curl http://localhost:8000/health` should return `{"status": "ok"}`.
- Check the URL in your client config — the MCP endpoint is `/mcp/sse`, not `/mcp`.
- If running in Docker, ensure the port is exposed and the host is reachable from
  the client.

**The SSE connection drops after a few seconds.**

- Some reverse proxies (nginx, Caddy) close idle SSE connections. Configure
  `proxy_read_timeout` (nginx) or an equivalent keepalive setting.

## Tool call failures

**The LLM calls a tool but gets an error response.**

- Check the server logs — tool errors are logged at WARNING level with the full
  exception.
- Validate that the bundle loaded correctly on startup. A bundle with a corrupt
  index will cause all tool calls to fail.

**Search returns empty results.**

- Embeddings may not have been generated during ingestion. Confirm the embedder
  ran in your pipeline.
- Check that the embedding model used at query time matches the one used at
  ingestion time.

## Debugging tips

- The MCP inspector (if available) can show raw tool call/response pairs.
- Enable `DEBUG` logging in kgserver to see every tool invocation.
- The `/docs` OpenAPI endpoint documents all REST endpoints; cross-check tool
  behavior against the equivalent REST call.

## See also

- [MCP Server](mcp-server.md)
- [Deployment and Operations](../deployment-and-operations.md)

# gwchat — GraphWright TypeScript chat app

A Next.js chat interface for the kgraph knowledge graph server. Replaces the
Python/Chainlit chat UI with a TypeScript app that has proper session memory.

This is intended to become a separate GitHub repo, pulled into kgraph as a git
submodule.

## Architecture

- **Next.js 16** (App Router) with TypeScript and Tailwind CSS
- **Vercel AI SDK v6** (`ai`, `@ai-sdk/anthropic`, `@ai-sdk/openai`, `@ai-sdk/react`)
  for streaming LLM responses
- **`@modelcontextprotocol/sdk`** MCP client connecting to the kgraph mcpserver
  SSE endpoint
- Two-phase chat loop: orchestrator (tool-calling, lighter model) → synthesis
  (final answer, stronger model)
- Session memory: full conversation history passed to synthesis each turn

## Configuration

### Environment variables (operational)

Copy `.env.example` to `.env.local` and fill in values. Key vars:

| Variable             | Default                     | Description                                    |
| -------------------- | --------------------------- | ---------------------------------------------- |
| `MCP_SSE_URL`        | `http://localhost:8001/sse` | kgraph mcpserver SSE endpoint                  |
| `LLM_PROVIDER`       | `anthropic`                 | `anthropic`, `openai`, or `ollama`             |
| `ANTHROPIC_API_KEY`  | —                           | Also supports `_1`, `_2`, … for load balancing |
| `ORCHESTRATOR_MODEL` | `claude-haiku-4-5-20251001` | Lighter model for tool-calling phase           |
| `SYNTHESIS_MODEL`    | `claude-sonnet-4-6`         | Stronger model for final answer                |
| `GWCHAT_CONFIG`      | —                           | Path to domain config YAML (see below)         |

See `.env.example` for the full list including OpenAI, Ollama, and tuning vars.

### Domain config file (content/persona)

Set `GWCHAT_CONFIG` to the path of a YAML file to customise the app for your
knowledge graph domain. Falls back to generic built-in defaults if unset or
the file is missing.

Example `domain.yaml`:

```yaml
app_title: "Medical Literature Chat"
app_description: "Ask questions about the medical literature knowledge graph."
system_prompt: |
  You are an expert assistant for a medical literature knowledge graph.
  Always cite the papers you draw evidence from when possible.
orchestrator_system_prompt: |
  You have tools to query a medical literature knowledge graph via MCP...
synthesis_system_prompt: |
  Answer ONLY using the retrieved knowledge graph evidence. Cite papers...
examples:
  "ST3Gal1 & ulcerative colitis": |
    How does ST3Gal1 regulate intestinal barrier function...
```

Supported keys: `app_title`, `app_description`, `system_prompt`,
`orchestrator_system_prompt`, `synthesis_system_prompt`, `examples`.

The MCP server URL is env-var only for now. Switching between multiple MCP
servers at runtime is a possible future addition.

## Running locally

```bash
npm install
cp .env.example .env.local  # fill in API keys and MCP_SSE_URL
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Docker

```bash
docker build -t gwchat .
docker run -p 3000:3000 --env-file .env gwchat
```

## Future work

- **Cross-session memory**: persist conversation history per user across chats
  (similar to Claude's memory feature)
- **Authentication**: optional login so memory can be user-scoped
- **Multiple MCP servers**: runtime-switchable MCP endpoints

## Relationship to kgraph

Currently lives inside the kgraph repo at `gwchat/` with its own git setup.
Will eventually be extracted to its own GitHub repo and pulled in as a git
submodule.

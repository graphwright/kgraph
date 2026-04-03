/**
 * GET /api/session
 * Returns app config (title, description, examples) and MCP connection status.
 * Called once by the client on page load.
 */

import { loadConfig } from "@/lib/config";
import { connectMcp, callMcpTool } from "@/lib/mcp";
import { MCP_SSE_URL, LLM_PROVIDER, ORCHESTRATOR_MODEL, SYNTHESIS_MODEL } from "@/lib/env";

export async function GET() {
  const config = loadConfig();

  let mcpStatus: { connected: boolean; tools: string[]; error?: string };
  let schemaSummary: string | null = null;
  try {
    const { tools, client } = await connectMcp();
    mcpStatus = { connected: true, tools: tools.map((t) => t.name) };
    if (tools.some((t) => t.name === "describe_schema")) {
      schemaSummary = await callMcpTool(client, "describe_schema", {});
    }
  } catch (err) {
    mcpStatus = {
      connected: false,
      tools: [],
      error: `Could not connect to MCP server (${MCP_SSE_URL}): ${err}`,
    };
  }

  return Response.json({
    app_title: config.app_title,
    app_description: config.app_description,
    examples: config.examples,
    mcp: mcpStatus,
    llm: {
      provider: LLM_PROVIDER,
      orchestrator_model: ORCHESTRATOR_MODEL,
      synthesis_model: SYNTHESIS_MODEL,
    },
    schema_summary: schemaSummary,
  });
}

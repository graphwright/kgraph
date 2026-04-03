/**
 * MCP client utilities: connect to the SSE endpoint, list tools, call tools.
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";
import { MCP_SSE_URL, MCP_CONNECT_TIMEOUT_MS } from "./env";

export interface McpTool {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
}

export interface McpConnection {
  client: Client;
  tools: McpTool[];
}

export async function connectMcp(): Promise<McpConnection> {
  const transport = new SSEClientTransport(new URL(MCP_SSE_URL));
  const client = new Client({ name: "gwchat", version: "1.0.0" });

  const connectPromise = client.connect(transport);
  const timeoutPromise = new Promise<never>((_, reject) =>
    setTimeout(
      () => reject(new Error(`MCP connect timed out after ${MCP_CONNECT_TIMEOUT_MS}ms`)),
      MCP_CONNECT_TIMEOUT_MS
    )
  );

  await Promise.race([connectPromise, timeoutPromise]);

  const result = await client.listTools();
  const tools: McpTool[] = result.tools.map((t) => ({
    name: t.name,
    description: t.description ?? "",
    inputSchema: (t.inputSchema as Record<string, unknown>) ?? {
      type: "object",
      properties: {},
    },
  }));

  return { client, tools };
}

export async function callMcpTool(
  client: Client,
  name: string,
  args: Record<string, unknown>
): Promise<string> {
  const result = await client.callTool({ name, arguments: args });
  if (!Array.isArray(result.content)) return String(result.content);
  return result.content
    .map((block) => {
      if (typeof block === "object" && block !== null && "text" in block) {
        return String((block as { text: unknown }).text);
      }
      return JSON.stringify(block);
    })
    .join(" ");
}

/** Convert MCP tool descriptors to OpenAI-style function tool defs for AI SDK. */
export function mcpToolsToAiSdk(tools: McpTool[]) {
  return Object.fromEntries(
    tools.map((t) => [
      t.name,
      {
        description: t.description,
        parameters: t.inputSchema,
      },
    ])
  );
}

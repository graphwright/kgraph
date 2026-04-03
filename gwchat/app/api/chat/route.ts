/**
 * POST /api/chat
 * Body (from @ai-sdk/react useChat): { messages: UIMessage[] }
 *
 * Two-phase chat loop:
 *   Phase A: Orchestrator calls MCP tools until it has enough info (or hits max iterations).
 *   Phase B: Synthesis produces the final answer using tool results + conversation history.
 *
 * Returns a UI message stream (SSE) using createUIMessageStream / createUIMessageStreamResponse.
 */

import { createAnthropic } from "@ai-sdk/anthropic";
import { createOpenAI } from "@ai-sdk/openai";
import {
  generateText,
  createUIMessageStream,
  createUIMessageStreamResponse,
  UIMessage,
  ModelMessage,
  LanguageModel,
  dynamicTool,
  jsonSchema,
  stepCountIs,
} from "ai";
import { loadConfig } from "@/lib/config";
import { connectMcp, callMcpTool, McpTool } from "@/lib/mcp";
import {
  LLM_PROVIDER,
  ORCHESTRATOR_MODEL,
  SYNTHESIS_MODEL,
  OLLAMA_BASE_URL,
  OLLAMA_MODEL,
  LLM_MIN_REQUEST_INTERVAL_MS,
  LLM_SYNTHESIS_HISTORY_TURNS,
  ORCHESTRATOR_MAX_ITERATIONS,
  collectApiKeys,
} from "@/lib/env";

// ── Throttle ──────────────────────────────────────────────────────────────────

let _lastRequestStart = 0;

async function throttle(): Promise<void> {
  const now = Date.now();
  const wait = Math.max(0, _lastRequestStart + LLM_MIN_REQUEST_INTERVAL_MS - now);
  _lastRequestStart = now + wait;
  if (wait > 0) await new Promise((r) => setTimeout(r, wait));
  _lastRequestStart = Date.now();
}

// ── Model factory ─────────────────────────────────────────────────────────────

function makeModel(modelId: string): LanguageModel {
  if (LLM_PROVIDER === "anthropic") {
    const keys = collectApiKeys("ANTHROPIC_API_KEY");
    const key = keys[Math.floor(Math.random() * keys.length)];
    return createAnthropic({ apiKey: key })(modelId);
  }
  if (LLM_PROVIDER === "openai") {
    const keys = collectApiKeys("OPENAI_API_KEY");
    const key = keys[Math.floor(Math.random() * keys.length)];
    return createOpenAI({ apiKey: key })(modelId);
  }
  if (LLM_PROVIDER === "ollama") {
    return createOpenAI({ baseURL: `${OLLAMA_BASE_URL}/v1`, apiKey: "ollama" })(OLLAMA_MODEL);
  }
  throw new Error(`Unknown LLM_PROVIDER: ${LLM_PROVIDER}`);
}

// ── Tool builder ──────────────────────────────────────────────────────────────

function buildAiTools(
  mcpTools: McpTool[],
  mcpClient: Awaited<ReturnType<typeof connectMcp>>["client"]
) {
  const tools: Record<string, ReturnType<typeof dynamicTool>> = {};
  for (const t of mcpTools) {
    const toolName = t.name;
    const schema =
      t.inputSchema && Object.keys(t.inputSchema).length > 0
        ? t.inputSchema
        : { type: "object" as const, properties: {} };
    tools[toolName] = dynamicTool({
      description: t.description,
      inputSchema: jsonSchema(schema as Parameters<typeof jsonSchema>[0]),
      execute: async (input) => callMcpTool(mcpClient, toolName, input as Record<string, unknown>),
    });
  }
  return tools;
}

// ── UIMessage → ModelMessage conversion ───────────────────────────────────────

function uiMessagesToModelMessages(messages: UIMessage[]): ModelMessage[] {
  const result: ModelMessage[] = [];
  for (const m of messages) {
    if (m.role === "system") continue; // system prompt handled separately
    if (m.role === "user") {
      const text = m.parts
        .filter((p) => p.type === "text")
        .map((p) => (p as { type: "text"; text: string }).text)
        .join("\n");
      result.push({ role: "user", content: text });
    } else if (m.role === "assistant") {
      const text = m.parts
        .filter((p) => p.type === "text")
        .map((p) => (p as { type: "text"; text: string }).text)
        .join("\n");
      result.push({ role: "assistant", content: text });
    }
  }
  return result;
}

function truncateHistory(history: ModelMessage[], nTurns: number): ModelMessage[] {
  const keep = 2 * nTurns;
  return history.length > keep ? history.slice(-keep) : history;
}

// ── POST handler ──────────────────────────────────────────────────────────────

export async function POST(req: Request) {
  const body = (await req.json()) as { messages: UIMessage[]; schema_summary?: string };
  const uiMessages = body.messages ?? [];
  const schemaSummary = body.schema_summary ?? null;

  // Extract the last user message text
  const lastUiMessage = uiMessages.at(-1);
  if (!lastUiMessage || lastUiMessage.role !== "user") {
    return new Response("Last message must be from user", { status: 400 });
  }
  const userText = lastUiMessage.parts
    .filter((p) => p.type === "text")
    .map((p) => (p as { type: "text"; text: string }).text)
    .join("\n");

  // Full conversation history (excluding last user message) for synthesis context
  const priorHistory = uiMessagesToModelMessages(uiMessages.slice(0, -1));
  const config = loadConfig();

  // Connect to MCP (best-effort)
  let aiTools: Record<string, ReturnType<typeof dynamicTool>> = {};
  try {
    const conn = await connectMcp();
    aiTools = buildAiTools(conn.tools, conn.client);
  } catch {
    // Continue without MCP tools
  }

  const hasTools = Object.keys(aiTools).length > 0;

  const stream = createUIMessageStream({
    execute: async ({ writer }) => {
      // ── Phase A: Orchestrator — runs tool loop internally ─────────────────
      const orchestratorSystem = schemaSummary
        ? `This knowledge graph session has the following schema:\n\n${schemaSummary}\n\n---\n\n${config.orchestrator_system_prompt}`
        : config.orchestrator_system_prompt;

      await throttle();
      const orchResult = await generateText({
        model: makeModel(ORCHESTRATOR_MODEL),
        system: orchestratorSystem,
        messages: [{ role: "user", content: userText }],
        tools: hasTools ? aiTools : undefined,
        stopWhen: stepCountIs(ORCHESTRATOR_MAX_ITERATIONS),
      });

      // Collect all dynamic tool outputs across all internal steps
      const toolResultsThisTurn: string[] = orchResult.dynamicToolResults.map((r) =>
        typeof r.output === "string" ? r.output : JSON.stringify(r.output)
      );

      // ── Phase B: Synthesis ────────────────────────────────────────────────
      await throttle();

      const truncated = truncateHistory(priorHistory, LLM_SYNTHESIS_HISTORY_TURNS);

      let finalText: string;
      if (toolResultsThisTurn.length === 0) {
        // No tools used — use orchestrator answer directly
        finalText = orchResult.text;
      } else {
        const synthesisUserContent = `${userText}\n\n---\nRetrieved from knowledge graph:\n${toolResultsThisTurn.join("\n\n")}`;
        const synthesisResult = await generateText({
          model: makeModel(SYNTHESIS_MODEL),
          system: config.synthesis_system_prompt,
          messages: [...truncated, { role: "user", content: synthesisUserContent }],
        });
        finalText = synthesisResult.text;
      }

      const textId = "t0";
      writer.write({ type: "text-start", id: textId });
      writer.write({ type: "text-delta", id: textId, delta: finalText });
      writer.write({ type: "text-end", id: textId });
    },

    onError: (err) => {
      console.error("[gwchat] chat error:", err);
      return "An error occurred processing your request.";
    },
  });

  return createUIMessageStreamResponse({ stream });
}

/**
 * Operational configuration from environment variables.
 * All values are read at module load time (server-side only).
 */

export const MCP_SSE_URL = process.env.MCP_SSE_URL ?? "http://localhost:8001/sse";
export const LLM_PROVIDER = (process.env.LLM_PROVIDER ?? "anthropic").toLowerCase();

export const ANTHROPIC_MODEL = process.env.ANTHROPIC_MODEL ?? "claude-sonnet-4-6";
export const ORCHESTRATOR_MODEL =
  process.env.ORCHESTRATOR_MODEL ??
  (LLM_PROVIDER === "openai" ? "gpt-4o-mini" : "claude-haiku-4-5-20251001");
export const SYNTHESIS_MODEL =
  process.env.SYNTHESIS_MODEL ?? (LLM_PROVIDER === "openai" ? "gpt-4o" : ANTHROPIC_MODEL);

export const OPENAI_MODEL = process.env.OPENAI_MODEL ?? "gpt-4o";
export const OLLAMA_MODEL = process.env.OLLAMA_MODEL ?? "llama3.2";
export const OLLAMA_BASE_URL = process.env.OLLAMA_BASE_URL ?? "http://ollama:11434";

export const MCP_CONNECT_TIMEOUT_MS = parseFloat(process.env.MCP_CONNECT_TIMEOUT ?? "25") * 1000;
export const LLM_MIN_REQUEST_INTERVAL_MS =
  parseFloat(process.env.LLM_MIN_REQUEST_INTERVAL_SECONDS ?? "3.0") * 1000;
export const LLM_RATE_LIMIT_RETRY_DELAY_MS =
  parseFloat(process.env.LLM_RATE_LIMIT_RETRY_DELAY_SECONDS ?? "20") * 1000;
export const LLM_SYNTHESIS_HISTORY_TURNS = parseInt(
  process.env.LLM_SYNTHESIS_HISTORY_TURNS ?? "4",
  10
);
export const ORCHESTRATOR_MAX_ITERATIONS = 8;

/** Collect numbered API keys: PREFIX, PREFIX_1, PREFIX_2, … */
export function collectApiKeys(prefix: string): string[] {
  const keys: string[] = [];
  const primary = process.env[prefix];
  if (primary) keys.push(primary);
  for (let i = 1; ; i++) {
    const k = process.env[`${prefix}_${i}`];
    if (!k) break;
    keys.push(k);
  }
  return keys;
}

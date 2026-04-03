import { describe, it, expect } from "vitest";
import { SessionInfoSchema } from "@/lib/schemas";

const VALID_SESSION = {
  app_title: "Test Graph",
  app_description: "A test knowledge graph",
  examples: { "Example 1": "What is X?" },
  mcp: { connected: true, tools: ["search_entities", "bfs_query"] },
  llm: {
    provider: "anthropic",
    orchestrator_model: "claude-haiku-4-5-20251001",
    synthesis_model: "claude-sonnet-4-6",
  },
  schema_summary: "Some schema text",
};

describe("SessionInfoSchema", () => {
  it("parses a valid session response", () => {
    const result = SessionInfoSchema.parse(VALID_SESSION);
    expect(result.app_title).toBe("Test Graph");
    expect(result.mcp.connected).toBe(true);
    expect(result.schema_summary).toBe("Some schema text");
  });

  it("accepts null schema_summary", () => {
    const result = SessionInfoSchema.parse({ ...VALID_SESSION, schema_summary: null });
    expect(result.schema_summary).toBeNull();
  });

  it("accepts optional mcp.error field", () => {
    const result = SessionInfoSchema.parse({
      ...VALID_SESSION,
      mcp: { connected: false, tools: [], error: "connection refused" },
    });
    expect(result.mcp.error).toBe("connection refused");
  });

  it("rejects missing required fields", () => {
    expect(() => SessionInfoSchema.parse({ app_title: "only title" })).toThrow();
  });

  it("rejects wrong types", () => {
    expect(() =>
      SessionInfoSchema.parse({ ...VALID_SESSION, mcp: { connected: "yes", tools: [] } })
    ).toThrow();
  });
});

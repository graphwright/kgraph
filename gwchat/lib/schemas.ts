/**
 * Zod schemas for API response types.
 * Provides both TypeScript types (inferred) and runtime validation at API boundaries.
 */

import { z } from "zod";

export const SessionInfoSchema = z.object({
  app_title: z.string(),
  app_description: z.string(),
  examples: z.record(z.string(), z.string()),
  mcp: z.object({
    connected: z.boolean(),
    tools: z.array(z.string()),
    error: z.string().optional(),
  }),
  llm: z.object({
    provider: z.string(),
    orchestrator_model: z.string(),
    synthesis_model: z.string(),
  }),
  schema_summary: z.string().nullable(),
});

export type SessionInfo = z.infer<typeof SessionInfoSchema>;

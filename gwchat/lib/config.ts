/**
 * Domain configuration loaded from GWCHAT_CONFIG (path to a YAML file).
 * Falls back to built-in defaults if the env var is unset or the file is missing.
 */

import fs from "fs";
import path from "path";
import yaml from "yaml";

export interface GwchatConfig {
  app_title: string;
  app_description: string;
  system_prompt: string;
  orchestrator_system_prompt: string;
  synthesis_system_prompt: string;
  examples: Record<string, string>;
}

const DEFAULT_CONFIG: GwchatConfig = {
  app_title: "Knowledge Graph Chat",
  app_description: "Chat with your knowledge graph.",
  system_prompt:
    "You are a helpful assistant with access to a knowledge graph. " +
    "Use the available tools to answer questions accurately. " +
    "Cite your sources when possible.",
  orchestrator_system_prompt:
    "You have tools to query a knowledge graph via MCP (Model Context Protocol). " +
    "Decide which tools to call to answer the user's question. " +
    "Call tools as needed; when you have enough information, respond with a final answer.\n\n" +
    "**Workflow:**\n" +
    "1. Call describe_schema() first to learn the entity types, predicates, and graph description.\n" +
    "2. Call search_entities(query) with a specific entity name to resolve it to a canonical ID.\n" +
    "3. Call bfs_query(seeds, max_hops, ...) to traverse the graph from known entity IDs.\n" +
    "4. Call describe_entity(id) to expand any stub node that needs more detail.\n\n" +
    "**Prefer bfs_query** whenever exploring a neighborhood or connections is needed. " +
    "It returns a subgraph via BFS and is more efficient than multiple individual lookups.\n\n" +
    "**Tool priority:** Always prefer describe_schema, search_entities, bfs_query, and describe_entity. " +
    "Only use other tools as a last resort. " +
    "Never use ingest_paper or check_ingest_status unless the user explicitly asks.",
  synthesis_system_prompt:
    "You are a helpful assistant. Answer the user's question ONLY using the retrieved " +
    "knowledge graph evidence. Cite papers and sources when possible.\n\n" +
    "CRITICAL: If the retrieved knowledge graph has no relevant entities for this query, " +
    "you MUST DECLINE TO ANSWER. Do NOT answer from general knowledge. " +
    "Simply state that you cannot answer because the graph has no relevant information for this query.",
  examples: {
    "What entities are in the graph?":
      "What kinds of entities and relationships does this knowledge graph contain? Give me an overview.",
  },
};

let _config: GwchatConfig | null = null;

export function loadConfig(): GwchatConfig {
  if (_config) return _config;

  const configPath = process.env.GWCHAT_CONFIG;
  if (configPath) {
    const resolved = path.resolve(configPath);
    try {
      const raw = fs.readFileSync(resolved, "utf-8");
      const parsed = yaml.parse(raw) as Partial<GwchatConfig>;
      _config = { ...DEFAULT_CONFIG, ...parsed };
      return _config;
    } catch (err) {
      console.warn(`[gwchat] Could not load config from ${resolved}: ${err}. Using defaults.`);
    }
  }

  _config = DEFAULT_CONFIG;
  return _config;
}

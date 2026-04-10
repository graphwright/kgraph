# Querying the Graph with LLMs

> **Placeholder** — this page needs to be written.

This page covers how LLMs navigate and query the knowledge graph in practice — what
patterns work, what to avoid, and how to structure agent prompts for effective graph use.

## The basic interaction pattern

1. The LLM receives a user question.
2. It calls `search_entities` to find relevant starting nodes.
3. It calls `get_relationships` or `traverse` to explore the neighborhood.
4. It synthesizes an answer from the returned subgraph, citing provenance.

## Grounding and citation

A key advantage of the knowledge graph over pure RAG is that every claim the LLM
makes can be grounded in a specific graph assertion with a provenance chain. Prompts
should instruct the LLM to cite entity IDs and source documents in its answers.

## Multi-hop reasoning

For questions that require following a chain of relationships (e.g. "which drugs
interact with enzymes that metabolize compound X?"), the `traverse` tool is more
efficient than repeated `get_relationships` calls. Set `max_hops` conservatively
to avoid returning very large subgraphs.

## Handling uncertainty

When the graph contains conflicting claims or low-confidence assertions, the LLM
should surface the uncertainty rather than picking one answer. Prompt guidance:
"If sources disagree, report the disagreement and cite both."

## See also

- [MCP Server](mcp-server.md)
- [Embeddings](embeddings.md)
- [Trust and Provenance](../trust/provenance.md)

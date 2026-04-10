# Knowledge Graph Framework — Documentation

A framework for building knowledge graphs over complex professional or academic
literature: medical papers, legal documents, technical specifications. Every assertion
in the graph traces back to a source document and location. Provenance is not an
afterthought — it is load-bearing.

For the conceptual foundation, see **[Overview](overview.md)** and
**[Architecture](architecture.md)**. For book-length treatments of the full
pipeline, see **[Graphwright Publications](books.md)**.

## Live tools

- [Medical literature chat](/chat/)
- [OpenAPI spec](/docs/)
- [Graph visualization](/graph-viz/) — currently focused on medical literature
- [GraphQL GUI](/graphiql/)

---

## Concepts and Architecture

- [Overview](overview.md) — why knowledge graphs, core concepts, two-pass ingestion model
- [Architecture](architecture.md) — component breakdown, module structure, immutability design

## Identity and Entity Resolution

- [Canonical IDs](identity/canonical-ids.md) — entity lifecycle, authority lookup, synonym caching
- [Deduplication](identity/deduplication.md) — merging and flagging near-duplicate entities

## Trust and Provenance

- [Provenance](trust/provenance.md) — source attribution, confidence scores, audit trail
- [Conflicting Claims](trust/conflicting-claims.md) — representing disagreements, not silently resolving them

## Ingestion Pipeline

- [Pipeline](ingestion/pipeline.md) — stages and interfaces (parser → extractor → resolver → embedder)
- [Chunking](ingestion/chunking.md) — document segmentation strategies
- [Error Handling](ingestion/error-handling.md) — partial extraction, retries, fallback behavior

## LLM Integration

- [MCP Server](llm-integration/mcp-server.md) — tools exposed to LLMs via Model Context Protocol
- [MCP Troubleshooting](llm-integration/mcp-troubleshooting.md) — connection and tool call issues
- [Querying with LLMs](llm-integration/querying.md) — how LLMs navigate and query the graph
- [Embeddings](llm-integration/embeddings.md) — semantic search strategy, storage and retrieval
- [Extraction Prompts](llm-integration/extraction-prompts.md) — prompt design for entity and relationship extraction

## Schema Design

- [Schema Design Guide](schema/schema-design-guide.md) — defining DomainSchema, entity and relationship subclasses
- [Adapting to Your Domain](schema/adapting-to-your-domain.md) — step-by-step: define schema, write prompts, configure pipeline, validate

## Storage, Export, and Serving

- [Storage and Export](storage-and-export.md) — bundle format (manifest.json + JSONL), export, query interfaces
- [Deployment and Operations](deployment-and-operations.md) — SQLite vs PostgreSQL, Docker, Chainlit, scaling

## Examples

- [Medical Literature (medlit)](examples/medlit.md) — reference biomedical implementation using JATS XML and UMLS
- [Sherlock Holmes](examples/sherlock.md) — simplified literary example, no external authorities

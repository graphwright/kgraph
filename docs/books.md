# Graphwright Publications

Three books covering the full pipeline from raw text to a language model that can reason over what that text contained.

---

## [The Identity Server: Canonical Identity for Knowledge Graphs](../books/the-identity-server.pdf)

The trustworthiness book. Full architecture of the identity server: the domain-agnostic base, the plugin contract, Docker deployment, caching, entity lifecycle, and the epistemic commons — the shared identifier infrastructure (MeSH, HGNC, RxNorm, UniProt) that makes graphs composable across sources.

[Download PDF](../books/the-identity-server.pdf)

---

## [Knowledge Graphs from Unstructured Text](../books/knowledge-graphs-from-unstructured-text.pdf)

The extraction book. How to build a knowledge graph from raw documents using LLMs: schema design, the ingestion pipeline, identity resolution, provenance, and diagnostics. Includes the medlit biomedical reference implementation.

[Download PDF](../books/knowledge-graphs-from-unstructured-text.pdf)

---

## [BFS-QL: A Graph Query Protocol for Language Models](../books/bfs-ql.pdf)

The interface book. How to serve a knowledge graph to a language model via a minimal, LLM-friendly protocol. Five MCP tools, a flat query format, backends for SPARQL, Postgres/pgvector, and Neo4j, and a worked implementation against the medlit graph.

[Download PDF](../books/bfs-ql.pdf)

---

Read in order, the three books cover: ensuring knowledge is **trustworthy** → getting knowledge **in** → getting it **out**.

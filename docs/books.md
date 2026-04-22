# Graphwright Publications

Three books covering the full pipeline from raw text to a language model that can reason over what that text contained.

---

## [The Typed Graph: Naming, Knowing, and Trusting Machine Knowledge](../identity-book/index.html)

The trustworthiness book. How canonical identity, a typed schema, and structural provenance together make machine knowledge defensible. Covers the epistemic commons (MeSH, HGNC, RxNorm, UniProt), the identity server's domain-agnostic core and plugin contract, the entity lifecycle, and the typed graph's central argument: that a finite predicate ontology with declared domain and range makes certain classes of error inexpressible rather than merely discouraged.

[Download PDF](../books/the-identity-server.pdf)

---

## [Knowledge Graphs from Unstructured Text](../kg-book/index.html)

The extraction book. How to build a knowledge graph from raw documents using LLMs: schema design, the ingestion pipeline, identity resolution, provenance, and diagnostics. Includes the medlit biomedical reference implementation.

[Download PDF](../books/knowledge-graphs-from-unstructured-text.pdf)

---

## [BFS-QL: A Graph Query Protocol for Language Models](../bfs-ql-book/index.html)

The interface book. The knowledge is in the graph; the LLM can't get to it — this is a book about the missing interface. Argues that SPARQL and Cypher are the wrong abstraction for LLM-driven graph exploration, and that breadth-first traversal with topology-first, metadata-on-demand design is the right one. Covers the five-tool MCP protocol, the working-set framing for context-window efficiency, backends for SPARQL, Postgres/pgvector, and Neo4j, and cross-graph composition via shared canonical identity.

[Download PDF](../books/bfs-ql.pdf)

---

Read in order, the three books cover: ensuring knowledge is **trustworthy** → getting knowledge **in** → getting it **out**.

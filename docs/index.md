# Knowledge Graph Framework -- Documentation

This is a framework for building knowledge graphs over complex professional or academic
literature: medical papers, legal documents, technical specifications. Every assertion
in the graph traces back to a source document and location. Provenance is not an
afterthought -- it is load-bearing.

For the conceptual foundation, see **[Overview](overview.md)** and
**[Architecture](architecture.md)**. For book-length treatments of the full
pipeline, see **[Graphwright Publications](books.md)**.

## A Manifesto for Machine Knowledge

We are now in an age of machine reasoning, and some of this reasoning is done
in high-stakes domains: medicine, law, engineering, spaceflight. Lives and
livelihoods can be affected by incorrect conclusions or decisions. The cost of
error is real and significant. LLMs are here, they are staying, and there is no
turning back the clock.

As we all know, LLMs have weaknesses. Their mastery of language syntax is
astonishing, but they don't understand "this refers to that," or "these two
things are the same." They have no persistent notion of identity. They do not
inhabit a world of things connected by relationships. They do not track logical
consequence from one step to the next.

They cannot reason across multiple causal steps because they cannot reliably
reason across a single causal step. They do not know what things *are* or how
they *behave*, only how they are *talked about*.

And so we build RAG (retrieval-augmented generation) systems, hoping to improve
the situation. We improve the LLM's focus on material that is more relevant,
more similar, better connected to sources of information, and it helps.

But we are still dealing with strings, not things.

We still cannot say "this refers to that," or "these two mentions refer to the
same entity." We still cannot follow a chain of causality or enforce a sequence
of logical steps. We retrieve passages, but we do not operate on meaning.

If RAG doesn't close the gap, what would?

* **Identity -- what are we talking about?**

  * Canonical IDs -- identifiers anchored in curated human knowledge (think Wikipedia)
  * Authoritative ontologies -- shared bodies of reference (think dictionaries, taxonomies)
  * Deduplication across sources -- recognizing that the same thing may be named in different ways ("tumor" vs "neoplasm")
  * A fixed set of entity types

* **Type -- which relationships are meaningful?**

  * A fixed set of predicates
  * Domain and range for each predicate -- constraints on which kinds of things can be related, so we do not assert things like "aspirin inhibits New York"
  * Structural validity -- a claim is valid if it is well-formed with respect to the graph's type system, independent of whether it is true or false

* **Provenance -- where did this claim come from?**

  * Source traceability
  * Evidence aggregation
  * Confidence grounded in origin

A system cannot reason reliably about the world unless it represents that world
with stable identities, constrained relationships, and explicit evidence.

Machine reasoning requires a data model, not just a model.

## The Typed Graph

When we build a knowledge graph where we

* fix the set of entity types and the set of predicates
* establish domain and range constraints for each predicate
* require that entities be assigned canonical IDs whenever possible
* preserve provenance information for all relationships

we are no longer dealing with strings, but with a structured representation of the world.

This is what we call a *typed graph*.

A typed graph does not guarantee that its conclusions are true. It guarantees
something more fundamental: that its claims are well-formed, grounded in
identifiable entities, and traceable to their sources.

Large classes of nonsense and hallucination are not corrected -- they are never admitted into the system at all.
Category errors are rejected. Ambiguous references are resolved or made
explicit. Unsupported claims are visible as such.

The result is a system whose outputs may still be wrong, but are always
inspectable, reproducible, and subject to correction.

That is the minimum standard for reasoning in high-stakes domains.

```
Unstructured Text
       |
       v
  Extraction (LLM)
       |
       v
  Mentions (strings)
       |
       v
  Identity Resolution
  -- canonical IDs
  -- deduplication
       |
       v
  Typed Graph
  -- entity types
  -- predicates
  -- domain/range
  -- provenance
       |
       v
  Queries / Traversals
       |
       v
  Machine Reasoning
  -- multi-step
  -- composable
  -- inspectable
```

## Live tools

- [Medical literature chat](/chat/)
- [OpenAPI spec](/docs/)
- [Graph visualization](/graph-viz/) -- currently focused on medical literature
- [GraphQL GUI](/graphiql/)

<!--
I want to review the stuff from here down, some will probably want to go away, or at least
be carefully reviewed and brought up to date.
-->

## Concepts and Architecture

- [Overview](overview.md) -- why knowledge graphs, core concepts, two-pass ingestion model
- [Architecture](architecture.md) -- component breakdown, module structure, immutability design

## Identity and Entity Resolution

- [Canonical IDs](identity/canonical-ids.md) -- entity lifecycle, authority lookup, synonym caching
- [Deduplication](identity/deduplication.md) -- merging and flagging near-duplicate entities

## Trust and Provenance

- [Provenance](trust/provenance.md) -- source attribution, confidence scores, audit trail
- [Conflicting Claims](trust/conflicting-claims.md) -- representing disagreements, not silently resolving them

## Ingestion Pipeline

- [Pipeline](ingestion/pipeline.md) -- stages and interfaces (parser → extractor → resolver → embedder)
- [Chunking](ingestion/chunking.md) -- document segmentation strategies
- [Error Handling](ingestion/error-handling.md) -- partial extraction, retries, fallback behavior

## LLM Integration

- [MCP Server](llm-integration/mcp-server.md) -- tools exposed to LLMs via Model Context Protocol
- [MCP Troubleshooting](llm-integration/mcp-troubleshooting.md) -- connection and tool call issues
- [Querying with LLMs](llm-integration/querying.md) -- how LLMs navigate and query the graph
- [Embeddings](llm-integration/embeddings.md) -- semantic search strategy, storage and retrieval
- [Extraction Prompts](llm-integration/extraction-prompts.md) -- prompt design for entity and relationship extraction

## Schema Design

- [Schema Design Guide](schema/schema-design-guide.md) -- defining DomainSchema, entity and relationship subclasses
- [Adapting to Your Domain](schema/adapting-to-your-domain.md) -- step-by-step: define schema, write prompts, configure pipeline, validate

## Storage, Export, and Serving

- [Storage and Export](storage-and-export.md) -- bundle format (manifest.json + JSONL), export, query interfaces
- [Deployment and Operations](deployment-and-operations.md) -- SQLite vs PostgreSQL, Docker, Chainlit, scaling

## Examples

- [Medical Literature (medlit)](examples/medlit.md) -- reference biomedical implementation using JATS XML and UMLS
- [Sherlock Holmes](examples/sherlock.md) -- simplified literary example, no external authorities

# Chunking Strategies

> **Placeholder** — this page needs to be written.

Before an LLM can extract entities and relationships, a document must be segmented into
chunks that fit within a context window and preserve enough surrounding context to make
extraction meaningful.

## Goals of chunking

- Keep related content together (a claim and its evidence should be in the same chunk).
- Avoid cutting across sentence or paragraph boundaries when possible.
- Produce chunks small enough for the LLM context window, large enough to be useful.
- Preserve chunk identity so extracted mentions can be traced back to a specific location.

## Strategies

### Fixed-size with overlap

Split at a token count (e.g. 512 or 1024 tokens) with a sliding overlap (e.g. 10%).
Simple and predictable. Works poorly when paragraph breaks fall mid-chunk.

### Structure-aware splitting

Use document structure (headings, sections, paragraphs) as natural split points. Works
well for structured formats like JATS XML or HTML. The parser stage identifies structure;
the chunker respects it.

### Semantic splitting

Use embedding similarity to find natural topic shifts. More expensive but produces
chunks that are semantically coherent. Useful for long-form prose without clear structure.

## Chunk metadata

Each chunk should carry:

- Document identifier and version.
- Section or heading path (if available).
- Character or token offset within the document.
- Chunk index and total chunk count.

This metadata flows through extraction and becomes part of provenance records.

## See also

- [Pipeline](pipeline.md)
- [Trust and Provenance](../trust/provenance.md)

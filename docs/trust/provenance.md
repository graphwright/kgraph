# Trust and Provenance

> **Placeholder** — this page needs to be written. Content currently lives in
> fragments across the pipeline and storage docs.

Provenance is the philosophical core of this project. Every assertion in the graph
must be traceable to a source document, a location within that document, and the
extraction step that produced it. Transparency is not an afterthought — it is
load-bearing.

## Source attribution

Each entity and relationship carries a reference to:

- The **source document** (title, DOI, or other identifier).
- The **chunk or section** within that document where the mention appears.
- The **text span** — the exact string the extractor saw.

This means a user or downstream system can always ask: "where did this come from?"
and get a meaningful answer.

## Confidence scores

Confidence is attached at extraction time. It reflects:

- The LLM's expressed certainty (where available).
- The quality of the source (peer-reviewed vs. grey literature).
- Whether the entity resolved to a canonical ID or remained provisional.

Confidence scores are not hidden; they are surfaced in query results and
available for filtering.

## Conflicting claims

When two sources make contradictory assertions about the same entities, the graph
records **both** claims — with their respective provenance and confidence — rather
than silently picking one. See [Conflicting Claims](conflicting-claims.md).

## Audit trail

The full chain is preserved:

```
raw document
  → chunk
    → extracted mention
      → resolved entity / provisional entity
        → graph assertion (edge)
```

At any point in this chain, you can walk backward to the source.

## See also

- [Conflicting Claims](conflicting-claims.md)
- [Storage and Export](../storage-and-export.md)

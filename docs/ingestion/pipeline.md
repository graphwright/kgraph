# The Ingestion Pipeline

> **Placeholder** — content to be migrated and expanded from
> [`../pipeline.md`](../pipeline.md).

## Two-pass architecture

The pipeline uses a two-pass architecture:

1. **Pass 1 — Entity extraction**: parse documents, extract entity mentions, resolve
   to canonical or provisional entities, build the entity table.
2. **Pass 2 — Relationship extraction**: with a stable entity vocabulary in hand,
   identify relationships between resolved entities within each document.

This ordering matters: resolving entities first means the relationship extractor can
refer to canonical IDs rather than raw text spans, which improves consistency and
enables cross-document linking.

## Stages

```
document
  → parser        (raw bytes → structured chunks)
  → extractor     (chunks → mentions)
  → resolver      (mentions → entities)
  → embedder      (entities → vector embeddings)
  → bundle builder (entities + relationships → exportable bundle)
```

Each stage is defined as an abstract interface. Domain pipelines implement them.

## Component interfaces

- `DocumentParserInterface` — takes a raw document, returns chunks.
- `EntityExtractorInterface` — takes a chunk, returns entity mentions.
- `RelationshipExtractorInterface` — takes a chunk + resolved entities, returns edges.
- `ResolverInterface` — maps mentions to canonical or provisional entities.
- `EmbedderInterface` — generates vector embeddings for entities.

## See also

- [Chunking](chunking.md)
- [Error Handling](error-handling.md)
- [Schema Design](../schema/schema-design-guide.md)

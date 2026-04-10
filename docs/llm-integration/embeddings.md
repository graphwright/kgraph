# Embeddings

> **Placeholder** — this page needs to be written.

Embeddings enable semantic search over the knowledge graph — finding entities by
meaning rather than exact string match.

## Where embeddings are generated

Embeddings are generated at the end of the ingestion pipeline, after entities are
resolved and deduplicated. The `EmbedderInterface` takes a resolved entity record
and returns a dense vector.

## What gets embedded

- **Entity name + description** — the primary embedding, used for semantic search.
- **Entity context** — optionally, a snippet of the source text where the entity
  was first mentioned, to capture domain-specific usage.

## Storage

Embeddings are stored in the bundle alongside entity records. At serve time, kgserver
loads them into a vector index (currently in-memory; persistent index support is
planned).

## Matching embedding models

The model used at ingestion time must match the model used at query time. Mismatches
produce meaningless similarity scores. The bundle manifest records the embedding model
name and version.

## Choosing a model

- For biomedical domains: PubMedBERT, BioLORD, or similar domain-adapted models
  outperform general-purpose models.
- For general domains: `text-embedding-3-small` or `text-embedding-3-large`
  (OpenAI) are practical defaults.
- For fully local deployments: Nomic Embed or similar open models.

## See also

- [Pipeline](../ingestion/pipeline.md)
- [Querying with LLMs](querying.md)

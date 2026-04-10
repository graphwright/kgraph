# Canonical IDs and Entity Resolution

> **Placeholder** — content to be migrated and expanded from
> [`../canonical-ids-and-entity-resolution.md`](../canonical-ids-and-entity-resolution.md).

## The importance of canonical IDs

Canonical IDs are stable identifiers drawn from accepted ontologies — UMLS, MeSH, HGNC,
RxNorm, UniProt, DBPedia, and others. They are the mechanism by which entities become
part of the edifice of human knowledge rather than isolated, document-local names.

When two papers refer to "ibuprofen" and "Advil," canonical resolution collapses those
mentions into a single node (`RxNorm:5640`). This is what makes cross-document reasoning
possible — and what makes the graph useful beyond a single corpus.

## Entity lifecycle

1. **Extraction** — the LLM produces a mention (a text span + type).
2. **Resolution** — the resolver checks the synonym cache, then calls an authority lookup.
3. **Provisional** — if no canonical ID is found, the entity gets a temporary ID and
   waits for promotion.
4. **Canonical** — once usage and confidence thresholds are met (`PromotionConfig`),
   the entity is promoted and assigned a stable ID from an authoritative ontology,
   frequently mappable to a specific URL.

## Authority lookup

The framework defines:

- `CanonicalId` — Pydantic model: `id`, optional `url`, optional `synonyms`.
- `CanonicalIdLookupInterface` — ABC for querying an authority (UMLS, RxNorm, etc.).
- `CanonicalIdCacheInterface` — ABC for caching results (e.g. `JsonFileCanonicalIdCache`).

## Synonym cache

A synonym cache maps `name → canonical_id` so repeated mentions resolve to one node
without hitting the authority API each time. It is seeded with a domain vocabulary and
updated as resolution and dedup discover new mappings. It persists across runs.

## See also

- [Deduplication](deduplication.md)
- [Trust and Provenance](../trust/provenance.md)

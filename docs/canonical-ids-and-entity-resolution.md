# Canonical IDs and Entity Resolution

Canonical IDs are stable identifiers from authoritative sources (UMLS, MeSH, HGNC, RxNorm, UniProt, DBPedia, etc.) that uniquely identify entities across knowledge bases. This doc covers how identity works, authority lookups, and the synonym cache.

## How identity works

- **Canonical entities** have a stable `entity_id` from an authority (e.g. `UMLS:C0006142`). The same entity is the same node across documents.
- **Provisional entities** have a temporary ID until they are promoted (usage/confidence thresholds) or linked by a later lookup.
- Resolution maps each **mention** (text span from extraction) to either an existing entity or a new canonical/provisional entity.

## Authority lookup

The framework provides:

- **`CanonicalId`** — Pydantic model: `id`, optional `url`, optional `synonyms`.
- **`CanonicalIdLookupInterface`** — ABC for looking up a canonical ID by name and type (e.g. call UMLS/RxNorm APIs).
- **`CanonicalIdCacheInterface`** — ABC for caching lookups (e.g. `JsonFileCanonicalIdCache`).

Typical flow: extractor produces mentions → resolver tries cache → on miss, calls authority lookup → stores result in cache and returns entity (canonical or provisional).

## Synonym cache

In domain pipelines (e.g. medlit), a **synonym cache** (or seeded vocabulary) records name → canonical_id (and optionally type) so that repeated mentions of the same entity hit the cache and resolve to one node. The cache is updated as resolution and dedup discover new mappings. Persist it so that incremental runs reuse it.

## Promotion

Provisional entities are promoted to canonical when they meet `PromotionConfig` thresholds (e.g. `min_usage_count`, `min_confidence`). Promotion may assign a canonical_id from a later authority lookup or from a minted ID scheme. See kgschema `PromotionConfig` and kgraph `PromotionPolicy`.

## Helper utilities

- `extract_canonical_id_from_entity`, `check_entity_id_format` (kgraph canonical_id helpers) for parsing and validating ID strings.
- Use the same ID scheme as your authority (e.g. UMLS CUI, HGNC symbol) so the graph stays interoperable.

# Architecture Overview

## Two-Pass Ingestion Pipeline

The framework processes documents in two passes:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│  Raw Docs   │────▶│   Parser    │────▶│  BaseDocument   │
└─────────────┘     └─────────────┘     └────────┬────────┘
                                                 │
                        ┌────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────┐
│                      PASS 1                             │
│  ┌─────────────────┐     ┌──────────────────┐           │
│  │ Entity Extractor│────▶│  Entity Resolver │           │
│  └─────────────────┘     └────────┬─────────┘           │
│         │                         │                     │
│         ▼                         ▼                     │
│  EntityMention[]           BaseEntity[]                 │
│                            (canonical or provisional)   │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                      PASS 2                             │
│  ┌───────────────────────┐                              │
│  │ Relationship Extractor│                              │
│  └───────────┬───────────┘                              │
│              │                                          │
│              ▼                                          │
│       BaseRelationship[]                                │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
                ┌───────────────┐
                │    Storage    │
                └───────────────┘
```

### Pass 1: Entity Extraction

1. **EntityExtractor** scans documents and produces `EntityMention` objects (raw text spans with type classifications)
2. **EntityResolver** maps mentions to existing canonical entities or creates provisional entities
3. **EmbeddingGenerator** creates semantic vectors for new entities
4. Entities are stored with usage counts incremented for duplicates

### Pass 2: Relationship Extraction

1. **RelationshipExtractor** identifies connections between entities found in Pass 1
2. Relationships are validated against the domain schema
3. Stored relationships link to entity IDs

## Entity Lifecycle

```
                 ┌──────────────┐
                 │   Mention    │
                 │ (text span)  │
                 └──────┬───────┘
                        │ resolve
                        ▼
          ┌─────────────────────────┐
          │                         │
          ▼                         ▼
┌─────────────────┐      ┌─────────────────┐
│   Provisional   │      │    Canonical    │
│    Entity       │      │     Entity      │
└────────┬────────┘      └─────────────────┘
         │                        ▲
         │ promote (when          │
         │ thresholds met)        │
         └────────────────────────┘
```

### Promotion Criteria

Provisional entities are promoted to canonical when they meet thresholds defined in `PromotionConfig`:

- `min_usage_count`: Minimum number of document appearances
- `min_confidence`: Minimum confidence score from extraction
- `require_embedding`: Whether embedding must be present

### Entity Merging

When canonical entities are detected as duplicates (via embedding similarity), they can be merged:

1. Synonyms and usage counts are combined
2. All relationship references are updated to point to the target entity
3. Source entities are removed

## Canonical ID System

The framework provides abstractions for working with canonical IDs (stable identifiers from authoritative sources):

- **`CanonicalId`**: Pydantic model representing a canonical identifier with ID, URL, and synonyms
- **`CanonicalIdCacheInterface`**: Abstract interface for caching canonical ID lookups
- **`CanonicalIdLookupInterface`**: Abstract interface for looking up canonical IDs
- **Helper functions**: Utilities for extracting canonical IDs from entities (`extract_canonical_id_from_entity`, `check_entity_id_format`)

Promotion policies use these abstractions to assign canonical IDs to entities. See [Canonical IDs and Entity Resolution](canonical-ids-and-entity-resolution.md) for details.

## Major Components and How They Relate

| Component | Role |
|-----------|------|
| **kgschema** | Data structures and ABCs only (entities, relationships, documents, domain, storage). No runtime logic. |
| **kgraph** | Ingestion pipeline: orchestrator, promotion, export, canonical_id lookup, in-memory storage, pipeline interfaces. |
| **kgbundle** | Lightweight Pydantic models for bundle exchange; used by both kgraph (producer) and kgserver (consumer). |
| **kgserver** | Query server: loads bundles, exposes REST, GraphQL, MCP; PostgreSQL/SQLite backends; optional Chainlit chat UI. |
| **examples** | Domain implementations (medlit, sherlock) and medlit_schema: concrete schemas, parsers, extractors, scripts. |

Data flow: **Documents** → kgraph pipeline (using kgschema types and domain from examples) → **bundle** (kgbundle format) → **kgserver** loads bundle and serves queries.

## Module Structure

The codebase is organized into these packages:

### kgschema/ (Data Structure Definitions)

Submodule within kgraph containing only Pydantic models and ABC interfaces, no functional code:

```
kgschema/
├── entity.py              # BaseEntity, EntityStatus, EntityMention, PromotionConfig
├── relationship.py        # BaseRelationship
├── document.py            # BaseDocument
├── domain.py              # DomainSchema ABC
└── storage.py             # Storage interface ABCs
```

### kgbundle/ (Bundle Exchange Models)

Separate lightweight package with minimal dependencies (pydantic only):

```
kgbundle/
├── models.py              # EntityRow, RelationshipRow, BundleManifestV1
└── pyproject.toml         # Standalone package configuration
```

Used by both kgraph (producer) and kgserver (consumer) for bundle file exchange.

### kgraph/ (Main Framework)

Functional code implementing the ingestion pipeline:

```
kgraph/
├── ingest.py              # IngestionOrchestrator
├── promotion.py           # PromotionPolicy ABC
├── export.py              # Bundle export functionality
├── builders.py            # Builder utilities
├── canonical_id/          # Canonical ID system
│   ├── models.py          # CanonicalId model, CanonicalIdCacheInterface ABC
│   ├── json_cache.py      # JsonFileCanonicalIdCache implementation
│   ├── lookup.py          # CanonicalIdLookupInterface ABC
│   └── helpers.py         # Helper functions for promotion policies
├── storage/               # Storage implementations
│   └── memory.py          # In-memory storage
└── pipeline/              # Pipeline component interfaces
    ├── interfaces.py      # Parser, Extractor, Resolver ABCs
    └── embedding.py       # EmbeddingGeneratorInterface
```

### kgserver/ (Query Server)

FastAPI app that loads a bundle and exposes:

- REST: entities, relationships
- GraphQL + GraphiQL
- MCP server for LLM/agent tooling
- Optional Chainlit chat UI at `/chat`
- Graph visualization

Storage backends: PostgreSQL, SQLite. Producer (kgraph) and consumer (kgserver) share the kgbundle schema so the bundle is the contract.

### examples/

- **medlit** — Medical literature: JATS/PMC parser, LLM extraction, authority lookup (UMLS, etc.), dedup, bundle build. Reference implementation.
- **medlit_schema** — Domain schema (entities, relationships, documents) for medlit.
- **sherlock** — Simpler literary example (characters, stories, co-occurrence) showing framework generality.

## Immutability

All data models (entities, relationships, documents) are immutable Pydantic models with `frozen=True`. This ensures:

- Thread safety for concurrent access
- Clear data flow (updates create new instances)
- Predictable behavior in storage operations

Use `model_copy(update={...})` to create modified copies:

```python
updated_entity = entity.model_copy(update={"usage_count": entity.usage_count + 1})
```

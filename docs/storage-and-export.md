# Storage and Export

## In-memory storage

The framework provides in-memory implementations of the kgschema storage interfaces (`EntityStorageInterface`, `RelationshipStorageInterface`, etc.) in `kgraph/storage/memory.py`. Use them for tests and single-process pipelines. They support the full entity lifecycle: add, resolve, promote, merge, and relationship CRUD.

## Bundle format

The **bundle** is the exchange format between producer (kgraph/pipeline) and consumer (kgserver). It is defined by the **kgbundle** package (Pydantic models: `BundleManifestV1`, `EntityRow`, `RelationshipRow`, `DocAssetRow`).

- **manifest.json** — Version, bundle_id, domain, paths to entities/relationships/doc_assets, metadata (counts, description).
- **entities.jsonl** — One JSON object per line: entity_id, entity_type, name, status, confidence, usage_count, created_at, source, properties.
- **relationships.jsonl** — subject_id, object_id, predicate, confidence, source_documents, created_at, properties.

Bundles are read-only for the server; the server validates and loads them at startup. Producer pipelines are responsible for flattening fields and using stable IDs.

## Export

kgraph’s **export** module writes entities and relationships from storage into the bundle layout (manifest + JSONL files). Domain pipelines (e.g. medlit’s pass3_build_bundle) orchestrate storage → export → zip or directory.

## Query interface

Once a bundle is loaded, **kgserver** exposes:

- **REST** — GET /api/v1/entities, /api/v1/relationships (with limit, filter).
- **GraphQL** — POST /graphql; schema exposes entities, relationships, and graph traversal (e.g. find within N hops).
- **MCP** — Tools for LLM/agent use: entity search, relationship lookup, traversal.

Storage backends for the server: PostgreSQL, SQLite. The query layer is the same; the backend is chosen by configuration (e.g. DATABASE_URL).

# Overview

This codebase is a **domain-agnostic knowledge graph framework** for extracting entities and relationships from unstructured text. It addresses the core problem: turning documents (papers, legal text, reports) into a queryable graph with canonical identities and provenance.

For the conceptual foundation — why knowledge graphs, why extraction from text, and why this approach — see the book **[*Knowledge Graphs from Unstructured Text*](https://github.com/wware/kg-book)** (kg-book). The technical docs here describe how the framework is built and how to use or extend it.

## What this repo does

- **Two-pass ingestion**: Pass 1 extracts entities and resolves them to canonical or provisional IDs; Pass 2 extracts relationships between those entities.
- **Pluggable domains**: Each domain (medical literature, legal, literary, etc.) defines its own schema (entity types, relationship types, documents) and pipeline components.
- **Canonical identity**: Entities can be tied to external authorities (e.g. UMLS, RxNorm for medicine) or remain provisional until promotion rules are met.
- **Bundle export**: Pipelines produce a validated bundle (entities, relationships, manifest) that the query server loads read-only.

## Where to go next

- [Architecture](architecture.md) — Components and how they relate.
- [Schema Design Guide](schema-design-guide.md) — Define your domain with kgschema.
- [The Pipeline](pipeline.md) — Parsing, extraction, dedup, resolution, bundle building.
- [Adapting to Your Domain](adapting-to-your-domain.md) — Step-by-step guide to add a new domain.

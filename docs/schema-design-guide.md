# Schema Design Guide

This guide describes how to define your domain's entities, relationships, and documents using **kgschema**. The schema is the contract between your pipeline and the framework.

## Domain schema (ABC)

Implement `DomainSchema` from `kgschema.domain` to declare entity types, relationship types, and document types:

- **Entity types** — Map type names to `BaseEntity` subclasses (e.g. `"drug"` → `DrugEntity`).
- **Relationship types** — Map predicate names to `BaseRelationship` subclasses.
- **Document type** — The `BaseDocument` subclass for your input docs.

Your domain also defines promotion config (thresholds for provisional → canonical) and any domain-specific validation.

### Why Python, not YAML

The domain spec is a Python module (`domain_spec.py`), not a config file. This was a
deliberate choice over a YAML schema:

- Entity class and its metadata sit next to each other, so they cannot drift apart.
- `subject_types`/`object_types` reference the classes themselves, not strings that have to
  be resolved and validated later.
- There is no parsing layer to maintain — the spec *is* the schema.
- Pydantic validates it at import time, so a malformed spec fails immediately.

Consumers that cannot import Python (e.g. the graph-viz frontend) are served by exporting the
relevant slice to JSON as a build step, rather than by making the source format weaker.

## Entities

- Subclass `BaseEntity` from `kgschema.entity`.
- Implement `get_entity_type()` (and any required fields).
- Use `EntityStatus`: `canonical` (has stable ID) or `provisional`.
- Optionally use `PromotionConfig` to control when provisionals are promoted.

Decide what gets to be a node: only things you want to query and link. Keep property blobs minimal; put domain-specific data in a `properties` dict if the framework allows it.

## Relationships

- Subclass `BaseRelationship` from `kgschema.relationship`.
- Relationships are directed: subject → predicate → object.
- Define predicates that are precise enough to be useful (e.g. `inhibits`, `treats`) and that your extractors can reliably produce.

Avoid overloading one predicate (e.g. "associated_with") for many meanings; split by semantics when it affects querying or reasoning.

## Documents

- Subclass `BaseDocument` from `kgschema.document`.
- The document type is what your parser produces and what the pipeline consumes.
- Include enough structure (sections, chunks) so that extraction and provenance can reference specific spans.

## Provenance

Design provenance into the schema from the start: source document, section, extraction method, confidence. The framework and kgbundle support source tracking so relationships can be traced back.

## Examples

- **medlit_schema** — Defines biomedical entity and relationship types for the medical literature example.
- **sherlock** — Defines character, story, location and predicates like `appears_in`, `co_occurs_with`.

See [Adapting to Your Domain](adapting-to-your-domain.md) for a step-by-step workflow and [The medlit Example](examples/medlit.md) for an annotated schema.

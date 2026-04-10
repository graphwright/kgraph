# Schema Design Guide

> **Placeholder** — content to be migrated and expanded from
> [`../schema-design-guide.md`](../schema-design-guide.md).

This guide describes how to define your domain's entities, relationships, and documents
using **kgschema**.

## Domain schema

Implement `DomainSchema` from `kgschema.domain` to declare:

- **Entity types** — map type names to `BaseEntity` subclasses.
- **Relationship types** — map predicate names to `BaseRelationship` subclasses.
- **Document type** — the `BaseDocument` subclass for your input format.
- **Promotion config** — thresholds for provisional → canonical promotion.

## Entities

- Subclass `BaseEntity`.
- Implement `get_entity_type()`.
- Use `EntityStatus`: `canonical` or `provisional`.
- All fields must have `description=` strings (enforced by convention).

## Relationships

- Subclass `BaseRelationship`.
- Declare `subject_type` and `object_type` to constrain valid endpoints.
- Include a `predicate` field with a controlled vocabulary from your domain.

## Documents

- Subclass `BaseDocument`.
- Include fields for document metadata: identifier, title, publication date, source.
- The parser produces one `BaseDocument` per input file.

## Immutability

Schema models should use `model_config = ConfigDict(frozen=True)`. This prevents
accidental mutation and makes models safe to use as dict keys or in sets.

## See also

- [Adapting to Your Domain](adapting-to-your-domain.md)
- [Pipeline](../ingestion/pipeline.md)

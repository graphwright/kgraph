# Adapting to Your Domain

Step-by-step guide to add a new domain to the framework: define your schema, write extraction prompts, configure your pipeline, and validate output.

## 1. Define your schema

- **Entity types** — What gets a node? Subclass `BaseEntity` for each type; register in your `DomainSchema.entity_types`.
- **Relationship types** — Which predicates? Subclass `BaseRelationship`; register in `DomainSchema.relationship_types`.
- **Document type** — Subclass `BaseDocument` for your input format (e.g. JATS for articles, plain sections for stories).
- **Provenance** — Include source document, section, and confidence in your relationship and evidence models so the graph stays traceable.

See [Schema Design Guide](schema-design-guide.md). Use **medlit_schema** or **sherlock** as references.

## 2. Write extraction prompts

If you use an LLM for extraction:

- Bind your **entity types** and **relationship types** in natural language so the model knows the allowed vocabulary.
- Handle hedging and negation explicitly (e.g. "did not inhibit" → no relationship or low confidence).
- Ask for provenance (source span, confidence) in the same pass.
- Iterate on the prompt; test on a small corpus before scaling.

The medlit pipeline uses structured prompts in `pass1_extract` and relationship extraction; see [The medlit Example](examples/medlit.md).

## 3. Configure your pipeline

- **Parser** — Implement or reuse a parser that produces your `BaseDocument` (e.g. JATS XML → medlit document with sections).
- **Chunking** — If documents are long, chunk by section or sentence so each piece fits model limits; keep boundaries so provenance can point to sections.
- **Entity extractor** — LLM or NER; output `EntityMention` with type and confidence.
- **Resolver** — Use a synonym cache and optional authority lookup (e.g. UMLS) to map mentions to canonical or provisional entities.
- **Dedup** — Merge duplicate entities (e.g. by embedding similarity or name normalization) before or during resolution.
- **Relationship extractor** — Input: document + resolved entities; output: `BaseRelationship` list with subject_id, object_id, predicate, provenance.
- **Bundle builder** — Write entities and relationships to the kgbundle format (manifest + JSONL); run export from your storage.

Wire these in a script or orchestrator (e.g. medlit’s pass1 → pass2 → pass3). See [The Pipeline](pipeline.md) and [Storage and Export](storage-and-export.md).

## 4. Validate output

- **Schema** — Ensure every entity and relationship conforms to your domain schema (types, required fields).
- **IDs** — Canonical IDs must match the authority format; provisionals should have a unique, stable placeholder ID.
- **Bundle** — Validate against kgbundle models; load a test bundle in kgserver and run a few REST/GraphQL queries.
- **Provenance** — Spot-check that source document and (if applicable) section are present and correct.

Add unit tests for parser, extractor, resolver, and bundle build; use the in-memory storage for fast tests. See [Contributing](contributing.md) for testing approach.

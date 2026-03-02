# The Sherlock Example

A **simpler, literary contrast case** that shows the framework’s generality. It ingests Sherlock Holmes stories (e.g. from Project Gutenberg), extracts characters, locations, and stories, and builds relationships such as `appears_in` and `co_occurs_with`. No biomedical authorities — a good template for non-medical domains.

## Schema

- **Documents**: Plain text or structured story documents (BaseDocument).
- **Entities**: Character, location, story; entity_id can be domain-minted (e.g. `holmes:char:SherlockHolmes`).
- **Relationships**: `appears_in` (character → story), `co_occurs_with` (character ↔ character), etc.
- **Domain**: DomainSchema defines the types and predicates; promotion config can be minimal (e.g. single use → canonical).

## Pipeline

1. **Parser** — Fetch or read Gutenberg text; produce a document per story (or chunk).
2. **Entity extraction** — LLM or rule-based: identify characters, locations, story titles.
3. **Resolution** — Map mentions to canonical or provisional entities (no external authority; IDs minted by domain).
4. **Relationship extraction** — Who appears in which story; who co-occurs with whom.
5. **Export** — Write bundle (manifest + entities.jsonl + relationships.jsonl) for kgserver.

## Code layout

- `examples/sherlock/domain.py` — Domain schema and entity/relationship types.
- `examples/sherlock/pipeline/` — Parser, extractors, resolver (and optional embeddings).
- `examples/sherlock/sources/gutenberg.py` — Fetching Gutenberg content.
- `examples/sherlock/data.py` — Data helpers if needed.

## Why it’s useful

- **No external APIs** — Good for local runs and demos.
- **Small corpus** — Fast iteration on schema and prompts.
- **Same patterns** — DomainSchema, pipeline interfaces, bundle export; reuse the same ideas for legal, financial, or other domains.

Use medlit for authority-backed, production-style ingestion; use Sherlock for learning and for domains without a single canonical ID source.

# The medlit Example

Annotated walkthrough of the **medical literature** reference implementation. It ingests biomedical journal articles (e.g. PMC/JATS XML), extracts entities (diseases, genes, drugs, etc.) and relationships (treats, causes, associated_with, etc.), resolves to canonical IDs (UMLS, HGNC, RxNorm, UniProt), and produces a bundle for kgserver.

## Schema (medlit_schema)

Entity types, predicates, and prompt instructions are defined in **`domain_spec.py`** (single source of truth). The extraction prompt, validation, and dedup all consume it.

- **Documents**: `JournalArticle` (BaseDocument) with paper_id, metadata, extraction provenance.
- **Entities**: DiseaseEntity, GeneEntity, DrugEntity, ProteinEntity, and others; entity_id uses authority IDs (UMLS:C..., HGNC:..., RxNorm:..., UniProt:...).
- **Relationships**: `MedicalClaimRelationship` with predicate (treats, causes, increases_risk, associated_with, interacts_with, etc.), evidence and source_documents in metadata.
- **Domain**: MedLitDomainSchema defines entity/relationship types and promotion config (e.g. min_usage_count=2, min_confidence=0.75).

## Pipeline

1. **Parsing** — JATS/PMC XML or JSON → `JournalArticle`; section boundaries for chunking.
2. **Chunking** — By section/sentence so each chunk fits the LLM context; see `pmc_chunker`, `extract`.
3. **extract (entity extraction)** — LLM extracts entity mentions; optional fetch_vocab run to seed a shared synonym list and reduce cross-paper duplication.
4. **Authority lookup** — Resolve mentions to canonical IDs via UMLS, HGNC, RxNorm, UniProt (see `authority_lookup`, `synonym_cache`).
5. **Dedup** — Merge duplicate entities (e.g. by synonym cache and embedding similarity) in ingest.
6. **ingest (relationship extraction)** — Extract relationships between resolved entities; aggregate source_documents across papers.
7. **Bundle build** — Export entities and relationships to kgbundle format (manifest + entities.jsonl + relationships.jsonl); optional doc_assets for documentation.

## Scripts

- `extract.py` — Run extract over an input dir of XML/JSON papers; writes per-paper or combined entity/mention output.
- `fetch_vocab.py` — Optional vocabulary pass to seed synonym cache and validate types (e.g. UMLS semantic types).
- `ingest.py` — Deduplicate entities and merge relationships.
- `build_bundle.py` — Build final bundle (manifest + JSONL) for kgserver.

## Configuration

- LLM provider (Anthropic, OpenAI, Ollama) and model via env or config.
- Input/output dirs, synonym cache path, authority API keys (e.g. UMLS) as needed.
- See the scripts under `medlit/medlit/scripts/` for CLI flags and env vars.

## Tests

Tests live under `medlit/tests/` and `medlit/domain_service/tests/`. Run them from the `medlit`
directory so uv uses that package's own environment:

```bash
cd medlit && uv run pytest
```

Or run the full package check (linters plus tests) with `medlit/lint.sh`.

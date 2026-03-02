# The medlit Example

Annotated walkthrough of the **medical literature** reference implementation. It ingests biomedical journal articles (e.g. PMC/JATS XML), extracts entities (diseases, genes, drugs, etc.) and relationships (treats, causes, associated_with, etc.), resolves to canonical IDs (UMLS, HGNC, RxNorm, UniProt), and produces a bundle for kgserver.

## Schema (medlit_schema)

- **Documents**: `JournalArticle` (BaseDocument) with paper_id, metadata, extraction provenance.
- **Entities**: DiseaseEntity, GeneEntity, DrugEntity, ProteinEntity, and others; entity_id uses authority IDs (UMLS:C..., HGNC:..., RxNorm:..., UniProt:...).
- **Relationships**: `MedicalClaimRelationship` with predicate (treats, causes, increases_risk, associated_with, interacts_with, etc.), evidence and source_documents in metadata.
- **Domain**: MedLitDomainSchema defines entity/relationship types and promotion config (e.g. min_usage_count=2, min_confidence=0.75).

## Pipeline

1. **Parsing** — JATS/PMC XML or JSON → `JournalArticle`; section boundaries for chunking.
2. **Chunking** — By section/sentence so each chunk fits the LLM context; see `pmc_chunker`, `pass1_extract`.
3. **Pass 1 (entity extraction)** — LLM extracts entity mentions; optional Pass 1a vocabulary run to seed a shared synonym list and reduce cross-paper duplication.
4. **Authority lookup** — Resolve mentions to canonical IDs via UMLS, HGNC, RxNorm, UniProt (see `authority_lookup`, `synonym_cache`).
5. **Dedup** — Merge duplicate entities (e.g. by synonym cache and embedding similarity) in Pass 2.
6. **Pass 2 (relationship extraction)** — Extract relationships between resolved entities; aggregate source_documents across papers.
7. **Bundle build** — Export entities and relationships to kgbundle format (manifest + entities.jsonl + relationships.jsonl); optional doc_assets for documentation.

## Scripts

- `pass1_extract.py` — Run Pass 1 over an input dir of XML/JSON papers; writes per-paper or combined entity/mention output.
- `pass1a_vocab.py` — Optional vocabulary pass to seed synonym cache and validate types (e.g. UMLS semantic types).
- `pass2_dedup.py` — Deduplicate entities and merge relationships.
- `pass3_build_bundle.py` — Build final bundle (manifest + JSONL) for kgserver.

## Configuration

- LLM provider (Anthropic, OpenAI, Ollama) and model via env or config.
- Input/output dirs, synonym cache path, authority API keys (e.g. UMLS) as needed.
- See `examples/medlit` README and scripts for CLI flags and env vars.

## Tests

Tests live under `examples/medlit/tests/` (e.g. authority_lookup, pass1_extract, pass3_bundle_builder, two_pass_ingestion). Run from repo root: `uv run pytest examples/medlit/tests/`.

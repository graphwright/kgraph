# Ingestion Pipeline — Remaining Work

Remaining work on the ingestion pipeline, plus known data-quality defects.

---

## Phase E: Chunking and per-chunk extraction (higher risk)

### E1: Add chunking module

- Create `kgraph/pipeline/chunker.py` or extend `medlit/medlit/pipeline/pmc_chunker.py`
- Input: document text, section boundaries
- Output: list of chunks with overlap (e.g. 512 tokens, 64 overlap)
- Each chunk: `{chunk_id, text, section, start_offset, end_offset}`

### E2: Per-chunk entity extraction

- Parse document → chunks
- For each chunk: call LLM with entity extraction template
- Merge entities by (name, type) across chunks within document
- Output: per-document bundle with deduplicated entities

### E3: Per-chunk relationship extraction

- After entity resolution within document, for each chunk: call LLM with relationship template
- Merge relationships by (sub, pred, obj) across chunks
- Accumulate provenance (chunk_id, section, sentence) per occurrence

**Sequencing:** Study design (D2) stays per-paper; do not move it to per-chunk when E lands.

---

## Phase F: Abstract pre-pass and citation integration (deferred)

- Phase 0 abstract pre-pass for claim hierarchy
- JATS reference list parsing
- Citation marker parsing in prompts
- Claim hierarchy data model

**Status:** Documented as future work. Not in initial execution scope.

---

## Schema Gaps

- **Missing `organism`/`species` entity type**: Non-human organisms (e.g. chimpanzees, *H. pylori*) appearing in comparative genomics or evolutionary medicine papers get misclassified into the nearest available biomedical category (typically `anatomicalstructure`). Add an `organism` or `species` type to `domain_spec.py` and the extraction prompts. The DBPedia canonical URL resolver also goes rogue on these (e.g. "Chimpanzees" → `DBPedia:Chimpanzees'_tea_party`), so the authority lookup blocklist or DBPedia matching may also need tuning for organism names.

## Known Defects

Verified against `bundle/` output regenerated 2026-03-27. Both were identified during the
graph data-quality review; the other two items from that review (CITES extraction from
`<ref-list>`, and ROR/grid identifiers corrupting institution names) are fixed.

### Mentions have no positional metadata

Every mention record in `mentions.jsonl` has `section: null` and `start_offset: 0` (6,249 of
6,249). Section name and character offset are dropped somewhere between extraction and bundle
assembly — likely in `medlit/medlit/scripts/extract.py` or the mention construction in
`bundle_builder.py`. This defeats traceability back to source text, and undercuts the
`get_mentions` MCP diagnostic tool, which exists so mentions can be checked against the
original passage.

### Self-loop relationships

`relationships.jsonl` contains 9 relationships where `subject_id == object_id`. These are
nonsensical and should be dropped at write time in `bundle_builder.py`, with a test asserting
no self-loops in bundle output. (An earlier count found 2, so this is growing.)

## Known Limitations

- **LLM JSON reliability**: `json-repair` fallback is in place. If problems persist: add closing reminders to prompts, use response prefilling, flatten nested schemas, or split large calls.
- **ORCID coverage**: Authors without `<contrib-id contrib-id-type="orcid">` XML tags fall back to ORCID name search (single unambiguous result only). Common names will not resolve.

## Operations

See `OPERATIONS.md` for redeploy, force-reload, and batch ingestion procedures.

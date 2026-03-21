# Ingestion Pipeline — Remaining Work

Items left from PLAN2.md after the initial implementation. See PLAN2.md and ingestion_redesign.md for full details.

---

## Phase E: Chunking and per-chunk extraction (higher risk)

### E1: Add chunking module

- Create `kgraph/pipeline/chunker.py` or extend `examples/medlit/pipeline/pmc_chunker.py`
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

## Known Limitations

- **LLM JSON reliability**: `json-repair` fallback is in place. If problems persist: add closing reminders to prompts, use response prefilling, flatten nested schemas, or split large calls.
- **ORCID coverage**: Authors without `<contrib-id contrib-id-type="orcid">` XML tags fall back to ORCID name search (single unambiguous result only). Common names will not resolve.

## Operations

See `OPERATIONS.md` for redeploy, force-reload, and batch ingestion procedures.

# Ingestion Pipeline — Remaining Work

Items left from PLAN2.md after the initial implementation. See PLAN2.md and ingestion_redesign.md for full details.

---

## Phase D (remaining)

### D2: Study design trust signal (per-paper) ✅ **DONE**

- **Created** `StudyDesignMetadata` model in `examples/medlit/bundle_models.py`:
  - Fields: `study_type`, `sample_size`, `multicenter`, `held_out_validation`
- **Modified** Pass 1b (`pass1_extract`): second LLM call per paper after main extraction
  - Structured prompt against Methods section (and abstract if needed)
  - Returns the four fields above
- **Storage:** Attach to paper-level node in bundle. Pass 3 output includes `study_design` on paper metadata.

### D3: Provenance list structure ✅ **DONE**

- **Modified** bundle models and Pass 3 output:
  - Relationship record: `ProvenanceEntry` with `section`, `sentence`, `citation_markers`; `RelationshipRow.provenance` list
  - Dedup accumulates provenance from evidence per (sub, pred, obj)
- **Acceptance:** Schema supports multiple provenance records per relationship. Pass 3 emits it in `properties["provenance"]` when available.

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

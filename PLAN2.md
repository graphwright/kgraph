# Plan 2: Medlit Entity Deduplication Fixes

Plan for addressing entity duplication and provenance noise in the medlit pipeline. **Do not execute yet** — this is a planning document. Work can proceed without supervision once approved.

---

## Summary of Issues

| # | Issue | Root Cause | Fix Location |
|---|-------|------------|--------------|
| 1 | Multi-namespace duplicate genes (tp53, brca1, slc7a11) | `_authoritative_id_from_entity` picks one ID; merge key = that ID; name-based index only catches entities *without* authoritative ID | `dedup.py` |
| 2 | Symmetric synonym pollution (STAT3 ↔ signal transducer...) | LLM emits both symbol and full name; `lookup_entity` only resolves by name; low-confidence SAME_AS leaves both alive | `dedup.py`, `synonym_cache.py` |
| 3 | 128 provisional `canon-` entities | No embedding-based dedup at merge time; different phrasings never collide | `dedup.py` |
| 4 | PMC_UNKNOWN / PMC_extracted provenance noise | Synthetic IDs from fallback/LLM end up in `supporting_documents` | `bundle_builder.py`, optionally `pass1_extract.py` |
| 5 | Zero-mention orphans (liproxstatin-1, vitamin E, atezolizumab) | Entities in relationships but never in `evidence_ids` → `usage_count=0` | `bundle_builder.py` |
| 6 | Cross-type provisional duplicates (e.g., "homologous recombination deficiency" as biomarker vs disease) | Reconciliation groups by `(name, entity_class)`; embedding pass groups by `entity_class` — neither catches same concept with different types | `dedup.py` |

**Priority:** Issue 2 (synonym indexing) is highest leverage — it addresses both synonym pollution and some multi-namespace duplicates. Issue 1 (namespace normalization) is second.

---

## 1. Synonym-Indexed Lookup in Pass 2 (Highest Leverage)

**Goal:** When building the name/type index in `_run_pass2_impl`, also index entities by all synonyms. If entity A's name matches entity B's synonym (or vice versa), treat as merge candidate.

**Files:**
- `examples/medlit/pipeline/dedup.py`
- `examples/medlit/pipeline/synonym_cache.py` (if extending cache structure)

**Steps:**

1. **Extend the index** in `_run_pass2_impl`:
   - Current: `name_type_to_canonical` maps `(name.lower(), entity_class)` → merge key.
   - Change: Populate this same dict with *both* primary names and synonyms. When adding entity A, insert `(a.lower(), entity_class) -> cid` for `a` in `{A.name} | set(A.synonyms)`.

2. **When assigning canonical ID in `get_or_assign_canonical`:**
   - Check `name_type_to_canonical` for `(name.lower(), entity_class)` first. If hit, merge to that canonical (this now catches both name matches and synonym matches, since synonyms are in the same dict).
   - Then authoritative ID, cache lookup, etc.
   - When assigning a new canonical, insert `(n.lower(), entity_class) -> cid` for `n` in `{name} | set(synonyms)`.

3. **Order of operations:** Process entities in deterministic order (e.g., `(paper_id, e.id)`). For each entity, the index already contains names and synonyms of all previously processed entities. A new entity whose name equals a prior entity's synonym will hit the index and merge.

4. **Explicit scope: name↔synonym only, not synonym→synonym.** When entity A (paper 1) has synonym "signal transducer and activator of transcription 3" and entity B (paper 2) has that as its primary name, we merge (B.name matches A.synonym). But if entity C (paper 2) has *STAT3* as a synonym on the same row as B, we do *not* merge A and C via A.synonym == C.synonym. **Decision:** Only trigger merge when the *incoming* entity's primary name matches an already-indexed name or synonym. Do not index synonym→synonym matches — that would over-merge (e.g., two unrelated entities that both list "cancer" as a synonym). Implementation: when checking the index, only use the incoming entity's `name`, not its synonyms, as the lookup key. When populating the index, add both name and synonyms. So we match incoming-name against (prior-name ∪ prior-synonyms), but never incoming-synonym against prior-synonym.

5. **Cache interaction:** `lookup_entity` in synonym_cache is keyed by normalized name. The extended index is in-memory only for this run; no change to cache schema.

6. **Tests:** Add `examples/medlit/tests/test_dedup.py` (or extend existing) with tests that:
   - Two entities with A.name == B.synonym (same class) merge to one canonical.
   - Two entities with A.synonym == B.name (same class) merge to one canonical.
   - Different entity classes with same name/synonym do not merge.

---

## 2. Namespace Normalization for Genes (UMLS → HGNC)

**Goal:** Ensure `tp53` with C0079419 (UMLS only, paper 1) and `tp53` with HGNC:11998 (HGNC only, paper 2) collapse to one merge key. In the observed dataset, no single row has both IDs — the duplicates are cross-paper. Intra-row normalization (prefer HGNC when both exist) helps but is insufficient; cross-paper UMLS→HGNC resolution is **required**.

**Files:**
- `examples/medlit/pipeline/dedup.py`
- `examples/medlit/pipeline/authority_lookup.py` (for UMLS→HGNC mapping if needed)

**Steps:**

1. **Add `_preferred_authoritative_id(e: ExtractedEntityRow) -> Optional[str]`** in `dedup.py`:
   - For `entity_class == "Gene"`: if both `umls_id` and `hgnc_id` present, return `hgnc_id` (or `HGNC:{hgnc_id}` if numeric). Otherwise return first authoritative from `(canonical_id, hgnc_id, umls_id, ...)`.
   - For other classes: keep current `_authoritative_id_from_entity` behavior (first match in canonical_id, umls_id, hgnc_id, rxnorm_id, uniprot_id).
   - Reuse `_is_authoritative_id` for validation.

2. **Replace `_authoritative_id_from_entity`** with `_preferred_authoritative_id` in `get_or_assign_canonical` (or refactor so the preferred logic is the single source of truth).

3. **Required: UMLS→HGNC cross-lookup for entities with only `umls_id`.** When a Gene entity has `umls_id` but no `hgnc_id`, resolve UMLS CUI to HGNC. **Implementation decision:** Use UMLS REST API `GET /rest/content/current/CUI/{cui}` to fetch concept atoms, extract the preferred gene symbol (or first atom name), then call `_lookup_hgnc(symbol)` — `CanonicalIdLookup._lookup_hgnc` takes a term, not a CUI, so the CUI→symbol step is required. Add `_lookup_hgnc_by_cui(cui)` in `authority_lookup.py` that does this two-step. Cache results to avoid repeated API calls. Fallback: if UMLS returns no usable symbol, keep entity as UMLS-only for that run (no merge). This is required for Issue 1 to fix the observed tp53/brca1/slc7a11 duplicates.

4. **Tests:** Add test that two Gene entities with same name, one with `umls_id` only and one with `hgnc_id` only, merge after UMLS→HGNC resolution. And that same name + both IDs on one row uses HGNC.

---

## 3. Post-Dedup Reconciliation by (normalized_name, entity_class)

**Goal:** After the primary merge, group surviving entities by `(normalized_name, entity_class)` and emit `SAME_AS` for any group with >1 member. This catches multi-namespace duplicates that slip through (e.g., different papers assign different IDs to the same concept).

**Files:**
- `examples/medlit/pipeline/dedup.py`

**Steps:**

1. **After step 5 in `_run_pass2_impl`** (after building `canonical_entities`), add a reconciliation pass:
   - Build `by_name_class: dict[tuple[str, str], list[str]]` mapping `(name.lower(), entity_class)` → list of `entity_id` (merge keys).
   - For each group with `len(ids) > 1`:
     - Pick a winner (prefer authoritative ID; otherwise first by deterministic sort).
     - Merge all others into winner: update `local_to_canonical`, `name_type_to_canonical`, `canonical_entities`, and `triple_to_rel` to replace loser IDs with winner.
     - Call `add_same_as_to_cache` for each pair (winner, loser).

2. **Triple rewrite and merge-on-collision:** `triple_to_rel` is keyed by `(subject_id, predicate, object_id)`. When merging B into A:
   - For each triple where B is subject or object, create a new key with B replaced by A (e.g., `(B, pred, C)` → `(A, pred, C)`).
   - **Merge-on-collision:** If the renamed key already exists (e.g., both A→C and B→C with the same predicate), merge the two `RelationshipRow` records: union `evidence_ids`, union `source_papers`, take `max(confidence)`. Do not silently drop one record.
   - Delete the old key(s) that referenced B.
   - Merge `canonical_entities[B]` into `canonical_entities[A]` (combine synonyms, source_papers).
   - Avoid redundant SAME_AS edges in `triple_to_rel`.

3. **Tests:** Two entities with same normalized name and class but different authoritative IDs end up as one after reconciliation.

---

## 4. Embedding-Based Dedup for Provisional Entities

**Goal:** After the name-based merge, run an embedding similarity pass over provisional (`canon-`) entities. Merge pairs above a threshold.

**Files:**
- `examples/medlit/pipeline/dedup.py`
- `examples/medlit/scripts/pass2_dedup.py` (to pass `embedding_generator` if needed)
- `kgraph/pipeline/embedding.py` or equivalent

**Steps:**

1. **Add optional `embedding_generator` and `similarity_threshold`** to `run_pass2` and `_run_pass2_impl`. Default `embedding_generator=None` so Pass 2 remains runnable without embeddings.

2. **After name-based merge and reconciliation**, collect all provisional entities: `[e for e in canonical_entities.values() if e["entity_id"].startswith("canon-")]`.

3. **For each pair (A, B) of same `entity_class`**:
   - Compute embedding for A.name and B.name (and optionally representative synonym).
   - Cosine similarity; if >= threshold, merge B into A (same logic as reconciliation).

4. **Threshold calibration:** Do not use a magic number. For short biomedical noun phrases, 0.92 with `nomic-embed-text` may be too tight — e.g., "homologous recombination deficiency" vs "HRD" might score ~0.85. Before committing to a value: (a) sample provisional entity pairs from the corpus, (b) compute similarity distribution, (c) manually inspect pairs at candidate thresholds (e.g., 0.90, 0.85, 0.80) for false positives/negatives, (d) choose threshold and document rationale. Make threshold configurable.

5. **Performance:** Use batched embedding generation. Consider limiting to entity_class groups (e.g., only Biomarker, BiologicalProcess, Procedure, Mutation) to reduce pairs.

6. **Tests:** Mock embedding generator; two provisional entities with very similar names merge when similarity exceeds threshold.

---

## 5. Cross-Type Provisional Duplicates (homologous recombination deficiency)

**Goal:** "Homologous recombination deficiency" appears as two `canon-` hashes — one `biomarker`, one `disease`. Reconciliation (section 3) groups by `(normalized_name, entity_class)`, so these won't merge (types differ). The embedding pass (section 4) groups by `entity_class`, so it won't merge them either. Need explicit handling.

**Files:**
- `examples/medlit/pipeline/dedup.py`

**Options:**
- **A. Cross-type embedding pass:** Run embedding similarity over provisional entities *without* restricting to same `entity_class`. Pairs above threshold with different types → flag for manual resolution or apply a type-precedence rule (e.g., biomarker > disease for lab-measured concepts).
- **B. Type-precedence merge:** Define a precedence order (e.g., Gene > Protein > Biomarker > Disease) and auto-merge when name/similarity match but types differ, taking the higher-precedence type.
- **C. Flag-only:** Detect cross-type near-duplicates, emit as a report for manual merge; do not auto-merge.

**Recommendation:** Start with C (flag-only) to avoid over-merging. Add a post-pass that finds provisional pairs with high embedding similarity but different `entity_class`, writes to `cross_type_candidates.json` for review. Upgrade to A or B after validating on a sample.

**Output schema for `cross_type_candidates.json`** (written to Pass 2 `output_dir`; array of candidate pairs for manual review):

```json
[
  {
    "entity_id": "canon-abc123",
    "name": "homologous recombination deficiency",
    "entity_class": "biomarker",
    "source_papers": ["PMC1234567", "PMC7654321"],
    "similar_entity_id": "canon-def456",
    "similar_name": "homologous recombination deficiency",
    "similar_class": "disease",
    "similar_source_papers": ["PMC1234567", "PMC9999999"],
    "similarity_score": 0.98
  }
]
```

Include `source_papers` for each side so reviewers have paper context to judge whether the pair represents the same concept.

---

## 6. Filter PMC_UNKNOWN / PMC_extracted from supporting_documents

**Goal:** In `_entity_usage_from_bundles`, filter out `supporting_documents` entries that match a denylist.

**Files:**
- `examples/medlit/pipeline/bundle_builder.py`

**Steps:**

1. **Define denylist** at module level:
   ```python
   PROVENANCE_DENYLIST = frozenset({"PMC_UNKNOWN", "PMC_extracted"})
   # Optional: support "PMC_UNKNOWN_*" pattern
   ```

2. **In `_entity_usage_from_bundles`**, when appending to `rec["supporting_documents"]`, skip `paper_id` if `paper_id in PROVENANCE_DENYLIST` or `paper_id.startswith("PMC_UNKNOWN_")`.

3. **Recompute usage_count** after filtering: `usage_count = len([d for d in supporting_documents if d not in denylist])` — or equivalently, only append non-denylisted paper_ids, so `usage_count = len(rec["supporting_documents"])` remains correct.

4. **Tests:** Entity with only PMC_UNKNOWN in supporting_documents ends up with empty supporting_documents and usage_count 0.

**Deeper fix (optional, separate PR):** In `pass1_extract.py`, make `_paper_content_fallback` log a warning when producing synthetic IDs. In `JournalArticleParser` or parser chain, avoid returning `PMC_extracted`-style IDs when real PMC ID cannot be extracted — consider raising or returning a sentinel that downstream can detect.

---

## 7. Zero-Mention Orphan Guard in Pass 3

**Goal:** Entities that appear in relationships but have `usage_count == 0` (never in any evidence) should be dropped or flagged.

**Files:**
- `examples/medlit/pipeline/bundle_builder.py`

**Steps:**

1. **In `run_pass3`**, after `usage = _entity_usage_from_bundles(...)` and before building `entity_rows`:
   - Option A (drop): Filter `entities_list` to exclude entities where `usage.get(ent["entity_id"], {}).get("usage_count", 0) == 0`.
   - Option B (flag): Add a property or metadata for `usage_count == 0` entities; still emit them but mark for review.
   - **Recommendation:** Option A — drop. These entities have no supporting evidence and add noise.

2. **Interaction with provenance denylist (section 6):** After applying the denylist in `_entity_usage_from_bundles`, some entities that *had* `usage_count > 0` (driven only by PMC_UNKNOWN/PMC_extracted) will drop to `usage_count == 0`. Those must also be caught by the orphan filter. **Execution order:** Apply denylist first (inside `_entity_usage_from_bundles`), so `usage` reflects filtered `supporting_documents`. Then apply orphan filter when building `entity_rows`. Both in the same pass — no recompute needed.

3. **Interaction with existing orphan filter:** The current filter drops entities not in `referenced_ids` (subject/object of any relationship). Zero-mention entities *are* in referenced_ids but have usage_count=0. So we need an additional filter: drop if `usage_count == 0` (or optionally, drop if not in `referenced_ids` OR `usage_count == 0`).

4. **Tests:** Entity that is subject of a relationship but has no evidence_ids gets usage_count=0 and is dropped from entity_rows.

---

## Execution Order

| Phase | Tasks | Dependencies |
|-------|-------|--------------|
| 1 | Synonym indexing (1), Namespace normalization (2) | None |
| 2 | Post-dedup reconciliation (3) | 1, 2 |
| 3 | Provenance denylist (6), Zero-mention guard (7) — same pass, denylist first | None |
| 4 | Embedding-based dedup (4) | 1, 2, 3; requires embedding infra |
| 5 | Cross-type handling (5) | 4; start with flag-only |

---

## File Touch Summary

| File | Changes |
|------|---------|
| `examples/medlit/pipeline/dedup.py` | Synonym index, `_preferred_authoritative_id`, UMLS→HGNC lookup, reconciliation pass (with triple merge-on-collision), optional embedding pass, cross-type handling |
| `examples/medlit/pipeline/synonym_cache.py` | Possibly extend for synonym indexing; may not need changes if index is in-memory only |
| `examples/medlit/pipeline/bundle_builder.py` | Provenance denylist (6), usage_count==0 filter (7) |
| `examples/medlit/scripts/pass2_dedup.py` | Pass `embedding_generator` if implementing (4) |
| `examples/medlit/tests/test_dedup*.py` | New or extended tests for each fix |

---

## Verification

After each change:

1. Run `uv run pytest examples/medlit/tests/ -v`
2. Run full pipeline on a small corpus (e.g., 5–10 papers) and inspect:
   - `medlit_merged/entities.json` — fewer duplicates, no PMC_UNKNOWN in supporting_documents
   - `medlit_merged/relationships.json` — SAME_AS edges for reconciled duplicates
3. Compare entity count before/after to confirm reduction.
4. As always, finish with `lint.sh` to verify no outstanding linter issues.

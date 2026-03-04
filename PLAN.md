# Plan: Entity Deduplication, Relationship Taxonomy, and Book Framing

Reminder for future work. Not complete; expand as needed.

---

## 1. De-duplication: Make it Observable, Then Strict

**Problem:** Multiple identity signals (string, UMLS, context, type) — "near-identical" entities slip through as distinct.

**Approach:** Identity tiers as contract:

- **Tier A (hard ID):** UMLS/DOID/CHEBI/etc → must merge
- **Tier B (strong alias set):** curated synonym list / abbreviation expansions → merge unless type conflict
- **Tier C (soft match):** embedding/string similarity → suggest merge, don't auto-merge without evidence

**Key deliverable:** Collision report after ingest:
> "These 27 nodes are >0.92 similar and share type + neighborhood overlap"

Then click through and fix root causes instead of hunting visually.

**Why dupes persist:** punctuation/hyphenation/plural, abbreviation vs expansion, tokenization, type drift. Normalize label aggressively; use type + neighborhood as sanity check. If two candidates share many neighbors and relationship types → strong merge signal.

**UI:** Show "Merged from: …" on hover. Even if dedupe isn't perfect, readers see you track identity.

**Relevant files:**

- `examples/medlit/pipeline/dedup.py` — pass 2 dedup, SAME_AS resolution, canonical ID assignment
- `examples/medlit/scripts/pass2_dedup.py` — script entry
- `examples/medlit/pipeline/synonym_cache.py` — synonym lookup, add_same_as_to_cache
- `examples/medlit/pipeline/authority_lookup.py` — UMLS/HGNC/RxNorm resolution
- `kgraph/pipeline/embedding.py` — embeddings for similarity
- `kgserver/query/static/graph-viz.js` — graph UI; add "Merged from" to tooltip/detail panel
- `kgserver/query/static/index.html` — graph viz controls

---

## 2. "Associated With": Split Unknown vs Weak vs Real

**Problem:** `associated_with` does two jobs: (1) "We know there's a relation but not which one" and (2) "The paper is vague/correlational." Those should not look the same.

**Taxonomy (replace associated_with with):**

**A. Unknown / underspecified**
- `related_to` (unspecified)
- `mentioned_with`
- `co_occurs_in_source`
- `evidence_links` (provenance-driven)

**B. Weak / correlational**
- `correlates_with`
- `risk_factor_for`
- `increases_risk_of` / `decreases_risk_of`
- `predicts`

**C. Strong / mechanistic / semantic**
- `treats`, `causes`, `induces`, `inhibits`, `diagnoses`, `indicates`, `complication_of`, etc.

**Orthogonal attributes on every edge:**
- `polarity`: positive / negative / unknown
- `strength`: asserted / inferred / speculative
- (optional) `evidence_kind`: RCT / observational / case report / review / guideline

**Cheap improvement:** Extractor outputs either (a) concrete predicate from controlled list, or (b) `UNSPECIFIED_RELATION` + `relation_rationale` string. Graph renders:
- solid labeled edges for real predicates
- dashed gray edges for `UNSPECIFIED_RELATION`
- tooltip shows rationale/snippet

**Relevant files:**

- `examples/medlit/pipeline/relationships.py` — predicate extraction, specificity ranking, `associated_with` last in list, OMIT rule
- `examples/medlit_schema/relationship.py` — predicate classes, `ASSOCIATED_WITH` / `AssociatedWith`
- `examples/medlit_schema/base.py` — `ASSOCIATED_WITH` enum
- `examples/medlit_schema/domain.py` — predicate constraints, subject/object types
- `examples/medlit/relationships.py` — `MedicalClaimRelationship`, predicate vocab
- `examples/medlit/vocab.py` — `predicate_associated_with`
- `examples/medlit/scripts/pass1_extract.py` — LLM prompt with predicate list
- `docs/schema-design-guide.md` — "Avoid overloading one predicate"
- `kgserver/query/static/graph-viz.js` — edge rendering; add dashed style for UNSPECIFIED_RELATION
- `kgserver/query/static/graph-viz.css` — link styles

---

## 3. Book-Friendly Framing

**Figure idea:** Same subgraph shown twice:
- **Left:** everything is "associated with" → spaghetti
- **Right:** typed predicates + dashed "unknown" edges → readable and honest

**Callout:** "A graph that admits uncertainty is more useful than one that confidently lies."

**Relevant files:**

- `kg-book/outline.md` — book structure; add section on uncertainty / predicate design
- `kg-book/` — figures, example graphs for before/after

---

## Quick Reference: Predicate / Schema Touchpoints

| Area | Files |
|------|-------|
| Extraction | `examples/medlit/pipeline/relationships.py`, `pass1_extract.py` |
| Schema | `examples/medlit_schema/relationship.py`, `base.py`, `domain.py` |
| Dedup | `examples/medlit/pipeline/dedup.py`, `synonym_cache.py` |
| Graph UI | `kgserver/query/static/graph-viz.js`, `graph-viz.css`, `index.html` |
| Docs | `docs/schema-design-guide.md`, `docs/examples/medlit.md` |

# PLAN6: Author and Institution Relationships

**Status:** Implemented (Phase 0–2 complete).

**Goal:** Connect authors and institutions to the knowledge graph via first-class entities and relationships. Enable queries like "who has written about disease X?" and "which institutions study drug Y?"

---

## Design Decisions (Locked)

- **Author** and **Institution** already exist as entity types in `domain_spec.py`. Add **Paper** entity type for document nodes (AUTHORED links Author→Paper).
- Relationships are **derived from metadata**, not LLM-extracted. The LLM continues to extract biomedical entities and relationships only.
- New predicates: AUTHORED, AFFILIATED_WITH, DESCRIBED, COAUTHORED_WITH, IS_COLLEAGUE.
- **Cardinality:** DESCRIBED uses **Paper** as subject (not Author/Institution) to avoid link explosion. One edge per (paper, entity) instead of N per (author, entity).
- **IS_COLLEAGUE:** Keep predicate defined but do not create IS_COLLEAGUE edges when COAUTHORED_WITH already exists. Reserve for future sources (e.g. "same lab but never coauthored").
- Author identity: use normalized string (e.g. `Author:LastName_FirstInitial`) for now. No ORCID/disambiguation in Phase 1.
- Institution identity: use normalized string from affiliation text. No authority lookup in Phase 1.
- **Symmetric predicates:** See "Symmetric Predicates" section below.

---

## Symmetric Predicates

Symmetric predicates (e.g. COAUTHORED_WITH, ASSOCIATED_WITH) have two distinct problems:

**Problem 1: Dedup identity.** Without canonical ordering, COAUTHORED_WITH(smith_j, jones_m) from one paper and COAUTHORED_WITH(jones_m, smith_j) from another are treated as different edges by id-based dedup. **Fix:** At write time (provenance_expansion, Pass 2), for symmetric predicates always store with `min(subject_id, object_id)` as subject and `max(...)` as object. Deterministic, no duplicates.

**Problem 2: Query traversal.** A query for "everyone Smith has collaborated with" must not depend on storage direction. **Fix:** Query layer treats symmetric predicate edges as undirected (e.g. Neo4j `(a)-[:COAUTHORED_WITH]-(b)` not `->`).

**Schema support:** Add to `PredicateSpec` in `kgschema/spec.py`:
```python
symmetric: bool = False
is_merge_signal: bool = False  # SAME_AS drives entity canonicalization; distinct from plain symmetric
```

Mark symmetric predicates in domain_spec:
- COAUTHORED_WITH, IS_COLLEAGUE, SAME_AS, INTERACTS_WITH, ASSOCIATED_WITH: `symmetric=True`
- SAME_AS only: `is_merge_signal=True`

**ASSOCIATED_WITH note:** It's symmetric but also a catch-all when the LLM can't commit to a more specific predicate. A future `specificity_fallback: bool` could downweight or flag such edges. Separate from symmetry; document for later.

---

## Predicate Definitions

| Predicate | Direction | Meaning | Source |
|-----------|-----------|---------|--------|
| AUTHORED | Author → Paper | Author wrote this paper | Parser metadata |
| AFFILIATED_WITH | Author → Institution | Author's affiliation at time of paper | Parser (author affiliations) |
| DESCRIBED | **Paper** → Entity | Paper describes this entity (disease, drug, etc.) | Derived: paper + entities in paper |
| COAUTHORED_WITH | Author ↔ Author | Co-authors on at least one paper | Derived from paper author lists |
| IS_COLLEAGUE | Author ↔ Author | Colleagues (e.g. same institution) from a source other than co-authorship | **Not populated when COAUTHORED_WITH exists.** Reserved for future (e.g. "same lab, never coauthored") |

---

## Phase 0: PredicateSpec and Symmetric Handling

### Step 0.1: Add symmetric and is_merge_signal to PredicateSpec

**File:** `kgschema/spec.py`

**0.1.1** Add to `PredicateSpec`:
```python
symmetric: bool = Field(default=False, description="If True, store with canonical (min,max) ordering; query layer treats as undirected")
is_merge_signal: bool = Field(default=False, description="If True, drives entity canonicalization (e.g. SAME_AS). Distinct from plain symmetric.")
```

**Verification:** `from kgschema.spec import PredicateSpec`; `PredicateSpec(description="x", symmetric=True)` succeeds.

---

### Step 0.2: Mark symmetric predicates in domain_spec

**File:** `examples/medlit/domain_spec.py`

**0.2.1** Add `symmetric=True` to existing predicates: INTERACTS_WITH, ASSOCIATED_WITH.
**0.2.2** For SAME_AS: add `symmetric=True, is_merge_signal=True`.
**0.2.3** COAUTHORED_WITH and IS_COLLEAGUE are added in Phase 1 (Step 1.2.2) with `symmetric=True` already set.

**Verification:** `PREDICATES["INTERACTS_WITH"].symmetric` is True. After Phase 1: `PREDICATES["COAUTHORED_WITH"].symmetric` is True.

---

### Step 0.3: Canonical ordering helper (shared util)

**File:** `examples/medlit/pipeline/utils.py` (create if missing)

**0.3.1** Implement `canonicalize_symmetric(subject_id: str, object_id: str) -> tuple[str, str]`:
- Return `(min(subject_id, object_id), max(subject_id, object_id))`.
- Both provenance_expansion (Phase 2) and dedup (Step 0.4) import from this module. Do not duplicate the logic.

**Verification:** `from examples.medlit.pipeline.utils import canonicalize_symmetric; canonicalize_symmetric("b", "a") == ("a", "b")`.

---

### Step 0.4: Pass 2 dedup canonical ordering

**File:** `examples/medlit/pipeline/dedup.py`

**0.4.1** Import `canonicalize_symmetric` from `examples.medlit.pipeline.utils`. In step 6 (accumulate relationships), when building the merge key `(sub_c, predicate, obj_c)` for `triple_to_rel`, check if the predicate is symmetric via `examples.medlit.domain_spec.PREDICATES.get(predicate)` and `.symmetric`. If symmetric, use `sub_c, obj_c = canonicalize_symmetric(sub_c, obj_c)` and then `(sub_c, predicate, obj_c)` as the key so that COAUTHORED_WITH(A,B) and COAUTHORED_WITH(B,A) merge to one edge.

**Verification:** Two papers with reversed COAUTHORED_WITH produce one merged edge.

---

### Step 0.5: Query-layer contract (documentation)

**File:** `kgserver/query/graph_traversal.py` or `docs/` — document the contract:

> For predicates with `symmetric=True`, graph traversal MUST treat edges as undirected. When expanding from an entity, follow both (entity as subject) and (entity as object). Storage may have canonical (min,max) ordering; queries must not depend on direction.

Add a comment or docstring where BFS/expansion happens. No code change required if the current traversal already follows both directions (e.g. `find_relationships(subject_id=X)` and `find_relationships(object_id=X)`). If it only follows one direction, add the symmetric case.

**Verification:** Query "entities connected to X via COAUTHORED_WITH" returns Y when edge is stored as (Y, X) or (X, Y).

---

### Step 0.6: metadata_only flag (extraction prompt filtering)

**Problem:** PaperEntity, AuthorEntity, InstitutionEntity are metadata-derived. If they appear in ENTITY_CLASSES (and thus BUNDLE_CLASS_TO_ENTITY), they will be included in the LLM extraction prompt unless filtered. The LLM must not extract Paper, Author, or Institution — those come from provenance expansion.

**File:** `kgschema/spec.py`

**0.6.1** Add to `EntitySpec`:
```python
metadata_only: bool = Field(default=False, description="If True, entity is derived from metadata only; exclude from LLM extraction prompt.")
```

**File:** `kgraph/templates/render.py`

**0.6.2** In `_format_from_domain_spec`, when building `entity_types_str`, filter out entity classes with `metadata_only=True`:
- Iterate `BUNDLE_CLASS_TO_ENTITY`; for each `(bundle_class, entity_cls)`, skip if `getattr(getattr(entity_cls, 'spec', None), 'metadata_only', False)`.
- Build `entity_types_str` from the filtered keys only.

**Verification:** With PaperEntity, AuthorEntity, InstitutionEntity marked `metadata_only=True`, the extraction prompt must not list Paper, Author, or Institution in the entity types.

---

## Phase 1: Parser and Schema (Metadata Only)

### Step 1.1: Extract author affiliations from parser

**File:** `examples/medlit/pipeline/parser.py`

**1.1.1** In `_parse_xml_to_dict`, add affiliation extraction. The method returns a flat dict with keys `paper_id`, `title`, `authors`, etc. JATS/PMC XML structure:
- Build a dict `aff_id_to_text`: for each `aff` in `root.findall(".//aff")`, get `aff.get("id")` and extract text from `aff.find("institution")` or `aff.find("institution[@content-type='orgname']")` or `"".join(aff.itertext()).strip()` as fallback.
- For each `contrib` in `root.findall('.//contrib[@contrib-type="author"]')`: get name (surname + given-names) as before. For affiliations: find `contrib.findall("xref[@ref-type='aff']")`; for each xref, get `rid = xref.get("rid")` (may have # prefix, e.g. "aff1"); look up `aff_id_to_text.get(rid) or aff_id_to_text.get(rid.lstrip("#"))`; collect into list. Build `{"name": author_str, "affiliations": [aff_text, ...]}`.

**1.1.2** Build `author_details: list[dict]` with structure `{"name": str, "affiliations": list[str]}`. Keep `authors` as `list[str]` (author names only) for backward compatibility. Add `author_details` to the returned dict (same level as `authors`, `title`). If XML has no aff data, use `affiliations=[]` for each author.

**1.1.3** In `_parse_from_dict`, add `metadata["author_details"] = data.get("author_details", [])` when building the `metadata` dict (before constructing `JournalArticle`).

**Verification:** Parse a PMC XML with affiliations; assert `metadata["author_details"][0]["affiliations"]` is non-empty when XML has aff data.

---

### Step 1.2: Add predicates to domain_spec

**File:** `examples/medlit/domain_spec.py`

**1.2.1** Add `PaperEntity` to `domain_spec.py` (before ENTITY_CLASSES list):
```python
class PaperEntity(BaseEntity):
    spec: ClassVar[EntitySpec] = EntitySpec(
        description="A published paper or document.",
        color="#9e9e9e",
        label="Paper",
        metadata_only=True,
    )
    def get_entity_type(self) -> str:
        return "paper"
```
Add `PaperEntity` to `ENTITY_CLASSES` list.

**1.2.1b** Set `metadata_only=True` on `AuthorEntity` and `InstitutionEntity` specs. In `examples/medlit/domain_spec.py`, remove `AuthorEntity` and `InstitutionEntity` from `MENTIONS.mentionable_types` (MENTIONS is the `MentionsSpec` instance at module level; it controls which entity types the LLM may extract). They are metadata-derived, not LLM-extracted.

**1.2.2** Ensure `kgschema/spec.py` PredicateSpec has `subject_types` and `object_types` typed as `Optional[list[type]] = Field(default=None, ...)`. If either uses `list[type]` without `Optional`, update the type annotation so `None` is valid (semantics: any entity type). Then add to `PREDICATES` dict (after ENCODES, before closing `}`):

```python
    "AUTHORED": PredicateSpec(
        description="Author wrote this paper.",
        subject_types=[AuthorEntity],
        object_types=[PaperEntity],
        specificity=1,
    ),
    "AFFILIATED_WITH": PredicateSpec(
        description="Author's institutional affiliation at time of publication.",
        subject_types=[AuthorEntity],
        object_types=[InstitutionEntity],
        specificity=2,
    ),
    "DESCRIBED": PredicateSpec(
        description="Paper describes this entity (disease, drug, etc.).",
        subject_types=[PaperEntity],
        object_types=None,  # Any domain entity
        specificity=1,
    ),
    "COAUTHORED_WITH": PredicateSpec(
        description="Authors co-authored at least one paper.",
        subject_types=[AuthorEntity],
        object_types=[AuthorEntity],
        specificity=2,
        symmetric=True,
    ),
    "IS_COLLEAGUE": PredicateSpec(
        description="Authors are colleagues (e.g. same institution) from a source other than co-authorship. Do not create when COAUTHORED_WITH exists.",
        subject_types=[AuthorEntity],
        object_types=[AuthorEntity],
        specificity=2,
        symmetric=True,
    ),
```

**Note:** AUTHORED links Author to Paper. Add a minimal `Paper` entity type: `id=Paper:{document_id}`, `name=title`, `class="Paper"`. Add `PaperEntity` to `domain_spec.ENTITY_CLASSES` and `BUNDLE_CLASS_TO_ENTITY`. Paper entities are created during provenance expansion, not LLM extraction.

**1.2.4** Add predicate strings to `examples/medlit/vocab.py` in `ALL_PREDICATES`:
```python
predicate_authored = "authored"
predicate_affiliated_with = "affiliated_with"
predicate_described = "described"
predicate_coauthored_with = "coauthored_with"
predicate_is_colleague = "is_colleague"
# Add to ALL_PREDICATES set
```

**Verification:** `from examples.medlit.domain_spec import PREDICATES` and assert "AUTHORED" in PREDICATES.

---

### Step 1.3: Update PaperInfo and bundle models for structured authors

**File:** `examples/medlit/bundle_models.py`

**1.3.1** Add model:
```python
class AuthorInfo(BaseModel):
    """Author with optional affiliations."""
    name: str
    affiliations: list[str] = Field(default_factory=list)
```

**1.3.2** Add `PaperInfo.author_details: list[AuthorInfo] | None = None` and `PaperInfo.document_id: str = ""`. When building PaperInfo in pass1_extract, set `document_id=paper_id` (where `paper_id = paper_info.pmcid or path.stem`). Populate `author_details` from `metadata.get("author_details")` if the parser provided it; if `author_details` is None, derive from `authors` as `[AuthorInfo(name=a, affiliations=[]) for a in authors]`.

**1.3.3** Ensure `to_bundle_dict()` includes `author_details` and `document_id` when present so bundles on disk have structured author data for Pass 2/3.

**Verification:** Existing tests in `examples/medlit/tests/` must still pass.

---

## Phase 2: Provenance Expansion (Derived Relationships)

### Step 2.1: Create provenance_expansion module

**File:** `examples/medlit/pipeline/provenance_expansion.py` (new)

**2.1.1** Implement `normalize_author_id(name: str, paper_id: str) -> str`:
- Return `f"Author:{normalized}"` where normalized = last word + first initial, lowercased, alphanumeric only. E.g. "John Smith" → "Author:smith_j". Include paper_id hash or suffix if needed to avoid collisions across papers with same author name. Simpler: `Author:{paper_id}:{normalized}` so each paper gets its own author nodes, merged later. For Phase 2, use `Author:{normalized}` and accept possible merges of different people.

**2.1.2** Implement `normalize_institution_id(affiliation: str) -> str`:
- Return `f"Institution:{normalized}"` where normalized = first 50 chars, lowercased, non-alphanumeric replaced with underscore. E.g. "Harvard Medical School" → "Institution:harvard_medical_school".

**2.1.3** Implement `expand_provenance(bundle: PerPaperBundle) -> tuple[list[ExtractedEntityRow], list[RelationshipRow]]`:
- Input: PerPaperBundle (has paper, entities, relationships).
- Output: (new_entities, new_relationships).
- Logic:
  - Resolve author list: use `paper.author_details` if present, else `[AuthorInfo(name=a, affiliations=[]) for a in (paper.authors or [])]`.
  - For each author in that list: create Author entity `ExtractedEntityRow(id=normalize_author_id(author.name, document_id), entity_class="Author", name=author.name)`. Append to new_entities (dedupe by id within this bundle).
  - For each affiliation in each author's affiliations: create Institution entity `ExtractedEntityRow(id=normalize_institution_id(aff), entity_class="Institution", name=aff)`. Append to new_entities (dedupe).
  - For each author: add AFFILIATED_WITH(Author, Institution) for each of their affiliations.
  - Create Paper entity: `ExtractedEntityRow(id=f"Paper:{document_id}", entity_class="Paper", name=paper.title)`. Use `document_id = bundle.paper.document_id or bundle.paper.pmcid or "unknown"`. Add to new_entities.
  - For each author: add AUTHORED(Author, Paper) with subject_id=author_id, object_id=Paper entity id.
  - For each entity in bundle.entities where `entity.entity_class not in ("Author", "Institution", "Evidence")`: add DESCRIBED(Paper, entity). Build `RelationshipRow(subject=paper_entity_id, predicate="DESCRIBED", object_id=entity.id, source_papers=[document_id], confidence=0.9, asserted_by="derived")`. One edge per (paper, entity).
  - For each pair of authors on the same paper: add COAUTHORED_WITH(a1, a2). Import `canonicalize_symmetric` from `examples.medlit.pipeline.utils`; call `sub, obj = canonicalize_symmetric(a1, a2)` and build `RelationshipRow(subject=sub, predicate="COAUTHORED_WITH", object_id=obj, ...)`. Dedupe by (sub, obj) — one edge per pair.
  - **Do not** create IS_COLLEAGUE when COAUTHORED_WITH exists. Omit IS_COLLEAGUE from expansion for now (reserved for future sources).
- Return (new_entities, new_relationships).

**2.1.4** Paper entity is created in Step 2.1.3. Ensure PaperEntity is in domain_spec (Step 1.2.1).

**Verification:** Unit test: `expand_provenance(bundle_with_authors_and_entities)` returns Author entities, Institution entities, Paper entity, AFFILIATED_WITH, AUTHORED, DESCRIBED(Paper, Entity), COAUTHORED_WITH. Does **not** return IS_COLLEAGUE.

---

### Step 2.2: Integrate expansion into bundle building

**File:** `examples/medlit/pipeline/bundle_builder.py` or `examples/medlit/scripts/pass1_extract.py`

**2.2.1** In pass1_extract's `_paper_content_from_parser`, when building PaperInfo from doc: add `author_details=[AuthorInfo(**a) for a in doc.metadata.get("author_details", [])] if doc.metadata.get("author_details") else None`, and `document_id=doc.document_id or ""`. In the main loop (around line 343), when building the final `paper` PaperInfo, preserve `author_details=paper_info.author_details` and set `document_id=paper_id` (paper_id is already computed as `paper_info.pmcid or path.stem`).
**2.2.2** After the LLM returns and the bundle is built (before `with open(out_path, "w", ...)` around line 370), call `expand_provenance(bundle)` and extend `bundle.entities` and `bundle.relationships` with the returned lists. Then write the bundle to disk.
**2.2.3** Ensure dedup (Pass 2) handles Author and Institution entities - they use string IDs, no canonical lookup. Pass through to merged output.

**Integration point:** Expansion runs in **pass1_extract** (not bundle_builder). pass1_extract processes one paper at a time; expansion is per-paper, so it belongs there. bundle_builder loads pre-built bundles from disk; those bundles already include expanded entities/relationships from pass1_extract.

**Verification:** Run pass1_extract on one paper; inspect output JSON for Author entities, Institution entities, DESCRIBED relationships.

---

## Phase 3: Dedup and Storage (Optional)

- Pass 2 dedup: Author and Institution entities are merged by id (exact match). No fuzzy merge for Phase 1.
- When loading into kgserver storage: ensure Author and Institution entity types are accepted. Check `MedLitDomainSchema` or equivalent for entity type allowlist.

---

## Verification Checklist

- [ ] Parser extracts authors with affiliations from PMC XML
- [ ] PaperInfo supports structured authors (AuthorInfo)
- [ ] PREDICATES includes AUTHORED, AFFILIATED_WITH, DESCRIBED, COAUTHORED_WITH, IS_COLLEAGUE
- [ ] vocab.ALL_PREDICATES includes new predicates
- [ ] provenance_expansion.expand_provenance produces correct entities and relationships
- [ ] Bundle builder or pass1 integrates expansion
- [ ] Pass 2 dedup does not drop Author/Institution
- [ ] `./lint.sh` passes

---

## Files to Create or Modify

| File | Action |
|------|--------|
| `kgschema/spec.py` | Add symmetric, is_merge_signal (PredicateSpec); metadata_only (EntitySpec) |
| `kgraph/templates/render.py` | Filter metadata_only entities from extraction prompt |
| `examples/medlit/domain_spec.py` | Add predicates, PaperEntity, metadata_only on Author/Institution |
| `examples/medlit/vocab.py` | Add predicate strings |
| `examples/medlit/bundle_models.py` | Add AuthorInfo, update PaperInfo (author_details, document_id) |
| `examples/medlit/pipeline/parser.py` | Add affiliation extraction |
| `examples/medlit/pipeline/utils.py` | **New** (or add to existing) — `canonicalize_symmetric` |
| `examples/medlit/pipeline/provenance_expansion.py` | **New** |
| `examples/medlit/pipeline/dedup.py` | Canonical ordering for symmetric predicates |
| `examples/medlit/scripts/pass1_extract.py` | Integrate expansion, author_details, document_id |

---

## Open Questions (Resolve During Implementation)

**Author dedup:** Same name in different papers = same author? Phase 1: no. Phase 2: add optional merge by name similarity.

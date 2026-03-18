# PLAN8: Graph Data Quality Fixes

## Problems to Solve

### 1. Citation extraction (paper → paper relationships)

The pipeline does not extract references from PMC XML. Each paper's `<ref-list>` contains
structured citations that should become `CITES` relationships between paper entities. This
would allow the graph to represent how papers build on each other and enable citation-based
traversal.

Work needed:
- Parse `<ref-list>` / `<ref>` elements from PMC XML during the `extract` step
- Match cited PMC IDs to existing paper entities where possible; create provisional paper
  entities for cited papers not yet in the corpus
- Emit `CITES` relationships (subject=citing paper, object=cited paper) in the per-document
  bundle JSON
- Wire through `build_bundle` so these appear in `relationships.jsonl`

### 2. Institution name corruption (embedded ROR/grid identifiers)

Institution entity names are being corrupted during extraction — affiliation strings from
PMC XML contain structured identifiers (`https://ror.org/...`, `grid.XXXXX.XX`) concatenated
directly into the name field. Example:

```
"Department of Internal Medicine, University of... https://ror.org/01gmqr298grid.15496.3f0000 0001 0439 0892Institute of..."
```

Work needed:
- In the affiliation parsing logic, strip or separately capture ROR/grid identifiers before
  they reach the entity name
- Store the ROR URI in `canonical_url` on the institution entity instead
- Use the clean human-readable affiliation string as `name`

### 3. Missing positional metadata in mentions

All mention records have null `section` and `start_offset` fields. Positional metadata is
being lost between extraction and bundle assembly — traceability back to source text is
therefore missing.

Work needed:
- Identify where section/offset is dropped (likely in `extract.py` or the mention
  construction in `build_bundle.py`)
- Preserve section name and character offset through the pipeline
- Populate `section` and `start_offset` on mention records in `mentions.jsonl`

### 4. Self-loop relationships

Two relationships exist where `subject_id == object_id`. These are nonsensical and should
be excluded.

Work needed:
- Add a filter in `build_bundle.py` (or wherever relationships are written) to drop any
  relationship where subject and object are the same entity
- Optionally add a test asserting no self-loops in bundle output

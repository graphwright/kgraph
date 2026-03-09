# Config as Single Source of Truth — Future Project

## Goal

Consolidate all domain-specific configuration into a single Python module, `domain_spec.py`, that drives predicates, entity types, mentions, and evidence across the stack. Eliminate duplication and drift between schema and front-end.

**Status:** Project for another day. No implementation yet.

**Core insight:** YAML can't contain Python class definitions, which is why you always end up with YAML *plus* Python subclasses. A Python SSOT eliminates that split entirely — the spec *is* the schema.

---

## Current Duplication

| Concern | Source 1 | Source 2 | Source 3 |
|---------|----------|----------|----------|
| Predicates | `examples/medlit/config/predicates.yaml` | `examples/medlit/vocab.py` (ALL_PREDICATES, get_valid_predicates) | `examples/medlit_schema/base.py` (PredicateType enum) |
| Predicate specificity | — | `examples/medlit/pipeline/relationships.py` (PREDICATE_SPECIFICITY) | — |
| Entity types + colors | `examples/medlit/config/entity_types.yaml` | `kgserver/query/static/graph-viz.js` (ENTITY_TYPE_COLORS) | — |
| Evidence / mentions | Hardcoded in `bundle_builder.py`, `dedup.py` | — | — |

Adding a new predicate or entity type today requires edits in multiple places.

---

## Proposed Architecture: domain_spec.py

**Location:** `examples/medlit/domain_spec.py` (medlit domain); each domain has its own.

Replace `entity_types.yaml`, `predicates.yaml`, and scattered Python with a single module. Entity class *and* metadata are literally adjacent — zero drift possible.

### Spec models (define in kgschema)

Add to `kgschema/` (exact module TBD, e.g. `kgschema/spec.py`):

```python
# EntitySpec: display + prompt metadata for an entity type
class EntitySpec(BaseModel):
    description: str
    prompt_guidance: str = ""
    color: str = "#78909c"   # hex for graph-viz
    label: str               # display name (e.g. "Disease")

# PredicateSpec: validity + dedup metadata
class PredicateSpec(BaseModel):
    description: str
    subject_types: list[type]   # Entity classes
    object_types: list[type]
    specificity: int = 0        # for dedup: higher = prefer when (s,o) has multiple preds

# EvidenceSpec, MentionsSpec: as needed for bundle_builder, mentions
class EvidenceSpec(BaseModel):
    id_format: str
    methods: list[str] = ["llm"]
    section_names: list[str] = []

class MentionsSpec(BaseModel):
    mentionable_types: list[type]
    skip_name_equals_type: bool = True
```

### Example domain_spec.py structure

```python
# examples/medlit/domain_spec.py
from kgschema.entity import BaseEntity
from kgschema.spec import EntitySpec, PredicateSpec, EvidenceSpec, MentionsSpec

class DiseaseEntity(BaseEntity):
    def get_entity_type(self) -> str:
        return "disease"
    spec = EntitySpec(
        description="Diseases, conditions, syndromes.",
        prompt_guidance="Use the most specific term.",
        color="#ef5350",
        label="Disease",
    )

# ... AuthorEntity, GeneEntity, etc. (add spec to each)

PREDICATES = {
    "TREATS": PredicateSpec(
        description="Drug or procedure used therapeutically.",
        subject_types=[DrugEntity, ProcedureEntity],
        object_types=[DiseaseEntity],
        specificity=2,
    ),
    # ...
}

PROMPT_INSTRUCTIONS = """..."""
EVIDENCE = EvidenceSpec(id_format="{paper_id}:{section}:{paragraph_idx}:{method}", ...)
MENTIONS = MentionsSpec(mentionable_types=[DiseaseEntity, GeneEntity, ...], ...)
```

### Benefits over YAML

- Entity class and metadata adjacent — zero drift
- `subject_types`/`object_types` reference classes, not strings
- No parsing layer; spec IS the schema
- Type-safe: Pydantic validates at import time

### graph-viz export

JS can't import Python. Add script `examples/medlit/scripts/export_entity_types.py` that:
1. Imports `domain_spec`
2. Iterates entity classes with `spec` attr
3. Writes `{entity_type: {color, label}}` to `kgserver/query/static/entity_types.json`
4. graph-viz.js loads that JSON instead of hardcoded ENTITY_TYPE_COLORS

Run as build step (Makefile or `uv run` before serving).

---

## Migration: Step-by-Step

Execute in order. After each step, run `uv run pytest` and fix any failures before proceeding.

### Phase 1: Add spec infrastructure

1. **Create `kgschema/spec.py`** (or add to existing kgschema module)
   - Define `EntitySpec`, `PredicateSpec`, `EvidenceSpec`, `MentionsSpec` (Pydantic, frozen)
   - Export from `kgschema/__init__.py`

2. **Create `examples/medlit/domain_spec.py`** (alongside existing files)
   - Copy entity classes from `examples/medlit/entities.py`; add `spec = EntitySpec(...)` to each
   - Copy predicate definitions from `examples/medlit/config/predicates.yaml` into `PREDICATES` dict. Pick one casing (UPPER_SNAKE or lowercase) and use consistently; predicates.yaml uses UPPER_SNAKE.
   - Add `PROMPT_INSTRUCTIONS` from `examples/medlit/config/domain_instructions.md`
   - Add `EVIDENCE`, `MENTIONS` (extract from bundle_builder/dedup or use defaults)
   - Do NOT delete old files yet; domain_spec coexists during migration

### Phase 2: Wire consumers one by one

3. **Pass 1 prompt** (`kgraph/templates/render.py`)
   - Change `render_extraction_prompt(config_dir, vocab_entries)` to accept optional `domain_spec` module
   - If `domain_spec` provided: build `entity_types_str`, `predicates_str`, `domain_instructions` from `domain_spec.PROMPT_INSTRUCTIONS`, entity `spec.prompt_guidance`, `PREDICATES`
   - If not: keep current `_load_config(config_dir)` behavior (backward compat during transition)
   - Caller (`pass1_extract.py`) passes `domain_spec` when available

4. **pass1_extract.py** (`examples/medlit/scripts/pass1_extract.py`)
   - Import `from examples.medlit import domain_spec`
   - Pass `domain_spec` to `render_extraction_prompt` instead of `config_dir` (or pass both; render prefers domain_spec)
   - Remove or gate `load_entity_types` usage for prompt building

5. **domain.py** (`examples/medlit/domain.py`)
   - Change `get_valid_predicates(subject_type, object_type)` to iterate `PREDICATES`, filter by `subject_types`/`object_types` containing the matching entity class
   - Replace `from .vocab import ALL_PREDICATES, get_valid_predicates` with logic that uses `domain_spec.PREDICATES`
   - `ALL_PREDICATES` becomes `set(domain_spec.PREDICATES.keys())`

6. **dedup.py** (`examples/medlit/pipeline/dedup.py`)
   - Replace `load_entity_types(config_dir)` with data derived from `domain_spec` (entity classes → bundle_class, lookup type mapping)
   - `_entity_class_to_lookup_type` built from entity classes in domain_spec

7. **bundle_builder.py** (`examples/medlit/pipeline/bundle_builder.py`)
   - Replace hardcoded evidence id_format with `domain_spec.EVIDENCE.id_format`

8. **pipeline/relationships.py** (`examples/medlit/pipeline/relationships.py`)
   - Replace `PREDICATE_SPECIFICITY` dict with `{k: v.specificity for k, v in domain_spec.PREDICATES.items()}`

9. **pass1a_vocab.py**, **pass2_dedup.py**
   - Replace `load_entity_types(config_dir)` with domain_spec–derived data
   - Update `--config-dir` help text; may keep for backward compat or remove if domain_spec is sole source

### Phase 3: graph-viz export

10. **Create `examples/medlit/scripts/export_entity_types.py`**
    - Import domain_spec, iterate entity classes with `spec`, write JSON to `kgserver/query/static/entity_types.json`
    - Add to Makefile or document: `uv run python examples/medlit/scripts/export_entity_types.py`

11. **graph-viz.js** (`kgserver/query/static/graph-viz.js`)
    - Replace hardcoded `ENTITY_TYPE_COLORS` with fetch/load of `entity_types.json`, or inject at build time
    - Ensure fallback if JSON missing (e.g. dev without running export)

### Phase 4: Remove obsolete files

12. **Delete**
    - `examples/medlit/config/entity_types.yaml`
    - `examples/medlit/config/predicates.yaml`
    - `examples/medlit/config/domain_instructions.md`

13. **Remove or repurpose**
    - `examples/medlit/pipeline/config_loader.py` — delete if no remaining callers; or keep `get_schema_version()` that hashes domain_spec module content
    - `examples/medlit/vocab.py` — delete; logic lives in domain_spec and domain.py

14. **Update tests**
    - `examples/medlit/tests/test_config_loader.py` — remove or rewrite to test domain_spec
    - `examples/medlit/tests/test_pass1_extract.py` — update fixtures to use domain_spec
    - All other tests that imported config_loader or vocab

### Verification

After each step: `uv run pytest`

Final: `uv run pytest` and manual check that Pass 1 extraction, Pass 2 dedup, Pass 3 bundle build, and graph-viz all work.

---

## Consumer Change Summary

| File | Change |
|------|--------|
| `kgraph/templates/render.py` | Accept `domain_spec`; build prompt from it when provided |
| `examples/medlit/scripts/pass1_extract.py` | Pass domain_spec to render |
| `examples/medlit/domain.py` | Use domain_spec.PREDICATES for get_valid_predicates |
| `examples/medlit/pipeline/dedup.py` | Use domain_spec for entity_types, lookup mapping |
| `examples/medlit/pipeline/bundle_builder.py` | Use domain_spec.EVIDENCE.id_format |
| `examples/medlit/pipeline/relationships.py` | PREDICATE_SPECIFICITY from domain_spec.PREDICATES |
| `examples/medlit/scripts/pass1a_vocab.py` | Use domain_spec instead of load_entity_types |
| `examples/medlit/scripts/pass2_dedup.py` | Use domain_spec instead of load_entity_types |
| `kgserver/query/static/graph-viz.js` | Load entity_types.json (from export script) |

---

## Acceptance Criteria

- [ ] Adding a new predicate requires editing only `domain_spec.py`
- [ ] Adding a new entity type (with color) requires editing only `domain_spec.py`
- [ ] Evidence id_format and mention rules live in `domain_spec.py`
- [ ] Pass 1 prompt generated from domain_spec; no domain_instructions.md
- [ ] graph-viz colors from `entity_types.json` produced by export script
- [ ] `uv run pytest` passes
- [ ] Pass 1, 2, 3 pipeline runs end-to-end without regression

---

## Deferred: Complete config_loader → domain_spec migration

The ssot branch establishes `domain_spec.py` as SSOT for prompts and pass1 type mapping,
but `config_loader.py` remains load-bearing in pass1_extract (get_schema_version, fallback),
pass1a_vocab, and dedup. Full migration: wire those three to domain_spec, replace
get_schema_version with hash of domain_spec module source, then delete YAML files and
config_loader. See `config_loader.py` TODO. Also: change `render_extraction_prompt` to
raise an explicit error when both `domain_spec` and `config_dir` are None (instead of
silently falling back to `Path(".")`).

---

## Domain-Agnostic Moves to kgraph Core

**North star:** A new domain implementor provides `domain_spec.py` (entity classes + specs, PREDICATES, PROMPT_INSTRUCTIONS, EVIDENCE, MENTIONS), BaseDocument subclass, and PromotionPolicy. Everything else inherited from core.

### Proposed moves (reviewed)

| Item | From | To | Caveats |
|------|------|-----|---------|
| `stage_models.py` | `examples/medlit/` | `kgraph/` | Currently unused. Move as spec for future pipeline output. |
| `progress.py` | `examples/medlit/` | `kgraph/` | Generic. Move with `examples/medlit/tests/test_progress_tracker.py` → `kgraph/tests/` |
| `llm_client.py` | `examples/medlit/pipeline/` | `kgraph/pipeline/` | Parameterize hardcoded "biomedical" system prompts in OllamaLLMClient before move |
| `pass1_llm.py` | `examples/medlit/pipeline/` | `kgraph/pipeline/` | Update ollama backend to import from kgraph.pipeline.llm_client |
| `embeddings.py` | `examples/medlit/pipeline/` | `kgraph/pipeline/` | Rename OllamaMedLitEmbeddingGenerator → OllamaEmbeddingGenerator |
| `synonym_cache.py` | `examples/medlit/pipeline/` | `kgraph/pipeline/` | No changes; already generic |

### Stays in medlit

- `authority_lookup.py`, `canonical_urls.py` — UMLS/HGNC/RxNorm/UniProt
- `pmc_streaming.py`, `pmc_chunker.py`, `parser.py` — PMC/JATS
- `dedup.py`, `bundle_builder.py` — medlit field handling (candidate for future core extraction when second domain needs dedup)

### config_loader.py

After domain_spec migration: delete `examples/medlit/pipeline/config_loader.py` or keep only `get_schema_version(domain_spec_module)` that hashes module content for cache busting.

### Implementation order (domain-agnostic moves)

1. Move `stage_models.py`, `progress.py` to kgraph; update imports; run pytest
2. Move `llm_client.py` (fix prompts), `pass1_llm.py`, `embeddings.py`, `synonym_cache.py` to kgraph; update all imports; run pytest
3. Proceed with domain_spec migration (Phase 1–4 above)

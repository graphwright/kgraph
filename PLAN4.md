# Refined Plan: Complete config_loader → domain_spec Migration

**Status:** Approved. Execute in order with `uv run pytest` after each step.

**Principle:** After each step, run `uv run pytest` and fix any breakage before proceeding.

---

## Step 1: `pass1_extract.py` + `render_extraction_prompt` hardening

**Note:** Step 2 must be done in the same batch as Step 1. `pass1a_vocab` imports `_normalized_to_bundle_class` from `pass1_extract`; removing it in Step 1 without updating pass1a_vocab in Step 2 would break imports.

### 1.1 Audit `cfg_dir` usage before removal

**Audit result:** `cfg_dir` is used only for schema loading:
- `load_entity_types(cfg_dir)` — schema
- `get_schema_version(cfg_dir)` — schema
- `_default_system_prompt(cfg_dir, ...)` — passed to `render_extraction_prompt`, but when `domain_spec` is provided, `config_dir` is ignored

**Vocab loading is separate:** `vocab_entries` comes from `--vocab-file` (lines 296–304), which is an explicit path (e.g. `pass1_vocab/vocab.json`). That is a workspace path, not `config_dir`. Do not conflate the two. Safe to remove `cfg_dir`.

### 1.2 Remove fallback and config_loader imports

**Current state (lines 39–42, 288–293):**
- Imports `get_schema_version`, `load_entity_types` from `config_loader`
- `normalized_to_bundle = getattr(_ds, "NORMALIZED_TO_BUNDLE", None) or _normalized_to_bundle_class(load_entity_types(cfg_dir))`
- `schema_version = get_schema_version(cfg_dir) if cfg_dir.exists() else None`

**Actions:**
1. Remove the `config_loader` import entirely.
2. Replace `normalized_to_bundle` assignment with:
   ```python
   normalized_to_bundle = _ds.NORMALIZED_TO_BUNDLE
   ```
   (No fallback; `domain_spec` is the sole source.)
3. Remove `_normalized_to_bundle_class`, `_FALLBACK_NORMALIZED_TO_BUNDLE`, and the `_normalized_to_bundle_class` function (they become dead code).
4. Replace `schema_version` with:
   ```python
   import inspect
   schema_version = hashlib.sha256(inspect.getsource(_ds).encode()).hexdigest()[:8]
   ```
   (`hashlib` is already imported.)
5. Remove `cfg_dir` / `config_dir` from `run_pass1` and the `--config-dir` CLI arg.
6. Update `_default_system_prompt` signature: drop `config_dir`. Call `render_extraction_prompt(config_dir=None, vocab_entries=..., domain_spec=domain_spec)`.

### 1.3 Harden `render_extraction_prompt` (required)

In `kgraph/templates/render.py`:

1. Add explicit validation at the start of `render_extraction_prompt` (before the `if domain_spec is not None` branch):
   ```python
   if domain_spec is None and config_dir is None:
       raise ValueError("Either domain_spec or config_dir must be provided")
   ```

2. Remove the silent fallback `config_dir = config_dir or Path(".")` in the `else` branch. Once config_loader is deleted there is no valid config dir to fall back to; the silent fallback is a latent bug. In the `else` branch we know `domain_spec` is None, so `config_dir` must have been provided (otherwise we would have raised). Use `config_dir` directly.

**Verification:** `uv run pytest`

---

## Step 2: `pass1a_vocab.py` (run with Step 1)

### 2.1 Replace `load_entity_types` with domain_spec

**Current state:**
- Imports `load_entity_types` from `config_loader` (line 34)
- Imports `_normalized_to_bundle_class` from `pass1_extract` (line 35)
- `_pass1a_system_prompt(config_dir)` calls `load_entity_types(config_dir)` and uses `entity_types.keys()` for the type enum (lines 38–41)
- `run_pass1a` calls `load_entity_types(cfg_dir)` and `_normalized_to_bundle_class(entity_types)` (lines 235–237)

**Actions:**
1. Add `import examples.medlit.domain_spec as _ds` (same pattern as pass1_extract).
2. Remove `config_loader` and `pass1_extract._normalized_to_bundle_class` imports.
3. Change `_pass1a_system_prompt` to take no config_dir argument. Build type enum from `sorted(_ds.NORMALIZED_TO_BUNDLE.keys())`. Remove the hardcoded fallback list (lines 43–65); use `_ds.NORMALIZED_TO_BUNDLE` as sole source.
4. In `run_pass1a`: set `normalized_to_bundle = _ds.NORMALIZED_TO_BUNDLE`; remove `load_entity_types` and `_normalized_to_bundle_class` usage.
5. Update `_pass1a_system_prompt()` call site to pass no args (it currently receives `cfg_dir`).
6. Remove `config_dir` parameter from `run_pass1a` and the `--config-dir` CLI arg.

**Verification:** `uv run pytest`

---

## Step 3: `dedup.py`

### 3.1 Replace `load_entity_types` with domain_spec-derived mapping

**Current state:**
- Imports `load_entity_types` from `config_loader` (line 17)
- `_build_entity_class_to_lookup_type(config_dir)` reads `entity_types.yaml` and builds `bundle_class -> lookup_type` (lines 138–148)
- `run_pass2` uses `config_dir` to call `_build_entity_class_to_lookup_type` (lines 190–192)

**Actions:**
1. Remove `config_loader` import.
2. Add `import examples.medlit.domain_spec as _ds`.
3. Replace `_build_entity_class_to_lookup_type(config_dir)` with a function that builds the mapping from `domain_spec`:
   ```python
   def _build_entity_class_to_lookup_type() -> dict[str, str]:
       """Derive bundle_class -> lookup_type from domain_spec.NORMALIZED_TO_BUNDLE."""
       out = {v: k for k, v in _ds.NORMALIZED_TO_BUNDLE.items()}
       out.update(_AUTHORITY_LOOKUP_OVERRIDES)
       return out
   ```
   **Semantics verification:** The old YAML version iterated `entity_types.items()` with `config_key` (e.g. `"biologicalprocess"`) and `val["bundle_class"]` (e.g. `"BiologicalProcess"`), producing `out["BiologicalProcess"] = "biologicalprocess"`. `NORMALIZED_TO_BUNDLE` maps `"biologicalprocess"` → `"BiologicalProcess"`. Inverting gives `"BiologicalProcess"` → `"biologicalprocess"`. Same semantics. Overrides (Hormone→drug, Enzyme→protein, Biomarker→disease) take precedence.
4. In `run_pass2`: remove `config_dir` parameter. Call `_build_entity_class_to_lookup_type()` with no args. Remove the `if config_dir is None` / `config_dir.exists()` logic.
5. Update `pass2_dedup.py` to stop passing `config_dir` to `run_pass2` and remove the `--config-dir` CLI arg.
6. Update `kgserver/mcp_server/ingest_worker.py` if it passes `config_dir` to `run_pass2` (it currently does not; verify no change needed).

**Verification:** `uv run pytest`

---

## Step 4: Update tests that use config_loader or config_dir

### 4.1 `test_pass1_extract.py`

**Current state:**
- Uses `load_entity_types(_config_dir())` and `_normalized_to_bundle_class` for `_normalized_to_bundle()` (lines 5, 17–18)
- Calls `_default_system_prompt(_config_dir(), None)` and `_default_system_prompt(_config_dir(), vocab)` (lines 62–63, 73)

**Actions:**
1. Remove `config_loader` import.
2. Add `import examples.medlit.domain_spec as _ds`.
3. Replace `_normalized_to_bundle()` with `_ds.NORMALIZED_TO_BUNDLE`.
4. Change `_default_system_prompt` calls to pass `domain_spec=_ds` and `config_dir=None` (or whatever the updated signature expects).
5. Remove `_config_dir()` helper if it becomes unused.

**Verification:** `uv run pytest`

---

## Step 5: Delete obsolete files and config_loader

### 5.1 Delete files

- `examples/medlit/config/entity_types.yaml`
- `examples/medlit/config/predicates.yaml`
- `examples/medlit/config/domain_instructions.md`
- `examples/medlit/pipeline/config_loader.py`

### 5.2 Handle `test_config_loader.py`

**Options:**
- **Delete** `examples/medlit/tests/test_config_loader.py` (recommended; config_loader is gone).
- **Or** rewrite to test domain_spec (e.g., that `NORMALIZED_TO_BUNDLE` and `BUNDLE_CLASS_TO_ENTITY` are consistent, that schema version hash is deterministic). Given the scope, deletion is simpler.

**Recommended:** Delete `test_config_loader.py`.

**Verification:** `uv run pytest`

---

## Step 6: Final verification

1. Run `uv run pytest`.
2. Manually run Pass 1, Pass 1a, and Pass 2 if feasible to confirm end-to-end behavior.
3. Confirm no remaining references to `config_loader`, `load_entity_types`, or `get_schema_version` in the medlit pipeline.

---

## Summary: What stays vs. what goes

| Item | Action |
|------|--------|
| `--config-dir` in pass1_extract | Remove (schema no longer loaded from dir) |
| `--config-dir` in pass1a_vocab | Remove |
| `--config-dir` in pass2_dedup | Remove |
| `--input-dir`, `--output-dir`, `--bundle-dir` | **Keep** — these are workspace paths |
| `config_loader.py` | Delete |
| `entity_types.yaml`, `predicates.yaml`, `domain_instructions.md` | Delete |
| `test_config_loader.py` | Delete |

---

## Dependency order

1. **Steps 1 + 2** — Run together. Step 1 removes `_normalized_to_bundle_class` from pass1_extract; pass1a_vocab imports it, so Step 2 must update pass1a_vocab in the same batch.
2. Step 3 (dedup) — independent; can run after 1+2.
3. Step 4 (tests) — must be done after Steps 1–3 so tests align with new behavior.
4. Step 5 (deletions) — must be last, after all consumers are migrated.

**Suggested execution order:** (1+2) → 3 → 4 → 5 → 6, with `uv run pytest` after each step.

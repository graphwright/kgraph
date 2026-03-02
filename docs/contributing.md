# Contributing

## Internals

- **summary.md** — Generated codebase overview at repo root (e.g. `git ls-files | uv run python summarize_codebase.py > summary.md`). Keep this file; it is the reference for architecture and module layout (see also root `CLAUDE.md`).
- **kgschema** — Data structures and ABCs only; no business logic. Changes here affect all domains; keep the surface small and stable.
- **kgraph** — Orchestration, promotion, export, canonical_id, storage, pipeline interfaces. New pipeline stages should implement the existing ABCs where possible.
- **kgbundle** — Bundle contract between producer and consumer. Changes to the bundle format require coordination with kgserver and any existing bundles.
- **kgserver** — Query layer and storage backends. New backends implement the same interfaces; avoid server-specific assumptions in the bundle format.

## Extension points

- **Domain**: Implement `DomainSchema`, entity/relationship/document subclasses, and pipeline components (parser, entity extractor, resolver, relationship extractor). See [Adapting to Your Domain](adapting-to-your-domain.md) and the medlit/sherlock examples.
- **Canonical ID**: Implement `CanonicalIdLookupInterface` and optionally `CanonicalIdCacheInterface` for new authorities.
- **Storage**: Implement kgschema storage interfaces for new backends (e.g. another database or vector store).
- **Pipeline**: Implement the pipeline ABCs (DocumentParserInterface, EntityExtractorInterface, etc.) for new extraction or resolution strategies.

## Testing approach

- **pytest** for all packages. Run from repo root: `uv run pytest` (root tests), `uv run pytest kgbundle/tests/`, `uv run pytest kgserver/tests/` (from kgserver with PYTHONPATH for kgbundle).
- Prefer **in-memory storage** and small fixtures so tests are fast and deterministic.
- **Linters**: Run `./lint.sh` (ruff, mypy, black, flake8, pylint, then pytest). See root `CLAUDE.md` for tool order and scope.
- Add tests for new pipeline stages and schema changes; keep coverage for promotion, export, and bundle loading.

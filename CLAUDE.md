# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Knowledge graph system for extracting entities and relationships from documents across multiple knowledge domains (medical literature, legal documents, academic CS papers, etc.). The architecture uses a two-pass ingestion process:

1. **Pass 1 (Entity Extraction)**: Extract entities from documents, assign canonical IDs where appropriate (UMLS for medical, DBPedia URIs cross-domain, etc.)
2. **Pass 2 (Relationship Extraction)**: Identify edges/relationships between entities, produce per-document JSON with edges and provisional entities

### Key Concepts

- **Canonical entities**: Assigned stable IDs from authoritative sources
- **Provisional entities**: Mentions awaiting promotion based on usage count and confidence scores
- **Entity promotion**: Provisional → canonical when usage thresholds are met
- **Entity merging**: Combining canonical entities detected as duplicates via semantic vector similarity

**For detailed project architecture and package-by-package structure**, see **`summary.md`** in the repository root. It contains an overview of the Python codebase and is the reference for components, modules, and how they relate. Keep **`summary.md`** at repo root (do not remove); it is in the list of retained repo files alongside the Track 2 docs.

## Build & Test Commands

```bash
# Setup environment (Python 3.12+)
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"

# Run all tests
uv run pytest

# Run single test file
uv run pytest tests/test_entities.py

# Run single test
uv run pytest tests/test_entities.py::test_canonical_promotion -v
```

## Linters

Preferred linter tools and **order** are defined in **`lint.sh`**. Run that script to lint and test. Order: **ruff** (check, with auto-fix on failure) → **mypy** → **black** (check) → **flake8** → **pylint**, then **pytest**. Scope is `kgraph`, `kgbundle`, `kgschema`, `kgserver`, and `examples`; `kgserver/chainlit/app.py` is excluded from mypy and pylint. If a step fails, `fixes_needed` runs `black` and `ruff check --fix` and exits so you can re-run.

## Python and Testing Conventions

- Prefer **`uv`** for virtualenvs and running commands. Use Python 3.12 or 3.13.
- Use **pydantic** models and **immutable data** (tuple, frozenset, frozendict, or pydantic models with `frozen=True`) where it improves clarity and reliability.
- Use **descriptive** variable and class names. Give pydantic fields meaningful `description` strings.
- **Pytest** for verification. Write tests early; keep them well documented and structured. Run the suite often during development. Prefer tests that do not inhibit refactoring.

## Interface–Implementation and ABCs

Prefer **interface–implementation** separation where it makes sense: define abstract contracts with **ABC (Abstract Base Class)** classes, then provide one or more concrete implementations. This keeps domain logic independent of storage, pipelines, or pluggable strategies.

- **Storage**: `kgschema/storage.py` defines ABCs for entity/relationship storage; kgraph and kgserver provide concrete backends.
- **Domain schema**: `DomainSchema`, `BaseDocument`, and related types in kgschema are abstract; each example (medlit, sherlock) implements them.
- **Promotion**: `PromotionPolicy` in kgraph is an ABC; domain-specific promotion rules are implementations.
- When adding new pluggable behavior (e.g. a new pipeline stage or backend), consider introducing an ABC in the appropriate package and implementing it in the concrete layer rather than hard-coding a single implementation.

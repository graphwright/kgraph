# Sherlock Holmes Knowledge Graph Pipeline

Dense typed knowledge graph extraction from "A Scandal in Bohemia" (Arthur Conan Doyle, 1891).

## Overview

This package builds a rich, entity-typed knowledge graph from the Sherlock Holmes story
"A Scandal in Bohemia" using LLM-driven extraction — the same approach that made the
`medlit` pipeline produce dense graphs (many entity types, semantically specific predicates)
rather than sparse co-occurrence graphs.

## Design goals vs prior approaches

| Feature | Old `wware/sherlock` approach | This pipeline |
|---|---|---|
| Entity types | 1–2 (character, location) | 7 (Character, Location, Story, PhysicalObject, Event, Occupation, Organization) |
| Predicates | `co_occurs_with` only | 27 semantically typed predicates |
| Extraction | Rule-based / co-occurrence | LLM-driven structured extraction |
| Dedup | None | Union-find SAME_AS + alias normalization |
| Provenance | None | DESCRIBED_IN edges + narrator trust levels |
| Output format | Custom | kgbundle JSONL (loadable by kgserver) |
| Graph density | Sparse | Dense (target: 3–5 edges per paragraph) |

## Entity types

| Class | Description |
|---|---|
| `Character` | Persons in the story (Holmes, Watson, Irene Adler, the King…) |
| `Location` | Addresses and places (221B Baker Street, Briony Lodge…) |
| `Story` | The containing narrative (one per ingestion run) |
| `PhysicalObject` | Plot-relevant items (photograph, disguise, telegram, ring…) |
| `Event` | Discrete happenings (staged fire alarm, the King's visit…) |
| `Occupation` | Social roles and titles (detective, king, adventuress, groom…) |
| `Organization` | Institutions and groups (Royal House of Bohemia, Scotland Yard…) |

## Predicates (27 typed predicates)

Spatial: `LIVES_AT`, `VISITS`, `LOCATED_AT`, `PRESENT_AT`, `CONTAINS`  
Possession: `OWNS`, `POSSESSED_BY`  
Knowledge: `KNOWS_ABOUT`, `CONCEALS`, `WITNESSES`  
Social: `ALLY_OF`, `ANTAGONIST_OF`, `TRUSTS`, `DECEIVES`, `HIRED`, `ROMANTICALLY_LINKED_TO`, `MEMBER_OF`  
Identity: `HAS_OCCUPATION`, `DISGUISED_AS`, `SAME_AS`  
Events: `CAUSES`, `PARTICIPATES_IN`, `PRECEDES`  
Inference: `IMPLICATES`, `EXONERATES`, `HAS_MOTIVE`  
Narrative: `APPEARS_IN`, `DESCRIBED_IN`  
Fallback: `ASSOCIATED_WITH`

## Narrator trust metadata

Every relationship carries an epistemic source label (`narrator_trust`):

- `watson_direct` — Watson directly observed this (most reliable)
- `watson_inference` — Watson's own deduction (often wrong)
- `watson_speculation` — Watson explicitly hedges
- `watson_retrospective` — Watson narrates with hindsight
- `holmes_assertion` — Holmes stated this directly
- `holmes_inference` — Holmes's deduction (high trust)
- `third_party` — Reported by another character
- `narrator` — Authorial frame-level fact

## Pipeline

```
sherlock-extract  →  story_{id}.json  →  sherlock-ingest  →  deduped.json  →  sherlock-build-bundle  →  bundle/
```

### 1. Extract

```bash
sherlock-extract --output-dir output/ --llm-backend anthropic
```

Options:
- `--output-dir DIR` — where to write the bundle JSON (default: `output/`)
- `--llm-backend` — `anthropic` (requires `ANTHROPIC_API_KEY`) or `ollama`
- `--story-file FILE` — override with local story text (for offline use)
- `--window-size N` — paragraphs per LLM window (default: 3)
- `--limit-chunks N` — process only first N chunks (for testing)
- `--skip-if-exists` — don't re-run if output already exists

### 2. Ingest (dedup)

```bash
sherlock-ingest --input output/story_scandal_in_bohemia.json --output output/deduped.json
```

Resolves SAME_AS edges, collapses alias fragments into canonical nodes, drops self-loops.

### 3. Build bundle

```bash
sherlock-build-bundle --input output/deduped.json --output-dir bundle/
```

Writes:
- `bundle/entities.jsonl` — entity rows in kgbundle format
- `bundle/relationships.jsonl` — relationship rows with narrator_trust, story_time
- `bundle/evidence.jsonl` — evidence spans
- `bundle/manifest.json` — bundle metadata

## LLM configuration

### Anthropic (Claude)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
sherlock-extract --llm-backend anthropic
```

### Ollama (local)

```bash
ollama pull llama3.2
sherlock-extract --llm-backend ollama
```

## Output

The bundle directory is directly loadable by `kgserver`:

```bash
kgserver serve --bundle bundle/
```

BFS and subgraph queries work out of the box. For "solve the case" analysis:
- Filter relationships by `narrator_trust = "holmes_inference"` for high-confidence edges
- Use `story_time` to order the narrative timeline
- BFS from a character node to find their full connection graph

## Development

```bash
cd sherlock
pip install -e ".[dev]" -e ../kgschema -e ../ -e ../kgbundle
pytest tests/
```

## Key files

| File | Purpose |
|---|---|
| `sherlock/domain_spec.py` | Single source of truth: entity types, predicates, NarratorTrust, extraction prompt |
| `sherlock/bundle_models.py` | Wire format for extraction output (PerStoryBundle) |
| `sherlock/pipeline/parser.py` | Gutenberg fetcher, story chunker (includes embedded fallback excerpt) |
| `sherlock/pipeline/extractor.py` | LLM extraction (async, per-chunk) |
| `sherlock/pipeline/dedup.py` | SAME_AS resolution, alias normalization, entity collapse |
| `sherlock/pipeline/bundle_builder.py` | kgbundle JSONL output + DESCRIBED_IN provenance expansion |
| `sherlock/promotion.py` | DBPedia canonical IDs for well-known entities |

## Borrowed from `wware/sherlock`

- Story identity: `scandal_in_bohemia` as the stable story ID
- The design inspiration for narrator trust as a first-class metadata dimension
- `sherlock_design.md` provided the initial list of entity types and predicate vocabulary

## Adapted from `medlit` (graphwright/kgraph)

- `domain_spec.py` as single source of truth pattern
- `PerStoryBundle` / `PerPaperBundle` wire format pattern
- LLM extraction with structured JSON output per chunk
- Union-find dedup + alias normalization approach
- kgbundle JSONL output format with manifest
- DESCRIBED_IN provenance expansion for graph density
- Async extraction with per-chunk merge

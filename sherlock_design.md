# Sherlock Holmes Example: Design Notes

## Goal

Upgrade the Sherlock example from a thin demo (3 entity types, 5 generic predicates,
no LLM extraction) to a richly specified domain that:

1. Follows the `domain_spec.py` single-source-of-truth pattern from medlit
2. Captures the epistemic complexity of fiction, especially the unreliable narrator
3. Supports a compelling "solve the crime" demo using BFS graph traversal + LLM inference
4. Illustrates the *generality* of the kgraph architecture in the book (Ch. 8, Ch. 13-14)

---

## Time Is Different in Fiction

In medical literature, time is either a physical measurement (duration, age, follow-up
period) or a provenance marker (publication date, which study preceded which). It does
not constrain what entities are *allowed to know*.

In fiction, time is **epistemic**. It governs what each character can possibly know at
any given moment, and therefore which assertions in the graph are valid from which
character's perspective at which point in the narrative. Four distinct time axes apply:

- **Narrative time**: the order in which Watson presents events (chapter/paragraph index)
- **Story time**: the order in which events actually occurred in the world of the story
  (often different — Holmes cases frequently involve flashback and late-revealed backstory)
- **Knowledge time**: when each character actually learned each fact
- **Reader time**: what the reader is permitted to know at each point (deliberately
  controlled by Watson for suspense)

These axes are independent and frequently misaligned. Watson's narration is retrospective:
he writes after the fact but withholds what he knows. Holmes deduces things Watson hasn't
told the reader yet. A suspect's alibi may rest on events that occurred before the crime
but are revealed after it.

For the "solve the crime" demo, the graph must be filterable to *what Holmes could have
known by deduction at the moment of the reveal* — which requires all four axes to be
tracked on assertions.

This is a natural extension of medlit's provenance model, not a departure from it.
The same infrastructure handles both; the schema design work is different.

---

## Unreliable Narrator

Watson is not a neutral recorder. He:
- Reports his own direct observations (most trustworthy)
- Reports what Holmes tells him (Holmes is reliable but may be deliberately withholding)
- Draws his own inferences (often wrong — that's the dramatic point)
- Omits or reorders events for narrative effect
- Occasionally speculates, which he signals with hedged language

The `linguistic_trust` field from medlit (`asserted` | `suggested` | `speculative`)
needs a Sherlock-specific analog that captures *who is asserting* as well as *how
confidently*. Proposed field: `narrator_trust` with values:

| Value | Meaning |
|---|---|
| `watson_direct` | Watson directly observed this |
| `watson_inference` | Watson's own deduction (treat skeptically) |
| `holmes_assertion` | Holmes stated this directly |
| `holmes_inference` | Holmes's deduction (high trust) |
| `third_party` | Reported by another character |
| `watson_speculation` | Watson explicitly hedges ("I fancied", "it seemed to me") |
| `retrospective` | Watson narrating with knowledge he didn't have at the time |

The "solve the crime" demo specifically depends on this: the LLM should be able to
reconstruct Holmes's reasoning chain using only `holmes_assertion`, `holmes_inference`,
and `watson_direct` — ignoring Watson's wrong inferences and speculations.

---

## Richer Schema

### Current entity types (thin demo)
- `Character`, `Location`, `Story`

### Proposed entity types
- `Character` — persons in the story
- `Location` — physical places
- `Story` — the containing narrative (metadata)
- `PhysicalObject` — objects that serve as clues (the dog, the watch, the mud on the boot)
- `CrimeEvent` — the central crime and any related events
- `Clue` — an observation or fact that bears on the solution
- `Motive` — a character's reason to commit or conceal
- `Alibi` — a claimed absence from the scene
- `Occupation` / `SocialRole` — Holmes draws heavily on professional and class markers

### Current predicates (thin demo)
`appears_in`, `co_occurs_with`, `lives_at`, `antagonist_of`, `ally_of`

### Proposed predicates
| Predicate | Subject | Object | Notes |
|---|---|---|---|
| `APPEARS_IN` | Character | Story | retained |
| `PRESENT_AT` | Character | CrimeEvent / Location | with narrative_position |
| `WITNESSED` | Character | CrimeEvent / PhysicalObject | narrator_trust load-bearing |
| `POSSESSED_BY` | PhysicalObject | Character | at a given story_time |
| `LOCATED_AT` | Character / PhysicalObject | Location | at a given story_time |
| `IMPLICATES` | Clue / PhysicalObject | Character | Holmes's inference |
| `EXONERATES` | Clue / Alibi | Character | |
| `CONTRADICTS` | Clue / Statement | Clue / Statement | key for misdirection |
| `ESTABLISHES_ALIBI` | Character | CrimeEvent | |
| `HAS_MOTIVE` | Character | CrimeEvent | |
| `KNOWS_ABOUT` | Character | Clue / CrimeEvent | with knowledge_time |
| `CONCEALS` | Character | Clue / CrimeEvent | Watson sometimes does this narratively |
| `ALLY_OF` | Character | Character | retained |
| `ANTAGONIST_OF` | Character | Character | retained |
| `SAME_AS` | Character | Character | coreference / alias resolution |

---

## Temporal Fields on Assertions

Relationships (and some entity attributes) should carry:

```python
narrative_position: int | None      # paragraph index in Watson's telling
story_time: str | None              # estimated position in story chronology
                                    # (e.g. "before_crime", "day_of", "aftermath")
known_by: frozenset[str] | None     # entity_ids of characters who know this fact
knowledge_time: str | None          # when they learned it (story_time vocabulary)
narrator_trust: NarratorTrust       # see enum above
```

These fields are analogous to medlit's `linguistic_trust` and provenance fields —
they attach epistemic metadata to the assertion rather than treating all graph
edges as equally reliable.

---

## The "Solve the Crime" Demo

**Setup:** Ingest a self-contained story (good candidates: *Silver Blaze*,
*The Speckled Band*, *The Adventure of the Blue Carbuncle*) up to but not
including the reveal chapter.

**Query:** BFS traversal from the `CrimeEvent` node, filtered to:
- `narrator_trust` in `{holmes_assertion, holmes_inference, watson_direct}`
- `narrative_position` ≤ penultimate chapter

**Prompt to LLM:** "Given the following graph of entities and relationships
extracted from this story, who committed the crime and how did they do it?
Reason step by step, citing specific edges."

**What this demonstrates:**
- The graph's epistemic filtering capability (narrator trust + narrative time)
- Multi-hop traversal surfacing non-obvious connections
- LLM reasoning *from structure* rather than from prose memorization
- The `CONTRADICTS` predicate catching the misdirection Holmes exploits
- That the same infrastructure that handles medical literature handles fiction

This is a strong set piece for Ch. 13 ("What Your Graph Can Do") and Ch. 14
("The Augmented Researcher").

---

## Implementation Plan

1. Create `sherlock/sherlock/domain_spec.py` following the medlit pattern:
   - `EntitySpec` for each entity type with descriptions and prompt guidance
   - `PredicateSpec` for each predicate with subject/object type constraints
   - `PROMPT_INSTRUCTIONS` covering narrator trust classification
   - `NarratorTrust` enum
   - Temporal field definitions

2. Refactor `domain.py` to import from `domain_spec.py` rather than defining
   everything inline (same split as medlit `domain.py` / `domain_spec.py`)

3. Replace the current rule-based `relationships.py` extractor with an LLM-based
   extractor (same pattern as medlit's `ner_extractor.py` + `relationships.py`)

4. Add temporal fields to the Sherlock relationship base class or as metadata

5. Pick one story and run end-to-end; tune prompt until narrator trust
   classification is reliable

6. Build the "solve the crime" query as a script or notebook

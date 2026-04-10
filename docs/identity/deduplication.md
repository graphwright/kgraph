# Deduplication

> **Placeholder** — this page needs to be written.

Deduplication handles the case where two entity records refer to the same real-world
thing but have not yet been linked by canonical ID — either because both are provisional,
or because authority lookup returned different IDs that are actually synonymous.

## When dedup runs

Dedup runs after resolution, as a pass over the entity table. It looks for near-duplicate
pairs and either merges them (if confidence is high) or flags them for review.

## Signals used

- **Name similarity** — string distance, normalized forms, known synonyms.
- **Embedding similarity** — semantic distance between entity description embeddings.
- **Type agreement** — two entities of different declared types are rarely the same thing.
- **Co-occurrence** — entities that appear together in the same contexts are more likely
  to be distinct.

## Merge vs. flag

- **Merge** — one entity absorbs the other; all edges are rewritten to the survivor.
  The absorbed entity's ID is recorded as an alias.
- **Flag** — the pair is marked as a candidate merge and surfaced for human review.
  Useful when confidence is below threshold or types conflict.

## Provenance impact

When entities are merged, provenance is preserved: every source mention that pointed
to either entity continues to be recorded. The audit trail is never collapsed.

## See also

- [Canonical IDs and Entity Resolution](canonical-ids.md)

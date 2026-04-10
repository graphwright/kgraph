# Conflicting Claims

> **Placeholder** — this page needs to be written.

Scientific and legal literature routinely contains contradictory claims. A graph that
silently resolves conflicts by picking a winner destroys information. This framework
represents disagreements explicitly.

## What counts as a conflict

Two relationships conflict when they share the same subject and object entities and
the same (or inverse) predicate, but differ in:

- **Polarity** — one asserts the relationship holds; another asserts it does not.
- **Magnitude** — one claims a drug increases a biomarker; another claims it decreases it.
- **Conditionality** — the relationship holds under one set of conditions but not another.

## How conflicts are stored

Conflicting edges are stored as separate relationship nodes, each with its own
provenance. A `conflict_group` tag links them so that query interfaces can surface
the disagreement rather than arbitrarily returning one result.

## Resolution strategies

The framework does not resolve conflicts automatically. Options for downstream users:

- **Surface all** — return all conflicting claims with provenance; let the user judge.
- **Weight by confidence** — rank claims by confidence score, but show the others.
- **Flag for review** — mark the conflict group for human curation.
- **Domain rules** — a domain pipeline may define rules (e.g. "prefer randomized trials
  over case reports") that influence display order without discarding minority claims.

## See also

- [Trust and Provenance](provenance.md)

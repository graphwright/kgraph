# Error Handling

> **Placeholder** — this page needs to be written.

Ingestion pipelines fail in predictable ways: LLMs return malformed JSON, authority
lookups time out, documents are corrupt. This page covers how the framework handles
partial failures without losing work.

## Failure modes

- **Parse failure** — the document cannot be parsed (wrong format, encoding error).
- **Extraction failure** — the LLM returns output that does not validate against the
  expected schema.
- **Resolution failure** — the authority lookup times out or returns no result.
- **Embedding failure** — the embedding model is unavailable.

## Design principles

- **Partial progress is preserved.** If pass 1 completes but pass 2 fails halfway
  through, the completed work is not discarded. The pipeline can resume from the
  last checkpoint.
- **Failures are recorded, not swallowed.** Each failure is written to an error log
  with the document ID, stage, and exception. Silent failures are not acceptable.
- **Retries are bounded.** Transient failures (network timeouts) are retried with
  exponential backoff. Persistent failures are surfaced after a configurable retry limit.

## Extraction validation and fallback

When the LLM returns output that fails Pydantic validation:

1. Log the raw output and the validation error.
2. Optionally retry with a repair prompt.
3. If repair fails, mark the chunk as `extraction_failed` and continue.

Chunks marked `extraction_failed` are included in the run report so they can be
reviewed and reprocessed.

## Resumable runs

The pipeline writes a checkpoint file after each document completes. On restart, already-
processed documents are skipped. This makes large ingestion runs safe to interrupt.

## See also

- [Pipeline](pipeline.md)

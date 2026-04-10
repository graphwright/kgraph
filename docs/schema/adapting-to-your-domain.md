# Adapting to Your Domain

> **Placeholder** — content to be migrated and expanded from
> [`../adapting-to-your-domain.md`](../adapting-to-your-domain.md).

Step-by-step guide to implementing the framework for a new domain.

## Step 1: Define your schema

Implement `DomainSchema` with your entity types, relationship types, and document type.
Start minimal — add types as you discover them during extraction experiments, not upfront.

See [Schema Design Guide](schema-design-guide.md).

## Step 2: Write extraction prompts

Write entity and relationship extraction prompts tailored to your domain's vocabulary
and document structure. Test them manually on a sample of documents before wiring
them into the pipeline.

See [Prompt Design for Extraction](../llm-integration/extraction-prompts.md).

## Step 3: Implement pipeline components

Implement the parser, extractor, and resolver interfaces for your document format
and authority sources. Use the Sherlock or medlit examples as reference.

## Step 4: Seed the synonym cache

If your domain has a known controlled vocabulary (MeSH headings, drug name lists,
etc.), seed the synonym cache before running ingestion. This dramatically improves
resolution accuracy for the first run.

## Step 5: Run and validate

Run pass 1 on a small document set. Inspect:

- Entity extraction rate (mentions per chunk).
- Resolution rate (what fraction resolved to canonical IDs).
- Provisional entity count (high count → authority lookup gaps or prompt issues).

Then run pass 2 and inspect relationship counts and types.

## Step 6: Iterate

Adjust prompts, add entity types, or extend the synonym cache based on inspection.
Re-run on the validation set. Repeat until quality is acceptable.

## See also

- [Schema Design Guide](schema-design-guide.md)
- [Examples: medlit](../examples/medlit.md)
- [Examples: Sherlock](../examples/sherlock.md)

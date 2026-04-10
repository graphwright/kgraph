# Prompt Design for Extraction

> **Placeholder** — this page needs to be written. See also
> [`../schema/adapting-to-your-domain.md`](../schema/adapting-to-your-domain.md)
> for the step-by-step workflow.

Extraction quality depends heavily on prompt design. This page covers principles and
patterns for writing prompts that produce reliable, schema-conformant output.

## General principles

- **Be explicit about schema.** Include the entity and relationship type names from
  your `DomainSchema` directly in the prompt. Don't assume the LLM will infer them.
- **Show examples.** Few-shot examples of (chunk → extracted JSON) dramatically
  improve consistency, especially for relationship extraction.
- **Ask for confidence.** Instruct the LLM to include a confidence score for each
  extraction. This feeds into the provenance model.
- **Constrain output format.** Ask for JSON matching the Pydantic schema. Validate
  the response immediately; retry with a repair prompt on failure.

## Entity extraction prompt structure

```
You are extracting {entity_type} entities from the following text.
Return a JSON array of objects matching this schema: {schema_json}.
Include only entities explicitly mentioned in the text.
For each entity, include a confidence score from 0.0 to 1.0.

Text:
{chunk_text}
```

## Relationship extraction prompt structure

```
Given the following resolved entities: {entity_list}
Extract relationships from the text below.
Valid relationship types: {relationship_types}.
Return a JSON array matching this schema: {schema_json}.

Text:
{chunk_text}
```

## Domain-specific tuning

See [Adapting to Your Domain](../schema/adapting-to-your-domain.md) for how to
write domain-specific prompt variants and validate them against a labeled test set.

## See also

- [Schema Design Guide](../schema/schema-design-guide.md)
- [Adapting to Your Domain](../schema/adapting-to-your-domain.md)

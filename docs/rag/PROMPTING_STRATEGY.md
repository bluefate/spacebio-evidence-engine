# Prompting Strategy

## Purpose
Define how prompts enforce grounded, citation-first answers.

## Scope
Answer generation, sufficiency checking, study comparison, entity extraction, and gap identification.

## Current status
Initial strategy.

## Prompt requirements
- Use only retrieved passages.
- Cite claims with passage IDs.
- State when evidence is insufficient.
- Distinguish evidence from inference.
- Preserve limitations and uncertainty.
- Avoid medical or mission recommendations.
- Version prompts and evaluate prompt changes.

## Provider abstraction
Prompts must not assume a single LLM provider. OpenAI models may be used when configured, but the application must isolate provider-specific code.

## Related documents
- [Citation strategy](CITATION_STRATEGY.md)
- [Evaluation strategy](EVALUATION_STRATEGY.md)
- [RAG architecture](../architecture/RAG_ARCHITECTURE.md)

## Human decisions still required
- Approve prompt templates before implementation.
- Decide whether prompt outputs must use strict JSON for selected tasks.


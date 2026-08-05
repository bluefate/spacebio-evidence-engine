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

Application code should call `spacebio_evidence_engine.llm.LanguageModelProvider` (`generate` / `chat`) with prompt text assembled elsewhere. Optional structured outputs use `GenerateRequest.structured_output` / `ChatRequest.structured_output` (JSON Schema maps). Token usage, when reported, lands in `GenerationResult.usage` (`UsageMetadata`) for the $50/mo LLM cap (D4). Concrete OpenAI (or other) clients are follow-on issues — not imported from the interface module (issue #51).

## Related documents
- [Citation strategy](CITATION_STRATEGY.md)
- [Evaluation strategy](EVALUATION_STRATEGY.md)
- [RAG architecture](../architecture/RAG_ARCHITECTURE.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).


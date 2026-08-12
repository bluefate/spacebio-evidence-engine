# Prompting Strategy

## Purpose
Define how prompts enforce grounded, citation-first answers.

## Scope
Answer generation, sufficiency checking, study comparison, entity extraction, and gap identification.

## Current status
Context assembly (`assemble_context`, #52) and the versioned grounded-answer
prompt template (`prompts/grounded_answer_v1.0.0.md`, #53) are implemented.
Passage-level citation emission and `/ask` wiring remain follow-on.

## Prompt requirements
- Use only retrieved passages.
- Cite claims with passage IDs.
- State when evidence is insufficient.
- Distinguish evidence from inference.
- Preserve limitations and uncertainty.
- Avoid medical or mission recommendations.
- Version prompts and evaluate prompt changes.

## Grounded answer prompt template

Versioned template file: [`prompts/grounded_answer_v1.0.0.md`](../../prompts/grounded_answer_v1.0.0.md)

Render with:

```python
from spacebio_evidence_engine.rag import assemble_context, render_grounded_answer_prompt

context = assemble_context(hits)
prompt = render_grounded_answer_prompt(question, context)
request = prompt.to_chat_request()  # or prompt.to_generate_request()
```

The template:

- is versioned in-repo (`prompt_id=grounded_answer`, `version=1.0.0`)
- requires use-only-retrieved-evidence behavior and citation IDs
- instructs insufficient-evidence handling when support is missing
- forbids medical advice and mission/operations recommendations
- separates system policy from the user question + evidence blocks

Bump the filename/version (for example `v1.1.0`) when the prompt text changes,
and update `GROUNDED_ANSWER_PROMPT_VERSION` in
`spacebio_evidence_engine.rag.prompt`.

## Context assembly

`assemble_context` builds model-facing text from ranked `SemanticSearchHit`
rows before any LLM call:

- **Instructions and evidence are separated** (`### Instructions` then
  `### Evidence`) so system guidance is not mixed into source passages.
- Every included block keeps `chunk_id`, `publication_id`, title, section,
  pages, and `source_url`, plus a stable citation id (`C1`, `C2`, …).
- An evidence **token budget** (default 2400 whitespace-estimated tokens) is
  enforced. When a hit cannot fit, its `chunk_id` is recorded in
  `omitted_chunk_ids` — citation IDs are never dropped silently.
- Excerpts may be truncated to fit remaining budget, but provenance headers
  and `chunk_id` are never stripped from included blocks.
- The assembler also returns `PassageCitation` objects for downstream citation
  wiring (#54+).

## Insufficient evidence handling

Before any prompt is sent to the language model, the pipeline evaluates whether the retrieved evidence is strong enough to ground an answer.

- **Sufficiency policy (MVP default):** at least 3 retrieved passages and at least 2 distinct supporting publications. This is intentionally conservative to prevent the model from generalizing from sparse or single-study evidence.
- If retrieval is **empty** or **below the threshold**, the system must not call the LLM.
- The response is a fixed, citation-free `GroundedAnswerResponse` with `sufficiency.status = "insufficient"` and an explanatory `reason`.
- The answer text is: "Insufficient evidence in the controlled corpus to answer this question."

This rule is enforced by `spacebio_evidence_engine.rag.sufficiency` (issue #55).

## Provider abstraction
Prompts must not assume a single LLM provider. OpenAI models may be used when configured, but the application must isolate provider-specific code.

Application code should call `spacebio_evidence_engine.llm.LanguageModelProvider` (`generate` / `chat`) with prompt text from `render_grounded_answer_prompt` (or `GroundedAnswerPrompt.to_chat_request` / `to_generate_request`). Optional structured outputs use `GenerateRequest.structured_output` / `ChatRequest.structured_output` (JSON Schema maps). Token usage, when reported, lands in `GenerationResult.usage` (`UsageMetadata`) for the $50/mo LLM cap (D4). Concrete OpenAI (or other) clients are follow-on issues — not imported from the interface module (issue #51).

## Related documents
- [Citation strategy](CITATION_STRATEGY.md)
- [Evaluation strategy](EVALUATION_STRATEGY.md)
- [RAG architecture](../architecture/RAG_ARCHITECTURE.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).


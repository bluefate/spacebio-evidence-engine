# Evaluation Strategy

## Purpose
Define how retrieval, grounding, citations, and answer quality are tested.

## Scope
MVP evaluation using benchmark questions, automated checks, and human review.

## Current status
August MVP reference question set drafted (issue #26). Machine fixture:
[`evals/fixtures/reference_questions.json`](../../evals/fixtures/reference_questions.json).
Human-readable index: [REFERENCE_QUESTIONS.md](REFERENCE_QUESTIONS.md).
**Scientific review of questions is pending owner approval.**

## Evaluation areas
- Retrieval relevance.
- Citation correctness.
- Unsupported-claim rate.
- Insufficient-evidence behavior.
- Study comparison accuracy.
- Entity extraction quality.
- Regression stability after prompt, model, or chunking changes.

## MVP artifacts
- Benchmark question set (**10** reference questions; styles: factual lookup, comparison, sufficiency).
- Expected source publications or passages (candidate publication IDs in the fixture; passage IDs after ingest).
- Evaluation notebooks (follow-on).
- Automated tests for citation integrity (follow-on).
- Human review notes for scientific correctness (`human_scientific_review` in the fixture).

## Reference question rules
- Questions target topic `microgravity_skeletal_muscle` only.
- `should_be_answerable: false` items must exercise the insufficient-evidence path.
- Candidate publication IDs must exist in `data/inventory/august_mvp_corpus_manifest.csv`.
- Do not treat the fixture as gold passage answers until PDFs are ingested and spans exist.

## Related documents
- [Reference questions](REFERENCE_QUESTIONS.md)
- [Testing strategy](../development/TESTING_STRATEGY.md)
- [Retrieval strategy](RETRIEVAL_STRATEGY.md)
- [Citation strategy](CITATION_STRATEGY.md)
- [Corpus inventory](../data/CORPUS_INVENTORY.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).

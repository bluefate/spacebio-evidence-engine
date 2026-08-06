# Evaluation Strategy

## Purpose
Define how retrieval, grounding, citations, and answer quality are tested.

## Scope
MVP evaluation using benchmark questions, automated checks, and human review.

## Current status
August MVP reference question set drafted (issue #26). Machine fixture:
[`evals/fixtures/reference_questions.json`](../../evals/fixtures/reference_questions.json).
Human-readable index: [REFERENCE_QUESTIONS.md](REFERENCE_QUESTIONS.md).
**Scientific review of questions is approved** (`human_scientific_review=approved` in the fixture; follow-up [#94](https://github.com/bluefate/spacebio-evidence-engine/issues/94)).

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
- Offline hallucination check (`evals/hallucination_check.py`) for fixture
  `GroundedAnswerResponse` payloads. The MVP metric flags claim-like answer
  sentences that lack citation markers when evidence is sufficient or marginal,
  and verifies insufficient-evidence responses clearly decline without citations.
- Machine-readable hallucination metrics: `unsupported_claim_count`,
  `claim_sentence_count`, `cited_claim_sentence_count`, and `cited_claim_rate`.
- Automated tests for citation integrity (follow-on).
- Human review notes for scientific correctness (`human_scientific_review` in the fixture).

## Hallucination check

Run the deterministic fixture check:

```bash
python evals/hallucination_check.py evals/fixtures/hallucination_answers.json --json
```

The command exits non-zero when unsupported claims are detected, making failures
actionable in CI or local reports. It is not a substitute for human scientific
review: it checks citation-marker discipline and insufficient-evidence behavior,
while deeper citation support precision/recall remains issue #59.

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

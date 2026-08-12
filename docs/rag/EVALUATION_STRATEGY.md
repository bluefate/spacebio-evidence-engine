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
- Offline retrieval evaluation harness (`evals/retrieval_eval.py`) for an already
  migrated and indexed corpus database. The harness runs semantic vector search
  over the approved microgravity + skeletal muscle reference questions, records
  retrieved chunk IDs, ranks, scores, publication IDs, section/page provenance,
  source URLs, and computes publication-level hit-rate / rank metrics.
- Offline hallucination check (`evals/hallucination_check.py`) for fixture
  `GroundedAnswerResponse` payloads. The MVP metric flags claim-like answer
  sentences that lack citation markers when evidence is sufficient or marginal,
  and verifies insufficient-evidence responses clearly decline without citations.
- Machine-readable hallucination metrics: `unsupported_claim_count`,
  `claim_sentence_count`, `cited_claim_sentence_count`, and `cited_claim_rate`.
- Offline citation correctness check (`evals/citation_correctness.py`) for
  fixture `GroundedAnswerResponse` payloads plus retrieved citation context.
  The MVP check verifies emitted citation IDs are backed by retrieved chunk IDs,
  answer citation markers reference emitted citations, and optional per-claim
  fixture labels report citation precision/recall. It preserves publication ID,
  title, section, page, source URL, and chunk provenance in fixtures/reports.
- Human review notes for scientific correctness (`human_scientific_review` in the fixture).

## Retrieval evaluation

Run the deterministic retrieval harness against an indexed local corpus:

```bash
python evals/retrieval_eval.py \
  --database-url "$DATABASE_URL" \
  --reference-questions evals/fixtures/reference_questions.json \
  --output evals/artifacts/retrieval_eval.json \
  --top-k 8
```

The default results artifact path is `evals/artifacts/retrieval_eval.json`.
The artifact is JSON and includes:

- run metadata: schema version, timestamp, topic, provider model, top-k, and
  reference question fixture path
- aggregate metrics: `hit_rate`, `mean_reciprocal_rank`,
  `mean_first_relevant_rank`, `hit_count`, and unanswerable-question hit count
- per-question metrics: expected publication IDs, first relevant rank,
  reciprocal rank, relevant hit count, and unexpected hits for sufficiency items
- retrieved evidence records: rank, chunk ID, score, publication ID, title,
  section, source URL, page range, section heading, embedding model, and whether
  the chunk came from an expected candidate publication

For the August MVP, relevance is scored against the candidate publication IDs in
the approved reference-question fixture because passage IDs are not gold labels
until the PDFs are fully ingested and spans exist. The harness does not perform
LLM judging, answer generation, `/ask` wiring, hybrid search, or domain expansion.

## Hallucination check

Run the deterministic fixture check:

```bash
python evals/hallucination_check.py evals/fixtures/hallucination_answers.json --json
```

The command exits non-zero when unsupported claims are detected, making failures
actionable in CI or local reports. It is not a substitute for human scientific
review: it checks citation-marker discipline and insufficient-evidence behavior,
while deeper citation support precision/recall remains issue #59.

## Citation correctness check

Run the deterministic citation correctness fixture check:

```bash
python evals/citation_correctness.py evals/fixtures/citation_correctness_answers.json --json
```

The command exits non-zero when an answer emits citations that were not in
retrieved context, uses answer markers that were not emitted, emits unused
citations, or misses/overstates expected support in fixture `claim_checks`.
Machine-readable metrics include `citation_id_precision`,
`answer_marker_precision`, `claim_citation_precision`, and
`claim_citation_recall`.

For August MVP this checker is deliberately bounded: it does not call an LLM,
does not run retrieval, does not wire `/ask`, and does not infer scientific
truth from model knowledge. Claim-level precision/recall is only computed
against explicit fixture labels so unsupported scientific conclusions are not
invented by the evaluator.

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

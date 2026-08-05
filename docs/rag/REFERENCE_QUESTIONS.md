# Reference research questions (August MVP)

## Purpose

Provide ten evaluation questions for retrieval and grounded-answer testing on the **microgravity and skeletal muscle** corpus (issue [#26](https://github.com/bluefate/spacebio-evidence-engine/issues/26)).

## Status

**Owner-approved** (human scientific review). Machine-readable source of truth:

[`evals/fixtures/reference_questions.json`](../../evals/fixtures/reference_questions.json)

| Field | Meaning |
| --- | --- |
| `human_scientific_review` | `approved` after owner scientific review (was `pending`) |
| `style` | `factual_lookup` \| `comparison` \| `sufficiency` |
| `expected_evidence.should_be_answerable` | Whether the controlled corpus should support an answer in principle |
| `candidate_publication_ids` | Likely inventory anchors (not gold passage IDs until ingest) |

## Style coverage

| Style | Question IDs |
| --- | --- |
| Factual lookup | `rq_01`, `rq_02`, `rq_03`, `rq_04`, `rq_10` |
| Comparison | `rq_05`, `rq_06`, `rq_07` |
| Sufficiency (expect insufficient evidence) | `rq_08`, `rq_09` |

## Questions (summary)

1. **rq_01** — Astronaut ISS skeletal muscle proteome changes (human spaceflight).
2. **rq_02** — Hindlimb unloading effects on mouse skeletal muscle.
3. **rq_03** — Simulated microgravity on 3D engineered skeletal muscle.
4. **rq_04** — Review-level atrophy mechanisms and countermeasures.
5. **rq_05** — Compare human spaceflight vs mouse HU models.
6. **rq_06** — Partial-gravity levels (~0.33g vs ~0.67g) and muscle outcomes.
7. **rq_07** — Radiation + unloading vs unloading alone.
8. **rq_08** — Clinical Mars drug regimen (expect **insufficient**).
9. **rq_09** — Cardiac ejection fraction in this corpus (expect **insufficient**).
10. **rq_10** — Countermeasures / interventions against unloading atrophy.

## Eval rules

- Product answers must use retrieved corpus evidence only.
- Label organism model and exposure; do not merge human/animal/in-vitro without labels.
- Treat abstracts/reviews carefully; prefer methods/results passages when available.
- For `should_be_answerable: false`, the system should take the insufficient-evidence path.

## Human review checklist

Owner confirmed (PR [#92](https://github.com/bluefate/spacebio-evidence-engine/pull/92) comment; follow-up [#94](https://github.com/bluefate/spacebio-evidence-engine/issues/94)):

- [x] Questions are scientifically appropriate for the topic
- [x] Candidate publication anchors are reasonable
- [x] Sufficiency negatives are fair (not answerable from this corpus)
- [x] `human_scientific_review` set to `approved` in the JSON

## Related documents

- [Evaluation strategy](EVALUATION_STRATEGY.md)
- [Corpus inventory](../data/CORPUS_INVENTORY.md)
- [Citation strategy](CITATION_STRATEGY.md)

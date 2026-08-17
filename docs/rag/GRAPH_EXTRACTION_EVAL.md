# Graph extraction evaluation (issue #75)

## Purpose

Measure mention-level and Finding-presence precision/recall for the experimental
gazetteer extractor (`src/spacebio_evidence_engine/graph/extract.py`) against a
small human-labeled fixture. This is not a gold-label eval of ingested PDFs and
is not a `/ask` quality gate.

## Labeled sample

[`evals/fixtures/graph_extraction_labels.json`](../../evals/fixtures/graph_extraction_labels.json)
contains five passages:

| Chunk | Role |
| --- | --- |
| `chk_mouse_hu_atrophy` | Gazetteer true positives (mouse HU atrophy); expected Finding |
| `chk_human_iss_proteome` | Gazetteer true positives (human ISS proteome); no Finding (assay, not outcome) |
| `chk_no_match` | Negative control (avionics) |
| `chk_c2c12_fn` | Cell line + atrophy + microgravity; CellType not in gazetteer |
| `chk_radiation_fp` | Off-topic “radiation oncology”; Exposure false positive |

Gold mentions are `(chunk_id, entity_type, preferred_label)` tuples. Finding
labels use `expect_finding` on each passage.

## How to run

```bash
make eval-graph-extraction
# or
python evals/graph_extraction_eval.py --json
```

The script always exits `0` when the fixture is valid (measurement only).
`make validate` does not run this check. Pytest smoke:
`pytest -q tests/test_graph_extraction_eval.py`.

## Reported metrics (fixture run 2026-08-17)

| Metric | Value |
| --- | --- |
| Mention precision | 0.909 (10 / 11) |
| Mention recall | 0.909 (10 / 11) |
| Mention F1 | 0.909 |
| Finding precision | 1.000 (1 / 1) |
| Finding recall | 0.500 (1 / 2) |

## Error categories

| Category | Count | Example |
| --- | --- | --- |
| `false_positive_mention` | 1 | `chk_radiation_fp` Exposure `radiation` from substring match in “radiation oncology” |
| `false_negative_mention` | 1 | `chk_c2c12_fn` CellType `C2C12` — not in the gazetteer |
| `false_negative_finding` | 1 | Same C2C12 passage: Finding requires Organism + Outcome; CellType is not Organism |
| `false_positive_finding` | 0 | — |

## Interpretation

The gazetteer is high-precision on in-vocabulary space-biology phrases and fails
on (1) out-of-gazetteer cell lines and (2) domain-ambiguous tokens such as
`radiation`. Finding emission is conservative: organism-less cell-culture
outcomes are missed. Human validation of live corpus graphs remains issue #76.
Do not treat these scores as production accuracy.

## Related documents

- [Evaluation strategy](EVALUATION_STRATEGY.md)
- [Graph extraction prototype](../data/GRAPH_EXTRACTION_PROTOTYPE.md)
- [Candidate entity types](../data/GRAPH_ENTITY_TYPES.md)

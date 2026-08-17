# Notebooks

Reproducible review notebooks for corpus and evaluation work.

## Corpus inventory

`corpus_inventory.ipynb` loads the approved August MVP manifest, validates it
with `spacebio_evidence_engine.corpus.CorpusInventoryRecord`, summarizes source
and provenance fields, then writes and reads a review copy using the approved
CSV schema.

Run from the repository root:

```bash
jupyter notebook notebooks/corpus_inventory.ipynb
```

The notebook uses only repository Python helpers. Optional environment
variables make smoke execution deterministic:

- `SPACEBIO_INVENTORY_MANIFEST`: input manifest path; defaults to
  `data/inventory/august_mvp_corpus_manifest.csv`.
- `SPACEBIO_INVENTORY_REVIEW_OUTPUT`: output CSV path; defaults to
  `notebooks/generated/corpus_inventory_review.csv`.

Generated notebook outputs under `notebooks/generated/` are review artifacts and
do not need to be committed.

## Graph extraction (experimental)

Issue #74 is tested Python, not a notebook. See
[experiments/graph_extraction/README.md](../experiments/graph_extraction/README.md).
Do not use it for production answers.


# Experimental graph extraction (issue #74)

**Not for production.** This prototype must not feed `/ask`, citations, or a
live graph database. Every extracted node and edge is `unverified`.

## What it does

Rule-based gazetteer matching over fixture (or caller-supplied) passages.
Outputs include `chunk_id` on every entity and relationship, `mentions`
edges, and a `Finding` with `supported_by` when a passage names both an
organism and an outcome.

Code: `spacebio_evidence_engine.graph.extract`  
Catalogs: [GRAPH_ENTITY_TYPES.md](../../docs/data/GRAPH_ENTITY_TYPES.md),
[GRAPH_RELATIONSHIP_TYPES.md](../../docs/data/GRAPH_RELATIONSHIP_TYPES.md)

## Run

From the repository root:

```bash
pytest -q tests/test_graph_extraction.py
python -m spacebio_evidence_engine.graph --fixture tests/fixtures/graph_extraction_passages.json
```

Accuracy measurement is [#75](https://github.com/bluefate/spacebio-evidence-engine/issues/75).
Human validation is [#76](https://github.com/bluefate/spacebio-evidence-engine/issues/76).

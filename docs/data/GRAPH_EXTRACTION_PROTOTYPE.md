# Graph extraction prototype (issue #74)

## Purpose

Document the **experimental** passage extractor that emits unverified graph
entities and relationships with mandatory `chunk_id` provenance.

## Scope

Post-August research only. **Not production.** Do not send these objects into
grounded answers, citation emission, or a graph database.

Implementation: `spacebio_evidence_engine.graph` (gazetteer, not an LLM).
How to run: [experiments/graph_extraction/README.md](../../experiments/graph_extraction/README.md).

## Behavior

- Input: passages with `chunk_id`, `publication_id`, and `chunk_text`.
- Output: `ExtractionResult` with `experimental=true` and
  `warning=EXPERIMENTAL_NOT_FOR_PRODUCTION`.
- Entities and relationships set `verification_status=unverified` and
  `extraction_method=gazetteer`.
- Epistemic qualifier is always `associates` (no causation upgrade).
- Human and mouse mentions stay distinct; the prototype never emits
  `contradicts`.

## Related documents

- [Candidate graph entity types](GRAPH_ENTITY_TYPES.md)
- [Candidate graph relationship types](GRAPH_RELATIONSHIP_TYPES.md)
- [Knowledge graph use cases](../architecture/KNOWLEDGE_GRAPH_USE_CASES.md)

## Decision status

Research prototype. Accuracy eval is issue #75. Human validation is #76.

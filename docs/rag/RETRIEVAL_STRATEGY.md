# Retrieval Strategy

## Purpose
Define how relevant passages are found for search and question answering.

## Scope
MVP retrieval over PostgreSQL and pgvector.

## Current status
Initial strategy.

## MVP strategy
- Embeddings: local Sentence Transformers (`all-MiniLM-L6-v2`).
- Store vectors in pgvector.
- Vector-only search (hybrid keyword retrieval deferred post-August).
- Default top-k: 8; no reranker for August MVP.
- Filter by corpus topic, organism, system, exposure, and publication metadata when available.
- Return ranked passages with citation metadata.

## Future strategy
Reranking, query decomposition, ontology expansion, and graph-assisted retrieval may be added later.

## Related documents
- [RAG architecture](../architecture/RAG_ARCHITECTURE.md)
- [Evaluation strategy](EVALUATION_STRATEGY.md)
- [Data architecture](../architecture/DATA_ARCHITECTURE.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).


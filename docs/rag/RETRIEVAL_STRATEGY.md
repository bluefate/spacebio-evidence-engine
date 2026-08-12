# Retrieval Strategy

## Purpose
Define how relevant passages are found for search and question answering.

## Scope
MVP retrieval over PostgreSQL and pgvector.

## Current status
Initial strategy. The vector storage schema exists and the indexing job writes
chunk embeddings with provider/model lineage before semantic search is wired.

## MVP strategy
- Embeddings: local Sentence Transformers (`all-MiniLM-L6-v2`).
- Store vectors in pgvector.
- Indexing embeds chunks with the configured provider and writes one
  `chunk_embeddings` row per chunk. By default indexing is idempotent: chunks
  already indexed for the current provider model are skipped. Explicit reindex
  mode rewrites existing vectors for that model.
- Indexing progress is reported as a structured summary with status, scanned
  chunk count, embedded chunk count, updated chunk count, provider model, vector
  dimension, and indexed chunk IDs.
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

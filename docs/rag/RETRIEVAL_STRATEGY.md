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
  `chunk_embeddings` row per chunk. By default indexing is idempotent for a
  given `model_name`: chunks already indexed for the current provider model are
  skipped (counted in `skipped_chunks`). Default mode does **not** invalidate
  vectors when `chunk_text` / `content_hash` changes; after re-chunking, run
  with `reindex=True` (or switch models) so vectors are rewritten.
- Explicit `reindex=True` force-embeds every selected chunk with the current
  provider, including rows previously tagged with a different `model_name`.
- Indexing progress is reported as a structured summary with status, scanned
  chunk count, embedded / skipped / updated counts, provider model, vector
  dimension, and indexed chunk IDs.
- Semantic search (#44) must filter `chunk_embeddings.model_name` to the query
  embedding provider's model so mixed-model corpora are not compared.
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

# Retrieval Strategy

## Purpose
Define how relevant passages are found for search and question answering.

## Scope
MVP retrieval over PostgreSQL and pgvector.

## Current status
Vector storage (#42), indexing (#43), semantic search (#44), full-text search
(#45), hybrid RRF fusion (#46), shared metadata filters (#47), and optional
lexical reranking (#48, disabled by default) are implemented.

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
- Semantic search (`spacebio_evidence_engine.retrieval.semantic_search`) embeds
  the query with the configured provider, filters
  `chunk_embeddings.model_name` to that provider's model, optionally applies
  validated metadata filters, and returns top-k hits with cosine similarity
  scores plus provenance (`chunk_id`, `publication_id`, title, section, pages,
  `source_url`, `chunk_text`, `model_name`). Default `k` is 8. PostgreSQL uses
  pgvector cosine distance (`<=>`); SQLite CI ranks in process over stored
  vectors.
- Full-text search (`spacebio_evidence_engine.retrieval.keyword_search`) ranks
  chunks using a PostgreSQL `tsvector` generated from `chunk_text` and a GIN
  index on `chunks.search_tsv`. It works without embeddings and accepts the
  same metadata filters. It returns `KeywordSearchHit` objects with
  `ts_rank_cd` scores and full provenance. SQLite CI uses a substring fallback
  with term-overlap scoring.
- **Retrieval filter API (#47):** `RetrievalFilters` /
  `parse_retrieval_filters` / `apply_retrieval_filters` document and enforce
  approved keys: `corpus_topic`, `organism_model`, `exposure`,
  `publication_id`, `section`, `license_status`, `year`, `human_approval`.
  Unknown keys, blank strings, and invalid `year` values raise
  `InvalidRetrievalFilterError`. Both `semantic_search` and `keyword_search`
  apply the same filters before ranking.
- Vector-only search is the default MVP path; hybrid fusion (#46) is available
  via `hybrid_search(..., channels=("semantic", "fts"))`.
- Default top-k: 8.
- **Reranking (#48) is off by default.** `ChunkReranker` is the provider
  abstraction. `LexicalOverlapReranker` is a local, dependency-free reranker
  that scores query-term coverage of `chunk_text`. Enable with
  `SPACEBIO_RERANK_ENABLED=true` and optional `SPACEBIO_RERANKER=lexical_overlap`
  (or `noop`). Pass the instance into `hybrid_search(..., reranker=...)`.
  `reranker_from_env()` returns `None` when disabled so callers skip the stage.
- Filter by corpus topic, organism, exposure, section, year, approval, and
  publication metadata when available.
- Return ranked passages with citation metadata. No LLM generation in the
  semantic/hybrid search functions themselves.

## Future strategy
Query decomposition, ontology expansion, and graph-assisted retrieval may be added later. Cross-encoder / LLM rerankers can implement `ChunkReranker` without changing the retrieval store.

## Related documents
- [RAG architecture](../architecture/RAG_ARCHITECTURE.md)
- [Evaluation strategy](EVALUATION_STRATEGY.md)
- [Data architecture](../architecture/DATA_ARCHITECTURE.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).

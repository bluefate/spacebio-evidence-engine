# Retrieval Strategy

## Purpose
Define how relevant passages are found for search and question answering.

## Scope
MVP retrieval over PostgreSQL and pgvector.

## Current status
Initial strategy.

## MVP strategy
- Use Sentence Transformers for local embeddings where practical.
- Store vectors in pgvector.
- Support vector search.
- Add keyword or hybrid search if benchmark questions show vector-only gaps.
- Filter by corpus topic, organism, system, exposure, and publication metadata when available.
- Return ranked passages with citation metadata.

## Future strategy
Reranking, query decomposition, ontology expansion, and graph-assisted retrieval may be added later.

## Related documents
- [RAG architecture](../architecture/RAG_ARCHITECTURE.md)
- [Evaluation strategy](EVALUATION_STRATEGY.md)
- [Data architecture](../architecture/DATA_ARCHITECTURE.md)

## Human decisions still required
- Approve embedding model.
- Approve hybrid retrieval priority.
- Approve retrieval quality targets.


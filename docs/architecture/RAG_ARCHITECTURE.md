# RAG Architecture

## Purpose
Define how retrieval-augmented generation grounds answers in controlled publications.

## Scope
Ingestion, retrieval, answer generation, citations, and sufficiency behavior.

## Current status
Initial RAG architecture.

## Ingestion sequence
```mermaid
sequenceDiagram
  participant M as Maintainer
  participant W as Worker
  participant P as PyMuPDF
  participant DB as PostgreSQL/pgvector
  participant E as Embedding provider
  M->>W: Add corpus manifest entry
  W->>P: Extract text and page spans
  W->>W: Normalize sections and chunks
  W->>DB: Store documents, passages, chunks
  W->>E: Generate embeddings
  E-->>W: Vectors
  W->>DB: Store vectors and lineage
```

## Query sequence
```mermaid
sequenceDiagram
  participant U as User
  participant API as FastAPI
  participant R as Retriever
  participant DB as PostgreSQL/pgvector
  participant L as LLM provider
  U->>API: Ask question
  API->>R: Retrieve candidate passages
  R->>DB: Hybrid/vector query
  DB-->>R: Ranked passages
  R-->>API: Cited context
  API->>API: Evidence sufficiency check
  API->>L: Generate grounded answer
  L-->>API: Answer draft
  API->>API: Citation validation
  API-->>U: Answer with passage citations
```

## MVP RAG requirements
- Controlled corpus only.
- Citation-preserving chunks.
- Semantic retrieval with optional hybrid keyword support.
- Grounded generation.
- Insufficient-evidence response path.
- Evaluation with benchmark questions.

## Related documents
- [Chunking strategy](../rag/CHUNKING_STRATEGY.md)
- [Retrieval strategy](../rag/RETRIEVAL_STRATEGY.md)
- [Prompting strategy](../rag/PROMPTING_STRATEGY.md)
- [Citation strategy](../rag/CITATION_STRATEGY.md)
- [Evaluation strategy](../rag/EVALUATION_STRATEGY.md)

## Human decisions still required
- Approve top-k defaults and reranking approach.
- Approve model provider selection.
- Approve minimum citation validation thresholds.


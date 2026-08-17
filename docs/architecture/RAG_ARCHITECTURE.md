# RAG Architecture

## Purpose
Define how retrieval-augmented generation grounds answers in controlled publications.

## Scope
Ingestion, retrieval, answer generation, citations, and sufficiency behavior.

## Current status
Initial RAG architecture. Embedding **provider interface** is defined (issue #39). **Local** Sentence Transformers provider is implemented (issue #40, `LocalEmbeddingProvider`). Optional OpenAI embeddings remain issue #41. **LLM provider interface** is defined (issue #51, `LanguageModelProvider`); concrete OpenAI/local chat providers are follow-on work.

## Embedding provider interface

Embeddings are accessed only through `spacebio_evidence_engine.embeddings.EmbeddingProvider`:

| Member | Role |
| --- | --- |
| `model_name` | Stable model id stored with vectors for lineage |
| `dimension` | Fixed output length for all vectors from the provider |
| `embed_documents(texts)` | Batch-embed chunk/passage texts |
| `embed_query(text)` | Embed a single retrieval query |

Rules:

- Call sites depend on the abstract interface, not on Sentence Transformers or OpenAI SDKs.
- The interface module must not import provider-specific packages.
- Local implementation: `LocalEmbeddingProvider` (`embeddings/local.py`), default `all-MiniLM-L6-v2` (D4). Install with `pip install -e ".[embeddings]"`.
- Optional OpenAI embeddings stay behind a separate implementation (#41).

```mermaid
flowchart LR
  ingest[Ingest / chunk job] --> iface[EmbeddingProvider]
  query[Retriever query] --> iface
  iface --> local[LocalEmbeddingProvider #40]
  iface --> openai[#41 OpenAI optional]
  local --> vectors[(Vectors + model_name)]
  openai --> vectors
```

## Language model provider interface

Grounded generation goes through `spacebio_evidence_engine.llm.LanguageModelProvider` only:

| Member / type | Role |
| --- | --- |
| `model_name` | Stable model id for logs / cost tracking |
| `generate(GenerateRequest)` | Single-prompt completion |
| `chat(ChatRequest)` | Multi-turn chat completion |
| `GenerateRequest` / `ChatRequest` | Optional `structured_output` (JSON Schema map) |
| `GenerationResult` | `text`, optional `structured`, optional `UsageMetadata` |
| `UsageMetadata` | Optional `prompt_tokens` / `completion_tokens` / `total_tokens` (+ `extra`) |

Rules:

- Call sites depend on the ABC, not on OpenAI or other vendor SDKs.
- The interface module must not import provider-specific packages.
- MVP default remains optional OpenAI `gpt-4o-mini` behind a future concrete provider (D4 / ADR-006); local/$0 mode may use a stub or disabled path.

```mermaid
flowchart LR
  ask["/ask grounded path"] --> llm[LanguageModelProvider]
  llm --> openaiChat[OpenAI chat optional]
  llm --> stub[Test / local stub]
  openaiChat --> result[GenerationResult + usage]
  stub --> result
```

## Evidence sufficiency check

Before the language model is invoked, `spacebio_evidence_engine.rag.sufficiency.evaluate_sufficiency` checks that retrieved evidence crosses an MVP threshold (3 passages, 2 supporting publications by default). If the evidence is empty or weak, the pipeline returns a `GroundedAnswerResponse` with `sufficiency.status = "insufficient"` and does not call the model. See issue #55.

## Grounded answer response schema

Versioned Pydantic models live in `spacebio_evidence_engine.schemas` (issue #57). Current version: **`1.0.0`** (`GROUNDED_ANSWER_SCHEMA_VERSION`).

| Model | Role |
| --- | --- |
| `AskRequest` | `/ask` body (`question`, `top_k`) |
| `GroundedAnswerResponse` | Answer text, citations, sufficiency, limitations, conflicts, warnings |
| `PassageCitation` | Passage-level provenance (`chunk_id`, publication, section, page, excerpt) |
| `EvidenceSufficiency` | `sufficient` / `insufficient` / `marginal` plus counts |
| `LimitationNote` / `ConflictFinding` / `AnswerWarning` | Optional scientific caveats |

FastAPI exposes these in OpenAPI via `POST /ask` (`response_model=GroundedAnswerResponse`). The route delegates to a configured `GroundedAnswerService`, which uses current vector-only retrieved hits, context assembly, prompt rendering, citation emission, and sufficiency checks. If no retriever/LLM service is configured, the API returns **503** instead of falling back to model memory.

## Grounded answer API flow

`spacebio_evidence_engine.rag.GroundedAnswerService` is the backend orchestration boundary for issue #60:

1. Retrieve ranked hits from the controlled corpus. Default August path is
   vector search; **hybrid retrieval (#46) and optional lexical rerank (#48)
   exist** and stay off unless configured.
2. Assemble evidence with `assemble_context`, preserving chunk IDs, publication ID/title, section, page, source URL, and excerpts.
3. Evaluate sufficiency before generation. Insufficient evidence returns the fixed insufficient-evidence response and does not call the LLM.
4. Render the versioned grounded-answer prompt and call `LanguageModelProvider.chat`.
5. Emit citations only for `[C1]`-style markers present in the retrieved context. Unknown or unretrieved citation IDs fail closed; the API returns **502** rather than returning unsupported claims.

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
  R->>DB: Vector query
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
- Vector semantic retrieval (default top-k 8). Hybrid keyword + optional rerank
  are implemented post-August and are not on unless flags/env enable them.
- Grounded generation.
- Insufficient-evidence response path.
- Evaluation with benchmark questions.

## Related documents
- [Chunking strategy](../rag/CHUNKING_STRATEGY.md)
- [Retrieval strategy](../rag/RETRIEVAL_STRATEGY.md)
- [Prompting strategy](../rag/PROMPTING_STRATEGY.md)
- [Citation strategy](../rag/CITATION_STRATEGY.md)
- [Evaluation strategy](../rag/EVALUATION_STRATEGY.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).

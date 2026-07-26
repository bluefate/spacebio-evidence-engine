# Component Architecture

## Purpose
Define major software components and their responsibilities.

## Scope
Backend, frontend, RAG, data, and evaluation components for MVP.

## Current status
Initial component map.

## Diagram
```mermaid
flowchart TD
  UI["Citation-first UI"] --> API["API routes"]
  API --> Search["Search service"]
  API --> QA["Question-answering service"]
  API --> Compare["Study comparison service"]
  API --> Corpus["Corpus service"]
  Search --> Retrieval["Retrieval engine"]
  QA --> Retrieval
  QA --> Prompting["Prompt builder"]
  QA --> Citations["Citation assembler"]
  Retrieval --> Embeddings["Embedding provider"]
  Retrieval --> Store["PostgreSQL repositories"]
  Corpus --> Processing["Document processing"]
  Processing --> Extraction["Metadata/entity extraction"]
  Evaluation["Evaluation harness"] --> Retrieval
  Evaluation --> QA
```

## MVP components
Use modular Python packages for ingestion, retrieval, RAG orchestration, citation assembly, extraction, persistence, and evaluation.

## Future components
Curated graph services, contradiction review, and evidence grading should be separate modules.

## Related documents
- [RAG architecture](RAG_ARCHITECTURE.md)
- [Data architecture](DATA_ARCHITECTURE.md)
- [Testing strategy](../development/TESTING_STRATEGY.md)

## Human decisions still required
- Approve internal package boundaries.
- Decide whether API schemas use Pydantic directly or SQLModel-derived schemas.


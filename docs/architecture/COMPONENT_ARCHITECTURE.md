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

  classDef ui fill:#E0F2FE,stroke:#0284C7,color:#0F172A
  classDef api fill:#DCFCE7,stroke:#16A34A,color:#052E16
  classDef rag fill:#F3E8FF,stroke:#9333EA,color:#3B0764
  classDef data fill:#FEF3C7,stroke:#D97706,color:#451A03
  classDef eval fill:#FFE4E6,stroke:#E11D48,color:#4C0519

  class UI ui
  class API,Search,QA,Compare,Corpus api
  class Retrieval,Prompting,Citations,Embeddings rag
  class Store,Processing,Extraction data
  class Evaluation eval
```

## MVP components
Use modular Python packages for ingestion, retrieval, RAG orchestration, citation assembly, extraction, persistence, and evaluation. API request/response schemas use Pydantic directly (not SQLModel-derived schemas); persistence uses SQLAlchemy 2.x.

## Future components
Curated graph services, contradiction review, and evidence grading should be separate modules.

## Related documents
- [RAG architecture](RAG_ARCHITECTURE.md)
- [Data architecture](DATA_ARCHITECTURE.md)
- [Testing strategy](../development/TESTING_STRATEGY.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).


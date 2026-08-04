# System Context

## Purpose
Show how users and external systems interact with the evidence engine.

## Scope
MVP context and future context.

## Current status
Initial context model.

## Diagram
```mermaid
flowchart LR
  Researcher["Researcher"] --> App["Space Biology Evidence Engine"]
  Student["Student or educator"] --> App
  Maintainer["Corpus maintainer"] --> App
  App --> DB["PostgreSQL + pgvector"]
  App --> Models["Embedding and LLM providers"]
  App --> Corpus["Controlled open-access publication corpus"]
  App -. "future optional" .-> Graph["Neo4j or graph service"]

  classDef user fill:#E0F2FE,stroke:#0284C7,color:#0F172A
  classDef app fill:#DCFCE7,stroke:#16A34A,color:#052E16
  classDef data fill:#FEF3C7,stroke:#D97706,color:#451A03
  classDef provider fill:#F3E8FF,stroke:#9333EA,color:#3B0764
  classDef future fill:#F1F5F9,stroke:#64748B,stroke-dasharray: 5 5,color:#334155

  class Researcher,Student,Maintainer user
  class App app
  class DB,Corpus data
  class Models provider
  class Graph future
```

## MVP context
Users access the web app anonymously for local August MVP. The backend retrieves controlled-corpus passages from PostgreSQL and calls configured model providers (local Sentence Transformers embeddings; optional OpenAI LLM) through abstractions.

## Future context
Graph-native services, curator interfaces, external repository integrations, and additional corpora may be added after MVP.

## Related documents
- [Architecture overview](ARCHITECTURE.md)
- [Container architecture](CONTAINER_ARCHITECTURE.md)
- [Security architecture](SECURITY_ARCHITECTURE.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).


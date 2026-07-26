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
```

## MVP context
Users access the web app. The backend retrieves controlled-corpus passages from PostgreSQL and calls configured model providers through abstractions.

## Future context
Graph-native services, curator interfaces, external repository integrations, and additional corpora may be added after MVP.

## Related documents
- [Architecture overview](ARCHITECTURE.md)
- [Container architecture](CONTAINER_ARCHITECTURE.md)
- [Security architecture](SECURITY_ARCHITECTURE.md)

## Human decisions still required
- Confirm whether anonymous public users are supported.
- Confirm allowed external model providers.


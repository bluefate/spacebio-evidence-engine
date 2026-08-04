# Container Architecture

## Purpose
Define deployable application containers for local and future environments.

## Scope
MVP containers with future additions noted separately.

## Current status
Initial container model.

## Diagram
```mermaid
flowchart TD
  Browser["Browser"] --> Web["Next.js web app"]
  Web --> API["FastAPI API"]
  API --> DB["PostgreSQL + pgvector"]
  API --> Worker["Ingestion/evaluation worker"]
  Worker --> DB
  Worker --> Files["Local corpus files"]
  API --> Provider["Model provider abstraction"]
  Provider --> LocalEmb["Sentence Transformers"]
  Provider --> OpenAI["OpenAI API when configured"]
  API -. "future" .-> Neo4j["Neo4j graph database"]

  classDef client fill:#E0F2FE,stroke:#0284C7,color:#0F172A
  classDef service fill:#DCFCE7,stroke:#16A34A,color:#052E16
  classDef data fill:#FEF3C7,stroke:#D97706,color:#451A03
  classDef provider fill:#F3E8FF,stroke:#9333EA,color:#3B0764
  classDef future fill:#F1F5F9,stroke:#64748B,stroke-dasharray: 5 5,color:#334155

  class Browser client
  class Web,API,Worker service
  class DB,Files data
  class Provider,LocalEmb,OpenAI provider
  class Neo4j future
```

## MVP containers
- `web`: Next.js TypeScript application.
- `api`: FastAPI backend.
- `db`: PostgreSQL with pgvector.
- `worker`: ingestion, embedding, and evaluation jobs.

## Future containers
- `graph`: Neo4j or graph API.
- `observability`: metrics, traces, and dashboards.

## Related documents
- [Component architecture](COMPONENT_ARCHITECTURE.md)
- [Deployment architecture](DEPLOYMENT_ARCHITECTURE.md)
- [Local setup](../operations/LOCAL_SETUP.md)

## Human decisions still required
- Decide whether worker is a separate process in MVP or a CLI module.
- Approve Docker image standards.


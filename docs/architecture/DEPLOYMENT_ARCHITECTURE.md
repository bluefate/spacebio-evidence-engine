# Deployment Architecture

## Purpose
Describe local and future deployment topology.

## Scope
Docker Compose for MVP; cloud deployment as future architecture.

## Current status
Initial deployment plan.

## Diagram
```mermaid
flowchart TD
  Dev["Developer machine"] --> Compose["Docker Compose"]
  Compose --> Web["web container"]
  Compose --> API["api container"]
  Compose --> CLI["CLI jobs (ingest/eval)"]
  Compose --> DB["postgres-pgvector volume"]
  API --> Env["Environment secrets"]
  CLI --> Corpus["Mounted corpus directory"]
  Cloud["Future cloud environment"] -.-> LB["Load balancer"]
  LB -.-> CloudWeb["Web service"]
  LB -.-> CloudAPI["API service"]
  CloudAPI -.-> ManagedDB["Managed PostgreSQL"]

  classDef local fill:#E0F2FE,stroke:#0284C7,color:#0F172A
  classDef service fill:#DCFCE7,stroke:#16A34A,color:#052E16
  classDef data fill:#FEF3C7,stroke:#D97706,color:#451A03
  classDef secret fill:#FFE4E6,stroke:#E11D48,color:#4C0519
  classDef future fill:#F1F5F9,stroke:#64748B,stroke-dasharray: 5 5,color:#334155

  class Dev,Compose local
  class Web,API,CLI service
  class DB,Corpus,ManagedDB data
  class Env secret
  class Cloud,LB,CloudWeb,CloudAPI future
```

## MVP deployment
Local Docker Compose is the only August MVP deployment target (deadline 2026-08-31). Public cloud hosting is deferred post-August.

## Future deployment
Cloud deployment may use managed PostgreSQL, managed secrets, container hosting, and object storage.

## Related documents
- [Operations deployment](../operations/DEPLOYMENT.md)
- [Local setup](../operations/LOCAL_SETUP.md)
- [Security architecture](SECURITY_ARCHITECTURE.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).


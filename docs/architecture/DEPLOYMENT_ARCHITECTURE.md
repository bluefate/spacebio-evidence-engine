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
  Compose --> Worker["worker container"]
  Compose --> DB["postgres-pgvector volume"]
  API --> Env["Environment secrets"]
  Worker --> Corpus["Mounted corpus directory"]
  Cloud["Future cloud environment"] -.-> LB["Load balancer"]
  LB -.-> CloudWeb["Web service"]
  LB -.-> CloudAPI["API service"]
  CloudAPI -.-> ManagedDB["Managed PostgreSQL"]
```

## MVP deployment
Local Docker Compose is the primary deployment target.

## Future deployment
Cloud deployment may use managed PostgreSQL, managed secrets, container hosting, and object storage.

## Related documents
- [Operations deployment](../operations/DEPLOYMENT.md)
- [Local setup](../operations/LOCAL_SETUP.md)
- [Security architecture](SECURITY_ARCHITECTURE.md)

## Human decisions still required
- Choose production host.
- Decide whether public deployment is required for the challenge submission.


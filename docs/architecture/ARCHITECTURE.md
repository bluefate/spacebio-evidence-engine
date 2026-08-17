# Architecture Overview

## Purpose
Summarize the technical architecture and evaluate preferred technology choices.

## Scope
Covers August MVP architecture (deadline 2026-08-31) and explicitly separates future architecture.

## Current status
Architecture baseline **accepted**. See [decision log](../governance/DECISION_LOG.md).

## Technology evaluation (locked)
- Python 3.12+: accepted for backend, ingestion, RAG, notebooks, and scientific tooling.
- FastAPI: accepted for clear API boundaries and Python-native service development.
- PostgreSQL: accepted as durable relational storage.
- pgvector: accepted for MVP vector search to avoid a separate vector database.
- **SQLAlchemy 2.x + Alembic**: accepted; API schemas via **Pydantic** (not SQLModel).
- PyMuPDF: accepted for initial PDF parsing; tables/figures out of August MVP.
- Jupyter: accepted for corpus analysis, retrieval experiments, and evaluation.
- Sentence Transformers **`all-MiniLM-L6-v2`**: accepted for local embeddings.
- OpenAI **`gpt-4o-mini`**: optional behind an abstraction layer; **$50/mo hard cap**.
- Next.js with TypeScript: accepted for citation inspection UI.
- Docker Compose: accepted for local PostgreSQL, API, and web; ingest via CLI/jobs.
- **pyright**: primary type checker.
- Neo4j / graph database: **no** (ADR-011 / #77). Modeling, if any, would be PostgreSQL tables (ADR-010).
- Pytest, Ruff, GitHub Actions: accepted for quality gates.
- Mermaid: accepted for architecture diagrams in documentation.
- License: **Apache-2.0**.

## August MVP architecture
The August MVP uses a Next.js frontend, FastAPI backend, PostgreSQL with pgvector, CLI ingest/eval jobs, local or configured model providers, and a small evaluation set. Deployment target is **local Compose only**.

## Future architecture
Future phases may add study compare UI, hybrid retrieval, Neo4j, curator workflows, auth, public cloud deployment, richer observability, and advanced contradiction workflows.

## Related documents
- [System context](SYSTEM_CONTEXT.md)
- [Container architecture](CONTAINER_ARCHITECTURE.md)
- [RAG architecture](RAG_ARCHITECTURE.md)
- [Data architecture](DATA_ARCHITECTURE.md)
- [Knowledge graph use cases](KNOWLEDGE_GRAPH_USE_CASES.md)
- [Candidate graph entity types](../data/GRAPH_ENTITY_TYPES.md)
- [Candidate graph relationship types](../data/GRAPH_RELATIONSHIP_TYPES.md)
- [Decision log](../governance/DECISION_LOG.md)
- [Build plan](../../plan.md)
- [Technical design](../../design.md)

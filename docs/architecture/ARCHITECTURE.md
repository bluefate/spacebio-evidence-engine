# Architecture Overview

## Purpose
Summarize the technical architecture and evaluate preferred technology choices.

## Scope
Covers MVP architecture and explicitly separates future architecture.

## Current status
Initial architecture baseline pending human approval.

## Technology evaluation
- Python 3.12+: accepted for backend, ingestion, RAG, notebooks, and scientific tooling.
- FastAPI: accepted for clear API boundaries and Python-native service development.
- PostgreSQL: accepted as durable relational storage.
- pgvector: accepted for MVP vector search to avoid a separate vector database.
- SQLAlchemy or SQLModel: both viable; SQLAlchemy is more mature, SQLModel is simpler for FastAPI data models. Decision required.
- Alembic: accepted for schema migration discipline.
- PyMuPDF: accepted for initial PDF parsing; table/figure extraction may need later tools.
- Jupyter: accepted for corpus analysis, retrieval experiments, and evaluation.
- Sentence Transformers: accepted for local embeddings where quality is sufficient.
- OpenAI models: accepted only behind an abstraction layer.
- Next.js with TypeScript: accepted for a modern citation inspection UI.
- Docker Compose: accepted for local PostgreSQL, API, UI, and worker services.
- Neo4j: deferred until graph-native needs justify operational cost.
- Pytest, Ruff, mypy or pyright, GitHub Actions: accepted for quality gates.
- Mermaid: accepted for architecture diagrams in documentation.

## MVP architecture
The MVP uses a Next.js frontend, FastAPI backend, PostgreSQL with pgvector, ingestion workers, local or configured model providers, and documented evaluation workflows.

## Future architecture
Future phases may add Neo4j, curator workflows, graph analytics, advanced contradiction workflows, richer observability, and cloud deployment.

## Related documents
- [System context](SYSTEM_CONTEXT.md)
- [Container architecture](CONTAINER_ARCHITECTURE.md)
- [RAG architecture](RAG_ARCHITECTURE.md)
- [Data architecture](DATA_ARCHITECTURE.md)

## Human decisions still required
- Choose SQLAlchemy or SQLModel.
- Choose type checker.
- Approve model provider abstraction boundaries.
- Approve deployment target.


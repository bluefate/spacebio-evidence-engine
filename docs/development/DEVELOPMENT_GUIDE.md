# Development Guide

## Purpose
Define engineering standards for implementation.

## Scope
Backend, frontend, ingestion, RAG, data, tests, and CI.

## Current status
Initial guide before code scaffolding.

## Standards
- Python 3.12 or newer.
- FastAPI for backend APIs.
- PostgreSQL with pgvector for MVP persistence and vector search.
- Alembic for migrations.
- Next.js with TypeScript for frontend.
- Docker Compose for local services.
- Pytest for Python tests.
- Ruff for linting and formatting.
- Pyright for type checking.
- GitHub Actions for CI.

## Diagram standards
- Use Mermaid diagrams for architecture, workflow, data lineage, and RAG sequences.
- Use color where it clarifies meaning, such as distinguishing users, services, data stores, providers, future/deferred components, review states, and risk paths.
- Prefer restrained, consistent colors over decorative gradients.
- Keep color semantic and readable in light and dark GitHub themes.

## Package layout
- Monorepo with `apps/api` (FastAPI) and `apps/web` (Next.js); shared `packages` deferred until needed.

## Package principles
- Keep provider-specific model code behind abstractions.
- Keep RAG orchestration separate from API routes.
- Keep ingestion repeatable and observable.
- Keep prompts versioned.
- Follow the root [AGENTS.md](../../AGENTS.md) contract on every task.

## Related documents
- [Local setup](../operations/LOCAL_SETUP.md)
- [Testing strategy](TESTING_STRATEGY.md)
- [Branching strategy](BRANCHING_STRATEGY.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).


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
- mypy or pyright after human decision.
- GitHub Actions for CI.

## Package principles
- Keep provider-specific model code behind abstractions.
- Keep RAG orchestration separate from API routes.
- Keep ingestion repeatable and observable.
- Keep prompts versioned.

## Related documents
- [Local setup](../operations/LOCAL_SETUP.md)
- [Testing strategy](TESTING_STRATEGY.md)
- [Branching strategy](BRANCHING_STRATEGY.md)

## Human decisions still required
- Confirm backend package layout.
- Choose type checker.
- Decide whether monorepo package management is required.


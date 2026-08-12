# Development Guide

## Purpose
Define engineering standards for implementation.

## Scope
Backend, frontend, ingestion, RAG, data, tests, and CI.

## Current status
Monorepo scaffold started: FastAPI under `apps/api`, Next.js under `apps/web`, shared placeholder package under `src/spacebio_evidence_engine`.

## Standards
- Python 3.12 or newer.
- FastAPI for backend APIs (`apps/api/src/spacebio_api`).
- PostgreSQL with pgvector for MVP persistence and vector search.
- SQLAlchemy 2.x + Alembic for persistence (migrations land in later issues).
- Pydantic / pydantic-settings for API schemas and settings.
- Next.js with TypeScript for frontend (`apps/web`).
- Docker Compose for local Postgres.
- Pytest for Python tests (`make test` / `pytest -q`).
- Ruff for linting and formatting (`make lint` / `ruff check .` / `ruff format --check .`);
  pre-commit runs `ruff --fix` and `ruff-format` on staged Python files.
- **Pyright** for type checking.
- GitHub Actions for CI.

## Diagram standards
- Use Mermaid diagrams for architecture, workflow, data lineage, and RAG sequences.
- Use color where it clarifies meaning, such as distinguishing users, services, data stores, providers, future/deferred components, review states, and risk paths.
- Prefer restrained, consistent colors over decorative gradients.
- Keep color semantic and readable in light and dark GitHub themes.

## Package layout
- `apps/api` — FastAPI service (`spacebio_api.main:app`)
- `apps/web` — Next.js UI
- `src/spacebio_evidence_engine` — shared Python package placeholder
- `packages/` — deferred until shared libraries are needed
- Ports: API `8000`, web `3000`, Postgres `5432`

## Package principles
- Keep provider-specific model code behind abstractions.
- Keep RAG orchestration separate from API routes.
- Keep ingestion repeatable and observable.
- Keep prompts versioned.
- Follow the root [AGENTS.md](../../AGENTS.md) contract on every task.
- If you add new Python tests, keep them under `tests/` in the concern-based layout described in [TESTING_STRATEGY.md](TESTING_STRATEGY.md).

## Related documents
- [Local setup](../operations/LOCAL_SETUP.md)
- [Testing strategy](TESTING_STRATEGY.md)
- [Branching strategy](BRANCHING_STRATEGY.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).

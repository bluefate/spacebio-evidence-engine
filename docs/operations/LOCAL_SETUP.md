# Local Setup

## Purpose
Define the expected local development environment and Make targets used by humans and agents.

## Scope
Setup, services, lint, typecheck, test, and API/web run commands.

## Current status
Monorepo scaffold is in place: `apps/api` (FastAPI), `apps/web` (Next.js), Compose Postgres/pgvector.

## Expected tools
- Python 3.12 or newer.
- Node.js 20+.
- Docker and Docker Compose.
- GNU Make.
- `pre-commit`, Ruff, Pytest, Pyright.

## Commands

Aligned with [AGENTS.md](../../AGENTS.md):

```bash
make setup       # .env, venv, editable install, web npm install, pre-commit, Compose DB
make services    # PostgreSQL + pgvector via Docker Compose
make api         # uvicorn on http://localhost:8000 (GET /health)
make web         # Next.js on http://localhost:3000
make lint
make typecheck
make test
make validate    # lint + typecheck + test
```

## Expected local services
- PostgreSQL with pgvector (Compose) on port `5432`.
- FastAPI backend (`apps/api`) on port `8000`.
- Next.js frontend (`apps/web`) on port `3000`.
- CLI jobs for ingestion and evaluation (no always-on worker for August MVP).

## Related documents
- [AGENTS](../../AGENTS.md)
- [Development guide](../development/DEVELOPMENT_GUIDE.md)
- [Deployment architecture](../architecture/DEPLOYMENT_ARCHITECTURE.md)
- [Operations deployment](DEPLOYMENT.md)
- [Backlog index](../governance/BACKLOG.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).

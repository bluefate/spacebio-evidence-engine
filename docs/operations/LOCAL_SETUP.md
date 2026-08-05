# Local Setup

## Purpose
Define the expected local development environment and Make targets used by humans and agents.

## Scope
Setup, services, lint, typecheck, test, and API/web run commands.

## Current status
Monorepo scaffold is in place: `apps/api` (FastAPI), `apps/web` (Next.js), Compose Postgres/pgvector.

## Expected tools
- Python 3.12 or newer.
- Node.js 22+.
- Docker and Docker Compose.
- GNU Make.
- `pre-commit`, Ruff, Pytest, Pyright.

## Commands

Aligned with [AGENTS.md](../../AGENTS.md):

```bash
make setup         # .env, venv, editable install, web npm install, pre-commit, Compose DB, pgvector bootstrap
make services      # PostgreSQL + pgvector via Docker Compose
make db-bootstrap  # Idempotent CREATE EXTENSION IF NOT EXISTS vector
make migrate       # Alembic upgrade head (publications table, …)
make api           # uvicorn on http://localhost:8000 (GET /health)
make web           # Next.js on http://localhost:3000
make lint
make typecheck
make test
make validate      # lint + typecheck + test
```

## Database / pgvector

1. Copy `.env.example` to `.env` and set `POSTGRES_PASSWORD` / `DATABASE_URL` (keep them consistent).
2. `make services` starts Compose Postgres (`pgvector/pgvector:pg16` on port `5432`).
3. `make db-bootstrap` enables the `vector` extension (needed if the data volume already existed before init scripts were added).
4. Fresh volumes also apply `scripts/db/init/01_pgvector.sql` automatically.
5. Application tables are **not** created here — only the extension (see issue #8).

Integration smoke (optional, needs DB up):

```bash
SPACEBIO_REQUIRE_DB=1 pytest -q -m integration tests/test_pgvector_bootstrap.py
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

# Local Setup

## Purpose
Define the expected local development environment and Make targets used by humans and agents.

## Scope
Setup, services, lint, typecheck, test, and future API/web run commands.

## Current status
Make targets exist. `make api` and `make web` fail intentionally until those packages are scaffolded.

## Expected tools
- Python 3.12 or newer.
- Node.js 20+ (for the MVP Next.js app when scaffolded).
- Docker and Docker Compose.
- GNU Make.
- `pre-commit`, Ruff, Pytest, Pyright (or mypy after human decision).

## Commands

Aligned with [AGENTS.md](../../AGENTS.md):

```bash
make setup       # .env, venv, editable install, pre-commit, Compose DB
make services    # PostgreSQL + pgvector via Docker Compose
make lint
make typecheck
make test
make validate    # lint + typecheck + test
make api         # placeholder until API package exists
make web         # placeholder until web package exists
```

## Expected local services
- PostgreSQL with pgvector (Compose).
- FastAPI backend (future package).
- Next.js frontend (future package).
- Optional worker for ingestion and evaluation.

## Related documents
- [AGENTS](../../AGENTS.md)
- [Development guide](../development/DEVELOPMENT_GUIDE.md)
- [Deployment architecture](../architecture/DEPLOYMENT_ARCHITECTURE.md)
- [Operations deployment](DEPLOYMENT.md)

## Human decisions still required
- Choose package managers and final package layout.
- Approve default local ports.
- Choose mypy versus pyright as the primary type checker.

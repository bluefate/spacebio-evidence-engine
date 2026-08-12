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
make refresh-board # regenerate docs/development/ACTIVE_BOARD.md from Project + PRs
```

## Local embeddings (issue #40)

Default model: `sentence-transformers/all-MiniLM-L6-v2` (configure via `EMBEDDING_MODEL`).

1. Install the optional extra (pulls `sentence-transformers` / torch):

```bash
source .venv/bin/activate
pip install -e ".[embeddings]"
```

2. First real embed downloads weights into the Hugging Face cache (~90MB for MiniLM). Offline CI does **not** need this — unit tests inject a stub model.

3. Optional live smoke (downloads weights):

```bash
pytest -q -m embedding_smoke
```

4. Construct in code:

```python
from spacebio_evidence_engine.embeddings import LocalEmbeddingProvider

provider = LocalEmbeddingProvider()  # or LocalEmbeddingProvider(model_name=...)
```

## Optional OpenAI embeddings (issue #41)

OpenAI embeddings are disabled unless `OPENAI_API_KEY` is present. Keep keys in
your local `.env` only; `.env.example` documents the variable names without real
secrets.

```bash
# .env
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

Construct through `from_env()` so CI and local-only runs skip the provider when
credentials are absent:

```python
from spacebio_evidence_engine.embeddings import OpenAIEmbeddingProvider

provider = OpenAIEmbeddingProvider.from_env()
if provider is None:
    ...
```

Unit tests use an injected fake client and do not call the network.

## Database / pgvector

1. Copy `.env.example` to `.env` and set `POSTGRES_PASSWORD` / `DATABASE_URL` (keep them consistent).
2. `make services` starts Compose Postgres (`pgvector/pgvector:pg16` on port `5432`).
3. `make db-bootstrap` enables the `vector` extension (needed if the data volume already existed before init scripts were added).
4. Fresh volumes also apply `scripts/db/init/01_pgvector.sql` automatically.
5. `make migrate` applies Alembic revisions through `chunk_embeddings` (`vector(384)` on Postgres; issue #42).
5. Application tables are **not** created here — only the extension (see issue #8).

Integration smoke (optional, needs DB up):

```bash
SPACEBIO_REQUIRE_DB=1 pytest -q -m integration tests/test_pgvector_bootstrap.py
```

## PDF storage

The ingestion pipeline stores source PDFs through a backend selected by `PDF_STORAGE_BACKEND`.

- `PDF_STORAGE_BACKEND` — backend type (`local` for the default filesystem store).
- `PDF_STORAGE_LOCAL_ROOT` — root directory for local PDF files. Default: `data/pdfs`.

## PDF text extraction (issue #29)

PyMuPDF is included in the `dev` extra (so `make setup` / CI `.[dev]` can typecheck and test extraction) and also in the `ingestion` extra for feature-scoped installs:

```bash
pip install -e ".[dev]"
# or
pip install -e ".[ingestion]"
```

Extract page-ordered text via `spacebio_evidence_engine.ingestion.extract_pdf_bytes` / `extract_pdf_path` / `extract_pdf_from_storage`. See [Document processing](../data/DOCUMENT_PROCESSING.md).

## Expected local services
- PostgreSQL with pgvector (Compose) on port `5432`.
- FastAPI backend (`apps/api`) on port `8000`.
- Next.js frontend (`apps/web`) on port `3000`; `/search` calls the web app
  `/api/search` route for stored publication metadata and any exposed passage
  records.
- CLI jobs for ingestion and evaluation (no always-on worker for August MVP).

## Related documents
- [AGENTS](../../AGENTS.md)
- [Development guide](../development/DEVELOPMENT_GUIDE.md)
- [Deployment architecture](../architecture/DEPLOYMENT_ARCHITECTURE.md)
- [Operations deployment](DEPLOYMENT.md)
- [Backlog index](../governance/BACKLOG.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).

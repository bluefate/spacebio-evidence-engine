# Local Setup

## Purpose

Define the expected local development environment and Make targets used by
humans and agents.

## Scope

Setup, services, lint, typecheck, test, and API/web run commands for a clean
developer machine.

## Current status

Monorepo scaffold is in place: `apps/api` (FastAPI), `apps/web` (Next.js),
Compose Postgres/pgvector. `make setup` provisions `.env`, `.venv`, editable
Python install, web npm deps, pre-commit hooks, Compose DB, pgvector bootstrap,
and Alembic migrations (best-effort when Docker is available).

## Expected tools

| Tool | Version / notes |
| --- | --- |
| Python | 3.12 or newer (`python3`) |
| Node.js | 22+ (`node` / `npm`) |
| Docker + Compose | Required for Postgres/pgvector |
| GNU Make | `make` |
| Git + `gh` | Clone, PRs, `make refresh-board` |
| pre-commit / Ruff / Pytest / Pyright | Installed via `make setup` into `.venv` |

## Ports

| Service | Host port | How to start | Notes |
| --- | ---: | --- | --- |
| PostgreSQL + pgvector | `5432` | `make services` | Compose service `db` |
| FastAPI | `8000` | `make api` | OpenAPI at `/docs`; `GET /health`; `POST /ask` is enabled when `OPENAI_API_KEY` is set and the configured embedding provider can load; otherwise **503** |
| Next.js web | `3000` | `make web` | `/`, `/corpus`, `/publications/[id]`, `/compare`, `/ask`, `/search` |

## What works after `make setup` (honest)

**You can:**

- Start Compose Postgres, bootstrap pgvector, run Alembic migrations
- `GET /health` on the API
- Download the 23 approved PDFs with `make fetch-pdfs` (after setup)
- Browse corpus, publication detail, and **`/compare`** (inventory metadata only)
- Open the ask UI (`POST /ask` may still return **503** until `OPENAI_API_KEY` is set and the embedding provider is available)
- Run `make validate`, `make eval-hallucination`, `make eval-graph-extraction`

**You should not expect:**

- `make ingest` — indexes PDFs already under `data/pdfs/{publication_id}.pdf`; it does not enable `/ask` on its own
- Corpus PDFs are **not** in git (`data/pdfs/` is gitignored)
- Live grounded `POST /ask` answers — without a configured `GroundedAnswerService` the API **fails closed with 503** and does not use model memory
- Web `/search` querying pgvector — it still uses static `corpus.json` via the Next.js `/api/search` route

## What to run locally

1. `cp .env.example .env` and keep `POSTGRES_PASSWORD` aligned with `DATABASE_URL`.
2. `make setup` (venv, deps, Compose, `pgvector` bootstrap, and Alembic migrate — all read `.env` automatically; no secret values are printed).
3. If Docker was skipped: `make services && make db-bootstrap && make migrate`.
4. Optional local embeddings (MiniLM download on first use): `pip install -e ".[embeddings]"`.
5. Download the 23 approved PDFs: `make fetch-pdfs`. Alternatively, copy approved PDFs to `data/pdfs/{publication_id}.pdf`.
6. Ingest the downloaded PDFs: `make ingest` (loads `.env` automatically).
7. To enable grounded `POST /ask`, set `OPENAI_API_KEY` in `.env` and ensure the configured embedding provider (e.g. `sentence-transformers/all-MiniLM-L6-v2`) is installed (`pip install -e ".[embeddings]"`).
8. `make api` and `make web`.
9. `curl -s http://localhost:8000/health`
10. Open `http://localhost:3000/compare` and `http://localhost:3000/ask`.
11. `POST /ask` returning **503** is expected when `OPENAI_API_KEY` is unset, the embedding provider is unavailable, or the index is empty.

## Commands

Aligned with [AGENTS.md](../../AGENTS.md):

```bash
make setup         # .env, venv, editable install, web npm install, pre-commit, Compose DB, pgvector, migrate
make setup-check   # Dry-run checklist (tools, ports docs, .env.example hygiene; no secrets printed)
make services      # PostgreSQL + pgvector via Docker Compose
make db-bootstrap  # Idempotent CREATE EXTENSION IF NOT EXISTS vector; loads .env
make migrate       # Alembic upgrade head; loads .env
make fetch-pdfs  # Download the 23 approved OA PDFs into data/pdfs/
make ingest        # Local PDFs → chunks + embeddings (needs DATABASE_URL; optional MiniLM extra)
make api           # uvicorn on http://localhost:8000
make web           # Next.js on http://localhost:3000
make lint
make typecheck
make test
make test-web      # Vitest: citation, ask, and a11y UI (apps/web)
make validate      # lint + typecheck + Python tests + web tests (+ hallucination eval)
make eval-hallucination
make eval-graph-extraction
make refresh-board # regenerate docs/development/ACTIVE_BOARD.md from Project + PRs (`read:project` required)
```

## Clean-machine checklist

Use this on a fresh clone before claiming implementation work:

1. Install expected tools (Python 3.12+, Node 22+, Docker Desktop / Engine + Compose, Make, Git).
2. Clone the principal repo and enter the root directory.
3. Copy env template if you prefer to edit before setup:
   ```bash
   cp .env.example .env
   ```
   Keep `POSTGRES_PASSWORD` and the password segment of `DATABASE_URL` consistent.
   Never commit `.env`.
4. Run setup:
   ```bash
   make setup
   ```
5. Verify the dry-run checklist (does not print secret values):
   ```bash
   make setup-check
   ```
6. Confirm services:
   - `curl -s http://localhost:8000/health` after `make api`
   - open `http://localhost:3000` after `make web`
   - Postgres accepts connections on `localhost:5432`
7. Run validation when changing code:
   ```bash
   make validate
   ```

`make setup` continues when Docker is unavailable (Compose/bootstrap/migrate
steps are best-effort). Re-run `make services`, `make db-bootstrap`, and
`make migrate` once Docker is ready.

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
5. `make migrate` applies Alembic revisions through chunk embeddings / FTS columns as landed on `main`.
6. Application tables are created by Alembic migrations (not by the bootstrap script alone).

Integration smoke (optional, needs DB up):

```bash
SPACEBIO_REQUIRE_DB=1 pytest -q -m integration tests/test_pgvector_bootstrap.py
```

End-to-end ingestion integration smoke (optional, needs DB up and migrations applied):

```bash
make services
make migrate
SPACEBIO_REQUIRE_DB=1 pytest -q -m integration tests/integration/test_ingestion_e2e.py
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
- FastAPI backend (`apps/api`) on port `8000`. `POST /ask` returns
  `GroundedAnswerResponse` only when the app is constructed with a
  `GroundedAnswerService` (retriever + `LanguageModelProvider`). Without that
  runtime wiring it returns **503** and does not invent answers from model
  knowledge. `POST /publications/from-doi` and `POST /publications/from-pdf`
  register **local extras** (`local_*`, pending review), not the approved 23.
  Paywalled licenses are rejected. `POST /publications/{id}/index` runs ingest
  for a stored PDF. `make ingest` indexes catalog PDFs under `data/pdfs/`.
- Next.js frontend (`apps/web`) on port `3000`: `/compare` uses corpus inventory
  fields; `/search` uses static stored metadata (`corpus.json`), not the live
  vector index; `/add` registers local extras via the API (`from-doi`,
  `from-pdf`) and a separate Index action (`POST /publications/{id}/index`).
  Status text distinguishes registered vs indexed vs failed.
- Evaluation CLIs exist (`evals/`); they are not a substitute for placing PDFs and running `make ingest`.

## Environment variables

See [`.env.example`](../../.env.example). Required for local DB work:

- `POSTGRES_*`, `DATABASE_URL`

Optional (leave unset for local-only / $0 cloud mode):

- `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_EMBEDDING_MODEL`
- `EMBEDDING_MODEL`, retrieval logging flags, PDF storage paths
- Developer retrieval diagnostics (off by default): `SPACEBIO_DEV_RETRIEVAL_DIAGNOSTICS`,
  `NEXT_PUBLIC_ENABLE_RETRIEVAL_DIAGNOSTICS` — see [Observability](../architecture/OBSERVABILITY.md)
- Optional retrieval rerank (off by default): `SPACEBIO_RERANK_ENABLED`, `SPACEBIO_RERANKER`

`make setup-check` confirms `.env.example` documents required keys and does not
contain high-entropy secret-looking values.

## Related documents

- [AGENTS](../../AGENTS.md)
- [Development guide](../development/DEVELOPMENT_GUIDE.md)
- [Deployment architecture](../architecture/DEPLOYMENT_ARCHITECTURE.md)
- [Operations deployment](DEPLOYMENT.md)
- [Backlog index](../governance/BACKLOG.md)

## Decision status

Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See
[decision log](../governance/DECISION_LOG.md).

# Makefile for Space Biology Evidence Engine
# Keep targets aligned with AGENTS.md. Update AGENTS.md when tooling changes.
#
# Tooling prefers `.venv/bin` so `make lint|typecheck|test|validate` work from a
# fresh shell without requiring `source .venv/bin/activate`.

.PHONY: setup setup-check api web services db-bootstrap migrate ingest lint typecheck test test-web validate refresh-board eval-hallucination eval-graph-extraction help

VENV_BIN := $(CURDIR)/.venv/bin
SYSTEM_PYTHON ?= python3

ifeq ($(wildcard $(VENV_BIN)/python),)
  PYTHON ?= $(SYSTEM_PYTHON)
  PIP ?= pip
  RUFF ?= ruff
  PYRIGHT ?= pyright
  PYTEST ?= pytest
  UVICORN ?= uvicorn
  ALEMBIC ?= alembic
else
  PYTHON ?= $(VENV_BIN)/python
  PIP ?= $(VENV_BIN)/pip
  RUFF ?= $(VENV_BIN)/ruff
  PYRIGHT ?= $(VENV_BIN)/pyright
  PYTEST ?= $(VENV_BIN)/pytest
  UVICORN ?= $(VENV_BIN)/uvicorn
  ALEMBIC ?= $(VENV_BIN)/alembic
endif

help:
	@echo "Targets: setup setup-check api web services db-bootstrap migrate ingest lint typecheck test test-web validate refresh-board eval-hallucination eval-graph-extraction"
	@echo "Uses $(VENV_BIN) tools when .venv exists (no activate required)."

setup:
	@test -f .env || cp .env.example .env
	@if [ ! -d .venv ]; then $(SYSTEM_PYTHON) -m venv .venv; fi
	@$(VENV_BIN)/pip install -e ".[dev]"
	@$(VENV_BIN)/pre-commit install || true
	@if [ -f apps/web/package.json ]; then cd apps/web && npm install; fi
	@docker compose up -d
	@$(VENV_BIN)/python scripts/bootstrap_pgvector.py || true
	@$(VENV_BIN)/alembic upgrade head || true
	@echo "Setup complete. Optional: source .venv/bin/activate — Make targets use .venv/bin directly."
	@echo "Next: make setup-check && make api / make web (see docs/operations/LOCAL_SETUP.md)."

setup-check:
	@$(PYTHON) scripts/check_local_setup.py

api:
	@PYTHONPATH=apps/api/src:src $(UVICORN) spacebio_api.main:app --reload --host 0.0.0.0 --port 8000

web:
	@cd apps/web && npm run dev

services:
	@docker compose up -d
	@echo "Started Compose services (PostgreSQL + pgvector)."

db-bootstrap:
	@$(PYTHON) scripts/bootstrap_pgvector.py

migrate:
	@$(ALEMBIC) upgrade head

ingest:
	@$(PYTHON) scripts/ingest_corpus.py

lint:
	@$(RUFF) check .
	@$(RUFF) format --check .

typecheck:
	@$(PYRIGHT)

test:
	@$(PYTEST) -q

test-web:
	@npm run test:web

eval-hallucination:
	@$(PYTHON) evals/hallucination_check.py evals/fixtures/hallucination_answers.json

eval-graph-extraction:
	@$(PYTHON) evals/graph_extraction_eval.py evals/fixtures/graph_extraction_labels.json --json

validate: eval-hallucination lint typecheck test test-web
	@echo "Validation passed."

refresh-board:
	@$(PYTHON) scripts/refresh_active_board.py
	@echo "ACTIVE_BOARD.md refreshed. Commit docs/development/ACTIVE_BOARD.md with your task PR."

# Makefile for Space Biology Evidence Engine
# Keep targets aligned with AGENTS.md. Update AGENTS.md when tooling changes.
#
# Tooling prefers `.venv/bin` so `make lint|typecheck|test|validate` work from a
# fresh shell without requiring `source .venv/bin/activate`.

.PHONY: setup api web services db-bootstrap migrate lint typecheck test validate refresh-board help

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
	@echo "Targets: setup api web services db-bootstrap migrate lint typecheck test validate refresh-board"
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

lint:
	@$(RUFF) check .
	@$(RUFF) format --check .

typecheck:
	@$(PYRIGHT)

test:
	@$(PYTEST) -q

validate: lint typecheck test
	@echo "Validation passed."

refresh-board:
	@$(PYTHON) scripts/refresh_active_board.py
	@echo "ACTIVE_BOARD.md refreshed. Commit docs/development/ACTIVE_BOARD.md with your task PR."

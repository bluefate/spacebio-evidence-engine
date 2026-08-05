# Makefile for Space Biology Evidence Engine
# Keep targets aligned with AGENTS.md. Update AGENTS.md when tooling changes.

.PHONY: setup api web services db-bootstrap migrate lint typecheck test validate refresh-board help

PYTHON ?= python3
PIP ?= pip
RUFF ?= ruff
PYRIGHT ?= pyright
PYTEST ?= pytest
UVICORN ?= uvicorn
ALEMBIC ?= alembic

help:
	@echo "Targets: setup api web services db-bootstrap migrate lint typecheck test validate refresh-board"

setup:
	@test -f .env || cp .env.example .env
	@if [ ! -d .venv ]; then $(PYTHON) -m venv .venv; fi
	@. .venv/bin/activate && $(PIP) install -e ".[dev]"
	@. .venv/bin/activate && pre-commit install || true
	@if [ -f apps/web/package.json ]; then cd apps/web && npm install; fi
	@docker compose up -d
	@. .venv/bin/activate && $(PYTHON) scripts/bootstrap_pgvector.py || true
	@. .venv/bin/activate && $(ALEMBIC) upgrade head || true
	@echo "Setup complete. Activate with: source .venv/bin/activate"

api:
	@. .venv/bin/activate && PYTHONPATH=apps/api/src:src $(UVICORN) spacebio_api.main:app --reload --host 0.0.0.0 --port 8000

web:
	@cd apps/web && npm run dev

services:
	@docker compose up -d
	@echo "Started Compose services (PostgreSQL + pgvector)."

db-bootstrap:
	@. .venv/bin/activate && $(PYTHON) scripts/bootstrap_pgvector.py

migrate:
	@. .venv/bin/activate && $(ALEMBIC) upgrade head

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

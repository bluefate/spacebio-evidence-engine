# Makefile for Space Biology Evidence Engine
# Keep targets aligned with AGENTS.md. Update AGENTS.md when tooling changes.

.PHONY: setup api web services db-bootstrap lint typecheck test validate help

PYTHON ?= python3
PIP ?= pip
RUFF ?= ruff
PYRIGHT ?= pyright
PYTEST ?= pytest
UVICORN ?= uvicorn

help:
	@echo "Targets: setup api web services db-bootstrap lint typecheck test validate"

setup:
	@test -f .env || cp .env.example .env
	@if [ ! -d .venv ]; then $(PYTHON) -m venv .venv; fi
	@. .venv/bin/activate && $(PIP) install -e ".[dev]"
	@. .venv/bin/activate && pre-commit install || true
	@if [ -f apps/web/package.json ]; then cd apps/web && npm install; fi
	@docker compose up -d
	@. .venv/bin/activate && $(PYTHON) scripts/bootstrap_pgvector.py || true
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

lint:
	@$(RUFF) check .
	@$(RUFF) format --check .

typecheck:
	@$(PYRIGHT)

test:
	@$(PYTEST) -q

validate: lint typecheck test
	@echo "Validation passed."

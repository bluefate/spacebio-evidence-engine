# Makefile for Space Biology Evidence Engine
# Keep targets aligned with AGENTS.md. Update AGENTS.md when tooling changes.

.PHONY: setup api web services lint typecheck test validate help

PYTHON ?= python3
PIP ?= pip
RUFF ?= ruff
PYRIGHT ?= pyright
PYTEST ?= pytest

help:
	@echo "Targets: setup api web services lint typecheck test validate"

setup:
	@test -f .env || cp .env.example .env
	@if [ ! -d .venv ]; then $(PYTHON) -m venv .venv; fi
	@. .venv/bin/activate && $(PIP) install -e ".[dev]"
	@. .venv/bin/activate && pre-commit install || true
	@docker compose up -d
	@echo "Setup complete. Activate with: source .venv/bin/activate"

api:
	@echo "API package not scaffolded yet. Document start command in docs/operations/LOCAL_SETUP.md when apps/api (or equivalent) exists."
	@exit 1

web:
	@echo "Web package not scaffolded yet. Document start command in docs/operations/LOCAL_SETUP.md when apps/web (or equivalent) exists."
	@exit 1

services:
	@docker compose up -d
	@echo "Started Compose services (PostgreSQL + pgvector)."

lint:
	@$(RUFF) check .
	@$(RUFF) format --check .

typecheck:
	@$(PYRIGHT) src

test:
	@$(PYTEST) -q

validate: lint typecheck test
	@echo "Validation passed."

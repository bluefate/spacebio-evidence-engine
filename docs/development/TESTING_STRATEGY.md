# Testing Strategy

## Purpose
Define quality gates for software and scientific evidence behavior.

## Scope
Unit, integration, RAG evaluation, UI, and CI checks.

## Current status
Initial test strategy.

## Test layout

Repository tests live under `tests/` and are grouped by concern:

- `tests/api/` — FastAPI settings and health checks
- `tests/rag/` — retrieval and grounding behavior
- `tests/storage/` — storage abstractions
- `tests/` root — package smoke tests and cross-cutting behavior

Fixtures live under `tests/fixtures/` when a test needs checked-in sample data.

## MVP tests
- Unit tests for text processing, citation assembly, and schemas.
- Integration tests for database repositories and API endpoints.
- Retrieval evaluation against benchmark questions.
- Prompt regression tests for grounded answers.
- UI tests for citation rendering when frontend exists.
- Migration tests for Alembic revisions.
- Lint and type checks in CI.

## Running tests locally

- `make test` runs the Python test suite with `pytest -q`.
- `make validate` runs lint, type check, and tests together.
- `pytest tests/<path> -q` is useful for focused runs during implementation.
- `pytest -m integration` runs the optional integration-marked tests when local services are available.

## Related documents
- [Evaluation strategy](../rag/EVALUATION_STRATEGY.md)
- [Definition of done](DEFINITION_OF_DONE.md)
- [Pull request process](PULL_REQUEST_PROCESS.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).

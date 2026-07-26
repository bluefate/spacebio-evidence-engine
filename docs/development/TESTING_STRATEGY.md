# Testing Strategy

## Purpose
Define quality gates for software and scientific evidence behavior.

## Scope
Unit, integration, RAG evaluation, UI, and CI checks.

## Current status
Initial test strategy.

## MVP tests
- Unit tests for text processing, citation assembly, and schemas.
- Integration tests for database repositories and API endpoints.
- Retrieval evaluation against benchmark questions.
- Prompt regression tests for grounded answers.
- UI tests for citation rendering when frontend exists.
- Migration tests for Alembic revisions.
- Lint and type checks in CI.

## Related documents
- [Evaluation strategy](../rag/EVALUATION_STRATEGY.md)
- [Definition of done](DEFINITION_OF_DONE.md)
- [Pull request process](PULL_REQUEST_PROCESS.md)

## Human decisions still required
- Approve minimum coverage expectations.
- Choose frontend test framework.


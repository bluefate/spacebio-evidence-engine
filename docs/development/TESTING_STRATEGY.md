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
- `tests/ingestion/` — PDF extraction, page mapping, section detection, and chunking
- `tests/rag/` — retrieval and grounding behavior
- `tests/storage/` — storage abstractions
- `tests/` root — package smoke tests and cross-cutting behavior

Fixtures live under `tests/fixtures/` when a test needs checked-in sample data.

## Ingestion tests

Ingestion unit tests use deterministic synthetic text and the checked-in multi-page
PDF fixture. They should assert that extraction, sectioning, page mapping, and
chunking preserve publication provenance fields such as source keys, section
labels, offsets, pages, and chunking strategy lineage. They should also cover
typed failure paths without adding new corpus publications.

The end-to-end ingestion integration test composes the existing local PDF
storage, PDF extraction, chunking, chunk persistence, and final ingestion status
path against a migrated PostgreSQL test database. It uses only the checked-in
`tests/fixtures/sample_two_page.pdf` fixture and deletes its own fixture rows.

Run it locally with Compose PostgreSQL available:

```bash
make services
make migrate
SPACEBIO_REQUIRE_DB=1 pytest -q -m integration tests/integration/test_ingestion_e2e.py
```

Without `SPACEBIO_REQUIRE_DB=1`, the test skips when PostgreSQL is unavailable.

## Frontend tests (issues #69 and #68)

The Next.js app uses **Vitest** + Testing Library (`apps/web`). Coverage for
citation-first UI:

- `apps/web/src/app/ask/AskClient.test.tsx` — grounded answer citations, claims,
  evidence panel, insufficient-evidence banner, empty submit, API errors
- `apps/web/src/components/evidence/CitationLinks.test.tsx` — `[C1]` markers and
  publication links
- `apps/web/src/components/evidence/EvidencePanel.test.tsx` — passage provenance,
  empty list, missing active citation
- `apps/web/src/components/a11y/a11y.test.tsx` — keyboard/skip-link, labeled
  search/ask/evidence controls, **jest-axe** on those trees

`jest-axe` runs in jsdom. **color-contrast is disabled** there because jsdom
cannot compute real CSS contrast. Contrast for core controls is handled with
tokens: `--muted` (`#3d4f61` on `#f4f7fa`) and primary buttons using
`--accent-strong` (`#006888`) with white text. Use a browser axe extension for
full-page contrast after visual changes.

CI job **Node lint** also runs `npm run test -w @spacebio/web`.

## MVP tests
- Unit tests for text processing, citation assembly, and schemas.
- Integration tests for database repositories and API endpoints.
- Retrieval evaluation against benchmark questions.
- Prompt regression tests for grounded answers.
- UI tests for citation rendering and insufficient-evidence states (`make test-web`).
- Migration tests for Alembic revisions.
- Lint and type checks in CI.

## Running tests locally

- `make test` runs the Python test suite with `pytest -q`.
- `make test-web` runs Vitest for `apps/web` (`npm run test:web`).
- `make validate` runs lint, type check, Python tests, and web tests together.
- `cd apps/web && npm test` is equivalent to `make test-web`.
- `pytest tests/<path> -q` is useful for focused Python runs during implementation.
- `pytest -m integration` runs the optional integration-marked tests when local services are available.

## Related documents
- [Evaluation strategy](../rag/EVALUATION_STRATEGY.md)
- [Definition of done](DEFINITION_OF_DONE.md)
- [Pull request process](PULL_REQUEST_PROCESS.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).

# Parallel work guide

## Purpose

Tell humans and agents which August MVP issues can run concurrently, and which must stay serial.

## Scope

August MVP (`august-mvp` label) on [Project board #6](https://github.com/users/bluefate/projects/6).

## Rules

1. Claim from Project status `Ready` when possible ([AGENT_WORKFLOW.md](AGENT_WORKFLOW.md)).
2. One active implementation owner per issue.
3. Prefer issues labeled `parallel-safe` for concurrent agents.
4. Never start a second `parallel-unsafe` issue that shares the same files (especially `alembic/`, `src/spacebio_evidence_engine/db/`, ingest pipeline modules).
5. If overlap appears, stop and coordinate on the issue.

## Current critical path

1. **#27** Publication metadata schema — **Done** (merged PR #84).
2. **#28** PDF storage (`parallel-safe`) — Devin / parallel track.
3. **#29 → #30 → #31** Extract → sections → page map (after #28).
4. **#32 / #33** Chunking + chunk schema (`parallel-unsafe`).
5. **#39** Embedding provider interface → **#40 → #42 → #43 → #44** Embeddings and vector search.
6. **#51–#60** Grounded answers / API.
7. **#61–#66** Web UI for ask/evidence/citations.

## Good parallel picks while #28 / #39 are active

| Issue | Label | Typical files |
|-------|-------|----------------|
| #26 Reference questions | parallel-safe | `docs/` / eval fixtures |
| #23 License spot-check | parallel-safe | corpus docs / notes |
| #24 Duplicates | parallel-safe | inventory scripts/docs |
| #25 PDF quality | parallel-safe | corpus QA docs |
| #51 LLM provider interface | parallel-safe | provider interfaces (avoid `embeddings/`) |
| #57 Answer response schema | parallel-safe | Pydantic schemas |
| #55 Insufficient evidence | parallel-safe | RAG behavior module |
| #6 / #10 / #11 Foundation polish | parallel-safe | setup / test / lint docs |

## Avoid overlapping

- **#28:** PDF storage modules / docs owned by Devin — do not edit the same paths.
- **#39:** `src/spacebio_evidence_engine/embeddings/` until the interface PR merges; then #40 owns concrete local provider files.
- **#32 / #33 / #42:** Competing edits under `alembic/` or `src/spacebio_evidence_engine/db/` without coordination.

## Related documents

- [Repository README — What to work next](../../README.md#what-to-work-next-and-what-can-run-in-parallel)
- [Agent workflow](AGENT_WORKFLOW.md)
- [Backlog index](../governance/BACKLOG.md)
- [Project board](https://github.com/users/bluefate/projects/6)

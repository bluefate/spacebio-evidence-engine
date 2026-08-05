# Parallel work guide

## Purpose

Tell humans and agents which August MVP issues can run concurrently, and which must stay serial.

## Scope

August MVP (`august-mvp` label) on [Project board #6](https://github.com/users/bluefate/projects/6).

## Start here every time

1. Read [ACTIVE_BOARD.md](ACTIVE_BOARD.md).
2. Run `make refresh-board` so the Mermaid tree matches Project Status + open PRs.
3. Pick **one** Priority row that is not marked **Do not claim**.
4. Claim via [AGENT_WORKFLOW.md](AGENT_WORKFLOW.md).
5. Run `make refresh-board` again and commit `ACTIVE_BOARD.md` in the same PR.

Multiple agents may work in parallel **only** when they pick different issues that do not share file ownership.

## Rules

1. Claim from Project status `Ready` when possible ([AGENT_WORKFLOW.md](AGENT_WORKFLOW.md)).
2. One active implementation owner per issue.
3. Prefer issues labeled `parallel-safe` for concurrent agents.
4. Never start a second `parallel-unsafe` issue that shares the same files (especially `alembic/`, `src/spacebio_evidence_engine/db/`, ingest pipeline modules).
5. If overlap appears, stop and coordinate on the issue.
6. Always refresh and commit [ACTIVE_BOARD.md](ACTIVE_BOARD.md) when claiming or opening a PR so other agents see the tree move.

## Parallel agent checklist

Before you claim:

- [ ] `make refresh-board` ran successfully
- [ ] Chosen issue is not in the Mermaid **In flight** subgraph
- [ ] Chosen issue is not listed as **Do not claim** in Next options
- [ ] Open PRs checked for overlapping paths (`gh pr list` + claim comments)
- [ ] Issue labeled `parallel-safe` **or** you confirmed exclusive ownership is safe

After you claim:

- [ ] Claim comment posted (template in AGENT_WORKFLOW)
- [ ] Project Status → Claimed → In Progress
- [ ] Branch created: `feature|fix|docs|test|chore/<issue>-…`
- [ ] `make refresh-board` + commit `docs/development/ACTIVE_BOARD.md`

## Current critical path

1. **#27** Publication metadata schema — **Done** (merged PR #84).
2. **#28** PDF storage (`parallel-safe`) — was Devin; confirm claim status on board before taking.
3. **#29 → #30 → #31** Extract → sections → page map (after #28).
4. **#32 / #33** Chunking + chunk schema (`parallel-unsafe`).
5. **#39** Embedding provider interface — **Done** (PR #85) → **#40 → #42 → #43 → #44**.
6. **#51–#60** Grounded answers / API.
7. **#61–#66** Web UI for ask/evidence/citations.

## Good parallel picks (typical)

| Issue | Label | Typical files |
|-------|-------|----------------|
| #40 Local embeddings | after #39 Done | `embeddings/` concrete provider (not interface-only) |
| #51 LLM provider interface | parallel-safe | LLM interface package (avoid `embeddings/` if #40 active) |
| #26 Reference questions | parallel-safe | `docs/` / eval fixtures |
| #23 License spot-check | parallel-safe | corpus docs / notes |
| #24 Duplicates | parallel-safe | inventory scripts/docs |
| #25 PDF quality | parallel-safe | corpus QA docs |
| #57 Answer response schema | parallel-safe | Pydantic schemas |
| #55 Insufficient evidence | parallel-safe | RAG behavior module |
| #6 / #10 / #11 Foundation polish | parallel-safe | setup / test / lint docs |

Exact “what’s free right now” comes from `make refresh-board` → [ACTIVE_BOARD.md](ACTIVE_BOARD.md), not this static table.

## Avoid overlapping

- **In-flight issues** shown on ACTIVE_BOARD — do not claim.
- **#32 / #33 / #42:** Competing edits under `alembic/` or `src/spacebio_evidence_engine/db/` without coordination.
- Two agents on the same package path (e.g. both editing `embeddings/`).

## Related documents

- [Active board (Mermaid + next options)](ACTIVE_BOARD.md) — **start here** for current in-flight work and what to claim next
- [Repository README — What to work next](../../README.md#what-to-work-next-and-what-can-run-in-parallel)
- [Agent workflow](AGENT_WORKFLOW.md)
- [Backlog index](../governance/BACKLOG.md)
- [Project board](https://github.com/users/bluefate/projects/6)

# Space Biology Evidence Engine

![Space Biology Evidence Engine](docs/brand/logo-wordmark.png)

## Purpose
Define and build a citation-first evidence engine for a controlled corpus of open-access space biology publications.

## Scope
The August MVP (deadline 2026-08-31) focuses on retrieval-augmented generation, passage-level citations, evidence sufficiency, and a small corpus of approximately **10 to 15** open-access publications on **microgravity and skeletal muscle**. Study comparison and several advanced features are deferred past August.

## Repositories

| Role | Repository |
|------|------------|
| **Principal / development** | [bluefate/spacebio-evidence-engine](https://github.com/bluefate/spacebio-evidence-engine) |
| **Course submission (GitHub Classroom)** | [FAU-AI-HootCamp-Summer-2026/buildphase-bluefate](https://github.com/FAU-AI-HootCamp-Summer-2026/buildphase-bluefate) |

Development and day-to-day engineering happen in the principal repository. The Classroom repository is the official submission remote for AI HootCamp Summer 2026 and should stay in sync for plan, design, and incremental build deliverables.

## Backlog and project (source of truth)

Weekly windows in [plan.md](plan.md) are **schedule targets**. Execution order, ownership, and status live on GitHub:

| Resource | URL |
|----------|-----|
| **GitHub Project** | [Space Biology Evidence Engine (project #6)](https://github.com/users/bluefate/projects/6) |
| **Issues** | [bluefate/spacebio-evidence-engine/issues](https://github.com/bluefate/spacebio-evidence-engine/issues) |
| **Backlog index** | [docs/governance/BACKLOG.md](docs/governance/BACKLOG.md) |

Claim and implement from Project status `Ready` per [AGENT_WORKFLOW.md](docs/development/AGENT_WORKFLOW.md).

## What to work next (and what can run in parallel)

**Source of truth for status:** [Project board #6](https://github.com/users/bluefate/projects/6).  
**Rule:** one owner per issue; do not edit files owned by another active `parallel-unsafe` issue.

### Critical path (mostly serial — keep moving the MVP)

Do these in order unless a dependency is already Done:

| Order | Issue | Notes |
|------:|-------|-------|
| 1 | [#27](https://github.com/bluefate/spacebio-evidence-engine/issues/27) Publication metadata schema | **Done** (PR #84) |
| 2 | [#28](https://github.com/bluefate/spacebio-evidence-engine/issues/28) PDF storage abstraction | Devin track (`parallel-safe`) |
| 3 | [#29](https://github.com/bluefate/spacebio-evidence-engine/issues/29) → [#30](https://github.com/bluefate/spacebio-evidence-engine/issues/30) → [#31](https://github.com/bluefate/spacebio-evidence-engine/issues/31) | PDF extract → sections → page mapping (after #28) |
| 4 | [#32](https://github.com/bluefate/spacebio-evidence-engine/issues/32) / [#33](https://github.com/bluefate/spacebio-evidence-engine/issues/33) | Chunking + chunk schema (`parallel-unsafe`) |
| 5 | **[#39](https://github.com/bluefate/spacebio-evidence-engine/issues/39)** → [#40](https://github.com/bluefate/spacebio-evidence-engine/issues/40) → [#42](https://github.com/bluefate/spacebio-evidence-engine/issues/42) → [#43](https://github.com/bluefate/spacebio-evidence-engine/issues/43) → [#44](https://github.com/bluefate/spacebio-evidence-engine/issues/44) | Embeddings → vector schema/index → search (**#39 in progress**) |
| 6 | [#51](https://github.com/bluefate/spacebio-evidence-engine/issues/51)–[#60](https://github.com/bluefate/spacebio-evidence-engine/issues/60) | Grounded answer / `/ask` API |
| 7 | [#61](https://github.com/bluefate/spacebio-evidence-engine/issues/61)–[#66](https://github.com/bluefate/spacebio-evidence-engine/issues/66) | Web ask / evidence / citation UI |

### Safe to run in parallel **right now** (while #28 / #39 run)

Pick **one** issue per agent. Prefer Project status `Ready` + label `parallel-safe`:

| Issue | Why it is parallel-safe |
|-------|-------------------------|
| [#26](https://github.com/bluefate/spacebio-evidence-engine/issues/26) Ten reference research questions | Docs/eval data only |
| [#23](https://github.com/bluefate/spacebio-evidence-engine/issues/23) License/access spot-check | Corpus rights review |
| [#24](https://github.com/bluefate/spacebio-evidence-engine/issues/24) Duplicate detection | Inventory tooling/docs |
| [#25](https://github.com/bluefate/spacebio-evidence-engine/issues/25) PDF quality assessment | Corpus QA notes |
| [#51](https://github.com/bluefate/spacebio-evidence-engine/issues/51) LLM provider interface | Interface stubs (not `embeddings/`) |
| [#57](https://github.com/bluefate/spacebio-evidence-engine/issues/57) Grounded answer response schema | Pydantic schemas only |
| [#55](https://github.com/bluefate/spacebio-evidence-engine/issues/55) Insufficient-evidence behavior | Spec/module without ingest tables |
| [#49](https://github.com/bluefate/spacebio-evidence-engine/issues/49) / [#47](https://github.com/bluefate/spacebio-evidence-engine/issues/47) / [#50](https://github.com/bluefate/spacebio-evidence-engine/issues/50) | Retrieval logging / filters / eval harness (design + stubs OK) |
| [#6](https://github.com/bluefate/spacebio-evidence-engine/issues/6) / [#10](https://github.com/bluefate/spacebio-evidence-engine/issues/10) / [#11](https://github.com/bluefate/spacebio-evidence-engine/issues/11) | Local setup / pytest / ruff polish |

### Do **not** parallelize without coordination

These are `parallel-unsafe` and/or share Alembic/ORM/ingest ownership:

- [#32](https://github.com/bluefate/spacebio-evidence-engine/issues/32), [#33](https://github.com/bluefate/spacebio-evidence-engine/issues/33), [#42](https://github.com/bluefate/spacebio-evidence-engine/issues/42), [#43](https://github.com/bluefate/spacebio-evidence-engine/issues/43)
- Active owners of [#28](https://github.com/bluefate/spacebio-evidence-engine/issues/28) (PDF storage) and [#39](https://github.com/bluefate/spacebio-evidence-engine/issues/39) (`embeddings/`)
- Any second agent on `alembic/`, `src/spacebio_evidence_engine/db/`, or the same ingest pipeline modules

### Human gate (does not block parallel coding)

Corpus list rows are still `human_approval=pending`. Approve on [#20](https://github.com/bluefate/spacebio-evidence-engine/issues/20) before bulk ingest; parallel **schema/interface** work can continue.

**Live Mermaid board + next-task menu for agents:** [docs/development/ACTIVE_BOARD.md](docs/development/ACTIVE_BOARD.md).  
More detail: [docs/development/PARALLEL_WORK.md](docs/development/PARALLEL_WORK.md).

## Build Phase deliverables

| Document | Description |
|----------|-------------|
| [plan.md](plan.md) | Project plan: summary, requirements, RAG/production/security topics, weekly milestones |
| [design.md](design.md) | Technical design: architecture, data flow, user flow, schema, API, AI/RAG, deployment |

Supporting deep-dive documentation lives under [docs/](docs/README.md).

## Current status
Documentation-first project with locked Build Phase decisions and an **end-of-August 2026 MVP** (deadline 2026-08-31). Implementation scaffolding is next. See [plan.md](plan.md) and [decision log](docs/governance/DECISION_LOG.md).

## Architecture position
Accepted stack for the August MVP:

- Python 3.12+, FastAPI, PostgreSQL, pgvector, **SQLAlchemy 2.x + Alembic**, Pydantic API schemas, PyMuPDF, Sentence Transformers (`all-MiniLM-L6-v2`), optional OpenAI (`gpt-4o-mini`, **$50/mo hard cap**), Next.js, TypeScript, Docker Compose, Pytest, Ruff, **pyright**, GitHub Actions, Mermaid.
- Neo4j, study compare UI, hybrid retrieval, auth, and public hosting are deferred past August.
- Advanced multi-agent orchestration and advanced contradiction detection remain future capabilities.

## Start here
- [Build plan](plan.md)
- [Technical design](design.md)
- [Decision log](docs/governance/DECISION_LOG.md)
- [Documentation index](docs/README.md)
- [GitHub Project board](https://github.com/users/bluefate/projects/6)
- [Backlog index](docs/governance/BACKLOG.md)
- [Product requirements](docs/product/PRODUCT_REQUIREMENTS.md)
- [Architecture overview](docs/architecture/ARCHITECTURE.md)
- [RAG architecture](docs/architecture/RAG_ARCHITECTURE.md)
- [Development guide](docs/development/DEVELOPMENT_GUIDE.md)
- [Agent workflow](docs/development/AGENT_WORKFLOW.md)
- [Active board (Mermaid + next options)](docs/development/ACTIVE_BOARD.md)
- [Parallel work guide](docs/development/PARALLEL_WORK.md)

## Related documents
- [Corpus specification](docs/data/CORPUS_SPECIFICATION.md)
- [Citation strategy](docs/rag/CITATION_STRATEGY.md)
- [Evaluation strategy](docs/rag/EVALUATION_STRATEGY.md)
- [Risk register](docs/governance/RISK_REGISTER.md)
- [Decision log](docs/governance/DECISION_LOG.md)

## Open follow-ons (do not block August MVP)
- Select the final ~10–15 open-access publications for the approved topic.
- Public hosting platform (deferred past local Compose demo).
- Production secret manager, observability stack, and user accounts (post-August).

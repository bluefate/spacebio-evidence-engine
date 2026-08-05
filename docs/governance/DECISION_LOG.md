# Decision Log

## Purpose
Track architecture and product decisions.

## Scope
Major technical, scientific, product, data, and operational decisions.

## Current status
Accepted baseline for the end-of-August 2026 MVP. Single-file decision log (no per-decision ADR files for now).

## Accepted architecture decisions

| ID | Decision | Status | Notes |
| --- | --- | --- | --- |
| ADR-001 | Use RAG with passage-level citations | Accepted | Required by project definition |
| ADR-002 | Use PostgreSQL + pgvector for MVP | Accepted | Avoids separate vector DB |
| ADR-003 | Defer Neo4j until graph phase | Accepted | Graph is useful but not MVP infrastructure |
| ADR-004 | Use FastAPI backend | Accepted | Fits Python RAG stack |
| ADR-005 | Use Next.js TypeScript frontend | Accepted | Citation inspection UI path |
| ADR-006 | Use provider abstraction for LLMs | Accepted | Local and OpenAI-backed modes |
| ADR-007 | Use Apache-2.0 license | Accepted | Confirmed; already in repository `LICENSE` |

## Accepted product and delivery decisions (2026-08-04)

| ID | Decision | Status | Notes |
| --- | --- | --- | --- |
| D1 | Topic + corpus selection rules | Accepted | Topic: microgravity and skeletal muscle. Rules: open-access with clear rights; on-topic; extractable methods/results; citable metadata. Exclude paywalled/unclear rights, off-topic, unusable extraction, unapproved commentary. Paper list selection is a follow-on task. |
| D2 | ORM and API schemas | Accepted | SQLAlchemy 2.x + Alembic. API schemas via Pydantic (not SQLModel). |
| D3 | Primary type checker | Accepted | pyright |
| D4 | Model providers and cost limits | Accepted | Embeddings: local Sentence Transformers (`all-MiniLM-L6-v2`). LLM: optional OpenAI behind abstraction (`gpt-4o-mini` when enabled). Hard monthly LLM cap $50. Local/dev mode must work at $0 cloud spend. |
| D5 | Public license | Accepted | Apache-2.0 (same as ADR-007) |
| D6 | MVP date and scope | Accepted | Deadline 2026-08-31. Corpus size ~10–15 OA papers. See compressed MVP below. |
| D7 | August MVP deployment | Accepted | Local Docker Compose only; public hosting deferred |
| D8 | Authentication | Accepted | Out of August MVP; anonymous local use |
| D9 | ADR file format | Accepted | Keep this single decision log; no per-file ADRs for now |
| D10 | Corpus licenses including CC BY-NC-ND | Accepted | Engine is non-commercial (education/research/HootCamp). CC BY preferred; CC BY-NC-ND allowed for retrieval + attributed quotation with no commercial full-text redistribution. Re-review NC-ND if the project becomes commercial. See CORPUS_SPECIFICATION.md and CORPUS_INVENTORY.md. |

## End-of-August MVP scope (D6)

**Must ship by 2026-08-31**

1. Scaffold: FastAPI + Next.js + PostgreSQL/pgvector via Docker Compose
2. Controlled corpus of OA papers (proposed inventory; see corpus docs; size may exceed original 10–15 when owner adds high-relevance OA studies)
3. Ingest → chunk → embed → store lineage
4. Semantic search API
5. Grounded `/ask` with passage citations and insufficient-evidence path
6. Minimal web UI: ask, answer + citations, open passage
7. Tiny eval set (~5–10 benchmark questions) + smoke tests
8. Docs in sync (`plan.md`, `design.md`, this log)

**Deferred past August MVP**

- Study comparison UI
- Hybrid keyword retrieval
- Entity/relationship extraction and graph prep
- Tables/figures as first-class chunks
- Separate always-on worker service (use CLI/jobs)
- Public cloud deploy, auth/RBAC, Redis/CDN, production observability

## Accepted August MVP defaults

| Topic | Decision |
| --- | --- |
| Worker vs CLI | CLI/jobs, not a separate always-on worker |
| Tables/figures | Out of August MVP |
| Hybrid retrieval | Out; vector-only |
| Relationships | When added later: provisional until human reviewed |
| Citation display | Passage excerpt + title + section + page + source link |
| Citation granularity | Passage-level |
| Chunk size | ~500–900 tokens, overlap ~10–20%; tune later |
| Top-k | 8 default; no reranker in August |
| Prompt structure | Structured citation IDs required; answer text free-form |
| Package layout | Simple monorepo: `apps/api`, `apps/web` (`packages` later if needed) |
| Local ports | API `8000`, web `3000`, Postgres `5432` |
| Branching | Protect `main`; squash merge; 1 human approval to merge |
| Agents create issues | Yes, within backlog rules |
| Agent ownership | Single issues only, not long-running epics |
| Corpus PR review | Owner scientific/license review required |
| CI for merge | lint + typecheck + tests |
| Coverage | No hard % for August; critical RAG paths tested |
| Frontend tests | August: smoke/manual OK; Playwright later |
| Prompt logging | Log IDs/versions; redact full prompt bodies by default |
| Answer log retention | Keep locally for eval; no public retention policy yet |
| Backup | Compose volumes; regenerate-from-manifest documented |
| Versioning | SemVer when first tagged release exists |
| Anonymous users | Yes for local MVP |
| Ontology / controlled vocab | Out of August MVP; free-text metadata OK |
| Docs ownership | Repository owner |
| External contributions | Not expected for August |
| Vulnerability channel | `SECURITY.md` / GitHub advisories |
| Code of conduct | Keep current CoC; full Contributor Covenant later if needed |
| Issues without UX mocks | Allowed for August |
| Target user priority | Researchers first; students/educators second |

## Explicitly deferred (do not block 2026-08-31)

- Final 10–15 paper titles (after D1)
- Public hosting platform
- Production secret manager / observability stack
- User accounts / IAM
- Final benchmark question set (start with draft 5–10)
- Risk owners, release approvers, requirement ID freeze

## Related documents
- [Architecture overview](../architecture/ARCHITECTURE.md)
- [Project roadmap](PROJECT_ROADMAP.md)
- [Build plan](../../plan.md)
- [Technical design](../../design.md)
- [Corpus specification](../data/CORPUS_SPECIFICATION.md)
- [Risk register](RISK_REGISTER.md)
- [Traceability matrix](TRACEABILITY_MATRIX.md)

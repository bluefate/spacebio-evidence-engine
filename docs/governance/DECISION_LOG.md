# Decision Log

## Purpose
Track architecture and product decisions.

## Scope
Major technical, scientific, product, data, and operational decisions.

## Current status
Initial decision log.

## Proposed decisions
| ID | Decision | Status | Notes |
| --- | --- | --- | --- |
| ADR-001 | Use RAG with passage-level citations | Proposed | Required by project definition |
| ADR-002 | Use PostgreSQL + pgvector for MVP | Proposed | Avoids separate vector DB |
| ADR-003 | Defer Neo4j until graph phase | Proposed | Graph is useful but not MVP infrastructure requirement |
| ADR-004 | Use FastAPI backend | Proposed | Fits Python RAG stack |
| ADR-005 | Use Next.js TypeScript frontend | Proposed | Strong citation inspection UI path |
| ADR-006 | Use provider abstraction for LLMs | Proposed | Allows local and OpenAI-backed modes |
| ADR-007 | Recommend Apache-2.0 license | Proposed | Needs human/legal approval |

## Related documents
- [Architecture overview](../architecture/ARCHITECTURE.md)
- [Risk register](RISK_REGISTER.md)
- [Traceability matrix](TRACEABILITY_MATRIX.md)

## Human decisions still required
- Approve or reject each proposed decision.
- Decide whether to create one ADR file per accepted decision.


# Definition of Done

## Purpose
Define completion criteria for engineering work.

## Scope
All repository changes by humans and agents.

## Current status
Active completion checklist. Root contract: [AGENTS.md](../../AGENTS.md).

## Done checklist
- Acceptance criteria satisfied.
- Tests added or updated for new behavior; tests not disabled to force a green build.
- Lint and type checks pass (`make lint`, `make typecheck`, or `make validate`).
- Migrations added when schema changes; risks noted.
- Documentation updated when architecture, commands, schemas, or behavior change.
- Material architecture decisions recorded in the [decision log](../governance/DECISION_LOG.md) / ADR process.
- RAG changes include retrieval/citation evaluation notes.
- Citation identifiers, sections, pages, and passages remain intact.
- Security-sensitive changes called out for human review.
- PR opened against `main` with issue link, validation report, and human review requested.
- No secrets committed; `.env.example` updated if new config keys were added.

## Related documents
- [Testing strategy](TESTING_STRATEGY.md)
- [Pull request process](PULL_REQUEST_PROCESS.md)
- [Agent workflow](AGENT_WORKFLOW.md)
- [Release process](../governance/RELEASE_PROCESS.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).

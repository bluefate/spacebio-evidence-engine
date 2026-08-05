# Pull Request Process

## Purpose
Define review expectations for repository changes.

## Scope
All code, docs, prompts, corpus metadata, and schema changes.

## Current status
Active process. Agents open PRs; humans approve and merge.

## Process
- Open a focused PR linked to an issue (`Closes #N` / `Fixes #N`).
- Fill the PR template completely, including:
  - **Related issues** table (primary, related, blocked-by / assumes).
  - **Issue items** checklist copied from the issue acceptance criteria, follow-up bullets, or task list, with each item marked done or deferred (link a follow-up issue when deferred).
- Explain the change and identify affected components.
- List tests executed and include a clear validation report.
- Include documentation changes (or state none were required).
- Identify migrations, security/privacy effects, and remaining risks.
- For RAG changes, include retrieval and citation evaluation notes.
- For corpus changes, include license and metadata review.
- For architecture changes, link the ADR / decision log entry.
- Request human review; leave an agent handoff or `ready_for_review` progress comment with the PR URL when ready or when work stops.
- Remain unmerged until a human approves.

Reviewers should be able to verify scope against the PR body without re-reading the full issue thread.

### Format compliance

Agents must follow the comment templates in [AGENT_WORKFLOW.md](AGENT_WORKFLOW.md) and the sections in `.github/pull_request_template.md`. Free-form comments are only for replies inside an existing review thread, not for claim / progress / handoff / PR-open posts.

## Agent prohibitions
- Do not approve or merge pull requests.
- Do not enable auto-merge.
- Do not dismiss reviews.
- Do not push directly to `main`.

## Related documents
- [AGENTS](../../AGENTS.md)
- [Definition of ready](DEFINITION_OF_READY.md)
- [Definition of done](DEFINITION_OF_DONE.md)
- [Testing strategy](TESTING_STRATEGY.md)
- [Agent workflow](AGENT_WORKFLOW.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).

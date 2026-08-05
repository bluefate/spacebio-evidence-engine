# CONTRIBUTING

## Purpose
Explain how contributors should propose and land changes.

## Scope
Applies to code, documentation, prompts, database schema, corpus metadata, and evaluation data.

## Current status
Initial contribution policy for a pre-implementation repository.

## Contribution rules
- Start from a GitHub issue in Project status `Ready`. Board: [Space Biology Evidence Engine (project #6)](https://github.com/users/bluefate/projects/6).
- Keep changes small and traceable.
- Update tests, docs, prompts, and migrations when behavior changes.
- Do not add publications to the corpus without license and metadata review.
- Do not add model-specific logic outside provider abstractions.
- Do not claim scientific conclusions without passage-level citations.

## Pull request expectations
- Link the issue.
- Explain user-visible behavior.
- List tests and checks run.
- Identify changed docs or state that none were needed.
- Include screenshots for UI changes.
- Include retrieval/citation evaluation notes for RAG changes.

## Related documents
- [README backlog and project](README.md#backlog-and-project-source-of-truth)
- [Agent workflow](docs/development/AGENT_WORKFLOW.md)
- [Development guide](docs/development/DEVELOPMENT_GUIDE.md)
- [Branching strategy](docs/development/BRANCHING_STRATEGY.md)
- [Pull request process](docs/development/PULL_REQUEST_PROCESS.md)
- [Testing strategy](docs/development/TESTING_STRATEGY.md)
- [Backlog index](docs/governance/BACKLOG.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](docs/governance/DECISION_LOG.md).


# Branching Strategy

## Purpose
Define how branches move from work to review to release.

## Scope
Git branch naming, pull request flow, and release branches.

## Current status
Initial strategy.

## Flow
```mermaid
gitGraph
  commit id: "main"
  branch feature/rag-retrieval
  checkout feature/rag-retrieval
  commit id: "implement"
  commit id: "tests"
  checkout main
  merge feature/rag-retrieval id: "PR merge"
  branch release/mvp-0.1
  checkout release/mvp-0.1
  commit id: "release notes"
  checkout main
  merge release/mvp-0.1 id: "tag"
```

## Branch naming
- `feature/<short-name>`
- `fix/<short-name>`
- `docs/<short-name>`
- `experiment/<short-name>`
- `release/<version>`

## Related documents
- [Pull request process](PULL_REQUEST_PROCESS.md)
- [Release process](../governance/RELEASE_PROCESS.md)
- [Contributing](../../CONTRIBUTING.md)

## Human decisions still required
- Confirm branch protection.
- Confirm squash versus merge commits.


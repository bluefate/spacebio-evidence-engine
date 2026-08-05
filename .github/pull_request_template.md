## Linked issue

Closes #

<!-- Use Closes/Fixes for the primary issue. List additional related issues below. -->

## Related issues

| Relationship | Issue | Notes |
| --- | --- | --- |
| Primary | # | This PR implements |
| Related | # | Optional — docs, deps, follow-ups |
| Blocked by / assumes | # | Optional — upstream work this PR relies on |

## Issue items

<!-- REQUIRED for agent PRs. Copy acceptance criteria / follow-up bullets / task list from the linked issue. Mark each item. -->

- [ ] Item 1 from the issue
- [ ] Item 2 from the issue
- [ ] Deferred / out of scope (link follow-up issue if needed): 

## Summary

<!-- One short paragraph: what this PR does. -->

## Changes

-
-

## Reason

<!-- Why this change is needed now. -->

## Test evidence

```text
make lint
make typecheck
make test
# or make validate
```

- Commands run:
- Results:
- New/updated tests:

## Retrieval or RAG effects

- [ ] No RAG / retrieval / citation / prompt changes
- [ ] Retrieval behavior changed — describe:
- [ ] Generation / prompting changed — describe:
- [ ] Citation or grounding behavior changed — describe:
- [ ] Evaluation notes attached or linked:

## Data schema effects

- [ ] No schema changes
- [ ] Schema changed — tables/columns/indexes:
- [ ] Migration ID(s):

## Documentation updates

- [ ] Docs updated (list paths):
- [ ] Docs not required — why:

## Security effects

- [ ] No security or privacy impact
- [ ] Secrets / env keys changed (`.env.example` updated)
- [ ] Document parsing or untrusted content handling changed
- [ ] Auth, network exposure, or dependency risk — describe:

## Screenshots

<!-- Required for UI changes. Otherwise write N/A. -->

## Migration instructions

<!-- Steps to apply schema or data migrations. Write N/A if none. -->

## Rollback instructions

<!-- How to reverse this change safely. Write N/A if none. -->

## Known limitations

-
-

## Human review checklist

- [ ] Issue linked and **Issue items** checklist filled from the issue
- [ ] Related issues listed (or marked none)
- [ ] Acceptance criteria / follow-up items addressed or deferred with links
- [ ] Tests, lint, and type checks reported
- [ ] Documentation current
- [ ] No secrets committed
- [ ] Scientific provenance / citations preserved where applicable
- [ ] Migrations and rollback reviewed if applicable
- [ ] Remaining risks understood
- [ ] Human approval required before merge (agents must not approve or merge)

# Pull Request Process

## Purpose
Define review expectations for repository changes.

## Scope
All code, docs, prompts, corpus metadata, and schema changes.

## Current status
Active process. Agents open PRs; humans approve and merge.

## Process
- Open a focused PR linked to an issue.
- Explain the change and identify affected components.
- List tests executed and include a clear validation report.
- Include documentation changes (or state none were required).
- Identify migrations, security/privacy effects, and remaining risks.
- For RAG changes, include retrieval and citation evaluation notes.
- For corpus changes, include license and metadata review.
- For architecture changes, link the ADR / decision log entry.
- Request human review; leave an agent handoff comment when ready or when work stops.
- Remain unmerged until a human approves.

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

## Human decisions still required
- Confirm required approvals.
- Decide whether scientific reviewer approval is mandatory for corpus changes.

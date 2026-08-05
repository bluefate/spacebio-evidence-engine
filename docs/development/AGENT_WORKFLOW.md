# Agent Workflow

## Purpose

Define a task claiming system for human and AI contributors that prevents multiple agents from unknowingly modifying the same component. GitHub issues and the GitHub Project are the source of truth for task state and ownership.

## Scope

Task claiming, conflict prevention, implementation, review, handoff, and blocked-state handling for all contributors, including AI agents and human engineers.

## Source of truth

- **GitHub issue:** Scope, acceptance criteria, dependencies, linked PRs, and claim status. [Issues](https://github.com/bluefate/spacebio-evidence-engine/issues)
- **GitHub Project:** Issue status (`Planning`, `Human Review`, `Ready`, `Claimed`, `In Progress`, `PR Open`, `Done`). Board: [Space Biology Evidence Engine (project #6)](https://github.com/users/bluefate/projects/6)
- **Backlog index:** [BACKLOG.md](../governance/BACKLOG.md)
- **Branch name:** One branch per issue, using [BRANCHING_STRATEGY](BRANCHING_STRATEGY.md).
- **This document:** The canonical claiming procedure and standard comment templates.

## Project workflow

- `Planning`: New ideas and future work. Requirements are still being discussed or decomposed.
- `Human Review`: Items requiring approval or decisions from the project owner. Typical examples include product requirements, architecture, technology choices, and major design decisions. Agents must not implement tasks in this column.
- `Ready`: Fully defined, dependency-free tasks that are safe for an agent to begin. Each task must have clear acceptance criteria, no unresolved human decisions, completed dependencies, expected files/components identified, and `Parallel Safe = Yes` when applicable.
- `Claimed`: An agent has claimed the task and created a working branch.
- `In Progress`: Active implementation is underway.
- `PR Open`: A pull request has been opened. The task is awaiting automated checks and human review. Agents may respond to review comments but may not approve or merge.
- `Done`: Human approved and merged. Documentation, project board, and linked issues are updated.

## Prerequisites

Before claiming an issue, read:

1. [AGENTS.md](../../AGENTS.md)
2. [CONTRIBUTING.md](../../CONTRIBUTING.md)
3. The assigned GitHub issue
4. [ARCHITECTURE.md](../architecture/ARCHITECTURE.md)
5. [RAG_ARCHITECTURE.md](../architecture/RAG_ARCHITECTURE.md)
6. [DEFINITION_OF_READY.md](DEFINITION_OF_READY.md)
7. [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md)
8. Documentation specific to the affected component

## Claiming workflow

Follow the steps below in order. GitHub Project status transitions are required unless the Project is unavailable.

1. **Read AGENTS.md.** Confirm the authority, task rules, and stop conditions that apply to this repository.
2. **Read [ACTIVE_BOARD.md](ACTIVE_BOARD.md).** Use the Mermaid board and **Next options** table to pick work and to show humans/other agents what is free. Update that file in the same PR when you claim, open a PR, or clear a task.
3. **Select an issue in Ready.** The issue must satisfy [DEFINITION_OF_READY.md](DEFINITION_OF_READY.md).
4. **Skip human-review work.** If the selected task is blocked because it requires human approval, automatically look for the next `Ready`, dependency-free, parallel-safe task. Only stop when no such task exists.
5. **Check dependencies.** Verify that blocking issues, upstream PRs, and required data or credentials are available. If a dependency is missing, continue searching for another `Ready`, dependency-free, parallel-safe task.
6. **Check Parallel Safe.** Read the issue body and comments for a `Parallel Safe` flag or overlapping work. If the issue is not marked parallel safe and exclusive ownership is not safe, continue searching.
7. **Check active pull requests for overlapping files.** Review open PRs for changes to the same files or components. If overlap exists, coordinate on the issue or continue searching for a non-overlapping task.
8. **Assign the issue to yourself when supported.** If the GitHub API or repository permissions allow assignment, assign the issue to the current agent. Otherwise, proceed by comment and Project status only.
9. **Post a claim comment.** Use the [Claiming comment template](#claiming-comment-template).
10. **Move the issue to Claimed.** Update the GitHub Project status to `Claimed`.
11. **Create a branch.** Use one branch per issue following [BRANCHING_STRATEGY](BRANCHING_STRATEGY.md).
12. **Post the branch name.** Reply on the issue with the branch name.
13. **Move the issue to In Progress.** Update the GitHub Project status to `In Progress`.
14. **Implement only the defined scope.** Do not expand scope or fix unrelated findings without creating a follow-up issue.
15. **Post progress comments for long tasks.** Use the [Progress comment template](#progress-comment-template) when work spans multiple sessions or exceeds a short interval.
16. **Run required validation.** Execute `make lint`, `make typecheck`, `make test`, and `make validate` as applicable. Fix failures before opening a PR.
17. **Open a pull request.** Link the PR to the issue, fill out the PR template, and include a validation report. Also refresh [ACTIVE_BOARD.md](ACTIVE_BOARD.md) so other agents see the new In-flight / Next options state.
18. **Move the issue to PR Open.** Update the GitHub Project status to `PR Open`.
19. **Respond to review comments.** Address human and agent feedback, push follow-up commits, and re-request review when ready.
20. **Do not approve or merge.** Agents may review and comment, but only humans may approve or merge.
21. **Human approves and merges.** After merge, the branch may be deleted.
22. **Issue moves to Done.** The GitHub Project status is updated to `Done`. Update [ACTIVE_BOARD.md](ACTIVE_BOARD.md) in a follow-up if the merge PR did not already move the node to Done.

## Conflict prevention

- One active implementation owner per issue unless the issue is explicitly marked `Parallel Safe`.
- If two agents need the same files, stop and coordinate on the issue. Do not overwrite silently.
- If requirements conflict, stop and ask for human input.
- Do not modify files controlled by another active issue without coordination.
- Prefer narrowly scoped PRs; avoid long-lived overlapping branches.

## Human-only controls

- Do not push directly to `main`.
- Do not approve or merge pull requests.
- Do not change branch protection, required checks, or auto-merge settings.
- Do not modify secrets or repository access tokens.

## Handoff and blocked states

- If work stops before completion, post a [Handoff comment](#handoff-comment-template).
- If work is blocked, post a [Blocked comment](#blocked-comment-template), move the issue to a blocked column if available, and unassign or hand off if appropriate.
- Unclaim or hand off promptly if blocked for more than a short interval.

## Standard comment templates

### Claiming comment template

Use this comment when claiming an issue and after creating the branch.

```markdown
### Claimed by agent

- **CLAIMED BY:** @agent-name-or-identifier
- **AGENT TYPE:** ChatGPT | Cursor | Devin | Codex | Human | Other
- **START TIME:** YYYY-MM-DD HH:MM UTC±N
- **BRANCH:** feature/<issue-number>-<description>
- **EXPECTED FILES:**
  - path/to/expected/file.ext
- **DEPENDENCIES CHECKED:** yes/no — list blockers or links
- **OVERLAP CHECKED:** yes/no — list overlapping issues or PRs
- **EXPECTED COMPLETION:** YYYY-MM-DD HH:MM UTC±N
```

### Progress comment template

Use this comment for status updates on long-running issues.

```markdown
### Progress update

- **STATUS:** in_progress | blocked | ready_for_review
- **COMPLETED:**
  - Item finished since last update
- **NEXT:**
  - Next step
- **BLOCKERS:**
  - Any blockers
- **SCOPE CHANGES:**
  - Any scope changes with justification and approval
- **FILES ADDED OR MODIFIED:**
  - path/to/file.ext
```

### Handoff comment template

Use this comment when work stops (PR opened, blocked, or reassigned).

```markdown
### Agent handoff

- **WORK COMPLETED:**
  - Summary of completed work
- **WORK REMAINING:**
  - Summary of remaining work
- **BRANCH:** feature/<issue-number>-<description>
- **LAST COMMIT:** abc1234
- **TESTS:**
  - Tests run and results
- **KNOWN FAILURES:**
  - Any known failures or skipped tests
- **DECISIONS NEEDED:**
  - Decisions required from a human or next agent
- **SAFE TO REASSIGN:** yes/no — reason
```

### Blocked comment template

Use this comment when work cannot continue.

```markdown
### Blocked

- **BLOCKED BY:**
  - Issue, dependency, or reason
- **IMPACT:**
  - What is blocked and for how long
- **ATTEMPTS:**
  - Steps already tried
- **HUMAN DECISION NEEDED:** yes/no — what decision is required
- **SAFE WORK THAT CAN CONTINUE:**
  - Any independent work that can proceed
```

## Architecture decisions

- Record material architecture changes in [DECISION_LOG](../governance/DECISION_LOG.md) (and dedicated ADR files once that format is approved).
- Keep MVP and future architecture separate.
- Do not introduce Neo4j, autonomous multi-agent orchestration, or advanced contradiction detection as required MVP dependencies.

## RAG and scientific rules (summary)

- Preserve grounding and passage-level citations.
- Do not answer scientific questions from model memory when the application should use the corpus.
- Details: [CITATION_STRATEGY](../rag/CITATION_STRATEGY.md), [PROMPTING_STRATEGY](../rag/PROMPTING_STRATEGY.md), [EVALUATION_STRATEGY](../rag/EVALUATION_STRATEGY.md).

## Related documents

- [AGENTS](../../AGENTS.md)
- [Definition of ready](DEFINITION_OF_READY.md)
- [Definition of done](DEFINITION_OF_DONE.md)
- [Pull request process](PULL_REQUEST_PROCESS.md)
- [Testing strategy](TESTING_STRATEGY.md)
- [Branching strategy](BRANCHING_STRATEGY.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).

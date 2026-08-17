# AGENTS.md

## Project

Space Biology Evidence Engine is a retrieval-augmented system for searching and answering questions from an approved corpus of space biology publications.

The system must preserve scientific provenance and generate answers grounded in retrieved evidence.

## Authority

The human repository owner has final authority over requirements, architecture, security, pull request approval, and merging.

Agents may propose and implement changes. Agents may not approve or merge pull requests.

## Required Reading

Before starting work, read:

1. README.md
2. CONTRIBUTING.md
3. The assigned GitHub issue
4. docs/architecture/ARCHITECTURE.md
5. docs/architecture/RAG_ARCHITECTURE.md
6. docs/development/AGENT_WORKFLOW.md
7. docs/development/ACTIVE_BOARD.md — Mermaid live board + next-task menu; keep current with `make refresh-board`
8. docs/development/DEFINITION_OF_DONE.md
9. Documentation specific to the affected component

## Task Rules

1. Work only from a GitHub issue.
2. Confirm the issue is unassigned or assigned to you.
3. Assign or claim the issue before implementation.
4. Work on one implementation issue at a time.
5. Use one branch per issue.
6. Do not change files controlled by another active issue without coordination.
7. Keep changes within the issue scope.
8. Create follow-up issues for unrelated findings.
9. Link the pull request to the issue.
10. Provide a handoff note if work is incomplete.
11. Keep [ACTIVE_BOARD.md](docs/development/ACTIVE_BOARD.md) current with `make refresh-board` when claiming or opening a PR so parallel agents see the tree move.
12. Follow [PARALLEL_WORK.md](docs/development/PARALLEL_WORK.md) when more than one agent is active.

## Task Claiming System

The source of truth for task state is the GitHub issue and the [GitHub Project board](https://github.com/users/bluefate/projects/6) ([issues](https://github.com/bluefate/spacebio-evidence-engine/issues), [backlog index](docs/governance/BACKLOG.md)). To prevent multiple agents from modifying the same component, follow this claiming procedure:

1. Read AGENTS.md.
2. Read [ACTIVE_BOARD.md](docs/development/ACTIVE_BOARD.md). Prefer an unclaimed row from **Next options**; present that menu if asking the human what to do next. Run `make refresh-board` when asking “what’s next?” or when the snapshot looks stale.
3. Select an issue in `Ready`.
4. If the selected task is blocked because it requires human approval, automatically look for the next `Ready`, dependency-free, parallel-safe task. Only stop when no such task exists.
5. Check dependencies.
6. Check `Parallel Safe` in the issue.
7. Check active pull requests for overlapping files.
8. Assign the issue when possible (`gh issue edit <n> --add-assignee @me`). If assignment is impossible, still claim by comment — the board falls back to **CLAIMED BY**.
9. Post a claim comment using the template in [AGENT_WORKFLOW.md](docs/development/AGENT_WORKFLOW.md) (include **CLAIMED BY**).
10. Move the issue to `Claimed`.
11. Create a branch.
12. Post the branch name.
13. Move the issue to `In Progress` (working state).
14. Run `make refresh-board` and include `docs/development/ACTIVE_BOARD.md` in the working branch (in-flight nodes show `owner:` from assignee or CLAIMED BY).
15. Add yourself to the [Development team](README.md#development-team) on your first implementation PR if missing.
16. Implement only the defined scope.
17. Post progress comments for long tasks.
18. Run required validation.
19. Run `make refresh-board` again, open a pull request (include refreshed ACTIVE_BOARD.md).
20. Move the issue to `PR Open`.
21. Respond to review comments.
22. Do not approve or merge.
23. Wait for human approval and merge.
24. Issue moves to `Done` (next agent runs `make refresh-board` if the tree still shows the issue in flight).

Standard comment templates (claiming, progress, handoff, blocked) are in [AGENT_WORKFLOW.md](docs/development/AGENT_WORKFLOW.md).

## Branches

Use:

- `feature/<issue-number>-<description>`
- `fix/<issue-number>-<description>`
- `docs/<issue-number>-<description>`
- `test/<issue-number>-<description>`
- `chore/<issue-number>-<description>`

Never push directly to main.

### Branch isolation (required)

Agents must keep **all write activity** on their own issue branch:

1. Do not commit, push, or leave intentional edits on another agent’s or human’s branch.
2. Peer reviews must not overwrite others’ work — prefer `gh pr diff` / remote inspection; if a local checkout is required, use a throwaway review ref and do not commit on the author’s branch.
3. Before `checkout`, `stash -u`, `reset`, or `clean`, check `git status`. If uncommitted or untracked files look like someone else’s WIP, stop and ask; do not discard them.
4. One issue maps to one branch — do not mix unrelated issue commits onto the same branch.

See `.cursor/rules/agent-own-branch.mdc` and [BRANCHING_STRATEGY.md](docs/development/BRANCHING_STRATEGY.md).

## Pull Requests

Every pull request must:

1. Link its GitHub issue(s) (`Closes #N` / `Fixes #N`, plus any related issues).
2. Include an **Issue items** checklist copied from the issue (acceptance criteria, follow-up bullets, or task list) with each item marked done or deferred.
3. List related issues, blocked-by / blocking links, and dependency issues touched or assumed.
4. Explain the change.
5. Identify affected components.
6. List tests executed.
7. Include documentation changes.
8. Identify migrations.
9. Identify security or privacy effects.
10. State remaining risks.
11. Remain unmerged until a human approves it.
12. **List the contributing agent on the Development team** in [README.md](README.md#development-team) if this is that agent’s first implementation PR (or if the agent is missing from the table).

Agents opening a PR must fill the repository PR template completely. Do not omit the **Issue items**, **Related issues**, or **Development team** sections. Reviewers should be able to check work against the PR body without re-reading the full issue thread.

### Development team listing (required)

Any agent that implements repository work must appear in the [Development team](README.md#development-team) table in `README.md`.

- Add yourself on the **first** PR you open for this repo (same commit/PR as the work).
- Use a clear name and agent type (Cursor, Devin, Codex, ChatGPT, Other).
- Do not invent humans or agents who have not contributed.
- Do not remove other rows.
- Peer-review-only comments do not require a team row; opening or substantially updating an implementation PR does.

### Agent communication formats (required)

Use the fixed templates in [AGENT_WORKFLOW.md](docs/development/AGENT_WORKFLOW.md). Do not invent alternate headings.

| When | Required format | Where |
| --- | --- | --- |
| Claiming work | `### Claimed by agent` template | Issue comment |
| Multi-step / investigation update | `### Progress update` template | Issue comment |
| Opening or finishing a PR | `### Agent handoff` with `ready_for_review` (or Progress `STATUS: ready_for_review`) | Issue comment + full PR template body |
| Blocked | `### Blocked` template | Issue comment |

**Acceptable vs incomplete (example: #94 / PR #95):**

- Claim comment on #94: **acceptable** — matched the claim template (agent, branch, files, deps, overlap).
- Progress note on PR #97: **acceptable content**, **weak format** — useful finding, but used free-form `FINDING` / `CONCLUSION` instead of `COMPLETED` / `NEXT` / `BLOCKERS`.
- PR #95 body: **incomplete for review** — filled Summary/Changes/tests, but did **not** copy #94’s five follow-up bullets into an **Issue items** checklist. Humans had to re-read the issue to verify scope.

Agents may review and comment. Only humans may approve or merge.

## RAG Requirements

1. Answers must be based on retrieved corpus evidence.
2. Retrieved chunks must preserve publication ID, title, section, page, and source location.
3. Generated claims must link to supporting chunks.
4. The system must report insufficient evidence.
5. Retrieval and generation must be testable independently.
6. Do not hide retrieval failures with general model knowledge.
7. Record retrieval inputs, selected chunks, scores, and citations where permitted.
8. Separate source evidence, extracted structure, and generated interpretation.

## Scientific Integrity

1. Do not invent study findings.
2. Do not treat abstracts as complete studies.
3. Do not merge human, animal, plant, microbial, tissue, and cell evidence without labeling them.
4. Preserve experimental conditions and limitations.
5. Do not convert correlation into causation.
6. Display conflicting findings when detected.
7. Maintain links to the original publications.
8. Treat model-extracted metadata as unverified until validated.

## Code Quality

1. Use type annotations.
2. Keep functions focused.
3. Add tests for new behavior.
4. Do not disable tests to make a build pass.
5. Do not add dependencies without justification.
6. Use database migrations for schema changes.
7. Keep notebooks reproducible.
8. Move reusable notebook code into tested Python modules.

## Security

1. Never commit secrets.
2. Use environment variables.
3. Update .env.example when configuration changes.
4. Validate uploaded files.
5. Treat publication content as untrusted input.
6. Do not execute content extracted from documents.
7. Do not expose internal prompts, tokens, or connection strings.

## Commands

Full clean-machine checklist, ports, and env notes:
[docs/operations/LOCAL_SETUP.md](docs/operations/LOCAL_SETUP.md).

Setup:

```bash
make setup
make setup-check
```

Run API:

```bash
make api
```

Run web:

```bash
make web
```

Run services:

```bash
make services
```

Bootstrap pgvector extension (idempotent):

```bash
make db-bootstrap
```

Apply database migrations:

```bash
make migrate
```

Lint:

```bash
make lint
```

Type check:

```bash
make typecheck
```

Test:

```bash
make test
make test-web
```

Full validation:

```bash
make validate
```

Refresh the shared Mermaid task board from GitHub Project + open PRs:

```bash
make refresh-board
```

Update these commands when repository tooling changes.

## Completion

A task is complete only when:

1. Acceptance criteria pass.
2. Tests pass.
3. Lint and type checks pass.
4. Documentation is current.
5. No secrets are present.
6. The pull request links the issue.
7. The pull request includes a clear validation report.
8. A human review is requested.

## Stop Conditions

Stop and request human direction when:

1. Requirements conflict.
2. Scientific meaning is uncertain.
3. The task requires changing an approved architecture decision.
4. A migration could lose data.
5. Security controls would be weakened.
6. Another active task controls the same files.
7. Required credentials or source data are unavailable.

## Related documents

- [Active board (Mermaid + next options)](docs/development/ACTIVE_BOARD.md)
- [Agent workflow](docs/development/AGENT_WORKFLOW.md)
- [Definition of done](docs/development/DEFINITION_OF_DONE.md)
- [Local setup](docs/operations/LOCAL_SETUP.md)
- [Citation strategy](docs/rag/CITATION_STRATEGY.md)
- [GitHub Project board](https://github.com/users/bluefate/projects/6)
- [Backlog index](docs/governance/BACKLOG.md)

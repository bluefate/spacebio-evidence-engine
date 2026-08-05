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
7. docs/development/DEFINITION_OF_DONE.md
8. Documentation specific to the affected component

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

## Task Claiming System

The source of truth for task state is the GitHub issue and the [GitHub Project board](https://github.com/users/bluefate/projects/6) ([issues](https://github.com/bluefate/spacebio-evidence-engine/issues), [backlog index](docs/governance/BACKLOG.md)). To prevent multiple agents from modifying the same component, follow this claiming procedure:

1. Read AGENTS.md.
2. Select an issue in `Ready`.
3. If the selected task is blocked because it requires human approval, automatically look for the next `Ready`, dependency-free, parallel-safe task. Only stop when no such task exists.
4. Check dependencies.
5. Check `Parallel Safe` in the issue.
6. Check active pull requests for overlapping files.
7. Assign the issue to yourself when supported.
8. Post a claim comment using the template in [AGENT_WORKFLOW.md](docs/development/AGENT_WORKFLOW.md).
9. Move the issue to `Claimed`.
10. Create a branch.
11. Post the branch name.
12. Move the issue to `In Progress`.
13. Implement only the defined scope.
14. Post progress comments for long tasks.
15. Run required validation.
16. Open a pull request.
17. Move the issue to `PR Open`.
18. Respond to review comments.
19. Do not approve or merge.
20. Wait for human approval and merge.
21. Issue moves to `Done`.

Standard comment templates (claiming, progress, handoff, blocked) are in [AGENT_WORKFLOW.md](docs/development/AGENT_WORKFLOW.md).

## Branches

Use:

- `feature/<issue-number>-<description>`
- `fix/<issue-number>-<description>`
- `docs/<issue-number>-<description>`
- `test/<issue-number>-<description>`
- `chore/<issue-number>-<description>`

Never push directly to main.

## Pull Requests

Every pull request must:

1. Link its GitHub issue.
2. Explain the change.
3. Identify affected components.
4. List tests executed.
5. Include documentation changes.
6. Identify migrations.
7. Identify security or privacy effects.
8. State remaining risks.
9. Remain unmerged until a human approves it.

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

Setup:

```bash
make setup
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
```

Full validation:

```bash
make validate
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

- [Agent workflow](docs/development/AGENT_WORKFLOW.md)
- [Definition of done](docs/development/DEFINITION_OF_DONE.md)
- [Local setup](docs/operations/LOCAL_SETUP.md)
- [Citation strategy](docs/rag/CITATION_STRATEGY.md)
- [GitHub Project board](https://github.com/users/bluefate/projects/6)
- [Backlog index](docs/governance/BACKLOG.md)

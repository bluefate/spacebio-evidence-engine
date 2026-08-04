[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=24287746&assignment_repo_type=AssignmentRepo)

# Space Biology Evidence Engine

## Purpose
Define and build a citation-first evidence engine for a controlled corpus of open-access space biology publications.

## Scope
The MVP focuses on retrieval-augmented generation, passage-level citations, study comparison, evidence sufficiency, and a small corpus of approximately 20 to 30 publications in one topic area. The recommended initial topic is microgravity and skeletal muscle.

## Repositories

| Role | Repository |
|------|------------|
| **Principal / development** | [bluefate/spacebio-evidence-engine](https://github.com/bluefate/spacebio-evidence-engine) |
| **Course submission (GitHub Classroom)** | [FAU-AI-HootCamp-Summer-2026/buildphase-bluefate](https://github.com/FAU-AI-HootCamp-Summer-2026/buildphase-bluefate) |

Development and day-to-day engineering happen in the principal repository. The Classroom repository is the official submission remote for AI HootCamp Summer 2026 and should stay in sync for plan, design, and incremental build deliverables.

## Build Phase deliverables

| Document | Description |
|----------|-------------|
| [plan.md](plan.md) | Project plan: summary, requirements, RAG/production/security topics, weekly milestones |
| [design.md](design.md) | Technical design: architecture, data flow, user flow, schema, API, AI/RAG, deployment |

Supporting deep-dive documentation lives under [docs/](docs/README.md).

## Current status
Documentation-first project initialization. No implementation code has been generated yet. Build Phase plan and design documents are in place.

## Architecture position
The preferred stack is mostly accepted with review:

- Python 3.12+, FastAPI, PostgreSQL, pgvector, SQLAlchemy or SQLModel, Alembic, PyMuPDF, Jupyter, Sentence Transformers, Next.js, TypeScript, Docker Compose, Pytest, Ruff, mypy or pyright, GitHub Actions, and Mermaid are appropriate for the MVP.
- OpenAI models should be optional behind provider abstractions.
- Neo4j is deferred until the knowledge graph phase requires graph-native traversal or visualization.
- Advanced multi-agent orchestration and advanced contradiction detection are future capabilities, not MVP requirements.

## Start here
- [Build plan](plan.md)
- [Technical design](design.md)
- [Documentation index](docs/README.md)
- [Product requirements](docs/product/PRODUCT_REQUIREMENTS.md)
- [Architecture overview](docs/architecture/ARCHITECTURE.md)
- [RAG architecture](docs/architecture/RAG_ARCHITECTURE.md)
- [Development guide](docs/development/DEVELOPMENT_GUIDE.md)
- [Agent workflow](docs/development/AGENT_WORKFLOW.md)

## Related documents
- [Corpus specification](docs/data/CORPUS_SPECIFICATION.md)
- [Citation strategy](docs/rag/CITATION_STRATEGY.md)
- [Evaluation strategy](docs/rag/EVALUATION_STRATEGY.md)
- [Risk register](docs/governance/RISK_REGISTER.md)
- [Decision log](docs/governance/DECISION_LOG.md)

## Human decisions still required
- Approve the initial topic area and corpus selection rules.
- Choose SQLAlchemy versus SQLModel.
- Choose mypy versus pyright as the primary type checker.
- Choose the initial model providers and cost limits.
- Confirm Apache-2.0 as the final public license after legal review.

# Space Biology Evidence Engine

## Purpose
Define and build a citation-first evidence engine for a controlled corpus of open-access space biology publications.

## Scope
The MVP focuses on retrieval-augmented generation, passage-level citations, study comparison, evidence sufficiency, and a small corpus of approximately 20 to 30 publications in one topic area. The recommended initial topic is microgravity and skeletal muscle.

## Current status
Documentation-first project initialization. No implementation code has been generated yet.

## Architecture position
The preferred stack is mostly accepted with review:

- Python 3.12+, FastAPI, PostgreSQL, pgvector, SQLAlchemy or SQLModel, Alembic, PyMuPDF, Jupyter, Sentence Transformers, Next.js, TypeScript, Docker Compose, Pytest, Ruff, mypy or pyright, GitHub Actions, and Mermaid are appropriate for the MVP.
- OpenAI models should be optional behind provider abstractions.
- Neo4j is deferred until the knowledge graph phase requires graph-native traversal or visualization.
- Advanced multi-agent orchestration and advanced contradiction detection are future capabilities, not MVP requirements.

## Start here
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


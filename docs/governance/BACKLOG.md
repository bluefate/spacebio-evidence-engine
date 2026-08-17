# Backlog index

## Purpose
Human-readable index of GitHub issues with URLs. **Source of truth for status remains the GitHub Project and issues**—this file can lag; regenerate after large triage.

## Project

| Resource | URL |
|----------|-----|
| Project board | https://github.com/users/bluefate/projects/6 |
| All issues | https://github.com/bluefate/spacebio-evidence-engine/issues |
| Decision log | [DECISION_LOG.md](DECISION_LOG.md) |
| August plan | [plan.md](../../plan.md) |

## August MVP focus

Prioritize foundation → corpus (~10–15 papers) → ingestion → vector retrieval → grounded answers → minimal web UI.
Issues labeled `post-august-mvp` are deferred past 2026-08-31.

_Generated from repository issues (77 total). Last updated: 2026-08-17._

## Foundation

| # | State | Title | Labels |
|---|-------|-------|--------|
| [1](https://github.com/bluefate/spacebio-evidence-engine/issues/1) | CLOSED | Approve product requirements for MVP | |
| [2](https://github.com/bluefate/spacebio-evidence-engine/issues/2) | CLOSED | Approve MVP architecture baseline | |
| [3](https://github.com/bluefate/spacebio-evidence-engine/issues/3) | CLOSED | Initialize Git repository and remote linkage | |
| [4](https://github.com/bluefate/spacebio-evidence-engine/issues/4) | CLOSED | Add root AGENTS.md collaboration contract | |
| [5](https://github.com/bluefate/spacebio-evidence-engine/issues/5) | CLOSED | Add contributor and agent workflow documentation | |
| [6](https://github.com/bluefate/spacebio-evidence-engine/issues/6) | CLOSED | Document and script local development environment setup | `august-mvp` |
| [7](https://github.com/bluefate/spacebio-evidence-engine/issues/7) | CLOSED | Add Docker Compose for PostgreSQL with pgvector | |
| [8](https://github.com/bluefate/spacebio-evidence-engine/issues/8) | CLOSED | Configure PostgreSQL database bootstrap and pgvector extension | `august-mvp` |
| [9](https://github.com/bluefate/spacebio-evidence-engine/issues/9) | CLOSED | Create FastAPI application skeleton | `august-mvp` |
| [10](https://github.com/bluefate/spacebio-evidence-engine/issues/10) | CLOSED | Configure Pytest baseline and sample test layout | `august-mvp` |
| [11](https://github.com/bluefate/spacebio-evidence-engine/issues/11) | CLOSED | Configure Ruff linting and formatting | `august-mvp` |
| [12](https://github.com/bluefate/spacebio-evidence-engine/issues/12) | CLOSED | Configure Python type checking baseline | |
| [13](https://github.com/bluefate/spacebio-evidence-engine/issues/13) | CLOSED | Configure GitHub Actions CI for lint, typecheck, and tests | |
| [14](https://github.com/bluefate/spacebio-evidence-engine/issues/14) | CLOSED | Create GitHub Project board for multi-agent tracking | |
| [15](https://github.com/bluefate/spacebio-evidence-engine/issues/15) | CLOSED | Create GitHub issue and pull request templates | |

## Corpus Discovery

| # | State | Title | Labels |
|---|-------|-------|--------|
| [16](https://github.com/bluefate/spacebio-evidence-engine/issues/16) | CLOSED | Locate approved open-access publication sources | `august-mvp` |
| [17](https://github.com/bluefate/spacebio-evidence-engine/issues/17) | CLOSED | Define corpus inclusion criteria | |
| [18](https://github.com/bluefate/spacebio-evidence-engine/issues/18) | CLOSED | Define corpus exclusion criteria | |
| [19](https://github.com/bluefate/spacebio-evidence-engine/issues/19) | CLOSED | Select initial research topic for MVP corpus | |
| [20](https://github.com/bluefate/spacebio-evidence-engine/issues/20) | CLOSED | Select initial 10–15 publications for August MVP corpus | `august-mvp` |
| [21](https://github.com/bluefate/spacebio-evidence-engine/issues/21) | CLOSED | Create corpus inventory schema | `august-mvp` |
| [22](https://github.com/bluefate/spacebio-evidence-engine/issues/22) | CLOSED | Build corpus inventory notebook | `august-mvp` |
| [23](https://github.com/bluefate/spacebio-evidence-engine/issues/23) | CLOSED | Identify licensing and access restrictions for candidate publications | `august-mvp` |
| [24](https://github.com/bluefate/spacebio-evidence-engine/issues/24) | CLOSED | Detect duplicate publications in corpus candidates | `august-mvp` |
| [25](https://github.com/bluefate/spacebio-evidence-engine/issues/25) | CLOSED | Assess PDF quality for selected publications | `august-mvp` |
| [26](https://github.com/bluefate/spacebio-evidence-engine/issues/26) | CLOSED | Create ten reference research questions for evaluation | `august-mvp` |

## Document Ingestion

| # | State | Title | Labels |
|---|-------|-------|--------|
| [27](https://github.com/bluefate/spacebio-evidence-engine/issues/27) | CLOSED | Define publication metadata schema for persistence | `august-mvp` |
| [28](https://github.com/bluefate/spacebio-evidence-engine/issues/28) | CLOSED | Implement PDF storage abstraction | `august-mvp` |
| [29](https://github.com/bluefate/spacebio-evidence-engine/issues/29) | CLOSED | Implement PDF text extraction with PyMuPDF | `august-mvp` |
| [30](https://github.com/bluefate/spacebio-evidence-engine/issues/30) | CLOSED | Implement section detection for extracted publications | `august-mvp` |
| [31](https://github.com/bluefate/spacebio-evidence-engine/issues/31) | CLOSED | Implement page mapping for extracted text spans | `august-mvp` |
| [32](https://github.com/bluefate/spacebio-evidence-engine/issues/32) | CLOSED | Implement publication chunking strategy | `august-mvp` |
| [33](https://github.com/bluefate/spacebio-evidence-engine/issues/33) | CLOSED | Define and persist chunk metadata schema | `august-mvp` |
| [34](https://github.com/bluefate/spacebio-evidence-engine/issues/34) | CLOSED | Implement ingestion status tracking | `august-mvp` |
| [35](https://github.com/bluefate/spacebio-evidence-engine/issues/35) | OPEN | Implement publication reprocessing workflow | |
| [36](https://github.com/bluefate/spacebio-evidence-engine/issues/36) | CLOSED | Implement ingestion error reporting | `august-mvp` |
| [37](https://github.com/bluefate/spacebio-evidence-engine/issues/37) | CLOSED | Add unit tests for ingestion components | `august-mvp` |
| [38](https://github.com/bluefate/spacebio-evidence-engine/issues/38) | CLOSED | Add integration tests for end-to-end ingestion path | `august-mvp` |

## Retrieval

| # | State | Title | Labels |
|---|-------|-------|--------|
| [39](https://github.com/bluefate/spacebio-evidence-engine/issues/39) | CLOSED | Define embedding provider interface | `august-mvp` |
| [40](https://github.com/bluefate/spacebio-evidence-engine/issues/40) | CLOSED | Implement local embedding provider | `august-mvp` |
| [41](https://github.com/bluefate/spacebio-evidence-engine/issues/41) | CLOSED | Implement optional OpenAI embedding provider | |
| [42](https://github.com/bluefate/spacebio-evidence-engine/issues/42) | CLOSED | Define vector storage schema in PostgreSQL | `august-mvp` |
| [43](https://github.com/bluefate/spacebio-evidence-engine/issues/43) | CLOSED | Implement vector indexing for chunk embeddings | `august-mvp` |
| [44](https://github.com/bluefate/spacebio-evidence-engine/issues/44) | CLOSED | Implement semantic vector search | `august-mvp` |
| [45](https://github.com/bluefate/spacebio-evidence-engine/issues/45) | CLOSED | Implement PostgreSQL full-text search for chunks | `post-august-mvp` |
| [46](https://github.com/bluefate/spacebio-evidence-engine/issues/46) | OPEN | Implement hybrid retrieval combining vector and full-text search | `post-august-mvp` |
| [47](https://github.com/bluefate/spacebio-evidence-engine/issues/47) | CLOSED | Implement retrieval filtering by metadata | `august-mvp` |
| [48](https://github.com/bluefate/spacebio-evidence-engine/issues/48) | OPEN | Implement retrieval reranking stage | `post-august-mvp` |
| [49](https://github.com/bluefate/spacebio-evidence-engine/issues/49) | CLOSED | Implement retrieval logging for inputs, chunks, and scores | `august-mvp` |
| [50](https://github.com/bluefate/spacebio-evidence-engine/issues/50) | CLOSED | Build retrieval evaluation harness against reference questions | `august-mvp` |

## Grounded Answers

| # | State | Title | Labels |
|---|-------|-------|--------|
| [51](https://github.com/bluefate/spacebio-evidence-engine/issues/51) | CLOSED | Define language model provider interface | `august-mvp` |
| [52](https://github.com/bluefate/spacebio-evidence-engine/issues/52) | CLOSED | Implement context assembly from retrieved chunks | `august-mvp` |
| [53](https://github.com/bluefate/spacebio-evidence-engine/issues/53) | CLOSED | Implement grounded answer prompt template | `august-mvp` |
| [54](https://github.com/bluefate/spacebio-evidence-engine/issues/54) | CLOSED | Implement passage-level citation emission | `august-mvp` |
| [55](https://github.com/bluefate/spacebio-evidence-engine/issues/55) | CLOSED | Implement insufficient evidence response behavior | `august-mvp` |
| [56](https://github.com/bluefate/spacebio-evidence-engine/issues/56) | CLOSED | Implement claim-to-source mapping structure | `august-mvp` |
| [57](https://github.com/bluefate/spacebio-evidence-engine/issues/57) | CLOSED | Define grounded answer response schema | `august-mvp` |
| [58](https://github.com/bluefate/spacebio-evidence-engine/issues/58) | CLOSED | Add hallucination evaluation checks for grounded answers | |
| [59](https://github.com/bluefate/spacebio-evidence-engine/issues/59) | CLOSED | Add citation correctness evaluation | |
| [60](https://github.com/bluefate/spacebio-evidence-engine/issues/60) | CLOSED | Add grounded answer API endpoint | `august-mvp` |

## Web Interface

| # | State | Title | Labels |
|---|-------|-------|--------|
| [61](https://github.com/bluefate/spacebio-evidence-engine/issues/61) | CLOSED | Build search page for publications and passages | `august-mvp` |
| [62](https://github.com/bluefate/spacebio-evidence-engine/issues/62) | CLOSED | Build question answering page | `august-mvp` |
| [63](https://github.com/bluefate/spacebio-evidence-engine/issues/63) | CLOSED | Build evidence panel for cited passages | `august-mvp` |
| [64](https://github.com/bluefate/spacebio-evidence-engine/issues/64) | CLOSED | Build publication detail page | `august-mvp` |
| [65](https://github.com/bluefate/spacebio-evidence-engine/issues/65) | OPEN | Build study comparison page | `post-august-mvp` |
| [66](https://github.com/bluefate/spacebio-evidence-engine/issues/66) | CLOSED | Wire citation links from answers to evidence and publications | `august-mvp` |
| [67](https://github.com/bluefate/spacebio-evidence-engine/issues/67) | CLOSED | Add developer retrieval diagnostics view | `post-august-mvp` |
| [68](https://github.com/bluefate/spacebio-evidence-engine/issues/68) | CLOSED | Improve web accessibility for core flows | `post-august-mvp` |
| [69](https://github.com/bluefate/spacebio-evidence-engine/issues/69) | CLOSED | Add frontend tests for citation and answer rendering | `post-august-mvp` |

## Knowledge Graph

| # | State | Title | Labels |
|---|-------|-------|--------|
| [70](https://github.com/bluefate/spacebio-evidence-engine/issues/70) | CLOSED | Define knowledge graph use cases for space biology evidence | `post-august-mvp` |
| [71](https://github.com/bluefate/spacebio-evidence-engine/issues/71) | OPEN | Define candidate entity types for graph modeling | `post-august-mvp` |
| [72](https://github.com/bluefate/spacebio-evidence-engine/issues/72) | OPEN | Define candidate relationship types for graph modeling | `post-august-mvp` |
| [73](https://github.com/bluefate/spacebio-evidence-engine/issues/73) | OPEN | Compare Neo4j versus PostgreSQL graph modeling options | `post-august-mvp` |
| [74](https://github.com/bluefate/spacebio-evidence-engine/issues/74) | OPEN | Build entity-relationship extraction prototype from passages | `post-august-mvp` |
| [75](https://github.com/bluefate/spacebio-evidence-engine/issues/75) | OPEN | Evaluate graph extraction accuracy on sample corpus | `post-august-mvp` |
| [76](https://github.com/bluefate/spacebio-evidence-engine/issues/76) | OPEN | Design human validation workflow for extracted graph claims | `post-august-mvp` |
| [77](https://github.com/bluefate/spacebio-evidence-engine/issues/77) | OPEN | Decide whether to add a graph database post-MVP | `post-august-mvp` |


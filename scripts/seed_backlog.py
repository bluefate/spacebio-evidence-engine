#!/usr/bin/env python3
"""Create the initial Space Biology Evidence Engine issue backlog."""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field
from typing import Any


REPO = "bluefate/spacebio-evidence-engine"
PROJECT_OWNER = "bluefate"
PROJECT_NUMBER = 6


@dataclass
class Issue:
    title: str
    milestone: str
    roadmap_milestone: str
    work_type: str
    estimate: str
    parallel: str  # Yes | No | Conditional
    priority: str
    risk: str
    labels: list[str]
    description: str
    acceptance: list[str]
    dependencies: list[str]
    ownership: list[str]
    tests: list[str]
    docs: list[str]
    close_if_scaffolded: bool = False
    needs_human: bool = False
    status: str = "Backlog"


ISSUES: list[Issue] = []


def issue(**kwargs: Any) -> None:
    ISSUES.append(Issue(**kwargs))


# ---------------------------------------------------------------------------
# Milestone 1: Foundation
# ---------------------------------------------------------------------------
issue(
    title="Approve product requirements for MVP",
    milestone="Foundation",
    roadmap_milestone="Foundation",
    work_type="Documentation",
    estimate="S",
    parallel="Yes",
    priority="Critical",
    risk="High",
    labels=["needs-human", "work:documentation", "milestone:foundation", "estimate:s", "parallel-safe"],
    description="Human review and approval of MVP product requirements so implementation has a stable baseline.",
    acceptance=[
        "PRODUCT_REQUIREMENTS.md reviewed by the human owner",
        "MVP in-scope / out-of-scope confirmed in writing on this issue",
        "Open product decisions listed or resolved",
        "Issue closed only after explicit human approval comment",
    ],
    dependencies=["None"],
    ownership=["docs/product/PRODUCT_REQUIREMENTS.md", "docs/product/USER_STORIES.md"],
    tests=["No code tests; human sign-off recorded on the issue"],
    docs=["Update PRODUCT_REQUIREMENTS.md status to Approved if accepted"],
    needs_human=True,
    status="Ready",
)
issue(
    title="Approve MVP architecture baseline",
    milestone="Foundation",
    roadmap_milestone="Foundation",
    work_type="Architecture",
    estimate="S",
    parallel="Yes",
    priority="Critical",
    risk="High",
    labels=["needs-human", "work:architecture", "architecture", "milestone:foundation", "estimate:s", "parallel-safe"],
    description="Human approval of the MVP architecture (FastAPI, Next.js, PostgreSQL+pgvector, deferred Neo4j) and related ADRs.",
    acceptance=[
        "ARCHITECTURE.md and RAG_ARCHITECTURE.md reviewed",
        "ADR-001 through ADR-007 accepted, rejected, or deferred with notes in DECISION_LOG.md",
        "Explicit human approval comment on this issue",
    ],
    dependencies=["Approve product requirements for MVP"],
    ownership=["docs/architecture/", "docs/governance/DECISION_LOG.md"],
    tests=["No code tests; decision log updated"],
    docs=["DECISION_LOG.md statuses updated"],
    needs_human=True,
    status="Ready",
)
issue(
    title="Initialize Git repository and remote linkage",
    milestone="Foundation",
    roadmap_milestone="Foundation",
    work_type="Operations",
    estimate="XS",
    parallel="No",
    priority="High",
    risk="Low",
    labels=["work:operations", "milestone:foundation", "estimate:xs", "parallel-unsafe"],
    description="Ensure local git history, remotes, default branch main, and private GitHub repository are correctly initialized.",
    acceptance=[
        "Repository exists at bluefate/spacebio-evidence-engine",
        "Default branch is main",
        "Initial commit history is present and pushed",
        "README describes current scaffold status",
    ],
    dependencies=["None"],
    ownership=["README.md", ".git/", ".gitignore"],
    tests=["Verify remote and branch with gh/git commands"],
    docs=["README.md current status section"],
    close_if_scaffolded=True,
)
issue(
    title="Add root AGENTS.md collaboration contract",
    milestone="Foundation",
    roadmap_milestone="Foundation",
    work_type="Documentation",
    estimate="S",
    parallel="Conditional",
    priority="High",
    risk="Medium",
    labels=["documentation", "work:documentation", "milestone:foundation", "estimate:s"],
    description="Maintain the root AGENTS.md contract for human and AI contributors covering claiming, PRs, RAG, and stop conditions.",
    acceptance=[
        "AGENTS.md present at repository root",
        "Covers authority, task rules, RAG, scientific integrity, security, commands, completion, stop conditions",
        "Links to AGENT_WORKFLOW and DEFINITION_OF_DONE",
    ],
    dependencies=["Initialize Git repository and remote linkage"],
    ownership=["AGENTS.md", "docs/development/AGENT_WORKFLOW.md"],
    tests=["Manual review against AGENTS.md checklist"],
    docs=["AGENTS.md", "docs/development/AGENT_WORKFLOW.md"],
    close_if_scaffolded=True,
)
issue(
    title="Add contributor and agent workflow documentation",
    milestone="Foundation",
    roadmap_milestone="Foundation",
    work_type="Documentation",
    estimate="S",
    parallel="Yes",
    priority="High",
    risk="Low",
    labels=["documentation", "work:documentation", "milestone:foundation", "estimate:s", "parallel-safe"],
    description="Document how contributors and agents claim issues, branch, open PRs, and hand off work.",
    acceptance=[
        "CONTRIBUTING.md present and accurate",
        "AGENT_WORKFLOW.md includes claiming and handoff template",
        "BRANCHING_STRATEGY and PULL_REQUEST_PROCESS align with AGENTS.md",
    ],
    dependencies=["Add root AGENTS.md collaboration contract"],
    ownership=["CONTRIBUTING.md", "docs/development/"],
    tests=["Doc link check"],
    docs=["CONTRIBUTING.md", "docs/development/*"],
    close_if_scaffolded=True,
)
issue(
    title="Document and script local development environment setup",
    milestone="Foundation",
    roadmap_milestone="Foundation",
    work_type="Infrastructure",
    estimate="S",
    parallel="Yes",
    priority="High",
    risk="Low",
    labels=["work:infrastructure", "milestone:foundation", "estimate:s", "parallel-safe"],
    description="Provide reproducible local setup via Makefile and LOCAL_SETUP.md for Python, Node (when present), and Compose.",
    acceptance=[
        "make setup documented and works on a clean machine checklist",
        "LOCAL_SETUP.md lists tools, ports, and commands",
        ".env.example covers required variables without secrets",
    ],
    dependencies=["Initialize Git repository and remote linkage"],
    ownership=["Makefile", "docs/operations/LOCAL_SETUP.md", ".env.example"],
    tests=["Dry-run setup steps; no secret commit check"],
    docs=["docs/operations/LOCAL_SETUP.md", "AGENTS.md Commands section"],
)
issue(
    title="Add Docker Compose for PostgreSQL with pgvector",
    milestone="Foundation",
    roadmap_milestone="Foundation",
    work_type="Infrastructure",
    estimate="S",
    parallel="Conditional",
    priority="High",
    risk="Low",
    labels=["work:infrastructure", "milestone:foundation", "estimate:s"],
    description="Provide Compose service for PostgreSQL with pgvector only; no Neo4j or extra paid services.",
    acceptance=[
        "docker-compose.yml defines pgvector/pgvector PostgreSQL service",
        "Healthcheck and named volume present",
        "make services / docker compose up -d starts DB",
        "No application containers required in this issue",
    ],
    dependencies=["Document and script local development environment setup"],
    ownership=["docker-compose.yml", ".env.example"],
    tests=["Compose config validate; container becomes healthy"],
    docs=["docs/operations/LOCAL_SETUP.md", "docs/architecture/CONTAINER_ARCHITECTURE.md"],
    close_if_scaffolded=True,
)
issue(
    title="Configure PostgreSQL database bootstrap and pgvector extension",
    milestone="Foundation",
    roadmap_milestone="Foundation",
    work_type="Backend",
    estimate="S",
    parallel="No",
    priority="High",
    risk="Medium",
    labels=["work:backend", "work:data", "milestone:foundation", "estimate:s", "parallel-unsafe"],
    description="Ensure database initialization enables the vector extension and documents connection settings for the API.",
    acceptance=[
        "pgvector extension can be enabled on the Compose database",
        "Connection settings documented in .env.example",
        "Idempotent bootstrap script or migration stub documented",
        "No application schema beyond extension bootstrap in this issue",
    ],
    dependencies=["Add Docker Compose for PostgreSQL with pgvector"],
    ownership=["docker-compose.yml", "scripts/ or alembic bootstrap", ".env.example"],
    tests=["Integration smoke: connect and CREATE EXTENSION IF NOT EXISTS vector"],
    docs=["docs/architecture/DATA_ARCHITECTURE.md", "docs/operations/LOCAL_SETUP.md"],
)
issue(
    title="Create FastAPI application skeleton",
    milestone="Foundation",
    roadmap_milestone="Foundation",
    work_type="Backend",
    estimate="M",
    parallel="No",
    priority="High",
    risk="Medium",
    labels=["work:backend", "enhancement", "milestone:foundation", "estimate:m", "parallel-unsafe"],
    description="Scaffold a minimal FastAPI app with health endpoint, settings loading, and package layout—no RAG routes yet.",
    acceptance=[
        "FastAPI app package exists under approved layout",
        "GET /health returns OK",
        "Settings load from environment",
        "make api starts the app locally (update Makefile)",
        "No retrieval or ingestion logic in this PR",
    ],
    dependencies=["Configure PostgreSQL database bootstrap and pgvector extension", "Approve MVP architecture baseline"],
    ownership=["src/ or apps/api/", "Makefile", "pyproject.toml"],
    tests=["API test for /health", "settings unit test"],
    docs=["docs/operations/LOCAL_SETUP.md", "docs/development/DEVELOPMENT_GUIDE.md"],
)
issue(
    title="Configure Pytest baseline and sample test layout",
    milestone="Foundation",
    roadmap_milestone="Foundation",
    work_type="Testing",
    estimate="S",
    parallel="Yes",
    priority="High",
    risk="Low",
    labels=["work:testing", "milestone:foundation", "estimate:s", "parallel-safe"],
    description="Establish Pytest configuration, test layout, and a minimal smoke test for the Python package.",
    acceptance=[
        "pytest configured in pyproject.toml",
        "tests/ layout documented",
        "make test runs successfully",
        "CI-compatible local command documented",
    ],
    dependencies=["Create FastAPI application skeleton"],
    ownership=["tests/", "pyproject.toml", "Makefile"],
    tests=["Existing smoke tests pass; document how to add new tests"],
    docs=["docs/development/TESTING_STRATEGY.md"],
)
issue(
    title="Configure Ruff linting and formatting",
    milestone="Foundation",
    roadmap_milestone="Foundation",
    work_type="Infrastructure",
    estimate="S",
    parallel="Yes",
    priority="Medium",
    risk="Low",
    labels=["work:infrastructure", "milestone:foundation", "estimate:s", "parallel-safe"],
    description="Configure Ruff for lint and format; wire into Makefile and pre-commit.",
    acceptance=[
        "Ruff config in pyproject.toml",
        "make lint runs ruff check and format check",
        "pre-commit hooks include ruff",
        "No broad unrelated reformatting beyond configured paths",
    ],
    dependencies=["Initialize Git repository and remote linkage"],
    ownership=["pyproject.toml", ".pre-commit-config.yaml", "Makefile"],
    tests=["make lint passes on current tree"],
    docs=["docs/development/DEVELOPMENT_GUIDE.md"],
)
issue(
    title="Configure Python type checking baseline",
    milestone="Foundation",
    roadmap_milestone="Foundation",
    work_type="Infrastructure",
    estimate="S",
    parallel="Conditional",
    priority="Medium",
    risk="Low",
    labels=["needs-human", "work:infrastructure", "milestone:foundation", "estimate:s"],
    description="Choose and configure pyright or mypy as the primary type checker and wire make typecheck.",
    acceptance=[
        "Human chooses pyright or mypy",
        "make typecheck runs the chosen tool",
        "Baseline config committed",
        "CI job uses the same tool",
    ],
    dependencies=["Configure Ruff linting and formatting", "Create FastAPI application skeleton"],
    ownership=["pyproject.toml", "Makefile", ".github/workflows/ci.yml"],
    tests=["make typecheck passes on skeleton"],
    docs=["docs/development/DEVELOPMENT_GUIDE.md", "DECISION_LOG.md entry"],
    needs_human=True,
)
issue(
    title="Configure GitHub Actions CI for lint, typecheck, and tests",
    milestone="Foundation",
    roadmap_milestone="Foundation",
    work_type="Infrastructure",
    estimate="S",
    parallel="Conditional",
    priority="High",
    risk="Low",
    labels=["work:infrastructure", "milestone:foundation", "estimate:s"],
    description="Maintain CI workflow running lint, typecheck, and tests on pull requests to main.",
    acceptance=[
        ".github/workflows/ci.yml present",
        "Runs on pull_request and push to main",
        "Does not enable auto-merge",
        "Fails on lint/test failures",
    ],
    dependencies=["Configure Pytest baseline and sample test layout", "Configure Ruff linting and formatting"],
    ownership=[".github/workflows/ci.yml"],
    tests=["CI run on a sample PR or workflow_dispatch"],
    docs=["docs/development/TESTING_STRATEGY.md"],
    close_if_scaffolded=True,
)
issue(
    title="Create GitHub Project board for multi-agent tracking",
    milestone="Foundation",
    roadmap_milestone="Foundation",
    work_type="Operations",
    estimate="S",
    parallel="Yes",
    priority="Medium",
    risk="Low",
    labels=["work:operations", "milestone:foundation", "estimate:s", "parallel-safe"],
    description="Ensure the Space Biology Evidence Engine GitHub Project exists with status fields and is linked to the repo.",
    acceptance=[
        "Project exists and is linked to the repository",
        "Status and planning fields present",
        "Views/workflows documented for manual completion if API-limited",
        "Auto-merge not enabled",
    ],
    dependencies=["Initialize Git repository and remote linkage"],
    ownership=["docs/operations/ (optional project notes)", "GitHub Project"],
    tests=["Manual verification of project URL and fields"],
    docs=["Optional short note in LOCAL_SETUP or operations docs"],
    close_if_scaffolded=True,
)
issue(
    title="Create GitHub issue and pull request templates",
    milestone="Foundation",
    roadmap_milestone="Foundation",
    work_type="Documentation",
    estimate="S",
    parallel="Yes",
    priority="Medium",
    risk="Low",
    labels=["documentation", "work:documentation", "milestone:foundation", "estimate:s", "parallel-safe"],
    description="Provide issue forms and PR template capturing scope, provenance, security, and validation requirements.",
    acceptance=[
        "Issue templates for feature, bug, docs, research, architecture present",
        "PULL_REQUEST_TEMPLATE.md includes validation and human review checklist",
        "CODEOWNERS assigns human maintainer for sensitive paths",
    ],
    dependencies=["Initialize Git repository and remote linkage"],
    ownership=[".github/ISSUE_TEMPLATE/", ".github/PULL_REQUEST_TEMPLATE.md", ".github/CODEOWNERS"],
    tests=["Open template preview in GitHub UI"],
    docs=["CONTRIBUTING.md references templates"],
    close_if_scaffolded=True,
)

# ---------------------------------------------------------------------------
# Milestone 2: Corpus discovery
# ---------------------------------------------------------------------------
issue(
    title="Locate approved open-access publication sources",
    milestone="Corpus discovery",
    roadmap_milestone="Corpus Ingestion",
    work_type="Research",
    estimate="M",
    parallel="Yes",
    priority="High",
    risk="Medium",
    labels=["work:research", "work:data", "milestone:corpus-discovery", "estimate:m", "parallel-safe"],
    description="Identify and document approved sources for open-access space biology publications suitable for the MVP corpus.",
    acceptance=[
        "Source list documented with access method and license notes",
        "At least one primary source approved for MVP use",
        "Disallowed sources explicitly listed",
    ],
    dependencies=["Approve product requirements for MVP"],
    ownership=["docs/data/CORPUS_SPECIFICATION.md"],
    tests=["Manual review of source list"],
    docs=["docs/data/CORPUS_SPECIFICATION.md"],
)
issue(
    title="Define corpus inclusion criteria",
    milestone="Corpus discovery",
    roadmap_milestone="Corpus Ingestion",
    work_type="Data",
    estimate="S",
    parallel="Yes",
    priority="High",
    risk="Medium",
    labels=["work:data", "milestone:corpus-discovery", "estimate:s", "parallel-safe"],
    description="Write explicit inclusion criteria for publications entering the controlled corpus.",
    acceptance=[
        "Inclusion criteria documented and testable",
        "Examples of included publication types provided",
        "Human review requested",
    ],
    dependencies=["Locate approved open-access publication sources"],
    ownership=["docs/data/CORPUS_SPECIFICATION.md"],
    tests=["Apply criteria to 3 sample candidates"],
    docs=["docs/data/CORPUS_SPECIFICATION.md"],
)
issue(
    title="Define corpus exclusion criteria",
    milestone="Corpus discovery",
    roadmap_milestone="Corpus Ingestion",
    work_type="Data",
    estimate="S",
    parallel="Yes",
    priority="High",
    risk="Medium",
    labels=["work:data", "milestone:corpus-discovery", "estimate:s", "parallel-safe"],
    description="Write explicit exclusion criteria to keep the corpus legally and scientifically scoped.",
    acceptance=[
        "Exclusion criteria documented",
        "License, access, and quality exclusions covered",
        "Examples of excluded items provided",
    ],
    dependencies=["Locate approved open-access publication sources"],
    ownership=["docs/data/CORPUS_SPECIFICATION.md"],
    tests=["Apply criteria to 3 sample candidates"],
    docs=["docs/data/CORPUS_SPECIFICATION.md"],
)
issue(
    title="Select initial research topic for MVP corpus",
    milestone="Corpus discovery",
    roadmap_milestone="Corpus Ingestion",
    work_type="Research",
    estimate="S",
    parallel="No",
    priority="Critical",
    risk="High",
    labels=["needs-human", "work:research", "milestone:corpus-discovery", "estimate:s", "parallel-unsafe"],
    description="Choose the initial MVP topic area (recommended: microgravity and skeletal muscle) with human approval.",
    acceptance=[
        "Topic proposal with rationale posted",
        "Human owner approves topic on the issue",
        "CORPUS_SPECIFICATION.md updated with selected topic",
    ],
    dependencies=["Define corpus inclusion criteria", "Define corpus exclusion criteria"],
    ownership=["docs/data/CORPUS_SPECIFICATION.md", "docs/product/"],
    tests=["None beyond documented rationale"],
    docs=["docs/data/CORPUS_SPECIFICATION.md"],
    needs_human=True,
)
issue(
    title="Select initial 20–30 publications for MVP corpus",
    milestone="Corpus discovery",
    roadmap_milestone="Corpus Ingestion",
    work_type="Data",
    estimate="L",
    parallel="No",
    priority="Critical",
    risk="High",
    labels=["needs-human", "work:data", "work:research", "milestone:corpus-discovery", "estimate:l", "parallel-unsafe"],
    description="Select approximately 20–30 open-access publications matching the approved topic and criteria.",
    acceptance=[
        "Inventory of 20–30 candidates with IDs and licenses",
        "Each item passes inclusion and exclusion checks",
        "Human approval of the final list",
    ],
    dependencies=["Select initial research topic for MVP corpus", "Identify licensing and access restrictions"],
    ownership=["docs/data/", "data/inventory/ (future)"],
    tests=["Checklist validation against inclusion/exclusion criteria"],
    docs=["Corpus inventory artifact + CORPUS_SPECIFICATION.md"],
    needs_human=True,
)
issue(
    title="Create corpus inventory schema",
    milestone="Corpus discovery",
    roadmap_milestone="Corpus Ingestion",
    work_type="Data",
    estimate="S",
    parallel="Yes",
    priority="High",
    risk="Medium",
    labels=["work:data", "milestone:corpus-discovery", "estimate:s", "parallel-safe"],
    description="Define a machine-readable schema for corpus inventory records (identifiers, license, topic tags, paths).",
    acceptance=[
        "Schema documented in METADATA_SCHEMA or DATA_DICTIONARY",
        "Example inventory record provided",
        "Required vs optional fields specified",
    ],
    dependencies=["Define corpus inclusion criteria"],
    ownership=["docs/data/METADATA_SCHEMA.md", "docs/data/DATA_DICTIONARY.md"],
    tests=["Validate example record against schema (script or checklist)"],
    docs=["docs/data/METADATA_SCHEMA.md"],
)
issue(
    title="Build corpus inventory notebook",
    milestone="Corpus discovery",
    roadmap_milestone="Corpus Ingestion",
    work_type="Data",
    estimate="M",
    parallel="Conditional",
    priority="Medium",
    risk="Low",
    labels=["work:data", "milestone:corpus-discovery", "estimate:m"],
    description="Create a reproducible notebook to assemble and review the corpus inventory from the schema.",
    acceptance=[
        "Notebook runs end-to-end on sample data",
        "Writes/reads inventory in the approved schema",
        "Reusable helpers extracted or clearly marked for later module promotion",
    ],
    dependencies=["Create corpus inventory schema"],
    ownership=["notebooks/", "docs/data/"],
    tests=["Notebook smoke execution on fixture inventory"],
    docs=["notebook README or LOCAL_SETUP notebook section"],
)
issue(
    title="Identify licensing and access restrictions for candidate publications",
    milestone="Corpus discovery",
    roadmap_milestone="Corpus Ingestion",
    work_type="Security",
    estimate="M",
    parallel="Yes",
    priority="Critical",
    risk="High",
    labels=["work:security", "work:data", "milestone:corpus-discovery", "estimate:m", "parallel-safe"],
    description="Capture license and access constraints for each candidate publication before download or redistribution.",
    acceptance=[
        "License field populated for candidates",
        "Access restrictions and redistribution notes recorded",
        "Blocked items flagged and excluded",
    ],
    dependencies=["Locate approved open-access publication sources", "Create corpus inventory schema"],
    ownership=["docs/data/CORPUS_SPECIFICATION.md", "inventory records"],
    tests=["Audit sample of licenses against source pages"],
    docs=["License section in corpus docs"],
)
issue(
    title="Detect duplicate publications in corpus candidates",
    milestone="Corpus discovery",
    roadmap_milestone="Corpus Ingestion",
    work_type="Data",
    estimate="S",
    parallel="Yes",
    priority="Medium",
    risk="Low",
    labels=["work:data", "milestone:corpus-discovery", "estimate:s", "parallel-safe"],
    description="Define and apply duplicate detection rules (DOI, title normalization, version variants).",
    acceptance=[
        "Duplicate detection rules documented",
        "Duplicates flagged in inventory",
        "Canonical record chosen per duplicate set",
    ],
    dependencies=["Create corpus inventory schema", "Select initial 20–30 publications for MVP corpus"],
    ownership=["docs/data/", "notebooks/ or scripts/"],
    tests=["Unit tests for normalization/duplicate keys on fixtures"],
    docs=["CORPUS_SPECIFICATION.md duplicate policy"],
)
issue(
    title="Assess PDF quality for selected publications",
    milestone="Corpus discovery",
    roadmap_milestone="Corpus Ingestion",
    work_type="Data",
    estimate="M",
    parallel="Yes",
    priority="Medium",
    risk="Medium",
    labels=["work:data", "milestone:corpus-discovery", "estimate:m", "parallel-safe"],
    description="Assess extractability and quality of PDFs (text layer, scans, damage) before ingestion commitment.",
    acceptance=[
        "Quality rubric documented",
        "Each selected PDF scored or categorized",
        "Unusable PDFs excluded or flagged for OCR later (out of scope unless approved)",
    ],
    dependencies=["Select initial 20–30 publications for MVP corpus"],
    ownership=["docs/data/DOCUMENT_PROCESSING.md", "inventory fields"],
    tests=["Rubric applied to fixtures including one poor-quality example"],
    docs=["DOCUMENT_PROCESSING.md quality section"],
)
issue(
    title="Create ten reference research questions for evaluation",
    milestone="Corpus discovery",
    roadmap_milestone="Evaluation",
    work_type="Evaluation",
    estimate="M",
    parallel="Yes",
    priority="High",
    risk="Medium",
    labels=["work:evaluation", "work:research", "milestone:corpus-discovery", "estimate:m", "parallel-safe"],
    description="Author ten reference questions grounded in the selected topic for retrieval and answer evaluation.",
    acceptance=[
        "Ten questions documented with expected evidence characteristics",
        "Questions cover comparison, sufficiency, and factual lookup styles",
        "Human review of scientific appropriateness",
    ],
    dependencies=["Select initial research topic for MVP corpus"],
    ownership=["docs/rag/EVALUATION_STRATEGY.md", "evals/fixtures/ (future)"],
    tests=["Checklist that each question is answerable only via corpus evidence in principle"],
    docs=["docs/rag/EVALUATION_STRATEGY.md"],
    needs_human=True,
)

# ---------------------------------------------------------------------------
# Milestone 3: Document ingestion
# ---------------------------------------------------------------------------
issue(
    title="Define publication metadata schema for persistence",
    milestone="Document ingestion",
    roadmap_milestone="Corpus Ingestion",
    work_type="Data",
    estimate="M",
    parallel="No",
    priority="High",
    risk="Medium",
    labels=["work:data", "work:backend", "milestone:document-ingestion", "estimate:m", "parallel-unsafe"],
    description="Define SQL/metadata schema for publications (identifiers, license, paths, ingest state) without chunk tables.",
    acceptance=[
        "Schema documented in DATA_DICTIONARY/METADATA_SCHEMA",
        "Alembic migration creates publication table(s) only",
        "ORM models match schema",
    ],
    dependencies=["Create corpus inventory schema", "Create FastAPI application skeleton"],
    ownership=["docs/data/", "alembic/", "src/**/models"],
    tests=["Migration upgrade/downgrade test"],
    docs=["docs/data/DATA_DICTIONARY.md", "docs/data/METADATA_SCHEMA.md"],
)
issue(
    title="Implement PDF storage abstraction",
    milestone="Document ingestion",
    roadmap_milestone="Corpus Ingestion",
    work_type="Backend",
    estimate="M",
    parallel="Yes",
    priority="High",
    risk="Medium",
    labels=["work:backend", "work:infrastructure", "milestone:document-ingestion", "estimate:m", "parallel-safe"],
    description="Create a storage interface for PDF bytes/paths (local filesystem first) with no cloud vendor lock-in required for MVP.",
    acceptance=[
        "Storage protocol/interface defined",
        "Local filesystem implementation works",
        "Configuration via environment variables",
        "No cloud SDK required for default path",
    ],
    dependencies=["Create FastAPI application skeleton"],
    ownership=["src/**/storage/", ".env.example"],
    tests=["Unit tests with temp directory fixtures"],
    docs=["docs/data/DOCUMENT_PROCESSING.md", "LOCAL_SETUP.md"],
)
issue(
    title="Implement PDF text extraction with PyMuPDF",
    milestone="Document ingestion",
    roadmap_milestone="Corpus Ingestion",
    work_type="Data",
    estimate="M",
    parallel="Conditional",
    priority="High",
    risk="Medium",
    labels=["work:data", "work:backend", "milestone:document-ingestion", "estimate:m"],
    description="Extract text from PDFs using PyMuPDF into structured page-level outputs; treat PDF content as untrusted.",
    acceptance=[
        "Extractor returns page-ordered text",
        "Failures raise typed errors",
        "No code execution from PDF content",
        "Fixture PDF covered by tests",
    ],
    dependencies=["Implement PDF storage abstraction"],
    ownership=["src/**/ingestion/extract*", "tests/"],
    tests=["Unit tests on fixture PDFs"],
    docs=["docs/data/DOCUMENT_PROCESSING.md"],
)
issue(
    title="Implement section detection for extracted publications",
    milestone="Document ingestion",
    roadmap_milestone="Corpus Ingestion",
    work_type="Data",
    estimate="M",
    parallel="Conditional",
    priority="Medium",
    risk="Medium",
    labels=["work:data", "work:rag", "milestone:document-ingestion", "estimate:m"],
    description="Detect common sections (abstract, methods, results, etc.) from extracted text without inventing missing sections.",
    acceptance=[
        "Section detector outputs labeled spans with offsets/pages when possible",
        "Unknown sections handled safely",
        "Does not treat abstract as full study in downstream metadata",
    ],
    dependencies=["Implement PDF text extraction with PyMuPDF"],
    ownership=["src/**/ingestion/sections*", "tests/"],
    tests=["Unit tests with synthetic section fixtures"],
    docs=["docs/data/DOCUMENT_PROCESSING.md", "docs/rag/CHUNKING_STRATEGY.md"],
)
issue(
    title="Implement page mapping for extracted text spans",
    milestone="Document ingestion",
    roadmap_milestone="Corpus Ingestion",
    work_type="Data",
    estimate="S",
    parallel="Conditional",
    priority="High",
    risk="Medium",
    labels=["work:data", "milestone:document-ingestion", "estimate:s"],
    description="Preserve page number mapping for text spans used later in citations.",
    acceptance=[
        "Every extracted span can report page number when available",
        "Mapping persisted in chunk/intermediate metadata contract",
        "Missing page numbers explicitly represented",
    ],
    dependencies=["Implement PDF text extraction with PyMuPDF"],
    ownership=["src/**/ingestion/", "docs/data/METADATA_SCHEMA.md"],
    tests=["Unit tests verifying page assignments"],
    docs=["docs/rag/CITATION_STRATEGY.md", "METADATA_SCHEMA.md"],
)
issue(
    title="Implement publication chunking strategy",
    milestone="Document ingestion",
    roadmap_milestone="Corpus Ingestion",
    work_type="RAG",
    estimate="M",
    parallel="No",
    priority="High",
    risk="High",
    labels=["work:rag", "work:data", "milestone:document-ingestion", "estimate:m", "parallel-unsafe"],
    description="Chunk publications per CHUNKING_STRATEGY while preserving provenance fields.",
    acceptance=[
        "Chunker produces stable chunk IDs",
        "Publication ID, section, page, and offsets preserved",
        "Chunk size policy documented and implemented",
        "No embedding or DB vector writes in this issue",
    ],
    dependencies=["Implement section detection for extracted publications", "Implement page mapping for extracted text spans"],
    ownership=["src/**/ingestion/chunk*", "docs/rag/CHUNKING_STRATEGY.md"],
    tests=["Unit tests for chunk boundaries and provenance fields"],
    docs=["docs/rag/CHUNKING_STRATEGY.md"],
)
issue(
    title="Define and persist chunk metadata schema",
    milestone="Document ingestion",
    roadmap_milestone="Corpus Ingestion",
    work_type="Data",
    estimate="M",
    parallel="No",
    priority="High",
    risk="Medium",
    labels=["work:data", "work:backend", "milestone:document-ingestion", "estimate:m", "parallel-unsafe"],
    description="Create DB schema for chunks and metadata required for retrieval and citations.",
    acceptance=[
        "Chunk table migration added",
        "Fields include publication_id, section, page, offsets, text, hash",
        "Foreign key to publications enforced",
    ],
    dependencies=["Define publication metadata schema for persistence", "Implement publication chunking strategy"],
    ownership=["alembic/", "src/**/models", "docs/data/"],
    tests=["Migration tests; model round-trip test"],
    docs=["DATA_DICTIONARY.md", "METADATA_SCHEMA.md"],
)
issue(
    title="Implement ingestion status tracking",
    milestone="Document ingestion",
    roadmap_milestone="Corpus Ingestion",
    work_type="Backend",
    estimate="S",
    parallel="Conditional",
    priority="Medium",
    risk="Low",
    labels=["work:backend", "milestone:document-ingestion", "estimate:s"],
    description="Track per-publication ingestion states (pending, processing, succeeded, failed).",
    acceptance=[
        "Status enum persisted",
        "Transitions are explicit and logged",
        "API or CLI can show status for a publication ID",
    ],
    dependencies=["Define publication metadata schema for persistence"],
    ownership=["src/**/ingestion/", "alembic/"],
    tests=["Unit tests for valid/invalid transitions"],
    docs=["DOCUMENT_PROCESSING.md status section"],
)
issue(
    title="Implement publication reprocessing workflow",
    milestone="Document ingestion",
    roadmap_milestone="Corpus Ingestion",
    work_type="Backend",
    estimate="M",
    parallel="No",
    priority="Medium",
    risk="Medium",
    labels=["work:backend", "milestone:document-ingestion", "estimate:m", "parallel-unsafe"],
    description="Allow safe reprocessing of a publication with deterministic replacement of derived chunks.",
    acceptance=[
        "Reprocess command/job regenerates chunks",
        "Old chunks removed or versioned per approved strategy",
        "Status and timestamps updated",
        "No silent data loss without documented behavior",
    ],
    dependencies=["Implement ingestion status tracking", "Define and persist chunk metadata schema"],
    ownership=["src/**/ingestion/", "tests/"],
    tests=["Integration test reprocess replaces chunks"],
    docs=["DOCUMENT_PROCESSING.md reprocessing section"],
)
issue(
    title="Implement ingestion error reporting",
    milestone="Document ingestion",
    roadmap_milestone="Corpus Ingestion",
    work_type="Backend",
    estimate="S",
    parallel="Yes",
    priority="Medium",
    risk="Low",
    labels=["work:backend", "milestone:document-ingestion", "estimate:s", "parallel-safe"],
    description="Capture structured ingestion errors (extract failures, empty text, validation) for operator visibility.",
    acceptance=[
        "Errors stored with publication ID, stage, message, timestamp",
        "No secrets in error payloads",
        "Failed status linked to last error",
    ],
    dependencies=["Implement ingestion status tracking"],
    ownership=["src/**/ingestion/", "docs/operations/"],
    tests=["Unit tests for error record creation"],
    docs=["DOCUMENT_PROCESSING.md", "OBSERVABILITY.md"],
)
issue(
    title="Add unit tests for ingestion components",
    milestone="Document ingestion",
    roadmap_milestone="Corpus Ingestion",
    work_type="Testing",
    estimate="M",
    parallel="Yes",
    priority="High",
    risk="Low",
    labels=["work:testing", "milestone:document-ingestion", "estimate:m", "parallel-safe"],
    description="Expand unit tests covering extraction, sectioning, page mapping, and chunking edge cases.",
    acceptance=[
        "Tests cover success and failure paths",
        "Fixtures include multi-page sample",
        "make test includes these tests",
    ],
    dependencies=["Implement publication chunking strategy", "Implement PDF text extraction with PyMuPDF"],
    ownership=["tests/ingestion/"],
    tests=["The unit tests themselves"],
    docs=["TESTING_STRATEGY.md ingestion section"],
)
issue(
    title="Add integration tests for end-to-end ingestion path",
    milestone="Document ingestion",
    roadmap_milestone="Corpus Ingestion",
    work_type="Testing",
    estimate="M",
    parallel="Conditional",
    priority="High",
    risk="Medium",
    labels=["work:testing", "milestone:document-ingestion", "estimate:m"],
    description="Integration test: store PDF → extract → chunk → persist → status succeeded against Compose Postgres.",
    acceptance=[
        "Integration test runs with test DB",
        "Asserts chunk provenance fields persisted",
        "Documented how to run locally",
    ],
    dependencies=["Define and persist chunk metadata schema", "Implement ingestion status tracking"],
    ownership=["tests/integration/", "docker-compose.yml"],
    tests=["Integration test suite"],
    docs=["LOCAL_SETUP.md", "TESTING_STRATEGY.md"],
)

# ---------------------------------------------------------------------------
# Milestone 4: Retrieval
# ---------------------------------------------------------------------------
issue(
    title="Define embedding provider interface",
    milestone="Retrieval",
    roadmap_milestone="Semantic Search",
    work_type="RAG",
    estimate="S",
    parallel="Yes",
    priority="High",
    risk="Medium",
    labels=["work:rag", "work:architecture", "milestone:retrieval", "estimate:s", "parallel-safe"],
    description="Create an embedding provider protocol/ABC so local and OpenAI providers are swappable.",
    acceptance=[
        "Interface supports embed_documents and embed_query",
        "Dimension and model name exposed",
        "No provider-specific imports in interface module",
    ],
    dependencies=["Create FastAPI application skeleton"],
    ownership=["src/**/embeddings/", "docs/architecture/RAG_ARCHITECTURE.md"],
    tests=["Typing/protocol unit test with fake provider"],
    docs=["RAG_ARCHITECTURE.md", "DECISION_LOG if needed"],
)
issue(
    title="Implement local embedding provider",
    milestone="Retrieval",
    roadmap_milestone="Semantic Search",
    work_type="RAG",
    estimate="M",
    parallel="Conditional",
    priority="High",
    risk="Medium",
    labels=["work:rag", "milestone:retrieval", "estimate:m"],
    description="Implement Sentence Transformers (or approved local model) behind the embedding interface.",
    acceptance=[
        "Local provider implements the interface",
        "Model name configurable",
        "Deterministic test with tiny fixture or mocked model weights strategy documented",
    ],
    dependencies=["Define embedding provider interface"],
    ownership=["src/**/embeddings/local*", "pyproject.toml", ".env.example"],
    tests=["Unit test with stub/mock; optional smoke test marked heavy"],
    docs=["LOCAL_SETUP.md model download notes"],
)
issue(
    title="Implement optional OpenAI embedding provider",
    milestone="Retrieval",
    roadmap_milestone="Semantic Search",
    work_type="RAG",
    estimate="S",
    parallel="Yes",
    priority="Medium",
    risk="Medium",
    labels=["work:rag", "work:security", "milestone:retrieval", "estimate:s", "parallel-safe"],
    description="Optional OpenAI embeddings provider enabled only when configured; secrets via env only.",
    acceptance=[
        "Provider inactive unless API key present",
        "No secrets logged",
        "Interface-compatible",
        "Skipped in CI without credentials",
    ],
    dependencies=["Define embedding provider interface"],
    ownership=["src/**/embeddings/openai*", ".env.example"],
    tests=["Unit tests with mocked HTTP client"],
    docs=["SECURITY.md note", "LOCAL_SETUP.md"],
)
issue(
    title="Define vector storage schema in PostgreSQL",
    milestone="Retrieval",
    roadmap_milestone="Semantic Search",
    work_type="Data",
    estimate="M",
    parallel="No",
    priority="High",
    risk="Medium",
    labels=["work:data", "work:backend", "milestone:retrieval", "estimate:m", "parallel-unsafe"],
    description="Add pgvector columns/tables for chunk embeddings without implementing search APIs yet.",
    acceptance=[
        "Migration adds vector column/table linked to chunks",
        "Dimension documented and enforced",
        "Extension dependency documented",
    ],
    dependencies=["Configure PostgreSQL database bootstrap and pgvector extension", "Define and persist chunk metadata schema"],
    ownership=["alembic/", "docs/architecture/DATA_ARCHITECTURE.md"],
    tests=["Migration test"],
    docs=["DATA_ARCHITECTURE.md", "DATA_DICTIONARY.md"],
)
issue(
    title="Implement vector indexing for chunk embeddings",
    milestone="Retrieval",
    roadmap_milestone="Semantic Search",
    work_type="Backend",
    estimate="M",
    parallel="No",
    priority="High",
    risk="Medium",
    labels=["work:backend", "work:rag", "milestone:retrieval", "estimate:m", "parallel-unsafe"],
    description="Create embedding index job that writes vectors for chunks using the configured provider.",
    acceptance=[
        "Job embeds pending chunks and stores vectors",
        "Idempotent re-index behavior defined",
        "Progress/status visible",
    ],
    dependencies=["Define vector storage schema in PostgreSQL", "Implement local embedding provider"],
    ownership=["src/**/indexing/", "tests/"],
    tests=["Integration test with fake embedder"],
    docs=["docs/rag/RETRIEVAL_STRATEGY.md"],
)
issue(
    title="Implement semantic vector search",
    milestone="Retrieval",
    roadmap_milestone="Semantic Search",
    work_type="RAG",
    estimate="M",
    parallel="Conditional",
    priority="High",
    risk="Medium",
    labels=["work:rag", "work:backend", "milestone:retrieval", "estimate:m"],
    description="Query pgvector for top-k similar chunks for a question embedding.",
    acceptance=[
        "Search returns chunk IDs, scores, and provenance fields",
        "k and filters parameters supported at function level",
        "No LLM generation in this issue",
    ],
    dependencies=["Implement vector indexing for chunk embeddings"],
    ownership=["src/**/retrieval/semantic*", "tests/"],
    tests=["Integration test with known fixture vectors"],
    docs=["RETRIEVAL_STRATEGY.md"],
)
issue(
    title="Implement PostgreSQL full-text search for chunks",
    milestone="Retrieval",
    roadmap_milestone="Semantic Search",
    work_type="Backend",
    estimate="M",
    parallel="Yes",
    priority="Medium",
    risk="Low",
    labels=["work:backend", "milestone:retrieval", "estimate:m", "parallel-safe"],
    description="Add Postgres full-text search over chunk text independent of vectors.",
    acceptance=[
        "tsvector index or equivalent created",
        "Keyword search returns ranked chunk hits with provenance",
        "Works without embeddings",
    ],
    dependencies=["Define and persist chunk metadata schema"],
    ownership=["alembic/", "src/**/retrieval/fts*", "tests/"],
    tests=["Integration tests for keyword queries"],
    docs=["RETRIEVAL_STRATEGY.md"],
)
issue(
    title="Implement hybrid retrieval combining vector and full-text search",
    milestone="Retrieval",
    roadmap_milestone="Semantic Search",
    work_type="RAG",
    estimate="M",
    parallel="No",
    priority="High",
    risk="Medium",
    labels=["work:rag", "milestone:retrieval", "estimate:m", "parallel-unsafe"],
    description="Combine semantic and FTS channels with a documented fusion strategy.",
    acceptance=[
        "Hybrid retriever merges candidates with documented scoring",
        "Either channel can be disabled by config for ablation",
        "Returns provenance-complete chunk objects",
    ],
    dependencies=["Implement semantic vector search", "Implement PostgreSQL full-text search for chunks"],
    ownership=["src/**/retrieval/hybrid*", "docs/rag/RETRIEVAL_STRATEGY.md"],
    tests=["Unit tests for fusion; integration smoke test"],
    docs=["RETRIEVAL_STRATEGY.md"],
)
issue(
    title="Implement retrieval filtering by metadata",
    milestone="Retrieval",
    roadmap_milestone="Semantic Search",
    work_type="RAG",
    estimate="S",
    parallel="Yes",
    priority="Medium",
    risk="Low",
    labels=["work:rag", "work:backend", "milestone:retrieval", "estimate:s", "parallel-safe"],
    description="Filter retrieval by publication, section, organism/system labels, or other approved metadata.",
    acceptance=[
        "Filter API documented",
        "Filters apply to hybrid retrieval",
        "Invalid filters fail clearly",
    ],
    dependencies=["Implement hybrid retrieval combining vector and full-text search"],
    ownership=["src/**/retrieval/", "tests/"],
    tests=["Unit/integration filter tests"],
    docs=["RETRIEVAL_STRATEGY.md", "METADATA_SCHEMA.md"],
)
issue(
    title="Implement retrieval reranking stage",
    milestone="Retrieval",
    roadmap_milestone="Semantic Search",
    work_type="RAG",
    estimate="M",
    parallel="Conditional",
    priority="Medium",
    risk="Medium",
    labels=["work:rag", "milestone:retrieval", "estimate:m"],
    description="Optional reranking of retrieved chunks with a documented algorithm/provider abstraction.",
    acceptance=[
        "Rerank interface defined",
        "At least one local/simple reranker implemented",
        "Can be disabled via config",
    ],
    dependencies=["Implement hybrid retrieval combining vector and full-text search"],
    ownership=["src/**/retrieval/rerank*", "docs/rag/RETRIEVAL_STRATEGY.md"],
    tests=["Unit tests for ordering changes"],
    docs=["RETRIEVAL_STRATEGY.md"],
)
issue(
    title="Implement retrieval logging for inputs, chunks, and scores",
    milestone="Retrieval",
    roadmap_milestone="Semantic Search",
    work_type="Backend",
    estimate="S",
    parallel="Yes",
    priority="Medium",
    risk="Medium",
    labels=["work:backend", "work:rag", "milestone:retrieval", "estimate:s", "parallel-safe"],
    description="Log retrieval queries, selected chunk IDs, and scores where permitted; never log secrets.",
    acceptance=[
        "Structured retrieval log records created",
        "PII/secrets policy documented",
        "Toggle to disable verbose logs in production-like configs",
    ],
    dependencies=["Implement hybrid retrieval combining vector and full-text search"],
    ownership=["src/**/retrieval/", "docs/architecture/OBSERVABILITY.md"],
    tests=["Unit test asserts log payload shape"],
    docs=["OBSERVABILITY.md", "SECURITY_ARCHITECTURE.md"],
)
issue(
    title="Build retrieval evaluation harness against reference questions",
    milestone="Retrieval",
    roadmap_milestone="Evaluation",
    work_type="Evaluation",
    estimate="M",
    parallel="Yes",
    priority="High",
    risk="Medium",
    labels=["work:evaluation", "work:rag", "milestone:retrieval", "estimate:m", "parallel-safe"],
    description="Evaluate retrieval quality using the ten reference questions and record metrics.",
    acceptance=[
        "Harness runs offline against indexed corpus fixture",
        "Reports hit-rate / rank metrics as defined in EVALUATION_STRATEGY",
        "Results artifact path documented",
    ],
    dependencies=["Create ten reference research questions for evaluation", "Implement hybrid retrieval combining vector and full-text search"],
    ownership=["evals/", "docs/rag/EVALUATION_STRATEGY.md"],
    tests=["Harness smoke test on tiny fixture"],
    docs=["EVALUATION_STRATEGY.md"],
)

# ---------------------------------------------------------------------------
# Milestone 5: Grounded answers
# ---------------------------------------------------------------------------
issue(
    title="Define language model provider interface",
    milestone="Grounded answers",
    roadmap_milestone="Grounded Answers",
    work_type="RAG",
    estimate="S",
    parallel="Yes",
    priority="High",
    risk="Medium",
    labels=["work:rag", "work:architecture", "milestone:grounded-answers", "estimate:s", "parallel-safe"],
    description="Create an LLM provider interface for grounded generation without binding to a single vendor.",
    acceptance=[
        "Interface for generate/chat with structured output option",
        "Token/usage metadata optional fields defined",
        "No provider SDK imports in interface module",
    ],
    dependencies=["Create FastAPI application skeleton"],
    ownership=["src/**/llm/", "docs/architecture/RAG_ARCHITECTURE.md"],
    tests=["Fake provider unit test"],
    docs=["RAG_ARCHITECTURE.md", "PROMPTING_STRATEGY.md"],
)
issue(
    title="Implement context assembly from retrieved chunks",
    milestone="Grounded answers",
    roadmap_milestone="Grounded Answers",
    work_type="RAG",
    estimate="M",
    parallel="Conditional",
    priority="High",
    risk="High",
    labels=["work:rag", "milestone:grounded-answers", "estimate:m"],
    description="Assemble model context from retrieved chunks while preserving citation identifiers and separating evidence from instructions.",
    acceptance=[
        "Assembler includes chunk IDs and provenance in context",
        "Token/length budget enforced",
        "Does not silently drop citation IDs",
    ],
    dependencies=["Implement hybrid retrieval combining vector and full-text search"],
    ownership=["src/**/rag/context*", "tests/"],
    tests=["Unit tests for budget and ID preservation"],
    docs=["PROMPTING_STRATEGY.md", "CITATION_STRATEGY.md"],
)
issue(
    title="Implement grounded answer prompt template",
    milestone="Grounded answers",
    roadmap_milestone="Grounded Answers",
    work_type="RAG",
    estimate="M",
    parallel="Conditional",
    priority="High",
    risk="High",
    labels=["work:rag", "milestone:grounded-answers", "estimate:m"],
    description="Versioned prompt that requires citations, forbids unsupported claims, and handles insufficient evidence.",
    acceptance=[
        "Prompt versioned and stored in repo",
        "Instructs use-only-retrieved-evidence behavior",
        "Includes insufficient-evidence instruction",
        "No medical/mission recommendation language",
    ],
    dependencies=["Implement context assembly from retrieved chunks", "Define language model provider interface"],
    ownership=["prompts/", "src/**/rag/prompt*", "docs/rag/PROMPTING_STRATEGY.md"],
    tests=["Snapshot/unit test for rendered prompt structure"],
    docs=["PROMPTING_STRATEGY.md"],
)
issue(
    title="Implement passage-level citation emission",
    milestone="Grounded answers",
    roadmap_milestone="Grounded Answers",
    work_type="RAG",
    estimate="M",
    parallel="No",
    priority="Critical",
    risk="High",
    labels=["work:rag", "milestone:grounded-answers", "estimate:m", "parallel-unsafe"],
    description="Ensure answers emit passage-level citations tied to retrieved chunk IDs only.",
    acceptance=[
        "Citations reference retrieved chunk IDs exclusively",
        "Unknown citation IDs rejected/stripped with failure signaling",
        "Publication ID, section, page available for each citation",
    ],
    dependencies=["Implement grounded answer prompt template"],
    ownership=["src/**/rag/citations*", "docs/rag/CITATION_STRATEGY.md"],
    tests=["Unit tests for validation of citation IDs"],
    docs=["CITATION_STRATEGY.md"],
)
issue(
    title="Implement insufficient evidence response behavior",
    milestone="Grounded answers",
    roadmap_milestone="Grounded Answers",
    work_type="RAG",
    estimate="S",
    parallel="Yes",
    priority="High",
    risk="High",
    labels=["work:rag", "milestone:grounded-answers", "estimate:s", "parallel-safe"],
    description="When retrieval is empty/weak, return an insufficient-evidence response instead of model knowledge.",
    acceptance=[
        "Threshold/policy documented",
        "Response schema distinguishes insufficient evidence",
        "Does not fill gaps with general model knowledge",
    ],
    dependencies=["Implement passage-level citation emission"],
    ownership=["src/**/rag/", "docs/rag/"],
    tests=["Unit tests for empty and weak retrieval cases"],
    docs=["PROMPTING_STRATEGY.md", "CITATION_STRATEGY.md"],
)
issue(
    title="Implement claim-to-source mapping structure",
    milestone="Grounded answers",
    roadmap_milestone="Grounded Answers",
    work_type="RAG",
    estimate="M",
    parallel="Conditional",
    priority="High",
    risk="High",
    labels=["work:rag", "milestone:grounded-answers", "estimate:m"],
    description="Map individual answer claims to supporting chunk IDs for UI and evaluation.",
    acceptance=[
        "Answer payload includes claim list with citation IDs",
        "Claims without sources are rejected or flagged",
        "Compatible with answer schema issue",
    ],
    dependencies=["Implement passage-level citation emission"],
    ownership=["src/**/rag/", "docs/rag/CITATION_STRATEGY.md"],
    tests=["Unit tests for mapping validation"],
    docs=["CITATION_STRATEGY.md"],
)
issue(
    title="Define grounded answer response schema",
    milestone="Grounded answers",
    roadmap_milestone="Grounded Answers",
    work_type="Backend",
    estimate="S",
    parallel="Yes",
    priority="High",
    risk="Medium",
    labels=["work:backend", "work:rag", "milestone:grounded-answers", "estimate:s", "parallel-safe"],
    description="Define Pydantic/JSON schema for answers, citations, sufficiency, and warnings.",
    acceptance=[
        "Schema committed and versioned",
        "OpenAPI reflects schema",
        "Includes fields for limitations and conflicts when present",
    ],
    dependencies=["Implement claim-to-source mapping structure", "Implement insufficient evidence response behavior"],
    ownership=["src/**/schemas/", "docs/architecture/"],
    tests=["Schema validation unit tests"],
    docs=["API docs / RAG_ARCHITECTURE.md"],
)
issue(
    title="Add hallucination evaluation checks for grounded answers",
    milestone="Grounded answers",
    roadmap_milestone="Evaluation",
    work_type="Evaluation",
    estimate="M",
    parallel="Yes",
    priority="High",
    risk="High",
    labels=["work:evaluation", "milestone:grounded-answers", "estimate:m", "parallel-safe"],
    description="Evaluate whether answers introduce claims not supported by retrieved evidence.",
    acceptance=[
        "Eval script/metric defined",
        "Runs on fixture answers",
        "Failures are actionable in CI or offline report",
    ],
    dependencies=["Define grounded answer response schema", "Create ten reference research questions for evaluation"],
    ownership=["evals/", "docs/rag/EVALUATION_STRATEGY.md"],
    tests=["Eval harness tests on synthetic hallucinated fixture"],
    docs=["EVALUATION_STRATEGY.md"],
)
issue(
    title="Add citation correctness evaluation",
    milestone="Grounded answers",
    roadmap_milestone="Evaluation",
    work_type="Evaluation",
    estimate="M",
    parallel="Yes",
    priority="High",
    risk="High",
    labels=["work:evaluation", "milestone:grounded-answers", "estimate:m", "parallel-safe"],
    description="Evaluate that cited chunk IDs exist in retrieved context and support the linked claims.",
    acceptance=[
        "Checker validates citation IDs ⊆ retrieved IDs",
        "Reports precision/recall style citation metrics as defined",
        "Integrated with eval harness entrypoint",
    ],
    dependencies=["Implement passage-level citation emission", "Add hallucination evaluation checks for grounded answers"],
    ownership=["evals/", "docs/rag/CITATION_STRATEGY.md"],
    tests=["Unit tests for citation checker"],
    docs=["EVALUATION_STRATEGY.md", "CITATION_STRATEGY.md"],
)
issue(
    title="Add grounded answer API endpoint",
    milestone="Grounded answers",
    roadmap_milestone="Grounded Answers",
    work_type="Backend",
    estimate="M",
    parallel="No",
    priority="High",
    risk="High",
    labels=["work:backend", "work:rag", "milestone:grounded-answers", "estimate:m", "parallel-unsafe"],
    description="Expose POST endpoint that retrieves, generates grounded answer, and returns schema-compliant payload.",
    acceptance=[
        "Endpoint documented in OpenAPI",
        "Uses retrieval + grounded pipeline only",
        "Returns insufficient-evidence path correctly",
        "No uncited scientific claims in happy-path fixture test",
    ],
    dependencies=["Define grounded answer response schema", "Implement hybrid retrieval combining vector and full-text search", "Define language model provider interface"],
    ownership=["src/**/api/", "tests/api/"],
    tests=["API integration tests with fake LLM/embedder"],
    docs=["LOCAL_SETUP.md", "RAG_ARCHITECTURE.md"],
)

# ---------------------------------------------------------------------------
# Milestone 6: Web interface
# ---------------------------------------------------------------------------
issue(
    title="Build search page for publications and passages",
    milestone="Web interface",
    roadmap_milestone="Web Interface",
    work_type="Frontend",
    estimate="M",
    parallel="Conditional",
    priority="High",
    risk="Medium",
    labels=["work:frontend", "milestone:web-interface", "estimate:m"],
    description="Next.js search page for querying publications/passages via API; no answer generation on this page.",
    acceptance=[
        "Search UI calls search/retrieval API",
        "Results show provenance fields",
        "Loading and empty states handled",
    ],
    dependencies=["Implement hybrid retrieval combining vector and full-text search", "Create FastAPI application skeleton"],
    ownership=["apps/web/ or frontend package", "package.json"],
    tests=["Frontend component/unit test for results rendering"],
    docs=["LOCAL_SETUP.md web section"],
)
issue(
    title="Build question answering page",
    milestone="Web interface",
    roadmap_milestone="Web Interface",
    work_type="Frontend",
    estimate="M",
    parallel="No",
    priority="High",
    risk="High",
    labels=["work:frontend", "work:rag", "milestone:web-interface", "estimate:m", "parallel-unsafe"],
    description="UI to submit a research question and render grounded answers with citations.",
    acceptance=[
        "Submits to grounded answer API",
        "Renders claims and citations",
        "Shows insufficient-evidence state",
    ],
    dependencies=["Add grounded answer API endpoint"],
    ownership=["apps/web/", "tests or playwright later"],
    tests=["Component test for answer + insufficient states"],
    docs=["User-facing help blurb if required"],
)
issue(
    title="Build evidence panel for cited passages",
    milestone="Web interface",
    roadmap_milestone="Web Interface",
    work_type="Frontend",
    estimate="M",
    parallel="Conditional",
    priority="High",
    risk="High",
    labels=["work:frontend", "work:rag", "milestone:web-interface", "estimate:m"],
    description="Panel showing cited passage text and provenance for the active answer.",
    acceptance=[
        "Displays passage text, publication ID/title, section, page",
        "Highlights active citation",
        "Handles missing passage gracefully",
    ],
    dependencies=["Build question answering page"],
    ownership=["apps/web/components/evidence*"],
    tests=["Component tests"],
    docs=["CITATION_STRATEGY.md UI notes"],
)
issue(
    title="Build publication detail page",
    milestone="Web interface",
    roadmap_milestone="Web Interface",
    work_type="Frontend",
    estimate="M",
    parallel="Yes",
    priority="Medium",
    risk="Low",
    labels=["work:frontend", "milestone:web-interface", "estimate:m", "parallel-safe"],
    description="Page showing publication metadata and link to original source.",
    acceptance=[
        "Shows metadata and license",
        "External link to original publication",
        "Lists available sections/chunks summary without exposing secrets",
    ],
    dependencies=["Define publication metadata schema for persistence"],
    ownership=["apps/web/app/publications/"],
    tests=["Component/page test with mock data"],
    docs=["Short UX note in docs if needed"],
)
issue(
    title="Build study comparison page",
    milestone="Web interface",
    roadmap_milestone="Web Interface",
    work_type="Frontend",
    estimate="L",
    parallel="No",
    priority="Medium",
    risk="Medium",
    labels=["work:frontend", "work:rag", "milestone:web-interface", "estimate:l", "parallel-unsafe"],
    description="UI to compare evidence across studies with organism/system labels preserved.",
    acceptance=[
        "User can select multiple publications or evidence sets",
        "Comparison view labels organism/system categories",
        "Does not invent differences not present in evidence",
    ],
    dependencies=["Build evidence panel for cited passages", "Add grounded answer API endpoint"],
    ownership=["apps/web/app/compare/"],
    tests=["Component tests for labeling"],
    docs=["USER_STORIES.md reference"],
)
issue(
    title="Wire citation links from answers to evidence and publications",
    milestone="Web interface",
    roadmap_milestone="Web Interface",
    work_type="Frontend",
    estimate="S",
    parallel="Conditional",
    priority="High",
    risk="Medium",
    labels=["work:frontend", "milestone:web-interface", "estimate:s"],
    description="Make citation markers navigate to evidence panel entries and publication pages.",
    acceptance=[
        "Citation click focuses evidence passage",
        "Link to publication detail available",
        "Broken links handled",
    ],
    dependencies=["Build evidence panel for cited passages", "Build publication detail page"],
    ownership=["apps/web/"],
    tests=["Interaction test for citation click"],
    docs=["CITATION_STRATEGY.md"],
)
issue(
    title="Add developer retrieval diagnostics view",
    milestone="Web interface",
    roadmap_milestone="Web Interface",
    work_type="Frontend",
    estimate="M",
    parallel="Yes",
    priority="Low",
    risk="Medium",
    labels=["work:frontend", "work:rag", "milestone:web-interface", "estimate:m", "parallel-safe"],
    description="Developer-only diagnostics showing retrieval inputs, chunk scores, and selected citations.",
    acceptance=[
        "Gated behind development/config flag",
        "Shows chunk IDs and scores",
        "Does not expose secrets or internal tokens",
    ],
    dependencies=["Implement retrieval logging for inputs, chunks, and scores", "Build question answering page"],
    ownership=["apps/web/app/dev/", "docs/architecture/OBSERVABILITY.md"],
    tests=["Ensures flag hides view by default"],
    docs=["OBSERVABILITY.md"],
)
issue(
    title="Improve web accessibility for core flows",
    milestone="Web interface",
    roadmap_milestone="Web Interface",
    work_type="Frontend",
    estimate="M",
    parallel="Yes",
    priority="Medium",
    risk="Low",
    labels=["work:frontend", "milestone:web-interface", "estimate:m", "parallel-safe"],
    description="Ensure search, question, and evidence flows meet basic a11y requirements (labels, keyboard, contrast).",
    acceptance=[
        "Core pages keyboard navigable",
        "Interactive elements labeled",
        "Accessibility checks documented (axe or equivalent)",
    ],
    dependencies=["Build search page for publications and passages", "Build question answering page"],
    ownership=["apps/web/"],
    tests=["a11y test script on core pages"],
    docs=["Frontend testing notes"],
)
issue(
    title="Add frontend tests for citation and answer rendering",
    milestone="Web interface",
    roadmap_milestone="Web Interface",
    work_type="Testing",
    estimate="M",
    parallel="Yes",
    priority="High",
    risk="Low",
    labels=["work:testing", "work:frontend", "milestone:web-interface", "estimate:m", "parallel-safe"],
    description="Establish frontend test tooling and cover citation rendering and insufficient-evidence UI.",
    acceptance=[
        "Test runner configured",
        "Tests for answer citations and empty/insufficient states",
        "make target or npm script documented",
    ],
    dependencies=["Build question answering page", "Build evidence panel for cited passages"],
    ownership=["apps/web/", "package.json", "docs/development/TESTING_STRATEGY.md"],
    tests=["Frontend unit/component tests"],
    docs=["TESTING_STRATEGY.md"],
)

# ---------------------------------------------------------------------------
# Milestone 7: Knowledge graph research
# ---------------------------------------------------------------------------
issue(
    title="Define knowledge graph use cases for space biology evidence",
    milestone="Knowledge graph research",
    roadmap_milestone="Knowledge Graph",
    work_type="Research",
    estimate="M",
    parallel="Yes",
    priority="Medium",
    risk="Low",
    labels=["work:research", "work:architecture", "milestone:knowledge-graph", "estimate:m", "parallel-safe"],
    description="Document concrete graph use cases that are not well served by RAG alone; keep MVP non-blocking.",
    acceptance=[
        "Use cases listed with user value",
        "Explicit non-goals for MVP",
        "Human review requested",
    ],
    dependencies=["Approve MVP architecture baseline"],
    ownership=["docs/architecture/", "docs/governance/"],
    tests=["N/A research review"],
    docs=["New research note or architecture appendix"],
)
issue(
    title="Define candidate entity types for graph modeling",
    milestone="Knowledge graph research",
    roadmap_milestone="Knowledge Graph",
    work_type="Research",
    estimate="S",
    parallel="Yes",
    priority="Medium",
    risk="Low",
    labels=["work:research", "work:data", "milestone:knowledge-graph", "estimate:s", "parallel-safe"],
    description="Propose entity types (organism, system, intervention, outcome, etc.) with provenance requirements.",
    acceptance=[
        "Entity type list with definitions",
        "Provenance fields required per entity",
        "Examples mapped from sample publications",
    ],
    dependencies=["Define knowledge graph use cases for space biology evidence"],
    ownership=["docs/data/", "docs/architecture/"],
    tests=["N/A"],
    docs=["Data/architecture research note"],
)
issue(
    title="Define candidate relationship types for graph modeling",
    milestone="Knowledge graph research",
    roadmap_milestone="Knowledge Graph",
    work_type="Research",
    estimate="S",
    parallel="Yes",
    priority="Medium",
    risk="Low",
    labels=["work:research", "work:data", "milestone:knowledge-graph", "estimate:s", "parallel-safe"],
    description="Propose relationship types linking entities, including evidence qualifiers and citation links.",
    acceptance=[
        "Relationship types documented",
        "Each relationship requires source passage linkage",
        "Conflict/qualification representation considered",
    ],
    dependencies=["Define candidate entity types for graph modeling"],
    ownership=["docs/data/", "docs/architecture/"],
    tests=["N/A"],
    docs=["Research note"],
)
issue(
    title="Compare Neo4j versus PostgreSQL graph modeling options",
    milestone="Knowledge graph research",
    roadmap_milestone="Knowledge Graph",
    work_type="Architecture",
    estimate="M",
    parallel="Yes",
    priority="Medium",
    risk="Medium",
    labels=["needs-human", "work:architecture", "architecture", "milestone:knowledge-graph", "estimate:m", "parallel-safe"],
    description="Compare Neo4j vs PostgreSQL-based graph modeling for the defined use cases; do not add Neo4j as MVP dependency.",
    acceptance=[
        "Comparison covers cost, ops, query patterns, and provenance",
        "Recommendation drafted",
        "Human decision recorded in DECISION_LOG",
    ],
    dependencies=["Define candidate relationship types for graph modeling"],
    ownership=["docs/governance/DECISION_LOG.md", "docs/architecture/"],
    tests=["N/A"],
    docs=["DECISION_LOG.md ADR draft"],
    needs_human=True,
)
issue(
    title="Build entity-relationship extraction prototype from passages",
    milestone="Knowledge graph research",
    roadmap_milestone="Knowledge Graph",
    work_type="Research",
    estimate="L",
    parallel="Conditional",
    priority="Low",
    risk="Medium",
    labels=["work:research", "work:rag", "milestone:knowledge-graph", "estimate:l"],
    description="Prototype extraction of entities/relations from retrieved passages with mandatory citation links; experimental only.",
    acceptance=[
        "Prototype runs on fixture passages",
        "Outputs include source chunk IDs",
        "Clearly marked non-production",
    ],
    dependencies=["Define candidate relationship types for graph modeling", "Implement passage-level citation emission"],
    ownership=["notebooks/ or experiments/", "docs/"],
    tests=["Fixture-based prototype assertions"],
    docs=["Prototype README"],
)
issue(
    title="Evaluate graph extraction accuracy on sample corpus",
    milestone="Knowledge graph research",
    roadmap_milestone="Knowledge Graph",
    work_type="Evaluation",
    estimate="M",
    parallel="Yes",
    priority="Low",
    risk="Medium",
    labels=["work:evaluation", "milestone:knowledge-graph", "estimate:m", "parallel-safe"],
    description="Measure extraction precision/recall on a small human-labeled sample.",
    acceptance=[
        "Labeled sample defined",
        "Metrics reported",
        "Error categories summarized",
    ],
    dependencies=["Build entity-relationship extraction prototype from passages"],
    ownership=["evals/", "docs/rag/EVALUATION_STRATEGY.md"],
    tests=["Eval script smoke test"],
    docs=["Evaluation write-up"],
)
issue(
    title="Design human validation workflow for extracted graph claims",
    milestone="Knowledge graph research",
    roadmap_milestone="Knowledge Graph",
    work_type="Research",
    estimate="M",
    parallel="Yes",
    priority="Low",
    risk="Low",
    labels=["work:research", "work:documentation", "milestone:knowledge-graph", "estimate:m", "parallel-safe"],
    description="Design a human validation workflow before any extracted graph facts are trusted in product answers.",
    acceptance=[
        "Workflow steps documented",
        "Roles and acceptance states defined",
        "Unverified extractions cannot silently enter answers",
    ],
    dependencies=["Evaluate graph extraction accuracy on sample corpus"],
    ownership=["docs/governance/", "docs/development/"],
    tests=["N/A process review"],
    docs=["Validation workflow doc"],
)
issue(
    title="Decide whether to add a graph database post-MVP",
    milestone="Knowledge graph research",
    roadmap_milestone="Knowledge Graph",
    work_type="Architecture",
    estimate="S",
    parallel="No",
    priority="Medium",
    risk="High",
    labels=["needs-human", "work:architecture", "architecture", "milestone:knowledge-graph", "estimate:s", "parallel-unsafe"],
    description="Human go/no-go decision on introducing a graph database after reviewing research outcomes.",
    acceptance=[
        "Decision recorded in DECISION_LOG",
        "If no: Neo4j remains deferred with rationale",
        "If yes: follow-up implementation issues filed (not in MVP critical path unless human overrides)",
    ],
    dependencies=["Compare Neo4j versus PostgreSQL graph modeling options", "Design human validation workflow for extracted graph claims"],
    ownership=["docs/governance/DECISION_LOG.md"],
    tests=["N/A"],
    docs=["DECISION_LOG.md"],
    needs_human=True,
)


def run(cmd: list[str], *, input_text: str | None = None) -> str:
    result = subprocess.run(
        cmd,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}\n{result.stdout}")
    return result.stdout.strip()


def milestone_map() -> dict[str, int]:
    raw = run(["gh", "api", f"repos/{REPO}/milestones?state=open", "--jq", ".[] | [.title, .number] | @tsv"])
    out: dict[str, int] = {}
    for line in raw.splitlines():
        title, number = line.split("\t")
        out[title] = int(number)
    return out


def body_for(issue: Issue) -> str:
    acc = "\n".join(f"- [ ] {a}" for a in issue.acceptance)
    deps = "\n".join(f"- {d}" for d in issue.dependencies)
    own = "\n".join(f"- `{p}`" for p in issue.ownership)
    tests = "\n".join(f"- {t}" for t in issue.tests)
    docs = "\n".join(f"- {d}" for d in issue.docs)
    return f"""## Description
{issue.description}

## Acceptance criteria
{acc}

## Dependencies
{deps}

## Suggested labels
{', '.join(f'`{l}`' for l in issue.labels)}

## Estimate
`{issue.estimate}`

## Parallel-safety classification
`{issue.parallel}`

## Likely file ownership
{own}

## Required tests
{tests}

## Required documentation
{docs}

## Project fields
- Status: `{issue.status}`
- Priority: `{issue.priority}`
- Work Type: `{issue.work_type}`
- Roadmap Milestone: `{issue.roadmap_milestone}`
- Parallel Safe: `{issue.parallel}`
- Risk: `{issue.risk}`
- Estimate: `{issue.estimate}`
- Owner Type: `{"Human" if issue.needs_human else "Unassigned"}`
"""


def create_issue(issue: Issue, milestones: dict[str, int]) -> int:
    args = [
        "gh",
        "issue",
        "create",
        "--repo",
        REPO,
        "--title",
        issue.title,
        "--body",
        body_for(issue),
        "--milestone",
        issue.milestone,
        "--project",
        "Space Biology Evidence Engine",
    ]
    for label in issue.labels:
        args.extend(["--label", label])
    url = run(args)
    number = int(url.rstrip("/").split("/")[-1])
    if issue.close_if_scaffolded:
        run(
            [
                "gh",
                "issue",
                "close",
                str(number),
                "--repo",
                REPO,
                "--comment",
                "Closing as completed during repository scaffolding. Reopen if gaps remain.",
            ]
        )
    return number


def main() -> None:
    milestones = milestone_map()
    missing = sorted({i.milestone for i in ISSUES} - set(milestones))
    if missing:
        raise SystemExit(f"Missing milestones: {missing}")

    created: list[dict[str, Any]] = []
    for idx, issue in enumerate(ISSUES, start=1):
        number = create_issue(issue, milestones)
        created.append(
            {
                "number": number,
                "title": issue.title,
                "milestone": issue.milestone,
                "roadmap_milestone": issue.roadmap_milestone,
                "work_type": issue.work_type,
                "estimate": issue.estimate,
                "parallel": issue.parallel,
                "priority": issue.priority,
                "risk": issue.risk,
                "status": "Done" if issue.close_if_scaffolded else issue.status,
                "owner_type": "Human" if issue.needs_human else "Unassigned",
                "closed": issue.close_if_scaffolded,
            }
        )
        print(f"[{idx}/{len(ISSUES)}] #{number} {issue.title}")
        time.sleep(0.4)

    out_path = "/tmp/spacebio_backlog_seed.json"
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump({"repo": REPO, "project": PROJECT_NUMBER, "issues": created}, fh, indent=2)
    print(f"Wrote {out_path} with {len(created)} issues")


if __name__ == "__main__":
    main()

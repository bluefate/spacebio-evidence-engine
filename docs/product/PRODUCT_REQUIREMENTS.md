# Product Requirements

## Purpose
Define what the Space Biology Evidence Engine must accomplish before implementation.

## Scope
August MVP requirements for a controlled-corpus, RAG-based evidence engine with passage-level citations. Deadline: **2026-08-31**.

## Current status
Approved project definition with locked decisions (see [decision log](../governance/DECISION_LOG.md)).

## Problem
Public space biology publications are difficult to search, compare, and synthesize for focused scientific questions. The product must help users explore the evidence while preserving citation traceability and uncertainty.

## Product vision
Build a trustworthy evidence workspace for space biology literature, beginning with approximately **10 to 15** open-access publications on **microgravity and skeletal muscle**.

## August MVP functional requirements
- Ingest controlled open-access publications.
- Search publications using natural language (vector semantic search).
- Answer scientific questions using RAG.
- Ground answers only in retrieved passages.
- Display passage-level citations.
- Provide insufficient-evidence responses.
- Support a minimal citation-first web UI.

## Deferred past August MVP
- Compare selected studies (UI).
- Rich organism/system/exposure inspection beyond free-text metadata.
- Candidate conflict detection.
- Corpus-limited research gap identification.
- Knowledge graph relationships / Neo4j.

## Nonfunctional requirements
- Citation-first trustworthiness.
- Repeatable ingestion and evaluation.
- Local-first development (Compose).
- Modular service boundaries.
- Clear separation between August MVP and future architecture.
- Open-source tools where practical; Apache-2.0 license.
- LLM spend hard-capped at $50/month; local mode at $0 cloud.

## Success metrics
See [plan.md](../../plan.md) §2.1.2 and [decision log](../governance/DECISION_LOG.md).

## Target user priority
Researchers first; students/educators second.

## Related documents
- [User stories](USER_STORIES.md)
- [RAG architecture](../architecture/RAG_ARCHITECTURE.md)
- [Citation strategy](../rag/CITATION_STRATEGY.md)
- [Traceability matrix](../governance/TRACEABILITY_MATRIX.md)
- [Decision log](../governance/DECISION_LOG.md)

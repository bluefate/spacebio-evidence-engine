# Product Requirements

## Purpose
Define what the Space Biology Evidence Engine must accomplish before implementation.

## Scope
MVP requirements for a controlled-corpus, RAG-based evidence engine with passage-level citations.

## Current status
Approved project definition converted into engineering requirements.

## Problem
Public space biology publications are difficult to search, compare, and synthesize for focused scientific questions. The product must help users explore the evidence while preserving citation traceability and uncertainty.

## Product vision
Build a trustworthy evidence workspace for space biology literature, beginning with approximately 20 to 30 open-access publications in one topic area.

## MVP functional requirements
- Ingest controlled open-access publications.
- Search publications using natural language.
- Answer scientific questions using RAG.
- Ground answers only in retrieved passages.
- Display passage-level citations.
- Compare selected studies.
- Inspect organisms, systems, exposures, conditions, measurements, findings, and limitations.
- Identify candidate conflicts only when evidence context is comparable.
- Identify corpus-limited research gaps.
- Provide insufficient-evidence responses.
- Show knowledge graph relationships when useful, without requiring Neo4j for MVP.

## Nonfunctional requirements
- Citation-first trustworthiness.
- Repeatable ingestion and evaluation.
- Local-first development.
- Modular service boundaries.
- Clear separation between MVP and future architecture.
- Open-source tools where practical.

## Related documents
- [User stories](USER_STORIES.md)
- [RAG architecture](../architecture/RAG_ARCHITECTURE.md)
- [Citation strategy](../rag/CITATION_STRATEGY.md)
- [Traceability matrix](../governance/TRACEABILITY_MATRIX.md)

## Human decisions still required
- Approve initial topic.
- Approve MVP success metrics.
- Confirm target user priority for first release.


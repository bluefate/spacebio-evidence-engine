# Data Dictionary

## Purpose
Define core domain terms consistently.

## Scope
MVP data entities and evidence concepts.

## Current status
Initial dictionary. Publication persistence fields are defined in [METADATA_SCHEMA.md](METADATA_SCHEMA.md) and the `publications` table (issue #27).

## Terms
- Publication: A scientific article included in the controlled corpus. Persisted in PostgreSQL table `publications` with identifiers, license, paths, and ingest/approval state.
- Source: The original access location, DOI, repository URL, PDF, or HTML source (`source_url`, `pdf_url`, `fulltext_url`, optional `pdf_path`).
- Passage: A citation-addressable text span with page or section metadata.
- Chunk: A retrieval unit derived from one or more passages.
- Citation: A link from an answer claim to a supporting passage.
- Organism: Biological organism studied (`organism_model` free-text in August MVP).
- Model system: Experimental model such as rodent, cell culture, tissue, or human sample.
- Exposure: Spaceflight, microgravity, simulated microgravity, radiation, unloading, or related condition (`exposure` free-text in August MVP).
- Measurement: Observed assay, endpoint, omics feature, or physiological result.
- Finding: A sourced statement about an observed result.
- Limitation: A sourced statement about study limits or uncertainty.
- Evidence gap: A corpus-limited area where evidence is absent, sparse, or inconsistent.
- Candidate conflict: A possible disagreement requiring human/scientific review.
- Ingestion status: Pipeline state for a publication (`not_ingested`, and later processing states).
- Human approval: Owner approval of a corpus row (`pending`, `approved`, `rejected`).

## Related documents
- [Metadata schema](METADATA_SCHEMA.md)
- [Corpus specification](CORPUS_SPECIFICATION.md)
- [Citation strategy](../rag/CITATION_STRATEGY.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).


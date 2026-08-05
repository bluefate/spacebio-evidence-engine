# Chunking Strategy

## Purpose
Define how publication text is divided for retrieval while preserving citations.

## Scope
MVP chunking for PDFs and extracted text.

## Current status
Section detection (#30) provides labeled spans for section-aware chunking. Chunk splitter implementation remains downstream (#32 / #33).

## Strategy
- Chunk by section-aware passages where possible, using `SectionSpan` labels from ingestion (`detect_sections` / `detect_sections_from_text`).
- Prefer methods/results/discussion over abstract-only evidence when answering; never treat an abstract span as a full study (`abstract_is_not_full_study`).
- Target ~500–900 tokens per chunk with ~10–20% overlap (tune with eval later).
- Preserve page and passage lineage (`start_page` / `end_page` / offsets from section detection).
- Avoid merging unrelated sections.
- Unlabeled (`unknown`) spans may still be chunked but should not be relabeled as Methods/Results.
- Exclude figure captions and tables as separate chunks for August MVP (deferred post-August).
- Store chunking strategy version.
- Evaluate chunk sizes empirically with benchmark questions.

## Related documents
- [Document processing](../data/DOCUMENT_PROCESSING.md)
- [Retrieval strategy](RETRIEVAL_STRATEGY.md)
- [Citation strategy](CITATION_STRATEGY.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).

# Chunking Strategy

## Purpose
Define how publication text is divided for retrieval while preserving citations.

## Scope
MVP chunking for PDFs and extracted text.

## Current status
Initial strategy.

## Strategy
- Chunk by section-aware passages where possible.
- Target ~500–900 tokens per chunk with ~10–20% overlap (tune with eval later).
- Preserve page and passage lineage.
- Avoid merging unrelated sections.
- Exclude figure captions and tables as separate chunks for August MVP (deferred post-August).
- Store chunking strategy version.
- Evaluate chunk sizes empirically with benchmark questions.

## Related documents
- [Document processing](../data/DOCUMENT_PROCESSING.md)
- [Retrieval strategy](RETRIEVAL_STRATEGY.md)
- [Citation strategy](CITATION_STRATEGY.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).


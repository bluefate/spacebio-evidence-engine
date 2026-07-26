# Chunking Strategy

## Purpose
Define how publication text is divided for retrieval while preserving citations.

## Scope
MVP chunking for PDFs and extracted text.

## Current status
Initial strategy.

## Strategy
- Chunk by section-aware passages where possible.
- Preserve page and passage lineage.
- Avoid merging unrelated sections.
- Keep chunks large enough for scientific context and small enough for retrieval precision.
- Store chunking strategy version.
- Evaluate chunk sizes empirically with benchmark questions.

## Recommendation beyond challenge
Begin with overlapping chunks of approximately 500 to 900 tokens, then tune using retrieval evaluation.

## Related documents
- [Document processing](../data/DOCUMENT_PROCESSING.md)
- [Retrieval strategy](RETRIEVAL_STRATEGY.md)
- [Citation strategy](CITATION_STRATEGY.md)

## Human decisions still required
- Approve initial chunk size and overlap.
- Decide whether figure captions and tables are separate chunks in MVP.


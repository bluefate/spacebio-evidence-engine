# Chunking Strategy

## Purpose
Define how publication text is divided for retrieval while preserving citations.

## Scope
MVP chunking for PDFs and extracted text.

## Current status
Implemented in `spacebio_evidence_engine.ingestion.chunking` (issue #32). Persistence / DB schema remains issue #33. Embedding and vector writes are **out of scope** for #32.

## Strategy
- Chunk by section-aware passages where possible, using `SectionSpan` labels from ingestion (`detect_sections` / `detect_sections_from_text`).
- Prefer methods/results/discussion over abstract-only evidence when answering; never treat an abstract span as a full study (`abstract_is_not_full_study` / `TextChunk.is_abstract`).
- Target ~500–900 tokens per chunk with ~10–20% overlap (tune with eval later).
- Preserve page and passage lineage (`start_page` / `end_page` / offsets from section detection + `PageOffsetMap`).
- Avoid merging unrelated sections.
- Unlabeled (`unknown`) spans may still be chunked but should not be relabeled as Methods/Results.
- Exclude figure captions and tables as separate chunks for August MVP (deferred post-August).
- Store chunking strategy version (`CHUNKING_STRATEGY_VERSION`).
- Evaluate chunk sizes empirically with benchmark questions.

## Size policy (MVP, version `1.0.0`)

| Knob | Default | Notes |
| --- | ---: | --- |
| Target tokens | 700 | Midpoint of the 500–900 band |
| Min tokens | 500 | Soft preference when splitting |
| Max tokens | 900 | Soft cap; sentence boundaries may slightly overshoot |
| Overlap | 15% | Applied when a single section exceeds max |
| Token estimate | whitespace words | No tokenizer dependency in MVP |

API entry points:

- `chunk_extraction(extraction, publication_id=...)` — detect sections then chunk
- `chunk_sections(sections, publication_id=..., page_map=...)` — chunk existing spans
- `chunk_text(text, publication_id=...)` — detect + chunk plain text
- `make_chunk_id(...)` — stable `chk_<sha256[:24]>` from publication, strategy version, section, and offsets

Each `TextChunk` preserves `publication_id`, `section`, `start_offset` / `end_offset`, `start_page` / `end_page` (nullable when unknown), and `chunking_strategy_version`.

## Related documents
- [Document processing](../data/DOCUMENT_PROCESSING.md)
- [Retrieval strategy](RETRIEVAL_STRATEGY.md)
- [Citation strategy](CITATION_STRATEGY.md)
- [Metadata schema](../data/METADATA_SCHEMA.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).

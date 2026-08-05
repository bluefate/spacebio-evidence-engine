# Document Processing

## Purpose
Define how source publications become searchable, citable evidence.

## Scope
MVP PDF-first processing using PyMuPDF, with future extraction improvements.

## Current status
PDF storage (#28), page-level text extraction (#29), section detection (#30), and page mapping (#31) are implemented for the MVP path. Chunking and embedding remain downstream.

## Document state flow
```mermaid
stateDiagram-v2
  [*] --> Candidate
  Candidate --> Approved: license and topic review
  Approved --> Acquired
  Acquired --> Extracted
  Extracted --> Chunked
  Chunked --> Embedded
  Embedded --> Indexed
  Indexed --> Evaluated
  Evaluated --> Published
  Extracted --> Rejected: poor extraction
  Candidate --> Rejected: out of scope

  classDef intake fill:#E0F2FE,stroke:#0284C7,color:#0F172A
  classDef processing fill:#DCFCE7,stroke:#16A34A,color:#052E16
  classDef review fill:#FEF3C7,stroke:#D97706,color:#451A03
  classDef terminal fill:#F3E8FF,stroke:#9333EA,color:#3B0764
  classDef rejected fill:#FFE4E6,stroke:#E11D48,color:#4C0519

  class Candidate,Approved,Acquired intake
  class Extracted,Chunked,Embedded,Indexed processing
  class Evaluated review
  class Published terminal
  class Rejected rejected
```

## MVP processing steps
- Register source in corpus manifest.
- Verify access and license status.
- Extract text with PyMuPDF (body text only for August MVP; tables and figures deferred post-August).
- Preserve page numbers and section hints.
- Normalize text.
- Create citation-preserving passages and chunks.
- Generate embeddings.
- Store lineage and processing status.

## PDF storage

Source PDFs are persisted through a storage abstraction before extraction.

- `PDFStorage` protocol defines `put`, `get`, `exists`, and `delete`.
- The default `local` backend (`LocalFileStorage`) writes files under `PDF_STORAGE_LOCAL_ROOT` (default `data/pdfs`) and requires no cloud SDK.
- The storage key returned by `put` is recorded on the publication record for later retrieval.
- Cloud/object backends can be added behind the same protocol but are not required for the MVP.
- Local PDF roots under `data/pdfs/` are gitignored so ingested binaries stay out of version control.

## PDF text extraction (issue #29)

Page-ordered plain text is extracted with PyMuPDF (`fitz`). Install via `dev` (CI / local validate) or the feature extra:

```bash
pip install -e ".[dev]"
# or
pip install -e ".[ingestion]"
```
API surface (`spacebio_evidence_engine.ingestion`):

- `extract_pdf_bytes(data)` — extract from in-memory PDF bytes
- `extract_pdf_path(path)` — extract from a filesystem path
- `extract_pdf_from_storage(storage, key)` — `storage.get(key)` then extract
- Return type: `ExtractionResult` with `pages: tuple[ExtractedPage, ...]` (`page_number` 1-based, `text`), `page_count`, optional `source_key`, and `full_text`

Typed failures:

- `PDFOpenError` — empty bytes, unreadable path/key, or non-PDF/corrupt input
- `PDFEmptyError` — opens but has no pages or no extractable text
- `PDFExtractionError` — base class / unexpected extraction failures

Security:

- Treat PDF bytes as untrusted. Extraction uses `fitz.open(..., filetype="pdf")` and `page.get_text("text")` only.
- Do not execute JavaScript, launch embedded files, or run content derived from the PDF.

Fixture coverage: `tests/fixtures/sample_two_page.pdf` and `tests/test_pdf_extraction.py`.

## Section detection (issue #30)

Heuristic heading detection over extracted plain text (`spacebio_evidence_engine.ingestion.sections`).

- `detect_sections(extraction)` — from `ExtractionResult` (page offsets preserved)
- `detect_sections_from_text(text, page_starts=...)` — from a string (tests / callers)
- Returns `SectionDetectionResult` with ordered `SectionSpan` values: `label`, `text`, `start_offset` / `end_offset`, optional `start_page` / `end_page`, `heading_text`, `heading_matched`

Labels: `abstract`, `introduction`, `methods`, `results`, `discussion`, `conclusion`, `references`, `acknowledgements`, `supplementary`, and `unknown`.

Rules:

- Only label a span when a heading line matches; **do not invent** missing Methods/Results/etc.
- Leading text before the first heading is `unknown` (safe catch-all).
- `abstract_is_not_full_study` is always `True` — downstream must not treat abstract spans as a complete study.

Fixture coverage: `tests/test_section_detection.py`.

## Page mapping (issue #31)

`ExtractionResult.page_map` returns a `PageOffsetMap` aligned to `full_text`:

- `page_starts`: `(char_offset, page_number)` pairs for non-empty pages
- `page_number_for_offset(offset)`: 1-based page, or `None` when offset is unknown / out of range
- Section detection reuses `extraction.page_map.page_starts` (no duplicate join logic)

## Related documents
- [Chunking strategy](../rag/CHUNKING_STRATEGY.md)
- [Data architecture](../architecture/DATA_ARCHITECTURE.md)
- [Corpus specification](CORPUS_SPECIFICATION.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).


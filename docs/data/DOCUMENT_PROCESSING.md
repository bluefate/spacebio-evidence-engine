# Document Processing

## Purpose
Define how source publications become searchable, citable evidence.

## Scope
MVP PDF-first processing using PyMuPDF, with future extraction improvements.

## Current status
Initial processing design.

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

## Related documents
- [Chunking strategy](../rag/CHUNKING_STRATEGY.md)
- [Data architecture](../architecture/DATA_ARCHITECTURE.md)
- [Corpus specification](CORPUS_SPECIFICATION.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).


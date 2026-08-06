# Metadata Schema

## Purpose
Define required and recommended metadata fields for persistence and citation.

## Scope
Publication, passage, chunk, entity, relationship, and evaluation metadata.
**Issue #27** implements `publications`. **Issue #33** implements `chunks`. Passage and embedding tables remain follow-on work.

## Current status
Publication persistence schema implemented (SQLAlchemy + Alembic revision `20260805_0001`).
Chunk persistence schema implemented (SQLAlchemy + Alembic revision `20260806_0002`).

## Required publication fields

| Field | DB column | Notes |
|-------|-----------|-------|
| `publication_id` | `publications.publication_id` (PK) | Stable corpus ID (e.g. `pub_001`) |
| `title` | `title` | Full title |
| `source_url` | `source_url` | Canonical DOI or landing URL |
| `license_status` | `license_status` | Review state (e.g. `approved_oa_candidate`) |
| `corpus_topic` | `corpus_topic` | e.g. `microgravity_skeletal_muscle` |
| `ingestion_status` | `ingestion_status` | Default `not_ingested` |

## Recommended / implemented publication fields

| Field | DB column | Notes |
|-------|-----------|-------|
| `doi` | `doi` | Indexed |
| `pmcid` / `pmid` | `pmcid`, `pmid` | When available |
| `year` | `year` | Integer |
| `journal` | `journal` | |
| `authors` | `authors` | Free-text author string for MVP |
| `abstract` | `abstract` | Optional |
| `keywords` | `keywords` | Optional free-text |
| `nasa_repository_id` | `nasa_repository_id` | Optional |
| `license` | `license` | e.g. `cc-by`, `cc-by-nc-nd` |
| `pdf_path` | `pdf_path` | Local path after staging |
| `pdf_url` / `fulltext_url` | `pdf_url`, `fulltext_url` | Remote paths |
| `organism_model` | `organism_model` | Free-text (August MVP) |
| `exposure` | `exposure` | Free-text (August MVP) |
| `selection_notes` | `selection_notes` | Curation notes |
| `human_approval` | `human_approval` | `pending` / `approved` / `rejected` |
| timestamps | `created_at`, `updated_at` | Timezone-aware |

ORM: `spacebio_evidence_engine.db.models.Publication`  
Migration: `alembic/versions/20260805_0001_create_publications.py`  
Apply: `make migrate` (or `alembic upgrade head`)

## Required passage fields
- `passage_id`
- `publication_id`
- `text`
- `page_start` / `page_end`
- `section_label`
- `extraction_method`

Page mapping note:

- `page_start` and `page_end` are 1-based page numbers when the source text can be mapped to pages.
- If page mapping is unavailable, keep the fields `null` rather than inventing page numbers.
- Ingestion contracts should preserve the page map from `ExtractionResult.page_map` so section and chunk spans can reuse it.

*(Not persisted yet — follow-on issues.)*

## Required chunk fields

| Field | DB column | Notes |
|-------|-----------|-------|
| `chunk_id` | `chunks.chunk_id` (PK) | Stable id from chunker (`chk_…`) |
| `publication_id` | `publication_id` (FK → `publications`) | Required; `ON DELETE RESTRICT` |
| `section` | `section` | Section label (e.g. `methods`, `unknown`) |
| `chunk_text` | `chunk_text` | Retrieval text |
| `content_hash` | `content_hash` | SHA-256 hex of `chunk_text` |
| `start_offset` / `end_offset` | `start_offset`, `end_offset` | Char offsets in full document text |
| `page_start` / `page_end` | `page_start`, `page_end` | 1-based pages or `NULL` |
| `chunking_strategy_version` | `chunking_strategy_version` | e.g. `1.0.0` |

## Recommended / implemented chunk fields

| Field | DB column | Notes |
|-------|-----------|-------|
| `passage_ids` | `passage_ids` | Optional text (JSON array) until passages table exists |
| `embedding_model` | `embedding_model` | Null until vectors are written |
| `section_heading` | `section_heading` | Optional matched heading |
| timestamps | `created_at`, `updated_at` | Timezone-aware |

Chunk page mapping note:

- Preserve page bounds on chunks whenever they can be derived from source passages.
- Missing page bounds must stay explicit as `null`; never synthesize a page.

ORM: `spacebio_evidence_engine.db.models.Chunk`  
Migration: `alembic/versions/20260806_0002_create_chunks.py`  
Apply: `make migrate` (or `alembic upgrade head`)

## Related documents
- [Data dictionary](DATA_DICTIONARY.md)
- [Citation strategy](../rag/CITATION_STRATEGY.md)
- [Data architecture](../architecture/DATA_ARCHITECTURE.md)
- [Corpus inventory](CORPUS_INVENTORY.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).

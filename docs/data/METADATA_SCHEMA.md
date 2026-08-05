# Metadata Schema

## Purpose
Define required and recommended metadata fields for persistence and citation.

## Scope
Publication, passage, chunk, entity, relationship, and evaluation metadata.
**Issue #27 implements the `publications` table only.** Passage/chunk tables come later.

## Current status
Publication persistence schema implemented (SQLAlchemy + Alembic revision `20260805_0001`).

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
- `page_start`
- `page_end`
- `section_label`
- `extraction_method`

*(Not persisted yet — follow-on issues.)*

## Required chunk fields
- `chunk_id`
- `publication_id`
- `passage_ids`
- `chunk_text`
- `embedding_model`
- `chunking_strategy_version`

*(Not persisted yet — follow-on issues.)*

## Related documents
- [Data dictionary](DATA_DICTIONARY.md)
- [Citation strategy](../rag/CITATION_STRATEGY.md)
- [Data architecture](../architecture/DATA_ARCHITECTURE.md)
- [Corpus inventory](CORPUS_INVENTORY.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).

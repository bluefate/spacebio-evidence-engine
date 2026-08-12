# Metadata Schema

## Purpose
Define required and recommended metadata fields for persistence and citation.

## Scope
Publication, passage, chunk, entity, relationship, and evaluation metadata.
**Issue #27** implements `publications`. **Issue #33** implements `chunks`. **Issue #42** implements `chunk_embeddings`. Passage tables remain follow-on work.

## Current status
Publication persistence schema implemented (SQLAlchemy + Alembic revision `20260805_0001`).
Chunk persistence schema implemented (SQLAlchemy + Alembic revision `20260806_0002`).
Chunk embedding vector schema implemented (SQLAlchemy + Alembic revision `20260806_0003`).
Retrieval metadata filter API documented for search (#47).
Corpus inventory CSV schema implemented in `spacebio_evidence_engine.corpus.inventory` (#21).

## Corpus inventory CSV schema

The August MVP corpus is described by a machine-readable manifest:

- **File:** `data/inventory/august_mvp_corpus_manifest.csv`
- **Python model:** `spacebio_evidence_engine.corpus.inventory.CorpusInventoryRecord`
- **Loader:** `spacebio_evidence_engine.corpus.inventory.load_inventory_manifest`

### Required fields

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `publication_id` | string | `min_length=1` | Stable corpus ID, e.g. `pub_001`. |
| `title` | string | `min_length=1` | Full publication title. |
| `doi` | string | `10.xxxx/...` | DOI identifier. |
| `year` | integer | `1900 <= year <= 2100` | Publication year. |
| `authors` | string | `min_length=1` | Author list string. |
| `license` | string | `min_length=1` | License identifier, e.g. `cc-by`, `cc-by-nc-nd`. |
| `license_status` | string | `min_length=1` | Project review label, e.g. `approved_oa_candidate`. |
| `access_restriction_notes` | string | `min_length=1` | Attribution/access constraints derived from the license. |
| `redistribution_notes` | string | `min_length=1` | Redistribution/derivative constraints derived from the license. |
| `source_url` | URL | `https://doi.org/...` | Canonical DOI landing page. |
| `pdf_url` | URL | `http(s)://...` | PDF URL or render link. |
| `fulltext_url` | URL | `http(s)://...` | Full-text landing URL. |
| `pdf_quality` | enum | `good`, `poor_text`, `needs_ocr`, `corrupt`, `missing` | PDF extraction quality assessment. |
| `corpus_topic` | string | `min_length=1` | Approved topic, e.g. `microgravity_skeletal_muscle`. |
| `organism_model` | string | `min_length=1` | Organism or model system. |
| `exposure` | string | `min_length=1` | Exposure or condition, e.g. `spaceflight`. |
| `inclusion_pass` | enum | `yes` / `no` | Whether the row passed inclusion criteria. |
| `exclusion_flags` | string | `min_length=1` | Comma-separated flags or `none`. |
| `ingestion_status` | enum | `not_ingested`, `pending`, `processing`, `succeeded`, `failed`, `pdf_quality_blocked` | Pipeline state. |
| `human_approval` | enum | `pending`, `approved`, `rejected` | Owner approval state. |

### Optional fields

| Field | Type | Description |
|-------|------|-------------|
| `pmcid` | string | PubMed Central identifier. |
| `pmid` | integer | PubMed numeric identifier. |
| `journal` | string | Journal or venue name. |
| `pdf_quality_notes` | string | Structured QA notes (page count, text density, issues). |
| `selection_notes` | string | Curation notes explaining selection. |

### Example inventory record

```json
{
  "publication_id": "pub_001",
  "title": "Spaceflight on the ISS changed the skeletal muscle proteome of two astronauts.",
  "doi": "10.1038/s41526-024-00406-3",
  "pmcid": "PMC11153545",
  "pmid": 38839773,
  "year": 2024,
  "journal": null,
  "authors": "Murgia M, Rittweger J, Reggiani C, Bottinelli R, Mann M, Schiaffino S, Narici MV.",
  "license": "cc-by",
  "license_status": "approved_oa_candidate",
  "access_restriction_notes": "Attribution (BY) required. Passages may be retrieved and quoted with citation and link to source.",
  "redistribution_notes": "Passage quoting with source link is allowed. Full-text redistribution or derivative works require attribution; do not remove copyright notices.",
  "source_url": "https://doi.org/10.1038/s41526-024-00406-3",
  "pdf_url": "https://europepmc.org/articles/PMC11153545?pdf=render",
  "fulltext_url": "https://doi.org/10.1038/s41526-024-00406-3",
  "pdf_quality": "good",
  "pdf_quality_notes": "page_count=13, text_chars=81723, empty_pages=0, image_pages=0, text_density=6286.4; text layer present and dense",
  "corpus_topic": "microgravity_skeletal_muscle",
  "organism_model": "human",
  "exposure": "spaceflight",
  "selection_notes": "astronaut skeletal muscle proteome",
  "inclusion_pass": "yes",
  "exclusion_flags": "none",
  "ingestion_status": "not_ingested",
  "human_approval": "approved"
}
```

### Validation

Use the loader to validate the whole manifest:

```python
from spacebio_evidence_engine.corpus import load_inventory_manifest

records = load_inventory_manifest()
```

## Required publication fields

| Field | DB column | Notes |
|-------|-----------|-------|
| `publication_id` | `publications.publication_id` (PK) | Stable corpus ID (e.g. `pub_001`) |
| `title` | `title` | Full title |
| `source_url` | `source_url` | Canonical DOI or landing URL |
| `license_status` | `license_status` | Review state (e.g. `approved_oa_candidate`) |
| `corpus_topic` | `corpus_topic` | e.g. `microgravity_skeletal_muscle` |
| `ingestion_status` | `ingestion_status` | Enum-backed string (#34): `not_ingested`, `pending`, `processing`, `succeeded`, `failed`, `pdf_quality_blocked` |

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

## Required chunk embedding fields (issue #42)

| Field | DB column | Notes |
|-------|-----------|-------|
| `chunk_id` | `chunk_embeddings.chunk_id` (PK, FK → `chunks`) | 1:1 with chunk; `ON DELETE CASCADE` |
| `embedding` | `embedding` | PostgreSQL `vector(384)`; SQLite CI uses JSON text |
| `model_name` | `model_name` | e.g. `sentence-transformers/all-MiniLM-L6-v2` |
| `dimension` | `dimension` | Constrained to **384** (MVP MiniLM) |

Extension dependency: PostgreSQL `vector` (#8). Migration also runs `CREATE EXTENSION IF NOT EXISTS vector`.

ORM: `spacebio_evidence_engine.db.models.ChunkEmbedding`  
Migration: `alembic/versions/20260806_0003_create_chunk_embeddings.py`

## Retrieval filter fields (issue #47)

Approved equality filters for `parse_retrieval_filters` /
`RetrievalFilters` (used by `semantic_search` and `hybrid_search`):

| Filter key | Source column | Notes |
|------------|---------------|-------|
| `publication_id` | `publications.publication_id` | Exact publication |
| `corpus_topic` | `publications.corpus_topic` | e.g. `microgravity_skeletal_muscle` |
| `organism_model` | `publications.organism_model` | Free-text MVP organism/system label |
| `exposure` | `publications.exposure` | Free-text MVP exposure |
| `license_status` | `publications.license_status` | License review state |
| `year` | `publications.year` | Integer year (`>= 1`) |
| `human_approval` | `publications.human_approval` | `pending` / `approved` / `rejected` |
| `section` | `chunks.section` | Chunk section label |

Unknown keys and blank string values raise `InvalidRetrievalFilterError`.
There is no separate `system` column in the MVP schema; use `organism_model`.

## Related documents
- [Data dictionary](DATA_DICTIONARY.md)
- [Citation strategy](../rag/CITATION_STRATEGY.md)
- [Retrieval strategy](../rag/RETRIEVAL_STRATEGY.md)
- [Data architecture](../architecture/DATA_ARCHITECTURE.md)
- [Corpus inventory](CORPUS_INVENTORY.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).

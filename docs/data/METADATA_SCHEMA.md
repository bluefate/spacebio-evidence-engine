# Metadata Schema

## Purpose
Define required and recommended metadata fields.

## Scope
Publication, passage, chunk, entity, relationship, and evaluation metadata.

## Current status
Initial logical schema, not yet implemented.

## Required publication fields
- `publication_id`
- `title`
- `source_url`
- `license_status`
- `corpus_topic`
- `ingestion_status`

## Recommended publication fields
- `doi`
- `authors`
- `year`
- `journal`
- `abstract`
- `keywords`
- `nasa_repository_id`

## Required passage fields
- `passage_id`
- `publication_id`
- `text`
- `page_start`
- `page_end`
- `section_label`
- `extraction_method`

## Required chunk fields
- `chunk_id`
- `publication_id`
- `passage_ids`
- `chunk_text`
- `embedding_model`
- `chunking_strategy_version`

## Related documents
- [Data dictionary](DATA_DICTIONARY.md)
- [Citation strategy](../rag/CITATION_STRATEGY.md)
- [Data architecture](../architecture/DATA_ARCHITECTURE.md)

## Human decisions still required
- Approve final database naming conventions.
- Choose JSON versus normalized tables for selected metadata.


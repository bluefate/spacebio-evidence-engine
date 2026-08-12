# Citation Strategy

## Purpose
Ensure every scientific answer can be verified against source passages.

## Scope
Passage-level citation model for MVP.

## Current status
Initial strategy. Context assembly preserves chunk IDs and provenance when
packing retrieved evidence for generation (issue #52).

## Requirements
- Cite at passage level, not only publication level.
- Store page, section, source URL, and text span where available.
- Link each answer claim to supporting passage IDs.
- Show cited passages in the UI.
- Omit unsupported claims.
- Warn when evidence is based on few passages or few studies.
- Preserve limitations when relevant.
- **When evidence is insufficient, return no citations and no generated answer.** The system must not fabricate citations or fill gaps with model knowledge. Instead, it returns an `EvidenceSufficiency` status of `insufficient` with a clear reason (issue #55).

## Context assembly and citation IDs

`assemble_context` assigns stable citation ids (`C1`…`Cn`) to included
retrieved chunks and emits matching `PassageCitation` rows. Budget pressure
may omit later hits, but omitted `chunk_id` values are listed explicitly in
`omitted_chunk_ids`. Included evidence blocks always retain `chunk_id` and
publication provenance in the packed context — never strip IDs to save tokens.

## Citation validation
Citation emission is handled by `spacebio_evidence_engine.rag.citations`.

- `emit_passage_citations(context, requested_citation_ids=...)` emits only
  `PassageCitation` rows whose citation IDs and chunk IDs are present in the
  included retrieved context.
- `emit_citations_for_answer_text(answer_text, context)` extracts `[C1]`-style
  markers and emits the matching retrieved citations.
- Unknown citation IDs are stripped and returned in `rejected_citation_ids` /
  `unknown_citation_ids` with `AnswerWarning` entries so downstream answer
  assembly can fail or decline instead of silently returning unsupported claims.
- Citations whose `chunk_id` is not in `ContextAssemblyResult.included_chunk_ids`
  are not emitted, even if a citation object exists.

The system must verify that cited passage IDs were present in retrieved context before returning the answer.

## UI evidence panel

The web app renders cited passages with
`apps/web/src/components/evidence/EvidencePanel` (issue #63):

- Shows passage text plus publication id/title, section, page, and chunk id.
- Highlights the active citation via `activeCitationId` (and optional
  `onSelectCitation` for answer→evidence wiring in #62/#66).
- Missing states stay explicit: empty citation lists, unknown active ids, and
  absent passage text or provenance fields render graceful placeholders rather
  than inventing content.
- Accepts UI `EvidencePassage` objects or API-shaped `PassageCitation` rows
  through `toEvidencePassage`.

## Page mapping
- Extraction should preserve a page map from source PDFs to text offsets (`ExtractionResult.page_map` / `PageOffsetMap`).
- Section spans and later chunks should reuse that map rather than inventing page numbers.
- When a page number cannot be determined — including negative or past-EOF offsets — keep the field `null` and preserve that unknown state through storage and retrieval.

## Agent preservation rules
- Preserve publication identifiers, section names, page numbers, and source passages across ingestion, chunking, storage, retrieval, and UI.
- Every product-generated scientific answer must be traceable to retrieved evidence.
- Do not answer scientific questions from model memory when the application is expected to use the corpus.
- Do not drop span linkage, passage IDs, or source text to simplify prompts or UI.
- Root contract: [AGENTS.md](../../AGENTS.md).

## Related documents
- [RAG architecture](../architecture/RAG_ARCHITECTURE.md)
- [Metadata schema](../data/METADATA_SCHEMA.md)
- [Prompting strategy](PROMPTING_STRATEGY.md)
- [Agent workflow](../development/AGENT_WORKFLOW.md)

## Decision status
Resolved for August MVP (deadline 2026-08-31) or deferred post-August. See [decision log](../governance/DECISION_LOG.md).

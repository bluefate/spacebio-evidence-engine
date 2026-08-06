# Corpus Specification

## Purpose
Define rules for selecting and maintaining the controlled publication corpus.

## Scope
August MVP controlled corpus of open-access publications on **microgravity and skeletal muscle**. Initial planning target was ~10–15 papers; the proposed inventory is larger because newer high-relevance OA studies were added by owner request.

## Current status
**Topic and selection rules approved** (D1, 2026-08-04).  
**License policy for NC-ND approved** (D10, 2026-08-04): CC BY-NC-ND allowed because the engine is non-commercial.  
**Owner-approved inventory of 23 publications** — see [CORPUS_INVENTORY.md](CORPUS_INVENTORY.md) and [august_mvp_corpus_manifest.csv](../../data/inventory/august_mvp_corpus_manifest.csv).

## Approved initial topic
**Microgravity and skeletal muscle.**

## Inclusion criteria (approved corpus selection rules)
- Open-access publication with legal permission for ingestion under this project's use model.
- Relevant to the approved initial topic.
- Contains extractable methods, results, or findings (or citable mission/methods design detail).
- Has sufficient metadata for citation (title, source, DOI/PMCID where available).

## Exclusion criteria (approved)
- Paywalled or unclear rights.
- Not directly relevant to the selected topic.
- No usable text extraction path.
- Non-scientific commentary unless explicitly approved.

## License policy (D10)

The evidence engine is **non-commercial** (education / research / HootCamp Build Phase).

| License | Allowed in corpus? | Use constraints |
|---------|--------------------|-----------------|
| CC BY | Yes (preferred) | Attribute; retrieve; quote with citation; link to source |
| CC BY-NC-ND | Yes | Same retrieval/citation use. No commercial redistribution of full texts; no selling adapted full-text derivatives. Re-review if the project becomes commercial |
| Other / unclear / paywalled | No | Exclude until clarified |

Every manifest row must record `license` and `license_status`. Ingest pipelines must preserve license metadata with the publication record.

## Access and redistribution notes

Every manifest row must record `access_restriction_notes` and `redistribution_notes` derived from the declared license.

| License | `access_restriction_notes` | `redistribution_notes` |
|---|---|---|
| CC BY | Attribution (BY) required; passages may be quoted with citation and source link. | Passage quoting allowed; full-text redistribution requires attribution. |
| CC BY-NC-ND | Attribution (BY), non-commercial (NC), and no-derivatives (ND) required. | Quote passages for non-commercial citation-first answers; do not sell the corpus or publish adapted full-text versions. |
| CC0 / public domain | No known copyright restrictions; attribution is good practice. | No redistribution restrictions. |
| Unknown / paywalled | Exclude until clarified. | Do not download or redistribute. |

`spacebio_evidence_engine.corpus.licenses.classify_license` automates this mapping and flags `blocked` or `needs_review` licenses.

## License review workflow (approved)
1. Record source URL, DOI if any, and stated license/access terms in the corpus manifest.
2. Owner reviews rights before ingestion; unclear rights block ingest.
3. Corpus-changing PRs require owner scientific/license review.
4. NC-ND items require the non-commercial use affirmation in [CORPUS_INVENTORY.md](CORPUS_INVENTORY.md).

## August MVP inventory (approved)
- Count: **23** publications (17 CC BY + 6 CC BY-NC-ND).
- Machine-readable manifest: `data/inventory/august_mvp_corpus_manifest.csv`.
- Narrative checklist and table: [CORPUS_INVENTORY.md](CORPUS_INVENTORY.md).
- List approval: **approved** (`human_approval=approved` on all rows; issue #20 closed).

## Follow-on work
- Per-item PDF quality assessment (#25) and license spot-check on publisher pages (#23).
- Ingest approved PDFs through the document pipeline.

## Related documents
- [Corpus inventory](CORPUS_INVENTORY.md)
- [Product requirements](../product/PRODUCT_REQUIREMENTS.md)
- [Document processing](DOCUMENT_PROCESSING.md)
- [Metadata schema](METADATA_SCHEMA.md)
- [Decision log](../governance/DECISION_LOG.md)

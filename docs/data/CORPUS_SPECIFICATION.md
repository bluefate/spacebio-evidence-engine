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

## Approved publication source discovery

Publication source discovery is limited to the approved August MVP topic:
**microgravity and skeletal muscle**. Discovery identifies legal, open-access
source locations for candidate publications; it does not by itself approve new
corpus content for ingest.

### Approved primary sources

These sources are approved for locating and verifying full-text publication
sources when the publication is already in scope and the manifest preserves the
source, license, and provenance fields.

| Source | Access method | License / provenance notes |
|---|---|---|
| Publisher version-of-record DOI landing page | Resolve the DOI in the manifest and record the canonical article page as `source_url` or `fulltext_url`. | Treat the publisher page as the primary authority for article license, copyright statement, and version-of-record provenance. Ingest only when the page declares an allowed license or owner review records approval. |
| PubMed Central / Europe PMC open-access full text | Resolve by DOI, PMID, or PMCID; record article, XML/HTML, and PDF URLs when available. | Approved for OA full text and PDFs when the record exposes an allowed license. Preserve DOI, PMID, PMCID, repository URL, PDF URL, and license terms. |
| Journal-hosted open-access PDF | Follow the publisher article page to the official PDF URL. | Approved when the article page and PDF carry matching allowed license terms. Prefer this over mirrors because it preserves version and publisher provenance. |

At least one primary source is approved for MVP use: **publisher
version-of-record DOI pages and PubMed Central / Europe PMC open-access full
text records** may be used to locate source URLs and PDFs for owner-approved
manifest rows.

### Supporting verification sources

Supporting sources may help confirm bibliographic metadata or discover candidate
OA locations, but they are not sufficient by themselves to approve ingest.

| Source | Use | Constraint |
|---|---|---|
| Crossref | Confirm DOI registration metadata and license links where present. | Use as a metadata cross-check; do not rely on Crossref alone when publisher or repository license terms disagree. |
| PubMed | Confirm PMID, title, journal, and publication metadata. | Abstract-only PubMed records are not full-text sources. |
| Unpaywall / OpenAlex | Discover OA locations and license hints for DOI-based candidates. | Re-resolve any discovered location to the publisher or repository page before ingest approval. |
| NASA OSDR / mission dataset pages | Support space-biology relevance checks and mission context. | Dataset pages do not replace publication license review. |

### Disallowed sources

The following sources are explicitly disallowed for MVP corpus ingest:

- Shadow libraries, pirate sites, or unauthorized PDF mirrors.
- Paywalled PDFs, institution-proxy downloads, or files requiring credentials.
- ResearchGate, Academia.edu, personal websites, or lab file shares unless the
  owner explicitly verifies that the uploaded file is legally open access under
  an allowed license.
- General web mirrors, scraping caches, and content aggregators that do not
  preserve article-level license and provenance.
- Abstract-only records used as substitutes for full-text publications.
- AI summaries, secondary summaries, or generated text used as source evidence.

### Discovery workflow

1. Start from an approved candidate DOI or owner-approved candidate title in the
   microgravity and skeletal muscle scope.
2. Resolve the DOI landing page and record canonical bibliographic metadata.
3. Locate an official OA full-text source, preferring the publisher article/PDF
   or PubMed Central / Europe PMC repository copy.
4. Record `source_url`, `pdf_url`, `fulltext_url`, `license`,
   `license_status`, `access_restriction_notes`, and `redistribution_notes` in
   the candidate manifest.
5. Exclude or hold the candidate when license, provenance, or full-text access
   is unclear.
6. Do not ingest a discovered source until owner approval is recorded in the
   manifest.

## Duplicate publication policy

Candidate manifests must be screened for duplicate publications before ingest.
Duplicate checks are applied to corpus candidates only and must preserve the
original source/provenance fields for every row.

Detection rules:

- Normalize DOI values by stripping DOI URL / `doi:` prefixes, lowercasing, and
  trimming trailing punctuation. Matching normalized DOIs are duplicates.
- Normalize titles by lowercasing, removing punctuation/accent variants, folding
  whitespace, and removing common version labels such as `preprint`, `accepted
  manuscript`, `author manuscript`, and `version of record`. Matching normalized
  title + year keys are treated as version variants.
- Choose the canonical record by stable lowest `publication_id` within the
  duplicate set so the earliest assigned corpus ID remains the citable source of
  truth.
- Flag every duplicate-set member with the duplicate set ID, canonical
  publication ID, whether the row is canonical, and match reason(s). Do not
  delete candidate rows silently; exclusions or replacements require owner
  review.

Utility:

```bash
python scripts/detect_corpus_duplicates.py data/inventory/august_mvp_corpus_manifest.csv
```

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

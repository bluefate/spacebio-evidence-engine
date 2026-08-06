"""Assess PDF quality for every row in the August MVP corpus manifest (issue #25).

This script downloads the source PDF for each publication, runs the local
quality rubric, and writes the scores back to the manifest. It does not keep
the downloaded files by default.

Run from the repository root:

    python3 scripts/assess_corpus_pdf_quality.py

Set ``SPACEBIO_PDF_TIMEOUT`` to override the per-request timeout (seconds).
"""

from __future__ import annotations

import csv
import os
import sys
import time
from pathlib import Path

from spacebio_evidence_engine.ingestion.pdf_quality import (
    PDFQualityCategory,
    PDFQualityResult,
    score_publication_pdf,
)

MANIFEST_PATH = Path("data/inventory/august_mvp_corpus_manifest.csv")
DEFAULT_TIMEOUT = float(os.environ.get("SPACEBIO_PDF_TIMEOUT", "30.0"))
REQUEST_DELAY = float(os.environ.get("SPACEBIO_PDF_DELAY", "1.5"))
RETRY_DELAY = float(os.environ.get("SPACEBIO_PDF_RETRY_DELAY", "5.0"))


def _row_quality_status(result: PDFQualityResult) -> str:
    """Map a quality category to a pipeline status value."""
    if result.category in (PDFQualityCategory.CORRUPT, PDFQualityCategory.MISSING):
        return "pdf_quality_blocked"
    return "not_ingested"


def _assess_row(row: dict[str, str]) -> tuple[str, PDFQualityResult]:
    """Assess one publication, returning its id and result.

    Sleeps between requests and retries once on HTTP 429 rate limits.
    """
    pub_id = row["publication_id"]
    pdf_url = row.get("pdf_url", "").strip()
    pmcid = row.get("pmcid", "").strip() or None
    if not pdf_url:
        return pub_id, PDFQualityResult(
            category=PDFQualityCategory.MISSING,
            page_count=0,
            text_chars=0,
            empty_pages=0,
            image_pages=0,
            text_density=0.0,
            has_text_layer=False,
            notes="No pdf_url in manifest",
            error="missing pdf_url",
        )

    result = score_publication_pdf(pdf_url, pmcid=pmcid, timeout=DEFAULT_TIMEOUT)
    time.sleep(REQUEST_DELAY)

    if result.category == PDFQualityCategory.MISSING and "429" in (result.error or ""):
        print(f"{pub_id}: rate limited, retrying after {RETRY_DELAY}s")
        time.sleep(RETRY_DELAY)
        result = score_publication_pdf(pdf_url, pmcid=pmcid, timeout=DEFAULT_TIMEOUT)

    return pub_id, result


def _ensure_columns(fieldnames: list[str]) -> list[str]:
    """Add pdf_quality and pdf_quality_notes columns if absent."""
    for column in ("pdf_quality", "pdf_quality_notes"):
        if column not in fieldnames:
            # Insert after fulltext_url so quality sits near source URLs.
            try:
                index = fieldnames.index("fulltext_url") + 1
            except ValueError:
                index = len(fieldnames)
            fieldnames.insert(index, column)
    return fieldnames


def main() -> int:
    if not MANIFEST_PATH.is_file():
        print(f"Manifest not found: {MANIFEST_PATH}", file=sys.stderr)
        return 1

    with MANIFEST_PATH.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = _ensure_columns(list(reader.fieldnames or []))
        rows = list(reader)

    results: dict[str, PDFQualityResult] = {}
    for row in rows:
        pub_id, result = _assess_row(row)
        results[pub_id] = result
        print(f"{pub_id}: {result.category} ({result.notes})")

    for row in rows:
        pub_id = row["publication_id"]
        result = results[pub_id]
        row["pdf_quality"] = result.category.value
        row["pdf_quality_notes"] = result.notes
        if result.error:
            row["pdf_quality_notes"] += f"; error={result.error}"
        row["ingestion_status"] = _row_quality_status(result)

    with MANIFEST_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nUpdated {MANIFEST_PATH} with {len(rows)} PDF quality scores.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

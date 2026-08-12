"""Reusable helpers for the corpus inventory review notebook."""

from __future__ import annotations

import csv
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from spacebio_evidence_engine.corpus.inventory import (
    CorpusInventoryRecord,
    load_inventory_manifest,
)

INVENTORY_FIELDNAMES = tuple(CorpusInventoryRecord.model_fields)


@dataclass(frozen=True, slots=True)
class InventorySummary:
    """Aggregate review counts for a corpus inventory manifest."""

    total_records: int
    approved_records: int
    ingestible_records: int
    included_records: int
    blocked_pdf_records: int
    corpus_topics: tuple[str, ...]
    license_counts: dict[str, int]
    organism_model_counts: dict[str, int]
    exposure_counts: dict[str, int]
    pdf_quality_counts: dict[str, int]
    human_approval_counts: dict[str, int]
    ingestion_status_counts: dict[str, int]


def summarize_inventory(records: list[CorpusInventoryRecord]) -> InventorySummary:
    """Return reproducible inventory review counts without changing records."""
    return InventorySummary(
        total_records=len(records),
        approved_records=sum(record.human_approval == "approved" for record in records),
        ingestible_records=sum(record.license_can_ingest() for record in records),
        included_records=sum(record.inclusion_pass == "yes" for record in records),
        blocked_pdf_records=sum(record.pdf_quality == "missing" for record in records),
        corpus_topics=tuple(sorted({record.corpus_topic for record in records})),
        license_counts=_counts(record.license for record in records),
        organism_model_counts=_counts(record.organism_model for record in records),
        exposure_counts=_counts(record.exposure for record in records),
        pdf_quality_counts=_counts(record.pdf_quality for record in records),
        human_approval_counts=_counts(record.human_approval for record in records),
        ingestion_status_counts=_counts(record.ingestion_status for record in records),
    )


def records_to_csv_rows(records: list[CorpusInventoryRecord]) -> list[dict[str, Any]]:
    """Serialize inventory records to approved CSV-schema rows."""
    rows: list[dict[str, Any]] = []
    for record in records:
        row = record.model_dump(mode="json")
        rows.append({field: _csv_value(row.get(field)) for field in INVENTORY_FIELDNAMES})
    return rows


def write_inventory_manifest(records: list[CorpusInventoryRecord], path: Path) -> Path:
    """Write records using the approved inventory CSV schema."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=INVENTORY_FIELDNAMES)
        writer.writeheader()
        writer.writerows(records_to_csv_rows(records))
    return path


def load_inventory_review(path: Path | None = None) -> list[CorpusInventoryRecord]:
    """Read and validate a notebook inventory review CSV."""
    return load_inventory_manifest(path)


def _counts(values: Iterable[object]) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values).items()))


def _csv_value(value: Any) -> str:
    if value is None:
        return ""
    return str(value)

"""Corpus inventory schema and loader.

Issue #21: machine-readable schema for corpus inventory records
(identifiers, license, topic tags, paths).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from spacebio_evidence_engine.corpus.licenses import classify_license

MANIFEST_PATH = (
    Path(__file__).resolve().parents[3] / "data" / "inventory" / "august_mvp_corpus_manifest.csv"
)

InclusionPass = Literal["yes", "no"]
HumanApproval = Literal["pending", "approved", "rejected"]
PdfQuality = Literal["good", "poor_text", "needs_ocr", "corrupt", "missing"]

IngestionStatus = Literal[
    "not_ingested",
    "pending",
    "processing",
    "succeeded",
    "failed",
    "pdf_quality_blocked",
]


class CorpusInventoryRecord(BaseModel):
    """Machine-readable schema for one row of the corpus inventory manifest.

    Maps directly to the CSV header in ``data/inventory/august_mvp_corpus_manifest.csv``.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    # Identifiers and bibliographic metadata
    publication_id: str = Field(
        ...,
        min_length=1,
        description="Stable corpus identifier (e.g. pub_001).",
    )
    title: str = Field(..., min_length=1, description="Full publication title.")
    doi: str = Field(
        ...,
        min_length=1,
        pattern=r"^10\.\d{4,9}/.+",
        description="DOI identifier, e.g. 10.1038/s41526-024-00406-3.",
    )
    pmcid: str | None = Field(default=None, description="PubMed Central identifier when available.")
    pmid: int | None = Field(
        default=None, ge=1, description="PubMed numeric identifier when available."
    )
    year: int = Field(..., ge=1900, le=2100, description="Publication year.")
    journal: str | None = Field(default=None, description="Journal or venue name.")
    authors: str = Field(..., min_length=1, description="Author string, often comma-separated.")

    # License and use policy
    license: str = Field(
        ...,
        min_length=1,
        description="License identifier, e.g. cc-by or cc-by-nc-nd.",
    )
    license_status: str = Field(
        ...,
        min_length=1,
        description="Project review state, e.g. approved_oa_candidate.",
    )
    access_restriction_notes: str = Field(
        ...,
        min_length=1,
        description="Attribution and access constraints derived from the license.",
    )
    redistribution_notes: str = Field(
        ...,
        min_length=1,
        description="Redistribution and derivative-work constraints derived from the license.",
    )

    # URLs and paths
    source_url: str = Field(
        ...,
        min_length=1,
        pattern=r"^https://doi\.org/",
        description="Canonical DOI landing page URL.",
    )
    pdf_url: str = Field(
        ...,
        min_length=1,
        pattern=r"^https?://",
        description="Direct or landing URL for the PDF.",
    )
    fulltext_url: str = Field(
        ...,
        min_length=1,
        pattern=r"^https?://",
        description="URL for HTML/full-text landing page.",
    )

    # PDF quality assessment
    pdf_quality: PdfQuality = Field(
        default="good",
        description=(
            "Quality assessment from PDF QA: good, poor_text, needs_ocr, corrupt, or missing."
        ),
    )
    pdf_quality_notes: str | None = Field(
        default=None,
        description="Structured QA notes (page count, text density, issues).",
    )

    # Topic and model system tags
    corpus_topic: str = Field(
        ...,
        min_length=1,
        description="Approved corpus topic, e.g. microgravity_skeletal_muscle.",
    )
    organism_model: str = Field(
        ...,
        min_length=1,
        description="Organism or model system studied.",
    )
    exposure: str = Field(
        ...,
        min_length=1,
        description="Exposure or condition, e.g. spaceflight or hindlimb_unloading.",
    )
    selection_notes: str | None = Field(
        default=None,
        description="Curation notes explaining why the publication was selected.",
    )

    # Inclusion / exclusion checklist
    inclusion_pass: InclusionPass = Field(
        ...,
        description="Whether the publication passed the inclusion checklist.",
    )
    exclusion_flags: str = Field(
        default="none",
        min_length=1,
        description="Comma-separated exclusion flags or 'none'.",
    )

    # Ingest and approval state
    ingestion_status: IngestionStatus = Field(
        default="not_ingested",
        description="Current pipeline state for this publication.",
    )
    human_approval: HumanApproval = Field(
        default="pending",
        description="Owner approval state for the corpus row.",
    )

    @field_validator("pmcid", "journal", "selection_notes", "pdf_quality_notes", mode="before")
    @classmethod
    def _blank_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("pmid", "year", mode="before")
    @classmethod
    def _int_from_str(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None
            try:
                return int(value)
            except ValueError as exc:
                raise ValueError("must be an integer") from exc
        return value

    def license_can_ingest(self) -> bool:
        """Return whether the recorded license permits ingestion."""
        return classify_license(self.license).can_ingest


def load_inventory_manifest(path: Path | None = None) -> list[CorpusInventoryRecord]:
    """Load and validate the corpus manifest CSV.

    Args:
        path: Path to the manifest CSV. Defaults to the repo
            ``data/inventory/august_mvp_corpus_manifest.csv``.

    Returns:
        Validated list of inventory records.

    Raises:
        ValueError: if the file is missing or a row fails schema validation.
    """
    path = path or MANIFEST_PATH
    if not path.is_file():
        raise ValueError(f"manifest not found: {path}")

    records: list[CorpusInventoryRecord] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_number, raw_row in enumerate(reader, start=2):
            row: dict[str, Any] = dict(raw_row)
            try:
                records.append(CorpusInventoryRecord.model_validate(row))
            except ValueError as exc:
                raise ValueError(f"manifest row {row_number}: {exc}") from exc
    return records

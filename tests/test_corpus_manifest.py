"""Validate August MVP corpus manifest checklist fields."""

from __future__ import annotations

import csv
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = _ROOT.joinpath("data", "inventory", "august_mvp_corpus_manifest.csv")

REQUIRED = {
    "publication_id",
    "title",
    "doi",
    "source_url",
    "license",
    "license_status",
    "corpus_topic",
    "inclusion_pass",
    "exclusion_flags",
    "ingestion_status",
    "human_approval",
}

ALLOWED_LICENSE_PREFIXES = ("cc-by",)


def _normalized_license(value: str) -> str:
    return value.strip().lower().replace(" ", "-")


def test_manifest_exists_and_has_target_size() -> None:
    assert MANIFEST.is_file(), f"missing manifest: {MANIFEST}"
    with MANIFEST.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert 10 <= len(rows) <= 30, f"expected 10-30 rows for August MVP corpus, got {len(rows)}"


def test_manifest_rows_pass_inclusion_checklist() -> None:
    with MANIFEST.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows, "manifest is empty"
    assert REQUIRED.issubset(rows[0].keys())
    dois: set[str] = set()
    for row in rows:
        assert row["inclusion_pass"] == "yes"
        assert row["exclusion_flags"] == "none"
        assert row["corpus_topic"] == "microgravity_skeletal_muscle"
        license_id = _normalized_license(row["license"])
        assert license_id.startswith(ALLOWED_LICENSE_PREFIXES), license_id
        # Allowed: CC BY and CC BY-NC-ND (non-commercial educational/research engine).
        # Disallow unknown commercial-restrictive variants without BY.
        assert "cc-by" in license_id
        assert row["doi"]
        assert row["doi"] not in dois
        dois.add(row["doi"])
        assert row["source_url"].startswith("https://doi.org/")
        assert row["human_approval"] in {"pending", "approved", "rejected"}

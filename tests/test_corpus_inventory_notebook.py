"""Tests for the corpus inventory notebook helpers and smoke execution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from spacebio_evidence_engine.corpus import (
    load_inventory_manifest,
    load_inventory_review,
    summarize_inventory,
    write_inventory_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "inventory" / "august_mvp_corpus_manifest.csv"
NOTEBOOK = ROOT / "notebooks" / "corpus_inventory.ipynb"


def test_summarize_inventory_preserves_manifest_provenance_counts() -> None:
    records = load_inventory_manifest(MANIFEST)

    summary = summarize_inventory(records)

    assert summary.total_records == 23
    assert summary.approved_records == 23
    assert summary.included_records == 23
    assert summary.corpus_topics == ("microgravity_skeletal_muscle",)
    assert summary.license_counts == {"cc-by": 17, "cc-by-nc-nd": 6}
    assert summary.pdf_quality_counts["good"] == 22
    assert summary.pdf_quality_counts["missing"] == 1
    assert summary.ingestion_status_counts["pdf_quality_blocked"] == 1


def test_write_and_read_inventory_review_uses_approved_schema(tmp_path: Path) -> None:
    records = load_inventory_manifest(MANIFEST)[:3]
    review_path = tmp_path / "review.csv"

    write_inventory_manifest(records, review_path)
    round_trip = load_inventory_review(review_path)

    assert [record.publication_id for record in round_trip] == ["pub_001", "pub_002", "pub_003"]
    assert [record.source_url for record in round_trip] == [record.source_url for record in records]
    assert [record.license for record in round_trip] == [record.license for record in records]
    assert [record.human_approval for record in round_trip] == ["approved", "approved", "approved"]


def test_corpus_inventory_notebook_smoke_executes_on_fixture(
    tmp_path: Path,
    monkeypatch,
) -> None:
    fixture_manifest = tmp_path / "fixture_manifest.csv"
    output_manifest = tmp_path / "review_output.csv"
    fixture_records = load_inventory_manifest(MANIFEST)[:2]
    write_inventory_manifest(fixture_records, fixture_manifest)
    monkeypatch.chdir(ROOT)
    monkeypatch.setenv("SPACEBIO_INVENTORY_MANIFEST", str(fixture_manifest))
    monkeypatch.setenv("SPACEBIO_INVENTORY_REVIEW_OUTPUT", str(output_manifest))

    namespace: dict[str, Any] = {"__name__": "__notebook_smoke__"}
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        exec(compile(source, f"{NOTEBOOK}#cell-{index}", "exec"), namespace)

    round_trip = load_inventory_review(output_manifest)
    assert [record.publication_id for record in round_trip] == ["pub_001", "pub_002"]
    assert namespace["summary"].total_records == 2
    assert namespace["review_output_path"] == output_manifest

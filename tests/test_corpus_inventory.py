"""Corpus inventory schema tests (issue #21)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from spacebio_evidence_engine.corpus import (
    CorpusInventoryRecord,
    load_inventory_manifest,
)


def _example_record() -> dict[str, Any]:
    return {
        "publication_id": "pub_test",
        "title": "Test publication for inventory schema validation.",
        "doi": "10.1234/example.5678",
        "pmcid": "PMC12345678",
        "pmid": "12345678",
        "year": "2024",
        "journal": "Journal of Examples",
        "authors": "Author A, Author B.",
        "license": "cc-by",
        "license_status": "approved_oa_candidate",
        "access_restriction_notes": "Attribution required.",
        "redistribution_notes": "Passage quoting allowed with attribution.",
        "source_url": "https://doi.org/10.1234/example.5678",
        "pdf_url": "https://example.com/pdf.pdf",
        "fulltext_url": "https://example.com/fulltext",
        "pdf_quality": "good",
        "pdf_quality_notes": "page_count=10, text_chars=50000",
        "corpus_topic": "microgravity_skeletal_muscle",
        "organism_model": "human",
        "exposure": "spaceflight",
        "selection_notes": "Example record for schema validation.",
        "inclusion_pass": "yes",
        "exclusion_flags": "none",
        "ingestion_status": "not_ingested",
        "human_approval": "approved",
    }


def test_example_record_validates() -> None:
    record = CorpusInventoryRecord(**_example_record())
    assert record.publication_id == "pub_test"
    assert record.year == 2024
    assert record.pmid == 12345678
    assert record.doi == "10.1234/example.5678"
    assert record.license_can_ingest()


def test_example_record_optional_fields_can_be_blank() -> None:
    data = _example_record()
    data["pmcid"] = ""
    data["journal"] = "   "
    data["selection_notes"] = ""
    record = CorpusInventoryRecord(**data)
    assert record.pmcid is None
    assert record.journal is None
    assert record.selection_notes is None


def test_example_record_blank_int_fields_become_none() -> None:
    data = _example_record()
    data["pmid"] = ""
    record = CorpusInventoryRecord(**data)
    assert record.pmid is None


def test_required_field_missing_raises() -> None:
    data = _example_record()
    del data["title"]
    with pytest.raises(ValueError, match="title"):
        CorpusInventoryRecord(**data)


def test_invalid_doi_raises() -> None:
    data = _example_record()
    data["doi"] = "not-a-doi"
    with pytest.raises(ValueError, match="doi"):
        CorpusInventoryRecord(**data)


def test_invalid_source_url_raises() -> None:
    data = _example_record()
    data["source_url"] = "https://example.com/"
    with pytest.raises(ValueError, match="source_url"):
        CorpusInventoryRecord(**data)


def test_invalid_license_not_blocked_can_ingest() -> None:
    data = _example_record()
    data["license"] = "all-rights-reserved"
    record = CorpusInventoryRecord(**data)
    assert not record.license_can_ingest()


def test_load_inventory_manifest_returns_all_rows() -> None:
    records = load_inventory_manifest()
    assert len(records) == 23
    assert records[0].publication_id == "pub_001"
    assert all(r.inclusion_pass == "yes" for r in records)
    assert all(r.corpus_topic == "microgravity_skeletal_muscle" for r in records)


def test_load_inventory_manifest_default_path_is_repo_manifest() -> None:
    records = load_inventory_manifest()
    assert records[0].source_url.startswith("https://doi.org/")


def test_load_inventory_manifest_missing_file_raises() -> None:
    with pytest.raises(ValueError, match="manifest not found"):
        load_inventory_manifest(Path("/nonexistent/manifest.csv"))


def test_inventory_records_have_required_fields() -> None:
    records = load_inventory_manifest()
    for record in records:
        assert record.publication_id
        assert record.title
        assert record.doi.startswith("10.")
        assert record.source_url.startswith("https://doi.org/")
        assert record.license
        assert record.license_status
        assert record.access_restriction_notes
        assert record.redistribution_notes

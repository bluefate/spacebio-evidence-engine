"""Unit tests for ingestion error reporting (issue #36)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from spacebio_evidence_engine.ingestion import (
    FAILED_INGESTION_STATUS,
    IngestionStage,
    InMemoryIngestionErrorStore,
    create_ingestion_error_record,
    redact_error_payload,
)


def test_create_error_record_preserves_publication_stage_message_and_timestamp() -> None:
    timestamp = datetime(2026, 8, 12, 2, 30, tzinfo=UTC)

    record = create_ingestion_error_record(
        publication_id="pub_001",
        stage=IngestionStage.EXTRACT,
        message="PDF yielded no extractable skeletal muscle text",
        occurred_at=timestamp,
        error_type="PDFEmptyError",
        source_key="pub_001/source.pdf",
        details={"page_count": 2},
    )

    assert record.publication_id == "pub_001"
    assert record.stage is IngestionStage.EXTRACT
    assert record.message == "PDF yielded no extractable skeletal muscle text"
    assert record.occurred_at == timestamp
    assert record.error_type == "PDFEmptyError"
    assert record.source_key == "pub_001/source.pdf"
    assert record.details == {"page_count": "2"}
    assert record.error_id.startswith("ingerr_")


def test_record_creation_normalizes_naive_timestamps_to_utc() -> None:
    record = create_ingestion_error_record(
        publication_id="pub_002",
        stage="validate",
        message="missing required microgravity metadata",
        occurred_at=datetime(2026, 8, 12, 2, 30),
    )

    assert record.stage is IngestionStage.VALIDATE
    assert record.occurred_at.tzinfo is UTC


def test_error_payload_redacts_common_secret_shapes() -> None:
    payload = (
        "token=ghp_abcdefghijklmnopqrstuvwxyz and "
        "api_key=sk-1234567890abcdef and Authorization: Bearer abc.def.ghi"
    )

    redacted = redact_error_payload(payload)

    assert "ghp_" not in redacted
    assert "sk-" not in redacted
    assert "abc.def.ghi" not in redacted
    assert "[REDACTED]" in redacted


def test_secret_detail_keys_are_redacted_before_storage() -> None:
    record = create_ingestion_error_record(
        publication_id="pub_003",
        stage=IngestionStage.ACQUIRE,
        message="download failed",
        details={
            "api_token": "super-secret-token",
            "url": "https://example.org/paper.pdf?token=ghp_abcdefghijklmnopqrstuvwxyz",
        },
    )

    assert record.details["api_token"] == "[REDACTED]"
    assert "ghp_" not in record.details["url"]


def test_error_store_links_failed_status_to_latest_error() -> None:
    store = InMemoryIngestionErrorStore()
    first = store.record_error(
        publication_id="pub_004",
        stage=IngestionStage.EXTRACT,
        message="corrupt pdf",
        occurred_at=datetime(2026, 8, 12, 2, 30, tzinfo=UTC),
    )
    second = store.record_error(
        publication_id="pub_004",
        stage=IngestionStage.CHUNK,
        message="empty chunk output",
        occurred_at=datetime(2026, 8, 12, 2, 31, tzinfo=UTC),
    )

    status = store.failure_status_for_publication("pub_004")

    assert first.error_id != second.error_id
    assert status is not None
    assert status.publication_id == "pub_004"
    assert status.ingestion_status == FAILED_INGESTION_STATUS
    assert status.last_error_id == second.error_id
    assert status.last_error == second


def test_error_store_returns_none_when_publication_has_no_errors() -> None:
    store = InMemoryIngestionErrorStore()

    assert store.last_for_publication("missing") is None
    assert store.failure_status_for_publication("missing") is None


def test_invalid_stage_is_rejected() -> None:
    with pytest.raises(ValueError):
        create_ingestion_error_record(
            publication_id="pub_005",
            stage="not-a-stage",
            message="bad stage",
        )

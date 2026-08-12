"""Structured ingestion error reporting (issue #36).

Errors may include exception messages or operator notes from untrusted inputs.
Before storing, messages and detail values are passed through a small redaction
layer so common secret-bearing payloads are not retained.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from spacebio_evidence_engine.ingestion.status import FAILED_INGESTION_STATUS


class IngestionStage(StrEnum):
    """Known ingestion stages that can emit operator-visible errors."""

    ACQUIRE = "acquire"
    PDF_QUALITY = "pdf_quality"
    EXTRACT = "extract"
    SECTION = "section"
    CHUNK = "chunk"
    EMBED = "embed"
    INDEX = "index"
    VALIDATE = "validate"


_SECRET_VALUE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(sk-[A-Za-z0-9_-]{8,})\b"),
    re.compile(r"\b(gh[pousr]_[A-Za-z0-9_]{8,})\b"),
    re.compile(r"\b([A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,})\b"),
)
_SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(api[_-]?key|token|secret|password|authorization)\b"
    r"\s*[:=]\s*(bearer\s+)?([^\s,;]+)"
)
_SECRET_DETAIL_KEY_RE = re.compile(r"(?i)(api[_-]?key|token|secret|password|authorization)")
_REDACTED = "[REDACTED]"


@dataclass(frozen=True, slots=True)
class IngestionErrorRecord:
    """One sanitized ingestion failure record for a publication."""

    publication_id: str
    stage: IngestionStage
    message: str
    occurred_at: datetime
    error_id: str
    error_type: str | None = None
    source_key: str | None = None
    details: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class IngestionFailureStatus:
    """Failed ingestion status linked to the most recent error."""

    publication_id: str
    ingestion_status: str
    last_error_id: str
    last_error: IngestionErrorRecord


def redact_error_payload(value: object) -> str:
    """Return a string safe enough for local operator logs."""
    text = str(value)
    text = _SECRET_ASSIGNMENT_RE.sub(lambda match: f"{match.group(1)}={_REDACTED}", text)
    for pattern in _SECRET_VALUE_PATTERNS:
        text = pattern.sub(_REDACTED, text)
    return text


def create_ingestion_error_record(
    *,
    publication_id: str,
    stage: IngestionStage | str,
    message: object,
    occurred_at: datetime | None = None,
    error_type: str | None = None,
    source_key: str | None = None,
    details: Mapping[str, object] | None = None,
) -> IngestionErrorRecord:
    """Create a sanitized, timestamped ingestion error record."""
    parsed_stage = stage if isinstance(stage, IngestionStage) else IngestionStage(stage)
    timestamp = _normalize_timestamp(occurred_at or datetime.now(UTC))
    sanitized_details = _redact_details(details or {})
    sanitized_message = redact_error_payload(message)
    sanitized_source_key = redact_error_payload(source_key) if source_key is not None else None
    error_id = _make_error_id(
        publication_id=publication_id,
        stage=parsed_stage,
        message=sanitized_message,
        occurred_at=timestamp,
    )
    return IngestionErrorRecord(
        publication_id=publication_id,
        stage=parsed_stage,
        message=sanitized_message,
        occurred_at=timestamp,
        error_id=error_id,
        error_type=redact_error_payload(error_type) if error_type is not None else None,
        source_key=sanitized_source_key,
        details=sanitized_details,
    )


class InMemoryIngestionErrorStore:
    """Small process-local store for ingestion error reporting.

    This is intentionally not a database repository. Issue #34 owns durable
    ingestion status transitions; this store provides deterministic behavior and
    a stable interface for unit tests and local operators.
    """

    def __init__(self) -> None:
        self._records: list[IngestionErrorRecord] = []

    def append(self, record: IngestionErrorRecord) -> IngestionErrorRecord:
        """Store an already-created error record."""
        self._records.append(record)
        return record

    def record_error(
        self,
        *,
        publication_id: str,
        stage: IngestionStage | str,
        message: object,
        occurred_at: datetime | None = None,
        error_type: str | None = None,
        source_key: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> IngestionErrorRecord:
        """Create, sanitize, and store one ingestion error."""
        record = create_ingestion_error_record(
            publication_id=publication_id,
            stage=stage,
            message=message,
            occurred_at=occurred_at,
            error_type=error_type,
            source_key=source_key,
            details=details,
        )
        return self.append(record)

    def list_for_publication(self, publication_id: str) -> tuple[IngestionErrorRecord, ...]:
        """Return stored errors for one publication in insertion order."""
        return tuple(record for record in self._records if record.publication_id == publication_id)

    def last_for_publication(self, publication_id: str) -> IngestionErrorRecord | None:
        """Return the most recent stored error for one publication."""
        for record in reversed(self._records):
            if record.publication_id == publication_id:
                return record
        return None

    def failure_status_for_publication(
        self,
        publication_id: str,
    ) -> IngestionFailureStatus | None:
        """Return a failed status linked to the publication's latest error."""
        last_error = self.last_for_publication(publication_id)
        if last_error is None:
            return None
        return IngestionFailureStatus(
            publication_id=publication_id,
            ingestion_status=FAILED_INGESTION_STATUS,
            last_error_id=last_error.error_id,
            last_error=last_error,
        )


def _redact_details(details: Mapping[str, object]) -> Mapping[str, str]:
    sanitized: dict[str, str] = {}
    for key, value in details.items():
        text_key = str(key)
        if _SECRET_DETAIL_KEY_RE.search(text_key):
            sanitized[text_key] = _REDACTED
        else:
            sanitized[text_key] = redact_error_payload(value)
    return sanitized


def _normalize_timestamp(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _make_error_id(
    *,
    publication_id: str,
    stage: IngestionStage,
    message: str,
    occurred_at: datetime,
) -> str:
    payload = f"{publication_id}|{stage.value}|{occurred_at.isoformat()}|{message}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
    return f"ingerr_{digest}"

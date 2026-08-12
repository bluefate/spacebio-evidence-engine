"""Per-publication ingestion status tracking (issue #34).

Persists an explicit status enum on ``publications.ingestion_status`` and records
every transition (structured log + in-process event history) so operators can
audit how a publication moved through the pipeline.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import TypedDict

from sqlalchemy.orm import Session

from spacebio_evidence_engine.db.models import Publication

logger = logging.getLogger(__name__)


class IngestionStatus(StrEnum):
    """Persisted ingestion states for a publication.

    ``not_ingested`` is the schema default (never started). ``pending`` means
    queued for work. ``pdf_quality_blocked`` is a terminal quality-gate state
    used by PDF assessment (#25).
    """

    NOT_INGESTED = "not_ingested"
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PDF_QUALITY_BLOCKED = "pdf_quality_blocked"


FAILED_INGESTION_STATUS = IngestionStatus.FAILED.value

ALLOWED_INGESTION_TRANSITIONS: Mapping[IngestionStatus, frozenset[IngestionStatus]] = {
    IngestionStatus.NOT_INGESTED: frozenset(
        {
            IngestionStatus.PENDING,
            IngestionStatus.PROCESSING,
            IngestionStatus.PDF_QUALITY_BLOCKED,
            IngestionStatus.FAILED,
        }
    ),
    IngestionStatus.PENDING: frozenset(
        {
            IngestionStatus.PROCESSING,
            IngestionStatus.PDF_QUALITY_BLOCKED,
            IngestionStatus.FAILED,
            IngestionStatus.NOT_INGESTED,
        }
    ),
    IngestionStatus.PROCESSING: frozenset(
        {
            IngestionStatus.SUCCEEDED,
            IngestionStatus.FAILED,
            IngestionStatus.PDF_QUALITY_BLOCKED,
        }
    ),
    IngestionStatus.SUCCEEDED: frozenset(
        {
            IngestionStatus.PENDING,
            IngestionStatus.PROCESSING,
            IngestionStatus.FAILED,
        }
    ),
    IngestionStatus.FAILED: frozenset(
        {
            IngestionStatus.PENDING,
            IngestionStatus.PROCESSING,
            IngestionStatus.NOT_INGESTED,
        }
    ),
    IngestionStatus.PDF_QUALITY_BLOCKED: frozenset(
        {
            IngestionStatus.PENDING,
            IngestionStatus.PROCESSING,
            IngestionStatus.NOT_INGESTED,
        }
    ),
}


class InvalidIngestionStatusTransitionError(ValueError):
    """Raised when a status transition is not allowed."""


@dataclass(frozen=True, slots=True)
class IngestionStatusTransition:
    """One explicit, logged ingestion status change."""

    publication_id: str
    from_status: IngestionStatus
    to_status: IngestionStatus
    reason: str
    occurred_at: datetime
    actor: str | None = None


@dataclass
class IngestionStatusEventLog:
    """Process-local transition history for tests and local operators."""

    events: list[IngestionStatusTransition] = field(default_factory=list)

    def record(self, event: IngestionStatusTransition) -> None:
        self.events.append(event)

    def for_publication(self, publication_id: str) -> tuple[IngestionStatusTransition, ...]:
        return tuple(event for event in self.events if event.publication_id == publication_id)

    def clear(self) -> None:
        self.events.clear()


DEFAULT_STATUS_EVENT_LOG = IngestionStatusEventLog()


class IngestionStatusTransitionView(TypedDict):
    from_status: str
    to_status: str
    reason: str
    occurred_at: str
    actor: str | None


class IngestionStatusSnapshot(TypedDict):
    publication_id: str
    ingestion_status: str
    allowed_next_statuses: list[str]
    recent_transitions: list[IngestionStatusTransitionView]


def parse_ingestion_status(value: IngestionStatus | str) -> IngestionStatus:
    """Parse a persisted status string into ``IngestionStatus``."""

    if isinstance(value, IngestionStatus):
        return value
    try:
        return IngestionStatus(value)
    except ValueError as exc:
        allowed = ", ".join(status.value for status in IngestionStatus)
        raise ValueError(f"unknown ingestion status {value!r}; allowed: {allowed}") from exc


def can_transition_ingestion_status(
    current: IngestionStatus | str,
    new_status: IngestionStatus | str,
) -> bool:
    """Return whether ``current -> new_status`` is an allowed transition."""

    from_status = parse_ingestion_status(current)
    to_status = parse_ingestion_status(new_status)
    if from_status == to_status:
        return True
    return to_status in ALLOWED_INGESTION_TRANSITIONS[from_status]


def transition_ingestion_status(
    session: Session,
    publication_id: str,
    new_status: IngestionStatus | str,
    *,
    reason: str,
    actor: str | None = None,
    event_log: IngestionStatusEventLog | None = None,
    occurred_at: datetime | None = None,
) -> IngestionStatusTransition:
    """Persist an explicit status transition and log it.

    Same-status updates are allowed (no-op persist) but still emit a logged
    event so operators can see repeated status reports.
    """

    if not reason.strip():
        raise ValueError("reason must be a non-empty string")

    publication = session.get(Publication, publication_id)
    if publication is None:
        raise LookupError(f"publication not found: {publication_id}")

    from_status = parse_ingestion_status(publication.ingestion_status)
    to_status = parse_ingestion_status(new_status)
    if not can_transition_ingestion_status(from_status, to_status):
        raise InvalidIngestionStatusTransitionError(
            f"invalid ingestion status transition for {publication_id}: "
            f"{from_status.value} -> {to_status.value}"
        )

    timestamp = occurred_at or datetime.now(UTC)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)

    publication.ingestion_status = to_status.value
    session.add(publication)
    session.flush()

    event = IngestionStatusTransition(
        publication_id=publication_id,
        from_status=from_status,
        to_status=to_status,
        reason=reason.strip(),
        occurred_at=timestamp,
        actor=actor,
    )
    (event_log or DEFAULT_STATUS_EVENT_LOG).record(event)
    logger.info(
        "ingestion_status_transition publication_id=%s from=%s to=%s reason=%s actor=%s",
        publication_id,
        from_status.value,
        to_status.value,
        event.reason,
        actor or "",
    )
    return event


def get_ingestion_status(
    session: Session,
    publication_id: str,
) -> IngestionStatus:
    """Return the persisted ingestion status for a publication ID."""

    publication = session.get(Publication, publication_id)
    if publication is None:
        raise LookupError(f"publication not found: {publication_id}")
    return parse_ingestion_status(publication.ingestion_status)


def describe_ingestion_status(
    session: Session,
    publication_id: str,
    *,
    event_log: IngestionStatusEventLog | None = None,
) -> IngestionStatusSnapshot:
    """Return a JSON-serializable status snapshot for CLI/API display."""

    status = get_ingestion_status(session, publication_id)
    log = event_log or DEFAULT_STATUS_EVENT_LOG
    events = log.for_publication(publication_id)
    return {
        "publication_id": publication_id,
        "ingestion_status": status.value,
        "allowed_next_statuses": sorted(
            candidate.value for candidate in ALLOWED_INGESTION_TRANSITIONS[status]
        ),
        "recent_transitions": [
            {
                "from_status": event.from_status.value,
                "to_status": event.to_status.value,
                "reason": event.reason,
                "occurred_at": event.occurred_at.isoformat(),
                "actor": event.actor,
            }
            for event in events[-10:]
        ],
    }


def allowed_next_statuses(current: IngestionStatus | str) -> tuple[IngestionStatus, ...]:
    """Return allowed destination statuses for ``current`` (excluding self)."""

    status = parse_ingestion_status(current)
    return tuple(sorted(ALLOWED_INGESTION_TRANSITIONS[status], key=lambda item: item.value))

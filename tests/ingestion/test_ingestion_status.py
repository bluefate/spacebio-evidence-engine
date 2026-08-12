"""Unit tests for ingestion status transitions (issue #34)."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from spacebio_evidence_engine.db.base import Base
from spacebio_evidence_engine.db.models import Publication
from spacebio_evidence_engine.ingestion import (
    IngestionStatus,
    IngestionStatusEventLog,
    InvalidIngestionStatusTransitionError,
    can_transition_ingestion_status,
    describe_ingestion_status,
    get_ingestion_status,
    parse_ingestion_status,
    transition_ingestion_status,
)


@pytest.fixture()
def session(tmp_path: Path) -> Iterator[Session]:
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'ingestion_status.sqlite3'}")
    Base.metadata.create_all(engine)
    with Session(engine) as db_session:
        yield db_session


def _add_publication(session: Session, publication_id: str = "pub_status") -> Publication:
    publication = Publication(
        publication_id=publication_id,
        title="Status tracking paper",
        source_url="https://doi.org/10.0/status",
        license_status="approved_oa_candidate",
        corpus_topic="microgravity_skeletal_muscle",
        ingestion_status=IngestionStatus.NOT_INGESTED.value,
    )
    session.add(publication)
    session.commit()
    return publication


def test_parse_ingestion_status_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="unknown ingestion status"):
        parse_ingestion_status("weird")


def test_valid_and_invalid_transitions() -> None:
    assert can_transition_ingestion_status(IngestionStatus.NOT_INGESTED, IngestionStatus.PROCESSING)
    assert can_transition_ingestion_status(IngestionStatus.PROCESSING, IngestionStatus.SUCCEEDED)
    assert not can_transition_ingestion_status(
        IngestionStatus.NOT_INGESTED, IngestionStatus.SUCCEEDED
    )
    assert not can_transition_ingestion_status(
        IngestionStatus.SUCCEEDED, IngestionStatus.PDF_QUALITY_BLOCKED
    )


def test_transition_persists_and_logs(session: Session) -> None:
    _add_publication(session)
    event_log = IngestionStatusEventLog()

    event = transition_ingestion_status(
        session,
        "pub_status",
        IngestionStatus.PROCESSING,
        reason="operator started ingest",
        actor="test",
        event_log=event_log,
    )
    session.commit()

    assert event.from_status is IngestionStatus.NOT_INGESTED
    assert event.to_status is IngestionStatus.PROCESSING
    assert get_ingestion_status(session, "pub_status") is IngestionStatus.PROCESSING
    assert len(event_log.for_publication("pub_status")) == 1

    snapshot = describe_ingestion_status(session, "pub_status", event_log=event_log)
    assert snapshot["ingestion_status"] == "processing"
    assert "succeeded" in snapshot["allowed_next_statuses"]
    assert snapshot["recent_transitions"][0]["reason"] == "operator started ingest"


def test_invalid_transition_raises_and_does_not_persist(session: Session) -> None:
    _add_publication(session)
    event_log = IngestionStatusEventLog()

    with pytest.raises(InvalidIngestionStatusTransitionError, match="invalid ingestion status"):
        transition_ingestion_status(
            session,
            "pub_status",
            IngestionStatus.SUCCEEDED,
            reason="skip processing",
            event_log=event_log,
        )

    assert get_ingestion_status(session, "pub_status") is IngestionStatus.NOT_INGESTED
    assert event_log.for_publication("pub_status") == ()


def test_missing_publication_raises(session: Session) -> None:
    with pytest.raises(LookupError, match="publication not found"):
        get_ingestion_status(session, "missing")

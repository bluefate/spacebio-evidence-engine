"""Publication reprocessing workflow (issue #35).

Re-extracts and re-chunks a publication that already has a stored PDF. By
default the old chunk set is deleted only after a successful new extraction,
so a failed reprocess leaves the previous chunks in place.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import StrEnum

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from spacebio_evidence_engine.db.models import Chunk, ChunkEmbedding, Publication
from spacebio_evidence_engine.ingestion.chunking import ChunkingResult, TextChunk, chunk_extraction
from spacebio_evidence_engine.ingestion.error_reporting import (
    IngestionErrorRecord,
    IngestionStage,
    InMemoryIngestionErrorStore,
    create_ingestion_error_record,
)
from spacebio_evidence_engine.ingestion.errors import PDFExtractionError
from spacebio_evidence_engine.ingestion.extract import ExtractionResult, extract_pdf_from_storage
from spacebio_evidence_engine.ingestion.status import (
    IngestionStatus,
    IngestionStatusEventLog,
    transition_ingestion_status,
)
from spacebio_evidence_engine.storage.base import PDFStorage


class ReprocessStrategy(StrEnum):
    """Supported reprocessing strategies."""

    REPLACE = "replace"
    ARCHIVE = "archive"


@dataclass(frozen=True, slots=True)
class ReprocessResult:
    """Outcome of one publication reprocessing run."""

    publication_id: str
    status: IngestionStatus
    previous_chunk_count: int
    new_chunk_count: int
    error_record: IngestionErrorRecord | None = None


class ReprocessError(RuntimeError):
    """Raised when a reprocessing precondition is violated."""


class UnsupportedReprocessStrategyError(ReprocessError):
    """Raised when the requested reprocessing strategy is not implemented."""


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _persist_chunks(session: Session, chunks: tuple[TextChunk, ...]) -> None:
    for chunk in chunks:
        session.add(
            Chunk(
                chunk_id=chunk.chunk_id,
                publication_id=chunk.publication_id,
                section=chunk.section.value,
                chunk_text=chunk.chunk_text,
                content_hash=_hash(chunk.chunk_text),
                start_offset=chunk.start_offset,
                end_offset=chunk.end_offset,
                chunking_strategy_version=chunk.chunking_strategy_version,
                page_start=chunk.start_page,
                page_end=chunk.end_page,
                section_heading=chunk.section_heading,
            )
        )


def _chunk_count(session: Session, publication_id: str) -> int:
    return (
        session.execute(
            select(func.count(Chunk.chunk_id)).where(Chunk.publication_id == publication_id)
        ).scalar()
        or 0
    )


def _delete_publication_chunks(session: Session, publication_id: str) -> None:
    """Delete embeddings then chunks for a publication.

    ``ChunkEmbedding`` has a ``CASCADE`` foreign key to ``Chunk``, but deleting
    embeddings first is dialect-robust for tests and avoids relying on DB-level
    cascade being enabled in every SQLite setup.
    """
    chunk_ids = (
        session.execute(select(Chunk.chunk_id).where(Chunk.publication_id == publication_id))
        .scalars()
        .all()
    )
    if chunk_ids:
        session.execute(delete(ChunkEmbedding).where(ChunkEmbedding.chunk_id.in_(chunk_ids)))
    session.execute(delete(Chunk).where(Chunk.publication_id == publication_id))
    session.flush()


def reprocess_publication(
    session: Session,
    publication_id: str,
    *,
    storage: PDFStorage,
    strategy: ReprocessStrategy = ReprocessStrategy.REPLACE,
    actor: str | None = None,
    event_log: IngestionStatusEventLog | None = None,
    error_store: InMemoryIngestionErrorStore | None = None,
) -> ReprocessResult:
    """Re-extract and re-chunk a publication, replacing the previous chunk set.

    The new extraction and chunking are computed before any old data is removed,
    so an extraction failure leaves the previous chunks intact. After a
    successful reprocess, the old ``Chunk`` and ``ChunkEmbedding`` rows are
    deleted and the new ``Chunk`` rows are inserted.

    Supported strategy:

    - ``REPLACE``: delete old chunks and write the new set (default).
    - ``ARCHIVE``: not implemented in the August MVP; raises
      ``UnsupportedReprocessStrategyError``.

    Returns a ``ReprocessResult`` with the previous and new chunk counts.
    """
    if strategy != ReprocessStrategy.REPLACE:
        raise UnsupportedReprocessStrategyError(
            f"reprocessing strategy {strategy!r} is not implemented; use 'replace'"
        )

    publication = session.get(Publication, publication_id)
    if publication is None:
        raise LookupError(f"publication not found: {publication_id}")
    if not publication.pdf_path:
        raise ReprocessError(
            f"publication {publication_id} has no stored PDF; reprocessing requires pdf_path"
        )

    previous_count = _chunk_count(session, publication_id)

    transition_ingestion_status(
        session,
        publication_id,
        IngestionStatus.PROCESSING,
        reason="reprocessing started",
        actor=actor,
        event_log=event_log,
    )

    extraction: ExtractionResult
    chunking: ChunkingResult
    try:
        extraction = extract_pdf_from_storage(storage, publication.pdf_path)
        chunking = chunk_extraction(extraction, publication_id=publication_id)
    except PDFExtractionError as exc:
        record = create_ingestion_error_record(
            publication_id=publication_id,
            stage=IngestionStage.EXTRACT,
            message=str(exc),
            error_type=type(exc).__name__,
            source_key=publication.pdf_path,
        )
        if error_store is not None:
            error_store.append(record)
        transition_ingestion_status(
            session,
            publication_id,
            IngestionStatus.FAILED,
            reason=f"reprocessing extraction failed: {record.error_id}",
            actor=actor,
            event_log=event_log,
        )
        return ReprocessResult(
            publication_id=publication_id,
            status=IngestionStatus.FAILED,
            previous_chunk_count=previous_count,
            new_chunk_count=0,
            error_record=record,
        )

    _delete_publication_chunks(session, publication_id)
    _persist_chunks(session, chunking.chunks)
    session.flush()

    transition_ingestion_status(
        session,
        publication_id,
        IngestionStatus.SUCCEEDED,
        reason="reprocessing succeeded",
        actor=actor,
        event_log=event_log,
    )
    session.commit()

    return ReprocessResult(
        publication_id=publication_id,
        status=IngestionStatus.SUCCEEDED,
        previous_chunk_count=previous_count,
        new_chunk_count=len(chunking.chunks),
    )

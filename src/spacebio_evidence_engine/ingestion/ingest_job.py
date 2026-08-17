"""Local corpus ingest: PDF on disk → chunks → embeddings (issue #163).

Does not download PDFs. Operators place files under ``PDF_STORAGE_LOCAL_ROOT``
(default ``data/pdfs``) as ``{publication_id}.pdf`` or
``{publication_id}/*.pdf``. Missing files are skipped with a recorded failure
detail; text is never invented.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from spacebio_evidence_engine.corpus.inventory import (
    CorpusInventoryRecord,
    load_inventory_manifest,
)
from spacebio_evidence_engine.db.models import Chunk, ChunkEmbedding, Publication
from spacebio_evidence_engine.embeddings import EmbeddingProvider
from spacebio_evidence_engine.indexing import index_chunk_embeddings
from spacebio_evidence_engine.ingestion.error_reporting import (
    IngestionStage,
    InMemoryIngestionErrorStore,
    create_ingestion_error_record,
)
from spacebio_evidence_engine.ingestion.reprocess import reprocess_publication
from spacebio_evidence_engine.ingestion.status import IngestionStatus, transition_ingestion_status
from spacebio_evidence_engine.storage.local import LocalFileStorage

IngestOutcome = Literal["ingested", "skipped_missing_pdf", "skipped_blocked", "failed"]


@dataclass(frozen=True, slots=True)
class PublicationIngestResult:
    """Outcome of ingesting one inventory publication."""

    publication_id: str
    outcome: IngestOutcome
    chunk_count: int
    embedded_count: int
    message: str | None = None


@dataclass(frozen=True, slots=True)
class CorpusIngestResult:
    """Summary of one ``ingest_local_corpus`` run."""

    results: tuple[PublicationIngestResult, ...]

    @property
    def ingested_count(self) -> int:
        return sum(1 for item in self.results if item.outcome == "ingested")

    @property
    def skipped_count(self) -> int:
        return sum(1 for item in self.results if item.outcome.startswith("skipped_"))

    @property
    def failed_count(self) -> int:
        return sum(1 for item in self.results if item.outcome == "failed")


def find_local_pdf(pdf_root: Path, publication_id: str) -> Path | None:
    """Return a PDF path for ``publication_id`` if one exists under ``pdf_root``."""

    root = pdf_root.expanduser().resolve()
    direct = root / f"{publication_id}.pdf"
    if direct.is_file():
        return direct
    nested = root / publication_id
    if nested.is_dir():
        matches = sorted(path for path in nested.glob("*.pdf") if path.is_file())
        if matches:
            return matches[0]
    return None


def upsert_publication_from_inventory(
    session: Session, record: CorpusInventoryRecord
) -> Publication:
    """Insert or update bibliographic fields from the inventory row.

    Does not overwrite ``ingestion_status`` on existing rows.
    """

    pmid = str(record.pmid) if record.pmid is not None else None
    publication = session.get(Publication, record.publication_id)
    if publication is None:
        publication = Publication(
            publication_id=record.publication_id,
            title=record.title,
            source_url=record.source_url,
            license_status=record.license_status,
            corpus_topic=record.corpus_topic,
            ingestion_status=IngestionStatus.NOT_INGESTED.value,
            doi=record.doi,
            pmcid=record.pmcid,
            pmid=pmid,
            year=record.year,
            journal=record.journal,
            authors=record.authors,
            license=record.license,
            pdf_url=record.pdf_url,
            fulltext_url=record.fulltext_url,
            organism_model=record.organism_model,
            exposure=record.exposure,
            selection_notes=record.selection_notes,
            human_approval=record.human_approval,
        )
        session.add(publication)
    else:
        publication.title = record.title
        publication.source_url = record.source_url
        publication.license_status = record.license_status
        publication.corpus_topic = record.corpus_topic
        publication.doi = record.doi
        publication.pmcid = record.pmcid
        publication.pmid = pmid
        publication.year = record.year
        publication.journal = record.journal
        publication.authors = record.authors
        publication.license = record.license
        publication.pdf_url = record.pdf_url
        publication.fulltext_url = record.fulltext_url
        publication.organism_model = record.organism_model
        publication.exposure = record.exposure
        publication.selection_notes = record.selection_notes
        publication.human_approval = record.human_approval
        session.add(publication)
    session.flush()
    return publication


def ingest_local_corpus(
    session: Session,
    *,
    pdf_root: Path,
    storage: LocalFileStorage | None = None,
    manifest_path: Path | None = None,
    publication_ids: Sequence[str] | None = None,
    embedding_provider: EmbeddingProvider | None = None,
    error_store: InMemoryIngestionErrorStore | None = None,
    actor: str = "ingest_job",
    include_quality_blocked: bool = False,
) -> CorpusIngestResult:
    """Register inventory rows, ingest local PDFs, optionally embed chunks."""

    store = storage or LocalFileStorage(pdf_root)
    records = load_inventory_manifest(manifest_path)
    wanted = {item.strip() for item in publication_ids} if publication_ids else None
    if wanted is not None:
        records = [record for record in records if record.publication_id in wanted]

    results: list[PublicationIngestResult] = []
    for record in records:
        results.append(
            _ingest_one(
                session,
                record,
                pdf_root=pdf_root,
                storage=store,
                embedding_provider=embedding_provider,
                error_store=error_store,
                actor=actor,
                include_quality_blocked=include_quality_blocked,
            )
        )
    return CorpusIngestResult(results=tuple(results))


def _ingest_one(
    session: Session,
    record: CorpusInventoryRecord,
    *,
    pdf_root: Path,
    storage: LocalFileStorage,
    embedding_provider: EmbeddingProvider | None,
    error_store: InMemoryIngestionErrorStore | None,
    actor: str,
    include_quality_blocked: bool,
) -> PublicationIngestResult:
    publication_id = record.publication_id
    if record.human_approval != "approved":
        return PublicationIngestResult(
            publication_id=publication_id,
            outcome="skipped_blocked",
            chunk_count=0,
            embedded_count=0,
            message="human_approval is not approved",
        )
    if record.ingestion_status == "pdf_quality_blocked" and not include_quality_blocked:
        return PublicationIngestResult(
            publication_id=publication_id,
            outcome="skipped_blocked",
            chunk_count=0,
            embedded_count=0,
            message="inventory marks pdf_quality_blocked",
        )

    publication = upsert_publication_from_inventory(session, record)
    pdf_path = find_local_pdf(pdf_root, publication_id)
    if pdf_path is None and publication.pdf_path and storage.exists(publication.pdf_path):
        key = publication.pdf_path
    elif pdf_path is not None:
        key = storage.put(publication_id, pdf_path.name, pdf_path.read_bytes())
        publication.pdf_path = key
        session.add(publication)
        session.flush()
    else:
        record_error = create_ingestion_error_record(
            publication_id=publication_id,
            stage=IngestionStage.EXTRACT,
            message=f"no PDF at {pdf_root / f'{publication_id}.pdf'}",
            error_type="MissingPDF",
        )
        if error_store is not None:
            error_store.append(record_error)
        if publication.ingestion_status == IngestionStatus.NOT_INGESTED.value:
            transition_ingestion_status(
                session,
                publication_id,
                IngestionStatus.FAILED,
                reason=f"missing local PDF: {record_error.error_id}",
                actor=actor,
            )
        session.commit()
        return PublicationIngestResult(
            publication_id=publication_id,
            outcome="skipped_missing_pdf",
            chunk_count=0,
            embedded_count=0,
            message=record_error.message,
        )

    reprocess = reprocess_publication(
        session,
        publication_id,
        storage=storage,
        actor=actor,
        error_store=error_store,
    )
    if reprocess.status is IngestionStatus.FAILED:
        return PublicationIngestResult(
            publication_id=publication_id,
            outcome="failed",
            chunk_count=0,
            embedded_count=0,
            message=reprocess.error_record.message if reprocess.error_record else "extract failed",
        )

    if embedding_provider is not None:
        index_chunk_embeddings(session, embedding_provider)
        session.commit()
    embedded = _embedding_count(session, publication_id)

    return PublicationIngestResult(
        publication_id=publication_id,
        outcome="ingested",
        chunk_count=reprocess.new_chunk_count,
        embedded_count=embedded,
        message=None,
    )


def _embedding_count(session: Session, publication_id: str) -> int:
    return (
        session.execute(
            select(func.count(ChunkEmbedding.chunk_id))
            .select_from(ChunkEmbedding)
            .join(Chunk, Chunk.chunk_id == ChunkEmbedding.chunk_id)
            .where(Chunk.publication_id == publication_id)
        ).scalar()
        or 0
    )

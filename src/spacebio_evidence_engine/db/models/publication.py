"""Publication persistence model (issue #27).

Chunk table is issue #33 (`Chunk`). Passage and embedding tables remain later.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from spacebio_evidence_engine.db.base import Base


class Publication(Base):
    """Controlled-corpus publication metadata and ingest state."""

    __tablename__ = "publications"
    __table_args__ = (
        Index("ix_publications_corpus_topic", "corpus_topic"),
        Index("ix_publications_ingestion_status", "ingestion_status"),
        Index("ix_publications_license_status", "license_status"),
        Index("ix_publications_doi", "doi"),
    )

    publication_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    license_status: Mapped[str] = mapped_column(String(64), nullable=False)
    corpus_topic: Mapped[str] = mapped_column(String(128), nullable=False)
    ingestion_status: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        server_default="not_ingested",
    )

    # Identifiers and bibliographic fields
    doi: Mapped[str | None] = mapped_column(String(256), nullable=True)
    pmcid: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pmid: Mapped[str | None] = mapped_column(String(64), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    journal: Mapped[str | None] = mapped_column(Text, nullable=True)
    authors: Mapped[str | None] = mapped_column(Text, nullable=True)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    nasa_repository_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # License and local/remote paths
    license: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pdf_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    pdf_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    fulltext_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Free-text August MVP filters (controlled vocab deferred)
    organism_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    exposure: Mapped[str | None] = mapped_column(String(128), nullable=True)
    selection_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    human_approval: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default="pending",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"Publication(publication_id={self.publication_id!r}, doi={self.doi!r})"

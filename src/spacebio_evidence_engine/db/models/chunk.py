"""Chunk persistence model (issue #33).

Stores retrieval chunks produced by section-aware chunking (#32). Embedding
vectors and passage tables remain follow-on work.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from spacebio_evidence_engine.db.base import Base


class Chunk(Base):
    """A retrieval unit with provenance relative to a publication."""

    __tablename__ = "chunks"
    __table_args__ = (
        Index("ix_chunks_publication_id", "publication_id"),
        Index("ix_chunks_section", "section"),
        Index("ix_chunks_content_hash", "content_hash"),
        Index("ix_chunks_chunking_strategy_version", "chunking_strategy_version"),
    )

    chunk_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    publication_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("publications.publication_id", ondelete="RESTRICT"),
        nullable=False,
    )
    section: Mapped[str] = mapped_column(String(64), nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    start_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    end_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    chunking_strategy_version: Mapped[str] = mapped_column(String(32), nullable=False)

    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Reserved until a passages table exists; store JSON array text or leave null.
    passage_ids: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Filled when embeddings are written (#40/#43); null until then.
    embedding_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    section_heading: Mapped[str | None] = mapped_column(Text, nullable=True)

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

    publication = relationship("Publication", backref="chunks")

    def __repr__(self) -> str:
        return (
            f"Chunk(chunk_id={self.chunk_id!r}, publication_id={self.publication_id!r}, "
            f"section={self.section!r})"
        )

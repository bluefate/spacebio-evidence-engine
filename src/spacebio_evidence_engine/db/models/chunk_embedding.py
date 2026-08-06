"""Chunk embedding vector storage (issue #42).

One row per chunk. MVP dimension is fixed at 384 (local MiniLM). Search /
indexing APIs are follow-on (#43 / #44).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from spacebio_evidence_engine.db.base import Base
from spacebio_evidence_engine.db.vector_types import (
    MVP_EMBEDDING_DIMENSION,
    EmbeddingVector,
)


class ChunkEmbedding(Base):
    """pgvector embedding linked 1:1 to a retrieval chunk."""

    __tablename__ = "chunk_embeddings"
    __table_args__ = (
        CheckConstraint(
            f"dimension = {MVP_EMBEDDING_DIMENSION}",
            name="ck_chunk_embeddings_dimension_mvp",
        ),
        Index("ix_chunk_embeddings_model_name", "model_name"),
    )

    chunk_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("chunks.chunk_id", ondelete="CASCADE"),
        primary_key=True,
    )
    embedding: Mapped[list[float]] = mapped_column(
        EmbeddingVector(MVP_EMBEDDING_DIMENSION),
        nullable=False,
    )
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    dimension: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=str(MVP_EMBEDDING_DIMENSION),
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

    chunk = relationship("Chunk", backref="embedding_row")

    def __repr__(self) -> str:
        return (
            f"ChunkEmbedding(chunk_id={self.chunk_id!r}, model_name={self.model_name!r}, "
            f"dimension={self.dimension!r})"
        )

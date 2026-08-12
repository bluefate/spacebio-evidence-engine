"""Index chunk embeddings with a configured provider (issue #43)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from spacebio_evidence_engine.db.models import Chunk, ChunkEmbedding
from spacebio_evidence_engine.db.vector_types import MVP_EMBEDDING_DIMENSION
from spacebio_evidence_engine.embeddings import EmbeddingProvider

IndexStatus = Literal["completed", "nothing_to_index"]


@dataclass(frozen=True)
class ChunkEmbeddingIndexResult:
    """Progress summary for a chunk embedding indexing run."""

    status: IndexStatus
    scanned_chunks: int
    embedded_chunks: int
    skipped_chunks: int
    updated_chunks: int
    model_name: str
    dimension: int
    chunk_ids: tuple[str, ...] = field(default_factory=tuple)


def index_chunk_embeddings(
    session: Session,
    provider: EmbeddingProvider,
    *,
    batch_size: int = 32,
    reindex: bool = False,
    limit: int | None = None,
) -> ChunkEmbeddingIndexResult:
    """Embed chunks and persist vectors.

    By default the job is idempotent for a given provider model: chunks that
    already have an embedding row for ``provider.model_name`` are skipped.
    Default mode does **not** detect ``chunk_text`` / ``content_hash`` changes;
    after re-chunking, call with ``reindex=True`` (or change models) so vectors
    are rewritten.

    Set ``reindex=True`` to force-embed every selected chunk with the current
    provider, regardless of any prior ``model_name`` on the embedding row.
    """

    _validate_provider(provider)
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")
    if limit is not None and limit < 1:
        raise ValueError("limit must be at least 1 when provided")

    candidates, scanned, skipped = _select_candidates(
        session, provider, reindex=reindex, limit=limit
    )
    if not candidates:
        return ChunkEmbeddingIndexResult(
            status="nothing_to_index",
            scanned_chunks=scanned,
            embedded_chunks=0,
            skipped_chunks=skipped,
            updated_chunks=0,
            model_name=provider.model_name,
            dimension=provider.dimension,
        )

    embedded = 0
    updated = 0
    chunk_ids: list[str] = []
    for start in range(0, len(candidates), batch_size):
        batch = candidates[start : start + batch_size]
        vectors = provider.embed_documents([chunk.chunk_text for chunk in batch])
        if len(vectors) != len(batch):
            raise ValueError(
                f"provider returned {len(vectors)} vectors for {len(batch)} input chunks"
            )

        for chunk, vector in zip(batch, vectors, strict=True):
            _validate_vector(vector, provider)
            existing = session.get(ChunkEmbedding, chunk.chunk_id)
            if existing is None:
                session.add(
                    ChunkEmbedding(
                        chunk_id=chunk.chunk_id,
                        embedding=vector,
                        model_name=provider.model_name,
                        dimension=provider.dimension,
                    )
                )
            else:
                existing.embedding = vector
                existing.model_name = provider.model_name
                existing.dimension = provider.dimension
                updated += 1
            chunk.embedding_model = provider.model_name
            embedded += 1
            chunk_ids.append(chunk.chunk_id)

    session.flush()
    return ChunkEmbeddingIndexResult(
        status="completed",
        scanned_chunks=scanned,
        embedded_chunks=embedded,
        skipped_chunks=skipped,
        updated_chunks=updated,
        model_name=provider.model_name,
        dimension=provider.dimension,
        chunk_ids=tuple(chunk_ids),
    )


def _select_candidates(
    session: Session,
    provider: EmbeddingProvider,
    *,
    reindex: bool,
    limit: int | None,
) -> tuple[list[Chunk], int, int]:
    """Return (chunks_to_embed, scanned_count, skipped_count)."""

    query = select(Chunk).order_by(Chunk.chunk_id)
    if limit is not None:
        query = query.limit(limit)

    chunks = list(session.scalars(query))
    scanned = len(chunks)
    if reindex:
        return chunks, scanned, 0

    candidates: list[Chunk] = []
    skipped = 0
    for chunk in chunks:
        existing = session.get(ChunkEmbedding, chunk.chunk_id)
        if existing is not None and existing.model_name == provider.model_name:
            skipped += 1
            continue
        candidates.append(chunk)
    return candidates, scanned, skipped


def _validate_provider(provider: EmbeddingProvider) -> None:
    if provider.dimension != MVP_EMBEDDING_DIMENSION:
        raise ValueError(
            f"provider dimension {provider.dimension} does not match "
            f"MVP dimension {MVP_EMBEDDING_DIMENSION}"
        )


def _validate_vector(vector: list[float], provider: EmbeddingProvider) -> None:
    if len(vector) != provider.dimension:
        raise ValueError(
            f"provider returned vector length {len(vector)} for dimension {provider.dimension}"
        )

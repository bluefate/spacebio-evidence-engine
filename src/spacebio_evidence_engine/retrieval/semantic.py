"""Semantic vector search over chunk embeddings (issue #44)."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from spacebio_evidence_engine.db.models import Chunk, ChunkEmbedding, Publication
from spacebio_evidence_engine.db.vector_types import MVP_EMBEDDING_DIMENSION
from spacebio_evidence_engine.embeddings import EmbeddingProvider
from spacebio_evidence_engine.retrieval.filters import (
    RetrievalFilters,
    apply_retrieval_filters,
    parse_retrieval_filters,
)

DEFAULT_TOP_K = 8


@dataclass(frozen=True)
class SemanticSearchHit:
    """One ranked chunk with score and provenance for citation wiring."""

    chunk_id: str
    score: float
    publication_id: str
    title: str
    section: str
    chunk_text: str
    source_url: str
    page_start: int | None
    page_end: int | None
    section_heading: str | None
    model_name: str


def semantic_search(
    session: Session,
    provider: EmbeddingProvider,
    query: str,
    *,
    k: int = DEFAULT_TOP_K,
    filters: RetrievalFilters | Mapping[str, Any] | None = None,
) -> list[SemanticSearchHit]:
    """Return top-k chunks by cosine similarity to the query embedding.

    Always restricts to ``chunk_embeddings.model_name == provider.model_name``
    so vectors from other models are never compared. Optional metadata filters
    are validated via ``parse_retrieval_filters`` (#47). No LLM generation.
    """

    if not query.strip():
        raise ValueError("query must be a non-empty string")
    if k < 1:
        raise ValueError("k must be at least 1")
    _validate_provider(provider)
    parsed_filters = parse_retrieval_filters(filters)

    query_vector = provider.embed_query(query)
    _validate_vector(query_vector, provider)

    bind = session.get_bind()
    dialect_name = bind.dialect.name if bind is not None else ""
    if dialect_name == "postgresql":
        return _search_pgvector(
            session,
            provider=provider,
            query_vector=query_vector,
            k=k,
            filters=parsed_filters,
        )
    return _search_python(
        session,
        provider=provider,
        query_vector=query_vector,
        k=k,
        filters=parsed_filters,
    )


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Cosine similarity in ``[-1, 1]`` (higher is more similar)."""

    if len(left) != len(right):
        raise ValueError(f"vector length mismatch: {len(left)} vs {len(right)}")
    dot = 0.0
    left_norm_sq = 0.0
    right_norm_sq = 0.0
    for a, b in zip(left, right, strict=True):
        dot += a * b
        left_norm_sq += a * a
        right_norm_sq += b * b
    if left_norm_sq == 0.0 or right_norm_sq == 0.0:
        return 0.0
    return dot / (math.sqrt(left_norm_sq) * math.sqrt(right_norm_sq))


def _search_python(
    session: Session,
    *,
    provider: EmbeddingProvider,
    query_vector: list[float],
    k: int,
    filters: RetrievalFilters | None,
) -> list[SemanticSearchHit]:
    rows = list(session.execute(_candidate_query(provider, filters)))
    scored: list[tuple[float, Chunk, Publication, ChunkEmbedding]] = []
    for chunk, publication, embedding_row in rows:
        score = cosine_similarity(query_vector, list(embedding_row.embedding))
        scored.append((score, chunk, publication, embedding_row))
    scored.sort(key=lambda item: (-item[0], item[1].chunk_id))
    return [
        _to_hit(chunk, publication, embedding_row, score)
        for score, chunk, publication, embedding_row in scored[:k]
    ]


def _search_pgvector(
    session: Session,
    *,
    provider: EmbeddingProvider,
    query_vector: list[float],
    k: int,
    filters: RetrievalFilters | None,
) -> list[SemanticSearchHit]:
    """Rank with pgvector cosine distance (``<=>``); score = 1 - distance."""

    from pgvector.sqlalchemy import Vector
    from sqlalchemy import bindparam

    distance = ChunkEmbedding.embedding.op("<=>")(
        bindparam("query_vector", value=query_vector, type_=Vector(MVP_EMBEDDING_DIMENSION))
    )
    stmt = (
        _candidate_query(provider, filters)
        .add_columns(distance.label("distance"))
        .order_by(distance)
        .limit(k)
    )
    hits: list[SemanticSearchHit] = []
    for chunk, publication, embedding_row, distance_value in session.execute(stmt):
        score = 1.0 - float(distance_value)
        hits.append(_to_hit(chunk, publication, embedding_row, score))
    return hits


def _candidate_query(
    provider: EmbeddingProvider,
    filters: RetrievalFilters | None,
) -> Select[tuple[Chunk, Publication, ChunkEmbedding]]:
    stmt = (
        select(Chunk, Publication, ChunkEmbedding)
        .join(ChunkEmbedding, ChunkEmbedding.chunk_id == Chunk.chunk_id)
        .join(Publication, Publication.publication_id == Chunk.publication_id)
        .where(ChunkEmbedding.model_name == provider.model_name)
    )
    return apply_retrieval_filters(stmt, filters)


def _to_hit(
    chunk: Chunk,
    publication: Publication,
    embedding_row: ChunkEmbedding,
    score: float,
) -> SemanticSearchHit:
    return SemanticSearchHit(
        chunk_id=chunk.chunk_id,
        score=score,
        publication_id=publication.publication_id,
        title=publication.title,
        section=chunk.section,
        chunk_text=chunk.chunk_text,
        source_url=publication.source_url,
        page_start=chunk.page_start,
        page_end=chunk.page_end,
        section_heading=chunk.section_heading,
        model_name=embedding_row.model_name,
    )


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

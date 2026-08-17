"""Hybrid retrieval combining semantic vector and full-text search (issue #46).

Implements reciprocal rank fusion (RRF) over ranked results from each enabled
channel. Each channel contributes up to ``channel_k`` candidates; the final
list is the top ``k`` chunks by fused RRF score.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from typing import Any, Literal

from sqlalchemy.orm import Session

from spacebio_evidence_engine.embeddings import EmbeddingProvider
from spacebio_evidence_engine.retrieval.filters import (
    InvalidRetrievalFilterError,
    RetrievalFilters,
    parse_retrieval_filters,
)
from spacebio_evidence_engine.retrieval.fts import (
    DEFAULT_SEARCH_CONFIG,
    KeywordSearchHit,
    keyword_search,
)
from spacebio_evidence_engine.retrieval.semantic import (
    DEFAULT_TOP_K,
    SemanticSearchHit,
    semantic_search,
)

RRF_K = 60
"""Reciprocal rank fusion constant. Higher values reduce the boost for top ranks."""

RetrievalChannel = Literal["semantic", "fts"]


def _keyword_to_semantic(hit: KeywordSearchHit) -> SemanticSearchHit:
    """Create a SemanticSearchHit from a keyword hit so both channels share one output type."""
    return SemanticSearchHit(
        chunk_id=hit.chunk_id,
        score=0.0,
        publication_id=hit.publication_id,
        title=hit.title,
        section=hit.section,
        chunk_text=hit.chunk_text,
        source_url=hit.source_url,
        page_start=hit.page_start,
        page_end=hit.page_end,
        section_heading=hit.section_heading,
        model_name=f"fts:{hit.search_config}",
    )


def hybrid_search(
    session: Session,
    provider: EmbeddingProvider,
    query: str,
    *,
    k: int = DEFAULT_TOP_K,
    filters: RetrievalFilters | Mapping[str, Any] | None = None,
    channels: tuple[RetrievalChannel, ...] = ("semantic",),
    search_config: str = DEFAULT_SEARCH_CONFIG,
) -> list[SemanticSearchHit]:
    """Retrieve chunks by fusing semantic and/or full-text search rankings.

    When both channels are requested, Reciprocal Rank Fusion (RRF) combines
    independent rankings:

        rrf_score = sum(1 / (RRF_K + rank))

    The same metadata filters are applied to every channel. The returned
    ``SemanticSearchHit`` uses the fused RRF score. ``model_name`` is the
    embedding model for semantic-only results, or ``fts:<config>`` for
    keyword-only results; mixed results keep the semantic hit's embedding model.
    """
    if not channels:
        raise ValueError("channels must include at least one retrieval channel")
    unknown = sorted({channel for channel in channels if channel not in {"semantic", "fts"}})
    if unknown:
        raise ValueError(f"unknown retrieval channel(s): {', '.join(unknown)}")

    if not query.strip():
        raise ValueError("query must be a non-empty string")
    if k < 1:
        raise ValueError("k must be at least 1")

    parsed = parse_retrieval_filters(filters)
    channel_k = max(k, 20)

    # chunk_id -> (hit, list of ranks from each channel)
    by_chunk: dict[str, tuple[SemanticSearchHit, list[int]]] = {}

    if "semantic" in channels:
        for rank, hit in enumerate(
            semantic_search(
                session,
                provider,
                query,
                k=channel_k,
                filters=parsed,
            ),
            start=1,
        ):
            by_chunk[hit.chunk_id] = (hit, [rank])

    if "fts" in channels:
        try:
            keyword_hits = keyword_search(
                session,
                query,
                k=channel_k,
                filters=parsed,
                search_config=search_config,
            )
        except ValueError:
            # SQLite fallback raises when a query has no searchable terms.
            # The semantic channel still provides results in that case.
            keyword_hits = []
        for rank, hit in enumerate(keyword_hits, start=1):
            if hit.chunk_id in by_chunk:
                existing_hit, ranks = by_chunk[hit.chunk_id]
                ranks.append(rank)
            else:
                by_chunk[hit.chunk_id] = (_keyword_to_semantic(hit), [rank])

    if not by_chunk:
        return []

    fused: list[tuple[float, str, SemanticSearchHit]] = []
    for chunk_id, (hit, ranks) in by_chunk.items():
        score = sum(1.0 / (RRF_K + rank) for rank in ranks)
        fused.append((score, chunk_id, hit))

    fused.sort(key=lambda item: (-item[0], item[1]))
    return [replace(hit, score=score) for score, _, hit in fused[:k]]


__all__ = [
    "InvalidRetrievalFilterError",
    "RetrievalChannel",
    "RetrievalFilters",
    "hybrid_search",
]

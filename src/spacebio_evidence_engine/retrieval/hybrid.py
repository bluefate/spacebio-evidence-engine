"""Hybrid retrieval entrypoint with shared metadata filters (issue #47).

Full FTS fusion scoring remains #45/#46. This module applies the documented
filter API across enabled channels so hybrid callers share one filter contract
with semantic search.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from sqlalchemy.orm import Session

from spacebio_evidence_engine.embeddings import EmbeddingProvider
from spacebio_evidence_engine.retrieval.filters import (
    InvalidRetrievalFilterError,
    RetrievalFilters,
    parse_retrieval_filters,
)
from spacebio_evidence_engine.retrieval.semantic import (
    DEFAULT_TOP_K,
    SemanticSearchHit,
    semantic_search,
)

RetrievalChannel = Literal["semantic", "fts"]


def hybrid_search(
    session: Session,
    provider: EmbeddingProvider,
    query: str,
    *,
    k: int = DEFAULT_TOP_K,
    filters: RetrievalFilters | Mapping[str, Any] | None = None,
    channels: tuple[RetrievalChannel, ...] = ("semantic",),
) -> list[SemanticSearchHit]:
    """Retrieve chunks with optional metadata filters across hybrid channels.

    Today only the ``semantic`` channel is implemented. Requesting ``fts``
    raises ``NotImplementedError`` until PostgreSQL full-text search (#45) and
    fusion (#46) land. Filters are validated and applied before ranking.
    """

    if not channels:
        raise ValueError("channels must include at least one retrieval channel")
    unknown = sorted({channel for channel in channels if channel not in {"semantic", "fts"}})
    if unknown:
        raise ValueError(f"unknown retrieval channel(s): {', '.join(unknown)}")

    parsed = parse_retrieval_filters(filters)

    if "fts" in channels:
        raise NotImplementedError(
            "FTS hybrid channel is not implemented yet (issues #45/#46); "
            "use channels=('semantic',) or omit channels"
        )
    if "semantic" not in channels:
        raise ValueError("no implemented retrieval channel enabled")

    return semantic_search(session, provider, query, k=k, filters=parsed)


__all__ = [
    "InvalidRetrievalFilterError",
    "RetrievalChannel",
    "RetrievalFilters",
    "hybrid_search",
]

"""Optional retrieval reranking (issue #48).

Rerankers reorder already-retrieved chunks. They do not fetch from the
database and do not generate answers. Default production path leaves
reranking disabled.
"""

from __future__ import annotations

import os
import re
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import replace

from spacebio_evidence_engine.retrieval.semantic import SemanticSearchHit

_TOKEN = re.compile(r"[a-z0-9]+")
_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off", ""}

LEXICAL_OVERLAP = "lexical_overlap"
NOOP = "noop"


class ChunkReranker(ABC):
    """Provider-agnostic rerank contract for retrieved chunks."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable algorithm id recorded in logs and docs."""

    @abstractmethod
    def rerank(
        self,
        query: str,
        hits: Sequence[SemanticSearchHit],
        *,
        top_k: int | None = None,
    ) -> list[SemanticSearchHit]:
        """Return hits ordered by this reranker, optionally truncated to ``top_k``."""


class NoOpReranker(ChunkReranker):
    """Pass-through reranker (same order as the retrieval stage)."""

    @property
    def name(self) -> str:
        return NOOP

    def rerank(
        self,
        query: str,
        hits: Sequence[SemanticSearchHit],
        *,
        top_k: int | None = None,
    ) -> list[SemanticSearchHit]:
        del query
        selected = list(hits)
        if top_k is not None:
            if top_k < 1:
                raise ValueError("top_k must be at least 1")
            selected = selected[:top_k]
        return selected


class LexicalOverlapReranker(ChunkReranker):
    """Local lexical reranker: query-term coverage of ``chunk_text``.

    Tokens are lowercase alphanumeric runs of length >= 2. The rerank score is
    ``|query_tokens ∩ chunk_tokens| / |query_tokens|`` (0 when the query has no
    tokens). Ties keep earlier retrieval order, then ``chunk_id``.
    """

    @property
    def name(self) -> str:
        return LEXICAL_OVERLAP

    def rerank(
        self,
        query: str,
        hits: Sequence[SemanticSearchHit],
        *,
        top_k: int | None = None,
    ) -> list[SemanticSearchHit]:
        if top_k is not None and top_k < 1:
            raise ValueError("top_k must be at least 1")
        query_tokens = _tokens(query)
        scored: list[tuple[float, int, str, SemanticSearchHit]] = []
        for index, hit in enumerate(hits):
            overlap = 0.0
            if query_tokens:
                chunk_tokens = _tokens(hit.chunk_text)
                overlap = len(query_tokens & chunk_tokens) / len(query_tokens)
            scored.append((overlap, index, hit.chunk_id, hit))
        scored.sort(key=lambda item: (-item[0], item[1], item[2]))
        ordered = [replace(hit, score=overlap) for overlap, _, _, hit in scored]
        if top_k is not None:
            ordered = ordered[:top_k]
        return ordered


def reranker_from_env(
    *,
    enabled: bool | None = None,
    name: str | None = None,
) -> ChunkReranker | None:
    """Return a reranker when enabled; ``None`` means skip reranking.

    Environment:

    - ``SPACEBIO_RERANK_ENABLED`` — default false
    - ``SPACEBIO_RERANKER`` — ``lexical_overlap`` (default when enabled) or ``noop``
    """

    if enabled is None:
        raw = os.environ.get("SPACEBIO_RERANK_ENABLED", "").strip().lower()
        enabled = raw in _TRUE_VALUES
    if not enabled:
        return None
    algorithm = (name or os.environ.get("SPACEBIO_RERANKER") or LEXICAL_OVERLAP).strip().lower()
    if algorithm in _FALSE_VALUES:
        algorithm = LEXICAL_OVERLAP
    if algorithm == LEXICAL_OVERLAP:
        return LexicalOverlapReranker()
    if algorithm == NOOP:
        return NoOpReranker()
    raise ValueError(f"unknown reranker: {algorithm}")


def _tokens(text: str) -> set[str]:
    return {token for token in _TOKEN.findall(text.lower()) if len(token) >= 2}


__all__ = [
    "LEXICAL_OVERLAP",
    "NOOP",
    "ChunkReranker",
    "LexicalOverlapReranker",
    "NoOpReranker",
    "reranker_from_env",
]

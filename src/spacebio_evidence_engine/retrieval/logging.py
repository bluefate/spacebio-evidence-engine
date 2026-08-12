"""Structured retrieval logging helpers."""

from __future__ import annotations

import hashlib
import logging
import os
from dataclasses import dataclass
from typing import Any

from spacebio_evidence_engine.retrieval.filters import RetrievalFilters
from spacebio_evidence_engine.retrieval.semantic import SemanticSearchHit

LOGGER_NAME = "spacebio_evidence_engine.retrieval"
SEMANTIC_SEARCH_ALGORITHM = "semantic_vector"
SEMANTIC_SCORE_KIND = "cosine_similarity"
RETRIEVAL_LOG_EVENT = "retrieval.semantic_search"

_TRUE_VALUES = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class RetrievalLogHit:
    """One selected chunk in a retrieval log record."""

    rank: int
    chunk_id: str
    score: float
    publication_id: str
    section: str
    page_start: int | None
    page_end: int | None
    source_url: str
    embedding_model: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "chunk_id": self.chunk_id,
            "score": self.score,
            "publication_id": self.publication_id,
            "section": self.section,
            "page_start": self.page_start,
            "page_end": self.page_end,
            "source_url": self.source_url,
            "embedding_model": self.embedding_model,
        }


@dataclass(frozen=True)
class RetrievalLogRecord:
    """Structured retrieval log payload without raw user query text."""

    event: str
    query_sha256: str
    query_length: int
    top_k: int
    filters: dict[str, str | int]
    search_algorithm: str
    score_kind: str
    embedding_model: str
    embedding_dimension: int
    result_count: int
    selected_chunks: tuple[RetrievalLogHit, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "event": self.event,
            "query_sha256": self.query_sha256,
            "query_length": self.query_length,
            "top_k": self.top_k,
            "filters": self.filters,
            "search_algorithm": self.search_algorithm,
            "score_kind": self.score_kind,
            "embedding_model": self.embedding_model,
            "embedding_dimension": self.embedding_dimension,
            "result_count": self.result_count,
            "selected_chunks": [hit.to_dict() for hit in self.selected_chunks],
        }


def verbose_retrieval_logging_enabled() -> bool:
    """Return whether verbose retrieval logs are enabled by environment."""

    return os.environ.get("SPACEBIO_RETRIEVAL_VERBOSE_LOGS", "").lower() in _TRUE_VALUES


def retrieval_logging_enabled() -> bool:
    """Return whether structured retrieval logs are enabled by environment."""

    value = os.environ.get("SPACEBIO_RETRIEVAL_LOGGING_ENABLED")
    if value is None:
        return True
    return value.lower() in _TRUE_VALUES


def make_retrieval_log_record(
    *,
    query: str,
    top_k: int,
    filters: RetrievalFilters | None,
    hits: list[SemanticSearchHit],
    embedding_model: str,
    embedding_dimension: int,
) -> RetrievalLogRecord:
    """Build the structured semantic retrieval log payload."""

    selected_chunks = tuple(
        RetrievalLogHit(
            rank=index,
            chunk_id=hit.chunk_id,
            score=hit.score,
            publication_id=hit.publication_id,
            section=hit.section,
            page_start=hit.page_start,
            page_end=hit.page_end,
            source_url=hit.source_url,
            embedding_model=hit.model_name,
        )
        for index, hit in enumerate(hits, start=1)
    )
    return RetrievalLogRecord(
        event=RETRIEVAL_LOG_EVENT,
        query_sha256=hashlib.sha256(query.strip().encode("utf-8")).hexdigest(),
        query_length=len(query.strip()),
        top_k=top_k,
        filters=_filters_to_dict(filters),
        search_algorithm=SEMANTIC_SEARCH_ALGORITHM,
        score_kind=SEMANTIC_SCORE_KIND,
        embedding_model=embedding_model,
        embedding_dimension=embedding_dimension,
        result_count=len(hits),
        selected_chunks=selected_chunks,
    )


def log_semantic_retrieval(
    *,
    query: str,
    top_k: int,
    filters: RetrievalFilters | None,
    hits: list[SemanticSearchHit],
    embedding_model: str,
    embedding_dimension: int,
    enabled: bool | None = None,
    verbose: bool | None = None,
    logger: logging.Logger | None = None,
) -> RetrievalLogRecord | None:
    """Emit a structured semantic retrieval log record when enabled."""

    if enabled is None:
        enabled = retrieval_logging_enabled()
    if not enabled:
        return None

    record = make_retrieval_log_record(
        query=query,
        top_k=top_k,
        filters=filters,
        hits=hits,
        embedding_model=embedding_model,
        embedding_dimension=embedding_dimension,
    )
    target_logger = logger or logging.getLogger(LOGGER_NAME)
    verbose_enabled = verbose if verbose is not None else verbose_retrieval_logging_enabled()
    level = logging.DEBUG if verbose_enabled else logging.INFO
    target_logger.log(
        level,
        "semantic retrieval selected %s chunks",
        record.result_count,
        extra={"retrieval": record.to_dict()},
    )
    return record


def _filters_to_dict(filters: RetrievalFilters | None) -> dict[str, str | int]:
    if filters is None:
        return {}
    return filters.active_items()

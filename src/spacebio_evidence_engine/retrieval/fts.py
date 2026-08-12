"""PostgreSQL full-text keyword search over chunk text (issue #45)."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from spacebio_evidence_engine.db.models import Chunk, Publication
from spacebio_evidence_engine.retrieval.filters import (
    RetrievalFilters,
    apply_retrieval_filters,
    parse_retrieval_filters,
)

DEFAULT_TOP_K = 8
DEFAULT_SEARCH_CONFIG = "english"


@dataclass(frozen=True)
class KeywordSearchHit:
    """One ranked chunk from a keyword search, with provenance for citations."""

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
    search_config: str


def keyword_search(
    session: Session,
    query: str,
    *,
    k: int = DEFAULT_TOP_K,
    filters: RetrievalFilters | Mapping[str, Any] | None = None,
    search_config: str = DEFAULT_SEARCH_CONFIG,
) -> list[KeywordSearchHit]:
    """Return top-k chunks matching ``query`` via PostgreSQL full-text search.

    Works without embeddings. Optional metadata filters are validated via
    ``parse_retrieval_filters`` (#47). On non-PostgreSQL dialects (e.g. SQLite
    CI) a substring fallback ranks by term overlap.
    """

    if not query.strip():
        raise ValueError("query must be a non-empty string")
    if k < 1:
        raise ValueError("k must be at least 1")

    parsed_filters = parse_retrieval_filters(filters)

    bind = session.get_bind()
    dialect_name = bind.dialect.name if bind is not None else ""
    if dialect_name == "postgresql":
        return _search_postgresql(session, query, k, parsed_filters, search_config)
    return _search_sqlite_fallback(session, query, k, parsed_filters, search_config)


def _search_postgresql(
    session: Session,
    query: str,
    k: int,
    filters: RetrievalFilters | None,
    search_config: str,
) -> list[KeywordSearchHit]:
    """Rank by ``ts_rank_cd`` over a generated ``tsvector`` column + GIN index."""

    tsquery = func.plainto_tsquery(search_config, query)
    rank = func.ts_rank_cd(Chunk.search_tsv, tsquery).label("rank")
    match = Chunk.search_tsv.op("@@")(tsquery)

    stmt: Select[Any] = (
        select(Chunk, Publication, rank)
        .join(Publication, Publication.publication_id == Chunk.publication_id)
        .where(match)
    )
    stmt = apply_retrieval_filters(stmt, filters)
    stmt = stmt.order_by(rank.desc(), Chunk.chunk_id).limit(k)

    hits: list[KeywordSearchHit] = []
    for chunk, publication, rank_value in session.execute(stmt):
        hits.append(_to_hit(chunk, publication, float(rank_value), search_config))
    return hits


def _search_sqlite_fallback(
    session: Session,
    query: str,
    k: int,
    filters: RetrievalFilters | None,
    search_config: str,
) -> list[KeywordSearchHit]:
    """Fallback ranking for SQLite CI: count distinct matching terms."""

    terms = _search_terms(query)
    if not terms:
        raise ValueError("query must contain searchable terms")

    term_predicates = [func.lower(Chunk.chunk_text).like(f"%{term}%") for term in terms]
    stmt: Select[Any] = (
        select(Chunk, Publication)
        .join(Publication, Publication.publication_id == Chunk.publication_id)
        .where(or_(*term_predicates))
    )
    stmt = apply_retrieval_filters(stmt, filters)

    scored: list[tuple[float, Chunk, Publication]] = []
    for chunk, publication in session.execute(stmt):
        text = chunk.chunk_text.lower()
        matches = sum(1 for term in terms if term in text)
        if matches == 0:
            continue
        score = matches / len(terms)
        scored.append((score, chunk, publication))

    scored.sort(key=lambda item: (-item[0], item[1].chunk_id))
    return [
        _to_hit(chunk, publication, score, search_config)
        for score, chunk, publication in scored[:k]
    ]


def _search_terms(query: str) -> list[str]:
    """Normalize a query into lower-case search terms for fallback ranking."""

    terms = [term for term in re.findall(r"[\w-]+", query.lower()) if term]
    return list(dict.fromkeys(terms))


def _to_hit(
    chunk: Chunk,
    publication: Publication,
    score: float,
    search_config: str,
) -> KeywordSearchHit:
    return KeywordSearchHit(
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
        search_config=search_config,
    )

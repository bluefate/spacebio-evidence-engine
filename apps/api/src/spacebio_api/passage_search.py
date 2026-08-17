"""Passage search for the web Search page (issue #167).

Kept separate from Ask wiring (#164) so ingest-backed search can land in parallel.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol

from pydantic import BaseModel, Field
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from spacebio_api.config import Settings
from spacebio_evidence_engine.db.models import ChunkEmbedding
from spacebio_evidence_engine.embeddings import EmbeddingProvider, LocalEmbeddingProvider
from spacebio_evidence_engine.retrieval import DEFAULT_TOP_K, SemanticSearchHit, semantic_search


class PassageRetriever(Protocol):
    """Retrieve ranked chunks for GET /search."""

    def __call__(
        self, query: str, *, top_k: int = DEFAULT_TOP_K
    ) -> Sequence[SemanticSearchHit]: ...


class PassageSearchItem(BaseModel):
    """One indexed passage for the Search UI."""

    kind: str = "passage"
    chunk_id: str
    publication_id: str
    title: str
    section: str
    page_start: int | None
    page_end: int | None
    source_url: str
    excerpt: str


class IndexedSearchResponse(BaseModel):
    """API payload for GET /search."""

    query: str
    source: str = Field(description="inventory_only or indexed")
    passages: list[PassageSearchItem]


def hit_to_item(hit: SemanticSearchHit) -> PassageSearchItem:
    excerpt = hit.chunk_text.strip()
    if len(excerpt) > 600:
        excerpt = excerpt[:597] + "..."
    return PassageSearchItem(
        chunk_id=hit.chunk_id,
        publication_id=hit.publication_id,
        title=hit.title,
        section=hit.section,
        page_start=hit.page_start,
        page_end=hit.page_end,
        source_url=hit.source_url,
        excerpt=excerpt,
    )


def embeddings_exist(session: Session, model_name: str) -> bool:
    count = session.execute(
        select(func.count(ChunkEmbedding.chunk_id)).where(ChunkEmbedding.model_name == model_name)
    ).scalar()
    return bool(count)


def search_indexed_passages(
    session: Session,
    provider: EmbeddingProvider,
    query: str,
    *,
    k: int = DEFAULT_TOP_K,
) -> IndexedSearchResponse:
    """Return indexed passages, or inventory_only when no vectors exist."""

    trimmed = query.strip()
    if not trimmed:
        return IndexedSearchResponse(query="", source="inventory_only", passages=[])
    if not embeddings_exist(session, provider.model_name):
        return IndexedSearchResponse(query=trimmed, source="inventory_only", passages=[])
    hits = semantic_search(session, provider, trimmed, k=k)
    return IndexedSearchResponse(
        query=trimmed,
        source="indexed",
        passages=[hit_to_item(hit) for hit in hits],
    )


def build_default_passage_retriever(settings: Settings) -> PassageRetriever | None:
    """Open a DB session + local MiniLM retriever, or None if extra missing."""

    try:
        provider: EmbeddingProvider = LocalEmbeddingProvider(model_name=settings.embedding_model)
    except ImportError:
        return None

    engine = create_engine(settings.database_url)

    def _retrieve(query: str, *, top_k: int = DEFAULT_TOP_K) -> Sequence[SemanticSearchHit]:
        with Session(engine) as session:
            if not embeddings_exist(session, provider.model_name):
                return ()
            return semantic_search(session, provider, query, k=top_k)

    return _retrieve


def indexed_response_from_hits(query: str, hits: Sequence[SemanticSearchHit]) -> dict[str, Any]:
    trimmed = query.strip()
    if not hits:
        return IndexedSearchResponse(
            query=trimmed, source="inventory_only", passages=[]
        ).model_dump()
    return IndexedSearchResponse(
        query=trimmed,
        source="indexed",
        passages=[hit_to_item(hit) for hit in hits],
    ).model_dump()

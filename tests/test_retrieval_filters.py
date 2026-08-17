"""Tests for retrieval metadata filters and hybrid filter wiring (issue #47)."""

from __future__ import annotations

import hashlib
import os
from collections.abc import Iterator, Sequence
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from spacebio_evidence_engine.db.models import Chunk, ChunkEmbedding, Publication
from spacebio_evidence_engine.db.vector_types import MVP_EMBEDDING_DIMENSION
from spacebio_evidence_engine.embeddings import EmbeddingProvider
from spacebio_evidence_engine.retrieval import (
    InvalidRetrievalFilterError,
    RetrievalFilters,
    hybrid_search,
    parse_retrieval_filters,
    semantic_search,
)

ROOT = Path(__file__).resolve().parents[1]


class FixtureEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        *,
        model_name: str = "fixture-filter-v1",
        dimension: int = MVP_EMBEDDING_DIMENSION,
        query_vectors: dict[str, list[float]] | None = None,
    ) -> None:
        self._model_name = model_name
        self._dimension = dimension
        self._query_vectors = query_vectors or {}

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [_axis_vector(index=0) for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return list(self._query_vectors[text])


def _alembic_config(database_url: str) -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", database_url)
    os.environ["DATABASE_URL"] = database_url
    return cfg


def _content_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _axis_vector(*, index: int) -> list[float]:
    vector = [0.0] * MVP_EMBEDDING_DIMENSION
    vector[index] = 1.0
    return vector


@pytest.fixture()
def session(tmp_path: Path) -> Iterator[Session]:
    db_path = tmp_path / "retrieval_filters.sqlite3"
    database_url = f"sqlite+pysqlite:///{db_path}"
    command.upgrade(_alembic_config(database_url), "head")
    engine = create_engine(database_url)
    with Session(engine) as db_session:
        yield db_session


def _seed(session: Session) -> None:
    session.add_all(
        [
            Publication(
                publication_id="pub_muscle",
                title="Muscle paper",
                source_url="https://doi.org/10.0/muscle",
                license_status="approved_oa_candidate",
                corpus_topic="microgravity_skeletal_muscle",
                organism_model="rodent",
                exposure="microgravity",
                year=2020,
                human_approval="approved",
            ),
            Publication(
                publication_id="pub_other",
                title="Other paper",
                source_url="https://doi.org/10.0/other",
                license_status="review_needed",
                corpus_topic="plant_biology",
                organism_model="arabidopsis",
                exposure="radiation",
                year=2018,
                human_approval="pending",
            ),
        ]
    )
    for chunk_id, publication_id, section, body, axis in (
        ("chk_muscle", "pub_muscle", "results", "Soleus atrophy in flight.", 0),
        ("chk_other", "pub_other", "methods", "Leaf morphology notes.", 1),
    ):
        session.add(
            Chunk(
                chunk_id=chunk_id,
                publication_id=publication_id,
                section=section,
                chunk_text=body,
                content_hash=_content_hash(body),
                start_offset=0,
                end_offset=len(body),
                chunking_strategy_version="1.0.0",
                embedding_model="fixture-filter-v1",
            )
        )
        session.add(
            ChunkEmbedding(
                chunk_id=chunk_id,
                embedding=_axis_vector(index=axis),
                model_name="fixture-filter-v1",
                dimension=MVP_EMBEDDING_DIMENSION,
            )
        )
    session.commit()


def test_parse_retrieval_filters_rejects_unknown_keys() -> None:
    with pytest.raises(InvalidRetrievalFilterError, match="unknown retrieval filter key"):
        parse_retrieval_filters({"organism": "rodent"})


def test_parse_retrieval_filters_rejects_blank_strings() -> None:
    with pytest.raises(InvalidRetrievalFilterError, match="non-empty string"):
        parse_retrieval_filters({"section": "  "})


def test_parse_retrieval_filters_rejects_invalid_year() -> None:
    with pytest.raises(InvalidRetrievalFilterError, match="year filter must be >= 1"):
        parse_retrieval_filters({"year": 0})
    with pytest.raises(InvalidRetrievalFilterError, match="year filter must be an int"):
        parse_retrieval_filters({"year": "2020"})


def test_parse_retrieval_filters_accepts_mapping() -> None:
    filters = parse_retrieval_filters(
        {
            "corpus_topic": "microgravity_skeletal_muscle",
            "year": 2020,
            "human_approval": "approved",
        }
    )
    assert filters == RetrievalFilters(
        corpus_topic="microgravity_skeletal_muscle",
        year=2020,
        human_approval="approved",
    )


def test_semantic_search_rejects_invalid_filter_mapping(session: Session) -> None:
    _seed(session)
    provider = FixtureEmbeddingProvider(query_vectors={"q": _axis_vector(index=0)})
    with pytest.raises(InvalidRetrievalFilterError, match="unknown retrieval filter key"):
        semantic_search(session, provider, "q", filters={"not_a_field": "x"})


def test_hybrid_search_applies_metadata_filters(session: Session) -> None:
    _seed(session)
    query = "soleus"
    provider = FixtureEmbeddingProvider(query_vectors={query: _axis_vector(index=0)})

    hits = hybrid_search(
        session,
        provider,
        query,
        k=5,
        filters={
            "corpus_topic": "microgravity_skeletal_muscle",
            "organism_model": "rodent",
            "exposure": "microgravity",
            "year": 2020,
            "human_approval": "approved",
            "section": "results",
        },
    )

    assert [hit.chunk_id for hit in hits] == ["chk_muscle"]


def test_hybrid_search_combines_semantic_and_fts(session: Session) -> None:
    _seed(session)
    # Make semantic prefer chk_other, while FTS matches chk_muscle.
    provider = FixtureEmbeddingProvider(query_vectors={"soleus": _axis_vector(index=1)})
    hits = hybrid_search(
        session,
        provider,
        "soleus",
        k=2,
        channels=("semantic", "fts"),
    )
    chunk_ids = {hit.chunk_id for hit in hits}
    assert "chk_other" in chunk_ids
    assert "chk_muscle" in chunk_ids
    assert all(hit.score > 0 for hit in hits)


def test_hybrid_search_rejects_empty_channels(session: Session) -> None:
    provider = FixtureEmbeddingProvider(query_vectors={"q": _axis_vector(index=0)})
    with pytest.raises(ValueError, match="at least one retrieval channel"):
        hybrid_search(session, provider, "q", channels=())

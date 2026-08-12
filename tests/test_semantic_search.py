"""Tests for semantic vector search (issue #44)."""

from __future__ import annotations

import hashlib
import os
from collections.abc import Iterator, Sequence
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from spacebio_evidence_engine.db.models import Chunk, ChunkEmbedding, Publication
from spacebio_evidence_engine.db.vector_types import MVP_EMBEDDING_DIMENSION
from spacebio_evidence_engine.embeddings import EmbeddingProvider
from spacebio_evidence_engine.retrieval import (
    SemanticSearchFilters,
    cosine_similarity,
    semantic_search,
)

ROOT = Path(__file__).resolve().parents[1]


class FixtureEmbeddingProvider(EmbeddingProvider):
    """Deterministic provider that returns pre-seeded query vectors by text."""

    def __init__(
        self,
        *,
        model_name: str = "fixture-search-v1",
        dimension: int = MVP_EMBEDDING_DIMENSION,
        query_vectors: dict[str, list[float]] | None = None,
    ) -> None:
        self._model_name = model_name
        self._dimension = dimension
        self._query_vectors = query_vectors or {}
        self.embed_query_calls = 0

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [_axis_vector(index=0) for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        self.embed_query_calls += 1
        if text not in self._query_vectors:
            raise KeyError(f"no fixture query vector for {text!r}")
        return list(self._query_vectors[text])


def _alembic_config(database_url: str) -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", database_url)
    os.environ["DATABASE_URL"] = database_url
    return cfg


def _content_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _axis_vector(*, index: int, scale: float = 1.0) -> list[float]:
    vector = [0.0] * MVP_EMBEDDING_DIMENSION
    vector[index] = scale
    return vector


@pytest.fixture()
def session(tmp_path: Path) -> Iterator[Session]:
    db_path = tmp_path / "semantic_search.sqlite3"
    database_url = f"sqlite+pysqlite:///{db_path}"
    command.upgrade(_alembic_config(database_url), "head")
    engine = create_engine(database_url)
    with Session(engine) as db_session:
        yield db_session


def _seed_corpus(session: Session, *, model_name: str = "fixture-search-v1") -> None:
    session.add_all(
        [
            Publication(
                publication_id="pub_muscle",
                title="Microgravity and soleus atrophy",
                source_url="https://doi.org/10.0/muscle",
                license_status="approved_oa_candidate",
                corpus_topic="microgravity_skeletal_muscle",
                organism_model="rodent",
                exposure="microgravity",
            ),
            Publication(
                publication_id="pub_plant",
                title="Plant growth off topic",
                source_url="https://doi.org/10.0/plant",
                license_status="approved_oa_candidate",
                corpus_topic="plant_biology",
                organism_model="arabidopsis",
                exposure="radiation",
            ),
        ]
    )
    chunks = [
        (
            "chk_near",
            "pub_muscle",
            "results",
            "Soleus muscle mass decreased in flight animals.",
            _axis_vector(index=0),
            2,
            2,
        ),
        (
            "chk_mid",
            "pub_muscle",
            "discussion",
            "Fiber cross-section was reduced after unloading.",
            _axis_vector(index=1),
            4,
            4,
        ),
        (
            "chk_far",
            "pub_plant",
            "results",
            "Leaf area increased under supplemental lighting.",
            _axis_vector(index=2),
            1,
            1,
        ),
        (
            "chk_other_model",
            "pub_muscle",
            "methods",
            "Animals were housed in flight cages.",
            _axis_vector(index=0, scale=0.9),
            1,
            1,
        ),
    ]
    for chunk_id, publication_id, section, text_body, vector, page_start, page_end in chunks:
        session.add(
            Chunk(
                chunk_id=chunk_id,
                publication_id=publication_id,
                section=section,
                chunk_text=text_body,
                content_hash=_content_hash(text_body),
                start_offset=0,
                end_offset=len(text_body),
                chunking_strategy_version="1.0.0",
                page_start=page_start,
                page_end=page_end,
                section_heading=section.title(),
                embedding_model=model_name if chunk_id != "chk_other_model" else "other-model",
            )
        )
        session.add(
            ChunkEmbedding(
                chunk_id=chunk_id,
                embedding=vector,
                model_name="other-model" if chunk_id == "chk_other_model" else model_name,
                dimension=MVP_EMBEDDING_DIMENSION,
            )
        )
    session.commit()


def test_cosine_similarity_known_vectors() -> None:
    assert cosine_similarity(_axis_vector(index=0), _axis_vector(index=0)) == pytest.approx(1.0)
    assert cosine_similarity(_axis_vector(index=0), _axis_vector(index=1)) == pytest.approx(0.0)


def test_semantic_search_ranks_known_fixture_vectors(session: Session) -> None:
    _seed_corpus(session)
    query = "soleus atrophy under microgravity"
    # Mostly aligned with chk_near (axis 0), slight axis-1 so chk_mid beats chk_far.
    query_vector = _axis_vector(index=0)
    query_vector[1] = 0.25
    provider = FixtureEmbeddingProvider(query_vectors={query: query_vector})

    hits = semantic_search(session, provider, query, k=3)

    assert provider.embed_query_calls == 1
    assert [hit.chunk_id for hit in hits] == ["chk_near", "chk_mid", "chk_far"]
    assert hits[0].score > hits[1].score > hits[2].score
    assert hits[0].publication_id == "pub_muscle"
    assert hits[0].title == "Microgravity and soleus atrophy"
    assert hits[0].section == "results"
    assert hits[0].page_start == 2
    assert hits[0].source_url == "https://doi.org/10.0/muscle"
    assert hits[0].model_name == "fixture-search-v1"
    assert "Soleus muscle mass" in hits[0].chunk_text


def test_semantic_search_excludes_other_model_embeddings(session: Session) -> None:
    _seed_corpus(session)
    query = "soleus"
    provider = FixtureEmbeddingProvider(query_vectors={query: _axis_vector(index=0)})

    hits = semantic_search(session, provider, query, k=10)

    assert all(hit.chunk_id != "chk_other_model" for hit in hits)
    assert {hit.model_name for hit in hits} == {"fixture-search-v1"}


def test_semantic_search_applies_metadata_filters(session: Session) -> None:
    _seed_corpus(session)
    query = "muscle"
    provider = FixtureEmbeddingProvider(query_vectors={query: _axis_vector(index=0)})

    hits = semantic_search(
        session,
        provider,
        query,
        k=10,
        filters=SemanticSearchFilters(
            corpus_topic="microgravity_skeletal_muscle",
            organism_model="rodent",
            exposure="microgravity",
            section="results",
        ),
    )

    assert [hit.chunk_id for hit in hits] == ["chk_near"]
    assert hits[0].publication_id == "pub_muscle"


def test_semantic_search_respects_k(session: Session) -> None:
    _seed_corpus(session)
    query = "muscle"
    provider = FixtureEmbeddingProvider(query_vectors={query: _axis_vector(index=0)})

    hits = semantic_search(session, provider, query, k=1)

    assert len(hits) == 1
    assert hits[0].chunk_id == "chk_near"


def test_semantic_search_rejects_empty_query(session: Session) -> None:
    provider = FixtureEmbeddingProvider(query_vectors={})
    with pytest.raises(ValueError, match="non-empty"):
        semantic_search(session, provider, "   ", k=1)


def test_semantic_search_rejects_invalid_k(session: Session) -> None:
    provider = FixtureEmbeddingProvider(query_vectors={"q": _axis_vector(index=0)})
    with pytest.raises(ValueError, match="k must be at least 1"):
        semantic_search(session, provider, "q", k=0)


@pytest.mark.integration
def test_semantic_search_pgvector_known_fixture_vectors() -> None:
    """Postgres path: pgvector ``<=>`` ranking with known fixture vectors."""

    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://spacebio:spacebio@localhost:5432/spacebio",
    )
    require = os.environ.get("SPACEBIO_REQUIRE_DB", "").lower() in {"1", "true", "yes"}
    cfg = _alembic_config(database_url)
    try:
        command.upgrade(cfg, "head")
        engine = create_engine(database_url)
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM chunk_embeddings WHERE chunk_id LIKE 'chk_sem_%'"))
            conn.execute(text("DELETE FROM chunks WHERE chunk_id LIKE 'chk_sem_%'"))
            conn.execute(text("DELETE FROM publications WHERE publication_id = 'pub_sem_search'"))

        with Session(engine) as session:
            session.add(
                Publication(
                    publication_id="pub_sem_search",
                    title="pgvector search fixture",
                    source_url="https://doi.org/10.0/sem",
                    license_status="approved_oa_candidate",
                    corpus_topic="microgravity_skeletal_muscle",
                )
            )
            near = "chk_sem_near"
            far = "chk_sem_far"
            for chunk_id, body, vector, page in (
                (near, "Near neighbor soleus text.", _axis_vector(index=0), 1),
                (far, "Far neighbor unrelated text.", _axis_vector(index=3), 2),
            ):
                session.add(
                    Chunk(
                        chunk_id=chunk_id,
                        publication_id="pub_sem_search",
                        section="results",
                        chunk_text=body,
                        content_hash=_content_hash(body),
                        start_offset=0,
                        end_offset=len(body),
                        chunking_strategy_version="1.0.0",
                        page_start=page,
                        page_end=page,
                        embedding_model="fixture-search-v1",
                    )
                )
                session.add(
                    ChunkEmbedding(
                        chunk_id=chunk_id,
                        embedding=vector,
                        model_name="fixture-search-v1",
                        dimension=MVP_EMBEDDING_DIMENSION,
                    )
                )
            session.commit()

            query = "pgvector fixture query"
            provider = FixtureEmbeddingProvider(
                query_vectors={query: _axis_vector(index=0)},
            )
            hits = semantic_search(session, provider, query, k=2)
            assert [hit.chunk_id for hit in hits] == [near, far]
            assert hits[0].score == pytest.approx(1.0)
            assert hits[0].publication_id == "pub_sem_search"
    except Exception as exc:  # noqa: BLE001
        if require:
            pytest.fail(f"PostgreSQL semantic search failed: {exc}")
        pytest.skip(f"PostgreSQL not available for semantic search integration: {exc}")

"""Tests for chunk embedding indexing (issue #43)."""

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
from spacebio_evidence_engine.indexing import index_chunk_embeddings

ROOT = Path(__file__).resolve().parents[1]


class FakeEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        *,
        model_name: str = "fake-indexer-v1",
        dimension: int = MVP_EMBEDDING_DIMENSION,
    ) -> None:
        self._model_name = model_name
        self._dimension = dimension

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self._dimension
        vector[0] = float(len(text))
        vector[1] = float(sum(ord(char) for char in text) % 997)
        return vector


def _alembic_config(database_url: str) -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", database_url)
    os.environ["DATABASE_URL"] = database_url
    return cfg


def _content_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@pytest.fixture()
def session(tmp_path: Path) -> Iterator[Session]:
    db_path = tmp_path / "indexing.sqlite3"
    database_url = f"sqlite+pysqlite:///{db_path}"
    command.upgrade(_alembic_config(database_url), "head")
    engine = create_engine(database_url)
    with Session(engine) as db_session:
        yield db_session


def _add_publication(session: Session) -> None:
    session.add(
        Publication(
            publication_id="pub_index",
            title="Indexing paper",
            source_url="https://doi.org/10.0/index",
            license_status="approved_oa_candidate",
            corpus_topic="microgravity_skeletal_muscle",
        )
    )


def _add_chunk(session: Session, chunk_id: str, text: str) -> None:
    session.add(
        Chunk(
            chunk_id=chunk_id,
            publication_id="pub_index",
            section="results",
            chunk_text=text,
            content_hash=_content_hash(text),
            start_offset=0,
            end_offset=len(text),
            chunking_strategy_version="1.0.0",
        )
    )


def test_index_chunk_embeddings_writes_pending_chunks(session: Session) -> None:
    _add_publication(session)
    _add_chunk(session, "chk_a", "Soleus mass decreased in flight animals.")
    _add_chunk(session, "chk_b", "Ground controls retained larger muscle fibers.")
    session.commit()

    result = index_chunk_embeddings(session, FakeEmbeddingProvider(), batch_size=1)
    session.commit()

    assert result.status == "completed"
    assert result.scanned_chunks == 2
    assert result.embedded_chunks == 2
    assert result.updated_chunks == 0
    assert result.chunk_ids == ("chk_a", "chk_b")

    stored = session.query(ChunkEmbedding).order_by(ChunkEmbedding.chunk_id).all()
    assert [row.chunk_id for row in stored] == ["chk_a", "chk_b"]
    assert all(row.model_name == "fake-indexer-v1" for row in stored)
    assert all(row.dimension == MVP_EMBEDDING_DIMENSION for row in stored)
    assert session.get(Chunk, "chk_a").embedding_model == "fake-indexer-v1"  # type: ignore[union-attr]


def test_index_chunk_embeddings_is_idempotent_by_default(session: Session) -> None:
    _add_publication(session)
    _add_chunk(session, "chk_once", "A single chunk is embedded once.")
    session.commit()

    first = index_chunk_embeddings(session, FakeEmbeddingProvider())
    second = index_chunk_embeddings(session, FakeEmbeddingProvider())

    assert first.embedded_chunks == 1
    assert second.status == "nothing_to_index"
    assert second.embedded_chunks == 0
    assert session.query(ChunkEmbedding).count() == 1


def test_index_chunk_embeddings_reindexes_existing_model(session: Session) -> None:
    _add_publication(session)
    _add_chunk(session, "chk_reindex", "Reindex this chunk.")
    session.commit()

    index_chunk_embeddings(session, FakeEmbeddingProvider(model_name="fake-indexer-v1"))
    result = index_chunk_embeddings(
        session,
        FakeEmbeddingProvider(model_name="fake-indexer-v1"),
        reindex=True,
    )

    assert result.embedded_chunks == 1
    assert result.updated_chunks == 1
    assert session.query(ChunkEmbedding).count() == 1


def test_index_chunk_embeddings_replaces_stale_model(session: Session) -> None:
    _add_publication(session)
    _add_chunk(session, "chk_stale", "Replace a stale embedding model.")
    session.commit()

    index_chunk_embeddings(session, FakeEmbeddingProvider(model_name="old-model"))
    result = index_chunk_embeddings(session, FakeEmbeddingProvider(model_name="new-model"))

    stored = session.get(ChunkEmbedding, "chk_stale")
    assert result.embedded_chunks == 1
    assert result.updated_chunks == 1
    assert stored is not None
    assert stored.model_name == "new-model"
    assert session.get(Chunk, "chk_stale").embedding_model == "new-model"  # type: ignore[union-attr]


def test_index_chunk_embeddings_rejects_wrong_provider_dimension(session: Session) -> None:
    with pytest.raises(ValueError, match="does not match MVP dimension"):
        index_chunk_embeddings(session, FakeEmbeddingProvider(dimension=3))

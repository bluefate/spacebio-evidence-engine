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
        broken_vector_length: int | None = None,
    ) -> None:
        self._model_name = model_name
        self._dimension = dimension
        self._broken_vector_length = broken_vector_length
        self.embed_documents_calls = 0
        self.texts_seen: list[str] = []

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        self.embed_documents_calls += 1
        self.texts_seen.extend(texts)
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        length = (
            self._broken_vector_length
            if self._broken_vector_length is not None
            else self._dimension
        )
        vector = [0.0] * length
        if length >= 1:
            vector[0] = float(len(text))
        if length >= 2:
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


def _expected_vector(text: str, dimension: int = MVP_EMBEDDING_DIMENSION) -> list[float]:
    vector = [0.0] * dimension
    vector[0] = float(len(text))
    vector[1] = float(sum(ord(char) for char in text) % 997)
    return vector


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


def _add_chunk(session: Session, chunk_id: str, text: str) -> Chunk:
    chunk = Chunk(
        chunk_id=chunk_id,
        publication_id="pub_index",
        section="results",
        chunk_text=text,
        content_hash=_content_hash(text),
        start_offset=0,
        end_offset=len(text),
        chunking_strategy_version="1.0.0",
    )
    session.add(chunk)
    return chunk


def test_index_chunk_embeddings_writes_pending_chunks(session: Session) -> None:
    _add_publication(session)
    text_a = "Soleus mass decreased in flight animals."
    text_b = "Ground controls retained larger muscle fibers."
    _add_chunk(session, "chk_a", text_a)
    _add_chunk(session, "chk_b", text_b)
    session.commit()

    provider = FakeEmbeddingProvider()
    result = index_chunk_embeddings(session, provider, batch_size=1)
    session.commit()

    assert result.status == "completed"
    assert result.scanned_chunks == 2
    assert result.embedded_chunks == 2
    assert result.skipped_chunks == 0
    assert result.updated_chunks == 0
    assert result.chunk_ids == ("chk_a", "chk_b")
    assert provider.embed_documents_calls == 2

    stored = session.query(ChunkEmbedding).order_by(ChunkEmbedding.chunk_id).all()
    assert [row.chunk_id for row in stored] == ["chk_a", "chk_b"]
    assert all(row.model_name == "fake-indexer-v1" for row in stored)
    assert all(row.dimension == MVP_EMBEDDING_DIMENSION for row in stored)
    assert stored[0].embedding == _expected_vector(text_a)
    assert stored[1].embedding == _expected_vector(text_b)
    assert session.get(Chunk, "chk_a").embedding_model == "fake-indexer-v1"  # type: ignore[union-attr]


def test_index_chunk_embeddings_is_idempotent_by_default(session: Session) -> None:
    _add_publication(session)
    _add_chunk(session, "chk_once", "A single chunk is embedded once.")
    session.commit()

    provider = FakeEmbeddingProvider()
    first = index_chunk_embeddings(session, provider)
    second = index_chunk_embeddings(session, provider)

    assert first.embedded_chunks == 1
    assert first.skipped_chunks == 0
    assert second.status == "nothing_to_index"
    assert second.scanned_chunks == 1
    assert second.embedded_chunks == 0
    assert second.skipped_chunks == 1
    assert provider.embed_documents_calls == 1
    assert session.query(ChunkEmbedding).count() == 1


def test_index_chunk_embeddings_reindexes_all_selected_chunks(session: Session) -> None:
    _add_publication(session)
    _add_chunk(session, "chk_reindex", "Reindex this chunk.")
    session.commit()

    first_provider = FakeEmbeddingProvider(model_name="fake-indexer-v1")
    index_chunk_embeddings(session, first_provider)
    second_provider = FakeEmbeddingProvider(model_name="fake-indexer-v1")
    result = index_chunk_embeddings(session, second_provider, reindex=True)

    assert result.embedded_chunks == 1
    assert result.skipped_chunks == 0
    assert result.updated_chunks == 1
    assert second_provider.embed_documents_calls == 1
    assert session.query(ChunkEmbedding).count() == 1


def test_index_chunk_embeddings_reindex_rewrites_other_model_rows(session: Session) -> None:
    _add_publication(session)
    text = "Force rebuild across models."
    _add_chunk(session, "chk_other", text)
    session.commit()

    index_chunk_embeddings(session, FakeEmbeddingProvider(model_name="old-model"))
    provider = FakeEmbeddingProvider(model_name="new-model")
    result = index_chunk_embeddings(session, provider, reindex=True)

    stored = session.get(ChunkEmbedding, "chk_other")
    assert result.embedded_chunks == 1
    assert result.skipped_chunks == 0
    assert result.updated_chunks == 1
    assert stored is not None
    assert stored.model_name == "new-model"
    assert stored.embedding == _expected_vector(text)
    assert session.get(Chunk, "chk_other").embedding_model == "new-model"  # type: ignore[union-attr]


def test_index_chunk_embeddings_replaces_stale_model(session: Session) -> None:
    _add_publication(session)
    text = "Replace a stale embedding model."
    _add_chunk(session, "chk_stale", text)
    session.commit()

    index_chunk_embeddings(session, FakeEmbeddingProvider(model_name="old-model"))
    result = index_chunk_embeddings(session, FakeEmbeddingProvider(model_name="new-model"))

    stored = session.get(ChunkEmbedding, "chk_stale")
    assert result.embedded_chunks == 1
    assert result.skipped_chunks == 0
    assert result.updated_chunks == 1
    assert stored is not None
    assert stored.model_name == "new-model"
    assert stored.embedding == _expected_vector(text)
    assert session.get(Chunk, "chk_stale").embedding_model == "new-model"  # type: ignore[union-attr]


def test_index_chunk_embeddings_default_skips_after_text_change(session: Session) -> None:
    """Model-based idempotency does not watch content_hash; use reindex after rechunk."""

    _add_publication(session)
    chunk = _add_chunk(session, "chk_stale_text", "Original chunk text.")
    session.commit()

    provider = FakeEmbeddingProvider()
    index_chunk_embeddings(session, provider)
    original = list(session.get(ChunkEmbedding, "chk_stale_text").embedding)  # type: ignore[union-attr]

    chunk.chunk_text = "Updated chunk text after rechunk."
    chunk.content_hash = _content_hash(chunk.chunk_text)
    chunk.end_offset = len(chunk.chunk_text)
    session.commit()

    skipped = index_chunk_embeddings(session, FakeEmbeddingProvider())
    assert skipped.status == "nothing_to_index"
    assert skipped.skipped_chunks == 1
    assert session.get(ChunkEmbedding, "chk_stale_text").embedding == original  # type: ignore[union-attr]

    rebuilt = index_chunk_embeddings(session, FakeEmbeddingProvider(), reindex=True)
    assert rebuilt.embedded_chunks == 1
    assert rebuilt.updated_chunks == 1
    assert session.get(ChunkEmbedding, "chk_stale_text").embedding == _expected_vector(  # type: ignore[union-attr]
        "Updated chunk text after rechunk."
    )


def test_index_chunk_embeddings_rejects_wrong_provider_dimension(session: Session) -> None:
    with pytest.raises(ValueError, match="does not match MVP dimension"):
        index_chunk_embeddings(session, FakeEmbeddingProvider(dimension=3))


def test_index_chunk_embeddings_rejects_wrong_vector_length(session: Session) -> None:
    _add_publication(session)
    _add_chunk(session, "chk_bad_vec", "Provider claims 384 but returns a short vector.")
    session.commit()

    with pytest.raises(ValueError, match="provider returned vector length"):
        index_chunk_embeddings(
            session,
            FakeEmbeddingProvider(broken_vector_length=8),
        )

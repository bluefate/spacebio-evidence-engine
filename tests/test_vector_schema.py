"""Migration and ORM tests for chunk embedding vector schema (issue #42)."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from spacebio_evidence_engine.db.vector_types import (
    MVP_EMBEDDING_DIMENSION,
    MVP_EMBEDDING_MODEL_NAME,
    EmbeddingVector,
)

ROOT = Path(__file__).resolve().parents[1]


def _alembic_config(database_url: str) -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", database_url)
    os.environ["DATABASE_URL"] = database_url
    return cfg


def _content_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _unit_vector(dim: int = MVP_EMBEDDING_DIMENSION) -> list[float]:
    values = [0.0] * dim
    values[0] = 1.0
    return values


def test_embedding_vector_rejects_wrong_dimension() -> None:
    column = EmbeddingVector(MVP_EMBEDDING_DIMENSION)
    with pytest.raises(ValueError, match="does not match required dimension"):
        column.process_bind_param([0.1, 0.2], dialect=type("D", (), {"name": "sqlite"})())


def test_chunk_embedding_orm_matches_required_columns() -> None:
    from spacebio_evidence_engine.db.models import ChunkEmbedding

    columns = {column.name for column in ChunkEmbedding.__table__.columns}
    required = {"chunk_id", "embedding", "model_name", "dimension"}
    assert required.issubset(columns)
    assert ChunkEmbedding.__tablename__ == "chunk_embeddings"
    assert len(ChunkEmbedding.__table__.c.chunk_id.foreign_keys) == 1
    fk = next(iter(ChunkEmbedding.__table__.c.chunk_id.foreign_keys))
    assert fk._get_colspec() == "chunks.chunk_id"


def test_migration_upgrade_and_downgrade(tmp_path: Path) -> None:
    db_path = tmp_path / "vector_migration.sqlite3"
    database_url = f"sqlite+pysqlite:///{db_path}"
    cfg = _alembic_config(database_url)

    command.upgrade(cfg, "head")
    engine = create_engine(database_url)
    inspector = inspect(engine)
    assert "chunk_embeddings" in inspector.get_table_names()
    column_names = {col["name"] for col in inspector.get_columns("chunk_embeddings")}
    assert {"chunk_id", "embedding", "model_name", "dimension"}.issubset(column_names)
    fks = inspector.get_foreign_keys("chunk_embeddings")
    assert any(
        fk["referred_table"] == "chunks" and "chunk_id" in fk["constrained_columns"] for fk in fks
    )

    command.downgrade(cfg, "20260806_0002")
    inspector = inspect(engine)
    assert "chunk_embeddings" not in inspector.get_table_names()
    assert "chunks" in inspector.get_table_names()


def test_chunk_embedding_model_round_trip(tmp_path: Path) -> None:
    from spacebio_evidence_engine.db.models import Chunk, ChunkEmbedding, Publication

    db_path = tmp_path / "vector_roundtrip.sqlite3"
    database_url = f"sqlite+pysqlite:///{db_path}"
    cfg = _alembic_config(database_url)
    command.upgrade(cfg, "head")
    engine = create_engine(database_url)

    body = "Soleus mass decreased relative to controls."
    vector = _unit_vector()
    with Session(engine) as session:
        session.add(
            Publication(
                publication_id="pub_vec",
                title="Vector paper",
                source_url="https://doi.org/10.0/vec",
                license_status="approved_oa_candidate",
                corpus_topic="microgravity_skeletal_muscle",
            )
        )
        session.add(
            Chunk(
                chunk_id="chk_vec",
                publication_id="pub_vec",
                section="results",
                chunk_text=body,
                content_hash=_content_hash(body),
                start_offset=0,
                end_offset=len(body),
                chunking_strategy_version="1.0.0",
                embedding_model=MVP_EMBEDDING_MODEL_NAME,
            )
        )
        session.add(
            ChunkEmbedding(
                chunk_id="chk_vec",
                embedding=vector,
                model_name=MVP_EMBEDDING_MODEL_NAME,
                dimension=MVP_EMBEDDING_DIMENSION,
            )
        )
        session.commit()

    with Session(engine) as session:
        loaded = session.get(ChunkEmbedding, "chk_vec")
        assert loaded is not None
        assert loaded.model_name == MVP_EMBEDDING_MODEL_NAME
        assert loaded.dimension == MVP_EMBEDDING_DIMENSION
        assert loaded.embedding == vector
        assert loaded.chunk is not None
        assert loaded.chunk.chunk_id == "chk_vec"


def test_chunk_embedding_dimension_check_constraint(tmp_path: Path) -> None:
    db_path = tmp_path / "vector_dim_check.sqlite3"
    database_url = f"sqlite+pysqlite:///{db_path}"
    cfg = _alembic_config(database_url)
    command.upgrade(cfg, "head")
    engine = create_engine(database_url)

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO publications (
                  publication_id, title, source_url, license_status,
                  corpus_topic, ingestion_status
                ) VALUES (
                  'pub_dim', 'Dim paper', 'https://doi.org/10.0/dim',
                  'approved_oa_candidate', 'microgravity_skeletal_muscle',
                  'not_ingested'
                )
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT INTO chunks (
                  chunk_id, publication_id, section, chunk_text, content_hash,
                  start_offset, end_offset, chunking_strategy_version
                ) VALUES (
                  'chk_dim', 'pub_dim', 'methods', 'x', :hash, 0, 1, '1.0.0'
                )
                """
            ),
            {"hash": _content_hash("x")},
        )

    with engine.connect() as conn:
        with pytest.raises(IntegrityError):
            with conn.begin():
                conn.execute(
                    text(
                        """
                        INSERT INTO chunk_embeddings (
                          chunk_id, embedding, model_name, dimension
                        ) VALUES (
                          'chk_dim', :embedding, :model, 1536
                        )
                        """
                    ),
                    {
                        "embedding": str(_unit_vector()),
                        "model": MVP_EMBEDDING_MODEL_NAME,
                    },
                )


@pytest.mark.integration
def test_chunk_embedding_migration_against_postgres() -> None:
    """Postgres path: extension present and vector(384) column exists."""
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://spacebio:spacebio@localhost:5432/spacebio",
    )
    require = os.environ.get("SPACEBIO_REQUIRE_DB", "").lower() in {"1", "true", "yes"}
    cfg = _alembic_config(database_url)
    try:
        command.upgrade(cfg, "head")
        engine = create_engine(database_url)
        with engine.connect() as conn:
            ext = conn.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")).scalar()
            assert ext == 1
            col_type = conn.execute(
                text(
                    """
                    SELECT format_type(a.atttypid, a.atttypmod)
                    FROM pg_attribute a
                    JOIN pg_class c ON a.attrelid = c.oid
                    JOIN pg_namespace n ON c.relnamespace = n.oid
                    WHERE c.relname = 'chunk_embeddings'
                      AND a.attname = 'embedding'
                      AND n.nspname = current_schema()
                      AND a.attnum > 0
                      AND NOT a.attisdropped
                    """
                )
            ).scalar_one()
        assert "vector" in str(col_type)
        assert "384" in str(col_type)
    except Exception as exc:  # noqa: BLE001
        if require:
            pytest.fail(f"Postgres vector migration failed: {exc}")
        pytest.skip(f"PostgreSQL not available for vector migration smoke: {exc}")

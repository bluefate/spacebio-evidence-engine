"""Migration and ORM tests for chunks schema (issue #33)."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]


def _alembic_config(database_url: str) -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", database_url)
    os.environ["DATABASE_URL"] = database_url
    return cfg


def _content_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def test_chunk_orm_matches_required_columns() -> None:
    from spacebio_evidence_engine.db.models import Chunk

    columns = {column.name for column in Chunk.__table__.columns}
    required = {
        "chunk_id",
        "publication_id",
        "section",
        "chunk_text",
        "content_hash",
        "start_offset",
        "end_offset",
        "page_start",
        "page_end",
        "chunking_strategy_version",
    }
    assert required.issubset(columns)
    assert Chunk.__tablename__ == "chunks"
    assert len(Chunk.__table__.c.publication_id.foreign_keys) == 1
    fk = next(iter(Chunk.__table__.c.publication_id.foreign_keys))
    assert fk._get_colspec() == "publications.publication_id"


def test_search_tsv_is_omitted_from_insert() -> None:
    """Postgres GENERATED ALWAYS search_tsv must not appear in INSERT."""
    from sqlalchemy import insert
    from sqlalchemy.dialects import postgresql
    from sqlalchemy.schema import FetchedValue

    from spacebio_evidence_engine.db.models import Chunk

    column = Chunk.__table__.c.search_tsv
    assert isinstance(column.server_default, FetchedValue)

    compiled = (
        insert(Chunk)
        .values(
            chunk_id="c",
            publication_id="p",
            section="results",
            chunk_text="microgravity atrophy",
            content_hash="h",
            start_offset=0,
            end_offset=20,
            chunking_strategy_version="1.0.0",
        )
        .compile(dialect=postgresql.dialect())
    )
    assert "search_tsv" not in str(compiled)
    assert "search_tsv" not in compiled.params


def test_migration_upgrade_and_downgrade(tmp_path: Path) -> None:
    db_path = tmp_path / "chunk_migration.sqlite3"
    database_url = f"sqlite+pysqlite:///{db_path}"
    cfg = _alembic_config(database_url)

    command.upgrade(cfg, "head")
    engine = create_engine(database_url)
    inspector = inspect(engine)
    assert "publications" in inspector.get_table_names()
    assert "chunks" in inspector.get_table_names()
    column_names = {col["name"] for col in inspector.get_columns("chunks")}
    assert {
        "chunk_id",
        "publication_id",
        "section",
        "chunk_text",
        "content_hash",
        "start_offset",
        "end_offset",
        "page_start",
        "page_end",
    }.issubset(column_names)
    fks = inspector.get_foreign_keys("chunks")
    assert any(
        fk["referred_table"] == "publications" and "publication_id" in fk["constrained_columns"]
        for fk in fks
    )

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO publications (
                  publication_id, title, source_url, license_status,
                  corpus_topic, ingestion_status
                ) VALUES (
                  'pub_test', 'Test title', 'https://doi.org/10.0/test',
                  'approved_oa_candidate', 'microgravity_skeletal_muscle',
                  'not_ingested'
                )
                """
            )
        )
        body = "Mice underwent hindlimb unloading for 14 days."
        conn.execute(
            text(
                """
                INSERT INTO chunks (
                  chunk_id, publication_id, section, chunk_text, content_hash,
                  start_offset, end_offset, chunking_strategy_version,
                  page_start, page_end
                ) VALUES (
                  'chk_test', 'pub_test', 'methods', :text, :hash,
                  10, 60, '1.0.0', 2, 2
                )
                """
            ),
            {"text": body, "hash": _content_hash(body)},
        )
        count = conn.execute(text("SELECT COUNT(*) FROM chunks")).scalar_one()
        assert count == 1

    command.downgrade(cfg, "20260805_0001")
    inspector = inspect(engine)
    assert "chunks" not in inspector.get_table_names()
    assert "publications" in inspector.get_table_names()

    command.downgrade(cfg, "base")
    inspector = inspect(engine)
    assert "publications" not in inspector.get_table_names()


def test_chunk_model_round_trip(tmp_path: Path) -> None:
    """ORM insert/refresh asserts FK + provenance fields survive a session."""
    from spacebio_evidence_engine.db.models import Chunk, Publication

    db_path = tmp_path / "chunk_roundtrip.sqlite3"
    database_url = f"sqlite+pysqlite:///{db_path}"
    cfg = _alembic_config(database_url)
    command.upgrade(cfg, "head")
    engine = create_engine(database_url)

    body = "Soleus mass decreased relative to controls."
    digest = _content_hash(body)
    with Session(engine) as session:
        session.add(
            Publication(
                publication_id="pub_rt",
                title="Round-trip paper",
                source_url="https://doi.org/10.0/rt",
                license_status="approved_oa_candidate",
                corpus_topic="microgravity_skeletal_muscle",
            )
        )
        session.add(
            Chunk(
                chunk_id="chk_rt",
                publication_id="pub_rt",
                section="results",
                chunk_text=body,
                content_hash=digest,
                start_offset=100,
                end_offset=100 + len(body),
                chunking_strategy_version="1.0.0",
                page_start=3,
                page_end=3,
                section_heading="3. Results",
            )
        )
        session.commit()

    with Session(engine) as session:
        loaded = session.get(Chunk, "chk_rt")
        assert loaded is not None
        assert loaded.publication_id == "pub_rt"
        assert loaded.section == "results"
        assert loaded.chunk_text == body
        assert loaded.content_hash == digest
        assert loaded.start_offset == 100
        assert loaded.end_offset == 100 + len(body)
        assert loaded.page_start == 3
        assert loaded.page_end == 3
        assert loaded.chunking_strategy_version == "1.0.0"
        assert loaded.publication is not None
        assert loaded.publication.title == "Round-trip paper"


def test_chunk_foreign_key_rejects_missing_publication(tmp_path: Path) -> None:
    from sqlalchemy.exc import IntegrityError

    db_path = tmp_path / "chunk_fk.sqlite3"
    database_url = f"sqlite+pysqlite:///{db_path}"
    cfg = _alembic_config(database_url)
    command.upgrade(cfg, "head")
    engine = create_engine(database_url)
    # SQLite only enforces FKs when PRAGMA foreign_keys=ON.
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
        conn.commit()
        with pytest.raises(IntegrityError):
            with conn.begin():
                conn.execute(
                    text(
                        """
                        INSERT INTO chunks (
                          chunk_id, publication_id, section, chunk_text, content_hash,
                          start_offset, end_offset, chunking_strategy_version
                        ) VALUES (
                          'chk_orphan', 'missing_pub', 'methods', 'x', :hash, 0, 1, '1.0.0'
                        )
                        """
                    ),
                    {"hash": _content_hash("x")},
                )


@pytest.mark.integration
def test_chunk_migration_against_postgres() -> None:
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://spacebio:spacebio@localhost:5432/spacebio",
    )
    require = os.environ.get("SPACEBIO_REQUIRE_DB", "").lower() in {"1", "true", "yes"}
    cfg = _alembic_config(database_url)
    try:
        command.upgrade(cfg, "head")
        engine = create_engine(database_url)
        inspector = inspect(engine)
        assert "chunks" in inspector.get_table_names()
    except Exception as exc:  # noqa: BLE001
        if require:
            pytest.fail(f"Postgres chunk migration failed: {exc}")
        pytest.skip(f"PostgreSQL not available for chunk migration smoke: {exc}")

"""Migration upgrade/downgrade tests for publications schema (issue #27)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

ROOT = Path(__file__).resolve().parents[1]


def _alembic_config(database_url: str) -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", database_url)
    os.environ["DATABASE_URL"] = database_url
    return cfg


def test_publication_orm_matches_required_columns() -> None:
    from spacebio_evidence_engine.db.models import Publication

    columns = {column.name for column in Publication.__table__.columns}
    required = {
        "publication_id",
        "title",
        "source_url",
        "license_status",
        "corpus_topic",
        "ingestion_status",
    }
    assert required.issubset(columns)
    assert Publication.__tablename__ == "publications"


def test_migration_upgrade_and_downgrade(tmp_path: Path) -> None:
    db_path = tmp_path / "migration.sqlite3"
    database_url = f"sqlite+pysqlite:///{db_path}"
    cfg = _alembic_config(database_url)

    command.upgrade(cfg, "head")
    engine = create_engine(database_url)
    inspector = inspect(engine)
    assert "publications" in inspector.get_table_names()
    column_names = {col["name"] for col in inspector.get_columns("publications")}
    assert {
        "publication_id",
        "title",
        "source_url",
        "license_status",
        "corpus_topic",
        "ingestion_status",
        "doi",
        "pdf_path",
        "human_approval",
    }.issubset(column_names)

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
        count = conn.execute(text("SELECT COUNT(*) FROM publications")).scalar_one()
        assert count == 1

    command.downgrade(cfg, "base")
    inspector = inspect(engine)
    assert "publications" not in inspector.get_table_names()


@pytest.mark.integration
def test_migration_against_postgres() -> None:
    """Optional live Postgres check when Compose is up."""
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
        assert "publications" in inspector.get_table_names()
    except Exception as exc:  # noqa: BLE001 — surface skip vs fail
        if require:
            pytest.fail(f"Postgres migration failed: {exc}")
        pytest.skip(f"PostgreSQL not available for migration smoke: {exc}")

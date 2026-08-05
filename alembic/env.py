"""Alembic environment for Space Biology Evidence Engine migrations."""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from spacebio_evidence_engine.db import models as _models  # noqa: E402, F401
from spacebio_evidence_engine.db.base import Base  # noqa: E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _database_url() -> str:
    """Resolve SQLAlchemy URL from env (same convention as API settings)."""
    configured = config.get_main_option("sqlalchemy.url")
    if configured and not configured.startswith("driver://"):
        return configured.strip()

    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return database_url.strip()

    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db = os.environ.get("POSTGRES_DB", "spacebio")
    user = os.environ.get("POSTGRES_USER", "spacebio")
    password = os.environ.get("POSTGRES_PASSWORD", "spacebio")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"


def _normalize_url(url: str) -> str:
    """Accept libpq or SQLAlchemy URLs."""
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        return "postgresql+psycopg://" + url.split("://", 1)[1]
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = _normalize_url(_database_url())
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = _normalize_url(_database_url())
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

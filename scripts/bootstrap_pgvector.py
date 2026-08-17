#!/usr/bin/env python3
"""Idempotent PostgreSQL bootstrap: enable the pgvector extension.

Compose mounts ``scripts/db/init`` into ``docker-entrypoint-initdb.d`` so a fresh
volume gets the extension automatically. This script covers existing volumes
(init scripts do not re-run) and CI smoke checks.

Usage:
  make db-bootstrap
  python scripts/bootstrap_pgvector.py

Environment:
  DATABASE_URL — SQLAlchemy-style URL (postgresql+psycopg://...) or libpq URL
  POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from spacebio_evidence_engine.env_loader import load_dotenv  # noqa: E402


def _libpq_url_from_database_url(database_url: str) -> str:
    """Convert SQLAlchemy URL to a libpq/psycopg connection string if needed."""
    url = database_url.strip()
    if url.startswith("postgresql+psycopg://"):
        return "postgresql://" + url.removeprefix("postgresql+psycopg://")
    if url.startswith("postgresql+psycopg2://"):
        return "postgresql://" + url.removeprefix("postgresql+psycopg2://")
    return url


def _connect_kwargs() -> dict[str, object]:
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        parsed = urlparse(_libpq_url_from_database_url(database_url))
        if parsed.scheme not in {"postgresql", "postgres"}:
            raise SystemExit(f"Unsupported DATABASE_URL scheme: {parsed.scheme!r}")
        return {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 5432,
            "dbname": (parsed.path or "/spacebio").lstrip("/") or "spacebio",
            "user": unquote(parsed.username) if parsed.username else "spacebio",
            "password": unquote(parsed.password) if parsed.password else "",
        }

    return {
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": int(os.environ.get("POSTGRES_PORT", "5432")),
        "dbname": os.environ.get("POSTGRES_DB", "spacebio"),
        "user": os.environ.get("POSTGRES_USER", "spacebio"),
        "password": os.environ.get("POSTGRES_PASSWORD", "spacebio"),
    }


def ensure_pgvector() -> str:
    """Create the vector extension if missing; return installed version label."""
    try:
        import psycopg
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "psycopg is required. Install with: pip install -e '.[dev]'"
        ) from exc

    kwargs = _connect_kwargs()
    try:
        conn = psycopg.connect(**kwargs)
    except psycopg.OperationalError as exc:
        raise SystemExit(
            "Could not connect to PostgreSQL. Start it with `make services` "
            f"(Docker must be running), then retry.\n{exc}"
        ) from exc

    with conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        row = conn.execute(
            "SELECT extversion FROM pg_extension WHERE extname = %s",
            ("vector",),
        ).fetchone()
        if row is None:
            raise RuntimeError("pgvector extension was not found after CREATE EXTENSION")
        conn.commit()
        return str(row[0])


def main() -> int:
    load_dotenv(ROOT / ".env")
    version = ensure_pgvector()
    print(f"pgvector extension ready (version {version})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

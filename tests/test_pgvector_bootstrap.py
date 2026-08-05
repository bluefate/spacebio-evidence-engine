"""Smoke tests for PostgreSQL pgvector bootstrap (issue #8)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
INIT_SQL = ROOT / "scripts" / "db" / "init" / "01_pgvector.sql"
BOOTSTRAP = ROOT / "scripts" / "bootstrap_pgvector.py"


def test_init_sql_enables_vector_extension() -> None:
    text = INIT_SQL.read_text(encoding="utf-8")
    assert "CREATE EXTENSION IF NOT EXISTS vector" in text


def test_bootstrap_script_exists_and_is_executable_docs() -> None:
    assert BOOTSTRAP.is_file()
    source = BOOTSTRAP.read_text(encoding="utf-8")
    assert "CREATE EXTENSION IF NOT EXISTS vector" in source
    assert "ensure_pgvector" in source


@pytest.mark.integration
def test_pgvector_extension_available() -> None:
    """Connect to Compose Postgres and ensure vector extension is enabled.

    Skips when the database is unreachable unless SPACEBIO_REQUIRE_DB=1.
    """
    require = os.environ.get("SPACEBIO_REQUIRE_DB", "").lower() in {"1", "true", "yes"}
    env = os.environ.copy()
    # Prefer documented local Compose defaults when .env is absent.
    env.setdefault(
        "DATABASE_URL",
        "postgresql+psycopg://spacebio:spacebio@localhost:5432/spacebio",
    )

    result = subprocess.run(
        [sys.executable, str(BOOTSTRAP)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        combined = f"{result.stdout}\n{result.stderr}"
        if require:
            pytest.fail(f"pgvector bootstrap failed:\n{combined}")
        pytest.skip(f"PostgreSQL not available for integration smoke:\n{combined}")

    assert "pgvector extension ready" in result.stdout

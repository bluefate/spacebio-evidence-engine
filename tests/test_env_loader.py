"""Tests for the stdlib .env loader (issue #172)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from spacebio_evidence_engine.env_loader import load_dotenv


@pytest.fixture()
def _clear_test_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure the tested env keys are not already set."""
    for key in ("TEST_POSTGRES_PASSWORD", "TEST_DATABASE_URL"):
        monkeypatch.delenv(key, raising=False)


def test_load_dotenv_sets_unset_keys(tmp_path: Path, _clear_test_keys: None) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "TEST_POSTGRES_PASSWORD=change-me-locally\n"
        "TEST_DATABASE_URL=postgresql+psycopg://spacebio:change-me-locally@localhost:5432/spacebio\n",
        encoding="utf-8",
    )

    load_dotenv(env)

    assert os.environ["TEST_POSTGRES_PASSWORD"] == "change-me-locally"
    assert (
        os.environ["TEST_DATABASE_URL"]
        == "postgresql+psycopg://spacebio:change-me-locally@localhost:5432/spacebio"
    )


def test_load_dotenv_does_not_override_existing(tmp_path: Path, _clear_test_keys: None) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "TEST_POSTGRES_PASSWORD=from-file\nTEST_DATABASE_URL=from-file\n",
        encoding="utf-8",
    )

    os.environ["TEST_POSTGRES_PASSWORD"] = "pre-existing"
    os.environ["TEST_DATABASE_URL"] = "pre-existing"

    load_dotenv(env)

    assert os.environ["TEST_POSTGRES_PASSWORD"] == "pre-existing"
    assert os.environ["TEST_DATABASE_URL"] == "pre-existing"

    del os.environ["TEST_POSTGRES_PASSWORD"]
    del os.environ["TEST_DATABASE_URL"]


def test_load_dotenv_skips_comments_and_blank_lines(tmp_path: Path, _clear_test_keys: None) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "# a comment\n\nTEST_POSTGRES_PASSWORD=secret\n# another comment\n",
        encoding="utf-8",
    )

    load_dotenv(env)

    assert os.environ["TEST_POSTGRES_PASSWORD"] == "secret"
    del os.environ["TEST_POSTGRES_PASSWORD"]


def test_load_dotenv_missing_file_is_noop() -> None:
    missing = Path("/nonexistent/path/.env")
    load_dotenv(missing)

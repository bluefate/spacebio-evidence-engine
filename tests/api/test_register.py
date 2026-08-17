"""API tests for publication register routes (issue #165)."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from spacebio_api.config import Settings
from spacebio_api.main import create_app
from spacebio_evidence_engine.storage.local import LocalFileStorage

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_PDF = ROOT / "tests" / "fixtures" / "sample_two_page.pdf"


def _alembic_config(database_url: str) -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", database_url)
    os.environ["DATABASE_URL"] = database_url
    return cfg


@pytest.fixture()
def client(tmp_path: Path) -> Iterator[TestClient]:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'api-register.sqlite3'}"
    command.upgrade(_alembic_config(database_url), "head")
    engine = create_engine(database_url)
    factory = sessionmaker(bind=engine)
    app = create_app(Settings(APP_ENV="test", OPENAI_API_KEY=None))
    app.state.register_session_factory = factory
    app.state.pdf_storage = LocalFileStorage(tmp_path / "pdfs")
    yield TestClient(app)


def test_from_pdf_rejects_non_pdf(client: TestClient) -> None:
    response = client.post(
        "/publications/from-pdf",
        data={"title": "Nope", "license_id": "cc-by"},
        files={"file": ("note.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_from_pdf_happy_path(client: TestClient) -> None:
    response = client.post(
        "/publications/from-pdf",
        data={
            "title": "Uploaded extra",
            "license_id": "cc-by",
            "organism_model": "mouse",
            "exposure": "hindlimb_unloading",
        },
        files={"file": ("paper.pdf", SAMPLE_PDF.read_bytes(), "application/pdf")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["publication_id"].startswith("local_")
    assert payload["pdf_stored"] is True
    assert payload["collection"] == "local_extras"
    assert payload["human_approval"] == "pending"
    assert payload["organism_model"] == "mouse"
    assert payload["exposure"] == "hindlimb_unloading"

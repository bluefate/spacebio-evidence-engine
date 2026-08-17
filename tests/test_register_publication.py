"""Tests for local-extra publication registration (issue #165)."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from spacebio_evidence_engine.ingestion.register import (
    RegisterError,
    register_from_doi,
    register_from_upload,
)
from spacebio_evidence_engine.storage.local import LocalFileStorage

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PDF = ROOT / "tests" / "fixtures" / "sample_two_page.pdf"


class FakeFetcher:
    def __init__(self, json_payload: dict[str, Any], pdf_bytes: bytes | None = None) -> None:
        self._json = json_payload
        self._pdf = pdf_bytes or b"%PDF-1.4 fake"

    def get_json(self, url: str) -> dict[str, Any]:
        return self._json

    def get_bytes(self, url: str) -> tuple[bytes, str]:
        return self._pdf, "application/pdf"


def _alembic_config(database_url: str) -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", database_url)
    os.environ["DATABASE_URL"] = database_url
    return cfg


@pytest.fixture()
def session(tmp_path: Path) -> Iterator[Session]:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'register.sqlite3'}"
    command.upgrade(_alembic_config(database_url), "head")
    engine = create_engine(database_url)
    with Session(engine) as db_session:
        yield db_session


def test_upload_rejects_non_pdf(session: Session, tmp_path: Path) -> None:
    storage = LocalFileStorage(tmp_path / "pdfs")
    with pytest.raises(RegisterError, match="not a PDF"):
        register_from_upload(
            session,
            storage,
            title="A paper",
            pdf_bytes=b"not a pdf",
            license_id="cc-by",
        )


def test_upload_rejects_blocked_license(session: Session, tmp_path: Path) -> None:
    storage = LocalFileStorage(tmp_path / "pdfs")
    with pytest.raises(RegisterError) as exc_info:
        register_from_upload(
            session,
            storage,
            title="Paywalled paper",
            pdf_bytes=SAMPLE_PDF.read_bytes(),
            license_id="all-rights-reserved",
        )
    assert exc_info.value.status_code == 403


def test_upload_stores_pdf_as_local_extra(session: Session, tmp_path: Path) -> None:
    storage = LocalFileStorage(tmp_path / "pdfs")
    result = register_from_upload(
        session,
        storage,
        title="Local extra muscle paper",
        pdf_bytes=SAMPLE_PDF.read_bytes(),
        license_id="cc-by",
        organism_model="mouse",
        exposure="hindlimb_unloading",
    )
    assert result.publication_id.startswith("local_")
    assert result.corpus_topic == "local_extras"
    assert result.human_approval == "pending"
    assert result.pdf_stored is True
    assert storage.exists(f"{result.publication_id}/{result.publication_id}.pdf")


def test_doi_rejects_paywalled_license(session: Session, tmp_path: Path) -> None:
    storage = LocalFileStorage(tmp_path / "pdfs")
    fetcher = FakeFetcher(
        {
            "message": {
                "title": ["Secret journal article"],
                "URL": "https://doi.org/10.1000/xyz",
                "license": [{"URL": "https://www.elsevier.com/tdm/userlicense/1.0/"}],
            }
        }
    )
    with pytest.raises(RegisterError) as exc_info:
        register_from_doi(
            session,
            storage,
            doi="10.1000/xyz",
            fetcher=fetcher,
        )
    assert exc_info.value.status_code == 403


def test_doi_stores_oa_pdf(session: Session, tmp_path: Path) -> None:
    storage = LocalFileStorage(tmp_path / "pdfs")
    fetcher = FakeFetcher(
        {
            "message": {
                "title": ["Open muscle study"],
                "URL": "https://doi.org/10.1038/s41526-024-00406-3",
                "license": [{"URL": "https://creativecommons.org/licenses/by/4.0/"}],
                "link": [
                    {
                        "URL": "https://example.org/paper.pdf",
                        "content-type": "application/pdf",
                    }
                ],
            }
        },
        pdf_bytes=SAMPLE_PDF.read_bytes(),
    )
    result = register_from_doi(
        session,
        storage,
        doi="10.1038/s41526-024-00406-3",
        organism_model="human",
        exposure="spaceflight",
        fetcher=fetcher,
    )
    assert result.pdf_stored is True
    assert result.license == "cc-by"
    assert result.human_approval == "pending"
    assert result.corpus_topic == "local_extras"

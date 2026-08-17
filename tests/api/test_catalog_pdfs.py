"""API tests for catalog PDF status and missing-file fetch (issue #189)."""

from __future__ import annotations

import os
from pathlib import Path

os.environ["LLM_PROVIDER"] = "openai"

import pytest
from fastapi.testclient import TestClient

from spacebio_api.config import Settings, get_settings
from spacebio_api.main import create_app
from spacebio_evidence_engine.corpus.fetch import FetchResult

get_settings.cache_clear()


def test_catalog_pdf_status_reports_missing(tmp_path: Path) -> None:
    app = create_app(
        Settings(
            APP_ENV="test", LLM_PROVIDER="openai", PDF_STORAGE_LOCAL_ROOT=str(tmp_path / "pdfs")
        )
    )
    client = TestClient(app)
    response = client.get("/publications/catalog-pdfs/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["catalog_count"] == 23
    assert payload["on_disk_count"] == 0
    assert payload["missing_count"] == 23


def test_fetch_missing_uses_fetch_corpus_pdfs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    called: list[Path] = []

    def fake_fetch(root: Path, *, force: bool = False) -> list[FetchResult]:
        called.append(root)
        assert force is False
        return [
            FetchResult("pub_001", "downloaded", path=root / "pub_001.pdf"),
            FetchResult("pub_002", "skipped_already_present", path=root / "pub_002.pdf"),
        ]

    monkeypatch.setattr(
        "spacebio_evidence_engine.corpus.fetch.fetch_corpus_pdfs",
        fake_fetch,
    )
    app = create_app(
        Settings(
            APP_ENV="test", LLM_PROVIDER="openai", PDF_STORAGE_LOCAL_ROOT=str(tmp_path / "pdfs")
        )
    )
    client = TestClient(app)
    response = client.post("/publications/catalog-pdfs/fetch-missing")
    assert response.status_code == 200
    payload = response.json()
    assert payload["downloaded_count"] == 1
    assert payload["downloaded"] == ["pub_001"]
    assert called

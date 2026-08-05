"""Unit tests for the PDF storage abstraction."""

from __future__ import annotations

from pathlib import Path

import pytest

from spacebio_evidence_engine.storage import LocalFileStorage, get_pdf_storage


def test_local_put_and_get(tmp_path: Path) -> None:
    storage = LocalFileStorage(tmp_path)
    data = b"%PDF-1.4 test content"
    key = storage.put("pub-001", "paper.pdf", data)

    assert key == "pub-001/paper.pdf"
    assert storage.exists(key)
    assert storage.get(key) == data


def test_local_get_path(tmp_path: Path) -> None:
    storage = LocalFileStorage(tmp_path)
    data = b"%PDF-1.4 test content"
    key = storage.put("pub-001", "paper.pdf", data)

    path = storage.get_path(key)
    assert path == tmp_path / "pub-001" / "paper.pdf"
    assert path.read_bytes() == data


def test_local_delete(tmp_path: Path) -> None:
    storage = LocalFileStorage(tmp_path)
    key = storage.put("pub-001", "paper.pdf", b"data")
    storage.delete(key)
    assert not storage.exists(key)


def test_get_pdf_storage_uses_env(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PDF_STORAGE_BACKEND", "local")
    monkeypatch.setenv("PDF_STORAGE_LOCAL_ROOT", str(tmp_path))
    storage = get_pdf_storage()
    key = storage.put("pub-002", "article.pdf", b"content")
    assert storage.get(key) == b"content"
    assert storage.exists(key)


def test_get_pdf_storage_unsupported_backend(monkeypatch) -> None:
    monkeypatch.setenv("PDF_STORAGE_BACKEND", "unknown")
    with pytest.raises(ValueError, match="Unsupported PDF storage backend"):
        get_pdf_storage()


def test_local_path_traversal_guard(tmp_path: Path) -> None:
    storage = LocalFileStorage(tmp_path)
    with pytest.raises(ValueError, match="Storage key escapes root"):
        storage.get("../outside.pdf")

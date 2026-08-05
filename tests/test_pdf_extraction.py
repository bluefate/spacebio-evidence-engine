"""Unit tests for PDF text extraction (issue #29)."""

from __future__ import annotations

from pathlib import Path

import fitz
import pytest

from spacebio_evidence_engine.ingestion import (
    PDFEmptyError,
    PDFOpenError,
    extract_pdf_bytes,
    extract_pdf_from_storage,
    extract_pdf_path,
    page_texts,
)
from spacebio_evidence_engine.storage import LocalFileStorage

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SAMPLE_PDF = FIXTURES / "sample_two_page.pdf"


def _write_sample_pdf(path: Path) -> None:
    doc = fitz.open()
    page1 = doc.new_page()
    page1.insert_text((72, 72), "Spacebio page one muscle atrophy.")
    page2 = doc.new_page()
    page2.insert_text((72, 72), "Spacebio page two microgravity unloading.")
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(path)
    doc.close()


@pytest.fixture(scope="session")
def sample_pdf(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Prefer checked-in fixture; otherwise generate a session-local PDF."""
    if SAMPLE_PDF.is_file():
        return SAMPLE_PDF
    path = tmp_path_factory.mktemp("pdf") / "sample_two_page.pdf"
    _write_sample_pdf(path)
    return path


def test_extract_returns_page_ordered_text(sample_pdf: Path) -> None:
    result = extract_pdf_path(sample_pdf)
    assert result.page_count == 2
    assert [p.page_number for p in result.pages] == [1, 2]
    assert result.page_map.page_starts[0] == (0, 1)
    assert result.page_map.page_number_for_offset(0) == 1
    assert result.page_map.page_number_for_offset(len(result.pages[0].text) + 2) == 2
    assert result.page_map.page_number_for_offset(-1) is None
    assert result.page_map.page_number_for_offset(9999) is None
    texts = page_texts(result)
    assert "page one" in texts[0].lower()
    assert "page two" in texts[1].lower()
    assert "page one" in result.full_text.lower()
    assert "page two" in result.full_text.lower()


def test_extract_pdf_bytes_and_storage(sample_pdf: Path, tmp_path: Path) -> None:
    data = sample_pdf.read_bytes()
    from_bytes = extract_pdf_bytes(data, source_key="inline")
    assert from_bytes.page_count == 2
    assert from_bytes.source_key == "inline"
    assert from_bytes.page_map.text_length == len(from_bytes.full_text)
    assert from_bytes.page_map.page_number_for_offset(len(from_bytes.full_text)) is None

    storage = LocalFileStorage(tmp_path)
    key = storage.put("pub_test", "sample.pdf", data)
    from_storage = extract_pdf_from_storage(storage, key)
    assert from_storage.source_key == key
    assert from_storage.page_count == 2
    assert "muscle" in from_storage.pages[0].text.lower()


def test_corrupt_pdf_raises_typed_open_error() -> None:
    with pytest.raises(PDFOpenError):
        extract_pdf_bytes(b"not-a-pdf")


def test_empty_bytes_raise_open_error() -> None:
    with pytest.raises(PDFOpenError, match="empty"):
        extract_pdf_bytes(b"")


def test_missing_path_raises_open_error(tmp_path: Path) -> None:
    with pytest.raises(PDFOpenError):
        extract_pdf_path(tmp_path / "missing.pdf")


def test_blank_pages_raise_empty_error() -> None:
    doc = fitz.open()
    doc.new_page()
    data = doc.tobytes()
    doc.close()
    with pytest.raises(PDFEmptyError):
        extract_pdf_bytes(data)

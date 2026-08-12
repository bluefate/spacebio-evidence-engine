"""Unit tests for ingestion PDF extraction edge cases (issue #37)."""

from __future__ import annotations

from pathlib import Path

import fitz
import pytest

from spacebio_evidence_engine.ingestion import (
    ExtractedPage,
    ExtractionResult,
    PDFExtractionError,
    PDFOpenError,
    extract_pdf_bytes,
    extract_pdf_path,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
SAMPLE_PDF = FIXTURES / "sample_two_page.pdf"


def test_checked_in_fixture_is_multi_page() -> None:
    result = extract_pdf_path(SAMPLE_PDF)

    assert result.page_count == 2
    assert [page.page_number for page in result.pages] == [1, 2]
    assert "page one" in result.pages[0].text.lower()
    assert "page two" in result.pages[1].text.lower()


def test_page_offset_map_skips_blank_pages_without_inventing_offsets() -> None:
    result = ExtractionResult(
        pages=(
            ExtractedPage(page_number=1, text="Abstract\nMicrogravity muscle summary."),
            ExtractedPage(page_number=2, text=""),
            ExtractedPage(page_number=3, text="Methods\nHindlimb unloading protocol."),
        ),
        page_count=3,
        source_key="pub_muscle/sample.pdf",
    )

    page_map = result.page_map

    assert result.full_text == (
        "Abstract\nMicrogravity muscle summary.\n\nMethods\nHindlimb unloading protocol."
    )
    assert page_map.page_starts == ((0, 1), (39, 3))
    assert page_map.page_number_for_offset(0) == 1
    assert page_map.page_number_for_offset(38) == 1
    assert page_map.page_number_for_offset(39) == 3
    assert page_map.page_number_for_offset(page_map.text_length) is None


def test_extraction_failure_closes_open_document(monkeypatch: pytest.MonkeyPatch) -> None:
    class BrokenDocument:
        page_count = 1
        closed = False

        def load_page(self, index: int) -> object:
            raise RuntimeError(f"synthetic page failure {index}")

        def close(self) -> None:
            self.closed = True

    document = BrokenDocument()

    def fake_open(*args: object, **kwargs: object) -> BrokenDocument:
        return document

    monkeypatch.setattr(fitz, "open", fake_open)

    with pytest.raises(PDFExtractionError, match="Unexpected failure"):
        extract_pdf_bytes(b"%PDF-1.7 synthetic")

    assert document.closed is True


def test_source_key_defaults_to_path_string() -> None:
    result = extract_pdf_path(SAMPLE_PDF)

    assert result.source_key == str(SAMPLE_PDF)


def test_directory_path_raises_open_error(tmp_path: Path) -> None:
    with pytest.raises(PDFOpenError, match="not a file"):
        extract_pdf_path(tmp_path)

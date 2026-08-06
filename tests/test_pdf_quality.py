"""Unit tests for PDF quality assessment (issue #25)."""

from __future__ import annotations

from pathlib import Path

import fitz

from spacebio_evidence_engine.ingestion.pdf_quality import (
    PDFQualityCategory,
    PDFQualityResult,
    assess_pdf_bytes,
    assess_pdf_path,
    assess_pdf_url,
    score_publication_pdf,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
LOGO_PNG = Path(__file__).resolve().parent.parent / "docs" / "brand" / "logo-wordmark.png"


def _write_text_pdf(path: Path, *, texts: list[str]) -> None:
    doc = fitz.open()
    rect = fitz.Rect(72, 72, 520, 780)
    for text in texts:
        page = doc.new_page()
        if text:
            page.insert_textbox(rect, text, fontsize=8)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(path)
    doc.close()


def _write_image_only_pdf(path: Path) -> None:
    """Create a PDF page with an image but no extractable text."""
    doc = fitz.open()
    page = doc.new_page()
    if LOGO_PNG.is_file():
        page.insert_image(fitz.Rect(72, 72, 400, 200), filename=str(LOGO_PNG))
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(path)
    doc.close()


def test_good_pdf(tmp_path: Path) -> None:
    path = tmp_path / "good.pdf"
    _write_text_pdf(
        path,
        texts=[
            "This is a long paragraph with enough text to exceed the good text "
            "density threshold when repeated over multiple pages. " * 20,
            "Second page also contains substantial extractable text content. " * 20,
        ],
    )
    result = assess_pdf_path(path)
    assert result.category == PDFQualityCategory.GOOD
    assert result.page_count == 2
    assert result.text_chars > 1000
    assert result.empty_pages == 0
    assert result.has_text_layer


def test_poor_text_pdf(tmp_path: Path) -> None:
    """Low but non-zero text density, no blank pages -> poor_text."""
    path = tmp_path / "poor_text.pdf"
    _write_text_pdf(
        path,
        texts=[
            "Short text. " * 15,
            "Another short page. " * 15,
        ],
    )
    result = assess_pdf_path(path)
    assert result.category == PDFQualityCategory.POOR_TEXT
    assert result.page_count == 2
    assert result.text_chars > 0
    assert 0 < result.text_density < 300


def test_needs_ocr_scanned_pdf(tmp_path: Path) -> None:
    """Image-only page with no text layer -> needs_ocr."""
    path = tmp_path / "scanned.pdf"
    _write_image_only_pdf(path)
    result = assess_pdf_path(path)
    assert result.category == PDFQualityCategory.NEEDS_OCR
    assert result.page_count == 1
    assert result.text_chars == 0
    assert result.image_pages == 1
    assert not result.has_text_layer


def test_needs_ocr_many_blank_pages(tmp_path: Path) -> None:
    """Mostly blank pages with a little text -> needs_ocr."""
    path = tmp_path / "mostly_blank.pdf"
    _write_text_pdf(
        path,
        texts=[
            "",
            "",
            "",
            "",
            "Only one page has any text at all.",
        ],
    )
    result = assess_pdf_path(path)
    assert result.category == PDFQualityCategory.NEEDS_OCR
    assert result.empty_pages / result.page_count >= 0.6


def test_corrupt_bytes() -> None:
    result = assess_pdf_bytes(b"not-a-pdf")
    assert result.category == PDFQualityCategory.CORRUPT
    assert result.error


def test_missing_path(tmp_path: Path) -> None:
    result = assess_pdf_path(tmp_path / "does-not-exist.pdf")
    assert result.category == PDFQualityCategory.MISSING
    assert result.error


def test_empty_bytes() -> None:
    result = assess_pdf_bytes(b"")
    assert result.category == PDFQualityCategory.CORRUPT
    assert "empty" in result.notes.lower()


def test_url_not_pdf() -> None:
    """A URL that returns HTML (or a non-PDF body) is reported as MISSING."""
    result = assess_pdf_url("https://example.com/")
    assert result.category == PDFQualityCategory.MISSING


def _dummy_result(category: PDFQualityCategory, notes: str) -> PDFQualityResult:
    return PDFQualityResult(
        category=category,
        page_count=0,
        text_chars=0,
        empty_pages=0,
        image_pages=0,
        text_density=0.0,
        has_text_layer=False,
        notes=notes,
    )


def test_score_publication_pdf_with_fallback() -> None:
    """When the primary URL is invalid but a PMCID is provided, use fallback."""
    from spacebio_evidence_engine.ingestion import pdf_quality

    def fake_assess(url: str, timeout: float) -> PDFQualityResult:
        if "primary" in url:
            return _dummy_result(
                PDFQualityCategory.MISSING,
                "primary missing",
            )
        if "europepmc" in url:
            return _dummy_result(
                PDFQualityCategory.GOOD,
                "fallback good",
            )
        return _dummy_result(
            PDFQualityCategory.MISSING,
            f"unexpected url: {url}",
        )

    original = pdf_quality.assess_pdf_url
    pdf_quality.assess_pdf_url = fake_assess
    try:
        result = score_publication_pdf("https://primary.example.com/x.pdf", pmcid="PMC12345")
        assert result.category == PDFQualityCategory.GOOD
    finally:
        pdf_quality.assess_pdf_url = original

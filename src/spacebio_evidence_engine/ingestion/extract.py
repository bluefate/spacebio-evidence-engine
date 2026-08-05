"""PyMuPDF-based page-level PDF text extraction (issue #29).

Treat all PDF content as untrusted input. This module only calls PyMuPDF
text extraction APIs and never executes JavaScript, launches files, or
runs embedded content.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from spacebio_evidence_engine.ingestion.errors import (
    PDFEmptyError,
    PDFExtractionError,
    PDFOpenError,
)
from spacebio_evidence_engine.storage.base import PDFStorage


@dataclass(frozen=True, slots=True)
class ExtractedPage:
    """Text extracted from a single PDF page (1-based page numbers)."""

    page_number: int
    text: str


@dataclass(frozen=True, slots=True)
class ExtractionResult:
    """Page-ordered extraction output for one PDF."""

    pages: tuple[ExtractedPage, ...]
    page_count: int
    source_key: str | None = None

    @property
    def full_text(self) -> str:
        """Concatenate page texts in page order with blank-line separators."""
        return "\n\n".join(page.text for page in self.pages if page.text)

    @property
    def page_map(self) -> PageOffsetMap:
        """Return a reusable page-to-offset map for this extraction."""
        return PageOffsetMap.from_extraction(self)


@dataclass(frozen=True, slots=True)
class PageOffsetMap:
    """Page lookup for character offsets in an extracted document."""

    page_starts: tuple[tuple[int, int], ...]

    @classmethod
    def from_extraction(cls, extraction: ExtractionResult) -> PageOffsetMap:
        """Build a page map from an extraction result."""
        page_starts: list[tuple[int, int]] = []
        offset = 0
        first = True
        for page in extraction.pages:
            if not page.text:
                continue
            if not first:
                offset += 2
            page_starts.append((offset, page.page_number))
            offset += len(page.text)
            first = False
        return cls(page_starts=tuple(page_starts))

    def page_number_for_offset(self, offset: int) -> int | None:
        """Return the 1-based page covering ``offset`` when known."""
        if not self.page_starts:
            return None
        current: int | None = self.page_starts[0][1]
        for start, page in self.page_starts:
            if offset >= start:
                current = page
            else:
                break
        return current


def extract_pdf_bytes(data: bytes, *, source_key: str | None = None) -> ExtractionResult:
    """Extract page-ordered text from PDF bytes.

    Raises:
        PDFOpenError: bytes are not a readable PDF.
        PDFEmptyError: document has no pages or no extractable text.
        PDFExtractionError: unexpected extraction failure.
    """
    if not data:
        raise PDFOpenError("PDF bytes are empty")
    return _extract_from_document(data, source_key=source_key)


def extract_pdf_path(path: str | Path, *, source_key: str | None = None) -> ExtractionResult:
    """Extract page-ordered text from a filesystem PDF path."""
    pdf_path = Path(path)
    if not pdf_path.is_file():
        raise PDFOpenError(f"PDF path does not exist or is not a file: {pdf_path}")
    try:
        data = pdf_path.read_bytes()
    except OSError as exc:
        raise PDFOpenError(f"Failed to read PDF path: {pdf_path}") from exc
    return extract_pdf_bytes(data, source_key=source_key or str(pdf_path))


def extract_pdf_from_storage(storage: PDFStorage, key: str) -> ExtractionResult:
    """Load PDF bytes from storage and extract page-ordered text."""
    try:
        data = storage.get(key)
    except FileNotFoundError as exc:
        raise PDFOpenError(f"PDF storage key not found: {key!r}") from exc
    except OSError as exc:
        raise PDFOpenError(f"Failed to read PDF storage key: {key!r}") from exc
    return extract_pdf_bytes(data, source_key=key)


def page_texts(result: ExtractionResult) -> Sequence[str]:
    """Return texts in page order (helper for callers/tests)."""
    return [page.text for page in result.pages]


def _extract_from_document(data: bytes, *, source_key: str | None) -> ExtractionResult:
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:  # pragma: no cover
        raise PDFExtractionError(
            'PyMuPDF is required for PDF extraction. Install with: pip install -e ".[ingestion]"'
        ) from exc

    try:
        # filetype="pdf" avoids sniffing other formats; no JS execution path used.
        document = fitz.open(stream=data, filetype="pdf")
    except Exception as exc:  # noqa: BLE001 — PyMuPDF raises varied errors
        raise PDFOpenError("Failed to open PDF document") from exc

    try:
        if document.page_count < 1:
            raise PDFEmptyError("PDF has no pages")
        pages: list[ExtractedPage] = []
        for index in range(document.page_count):
            page = document.load_page(index)
            # Plain text only — no HTML/JS, no file launches.
            raw = page.get_text("text")
            text = raw if isinstance(raw, str) else ""
            pages.append(ExtractedPage(page_number=index + 1, text=text))
        if not any(page.text.strip() for page in pages):
            raise PDFEmptyError("PDF yielded no extractable text on any page")
        return ExtractionResult(
            pages=tuple(pages),
            page_count=len(pages),
            source_key=source_key,
        )
    except PDFExtractionError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise PDFExtractionError("Unexpected failure during PDF text extraction") from exc
    finally:
        document.close()

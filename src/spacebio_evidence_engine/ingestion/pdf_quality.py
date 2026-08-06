"""PDF quality assessment before ingestion (issue #25).

Categorizes source PDFs by extractability so the pipeline can reject
corrupt/scan-only files or flag them for OCR.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from spacebio_evidence_engine.ingestion.errors import PDFExtractionError

DEFAULT_PDF_DOWNLOAD_TIMEOUT = 30.0
GOOD_TEXT_DENSITY = 300
POOR_TEXT_DENSITY = 100
GOOD_EMPTY_PAGE_RATIO = 0.25
POOR_EMPTY_PAGE_RATIO = 0.60

EUROPEPMC_PDF_URL = "https://europepmc.org/articles/{pmcid}?pdf=render"


class PDFQualityCategory(StrEnum):
    """Quality disposition of a PDF under the MVP extraction model."""

    GOOD = "good"
    POOR_TEXT = "poor_text"
    NEEDS_OCR = "needs_ocr"
    CORRUPT = "corrupt"
    MISSING = "missing"


@dataclass(frozen=True, slots=True)
class PDFQualityResult:
    """Quality assessment of a single PDF."""

    category: PDFQualityCategory
    page_count: int
    text_chars: int
    empty_pages: int
    image_pages: int
    text_density: float
    has_text_layer: bool
    notes: str
    error: str | None = None


def _categorize(
    page_count: int, text_chars: int, empty_pages: int, image_pages: int
) -> tuple[PDFQualityCategory, str]:
    """Map raw page/text metrics to a quality category and human note."""
    empty_ratio = empty_pages / page_count if page_count else 0.0
    density = text_chars / page_count if page_count else 0.0
    base = (
        f"page_count={page_count}, text_chars={text_chars}, "
        f"empty_pages={empty_pages}, image_pages={image_pages}, "
        f"text_density={density:.1f}"
    )

    if text_chars == 0:
        if image_pages > 0:
            return PDFQualityCategory.NEEDS_OCR, f"{base}; image-only PDF, OCR required"
        return PDFQualityCategory.POOR_TEXT, f"{base}; no extractable text or images"

    if empty_ratio >= POOR_EMPTY_PAGE_RATIO or density < POOR_TEXT_DENSITY:
        return (
            PDFQualityCategory.NEEDS_OCR,
            f"{base}; very low text density or many empty pages",
        )
    if empty_ratio >= GOOD_EMPTY_PAGE_RATIO or density < GOOD_TEXT_DENSITY:
        return (
            PDFQualityCategory.POOR_TEXT,
            f"{base}; low text density or several empty pages",
        )
    return PDFQualityCategory.GOOD, f"{base}; text layer present and dense"


def _open_document(data: bytes):
    """Open PDF bytes with PyMuPDF, raising a typed error on failure."""
    try:
        import fitz
    except ImportError as exc:
        raise PDFExtractionError(
            "PyMuPDF is required for PDF quality assessment. "
            'Install with: pip install -e ".[ingestion]"'
        ) from exc
    try:
        return fitz.open(stream=data, filetype="pdf")
    except Exception as exc:
        raise PDFExtractionError("Failed to open PDF document") from exc


def assess_pdf_bytes(data: bytes) -> PDFQualityResult:
    """Assess PDF quality from in-memory bytes.

    Returns a ``PDFQualityResult`` even for corrupt/missing input; the
    ``category`` and ``notes`` fields carry the disposition.
    """
    if not data:
        return PDFQualityResult(
            category=PDFQualityCategory.CORRUPT,
            page_count=0,
            text_chars=0,
            empty_pages=0,
            image_pages=0,
            text_density=0.0,
            has_text_layer=False,
            notes="PDF bytes are empty",
            error="empty bytes",
        )

    document = None
    try:
        document = _open_document(data)
    except PDFExtractionError as exc:
        return PDFQualityResult(
            category=PDFQualityCategory.CORRUPT,
            page_count=0,
            text_chars=0,
            empty_pages=0,
            image_pages=0,
            text_density=0.0,
            has_text_layer=False,
            notes="Failed to open PDF",
            error=str(exc.__cause__ or exc),
        )

    try:
        page_count = document.page_count
        text_chars = 0
        empty_pages = 0
        image_pages = 0
        for index in range(page_count):
            page = document.load_page(index)
            raw = page.get_text("text")
            text = raw if isinstance(raw, str) else ""
            text = text.strip()
            if not text:
                empty_pages += 1
                if page.get_images():
                    image_pages += 1
            text_chars += len(text)

        category, notes = _categorize(page_count, text_chars, empty_pages, image_pages)
        return PDFQualityResult(
            category=category,
            page_count=page_count,
            text_chars=text_chars,
            empty_pages=empty_pages,
            image_pages=image_pages,
            text_density=text_chars / page_count if page_count else 0.0,
            has_text_layer=text_chars > 0,
            notes=notes,
        )
    except Exception as exc:
        return PDFQualityResult(
            category=PDFQualityCategory.CORRUPT,
            page_count=document.page_count if document else 0,
            text_chars=0,
            empty_pages=0,
            image_pages=0,
            text_density=0.0,
            has_text_layer=False,
            notes="Unexpected failure during quality assessment",
            error=str(exc),
        )
    finally:
        if document is not None:
            document.close()


def assess_pdf_path(path: str | Path) -> PDFQualityResult:
    """Assess PDF quality from a filesystem path."""
    pdf_path = Path(path)
    if not pdf_path.is_file():
        return PDFQualityResult(
            category=PDFQualityCategory.MISSING,
            page_count=0,
            text_chars=0,
            empty_pages=0,
            image_pages=0,
            text_density=0.0,
            has_text_layer=False,
            notes="PDF path does not exist or is not a file",
            error=f"not found: {pdf_path}",
        )
    try:
        data = pdf_path.read_bytes()
    except OSError as exc:
        return PDFQualityResult(
            category=PDFQualityCategory.CORRUPT,
            page_count=0,
            text_chars=0,
            empty_pages=0,
            image_pages=0,
            text_density=0.0,
            has_text_layer=False,
            notes="Failed to read PDF path",
            error=str(exc),
        )
    return assess_pdf_bytes(data)


def _request_pdf(url: str, timeout: float) -> bytes:
    """Download a PDF URL with a browser-like user agent."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
            "Accept": "application/pdf,*/*;q=0.9",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def _result_from_download_error(exc: Exception, *, label: str) -> PDFQualityResult:
    """Convert a download failure into a consistent MISSING result."""
    if isinstance(exc, urllib.error.HTTPError):
        notes = f"HTTP {exc.code} when downloading {label}"
    elif isinstance(exc, urllib.error.URLError):
        notes = f"Network error when downloading {label}"
    elif isinstance(exc, TimeoutError):
        notes = f"{label} download timed out"
    else:
        notes = f"Unexpected error when downloading {label}"
    return PDFQualityResult(
        category=PDFQualityCategory.MISSING,
        page_count=0,
        text_chars=0,
        empty_pages=0,
        image_pages=0,
        text_density=0.0,
        has_text_layer=False,
        notes=notes,
        error=str(exc),
    )


def _result_from_invalid_content(label: str) -> PDFQualityResult:
    return PDFQualityResult(
        category=PDFQualityCategory.MISSING,
        page_count=0,
        text_chars=0,
        empty_pages=0,
        image_pages=0,
        text_density=0.0,
        has_text_layer=False,
        notes=f"Downloaded content from {label} is not a PDF",
        error="invalid content",
    )


def assess_pdf_url(url: str, timeout: float = DEFAULT_PDF_DOWNLOAD_TIMEOUT) -> PDFQualityResult:
    """Download and assess a PDF from a URL."""
    try:
        data = _request_pdf(url, timeout=timeout)
    except Exception as exc:  # noqa: BLE001 — network failures are expected
        return _result_from_download_error(exc, label=url)
    if not data.startswith(b"%PDF"):
        return _result_from_invalid_content(url)
    return assess_pdf_bytes(data)


def score_publication_pdf(
    pdf_url: str,
    pmcid: str | None = None,
    timeout: float = DEFAULT_PDF_DOWNLOAD_TIMEOUT,
) -> PDFQualityResult:
    """Assess a publication PDF, with a EuropePMC fallback when a PMCID is known.

    Returns ``MISSING`` only if both the primary URL and any fallback fail to
    yield a valid PDF.
    """
    result = assess_pdf_url(pdf_url, timeout=timeout)
    if result.category not in (PDFQualityCategory.MISSING, PDFQualityCategory.CORRUPT):
        return result
    if not pmcid:
        return result

    fallback = EUROPEPMC_PDF_URL.format(pmcid=pmcid)
    return assess_pdf_url(fallback, timeout=timeout)

"""Ingestion pipeline components (PDF extract, section detection, later chunking)."""

from spacebio_evidence_engine.ingestion.errors import (
    PDFEmptyError,
    PDFExtractionError,
    PDFOpenError,
)
from spacebio_evidence_engine.ingestion.extract import (
    ExtractedPage,
    ExtractionResult,
    PageOffsetMap,
    extract_pdf_bytes,
    extract_pdf_from_storage,
    extract_pdf_path,
    page_texts,
)
from spacebio_evidence_engine.ingestion.sections import (
    SectionDetectionResult,
    SectionLabel,
    SectionSpan,
    detect_sections,
    detect_sections_from_text,
)

__all__ = [
    "ExtractedPage",
    "ExtractionResult",
    "PageOffsetMap",
    "PDFEmptyError",
    "PDFExtractionError",
    "PDFOpenError",
    "SectionDetectionResult",
    "SectionLabel",
    "SectionSpan",
    "detect_sections",
    "detect_sections_from_text",
    "extract_pdf_bytes",
    "extract_pdf_from_storage",
    "extract_pdf_path",
    "page_texts",
]

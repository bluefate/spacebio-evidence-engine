"""Ingestion pipeline components (PDF extract, section detection, chunking, quality)."""

from spacebio_evidence_engine.ingestion.chunking import (
    CHUNKING_STRATEGY_VERSION,
    ChunkingPolicy,
    ChunkingResult,
    TextChunk,
    chunk_extraction,
    chunk_sections,
    chunk_text,
    estimate_tokens,
    make_chunk_id,
)
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
from spacebio_evidence_engine.ingestion.pdf_quality import (
    PDFQualityCategory,
    PDFQualityResult,
    assess_pdf_bytes,
    assess_pdf_path,
    assess_pdf_url,
    score_publication_pdf,
)
from spacebio_evidence_engine.ingestion.sections import (
    SectionDetectionResult,
    SectionLabel,
    SectionSpan,
    detect_sections,
    detect_sections_from_text,
)

__all__ = [
    "CHUNKING_STRATEGY_VERSION",
    "ChunkingPolicy",
    "ChunkingResult",
    "ExtractedPage",
    "ExtractionResult",
    "PageOffsetMap",
    "PDFEmptyError",
    "PDFExtractionError",
    "PDFOpenError",
    "PDFQualityCategory",
    "PDFQualityResult",
    "SectionDetectionResult",
    "SectionLabel",
    "SectionSpan",
    "TextChunk",
    "assess_pdf_bytes",
    "assess_pdf_path",
    "assess_pdf_url",
    "chunk_extraction",
    "chunk_sections",
    "chunk_text",
    "detect_sections",
    "detect_sections_from_text",
    "estimate_tokens",
    "extract_pdf_bytes",
    "extract_pdf_from_storage",
    "extract_pdf_path",
    "make_chunk_id",
    "page_texts",
    "score_publication_pdf",
]

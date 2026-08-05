"""PDF text extraction errors (issue #29).

PDF bytes are untrusted. Extractors must not execute embedded scripts or
other active content — only read text streams via PyMuPDF.
"""

from __future__ import annotations


class PDFExtractionError(Exception):
    """Base error for PDF text extraction failures."""


class PDFOpenError(PDFExtractionError):
    """Raised when PDF bytes/path cannot be opened as a document."""


class PDFEmptyError(PDFExtractionError):
    """Raised when a PDF opens but yields no extractable text on any page."""

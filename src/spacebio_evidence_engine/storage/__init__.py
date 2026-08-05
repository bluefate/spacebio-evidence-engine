"""PDF storage backends for the controlled corpus."""

from __future__ import annotations

from spacebio_evidence_engine.storage.base import PDFStorage
from spacebio_evidence_engine.storage.config import StorageSettings, get_pdf_storage
from spacebio_evidence_engine.storage.local import LocalFileStorage

__all__ = ["PDFStorage", "LocalFileStorage", "StorageSettings", "get_pdf_storage"]

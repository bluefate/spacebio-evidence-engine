"""PDF storage factory and environment-based configuration."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from spacebio_evidence_engine.storage.base import PDFStorage
from spacebio_evidence_engine.storage.local import LocalFileStorage


class StorageSettings(BaseSettings):
    """Environment configuration for the PDF storage backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    pdf_storage_backend: str = Field(default="local", alias="PDF_STORAGE_BACKEND")
    pdf_storage_local_root: str = Field(default="data/pdfs", alias="PDF_STORAGE_LOCAL_ROOT")


def get_pdf_storage(settings: StorageSettings | None = None) -> PDFStorage:
    """Return a configured PDF storage backend."""
    settings = settings or StorageSettings()
    backend = settings.pdf_storage_backend.lower()
    if backend == "local":
        root = Path(settings.pdf_storage_local_root).expanduser()
        root.mkdir(parents=True, exist_ok=True)
        return LocalFileStorage(root)
    raise ValueError(f"Unsupported PDF storage backend: {settings.pdf_storage_backend!r}")

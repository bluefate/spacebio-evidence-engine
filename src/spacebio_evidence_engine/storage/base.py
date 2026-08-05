"""Storage protocol for publication PDFs."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class PDFStorage(Protocol):
    """Backend-agnostic contract for storing and retrieving PDF bytes."""

    def put(self, publication_id: str, filename: str, data: bytes) -> str:
        """Store PDF data and return a backend-specific key for later retrieval."""
        ...

    def get(self, key: str) -> bytes:
        """Return the PDF bytes identified by ``key``."""
        ...

    def exists(self, key: str) -> bool:
        """Return ``True`` if the PDF identified by ``key`` is stored."""
        ...

    def delete(self, key: str) -> None:
        """Delete the PDF identified by ``key``."""
        ...

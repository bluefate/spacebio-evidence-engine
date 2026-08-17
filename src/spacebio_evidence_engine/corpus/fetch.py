"""Download approved corpus PDFs from recorded ``pdf_url`` values (issue #171)."""

from __future__ import annotations

import urllib.error
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from spacebio_evidence_engine.corpus.inventory import load_inventory_manifest

PDF_MAGIC = b"%PDF"


class FetchCorpusPDFError(RuntimeError):
    """Raised when a corpus PDF download cannot be completed safely."""


class _HTTPResponse(Protocol):
    """Minimal response surface for fetching a binary payload."""

    @property
    def headers(self) -> Mapping[str, str]: ...

    def read(self) -> bytes: ...

    def __enter__(self) -> _HTTPResponse: ...

    def __exit__(self, *exc: object) -> None: ...


class _HTTPClient(Protocol):
    """Swappable HTTP client for fetching PDFs (tests use a fake)."""

    def open(self, url: str, *, timeout: float) -> _HTTPResponse: ...


class _UrllibClient:
    """Default stdlib HTTP client."""

    def open(self, url: str, *, timeout: float) -> _HTTPResponse:
        return urllib.request.urlopen(url, timeout=timeout)  # type: ignore[return-value]


@dataclass(frozen=True)
class FetchResult:
    """Outcome of one PDF fetch attempt."""

    publication_id: str
    outcome: str
    path: Path | None = None
    message: str = ""


def _should_fetch_pdf(record: object) -> tuple[bool, str]:
    """Decide whether a manifest row should be downloaded."""
    from spacebio_evidence_engine.corpus.inventory import CorpusInventoryRecord

    record = record if isinstance(record, CorpusInventoryRecord) else None  # type: ignore[unreachable]
    if record is None:
        return False, "skipped_invalid_record"

    if record.inclusion_pass != "yes":
        return False, "skipped_not_included"

    if record.pdf_quality in {"corrupt", "missing"}:
        return False, "skipped_pdf_quality_blocked"

    if not record.pdf_url or not record.pdf_url.startswith(("http://", "https://")):
        return False, "skipped_no_pdf_url"

    return True, ""


def _download_pdf(
    pdf_url: str,
    output_path: Path,
    timeout: float,
    client: _HTTPClient,
) -> tuple[bool, str]:
    """Download the URL, validate PDF magic, and write to ``output_path``.

    Returns ``(success, message)``. Does not raise on network or validation
    errors; callers turn failures into ``FetchResult`` outcomes.
    """
    try:
        with client.open(pdf_url, timeout=timeout) as response:
            data = response.read()
            headers = dict(response.headers)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return False, f"download failed: {exc}"

    if not data.startswith(PDF_MAGIC):
        return False, "response did not start with PDF magic bytes (%PDF)"

    content_type = headers.get("Content-Type", "").lower()
    if content_type and "pdf" not in content_type:
        # Some hosts serve application/octet-stream, so magic bytes are the
        # ground-truth check. If a Content-Type is present and not PDF, warn.
        pass

    output_path.write_bytes(data)
    return True, ""


def fetch_corpus_pdfs(
    output_root: Path,
    *,
    manifest_path: Path | None = None,
    force: bool = False,
    timeout: float = 60.0,
    http_client: _HTTPClient | None = None,
) -> list[FetchResult]:
    """Download PDFs for approved manifest rows into ``output_root``.

    Args:
        output_root: Destination directory (created if missing).
        manifest_path: Path to the corpus manifest CSV.
        force: Overwrite files already present.
        timeout: Per-request timeout in seconds.
        http_client: Optional injectable HTTP client for tests.

    Returns:
        One ``FetchResult`` for every manifest row.
    """
    output_root.mkdir(parents=True, exist_ok=True)
    records = load_inventory_manifest(manifest_path)
    client = http_client or _UrllibClient()

    results: list[FetchResult] = []
    for record in records:
        ok, reason = _should_fetch_pdf(record)
        if not ok:
            results.append(FetchResult(record.publication_id, reason))
            continue

        output_path = output_root / f"{record.publication_id}.pdf"
        if output_path.is_file() and not force:
            results.append(
                FetchResult(record.publication_id, "skipped_already_present", path=output_path)
            )
            continue

        ok, message = _download_pdf(record.pdf_url, output_path, timeout, client)
        if not ok:
            results.append(FetchResult(record.publication_id, "failed_download", message=message))
            continue

        results.append(FetchResult(record.publication_id, "downloaded", path=output_path))

    return results


def corpus_pdf_disk_status(
    output_root: Path,
    *,
    manifest_path: Path | None = None,
) -> dict[str, object]:
    """Report which approved catalog PDFs exist under ``output_root``."""
    output_root.mkdir(parents=True, exist_ok=True)
    records = load_inventory_manifest(manifest_path)
    present: list[str] = []
    missing: list[str] = []
    for record in records:
        path = output_root / f"{record.publication_id}.pdf"
        if path.is_file():
            present.append(record.publication_id)
        else:
            missing.append(record.publication_id)
    return {
        "catalog_count": len(records),
        "on_disk": present,
        "missing": missing,
        "on_disk_count": len(present),
        "missing_count": len(missing),
        "output_root": str(output_root),
    }

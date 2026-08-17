"""Tests for corpus PDF fetch (issue #171)."""

from __future__ import annotations

import csv
from collections.abc import Mapping
from pathlib import Path

from spacebio_evidence_engine.corpus.fetch import (
    _HTTPResponse,
    fetch_corpus_pdfs,
)

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PDF = ROOT / "tests" / "fixtures" / "sample_two_page.pdf"

MANIFEST_FIELDS = [
    "publication_id",
    "title",
    "doi",
    "pmcid",
    "pmid",
    "year",
    "journal",
    "authors",
    "license",
    "license_status",
    "access_restriction_notes",
    "redistribution_notes",
    "source_url",
    "pdf_url",
    "fulltext_url",
    "pdf_quality",
    "pdf_quality_notes",
    "corpus_topic",
    "organism_model",
    "exposure",
    "selection_notes",
    "inclusion_pass",
    "exclusion_flags",
    "ingestion_status",
    "human_approval",
]


class FakeHTTPResponse:
    def __init__(self, body: bytes, *, content_type: str = "application/pdf") -> None:
        self._body = body
        self._headers = {"Content-Type": content_type}

    @property
    def headers(self) -> Mapping[str, str]:
        return self._headers

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> FakeHTTPResponse:
        return self

    def __exit__(self, *exc: object) -> None:
        pass


class FakeHTTPClient:
    def __init__(self, *, content: dict[str, tuple[bytes, str]]) -> None:
        self.content = content
        self.calls: list[tuple[str, float]] = []

    def open(self, url: str, *, timeout: float) -> _HTTPResponse:
        self.calls.append((url, timeout))
        if url not in self.content:
            raise OSError(f"network error: {url}")
        body, content_type = self.content[url]
        return FakeHTTPResponse(body, content_type=content_type)


def _write_manifest(
    path: Path,
    rows: list[dict[str, str]],
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        for row in rows:
            full_row = {field: row.get(field, "") for field in MANIFEST_FIELDS}
            full_row.setdefault("ingestion_status", "not_ingested")
            full_row.setdefault("exclusion_flags", "none")
            full_row.setdefault("human_approval", "approved")
            full_row.setdefault("corpus_topic", "microgravity_skeletal_muscle")
            full_row.setdefault("organism_model", "human")
            full_row.setdefault("exposure", "spaceflight")
            full_row.setdefault("license", "cc-by")
            full_row.setdefault("license_status", "approved_oa_candidate")
            full_row.setdefault("access_restriction_notes", "Attribution required.")
            full_row.setdefault("redistribution_notes", "Passage quoting allowed.")
            full_row.setdefault("source_url", "https://doi.org/10.1038/s41526-024-00406-3")
            full_row.setdefault("fulltext_url", "https://doi.org/10.1038/s41526-024-00406-3")
            full_row.setdefault("year", "2024")
            full_row.setdefault("journal", "npj Microgravity")
            full_row.setdefault("authors", "Fixture Author")
            full_row.setdefault("title", "Fixture paper")
            writer.writerow(full_row)


def _base_row(publication_id: str, pdf_url: str, *, pdf_quality: str = "good") -> dict[str, str]:
    return {
        "publication_id": publication_id,
        "pdf_url": pdf_url,
        "pdf_quality": pdf_quality,
    }


def test_fetch_downloads_pdf_and_writes_file(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.csv"
    _write_manifest(manifest, [_base_row("pub_001", "https://example.org/pub_001.pdf")])
    output_root = tmp_path / "pdfs"
    pdf_bytes = SAMPLE_PDF.read_bytes()
    client = FakeHTTPClient(
        content={"https://example.org/pub_001.pdf": (pdf_bytes, "application/pdf")}
    )

    results = fetch_corpus_pdfs(
        output_root,
        manifest_path=manifest,
        http_client=client,
    )

    assert len(results) == 1
    assert results[0].publication_id == "pub_001"
    assert results[0].outcome == "downloaded"
    assert results[0].path == output_root / "pub_001.pdf"
    assert (output_root / "pub_001.pdf").read_bytes() == pdf_bytes


def test_fetch_is_idempotent(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.csv"
    _write_manifest(manifest, [_base_row("pub_001", "https://example.org/pub_001.pdf")])
    output_root = tmp_path / "pdfs"
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n%%EOF"
    client = FakeHTTPClient(
        content={"https://example.org/pub_001.pdf": (pdf_bytes, "application/pdf")}
    )

    first = fetch_corpus_pdfs(output_root, manifest_path=manifest, http_client=client)
    assert first[0].outcome == "downloaded"

    second = fetch_corpus_pdfs(output_root, manifest_path=manifest, http_client=client)
    assert second[0].outcome == "skipped_already_present"
    assert (output_root / "pub_001.pdf").read_bytes() == pdf_bytes


def test_fetch_force_overwrites_existing(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.csv"
    _write_manifest(manifest, [_base_row("pub_001", "https://example.org/pub_001.pdf")])
    output_root = tmp_path / "pdfs"
    first_bytes = b"%PDF-1.4 first"
    second_bytes = b"%PDF-1.4 second"
    client = FakeHTTPClient(
        content={
            "https://example.org/pub_001.pdf": (first_bytes, "application/pdf"),
        }
    )

    fetch_corpus_pdfs(output_root, manifest_path=manifest, http_client=client)
    client.content["https://example.org/pub_001.pdf"] = (second_bytes, "application/pdf")

    results = fetch_corpus_pdfs(output_root, manifest_path=manifest, force=True, http_client=client)
    assert results[0].outcome == "downloaded"
    assert (output_root / "pub_001.pdf").read_bytes() == second_bytes


def test_fetch_skips_missing_url_and_quality_blocked(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.csv"
    _write_manifest(
        manifest,
        [
            _base_row("pub_001", "", pdf_quality="good"),
            _base_row("pub_002", "https://example.org/pub_002.pdf", pdf_quality="corrupt"),
            _base_row("pub_003", "https://example.org/pub_003.pdf", pdf_quality="missing"),
        ],
    )
    output_root = tmp_path / "pdfs"
    client = FakeHTTPClient(content={})

    results = fetch_corpus_pdfs(output_root, manifest_path=manifest, http_client=client)

    assert {r.outcome for r in results} == {
        "skipped_no_pdf_url",
        "skipped_pdf_quality_blocked",
    }
    assert not any((output_root / f"{r.publication_id}.pdf").exists() for r in results)


def test_fetch_rejects_non_pdf_response(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.csv"
    _write_manifest(manifest, [_base_row("pub_001", "https://example.org/pub_001.pdf")])
    output_root = tmp_path / "pdfs"
    client = FakeHTTPClient(
        content={"https://example.org/pub_001.pdf": (b"<html>not a pdf</html>", "text/html")}
    )

    results = fetch_corpus_pdfs(output_root, manifest_path=manifest, http_client=client)

    assert len(results) == 1
    assert results[0].outcome == "failed_download"
    assert "magic bytes" in results[0].message.lower()
    assert not (output_root / "pub_001.pdf").exists()

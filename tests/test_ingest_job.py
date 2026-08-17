"""Tests for local corpus ingest (issue #163)."""

from __future__ import annotations

import csv
import os
from collections.abc import Iterator, Sequence
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from spacebio_evidence_engine.db.models import Chunk, ChunkEmbedding
from spacebio_evidence_engine.db.vector_types import MVP_EMBEDDING_DIMENSION
from spacebio_evidence_engine.embeddings import EmbeddingProvider
from spacebio_evidence_engine.ingestion.ingest_job import (
    find_local_pdf,
    ingest_local_corpus,
)
from spacebio_evidence_engine.ingestion.status import IngestionStatus, get_ingestion_status

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


class FakeEmbeddingProvider(EmbeddingProvider):
    def __init__(self, *, dimension: int = MVP_EMBEDDING_DIMENSION) -> None:
        self._dimension = dimension

    @property
    def model_name(self) -> str:
        return "fake-ingest-v1"

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        vector = [0.0] * self._dimension
        vector[0] = float(len(text))
        return vector


def _alembic_config(database_url: str) -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", database_url)
    os.environ["DATABASE_URL"] = database_url
    return cfg


@pytest.fixture()
def session(tmp_path: Path) -> Iterator[Session]:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'ingest.sqlite3'}"
    command.upgrade(_alembic_config(database_url), "head")
    engine = create_engine(database_url)
    with Session(engine) as db_session:
        yield db_session


def _write_manifest(
    path: Path, publication_id: str, *, ingestion_status: str = "not_ingested"
) -> None:
    row = {
        "publication_id": publication_id,
        "title": "Fixture paper on microgravity skeletal muscle",
        "doi": "10.1038/s41526-024-00406-3",
        "pmcid": "",
        "pmid": "",
        "year": "2024",
        "journal": "npj Microgravity",
        "authors": "Fixture Author",
        "license": "cc-by",
        "license_status": "approved_oa_candidate",
        "access_restriction_notes": "Attribution required.",
        "redistribution_notes": "Passage quoting allowed.",
        "source_url": "https://doi.org/10.1038/s41526-024-00406-3",
        "pdf_url": "https://example.org/fixture.pdf",
        "fulltext_url": "https://doi.org/10.1038/s41526-024-00406-3",
        "pdf_quality": "good",
        "pdf_quality_notes": "",
        "corpus_topic": "microgravity_skeletal_muscle",
        "organism_model": "human",
        "exposure": "spaceflight",
        "selection_notes": "test",
        "inclusion_pass": "yes",
        "exclusion_flags": "none",
        "ingestion_status": ingestion_status,
        "human_approval": "approved",
    }
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerow(row)


def test_find_local_pdf_direct_and_nested(tmp_path: Path) -> None:
    root = tmp_path / "pdfs"
    root.mkdir()
    assert find_local_pdf(root, "pub_001") is None
    (root / "pub_001.pdf").write_bytes(b"%PDF-1.4")
    found = find_local_pdf(root, "pub_001")
    assert found is not None
    assert found.name == "pub_001.pdf"
    nested = root / "pub_002"
    nested.mkdir()
    (nested / "paper.pdf").write_bytes(b"%PDF-1.4")
    nested_found = find_local_pdf(root, "pub_002")
    assert nested_found is not None
    assert nested_found.name == "paper.pdf"


def test_ingest_skips_missing_pdf(session: Session, tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.csv"
    _write_manifest(manifest, "pub_missing")
    pdf_root = tmp_path / "pdfs"
    pdf_root.mkdir()
    summary = ingest_local_corpus(
        session,
        pdf_root=pdf_root,
        manifest_path=manifest,
        embedding_provider=FakeEmbeddingProvider(),
    )
    assert summary.skipped_count == 1
    assert summary.results[0].outcome == "skipped_missing_pdf"
    assert get_ingestion_status(session, "pub_missing") is IngestionStatus.FAILED
    assert session.scalar(select(func.count(Chunk.chunk_id))) == 0


def test_ingest_persists_chunks_and_embeddings(session: Session, tmp_path: Path) -> None:
    publication_id = "pub_ingest_ok"
    manifest = tmp_path / "manifest.csv"
    _write_manifest(manifest, publication_id)
    pdf_root = tmp_path / "pdfs"
    pdf_root.mkdir()
    (pdf_root / f"{publication_id}.pdf").write_bytes(SAMPLE_PDF.read_bytes())

    first = ingest_local_corpus(
        session,
        pdf_root=pdf_root,
        manifest_path=manifest,
        embedding_provider=FakeEmbeddingProvider(),
    )
    assert first.ingested_count == 1
    assert first.results[0].chunk_count > 0
    assert first.results[0].embedded_count == first.results[0].chunk_count
    assert get_ingestion_status(session, publication_id) is IngestionStatus.SUCCEEDED

    chunk_count = session.scalar(select(func.count(Chunk.chunk_id))) or 0
    embed_count = session.scalar(select(func.count(ChunkEmbedding.chunk_id))) or 0
    assert chunk_count == first.results[0].chunk_count
    assert embed_count == chunk_count

    second = ingest_local_corpus(
        session,
        pdf_root=pdf_root,
        manifest_path=manifest,
        embedding_provider=FakeEmbeddingProvider(),
    )
    assert second.ingested_count == 1
    assert (session.scalar(select(func.count(Chunk.chunk_id))) or 0) == chunk_count

"""End-to-end ingestion integration test (issue #38)."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, func, select, text
from sqlalchemy.orm import Session

from spacebio_evidence_engine.db.models import Chunk
from spacebio_evidence_engine.ingestion import (
    IngestionStatus,
    chunk_extraction,
    extract_pdf_from_storage,
    get_ingestion_status,
    reprocess_publication,
    transition_ingestion_status,
)
from spacebio_evidence_engine.storage.local import LocalFileStorage

ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_ID = "pub_ingest_e2e"


def _alembic_config(database_url: str) -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", database_url)
    os.environ["DATABASE_URL"] = database_url
    return cfg


@pytest.mark.integration
def test_pdf_store_extract_chunk_persist_status_succeeds(tmp_path: Path) -> None:
    """Compose the existing ingestion primitives against a migrated test DB."""

    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://spacebio:spacebio@localhost:5432/spacebio",
    )
    require = os.environ.get("SPACEBIO_REQUIRE_DB", "").lower() in {"1", "true", "yes"}
    try:
        command.upgrade(_alembic_config(database_url), "head")
        engine = create_engine(database_url)
        _delete_fixture_rows(engine)
    except Exception as exc:  # noqa: BLE001
        if require:
            pytest.fail(f"PostgreSQL ingestion integration setup failed: {exc}")
        pytest.skip(f"PostgreSQL not available for ingestion integration: {exc}")

    storage = LocalFileStorage(tmp_path / "pdfs")
    sample_pdf = ROOT / "tests" / "fixtures" / "sample_two_page.pdf"
    pdf_key = storage.put(PUBLICATION_ID, sample_pdf.name, sample_pdf.read_bytes())

    with Session(engine) as session:
        session.execute(
            text(
                """
                INSERT INTO publications (
                    publication_id, title, source_url, license_status, corpus_topic,
                    ingestion_status, pdf_path, human_approval
                ) VALUES (
                    :publication_id, :title, :source_url, :license_status, :corpus_topic,
                    :ingestion_status, :pdf_path, :human_approval
                )
                """
            ),
            {
                "publication_id": PUBLICATION_ID,
                "title": "Integration fixture for microgravity skeletal muscle ingestion",
                "source_url": "https://example.org/spacebio/ingestion-fixture",
                "license_status": "approved_oa_candidate",
                "corpus_topic": "microgravity_skeletal_muscle",
                "ingestion_status": IngestionStatus.NOT_INGESTED.value,
                "pdf_path": pdf_key,
                "human_approval": "approved",
            },
        )
        session.commit()

        transition_ingestion_status(
            session,
            PUBLICATION_ID,
            IngestionStatus.PROCESSING,
            reason="integration test started ingestion",
            actor="pytest",
        )
        extraction = extract_pdf_from_storage(storage, pdf_key)
        chunking = chunk_extraction(extraction, publication_id=PUBLICATION_ID)
        assert chunking.chunks, "fixture PDF should produce at least one persisted chunk"

        for chunk in chunking.chunks:
            session.execute(
                text(
                    """
                    INSERT INTO chunks (
                        chunk_id, publication_id, section, chunk_text, content_hash,
                        start_offset, end_offset, chunking_strategy_version,
                        page_start, page_end, section_heading
                    ) VALUES (
                        :chunk_id, :publication_id, :section, :chunk_text, :content_hash,
                        :start_offset, :end_offset, :chunking_strategy_version,
                        :page_start, :page_end, :section_heading
                    )
                    """
                ),
                {
                    "chunk_id": chunk.chunk_id,
                    "publication_id": chunk.publication_id,
                    "section": chunk.section.value,
                    "chunk_text": chunk.chunk_text,
                    "content_hash": hashlib.sha256(chunk.chunk_text.encode("utf-8")).hexdigest(),
                    "start_offset": chunk.start_offset,
                    "end_offset": chunk.end_offset,
                    "chunking_strategy_version": chunk.chunking_strategy_version,
                    "page_start": chunk.start_page,
                    "page_end": chunk.end_page,
                    "section_heading": chunk.section_heading,
                },
            )

        transition_ingestion_status(
            session,
            PUBLICATION_ID,
            IngestionStatus.SUCCEEDED,
            reason="integration test persisted chunks",
            actor="pytest",
        )
        session.commit()

        loaded = (
            session.execute(
                text(
                    """
                SELECT
                    p.publication_id,
                    p.ingestion_status,
                    p.pdf_path,
                    c.chunk_id,
                    c.section,
                    c.start_offset,
                    c.end_offset,
                    c.page_start,
                    c.page_end,
                    c.chunking_strategy_version,
                    c.section_heading,
                    c.content_hash,
                    c.chunk_text
                FROM publications p
                JOIN chunks c ON c.publication_id = p.publication_id
                WHERE p.publication_id = :publication_id
                ORDER BY c.start_offset
                """
                ),
                {"publication_id": PUBLICATION_ID},
            )
            .mappings()
            .all()
        )

        assert get_ingestion_status(session, PUBLICATION_ID) is IngestionStatus.SUCCEEDED
        assert len(loaded) == len(chunking.chunks)
        first_row = loaded[0]
        first_chunk = chunking.chunks[0]
        assert first_row["pdf_path"] == pdf_key
        assert first_row["chunk_id"] == first_chunk.chunk_id
        assert first_row["section"] == first_chunk.section.value
        assert first_row["start_offset"] == first_chunk.start_offset
        assert first_row["end_offset"] == first_chunk.end_offset
        assert first_row["page_start"] == first_chunk.start_page
        assert first_row["page_end"] == first_chunk.end_page
        assert first_row["chunking_strategy_version"] == first_chunk.chunking_strategy_version
        assert first_row["section_heading"] == first_chunk.section_heading
        assert (
            first_row["content_hash"]
            == hashlib.sha256(first_chunk.chunk_text.encode("utf-8")).hexdigest()
        )
        assert "microgravity" in first_row["chunk_text"].lower()

    _delete_fixture_rows(engine)


@pytest.mark.integration
def test_reprocess_publication_replaces_chunks(tmp_path: Path) -> None:
    """Reprocessing a publication deletes stale chunks and writes a new set."""

    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://spacebio:spacebio@localhost:5432/spacebio",
    )
    require = os.environ.get("SPACEBIO_REQUIRE_DB", "").lower() in {"1", "true", "yes"}
    try:
        command.upgrade(_alembic_config(database_url), "head")
        engine = create_engine(database_url)
        _delete_fixture_rows(engine)
    except Exception as exc:  # noqa: BLE001
        if require:
            pytest.fail(f"PostgreSQL reprocessing integration setup failed: {exc}")
        pytest.skip(f"PostgreSQL not available for reprocessing integration: {exc}")

    storage = LocalFileStorage(tmp_path / "pdfs")
    sample_pdf = ROOT / "tests" / "fixtures" / "sample_two_page.pdf"
    pdf_key = storage.put(PUBLICATION_ID, sample_pdf.name, sample_pdf.read_bytes())

    with Session(engine) as session:
        session.execute(
            text(
                """
                INSERT INTO publications (
                    publication_id, title, source_url, license_status, corpus_topic,
                    ingestion_status, pdf_path, human_approval
                ) VALUES (
                    :publication_id, :title, :source_url, :license_status, :corpus_topic,
                    :ingestion_status, :pdf_path, :human_approval
                )
                """
            ),
            {
                "publication_id": PUBLICATION_ID,
                "title": "Integration fixture for reprocessing",
                "source_url": "https://example.org/spacebio/reprocess-fixture",
                "license_status": "approved_oa_candidate",
                "corpus_topic": "microgravity_skeletal_muscle",
                "ingestion_status": IngestionStatus.SUCCEEDED.value,
                "pdf_path": pdf_key,
                "human_approval": "approved",
            },
        )
        session.commit()

        # Seed two stale chunks that should be removed during reprocessing.
        session.add(
            Chunk(
                chunk_id="chk_old_1",
                publication_id=PUBLICATION_ID,
                section="results",
                chunk_text="stale old results chunk",
                content_hash=hashlib.sha256(b"stale old results chunk").hexdigest(),
                start_offset=0,
                end_offset=24,
                chunking_strategy_version="0.0.0",
                page_start=1,
                page_end=1,
            )
        )
        session.add(
            Chunk(
                chunk_id="chk_old_2",
                publication_id=PUBLICATION_ID,
                section="methods",
                chunk_text="stale old methods chunk",
                content_hash=hashlib.sha256(b"stale old methods chunk").hexdigest(),
                start_offset=25,
                end_offset=50,
                chunking_strategy_version="0.0.0",
                page_start=2,
                page_end=2,
            )
        )
        session.commit()

        result = reprocess_publication(session, PUBLICATION_ID, storage=storage, actor="pytest")
        assert result.publication_id == PUBLICATION_ID
        assert result.status is IngestionStatus.SUCCEEDED
        assert result.previous_chunk_count == 2
        assert result.new_chunk_count > 0

        assert get_ingestion_status(session, PUBLICATION_ID) is IngestionStatus.SUCCEEDED

        # Stale chunks are gone.
        assert session.get(Chunk, "chk_old_1") is None
        assert session.get(Chunk, "chk_old_2") is None

        # New chunks match the count returned and are tied to the publication.
        new_count = (
            session.execute(
                select(func.count(Chunk.chunk_id)).where(Chunk.publication_id == PUBLICATION_ID)
            ).scalar()
            or 0
        )
        assert new_count == result.new_chunk_count

    _delete_fixture_rows(engine)


def _delete_fixture_rows(engine: Engine) -> None:
    params = {"publication_id": PUBLICATION_ID}
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                DELETE FROM chunk_embeddings
                WHERE chunk_id IN (
                    SELECT chunk_id FROM chunks WHERE publication_id = :publication_id
                )
                """
            ),
            params,
        )
        conn.execute(text("DELETE FROM chunks WHERE publication_id = :publication_id"), params)
        conn.execute(
            text("DELETE FROM publications WHERE publication_id = :publication_id"),
            params,
        )

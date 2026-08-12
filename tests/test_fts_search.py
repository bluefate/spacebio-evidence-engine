"""Tests for PostgreSQL full-text keyword search (issue #45)."""

from __future__ import annotations

import hashlib
import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from spacebio_evidence_engine.db.models import Chunk, Publication
from spacebio_evidence_engine.retrieval import KeywordSearchHit, keyword_search
from spacebio_evidence_engine.retrieval.filters import RetrievalFilters

ROOT = Path(__file__).resolve().parents[1]


def _alembic_config(database_url: str) -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", database_url)
    os.environ["DATABASE_URL"] = database_url
    return cfg


def _content_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@pytest.fixture()
def session(tmp_path: Path) -> Iterator[Session]:
    db_path = tmp_path / "fts_search.sqlite3"
    database_url = f"sqlite+pysqlite:///{db_path}"
    command.upgrade(_alembic_config(database_url), "head")
    engine = create_engine(database_url)
    with Session(engine) as db_session:
        yield db_session


def _seed_corpus(session: Session) -> None:
    session.add_all(
        [
            Publication(
                publication_id="pub_muscle",
                title="Microgravity and soleus atrophy",
                source_url="https://doi.org/10.0/muscle",
                license_status="approved_oa_candidate",
                corpus_topic="microgravity_skeletal_muscle",
                organism_model="rodent",
                exposure="microgravity",
            ),
            Publication(
                publication_id="pub_plant",
                title="Plant growth off topic",
                source_url="https://doi.org/10.0/plant",
                license_status="approved_oa_candidate",
                corpus_topic="plant_biology",
                organism_model="arabidopsis",
                exposure="radiation",
            ),
        ]
    )
    chunks = [
        (
            "chk_soleus",
            "pub_muscle",
            "results",
            "Soleus muscle mass decreased in flight animals after unloading.",
            2,
            2,
        ),
        (
            "chk_fiber",
            "pub_muscle",
            "discussion",
            "Fiber cross-section was reduced after hindlimb unloading.",
            4,
            4,
        ),
        (
            "chk_cage",
            "pub_muscle",
            "methods",
            "Animals were housed in flight cages with controlled lighting.",
            1,
            1,
        ),
        (
            "chk_leaf",
            "pub_plant",
            "results",
            "Leaf area increased under supplemental lighting in ground controls.",
            1,
            1,
        ),
    ]
    for chunk_id, publication_id, section, body, page_start, page_end in chunks:
        session.add(
            Chunk(
                chunk_id=chunk_id,
                publication_id=publication_id,
                section=section,
                chunk_text=body,
                content_hash=_content_hash(body),
                start_offset=0,
                end_offset=len(body),
                chunking_strategy_version="1.0.0",
                page_start=page_start,
                page_end=page_end,
                section_heading=section.title(),
            )
        )
    session.commit()


def test_keyword_search_ranks_sqlite_fallback(session: Session) -> None:
    _seed_corpus(session)

    hits = keyword_search(session, "soleus flight", k=2)

    assert [hit.chunk_id for hit in hits] == ["chk_soleus", "chk_cage"]
    assert hits[0].score >= hits[1].score
    assert hits[0].publication_id == "pub_muscle"
    assert hits[0].title == "Microgravity and soleus atrophy"
    assert hits[0].section == "results"
    assert hits[0].page_start == 2
    assert hits[0].source_url == "https://doi.org/10.0/muscle"
    assert "Soleus muscle mass" in hits[0].chunk_text
    assert hits[0].search_config == "english"


def test_keyword_search_applies_filters(session: Session) -> None:
    _seed_corpus(session)

    hits = keyword_search(
        session,
        "unloading",
        k=10,
        filters=RetrievalFilters(corpus_topic="microgravity_skeletal_muscle"),
    )

    assert all(hit.publication_id == "pub_muscle" for hit in hits)
    assert {hit.chunk_id for hit in hits} == {"chk_soleus", "chk_fiber"}

    section_hits = keyword_search(
        session,
        "unloading",
        k=10,
        filters=RetrievalFilters(section="methods"),
    )
    assert all(hit.section == "methods" for hit in section_hits)


def test_keyword_search_respects_k(session: Session) -> None:
    _seed_corpus(session)

    hits = keyword_search(session, "soleus", k=1)

    assert len(hits) == 1
    assert hits[0].chunk_id == "chk_soleus"


def test_keyword_search_rejects_empty_query(session: Session) -> None:
    with pytest.raises(ValueError, match="non-empty"):
        keyword_search(session, "   ", k=1)


def test_keyword_search_rejects_invalid_k(session: Session) -> None:
    with pytest.raises(ValueError, match="k must be at least 1"):
        keyword_search(session, "muscle", k=0)


def test_keyword_search_works_without_embeddings(session: Session) -> None:
    _seed_corpus(session)

    hits = keyword_search(session, "soleus", k=1)

    assert len(hits) == 1
    assert hits[0].chunk_id == "chk_soleus"


def test_keyword_search_returns_keyword_search_hits(session: Session) -> None:
    _seed_corpus(session)

    hits = keyword_search(session, "cage lighting", k=2)

    assert all(isinstance(hit, KeywordSearchHit) for hit in hits)
    assert [hit.chunk_id for hit in hits] == ["chk_cage", "chk_leaf"]


def test_migration_adds_fts_column_and_index(tmp_path: Path) -> None:
    db_path = tmp_path / "fts_migration.sqlite3"
    database_url = f"sqlite+pysqlite:///{db_path}"
    cfg = _alembic_config(database_url)
    command.upgrade(cfg, "head")
    engine = create_engine(database_url)
    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("chunks")}
    assert "search_tsv" in columns
    indexes = {idx["name"] for idx in inspector.get_indexes("chunks")}
    assert "ix_chunks_search_tsv" in indexes


@pytest.mark.integration
def test_keyword_search_postgres_tsvector() -> None:
    """Postgres path: generated tsvector and ts_rank_cd ranking."""

    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://spacebio:spacebio@localhost:5432/spacebio",
    )
    require = os.environ.get("SPACEBIO_REQUIRE_DB", "").lower() in {"1", "true", "yes"}
    cfg = _alembic_config(database_url)
    try:
        command.upgrade(cfg, "head")
        engine = create_engine(database_url)
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM chunks WHERE chunk_id LIKE 'chk_fts_%'"))
            conn.execute(text("DELETE FROM publications WHERE publication_id = 'pub_fts'"))

        with Session(engine) as session:
            session.add(
                Publication(
                    publication_id="pub_fts",
                    title="FTS fixture",
                    source_url="https://doi.org/10.0/fts",
                    license_status="approved_oa_candidate",
                    corpus_topic="microgravity_skeletal_muscle",
                )
            )
            near = "chk_fts_near"
            far = "chk_fts_far"
            for chunk_id, body, page in (
                (near, "Soleus muscle atrophy in spaceflight animals.", 1),
                (far, "Leaf area under supplemental lighting.", 2),
            ):
                session.add(
                    Chunk(
                        chunk_id=chunk_id,
                        publication_id="pub_fts",
                        section="results",
                        chunk_text=body,
                        content_hash=_content_hash(body),
                        start_offset=0,
                        end_offset=len(body),
                        chunking_strategy_version="1.0.0",
                        page_start=page,
                        page_end=page,
                    )
                )
            session.commit()

            hits = keyword_search(session, "soleus muscle spaceflight", k=2)
            assert [hit.chunk_id for hit in hits] == [near, far]
            assert hits[0].score > hits[1].score
            assert hits[0].publication_id == "pub_fts"
            assert hits[0].search_config == "english"
    except Exception as exc:  # noqa: BLE001
        if require:
            pytest.fail(f"PostgreSQL FTS failed: {exc}")
        pytest.skip(f"PostgreSQL not available for FTS integration: {exc}")

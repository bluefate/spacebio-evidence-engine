"""Tests for retrieval evaluation harness (issue #50)."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator, Sequence
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from spacebio_evidence_engine.db.base import Base
from spacebio_evidence_engine.db.models import Chunk, ChunkEmbedding, Publication
from spacebio_evidence_engine.db.vector_types import MVP_EMBEDDING_DIMENSION
from spacebio_evidence_engine.embeddings import EmbeddingProvider
from spacebio_evidence_engine.evaluation import (
    ReferenceQuestion,
    evaluate_retrieval,
    load_reference_questions,
    write_retrieval_report,
)


class FixtureEmbeddingProvider(EmbeddingProvider):
    """Deterministic provider for retrieval-eval smoke tests."""

    @property
    def model_name(self) -> str:
        return "fixture-eval-v1"

    @property
    def dimension(self) -> int:
        return MVP_EMBEDDING_DIMENSION

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [_axis_vector(index=0) for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        if "clinical drug regimen" in text:
            return _axis_vector(index=3)
        return _axis_vector(index=0)


@pytest.fixture()
def session(tmp_path: Path) -> Iterator[Session]:
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'retrieval_eval.sqlite3'}")
    Base.metadata.create_all(engine)
    with Session(engine) as db_session:
        yield db_session


def test_load_reference_questions_uses_approved_fixture() -> None:
    questions = load_reference_questions("evals/fixtures/reference_questions.json")

    assert len(questions) == 10
    assert questions[0].question_id == "rq_01"
    assert questions[0].candidate_publication_ids == ("pub_001", "pub_008")
    assert questions[7].should_be_answerable is False
    assert questions[7].candidate_publication_ids == ()


def test_retrieval_eval_scores_hits_and_writes_artifact(
    session: Session,
    tmp_path: Path,
) -> None:
    _seed_indexed_fixture(session)
    questions = [
        ReferenceQuestion(
            question_id="rq_fixture_answerable",
            style="factual_lookup",
            question="What skeletal muscle proteome changes were reported?",
            should_be_answerable=True,
            candidate_publication_ids=("pub_001",),
            organism_models=("human",),
            exposures=("spaceflight",),
            evidence_types=("primary_research",),
            notes="fixture",
        ),
        ReferenceQuestion(
            question_id="rq_fixture_insufficient",
            style="sufficiency",
            question="What is the recommended clinical drug regimen?",
            should_be_answerable=False,
            candidate_publication_ids=(),
            organism_models=(),
            exposures=(),
            evidence_types=(),
            notes="fixture",
        ),
    ]
    provider = FixtureEmbeddingProvider()

    report = evaluate_retrieval(session, provider, questions, top_k=2)

    assert report.metrics.question_count == 2
    assert report.metrics.hit_count == 1
    assert report.metrics.hit_rate == pytest.approx(1.0)
    assert report.metrics.mean_reciprocal_rank == pytest.approx(1.0)
    assert report.metrics.unanswerable_with_hits_count == 1
    first = report.questions[0]
    assert first.first_relevant_rank == 1
    assert first.retrieved_chunks[0].chunk_id == "chk_eval_relevant"
    assert first.retrieved_chunks[0].rank == 1
    assert first.retrieved_chunks[0].score == pytest.approx(1.0)
    assert first.retrieved_chunks[0].publication_id == "pub_001"
    assert first.retrieved_chunks[0].source_url == "https://doi.org/10.0/eval"
    assert first.retrieved_chunks[0].page_start == 4
    assert first.retrieved_chunks[0].is_expected_publication is True

    output_path = tmp_path / "retrieval_eval.json"
    written = write_retrieval_report(
        report,
        output_path,
        reference_question_path="evals/fixtures/reference_questions.json",
    )

    payload = json.loads(written.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0.0"
    assert payload["reference_question_path"] == "evals/fixtures/reference_questions.json"
    assert payload["metrics"]["hit_rate"] == pytest.approx(1.0)
    assert payload["questions"][0]["retrieved_chunks"][0]["chunk_id"] == "chk_eval_relevant"
    assert payload["questions"][0]["retrieved_chunks"][0]["rank"] == 1
    assert "chunk_text" not in payload["questions"][0]["retrieved_chunks"][0]


def _seed_indexed_fixture(session: Session) -> None:
    publications = [
        Publication(
            publication_id="pub_001",
            title="Astronaut skeletal muscle proteome",
            source_url="https://doi.org/10.0/eval",
            license_status="approved_oa_candidate",
            corpus_topic="microgravity_skeletal_muscle",
            organism_model="human",
            exposure="spaceflight",
        ),
        Publication(
            publication_id="pub_999",
            title="Off-topic biology",
            source_url="https://doi.org/10.0/off-topic",
            license_status="approved_oa_candidate",
            corpus_topic="microgravity_skeletal_muscle",
            organism_model="human",
            exposure="spaceflight",
        ),
    ]
    session.add_all(publications)

    for chunk_id, publication_id, body, vector, page in (
        (
            "chk_eval_relevant",
            "pub_001",
            "Astronaut skeletal muscle proteome evidence.",
            _axis_vector(index=0),
            4,
        ),
        (
            "chk_eval_irrelevant",
            "pub_999",
            "A less relevant chunk for ranking checks.",
            _axis_vector(index=2),
            9,
        ),
    ):
        session.add(
            Chunk(
                chunk_id=chunk_id,
                publication_id=publication_id,
                section="results",
                chunk_text=body,
                content_hash=hashlib.sha256(body.encode("utf-8")).hexdigest(),
                start_offset=0,
                end_offset=len(body),
                chunking_strategy_version="1.0.0",
                page_start=page,
                page_end=page,
                section_heading="Results",
                embedding_model="fixture-eval-v1",
            )
        )
        session.add(
            ChunkEmbedding(
                chunk_id=chunk_id,
                embedding=vector,
                model_name="fixture-eval-v1",
                dimension=MVP_EMBEDDING_DIMENSION,
            )
        )
    session.commit()


def _axis_vector(*, index: int) -> list[float]:
    vector = [0.0] * MVP_EMBEDDING_DIMENSION
    vector[index] = 1.0
    return vector

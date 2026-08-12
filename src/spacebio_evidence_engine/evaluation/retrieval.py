"""Offline retrieval evaluation against approved reference questions."""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from spacebio_evidence_engine.embeddings import EmbeddingProvider
from spacebio_evidence_engine.retrieval import (
    SemanticSearchFilters,
    SemanticSearchHit,
    semantic_search,
)

REFERENCE_TOPIC = "microgravity_skeletal_muscle"
REFERENCE_SCHEMA_VERSION = "1.0.0"
RESULT_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class ReferenceQuestion:
    """One approved retrieval-evaluation question."""

    question_id: str
    style: str
    question: str
    should_be_answerable: bool
    candidate_publication_ids: tuple[str, ...]
    organism_models: tuple[str, ...]
    exposures: tuple[str, ...]
    evidence_types: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class RetrievedChunk:
    """Serializable retrieval hit with score, rank, and provenance."""

    rank: int
    chunk_id: str
    score: float
    publication_id: str
    title: str
    section: str
    source_url: str
    page_start: int | None
    page_end: int | None
    section_heading: str | None
    model_name: str
    is_expected_publication: bool


@dataclass(frozen=True)
class QuestionRetrievalResult:
    """Per-question retrieval result and expected-evidence metrics."""

    question_id: str
    style: str
    question: str
    should_be_answerable: bool
    expected_publication_ids: tuple[str, ...]
    retrieved_chunks: tuple[RetrievedChunk, ...]
    first_relevant_rank: int | None
    relevant_hit_count: int
    hit: bool
    reciprocal_rank: float
    unexpected_hit_count: int


@dataclass(frozen=True)
class RetrievalEvaluationSummary:
    """Aggregate hit-rate and rank metrics for a retrieval run."""

    question_count: int
    answerable_question_count: int
    unanswerable_question_count: int
    hit_count: int
    hit_rate: float
    mean_reciprocal_rank: float
    mean_first_relevant_rank: float | None
    unanswerable_with_hits_count: int


@dataclass(frozen=True)
class RetrievalEvaluationReport:
    """Complete offline retrieval evaluation report."""

    schema_version: str
    generated_at: str
    topic: str
    reference_question_path: str
    top_k: int
    provider_model: str
    metrics: RetrievalEvaluationSummary
    questions: tuple[QuestionRetrievalResult, ...]


def load_reference_questions(path: str | Path) -> list[ReferenceQuestion]:
    """Load and validate the approved reference-question fixture."""

    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != REFERENCE_SCHEMA_VERSION:
        schema_version = payload.get("schema_version")
        raise ValueError(f"unsupported reference question schema: {schema_version!r}")
    if payload.get("topic") != REFERENCE_TOPIC:
        raise ValueError(f"reference questions must use topic {REFERENCE_TOPIC!r}")
    if payload.get("human_scientific_review") != "approved":
        raise ValueError("reference questions must have approved human scientific review")

    questions: list[ReferenceQuestion] = []
    seen_ids: set[str] = set()
    for raw_question in payload.get("questions", []):
        question_id = str(raw_question["id"])
        if question_id in seen_ids:
            raise ValueError(f"duplicate reference question id: {question_id}")
        seen_ids.add(question_id)

        evidence = raw_question["expected_evidence"]
        candidate_publication_ids = tuple(evidence.get("candidate_publication_ids", []))
        should_be_answerable = bool(evidence["should_be_answerable"])
        if should_be_answerable and not candidate_publication_ids:
            raise ValueError(f"{question_id} is answerable but has no candidate publications")
        if not should_be_answerable and candidate_publication_ids:
            raise ValueError(f"{question_id} is unanswerable but lists candidate publications")

        questions.append(
            ReferenceQuestion(
                question_id=question_id,
                style=str(raw_question["style"]),
                question=str(raw_question["question"]),
                should_be_answerable=should_be_answerable,
                candidate_publication_ids=candidate_publication_ids,
                organism_models=tuple(evidence.get("organism_models", [])),
                exposures=tuple(evidence.get("exposures", [])),
                evidence_types=tuple(evidence.get("evidence_types", [])),
                notes=str(evidence.get("notes", "")),
            )
        )

    if not questions:
        raise ValueError("reference question fixture contains no questions")
    return questions


def evaluate_retrieval(
    session: Session,
    provider: EmbeddingProvider,
    questions: Sequence[ReferenceQuestion],
    *,
    top_k: int = 8,
    search: Callable[
        [Session, EmbeddingProvider, str],
        Sequence[SemanticSearchHit],
    ]
    | None = None,
) -> RetrievalEvaluationReport:
    """Run vector retrieval and compute hit-rate / rank metrics.

    Relevance is measured against candidate publication IDs from the approved
    fixture until ingested passage IDs become available as gold evidence.
    """

    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    search_fn = search or _semantic_search_with_topic_filter(top_k)
    question_results = tuple(
        _evaluate_question(session, provider, question, search_fn) for question in questions
    )
    return RetrievalEvaluationReport(
        schema_version=RESULT_SCHEMA_VERSION,
        generated_at=datetime.now(UTC).isoformat(),
        topic=REFERENCE_TOPIC,
        reference_question_path="",
        top_k=top_k,
        provider_model=provider.model_name,
        metrics=_summarize(question_results),
        questions=question_results,
    )


def write_retrieval_report(
    report: RetrievalEvaluationReport,
    output_path: str | Path,
    *,
    reference_question_path: str | Path,
) -> Path:
    """Write a retrieval report JSON artifact and return its path."""

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    report_with_path = RetrievalEvaluationReport(
        schema_version=report.schema_version,
        generated_at=report.generated_at,
        topic=report.topic,
        reference_question_path=str(reference_question_path),
        top_k=report.top_k,
        provider_model=report.provider_model,
        metrics=report.metrics,
        questions=report.questions,
    )
    destination.write_text(
        json.dumps(_to_jsonable(report_with_path), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination


def _semantic_search_with_topic_filter(
    top_k: int,
) -> Callable[[Session, EmbeddingProvider, str], Sequence[SemanticSearchHit]]:
    def _search(
        session: Session,
        provider: EmbeddingProvider,
        query: str,
    ) -> Sequence[SemanticSearchHit]:
        return semantic_search(
            session,
            provider,
            query,
            k=top_k,
            filters=SemanticSearchFilters(corpus_topic=REFERENCE_TOPIC),
        )

    return _search


def _evaluate_question(
    session: Session,
    provider: EmbeddingProvider,
    question: ReferenceQuestion,
    search: Callable[[Session, EmbeddingProvider, str], Sequence[SemanticSearchHit]],
) -> QuestionRetrievalResult:
    expected = set(question.candidate_publication_ids)
    hits = tuple(
        _to_retrieved_chunk(rank, hit, expected)
        for rank, hit in enumerate(search(session, provider, question.question), start=1)
    )
    relevant_ranks = [hit.rank for hit in hits if hit.is_expected_publication]
    first_relevant_rank = min(relevant_ranks) if relevant_ranks else None
    hit = first_relevant_rank is not None
    unexpected_hit_count = 0
    if not question.should_be_answerable:
        unexpected_hit_count = len(hits)

    return QuestionRetrievalResult(
        question_id=question.question_id,
        style=question.style,
        question=question.question,
        should_be_answerable=question.should_be_answerable,
        expected_publication_ids=question.candidate_publication_ids,
        retrieved_chunks=hits,
        first_relevant_rank=first_relevant_rank,
        relevant_hit_count=len(relevant_ranks),
        hit=hit,
        reciprocal_rank=0.0 if first_relevant_rank is None else 1.0 / first_relevant_rank,
        unexpected_hit_count=unexpected_hit_count,
    )


def _to_retrieved_chunk(
    rank: int,
    hit: SemanticSearchHit,
    expected_publication_ids: set[str],
) -> RetrievedChunk:
    return RetrievedChunk(
        rank=rank,
        chunk_id=hit.chunk_id,
        score=hit.score,
        publication_id=hit.publication_id,
        title=hit.title,
        section=hit.section,
        source_url=hit.source_url,
        page_start=hit.page_start,
        page_end=hit.page_end,
        section_heading=hit.section_heading,
        model_name=hit.model_name,
        is_expected_publication=hit.publication_id in expected_publication_ids,
    )


def _summarize(results: Sequence[QuestionRetrievalResult]) -> RetrievalEvaluationSummary:
    answerable = [result for result in results if result.should_be_answerable]
    hit_results = [result for result in answerable if result.hit]
    reciprocal_rank_sum = sum(result.reciprocal_rank for result in answerable)
    first_ranks = [
        result.first_relevant_rank
        for result in answerable
        if result.first_relevant_rank is not None
    ]
    unanswerable_with_hits = [
        result
        for result in results
        if not result.should_be_answerable and result.unexpected_hit_count > 0
    ]

    answerable_count = len(answerable)
    return RetrievalEvaluationSummary(
        question_count=len(results),
        answerable_question_count=answerable_count,
        unanswerable_question_count=len(results) - answerable_count,
        hit_count=len(hit_results),
        hit_rate=0.0 if answerable_count == 0 else len(hit_results) / answerable_count,
        mean_reciprocal_rank=(
            0.0 if answerable_count == 0 else reciprocal_rank_sum / answerable_count
        ),
        mean_first_relevant_rank=(None if not first_ranks else sum(first_ranks) / len(first_ranks)),
        unanswerable_with_hits_count=len(unanswerable_with_hits),
    )


def _to_jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {key: _to_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, tuple | list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    return value

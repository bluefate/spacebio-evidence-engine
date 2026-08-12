"""Citation correctness evaluation for grounded answers (issue #59).

The evaluator is deterministic and fixture-driven. It verifies citation
identity/provenance discipline against retrieved evidence and, when a fixture
includes per-claim expected support, reports precision/recall over citation ids.
It does not judge scientific truth beyond the provided gold support labels.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from spacebio_evidence_engine.rag.citations import extract_citation_markers
from spacebio_evidence_engine.schemas import GroundedAnswerResponse

CITATION_CORRECTNESS_EVAL_VERSION = "1.0.0"


class RetrievedCitationEvidence(BaseModel):
    """Retrieved citation/provenance record available to the answer."""

    model_config = ConfigDict(extra="forbid")

    citation_id: str = Field(..., min_length=1)
    chunk_id: str = Field(..., min_length=1)
    publication_id: str = Field(..., min_length=1)
    title: str | None = None
    section: str | None = None
    page: int | None = Field(default=None, ge=1)
    source_url: str | None = None


class ClaimCitationCheck(BaseModel):
    """Gold support labels for one answer claim in an eval fixture."""

    model_config = ConfigDict(extra="forbid")

    claim_id: str = Field(..., min_length=1)
    claim_text: str = Field(..., min_length=1)
    expected_citation_ids: list[str] = Field(default_factory=list)
    actual_citation_ids: list[str] = Field(default_factory=list)


class CitationCorrectnessCase(BaseModel):
    """One grounded answer plus retrieved context for citation evaluation."""

    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(..., min_length=1)
    answer: GroundedAnswerResponse
    retrieved_context: list[RetrievedCitationEvidence] = Field(default_factory=list)
    claim_checks: list[ClaimCitationCheck] = Field(default_factory=list)


@dataclass(frozen=True, slots=True)
class CitationCorrectnessFinding:
    """One actionable citation correctness finding."""

    code: str
    message: str
    text: str


@dataclass(frozen=True, slots=True)
class ClaimCitationMetrics:
    """Precision/recall for citation ids on one fixture claim."""

    claim_id: str
    expected_citation_count: int
    actual_citation_count: int
    true_positive_count: int
    false_positive_count: int
    false_negative_count: int

    @property
    def precision(self) -> float:
        if self.actual_citation_count == 0:
            return 1.0 if self.expected_citation_count == 0 else 0.0
        return self.true_positive_count / self.actual_citation_count

    @property
    def recall(self) -> float:
        if self.expected_citation_count == 0:
            return 1.0
        return self.true_positive_count / self.expected_citation_count


@dataclass(frozen=True, slots=True)
class CitationCorrectnessCaseResult:
    """Evaluation result for one answer/case."""

    case_id: str
    question: str
    passed: bool
    findings: tuple[CitationCorrectnessFinding, ...]
    emitted_citation_count: int
    retrieved_citation_count: int
    valid_emitted_citation_count: int
    answer_marker_count: int
    valid_answer_marker_count: int
    claim_metrics: tuple[ClaimCitationMetrics, ...]

    @property
    def citation_id_precision(self) -> float:
        if self.emitted_citation_count == 0:
            return 1.0
        return self.valid_emitted_citation_count / self.emitted_citation_count

    @property
    def answer_marker_precision(self) -> float:
        if self.answer_marker_count == 0:
            return 1.0
        return self.valid_answer_marker_count / self.answer_marker_count

    @property
    def claim_citation_precision(self) -> float:
        return _mean(metric.precision for metric in self.claim_metrics)

    @property
    def claim_citation_recall(self) -> float:
        return _mean(metric.recall for metric in self.claim_metrics)


@dataclass(frozen=True, slots=True)
class CitationCorrectnessMetrics:
    """Aggregate citation correctness metrics for a fixture/report."""

    schema_version: str
    case_count: int
    passed_count: int
    failed_count: int
    finding_count: int
    citation_id_precision: float
    answer_marker_precision: float
    claim_citation_precision: float
    claim_citation_recall: float

    @property
    def passed(self) -> bool:
        return self.failed_count == 0


type CitationCorrectnessEvalResult = CitationCorrectnessMetrics | CitationCorrectnessCaseResult


def evaluate_case(case: CitationCorrectnessCase) -> CitationCorrectnessCaseResult:
    """Evaluate one answer's citations against retrieved evidence and claim labels."""
    retrieved_by_citation_id = {record.citation_id: record for record in case.retrieved_context}
    retrieved_chunk_ids = {record.chunk_id for record in case.retrieved_context}
    findings: list[CitationCorrectnessFinding] = []

    emitted_citations = case.answer.citations
    valid_emitted_count = 0
    for citation in emitted_citations:
        retrieved = retrieved_by_citation_id.get(citation.citation_id)
        if retrieved is None:
            findings.append(
                CitationCorrectnessFinding(
                    code="citation_id_not_retrieved",
                    message="Emitted citation id was not present in retrieved context.",
                    text=citation.citation_id,
                )
            )
            continue
        if citation.chunk_id != retrieved.chunk_id:
            findings.append(
                CitationCorrectnessFinding(
                    code="citation_chunk_mismatch",
                    message=(
                        "Emitted citation id points to a different chunk than retrieved context."
                    ),
                    text=(
                        f"{citation.citation_id}: emitted={citation.chunk_id} "
                        f"retrieved={retrieved.chunk_id}"
                    ),
                )
            )
            continue
        if citation.chunk_id not in retrieved_chunk_ids:
            findings.append(
                CitationCorrectnessFinding(
                    code="citation_chunk_not_retrieved",
                    message="Emitted citation chunk id was not present in retrieved context.",
                    text=citation.chunk_id,
                )
            )
            continue
        valid_emitted_count += 1

    emitted_ids = {citation.citation_id for citation in emitted_citations}
    answer_marker_ids = set(extract_citation_markers(case.answer.answer_text))
    valid_marker_count = 0
    for marker_id in sorted(answer_marker_ids):
        if marker_id in emitted_ids:
            valid_marker_count += 1
        else:
            findings.append(
                CitationCorrectnessFinding(
                    code="answer_marker_not_emitted",
                    message="Answer text references a citation id that was not emitted.",
                    text=marker_id,
                )
            )

    for citation_id in sorted(emitted_ids - answer_marker_ids):
        findings.append(
            CitationCorrectnessFinding(
                code="emitted_citation_not_used",
                message="Citation was emitted but not referenced by answer text.",
                text=citation_id,
            )
        )

    claim_metrics = tuple(_evaluate_claim_check(check, findings) for check in case.claim_checks)

    return CitationCorrectnessCaseResult(
        case_id=case.case_id,
        question=case.answer.question,
        passed=not findings,
        findings=tuple(findings),
        emitted_citation_count=len(emitted_citations),
        retrieved_citation_count=len(case.retrieved_context),
        valid_emitted_citation_count=valid_emitted_count,
        answer_marker_count=len(answer_marker_ids),
        valid_answer_marker_count=valid_marker_count,
        claim_metrics=claim_metrics,
    )


def evaluate_cases(
    cases: list[CitationCorrectnessCase],
) -> tuple[CitationCorrectnessEvalResult, ...]:
    """Evaluate cases and return aggregate metrics plus per-case results."""
    results = tuple(evaluate_case(case) for case in cases)
    metrics = CitationCorrectnessMetrics(
        schema_version=CITATION_CORRECTNESS_EVAL_VERSION,
        case_count=len(results),
        passed_count=sum(1 for result in results if result.passed),
        failed_count=sum(1 for result in results if not result.passed),
        finding_count=sum(len(result.findings) for result in results),
        citation_id_precision=_mean(result.citation_id_precision for result in results),
        answer_marker_precision=_mean(result.answer_marker_precision for result in results),
        claim_citation_precision=_mean(result.claim_citation_precision for result in results),
        claim_citation_recall=_mean(result.claim_citation_recall for result in results),
    )
    return (metrics, *results)


def load_cases(path: Path) -> list[CitationCorrectnessCase]:
    """Load a JSON fixture containing a list of citation correctness cases."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    data = payload["cases"] if isinstance(payload, dict) and "cases" in payload else payload
    adapter = TypeAdapter(list[CitationCorrectnessCase])
    return adapter.validate_python(data)


def result_to_dict(
    result: CitationCorrectnessMetrics | CitationCorrectnessCaseResult,
) -> dict:
    """Serialize citation correctness results for CLI JSON output."""
    if isinstance(result, CitationCorrectnessMetrics):
        return {
            "schema_version": result.schema_version,
            "case_count": result.case_count,
            "passed_count": result.passed_count,
            "failed_count": result.failed_count,
            "finding_count": result.finding_count,
            "citation_id_precision": result.citation_id_precision,
            "answer_marker_precision": result.answer_marker_precision,
            "claim_citation_precision": result.claim_citation_precision,
            "claim_citation_recall": result.claim_citation_recall,
            "passed": result.passed,
        }
    return {
        "case_id": result.case_id,
        "question": result.question,
        "passed": result.passed,
        "findings": [
            {"code": finding.code, "message": finding.message, "text": finding.text}
            for finding in result.findings
        ],
        "emitted_citation_count": result.emitted_citation_count,
        "retrieved_citation_count": result.retrieved_citation_count,
        "valid_emitted_citation_count": result.valid_emitted_citation_count,
        "citation_id_precision": result.citation_id_precision,
        "answer_marker_count": result.answer_marker_count,
        "valid_answer_marker_count": result.valid_answer_marker_count,
        "answer_marker_precision": result.answer_marker_precision,
        "claim_citation_precision": result.claim_citation_precision,
        "claim_citation_recall": result.claim_citation_recall,
        "claim_metrics": [
            {
                "claim_id": metric.claim_id,
                "expected_citation_count": metric.expected_citation_count,
                "actual_citation_count": metric.actual_citation_count,
                "true_positive_count": metric.true_positive_count,
                "false_positive_count": metric.false_positive_count,
                "false_negative_count": metric.false_negative_count,
                "precision": metric.precision,
                "recall": metric.recall,
            }
            for metric in result.claim_metrics
        ],
    }


def _evaluate_claim_check(
    check: ClaimCitationCheck,
    findings: list[CitationCorrectnessFinding],
) -> ClaimCitationMetrics:
    expected = _normalized_set(check.expected_citation_ids)
    actual = _normalized_set(check.actual_citation_ids)
    true_positive = expected & actual
    false_positive = actual - expected
    false_negative = expected - actual

    for citation_id in sorted(false_positive):
        findings.append(
            CitationCorrectnessFinding(
                code="claim_citation_false_positive",
                message="Claim is linked to a citation id not listed as expected support.",
                text=f"{check.claim_id}: {citation_id}",
            )
        )
    for citation_id in sorted(false_negative):
        findings.append(
            CitationCorrectnessFinding(
                code="claim_citation_false_negative",
                message="Claim is missing an expected supporting citation id.",
                text=f"{check.claim_id}: {citation_id}",
            )
        )

    return ClaimCitationMetrics(
        claim_id=check.claim_id,
        expected_citation_count=len(expected),
        actual_citation_count=len(actual),
        true_positive_count=len(true_positive),
        false_positive_count=len(false_positive),
        false_negative_count=len(false_negative),
    )


def _normalized_set(values: list[str]) -> set[str]:
    return {value.strip() for value in values if value.strip()}


def _mean(values: Iterable[float]) -> float:
    items = tuple(values)
    if not items:
        return 1.0
    return sum(items) / len(items)

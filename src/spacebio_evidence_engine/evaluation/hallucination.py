"""Offline hallucination checks for grounded answers (issue #58).

This evaluator is intentionally conservative and deterministic. It does not try
to judge scientific truth from free text. Instead, it flags answer sentences
that look like generated claims but do not carry any citation marker when the
response says evidence is sufficient or marginal.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from pydantic import TypeAdapter

from spacebio_evidence_engine.schemas import GroundedAnswerResponse

HALLUCINATION_EVAL_VERSION = "1.0.0"

_CITATION_MARKER_RE = re.compile(r"\[(C[0-9A-Za-z_-]+)\]")
_SENTENCE_RE = re.compile(r"[^.!?]+(?:[.!?]+|$)")
_CLAIM_WORD_RE = re.compile(
    r"\b("
    r"affect(?:s|ed|ing)?|alter(?:s|ed|ing)?|associate(?:s|d)?|atroph(?:y|ies|ied|ying)|"
    r"caus(?:e|es|ed|ing)|chang(?:e|es|ed|ing)|decreas(?:e|es|ed|ing)|"
    r"impair(?:s|ed|ing)?|increas(?:e|es|ed|ing)|induc(?:e|es|ed|ing)|"
    r"inhibit(?:s|ed|ing)?|los(?:e|es|t|ing)|reduc(?:e|es|ed|ing)|"
    r"report(?:s|ed|ing)?|show(?:s|ed|ing)?|suggest(?:s|ed|ing)?|"
    r"support(?:s|ed|ing)?|lead(?:s|ing)?|led|result(?:s|ed|ing)?|"
    r"improv(?:e|es|ed|ing)|worsen(?:s|ed|ing)?"
    r")\b",
    re.IGNORECASE,
)
_INSUFFICIENT_PHRASES = (
    "insufficient evidence",
    "not enough evidence",
    "cannot answer",
    "unable to answer",
)


@dataclass(frozen=True, slots=True)
class HallucinationFinding:
    """One actionable hallucination-eval finding."""

    code: str
    message: str
    text: str


@dataclass(frozen=True, slots=True)
class HallucinationCheckResult:
    """Evaluation result for one grounded answer."""

    question: str
    passed: bool
    findings: tuple[HallucinationFinding, ...]
    claim_sentence_count: int
    cited_claim_sentence_count: int
    citation_marker_count: int


@dataclass(frozen=True, slots=True)
class HallucinationMetrics:
    """Aggregate metrics for a fixture or offline report."""

    schema_version: str
    answer_count: int
    passed_count: int
    failed_count: int
    unsupported_claim_count: int
    claim_sentence_count: int
    cited_claim_sentence_count: int

    @property
    def passed(self) -> bool:
        return self.failed_count == 0

    @property
    def cited_claim_rate(self) -> float:
        if self.claim_sentence_count == 0:
            return 1.0
        return self.cited_claim_sentence_count / self.claim_sentence_count


type HallucinationEvalResult = HallucinationMetrics | HallucinationCheckResult


def evaluate_answer(answer: GroundedAnswerResponse) -> HallucinationCheckResult:
    """Evaluate one grounded answer for unsupported generated claims."""
    findings: list[HallucinationFinding] = []
    citation_ids = {citation.citation_id for citation in answer.citations}
    marker_ids = _citation_markers(answer.answer_text)

    if answer.sufficiency.status == "insufficient":
        _evaluate_insufficient_response(answer, marker_ids=marker_ids, findings=findings)
        return HallucinationCheckResult(
            question=answer.question,
            passed=not findings,
            findings=tuple(findings),
            claim_sentence_count=0,
            cited_claim_sentence_count=0,
            citation_marker_count=len(marker_ids),
        )

    claim_sentences = _claim_sentences(answer.answer_text)
    cited_claim_count = 0
    for sentence in claim_sentences:
        markers = _citation_markers(sentence)
        if markers:
            cited_claim_count += 1
            unknown = sorted(markers - citation_ids)
            if unknown:
                findings.append(
                    HallucinationFinding(
                        code="unknown_citation_marker",
                        message="Answer references citation markers not present in citations.",
                        text=", ".join(unknown),
                    )
                )
            continue
        findings.append(
            HallucinationFinding(
                code="unsupported_claim",
                message="Claim-like sentence has no citation marker.",
                text=sentence,
            )
        )

    if citation_ids and not marker_ids:
        findings.append(
            HallucinationFinding(
                code="citations_not_used",
                message="Response includes citations but answer_text uses no citation markers.",
                text=answer.answer_text,
            )
        )

    return HallucinationCheckResult(
        question=answer.question,
        passed=not findings,
        findings=tuple(findings),
        claim_sentence_count=len(claim_sentences),
        cited_claim_sentence_count=cited_claim_count,
        citation_marker_count=len(marker_ids),
    )


def evaluate_answers(answers: list[GroundedAnswerResponse]) -> tuple[HallucinationEvalResult, ...]:
    """Evaluate answers and return aggregate metrics plus per-answer results."""
    results = tuple(evaluate_answer(answer) for answer in answers)
    metrics = HallucinationMetrics(
        schema_version=HALLUCINATION_EVAL_VERSION,
        answer_count=len(results),
        passed_count=sum(1 for result in results if result.passed),
        failed_count=sum(1 for result in results if not result.passed),
        unsupported_claim_count=sum(
            1
            for result in results
            for finding in result.findings
            if finding.code == "unsupported_claim"
        ),
        claim_sentence_count=sum(result.claim_sentence_count for result in results),
        cited_claim_sentence_count=sum(result.cited_claim_sentence_count for result in results),
    )
    return (metrics, *results)


def load_answers(path: Path) -> list[GroundedAnswerResponse]:
    """Load a JSON fixture containing a list of grounded answer responses."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    data = payload["answers"] if isinstance(payload, dict) and "answers" in payload else payload
    adapter = TypeAdapter(list[GroundedAnswerResponse])
    return adapter.validate_python(data)


def result_to_dict(result: HallucinationMetrics | HallucinationCheckResult) -> dict:
    """Serialize evaluation results for CLI JSON output."""
    if isinstance(result, HallucinationMetrics):
        return {
            "schema_version": result.schema_version,
            "answer_count": result.answer_count,
            "passed_count": result.passed_count,
            "failed_count": result.failed_count,
            "unsupported_claim_count": result.unsupported_claim_count,
            "claim_sentence_count": result.claim_sentence_count,
            "cited_claim_sentence_count": result.cited_claim_sentence_count,
            "cited_claim_rate": result.cited_claim_rate,
            "passed": result.passed,
        }
    return {
        "question": result.question,
        "passed": result.passed,
        "findings": [
            {"code": finding.code, "message": finding.message, "text": finding.text}
            for finding in result.findings
        ],
        "claim_sentence_count": result.claim_sentence_count,
        "cited_claim_sentence_count": result.cited_claim_sentence_count,
        "citation_marker_count": result.citation_marker_count,
    }


def _evaluate_insufficient_response(
    answer: GroundedAnswerResponse,
    *,
    marker_ids: set[str],
    findings: list[HallucinationFinding],
) -> None:
    if answer.citations:
        findings.append(
            HallucinationFinding(
                code="insufficient_has_citations",
                message="Insufficient-evidence responses must not include citations.",
                text=", ".join(citation.citation_id for citation in answer.citations),
            )
        )
    if marker_ids:
        findings.append(
            HallucinationFinding(
                code="insufficient_has_markers",
                message="Insufficient-evidence responses must not cite generated claims.",
                text=", ".join(sorted(marker_ids)),
            )
        )
    lowered = answer.answer_text.lower()
    if not any(phrase in lowered for phrase in _INSUFFICIENT_PHRASES):
        findings.append(
            HallucinationFinding(
                code="insufficient_not_explicit",
                message="Insufficient-evidence response must clearly decline to answer.",
                text=answer.answer_text,
            )
        )


def _citation_markers(text: str) -> set[str]:
    return set(_CITATION_MARKER_RE.findall(text))


def _claim_sentences(text: str) -> tuple[str, ...]:
    sentences = []
    for match in _SENTENCE_RE.finditer(text):
        sentence = " ".join(match.group(0).split())
        if sentence and _CLAIM_WORD_RE.search(sentence):
            sentences.append(sentence)
    return tuple(sentences)

"""Evaluation helpers for grounded-answer quality checks."""

from spacebio_evidence_engine.evaluation.citation_correctness import (
    CitationCorrectnessCase,
    CitationCorrectnessCaseResult,
    CitationCorrectnessFinding,
    CitationCorrectnessMetrics,
    ClaimCitationCheck,
    ClaimCitationMetrics,
    RetrievedCitationEvidence,
    evaluate_case,
    evaluate_cases,
    load_cases,
)
from spacebio_evidence_engine.evaluation.hallucination import (
    HallucinationCheckResult,
    HallucinationFinding,
    HallucinationMetrics,
    evaluate_answer,
    evaluate_answers,
)
from spacebio_evidence_engine.evaluation.retrieval import (
    QuestionRetrievalResult,
    ReferenceQuestion,
    RetrievalEvaluationReport,
    RetrievalEvaluationSummary,
    RetrievedChunk,
    evaluate_retrieval,
    load_reference_questions,
    write_retrieval_report,
)

__all__ = [
    "CitationCorrectnessCase",
    "CitationCorrectnessCaseResult",
    "CitationCorrectnessFinding",
    "CitationCorrectnessMetrics",
    "ClaimCitationCheck",
    "ClaimCitationMetrics",
    "HallucinationCheckResult",
    "HallucinationFinding",
    "HallucinationMetrics",
    "QuestionRetrievalResult",
    "ReferenceQuestion",
    "RetrievedCitationEvidence",
    "RetrievalEvaluationReport",
    "RetrievalEvaluationSummary",
    "RetrievedChunk",
    "evaluate_case",
    "evaluate_cases",
    "evaluate_answer",
    "evaluate_answers",
    "evaluate_retrieval",
    "load_cases",
    "load_reference_questions",
    "write_retrieval_report",
]

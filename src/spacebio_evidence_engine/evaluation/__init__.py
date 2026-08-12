"""Evaluation helpers for grounded-answer quality checks."""

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
    "HallucinationCheckResult",
    "HallucinationFinding",
    "HallucinationMetrics",
    "QuestionRetrievalResult",
    "ReferenceQuestion",
    "RetrievalEvaluationReport",
    "RetrievalEvaluationSummary",
    "RetrievedChunk",
    "evaluate_answer",
    "evaluate_answers",
    "evaluate_retrieval",
    "load_reference_questions",
    "write_retrieval_report",
]

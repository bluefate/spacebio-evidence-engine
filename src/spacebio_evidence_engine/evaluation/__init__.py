"""Evaluation helpers for grounded-answer quality checks."""

from spacebio_evidence_engine.evaluation.hallucination import (
    HallucinationCheckResult,
    HallucinationFinding,
    HallucinationMetrics,
    evaluate_answer,
    evaluate_answers,
)

__all__ = [
    "HallucinationCheckResult",
    "HallucinationFinding",
    "HallucinationMetrics",
    "evaluate_answer",
    "evaluate_answers",
]

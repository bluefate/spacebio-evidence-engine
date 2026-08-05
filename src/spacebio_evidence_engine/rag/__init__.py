"""Retrieval-augmented generation behavior for grounded answers."""

from __future__ import annotations

from spacebio_evidence_engine.rag.sufficiency import (
    build_insufficient_evidence_response,
    build_insufficient_evidence_response_if_needed,
    evaluate_sufficiency,
)

__all__ = [
    "build_insufficient_evidence_response",
    "build_insufficient_evidence_response_if_needed",
    "evaluate_sufficiency",
]

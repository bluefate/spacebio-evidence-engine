"""Unit tests for insufficient-evidence response behavior (issue #55)."""

from __future__ import annotations

import pytest

from spacebio_evidence_engine.rag import (
    build_insufficient_evidence_response,
    build_insufficient_evidence_response_if_needed,
    evaluate_sufficiency,
)
from spacebio_evidence_engine.schemas import PassageCitation


def _make_citation(publication_id: str, chunk_id: str) -> PassageCitation:
    return PassageCitation(
        citation_id="C1",
        chunk_id=chunk_id,
        publication_id=publication_id,
    )


def test_evaluate_sufficiency_empty() -> None:
    sufficiency = evaluate_sufficiency([])
    assert sufficiency.status == "insufficient"
    assert sufficiency.retrieved_chunk_count == 0
    assert sufficiency.supporting_publication_count == 0
    assert "No on-topic" in (sufficiency.reason or "")


def test_evaluate_sufficiency_weak_one_chunk() -> None:
    sufficiency = evaluate_sufficiency([_make_citation("pub-001", "chunk-1")])
    assert sufficiency.status == "insufficient"
    assert sufficiency.retrieved_chunk_count == 1
    assert sufficiency.supporting_publication_count == 1
    assert "minimum is 3" in (sufficiency.reason or "")


def test_evaluate_sufficiency_weak_single_publication() -> None:
    citations = [
        _make_citation("pub-001", "chunk-1"),
        _make_citation("pub-001", "chunk-2"),
        _make_citation("pub-001", "chunk-3"),
    ]
    sufficiency = evaluate_sufficiency(citations)
    assert sufficiency.status == "insufficient"
    assert sufficiency.supporting_publication_count == 1
    assert "from 1 publication" in (sufficiency.reason or "")


def test_evaluate_sufficiency_sufficient() -> None:
    citations = [
        _make_citation("pub-001", "chunk-1"),
        _make_citation("pub-001", "chunk-2"),
        _make_citation("pub-002", "chunk-3"),
    ]
    sufficiency = evaluate_sufficiency(citations)
    assert sufficiency.status == "sufficient"
    assert sufficiency.retrieved_chunk_count == 3
    assert sufficiency.supporting_publication_count == 2


def test_build_insufficient_evidence_response_has_no_model_or_citations() -> None:
    sufficiency = evaluate_sufficiency([])
    response = build_insufficient_evidence_response(
        "What causes muscle atrophy in microgravity?", sufficiency
    )

    assert response.answer_text == (
        "Insufficient evidence in the controlled corpus to answer this question."
    )
    assert response.citations == []
    assert response.model_name is None
    assert response.sufficiency.status == "insufficient"


def test_build_insufficient_evidence_response_if_needed_returns_for_empty() -> None:
    response = build_insufficient_evidence_response_if_needed(
        "What causes muscle atrophy in microgravity?", []
    )
    assert response is not None
    assert response.sufficiency.status == "insufficient"
    assert response.model_name is None


def test_build_insufficient_evidence_response_if_needed_returns_none_when_sufficient() -> None:
    citations = [
        _make_citation("pub-001", "chunk-1"),
        _make_citation("pub-001", "chunk-2"),
        _make_citation("pub-002", "chunk-3"),
    ]
    response = build_insufficient_evidence_response_if_needed(
        "What causes muscle atrophy in microgravity?", citations
    )
    assert response is None


def test_custom_thresholds() -> None:
    citations = [_make_citation("pub-001", "chunk-1")]
    with pytest.raises(ValueError, match="min_chunks must be non-negative"):
        evaluate_sufficiency(citations, min_chunks=-1)

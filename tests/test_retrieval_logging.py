"""Tests for structured retrieval logging (issue #49)."""

from __future__ import annotations

import logging
from typing import Any, cast

import pytest

from spacebio_evidence_engine.retrieval.filters import RetrievalFilters
from spacebio_evidence_engine.retrieval.logging import (
    log_semantic_retrieval,
    make_retrieval_log_record,
)
from spacebio_evidence_engine.retrieval.semantic import SemanticSearchHit


def _hit(*, chunk_id: str = "chk_1", score: float = 0.91) -> SemanticSearchHit:
    return SemanticSearchHit(
        chunk_id=chunk_id,
        score=score,
        publication_id="pub_muscle_1",
        title="Microgravity and soleus atrophy",
        section="results",
        chunk_text="Soleus muscle mass decreased in flight animals.",
        source_url="https://doi.org/10.0/muscle",
        page_start=2,
        page_end=3,
        section_heading="Results",
        model_name="fixture-search-v1",
    )


def test_retrieval_log_payload_shape_excludes_raw_query_and_chunk_text() -> None:
    query = "Does microgravity reduce soleus mass? secret-token-123"

    record = make_retrieval_log_record(
        query=query,
        top_k=8,
        filters=RetrievalFilters(
            corpus_topic="microgravity_skeletal_muscle",
            organism_model="rodent",
            exposure="microgravity",
            section="results",
        ),
        hits=[_hit()],
        embedding_model="fixture-search-v1",
        embedding_dimension=384,
    )
    payload = record.to_dict()

    assert payload["event"] == "retrieval.semantic_search"
    assert payload["query_length"] == len(query)
    assert len(payload["query_sha256"]) == 64
    assert query not in repr(payload)
    assert "secret-token-123" not in repr(payload)
    assert "Soleus muscle mass decreased" not in repr(payload)
    assert payload["top_k"] == 8
    assert payload["filters"] == {
        "corpus_topic": "microgravity_skeletal_muscle",
        "organism_model": "rodent",
        "exposure": "microgravity",
        "section": "results",
    }
    assert payload["search_algorithm"] == "semantic_vector"
    assert payload["score_kind"] == "cosine_similarity"
    assert payload["embedding_model"] == "fixture-search-v1"
    assert payload["embedding_dimension"] == 384
    assert payload["result_count"] == 1
    assert payload["selected_chunks"] == [
        {
            "rank": 1,
            "chunk_id": "chk_1",
            "score": 0.91,
            "publication_id": "pub_muscle_1",
            "section": "results",
            "page_start": 2,
            "page_end": 3,
            "source_url": "https://doi.org/10.0/muscle",
            "embedding_model": "fixture-search-v1",
        }
    ]


def test_log_semantic_retrieval_emits_structured_extra(caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("test.retrieval")

    with caplog.at_level(logging.INFO, logger="test.retrieval"):
        record = log_semantic_retrieval(
            query="microgravity soleus",
            top_k=2,
            filters=None,
            hits=[_hit(chunk_id="chk_a", score=1.0), _hit(chunk_id="chk_b", score=0.5)],
            embedding_model="fixture-search-v1",
            embedding_dimension=384,
            enabled=True,
            logger=logger,
        )

    assert record is not None
    assert len(caplog.records) == 1
    payload = cast(dict[str, Any], caplog.records[0].__dict__["retrieval"])
    assert [chunk["chunk_id"] for chunk in payload["selected_chunks"]] == ["chk_a", "chk_b"]
    assert [chunk["rank"] for chunk in payload["selected_chunks"]] == [1, 2]
    assert [chunk["score"] for chunk in payload["selected_chunks"]] == [1.0, 0.5]


def test_log_semantic_retrieval_can_be_disabled(caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("test.retrieval.disabled")

    with caplog.at_level(logging.INFO, logger="test.retrieval.disabled"):
        record = log_semantic_retrieval(
            query="microgravity soleus",
            top_k=1,
            filters=None,
            hits=[_hit()],
            embedding_model="fixture-search-v1",
            embedding_dimension=384,
            enabled=False,
            logger=logger,
        )

    assert record is None
    assert caplog.records == []

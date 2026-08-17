from __future__ import annotations

import pytest

from spacebio_evidence_engine.retrieval.rerank import (
    LEXICAL_OVERLAP,
    LexicalOverlapReranker,
    NoOpReranker,
    reranker_from_env,
)
from spacebio_evidence_engine.retrieval.semantic import SemanticSearchHit


def _hit(chunk_id: str, text: str, score: float) -> SemanticSearchHit:
    return SemanticSearchHit(
        chunk_id=chunk_id,
        score=score,
        publication_id="pub_001",
        title="Example",
        section="Results",
        chunk_text=text,
        source_url="https://doi.org/10.0/example",
        page_start=1,
        page_end=1,
        section_heading=None,
        model_name="test-model",
    )


def test_lexical_reranker_changes_order_to_query_overlap() -> None:
    query = "microgravity skeletal muscle atrophy"
    weak = _hit("chk_high_vector", "unrelated liver iron homeostasis notes", score=0.99)
    strong = _hit(
        "chk_low_vector",
        "Microgravity induces skeletal muscle atrophy in antigravity muscles.",
        score=0.10,
    )

    ranked = LexicalOverlapReranker().rerank(query, [weak, strong])

    assert [hit.chunk_id for hit in ranked] == ["chk_low_vector", "chk_high_vector"]
    assert ranked[0].score > ranked[1].score


def test_noop_reranker_preserves_retrieval_order() -> None:
    first = _hit("chk_a", "zzzz", score=0.9)
    second = _hit("chk_b", "microgravity skeletal muscle atrophy", score=0.1)

    ranked = NoOpReranker().rerank("microgravity skeletal muscle atrophy", [first, second])

    assert [hit.chunk_id for hit in ranked] == ["chk_a", "chk_b"]
    assert ranked[0].score == 0.9


def test_lexical_reranker_respects_top_k() -> None:
    query = "soleus atrophy"
    hits = [
        _hit("chk_1", "unrelated", score=1.0),
        _hit("chk_2", "soleus atrophy after unloading", score=0.1),
        _hit("chk_3", "soleus", score=0.2),
    ]

    ranked = LexicalOverlapReranker().rerank(query, hits, top_k=1)

    assert len(ranked) == 1
    assert ranked[0].chunk_id == "chk_2"


def test_reranker_from_env_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SPACEBIO_RERANK_ENABLED", raising=False)
    monkeypatch.delenv("SPACEBIO_RERANKER", raising=False)
    assert reranker_from_env() is None


def test_reranker_from_env_can_be_disabled_explicitly(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPACEBIO_RERANK_ENABLED", "true")
    assert reranker_from_env(enabled=False) is None


def test_reranker_from_env_selects_lexical(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPACEBIO_RERANK_ENABLED", "true")
    monkeypatch.delenv("SPACEBIO_RERANKER", raising=False)
    reranker = reranker_from_env()
    assert reranker is not None
    assert reranker.name == LEXICAL_OVERLAP


def test_reranker_from_env_rejects_unknown_name() -> None:
    with pytest.raises(ValueError, match="unknown reranker"):
        reranker_from_env(enabled=True, name="cross-encoder")

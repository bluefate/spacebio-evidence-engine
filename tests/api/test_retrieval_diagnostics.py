"""API tests for gated developer retrieval diagnostics (issue #67)."""

from __future__ import annotations

from collections.abc import Sequence

from fastapi.testclient import TestClient

from spacebio_api.config import Settings
from spacebio_api.main import create_app
from spacebio_evidence_engine.retrieval import SemanticSearchHit


class FakeRetriever:
    def __init__(self, hits: Sequence[SemanticSearchHit]) -> None:
        self.hits = tuple(hits)

    def __call__(self, question: str, *, top_k: int = 8) -> Sequence[SemanticSearchHit]:
        return self.hits[:top_k]


def _hit(chunk_id: str, score: float) -> SemanticSearchHit:
    return SemanticSearchHit(
        chunk_id=chunk_id,
        score=score,
        publication_id="pub-001",
        title="Publication pub-001",
        section="results",
        chunk_text="secret passage text that must not appear in diagnostics",
        source_url="https://doi.org/10.0/pub-001",
        page_start=5,
        page_end=5,
        section_heading="Results",
        model_name="fixture-embedding",
    )


def test_retrieval_diagnostics_hidden_when_flag_disabled() -> None:
    client = TestClient(
        create_app(
            Settings(APP_ENV="test", SPACEBIO_DEV_RETRIEVAL_DIAGNOSTICS=False),
            retrieval_diagnostics_retriever=FakeRetriever([_hit("chunk-1", 0.91)]),
        )
    )

    response = client.post(
        "/dev/retrieval-diagnostics",
        json={"question": "How does microgravity affect skeletal muscle?"},
    )

    assert response.status_code == 404
    assert "disabled" in response.json()["detail"]


def test_retrieval_diagnostics_returns_chunk_ids_and_scores_without_secrets() -> None:
    question = "How does microgravity affect skeletal muscle?"
    client = TestClient(
        create_app(
            Settings(APP_ENV="test", SPACEBIO_DEV_RETRIEVAL_DIAGNOSTICS=True),
            retrieval_diagnostics_retriever=FakeRetriever(
                [_hit("chunk-1", 0.91), _hit("chunk-2", 0.77)]
            ),
        )
    )

    response = client.post(
        "/dev/retrieval-diagnostics",
        json={"question": question, "top_k": 8},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["selected_citation_ids"] == ["C1", "C2"]
    assert payload["selected_chunks"][0]["chunk_id"] == "chunk-1"
    assert payload["selected_chunks"][0]["score"] == 0.91
    assert payload["selected_chunks"][0]["citation_id"] == "C1"
    serialized = str(payload)
    assert question not in serialized
    assert "secret passage" not in serialized
    assert "sk-" not in serialized
    assert "OPENAI" not in serialized
    assert "query_sha256" in payload
    assert payload["query_length"] == len(question)


def test_retrieval_diagnostics_503_when_enabled_without_retriever() -> None:
    client = TestClient(create_app(Settings(APP_ENV="test", SPACEBIO_DEV_RETRIEVAL_DIAGNOSTICS=True)))

    response = client.post(
        "/dev/retrieval-diagnostics",
        json={"question": "How does microgravity affect skeletal muscle?"},
    )

    assert response.status_code == 503
    assert "no retriever" in response.json()["detail"]

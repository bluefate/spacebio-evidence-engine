"""API tests for the grounded /ask endpoint."""

from __future__ import annotations

from collections.abc import Sequence

from fastapi.testclient import TestClient

from spacebio_api.config import Settings
from spacebio_api.main import create_app
from spacebio_evidence_engine.llm import (
    ChatRequest,
    GenerateRequest,
    GenerationResult,
    LanguageModelProvider,
)
from spacebio_evidence_engine.rag import GroundedAnswerService
from spacebio_evidence_engine.retrieval import SemanticSearchHit


class FakeRetriever:
    def __init__(self, hits: Sequence[SemanticSearchHit]) -> None:
        self.hits = tuple(hits)

    def __call__(self, question: str, *, top_k: int = 8) -> Sequence[SemanticSearchHit]:
        return self.hits[:top_k]


class FakeLanguageModelProvider(LanguageModelProvider):
    def __init__(
        self,
        answer_text: str | None = None,
    ) -> None:
        self._answer_text = answer_text or (
            "Retrieved passages report reduced skeletal muscle fiber size [C1]. "
            "A related passage supports the same publication-level evidence [C2]. "
            "A separate publication reports unloading-related muscle changes [C3]."
        )

    @property
    def model_name(self) -> str:
        return "fake-api-llm"

    def generate(self, request: GenerateRequest) -> GenerationResult:
        raise AssertionError("API grounded service should use chat()")

    def chat(self, request: ChatRequest) -> GenerationResult:
        return GenerationResult(
            text=self._answer_text,
            model_name=self.model_name,
        )


def _hit(chunk_id: str, publication_id: str) -> SemanticSearchHit:
    return SemanticSearchHit(
        chunk_id=chunk_id,
        score=0.9,
        publication_id=publication_id,
        title=f"Publication {publication_id}",
        section="results",
        chunk_text="Skeletal muscle measurements changed after microgravity exposure.",
        source_url=f"https://doi.org/10.0/{publication_id}",
        page_start=5,
        page_end=5,
        section_heading="Results",
        model_name="fixture-embedding",
    )


def test_ask_returns_503_when_grounded_service_not_configured() -> None:
    app = create_app(Settings(APP_ENV="test"))
    app.state.grounded_answer_service = None
    client = TestClient(app)

    response = client.post(
        "/ask",
        json={"question": "What happens to skeletal muscle in microgravity?"},
    )

    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


def test_ask_returns_grounded_schema_payload() -> None:
    service = GroundedAnswerService(
        retriever=FakeRetriever(
            [
                _hit("chunk-1", "pub-001"),
                _hit("chunk-2", "pub-001"),
                _hit("chunk-3", "pub-002"),
            ]
        ),
        llm_provider=FakeLanguageModelProvider(),
    )
    app = create_app(Settings(APP_ENV="test"))
    app.state.grounded_answer_service = service
    client = TestClient(app)

    response = client.post(
        "/ask",
        json={"question": "What happens to skeletal muscle in microgravity?", "top_k": 3},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == "1.0.0"
    assert payload["sufficiency"]["status"] == "sufficient"
    assert payload["model_name"] == "fake-api-llm"
    assert [citation["citation_id"] for citation in payload["citations"]] == [
        "C1",
        "C2",
        "C3",
    ]
    assert payload["citations"][0]["chunk_id"] == "chunk-1"
    assert payload["citations"][0]["publication_id"] == "pub-001"
    assert payload["citations"][0]["title"] == "Publication pub-001"
    assert payload["citations"][0]["section"] == "results"
    assert payload["citations"][0]["page"] == 5
    assert payload["citations"][0]["source_url"] == "https://doi.org/10.0/pub-001"
    assert payload["citations"][0]["excerpt"]


def test_ask_returns_insufficient_for_empty_index() -> None:
    service = GroundedAnswerService(
        retriever=FakeRetriever([]),
        llm_provider=FakeLanguageModelProvider(),
    )
    app = create_app(Settings(APP_ENV="test"))
    app.state.grounded_answer_service = service
    client = TestClient(app)

    response = client.post(
        "/ask",
        json={"question": "What happens to skeletal muscle in microgravity?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["sufficiency"]["status"] == "insufficient"
    assert payload["model_name"] is None
    assert payload["citations"] == []


def test_ask_returns_502_for_uncited_invention() -> None:
    service = GroundedAnswerService(
        retriever=FakeRetriever(
            [
                _hit("chunk-1", "pub-001"),
                _hit("chunk-2", "pub-001"),
                _hit("chunk-3", "pub-002"),
            ]
        ),
        llm_provider=FakeLanguageModelProvider(
            "This answer contains no retrieved citations and is therefore unsafe."
        ),
    )
    app = create_app(Settings(APP_ENV="test"))
    app.state.grounded_answer_service = service
    client = TestClient(app)

    response = client.post(
        "/ask",
        json={"question": "What happens to skeletal muscle in microgravity?", "top_k": 3},
    )

    assert response.status_code == 502
    assert "did not cite" in response.json()["detail"].lower()


def test_ask_returns_json_500_when_retriever_raises() -> None:
    class BoomRetriever:
        def __call__(self, question: str, *, top_k: int = 8) -> Sequence[SemanticSearchHit]:
            raise TypeError("vector processor boom")

    service = GroundedAnswerService(
        retriever=BoomRetriever(),
        llm_provider=FakeLanguageModelProvider(),
    )
    app = create_app(Settings(APP_ENV="test"))
    app.state.grounded_answer_service = service
    client = TestClient(app)

    response = client.post("/ask", json={"question": "What happens to skeletal muscle?"})

    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/json")
    assert response.json()["detail"] == "vector processor boom"

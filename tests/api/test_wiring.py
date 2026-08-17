"""Tests for API service wiring (issue #164)."""

from __future__ import annotations

from collections.abc import Sequence

from spacebio_api.config import Settings
from spacebio_api.services import build_grounded_answer_service
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
    def __init__(self, answer_text: str) -> None:
        self.answer_text = answer_text
        self.chat_calls: list[ChatRequest] = []

    @property
    def model_name(self) -> str:
        return "fake-wired-llm"

    def generate(self, request: GenerateRequest) -> GenerationResult:
        raise AssertionError("GroundedAnswerService should use chat()")

    def chat(self, request: ChatRequest) -> GenerationResult:
        self.chat_calls.append(request)
        return GenerationResult(text=self.answer_text, model_name=self.model_name)


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


def test_build_service_disabled_without_openai_key() -> None:
    settings = Settings(APP_ENV="test", LLM_PROVIDER="openai")
    service = build_grounded_answer_service(settings)
    assert service is None


def test_build_service_wires_ollama_without_openai_key() -> None:
    settings = Settings(
        APP_ENV="test",
        LLM_PROVIDER="ollama",
        OLLAMA_MODEL="llama3.2:1b",
        OLLAMA_BASE_URL="http://127.0.0.1:11434/v1",
    )
    retriever = FakeRetriever([])
    service = build_grounded_answer_service(settings, retriever=retriever)
    assert isinstance(service, GroundedAnswerService)
    response = service.answer("What happens to skeletal muscle in microgravity?", top_k=3)
    assert response.sufficiency.status == "insufficient"


def test_build_service_disabled_without_openai_key_and_injected_dependencies() -> None:
    """When all dependencies are injected, the OpenAI key check is skipped."""
    settings = Settings(APP_ENV="test")
    retriever = FakeRetriever(
        [_hit("chunk-1", "pub-001"), _hit("chunk-2", "pub-001"), _hit("chunk-3", "pub-002")]
    )
    llm = FakeLanguageModelProvider(
        "Skeletal muscle showed reduced fiber size [C1]. "
        "A related passage supports the same evidence [C2]. "
        "A separate publication reports unloading-related changes [C3]."
    )
    service = build_grounded_answer_service(
        settings,
        retriever=retriever,
        llm_provider=llm,
    )
    assert isinstance(service, GroundedAnswerService)
    response = service.answer("What happens to skeletal muscle in microgravity?", top_k=3)
    assert response.sufficiency.status == "sufficient"
    assert response.model_name == "fake-wired-llm"


def test_build_service_wires_openai_provider_from_settings() -> None:
    """A configured OpenAI key builds a real provider without dependency injection."""
    settings = Settings(APP_ENV="test", OPENAI_API_KEY="test-key")
    # Empty retriever keeps the real OpenAI provider from being called.
    retriever = FakeRetriever([])
    service = build_grounded_answer_service(
        settings,
        retriever=retriever,
    )
    assert isinstance(service, GroundedAnswerService)
    response = service.answer("What happens to skeletal muscle in microgravity?", top_k=3)
    assert response.sufficiency.status == "insufficient"
    assert response.model_name is None

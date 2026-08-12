"""Tests for grounded answer orchestration."""

from __future__ import annotations

from collections.abc import Sequence

import pytest

from spacebio_evidence_engine.llm import (
    ChatRequest,
    GenerateRequest,
    GenerationResult,
    LanguageModelProvider,
)
from spacebio_evidence_engine.rag import GroundedAnswerError, GroundedAnswerService
from spacebio_evidence_engine.retrieval import SemanticSearchHit


class FakeRetriever:
    def __init__(self, hits: Sequence[SemanticSearchHit]) -> None:
        self.hits = tuple(hits)
        self.calls: list[tuple[str, int]] = []

    def __call__(self, question: str, *, top_k: int = 8) -> Sequence[SemanticSearchHit]:
        self.calls.append((question, top_k))
        return self.hits[:top_k]


class FakeLanguageModelProvider(LanguageModelProvider):
    def __init__(self, answer_text: str) -> None:
        self.answer_text = answer_text
        self.chat_calls: list[ChatRequest] = []

    @property
    def model_name(self) -> str:
        return "fake-grounded-llm"

    def generate(self, request: GenerateRequest) -> GenerationResult:
        raise AssertionError("GroundedAnswerService should use chat()")

    def chat(self, request: ChatRequest) -> GenerationResult:
        self.chat_calls.append(request)
        return GenerationResult(text=self.answer_text, model_name=self.model_name)


def _hit(
    chunk_id: str,
    publication_id: str,
    *,
    text: str = "Soleus fiber cross-sectional area decreased after unloading.",
    title: str = "Microgravity skeletal muscle study",
    section: str = "results",
    page_start: int | None = 4,
) -> SemanticSearchHit:
    return SemanticSearchHit(
        chunk_id=chunk_id,
        score=0.9,
        publication_id=publication_id,
        title=title,
        section=section,
        chunk_text=text,
        source_url=f"https://doi.org/10.0/{publication_id}",
        page_start=page_start,
        page_end=page_start,
        section_heading=section.title(),
        model_name="fixture-embedding",
    )


def test_service_returns_insufficient_without_calling_llm_for_weak_evidence() -> None:
    llm = FakeLanguageModelProvider("This should not be used [C1].")
    service = GroundedAnswerService(
        retriever=FakeRetriever([_hit("chunk-1", "pub-001")]),
        llm_provider=llm,
    )

    response = service.answer("What happens to skeletal muscle in microgravity?")

    assert response.sufficiency.status == "insufficient"
    assert response.citations == []
    assert response.model_name is None
    assert llm.chat_calls == []


def test_service_returns_citation_validated_grounded_answer() -> None:
    llm = FakeLanguageModelProvider(
        "Skeletal muscle showed reduced fiber size in the retrieved evidence [C1]. "
        "A related passage from the same publication supports that pattern [C2]. "
        "A second cited study also reported unloading-related changes [C3]."
    )
    service = GroundedAnswerService(
        retriever=FakeRetriever(
            [
                _hit("chunk-1", "pub-001"),
                _hit("chunk-2", "pub-001"),
                _hit(
                    "chunk-3",
                    "pub-002",
                    text="Unloading changed muscle contractile phenotype.",
                    title="Spaceflight muscle phenotype study",
                    page_start=7,
                ),
            ]
        ),
        llm_provider=llm,
    )

    response = service.answer("What happens to skeletal muscle in microgravity?", top_k=3)

    assert response.sufficiency.status == "sufficient"
    assert response.model_name == "fake-grounded-llm"
    assert [citation.citation_id for citation in response.citations] == ["C1", "C2", "C3"]
    assert response.citations[0].chunk_id == "chunk-1"
    assert response.citations[0].publication_id == "pub-001"
    assert response.citations[0].title == "Microgravity skeletal muscle study"
    assert response.citations[0].section == "results"
    assert response.citations[0].page == 4
    assert response.citations[0].source_url == "https://doi.org/10.0/pub-001"
    assert response.citations[0].excerpt
    assert llm.chat_calls


def test_service_rejects_answer_with_unknown_citation_marker() -> None:
    service = GroundedAnswerService(
        retriever=FakeRetriever(
            [
                _hit("chunk-1", "pub-001"),
                _hit("chunk-2", "pub-001"),
                _hit("chunk-3", "pub-002"),
            ]
        ),
        llm_provider=FakeLanguageModelProvider("Unsupported generated claim [C404]."),
    )

    with pytest.raises(GroundedAnswerError, match="outside retrieved context"):
        service.answer("What happens to skeletal muscle in microgravity?")

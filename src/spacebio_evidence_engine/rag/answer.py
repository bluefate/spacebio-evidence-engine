"""Grounded answer orchestration for the `/ask` API endpoint."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from spacebio_evidence_engine.llm import LanguageModelProvider
from spacebio_evidence_engine.rag.citations import emit_citations_for_answer_text
from spacebio_evidence_engine.rag.context import (
    DEFAULT_EVIDENCE_TOKEN_BUDGET,
    assemble_context,
)
from spacebio_evidence_engine.rag.prompt import render_grounded_answer_prompt
from spacebio_evidence_engine.rag.sufficiency import (
    build_insufficient_evidence_response,
    evaluate_sufficiency,
)
from spacebio_evidence_engine.retrieval import DEFAULT_TOP_K, SemanticSearchHit
from spacebio_evidence_engine.schemas import GroundedAnswerResponse

DEFAULT_ANSWER_MAX_TOKENS = 700


class RetrievedEvidenceProvider(Protocol):
    """Callable that retrieves citation-preserving evidence for a question."""

    def __call__(self, question: str, *, top_k: int = DEFAULT_TOP_K) -> Sequence[SemanticSearchHit]:
        """Return ranked semantic search hits with full provenance."""
        ...


class GroundedAnswerError(RuntimeError):
    """Raised when answer generation cannot satisfy grounding requirements."""


class GroundedAnswerService:
    """Retrieve evidence, enforce sufficiency, generate, and validate citations."""

    def __init__(
        self,
        *,
        retriever: RetrievedEvidenceProvider,
        llm_provider: LanguageModelProvider,
        evidence_token_budget: int = DEFAULT_EVIDENCE_TOKEN_BUDGET,
        answer_max_tokens: int = DEFAULT_ANSWER_MAX_TOKENS,
    ) -> None:
        if evidence_token_budget < 1:
            raise ValueError("evidence_token_budget must be at least 1")
        if answer_max_tokens < 1:
            raise ValueError("answer_max_tokens must be at least 1")
        self._retriever = retriever
        self._llm_provider = llm_provider
        self._evidence_token_budget = evidence_token_budget
        self._answer_max_tokens = answer_max_tokens

    def answer(self, question: str, *, top_k: int = DEFAULT_TOP_K) -> GroundedAnswerResponse:
        """Return a schema-compliant grounded answer for a question.

        The LLM is never called when retrieved evidence is insufficient. When
        generation is attempted, the returned answer text must cite only
        citation IDs emitted from the assembled retrieved context.
        """

        normalized_question = question.strip()
        if not normalized_question:
            raise ValueError("question must be a non-empty string")
        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        hits = tuple(self._retriever(normalized_question, top_k=top_k))
        context = assemble_context(hits, token_budget=self._evidence_token_budget)
        sufficiency = evaluate_sufficiency(list(context.citations))
        if sufficiency.status == "insufficient":
            return build_insufficient_evidence_response(normalized_question, sufficiency)

        prompt = render_grounded_answer_prompt(normalized_question, context)
        generation = self._llm_provider.chat(
            prompt.to_chat_request(temperature=0.0, max_tokens=self._answer_max_tokens)
        )
        answer_text = generation.text.strip()
        if not answer_text:
            raise GroundedAnswerError("LLM returned an empty answer.")

        citation_result = emit_citations_for_answer_text(answer_text, context)
        if not citation_result.valid:
            rejected = ", ".join(citation_result.rejected_citation_ids)
            raise GroundedAnswerError(
                "Generated answer referenced citation IDs outside retrieved context: "
                f"{rejected or 'unknown'}"
            )
        if not citation_result.citations:
            raise GroundedAnswerError("Generated answer did not cite any retrieved passages.")

        cited_sufficiency = evaluate_sufficiency(list(citation_result.citations))
        if cited_sufficiency.status == "insufficient":
            return build_insufficient_evidence_response(normalized_question, cited_sufficiency)

        return GroundedAnswerResponse(
            question=normalized_question,
            answer_text=answer_text,
            citations=list(citation_result.citations),
            sufficiency=cited_sufficiency,
            warnings=list(citation_result.warnings),
            model_name=generation.model_name,
        )

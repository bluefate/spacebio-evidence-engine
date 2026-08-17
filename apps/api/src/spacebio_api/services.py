"""Runtime service wiring for the FastAPI application (issue #164)."""

from __future__ import annotations

import logging
from collections.abc import Callable, Sequence

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from spacebio_api.config import Settings
from spacebio_evidence_engine.embeddings import EmbeddingProvider, LocalEmbeddingProvider
from spacebio_evidence_engine.llm import LanguageModelProvider
from spacebio_evidence_engine.llm.openai import OpenAILanguageModelProvider
from spacebio_evidence_engine.rag import GroundedAnswerService
from spacebio_evidence_engine.rag.answer import RetrievedEvidenceProvider
from spacebio_evidence_engine.retrieval import DEFAULT_TOP_K, SemanticSearchHit, semantic_search

_logger = logging.getLogger("spacebio_api.services")


def build_session_factory(database_url: str) -> Callable[[], Session]:
    """Return a callable that creates a new SQLAlchemy Session for the API."""
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)

    def _factory() -> Session:
        return SessionLocal()

    return _factory


def build_grounded_answer_service(
    settings: Settings,
    *,
    retriever: RetrievedEvidenceProvider | None = None,
    llm_provider: LanguageModelProvider | None = None,
    embedding_provider: EmbeddingProvider | None = None,
    session_factory: Callable[[], Session] | None = None,
) -> GroundedAnswerService | None:
    """Build a grounded answer service from settings, or return None when disabled.

    The service is constructed when an OpenAI API key is configured, or when
    ``LLM_PROVIDER=ollama`` for a local OpenAI-compatible server. If any required
    dependency is missing, the application fails closed and ``/ask`` remains
    unavailable.
    """
    if llm_provider is None:
        provider_name = settings.llm_provider.strip().lower()
        if provider_name == "ollama":
            llm_provider = OpenAILanguageModelProvider(
                api_key=settings.openai_api_key or "ollama",
                model_name=settings.ollama_model,
                api_base=settings.ollama_base_url,
                timeout_seconds=120.0,
            )
        elif settings.openai_api_key:
            llm_provider = OpenAILanguageModelProvider(
                api_key=settings.openai_api_key,
                model_name=settings.openai_model,
            )
        else:
            _logger.info("OPENAI_API_KEY not configured; /ask disabled (503).")
            return None

    if retriever is None:
        if embedding_provider is None:
            try:
                embedding_provider = LocalEmbeddingProvider(model_name=settings.embedding_model)
            except (ImportError, ValueError) as exc:
                _logger.warning("Cannot load embedding provider; /ask disabled: %s", exc)
                return None
        if session_factory is None:
            try:
                session_factory = build_session_factory(settings.database_url)
            except Exception as exc:  # noqa: BLE001 - startup wiring may fail safely
                _logger.warning("Cannot build database session factory; /ask disabled: %s", exc)
                return None

        def _retriever(question: str, *, top_k: int = DEFAULT_TOP_K) -> Sequence[SemanticSearchHit]:
            with session_factory() as session:
                return semantic_search(session, embedding_provider, question, k=top_k)

        retriever = _retriever

    return GroundedAnswerService(
        retriever=retriever,
        llm_provider=llm_provider,
    )

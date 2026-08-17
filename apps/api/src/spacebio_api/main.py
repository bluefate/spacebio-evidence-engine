"""FastAPI application entrypoint."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from fastapi import FastAPI, HTTPException, status

from spacebio_api import __version__
from spacebio_api.config import Settings, get_settings
from spacebio_evidence_engine.rag import GroundedAnswerError, GroundedAnswerService
from spacebio_evidence_engine.retrieval import DEFAULT_TOP_K, SemanticSearchHit
from spacebio_evidence_engine.retrieval.diagnostics import build_retrieval_diagnostics_payload
from spacebio_evidence_engine.schemas import AskRequest, GroundedAnswerResponse


class RetrievalDiagnosticsFn(Protocol):
    """Retrieve ranked chunks for the developer diagnostics view."""

    def __call__(
        self, question: str, *, top_k: int = DEFAULT_TOP_K
    ) -> Sequence[SemanticSearchHit]: ...


def create_app(
    settings: Settings | None = None,
    *,
    grounded_answer_service: GroundedAnswerService | None = None,
    retrieval_diagnostics_retriever: RetrievalDiagnosticsFn | None = None,
) -> FastAPI:
    """Build the FastAPI application."""
    _settings = settings or get_settings()
    app = FastAPI(
        title="Space Biology Evidence Engine API",
        version=__version__,
        docs_url="/docs" if _settings.app_env != "production" else None,
    )
    app.state.settings = _settings
    app.state.grounded_answer_service = grounded_answer_service
    app.state.retrieval_diagnostics_retriever = retrieval_diagnostics_retriever

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(
        "/ask",
        response_model=GroundedAnswerResponse,
        status_code=status.HTTP_200_OK,
        summary="Ask a grounded question",
        tags=["ask"],
        responses={
            status.HTTP_503_SERVICE_UNAVAILABLE: {
                "description": "Grounded answer service is not configured.",
            },
            status.HTTP_502_BAD_GATEWAY: {
                "description": "Generated answer failed grounding validation.",
            },
        },
    )
    def ask(body: AskRequest) -> GroundedAnswerResponse:
        """Retrieve evidence and return a citation-validated grounded answer."""
        service = app.state.grounded_answer_service
        if service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Grounded answer service is not configured. Configure a retriever "
                    "and LanguageModelProvider before enabling /ask."
                ),
            )
        try:
            return service.answer(body.question, top_k=body.top_k)
        except GroundedAnswerError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc

    @app.post(
        "/dev/retrieval-diagnostics",
        status_code=status.HTTP_200_OK,
        summary="Developer retrieval diagnostics",
        tags=["dev"],
        responses={
            status.HTTP_404_NOT_FOUND: {
                "description": "Diagnostics are disabled (default).",
            },
            status.HTTP_503_SERVICE_UNAVAILABLE: {
                "description": "Diagnostics are enabled but no retriever is configured.",
            },
        },
    )
    def retrieval_diagnostics_endpoint(body: AskRequest) -> dict[str, object]:
        """Return hashed query metadata, chunk IDs, ranks, scores, and citation ids."""
        if not _settings.dev_retrieval_diagnostics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Retrieval diagnostics are disabled.",
            )
        retriever = app.state.retrieval_diagnostics_retriever
        if retriever is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Retrieval diagnostics are enabled but no retriever is configured. "
                    "Wire a semantic retriever before using this endpoint."
                ),
            )
        hits = list(retriever(body.question, top_k=body.top_k))
        return build_retrieval_diagnostics_payload(
            query=body.question,
            top_k=body.top_k,
            hits=hits,
        )

    return app


app = create_app()

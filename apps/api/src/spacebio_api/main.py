"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, status

from spacebio_api import __version__
from spacebio_api.config import Settings, get_settings
from spacebio_evidence_engine.schemas import AskRequest, GroundedAnswerResponse


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI application."""
    _settings = settings or get_settings()
    app = FastAPI(
        title="Space Biology Evidence Engine API",
        version=__version__,
        docs_url="/docs" if _settings.app_env != "production" else None,
    )
    app.state.settings = _settings

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(
        "/ask",
        response_model=GroundedAnswerResponse,
        status_code=status.HTTP_200_OK,
        summary="Ask a grounded question (schema registered; behavior TBD)",
        tags=["ask"],
        responses={
            status.HTTP_501_NOT_IMPLEMENTED: {
                "description": "Grounded ask pipeline not implemented yet.",
            }
        },
    )
    def ask(_body: AskRequest) -> GroundedAnswerResponse:
        """OpenAPI registers AskRequest / GroundedAnswerResponse (issue #57).

        Full retrieval + generation lands in later grounded-answer issues.
        """
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Grounded /ask is not implemented yet; response schema is registered.",
        )

    return app


app = create_app()

"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from spacebio_api import __version__
from spacebio_api.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI application (no RAG routes in this skeleton)."""
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

    return app


app = create_app()

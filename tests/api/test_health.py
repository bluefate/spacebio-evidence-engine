"""API health endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from spacebio_api.config import Settings
from spacebio_api.main import create_app


def test_health_returns_ok() -> None:
    client = TestClient(create_app(Settings(APP_ENV="test")))
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

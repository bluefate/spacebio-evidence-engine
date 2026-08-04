"""Settings loading tests."""

from __future__ import annotations

import pytest

from spacebio_api.config import Settings, get_settings


def test_settings_defaults() -> None:
    settings = Settings(APP_ENV="test")
    assert settings.app_env == "test"
    assert settings.api_port == 8000
    assert settings.openai_model == "gpt-4o-mini"
    assert "all-MiniLM-L6-v2" in settings.embedding_model


def test_settings_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("API_PORT", "9000")
    get_settings.cache_clear()
    settings = Settings()
    assert settings.app_env == "staging"
    assert settings.log_level == "DEBUG"
    assert settings.api_port == 9000
    get_settings.cache_clear()

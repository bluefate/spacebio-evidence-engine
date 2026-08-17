"""Unit tests for the optional OpenAI chat provider (issue #164)."""

from __future__ import annotations

from typing import Any

import pytest

from spacebio_evidence_engine.llm import (
    ChatMessage,
    ChatRequest,
    GenerateRequest,
    GenerationResult,
    OpenAILanguageModelError,
    OpenAILanguageModelProvider,
)
from spacebio_evidence_engine.llm.base import LanguageModelProvider as BaseLanguageModelProvider


class StubOpenAIChatClient:
    """Deterministic stand-in for the OpenAI chat completions API."""

    def __init__(self, *, text: str = "Stub answer [C1].", finish_reason: str = "stop") -> None:
        self.text = text
        self.finish_reason = finish_reason
        self.calls: list[tuple[str, str, list[dict[str, str]]]] = []
        self.seen_api_keys: list[str] = []

    def create_chat_completion(
        self,
        *,
        api_key: str,
        model: str,
        messages: list[dict[str, str]],
        temperature: float | None,
        max_tokens: int | None,
        timeout_seconds: float,
    ) -> dict[str, Any]:
        assert timeout_seconds > 0
        self.calls.append((model, api_key, list(messages)))
        self.seen_api_keys.append(api_key)
        return {
            "choices": [
                {
                    "message": {"role": "assistant", "content": self.text},
                    "finish_reason": self.finish_reason,
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 3,
                "total_tokens": 13,
            },
        }


def test_from_env_returns_none_without_api_key() -> None:
    provider = OpenAILanguageModelProvider.from_env(environ={}, client=StubOpenAIChatClient())
    assert provider is None


def test_from_env_uses_api_key_and_default_model() -> None:
    client = StubOpenAIChatClient()
    provider = OpenAILanguageModelProvider.from_env(
        environ={"OPENAI_API_KEY": "test-key"},
        client=client,
    )
    assert provider is not None
    assert provider.model_name == "gpt-4o-mini"

    result = provider.chat(
        ChatRequest(messages=[ChatMessage(role="user", content="What happens to muscle?")])
    )
    assert isinstance(result, GenerationResult)
    assert result.text == "Stub answer [C1]."
    assert result.model_name == "gpt-4o-mini"
    assert result.usage is not None
    assert result.usage.total_tokens == 13
    assert client.seen_api_keys == ["test-key"]


def test_model_name_is_configurable_from_env() -> None:
    provider = OpenAILanguageModelProvider.from_env(
        environ={
            "OPENAI_API_KEY": "test-key",
            "OPENAI_MODEL": "custom-model",
        },
        client=StubOpenAIChatClient(),
    )
    assert provider is not None
    assert provider.model_name == "custom-model"


def test_openai_provider_is_language_model_provider() -> None:
    provider = OpenAILanguageModelProvider(
        api_key="test-key",
        client=StubOpenAIChatClient(),
    )
    assert isinstance(provider, BaseLanguageModelProvider)


def test_generate_uses_chat_underneath() -> None:
    client = StubOpenAIChatClient()
    provider = OpenAILanguageModelProvider(api_key="test-key", client=client)
    result = provider.generate(GenerateRequest(prompt="Summarize evidence."))
    assert result.text == "Stub answer [C1]."
    assert client.calls
    _model, _key, messages = client.calls[0]
    assert messages == [{"role": "user", "content": "Summarize evidence."}]


def test_generate_includes_system_message() -> None:
    client = StubOpenAIChatClient()
    provider = OpenAILanguageModelProvider(api_key="test-key", client=client)
    provider.generate(
        GenerateRequest(
            prompt="Summarize evidence.",
            system="Ground all answers in citations.",
        )
    )
    _model, _key, messages = client.calls[0]
    assert messages == [
        {"role": "system", "content": "Ground all answers in citations."},
        {"role": "user", "content": "Summarize evidence."},
    ]


def test_blank_api_key_rejected() -> None:
    with pytest.raises(ValueError, match="api_key"):
        OpenAILanguageModelProvider(api_key=" ", client=StubOpenAIChatClient())


def test_malformed_response_rejected() -> None:
    class BadClient(StubOpenAIChatClient):
        def create_chat_completion(
            self,
            *,
            api_key: str,
            model: str,
            messages: list[dict[str, str]],
            temperature: float | None,
            max_tokens: int | None,
            timeout_seconds: float,
        ) -> dict[str, Any]:
            del api_key, model, messages, temperature, max_tokens, timeout_seconds
            return {"invalid": "payload"}

    provider = OpenAILanguageModelProvider(api_key="test-key", client=BadClient())
    with pytest.raises(OpenAILanguageModelError, match="malformed"):
        provider.chat(ChatRequest(messages=[ChatMessage(role="user", content="q")]))


def test_package_exports_openai_provider() -> None:
    from spacebio_evidence_engine import llm

    assert llm.OpenAILanguageModelProvider is OpenAILanguageModelProvider


def test_chat_completions_url_appends_path_for_ollama_base() -> None:
    from spacebio_evidence_engine.llm.openai import chat_completions_url

    assert chat_completions_url(None) == "https://api.openai.com/v1/chat/completions"
    assert (
        chat_completions_url("http://127.0.0.1:11434/v1")
        == "http://127.0.0.1:11434/v1/chat/completions"
    )

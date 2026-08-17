"""Optional OpenAI chat provider for grounded answer generation (issue #164).

The provider is inactive unless an API key is supplied. Use ``from_env()`` to
construct it from environment variables; it returns ``None`` when
``OPENAI_API_KEY`` is unset so CI and local-only runs stay credential-free.
The implementation uses stdlib ``urllib`` so the OpenAI SDK is not required.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from spacebio_evidence_engine.llm.base import (
    ChatMessage,
    ChatRequest,
    GenerateRequest,
    GenerationResult,
    LanguageModelProvider,
    UsageMetadata,
)

DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
OPENAI_MODEL_ENV = "OPENAI_MODEL"
OPENAI_API_BASE_ENV = "OPENAI_API_BASE"


def chat_completions_url(api_base: str | None) -> str:
    """Return a chat-completions URL, including Ollama's OpenAI-compatible path."""
    if api_base is None or not api_base.strip():
        return DEFAULT_OPENAI_CHAT_URL
    base = api_base.strip().rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    return f"{base}/chat/completions"


class OpenAILanguageModelError(RuntimeError):
    """Raised when the OpenAI chat API cannot return a valid completion."""


class _OpenAIChatClient(Protocol):
    """Minimal client surface used by ``OpenAILanguageModelProvider``."""

    def create_chat_completion(
        self,
        *,
        api_key: str,
        model: str,
        messages: list[dict[str, str]],
        temperature: float | None,
        max_tokens: int | None,
        timeout_seconds: float,
    ) -> dict[str, Any]: ...


class _HTTPChatClient:
    """Small stdlib HTTP client to avoid requiring the OpenAI SDK in CI."""

    def __init__(self, endpoint: str = DEFAULT_OPENAI_CHAT_URL) -> None:
        self.endpoint = endpoint

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
        payload: dict[str, Any] = {"model": model, "messages": messages}
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                raw_body = response.read()
        except urllib.error.HTTPError as exc:  # pragma: no cover - live API path
            raise OpenAILanguageModelError(f"OpenAI chat request failed: HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:  # pragma: no cover - live API path
            raise OpenAILanguageModelError("OpenAI chat request failed") from exc

        try:
            return json.loads(raw_body.decode("utf-8"))
        except (ValueError, json.JSONDecodeError) as exc:
            raise OpenAILanguageModelError("OpenAI chat response was malformed") from exc


class OpenAILanguageModelProvider(LanguageModelProvider):
    """OpenAI chat-backed provider for grounded answer generation.

    Tests should pass an injected ``client`` and fake API key. Production callers
    should prefer ``from_env()`` so the provider remains disabled when no key is
    configured.
    """

    def __init__(
        self,
        *,
        api_key: str,
        model_name: str = DEFAULT_OPENAI_MODEL,
        client: _OpenAIChatClient | None = None,
        timeout_seconds: float = 60.0,
        api_base: str | None = None,
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key must be provided for OpenAI chat")
        if not model_name.strip():
            raise ValueError("model_name must be a non-empty string")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._api_key = api_key
        self._model_name = model_name
        self._api_base = api_base
        self._client = client or _HTTPChatClient(endpoint=chat_completions_url(api_base))
        self._timeout_seconds = timeout_seconds

    @property
    def model_name(self) -> str:
        return self._model_name

    @classmethod
    def from_env(
        cls,
        *,
        environ: Mapping[str, str] | None = None,
        client: _OpenAIChatClient | None = None,
    ) -> OpenAILanguageModelProvider | None:
        """Return a configured provider, or ``None`` when no API key is present."""
        env = os.environ if environ is None else environ
        api_key = env.get(OPENAI_API_KEY_ENV, "").strip()
        if not api_key:
            return None
        model_name = env.get(OPENAI_MODEL_ENV, DEFAULT_OPENAI_MODEL)
        api_base = env.get(OPENAI_API_BASE_ENV, "").strip() or None
        return cls(api_key=api_key, model_name=model_name, client=client, api_base=api_base)

    def _to_api_messages(self, messages: Sequence[ChatMessage]) -> list[dict[str, str]]:
        return [{"role": message.role, "content": message.content} for message in messages]

    def _parse_completion(self, response: dict[str, Any]) -> GenerationResult:
        try:
            choice = response["choices"][0]
            message = choice["message"]
            text = message.get("content") or ""
            finish_reason = choice.get("finish_reason")
        except (KeyError, IndexError, TypeError) as exc:
            raise OpenAILanguageModelError("OpenAI chat response was malformed") from exc

        usage = None
        usage_raw = response.get("usage")
        if isinstance(usage_raw, dict):
            usage = UsageMetadata(
                prompt_tokens=usage_raw.get("prompt_tokens"),
                completion_tokens=usage_raw.get("completion_tokens"),
                total_tokens=usage_raw.get("total_tokens"),
            )

        return GenerationResult(
            text=text,
            model_name=self._model_name,
            usage=usage,
            finish_reason=finish_reason,
        )

    def chat(self, request: ChatRequest) -> GenerationResult:
        messages = self._to_api_messages(request.messages)
        if not messages:
            raise OpenAILanguageModelError("Chat request must contain at least one message")

        response = self._client.create_chat_completion(
            api_key=self._api_key,
            model=self._model_name,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            timeout_seconds=self._timeout_seconds,
        )
        return self._parse_completion(response)

    def generate(self, request: GenerateRequest) -> GenerationResult:
        messages: list[ChatMessage] = []
        if request.system:
            messages.append(ChatMessage(role="system", content=request.system))
        messages.append(ChatMessage(role="user", content=request.prompt))
        return self.chat(
            ChatRequest(
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                structured_output=request.structured_output,
            )
        )

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
OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
OPENAI_MODEL_ENV = "OPENAI_MODEL"


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

    endpoint = "https://api.openai.com/v1/chat/completions"

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
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key must be provided for OpenAI chat")
        if not model_name.strip():
            raise ValueError("model_name must be a non-empty string")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._api_key = api_key
        self._model_name = model_name
        self._client = client or _HTTPChatClient()
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
        return cls(api_key=api_key, model_name=model_name, client=client)

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

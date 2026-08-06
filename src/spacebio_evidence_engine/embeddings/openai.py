"""Optional OpenAI embedding provider (issue #41).

The provider is inactive unless an API key is supplied. Use ``from_env()`` to
construct it from environment variables; it returns ``None`` when
``OPENAI_API_KEY`` is unset so CI and local-only runs stay credential-free.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from spacebio_evidence_engine.embeddings.base import EmbeddingProvider

DEFAULT_OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_OPENAI_EMBEDDING_DIMENSION = 1536
OPENAI_EMBEDDING_MODEL_ENV = "OPENAI_EMBEDDING_MODEL"
OPENAI_API_KEY_ENV = "OPENAI_API_KEY"


class OpenAIEmbeddingError(RuntimeError):
    """Raised when the OpenAI embeddings API cannot return valid vectors."""


class _OpenAIEmbeddingClient(Protocol):
    """Minimal client surface used by ``OpenAIEmbeddingProvider``."""

    def create_embeddings(
        self,
        *,
        api_key: str,
        model: str,
        texts: Sequence[str],
        timeout_seconds: float,
    ) -> list[list[float]]: ...


@dataclass(frozen=True, slots=True)
class _HTTPEmbeddingClient:
    """Small stdlib HTTP client to avoid requiring the OpenAI SDK in CI."""

    endpoint: str = "https://api.openai.com/v1/embeddings"

    def create_embeddings(
        self,
        *,
        api_key: str,
        model: str,
        texts: Sequence[str],
        timeout_seconds: float,
    ) -> list[list[float]]:
        payload = json.dumps({"model": model, "input": list(texts)}).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=payload,
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
            message = f"OpenAI embeddings request failed: HTTP {exc.code}"
            raise OpenAIEmbeddingError(message) from exc
        except urllib.error.URLError as exc:  # pragma: no cover - live API path
            raise OpenAIEmbeddingError("OpenAI embeddings request failed") from exc

        try:
            body = json.loads(raw_body.decode("utf-8"))
            data = body["data"]
            ordered = sorted(data, key=lambda item: int(item["index"]))
            return [[float(value) for value in item["embedding"]] for item in ordered]
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise OpenAIEmbeddingError("OpenAI embeddings response was malformed") from exc


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI-backed provider for documents and queries.

    Tests should pass an injected ``client`` and fake API key. Production callers
    should prefer ``from_env()`` so the provider remains disabled when no key is
    configured.
    """

    def __init__(
        self,
        *,
        api_key: str,
        model_name: str = DEFAULT_OPENAI_EMBEDDING_MODEL,
        dimension: int = DEFAULT_OPENAI_EMBEDDING_DIMENSION,
        client: _OpenAIEmbeddingClient | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key must be provided for OpenAI embeddings")
        if not model_name.strip():
            raise ValueError("model_name must be a non-empty string")
        if dimension <= 0:
            raise ValueError("dimension must be positive")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._api_key = api_key
        self._model_name = model_name
        self._dimension = dimension
        self._client = client or _HTTPEmbeddingClient()
        self._timeout_seconds = timeout_seconds

    @classmethod
    def from_env(
        cls,
        *,
        environ: dict[str, str] | None = None,
        client: _OpenAIEmbeddingClient | None = None,
    ) -> OpenAIEmbeddingProvider | None:
        """Return a configured provider, or ``None`` when no API key is present."""
        env = os.environ if environ is None else environ
        api_key = env.get(OPENAI_API_KEY_ENV, "").strip()
        if not api_key:
            return None
        model_name = env.get(OPENAI_EMBEDDING_MODEL_ENV, DEFAULT_OPENAI_EMBEDDING_MODEL)
        return cls(api_key=api_key, model_name=model_name, client=client)

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self._client.create_embeddings(
            api_key=self._api_key,
            model=self._model_name,
            texts=list(texts),
            timeout_seconds=self._timeout_seconds,
        )
        self._validate_batch(vectors, expected=len(texts))
        return vectors

    def embed_query(self, text: str) -> list[float]:
        vectors = self.embed_documents([text])
        return vectors[0]

    def _validate_batch(self, vectors: list[list[float]], *, expected: int) -> None:
        if len(vectors) != expected:
            raise ValueError(f"Expected {expected} embedding(s), got {len(vectors)} from OpenAI")
        for vector in vectors:
            if len(vector) != self._dimension:
                raise ValueError(
                    f"Embedding length {len(vector)} != provider dimension {self._dimension}"
                )

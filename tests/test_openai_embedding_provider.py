"""Unit tests for the optional OpenAI embedding provider (issue #41)."""

from __future__ import annotations

from collections.abc import Sequence

import pytest

from spacebio_evidence_engine.embeddings import EmbeddingProvider, OpenAIEmbeddingProvider
from spacebio_evidence_engine.embeddings.openai import (
    DEFAULT_OPENAI_EMBEDDING_DIMENSION,
    DEFAULT_OPENAI_EMBEDDING_MODEL,
)


class StubOpenAIEmbeddingClient:
    """Deterministic stand-in for the OpenAI embeddings API."""

    def __init__(self, *, dimension: int = DEFAULT_OPENAI_EMBEDDING_DIMENSION) -> None:
        self.dimension = dimension
        self.calls: list[tuple[str, tuple[str, ...]]] = []
        self.seen_api_keys: list[str] = []

    def create_embeddings(
        self,
        *,
        api_key: str,
        model: str,
        texts: Sequence[str],
        timeout_seconds: float,
    ) -> list[list[float]]:
        assert timeout_seconds > 0
        self.calls.append((model, tuple(texts)))
        self.seen_api_keys.append(api_key)
        return [self._vector(text) for text in texts]

    def _vector(self, text: str) -> list[float]:
        seed = float(len(text))
        return [seed + float(index) * 0.01 for index in range(self.dimension)]


def test_from_env_returns_none_without_api_key() -> None:
    provider = OpenAIEmbeddingProvider.from_env(environ={}, client=StubOpenAIEmbeddingClient())
    assert provider is None


def test_from_env_uses_api_key_and_default_model() -> None:
    client = StubOpenAIEmbeddingClient()
    provider = OpenAIEmbeddingProvider.from_env(
        environ={"OPENAI_API_KEY": "test-key"},
        client=client,
    )
    assert provider is not None
    assert provider.model_name == DEFAULT_OPENAI_EMBEDDING_MODEL

    vector = provider.embed_query("microgravity muscle")
    assert len(vector) == provider.dimension
    assert client.calls == [(DEFAULT_OPENAI_EMBEDDING_MODEL, ("microgravity muscle",))]
    assert client.seen_api_keys == ["test-key"]


def test_model_name_is_configurable_from_env() -> None:
    provider = OpenAIEmbeddingProvider.from_env(
        environ={
            "OPENAI_API_KEY": "test-key",
            "OPENAI_EMBEDDING_MODEL": "custom-embedding-model",
        },
        client=StubOpenAIEmbeddingClient(),
    )
    assert provider is not None
    assert provider.model_name == "custom-embedding-model"


def test_openai_provider_is_embedding_provider() -> None:
    provider = OpenAIEmbeddingProvider(
        api_key="test-key",
        dimension=4,
        client=StubOpenAIEmbeddingClient(dimension=4),
    )
    assert isinstance(provider, EmbeddingProvider)


def test_embed_documents_and_query_are_compatible() -> None:
    provider = OpenAIEmbeddingProvider(
        api_key="test-key",
        dimension=4,
        client=StubOpenAIEmbeddingClient(dimension=4),
    )
    docs = provider.embed_documents(["alpha", "beta"])
    assert len(docs) == 2
    assert all(len(vector) == provider.dimension for vector in docs)
    assert docs[0] != docs[1]

    query = provider.embed_query("alpha")
    assert query == docs[0]


def test_empty_documents_returns_empty_list_without_api_call() -> None:
    client = StubOpenAIEmbeddingClient()
    provider = OpenAIEmbeddingProvider(api_key="test-key", dimension=4, client=client)
    assert provider.embed_documents([]) == []
    assert client.calls == []


def test_blank_api_key_rejected() -> None:
    with pytest.raises(ValueError, match="api_key"):
        OpenAIEmbeddingProvider(api_key=" ", client=StubOpenAIEmbeddingClient())


def test_malformed_embedding_count_rejected() -> None:
    class BadCountClient(StubOpenAIEmbeddingClient):
        def create_embeddings(
            self,
            *,
            api_key: str,
            model: str,
            texts: Sequence[str],
            timeout_seconds: float,
        ) -> list[list[float]]:
            del api_key, model, texts, timeout_seconds
            return [[1.0, 2.0, 3.0, 4.0]]

    provider = OpenAIEmbeddingProvider(api_key="test-key", dimension=4, client=BadCountClient())
    with pytest.raises(ValueError, match="Expected 2 embedding"):
        provider.embed_documents(["alpha", "beta"])


def test_malformed_embedding_dimension_rejected() -> None:
    provider = OpenAIEmbeddingProvider(
        api_key="test-key",
        dimension=4,
        client=StubOpenAIEmbeddingClient(dimension=3),
    )
    with pytest.raises(ValueError, match="Embedding length"):
        provider.embed_query("alpha")


def test_package_exports_openai_provider() -> None:
    from spacebio_evidence_engine import embeddings

    assert embeddings.OpenAIEmbeddingProvider is OpenAIEmbeddingProvider

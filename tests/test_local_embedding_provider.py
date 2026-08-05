"""Unit tests for LocalEmbeddingProvider (issue #40).

Strategy: inject a deterministic stub model. CI never downloads weights.
Optional live smoke: ``pytest -m embedding_smoke`` after
``pip install -e ".[embeddings]"``.
"""

from __future__ import annotations

import pytest

from spacebio_evidence_engine.embeddings import EmbeddingProvider, LocalEmbeddingProvider
from spacebio_evidence_engine.embeddings.local import DEFAULT_LOCAL_EMBEDDING_MODEL


class StubSentenceModel:
    """Deterministic stand-in for SentenceTransformer.encode."""

    def __init__(self, dimension: int = 4) -> None:
        self._dimension = dimension

    def get_sentence_embedding_dimension(self) -> int:
        return self._dimension

    def encode(
        self,
        sentences: str | list[str],
        *,
        convert_to_numpy: bool = True,
    ) -> list[list[float]] | list[float]:
        del convert_to_numpy
        if isinstance(sentences, str):
            return self._vector(sentences)
        return [self._vector(text) for text in sentences]

    def _vector(self, text: str) -> list[float]:
        seed = float(len(text))
        return [seed + float(i) * 0.1 for i in range(self._dimension)]


def test_local_provider_is_embedding_provider() -> None:
    provider = LocalEmbeddingProvider(model=StubSentenceModel())
    assert isinstance(provider, EmbeddingProvider)


def test_model_name_is_configurable() -> None:
    provider = LocalEmbeddingProvider(
        model_name="custom/local-mini",
        model=StubSentenceModel(dimension=8),
    )
    assert provider.model_name == "custom/local-mini"
    assert provider.dimension == 8


def test_default_model_name_matches_mvp_choice() -> None:
    provider = LocalEmbeddingProvider(model=StubSentenceModel())
    assert provider.model_name == DEFAULT_LOCAL_EMBEDDING_MODEL


def test_embed_documents_and_query_are_compatible() -> None:
    provider = LocalEmbeddingProvider(model=StubSentenceModel(dimension=4))
    docs = provider.embed_documents(["alpha", "beta"])
    assert len(docs) == 2
    assert all(len(v) == provider.dimension for v in docs)
    assert docs[0] != docs[1]

    query = provider.embed_query("alpha")
    assert query == docs[0]


def test_empty_documents_returns_empty_list() -> None:
    provider = LocalEmbeddingProvider(model=StubSentenceModel())
    assert provider.embed_documents([]) == []


def test_blank_model_name_rejected() -> None:
    with pytest.raises(ValueError, match="model_name"):
        LocalEmbeddingProvider(model_name="  ", model=StubSentenceModel())


def test_package_exports_local_provider() -> None:
    from spacebio_evidence_engine import embeddings

    assert embeddings.LocalEmbeddingProvider is LocalEmbeddingProvider


@pytest.mark.embedding_smoke
def test_real_minilm_smoke() -> None:
    """Optional live check — skipped unless explicitly selected.

    Run: ``pytest -m embedding_smoke`` after installing ``.[embeddings]``.
    """
    pytest.importorskip("sentence_transformers")
    provider = LocalEmbeddingProvider()
    assert provider.dimension == 384
    vector = provider.embed_query("microgravity skeletal muscle")
    assert len(vector) == 384
    docs = provider.embed_documents(["a", "b"])
    assert len(docs) == 2

"""Unit tests for the embedding provider interface (issue #39)."""

from __future__ import annotations

import ast
from collections.abc import Sequence
from pathlib import Path

import pytest

from spacebio_evidence_engine.embeddings import EmbeddingProvider
from spacebio_evidence_engine.embeddings.base import EmbeddingProvider as BaseEmbeddingProvider

ROOT = Path(__file__).resolve().parents[1]
INTERFACE_MODULE = ROOT / "src/spacebio_evidence_engine/embeddings/base.py"

# Vendor packages that must not appear in the interface module.
_FORBIDDEN_IMPORT_ROOTS = frozenset(
    {
        "openai",
        "sentence_transformers",
        "transformers",
        "torch",
        "tiktoken",
        "httpx",
        "requests",
    }
)


class FakeEmbeddingProvider(EmbeddingProvider):
    """Deterministic stand-in used only in tests."""

    def __init__(self, *, model_name: str = "fake-embed-v1", dimension: int = 4) -> None:
        self._model_name = model_name
        self._dimension = dimension

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        seed = float(len(text))
        return [seed + float(i) for i in range(self._dimension)]


def test_package_exports_embedding_provider() -> None:
    assert EmbeddingProvider is BaseEmbeddingProvider


def test_fake_provider_satisfies_interface_contract() -> None:
    provider: EmbeddingProvider = FakeEmbeddingProvider(dimension=4)

    assert provider.model_name == "fake-embed-v1"
    assert provider.dimension == 4

    docs = provider.embed_documents(["alpha", "beta"])
    assert len(docs) == 2
    assert all(len(vector) == provider.dimension for vector in docs)
    assert docs[0] != docs[1]

    query = provider.embed_query("alpha")
    assert len(query) == provider.dimension
    assert query == docs[0]


def test_incomplete_provider_cannot_be_instantiated() -> None:
    class IncompleteProvider(EmbeddingProvider):
        @property
        def model_name(self) -> str:
            return "incomplete"

        @property
        def dimension(self) -> int:
            return 2

    with pytest.raises(TypeError):
        IncompleteProvider()  # type: ignore[abstract]


def test_interface_module_has_no_provider_specific_imports() -> None:
    source = INTERFACE_MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(INTERFACE_MODULE))
    imported: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".", maxsplit=1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".", maxsplit=1)[0])

    forbidden = imported & _FORBIDDEN_IMPORT_ROOTS
    assert not forbidden, f"provider-specific imports in interface module: {sorted(forbidden)}"

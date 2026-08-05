"""Embedding provider interface (issue #39).

This module defines a provider-agnostic contract only. Do not import
sentence-transformers, OpenAI, or other vendor SDKs here.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence


class EmbeddingProvider(ABC):
    """Swappable embedding backend for documents and queries.

    Implementations must expose a fixed output dimension and the model
    identifier used to generate vectors so retrieval can record lineage.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Stable model identifier recorded with stored embeddings."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Length of each embedding vector produced by this provider."""

    @abstractmethod
    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed one or more document/chunk texts.

        Returns a list of vectors in the same order as ``texts``. Each
        vector must have length ``dimension``.
        """

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Embed a single retrieval query.

        The returned vector must have length ``dimension``. Query and
        document embeddings for the same provider must be compatible for
        similarity search.
        """

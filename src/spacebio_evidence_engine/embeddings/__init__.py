"""Embedding provider abstractions.

The interface module (`base`) has no vendor imports. Local Sentence
Transformers live in `local` (issue #40); optional OpenAI is issue #41.
"""

from spacebio_evidence_engine.embeddings.base import EmbeddingProvider
from spacebio_evidence_engine.embeddings.local import (
    DEFAULT_LOCAL_EMBEDDING_MODEL,
    LocalEmbeddingProvider,
)

__all__ = [
    "DEFAULT_LOCAL_EMBEDDING_MODEL",
    "EmbeddingProvider",
    "LocalEmbeddingProvider",
]

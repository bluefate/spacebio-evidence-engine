"""Embedding provider abstractions.

Concrete providers (local Sentence Transformers, optional OpenAI) live in
follow-on issues and must not be imported from the interface module.
"""

from spacebio_evidence_engine.embeddings.base import EmbeddingProvider

__all__ = ["EmbeddingProvider"]

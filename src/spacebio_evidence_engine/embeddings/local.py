"""Local Sentence Transformers embedding provider (issue #40).

Install the optional extra before constructing without an injected model:

    pip install -e ".[embeddings]"

Unit tests inject a stub model so CI does not download weights.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol, cast

from spacebio_evidence_engine.embeddings.base import EmbeddingProvider

DEFAULT_LOCAL_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class _EncodeModel(Protocol):
    """Minimal encode surface used by LocalEmbeddingProvider."""

    def encode(
        self,
        sentences: str | list[str],
        *,
        convert_to_numpy: bool = True,
    ) -> Any: ...


def _require_sentence_transformers() -> Any:
    try:
        # Optional extra; not installed in default CI/typecheck environments.
        import sentence_transformers as st  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - exercised when extra missing
        raise ImportError(
            "Local embeddings require the optional 'embeddings' extra. "
            'Install with: pip install -e ".[embeddings]"'
        ) from exc
    return st.SentenceTransformer


def _as_float_vectors(raw: Any) -> list[list[float]]:
    """Normalize encode() output to list[list[float]]."""
    if hasattr(raw, "tolist"):
        raw = raw.tolist()
    if not isinstance(raw, list):
        raise TypeError(f"Unexpected embedding output type: {type(raw)!r}")
    if raw and isinstance(raw[0], (int, float)):
        return [[float(v) for v in raw]]
    return [[float(v) for v in row] for row in raw]


class LocalEmbeddingProvider(EmbeddingProvider):
    """Sentence Transformers-backed provider for documents and queries.

    Pass ``model=`` in tests to inject a stub. Production use loads
    ``sentence_transformers.SentenceTransformer`` lazily on first init.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_LOCAL_EMBEDDING_MODEL,
        *,
        model: _EncodeModel | None = None,
    ) -> None:
        if not model_name.strip():
            raise ValueError("model_name must be a non-empty string")
        self._model_name = model_name
        if model is not None:
            self._model: _EncodeModel = model
        else:
            sentence_transformer = _require_sentence_transformers()
            self._model = cast(_EncodeModel, sentence_transformer(model_name))
        self._dimension = self._infer_dimension()

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = _as_float_vectors(self._model.encode(list(texts), convert_to_numpy=True))
        self._validate_batch(vectors, expected=len(texts))
        return vectors

    def embed_query(self, text: str) -> list[float]:
        vectors = _as_float_vectors(self._model.encode(text, convert_to_numpy=True))
        self._validate_batch(vectors, expected=1)
        return vectors[0]

    def _infer_dimension(self) -> int:
        get_dim = getattr(self._model, "get_sentence_embedding_dimension", None)
        if callable(get_dim):
            raw_dim = cast(Any, get_dim())
            dim = int(raw_dim)
            if dim > 0:
                return dim
        vectors = _as_float_vectors(self._model.encode("", convert_to_numpy=True))
        if not vectors or not vectors[0]:
            raise ValueError("Could not infer embedding dimension from model")
        return len(vectors[0])

    def _validate_batch(self, vectors: list[list[float]], *, expected: int) -> None:
        if len(vectors) != expected:
            raise ValueError(f"Expected {expected} embedding(s), got {len(vectors)} from model")
        for vector in vectors:
            if len(vector) != self._dimension:
                raise ValueError(
                    f"Embedding length {len(vector)} != provider dimension {self._dimension}"
                )

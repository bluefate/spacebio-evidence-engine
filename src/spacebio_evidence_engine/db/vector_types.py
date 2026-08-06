"""pgvector-backed embedding column type and MVP dimension constants (issue #42)."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator

# MVP default matches LocalEmbeddingProvider / all-MiniLM-L6-v2.
MVP_EMBEDDING_DIMENSION = 384
MVP_EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingVector(TypeDecorator):
    """Store float vectors as ``vector(N)`` on PostgreSQL and JSON text on SQLite.

    Production databases must use PostgreSQL with the ``vector`` extension
    (#8). SQLite storage exists only so Alembic ``upgrade head`` stays
    runnable in fast CI migration tests.
    """

    impl = Text
    cache_ok = True

    def __init__(self, dim: int = MVP_EMBEDDING_DIMENSION) -> None:
        super().__init__()
        self.dim = dim

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            from pgvector.sqlalchemy import Vector

            return dialect.type_descriptor(Vector(self.dim))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value: list[float] | None, dialect: Any) -> Any:
        if value is None:
            return None
        if len(value) != self.dim:
            raise ValueError(
                f"embedding length {len(value)} does not match required dimension {self.dim}"
            )
        if dialect.name == "postgresql":
            return value
        return json.dumps(value)

    def process_result_value(self, value: Any, dialect: Any) -> list[float] | None:
        if value is None:
            return None
        if dialect.name == "postgresql":
            return list(value)
        if isinstance(value, str):
            parsed = json.loads(value)
            return [float(item) for item in parsed]
        return list(value)

"""Retrieval utilities for semantic and filtered hybrid search."""

from spacebio_evidence_engine.retrieval.filters import (
    ALLOWED_FILTER_KEYS,
    InvalidRetrievalFilterError,
    RetrievalFilters,
    SemanticSearchFilters,
    apply_retrieval_filters,
    parse_retrieval_filters,
)
from spacebio_evidence_engine.retrieval.fts import (
    DEFAULT_TOP_K,
    KeywordSearchHit,
    keyword_search,
)
from spacebio_evidence_engine.retrieval.hybrid import hybrid_search
from spacebio_evidence_engine.retrieval.semantic import (
    SemanticSearchHit,
    cosine_similarity,
    semantic_search,
)

__all__ = [
    "ALLOWED_FILTER_KEYS",
    "DEFAULT_TOP_K",
    "InvalidRetrievalFilterError",
    "KeywordSearchHit",
    "RetrievalFilters",
    "SemanticSearchFilters",
    "SemanticSearchHit",
    "apply_retrieval_filters",
    "cosine_similarity",
    "hybrid_search",
    "keyword_search",
    "parse_retrieval_filters",
    "semantic_search",
]

"""Developer retrieval diagnostics payload (issue #67).

Built from the same structured retrieval log as production logs: hashed query,
chunk IDs, ranks, and scores. Never includes raw query text, prompts, secrets,
API keys, or chunk text.
"""

from __future__ import annotations

from spacebio_evidence_engine.db.vector_types import MVP_EMBEDDING_DIMENSION
from spacebio_evidence_engine.retrieval.logging import make_retrieval_log_record
from spacebio_evidence_engine.retrieval.semantic import SemanticSearchHit

DEFAULT_DIAGNOSTICS_EMBEDDING_MODEL = "unknown"


def citation_id_for_rank(rank: int) -> str:
    """Return the C-n citation id used by grounded answers for this rank."""

    if rank < 1:
        raise ValueError("rank must be at least 1")
    return f"C{rank}"


def build_retrieval_diagnostics_payload(
    *,
    query: str,
    top_k: int,
    hits: list[SemanticSearchHit],
    embedding_model: str | None = None,
    embedding_dimension: int = MVP_EMBEDDING_DIMENSION,
) -> dict[str, object]:
    """Return a JSON-serializable diagnostics record without secrets or chunk text."""

    model_name = embedding_model or (
        hits[0].model_name if hits else DEFAULT_DIAGNOSTICS_EMBEDDING_MODEL
    )
    record = make_retrieval_log_record(
        query=query,
        top_k=top_k,
        filters=None,
        hits=hits,
        embedding_model=model_name,
        embedding_dimension=embedding_dimension,
    )
    selected_chunks: list[dict[str, object]] = []
    citation_ids: list[str] = []
    for hit in record.selected_chunks:
        citation_id = citation_id_for_rank(hit.rank)
        citation_ids.append(citation_id)
        payload = hit.to_dict()
        payload["citation_id"] = citation_id
        selected_chunks.append(payload)
    return {
        "query_sha256": record.query_sha256,
        "query_length": record.query_length,
        "top_k": record.top_k,
        "search_algorithm": record.search_algorithm,
        "score_kind": record.score_kind,
        "embedding_model": record.embedding_model,
        "embedding_dimension": record.embedding_dimension,
        "result_count": record.result_count,
        "selected_chunks": selected_chunks,
        "selected_citation_ids": citation_ids,
    }

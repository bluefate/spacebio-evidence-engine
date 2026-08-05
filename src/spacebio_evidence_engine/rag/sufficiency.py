"""Evidence sufficiency evaluation and insufficient-evidence response builder."""

from __future__ import annotations

from spacebio_evidence_engine.schemas.answers import (
    EvidenceSufficiency,
    GroundedAnswerResponse,
    PassageCitation,
)

# Minimum evidence for an MVP answer. These are intentionally conservative to
# avoid model hallucination when retrieval is empty or weak.
_MIN_RETRIEVED_CHUNKS = 3
_MIN_SUPPORTING_PUBLICATIONS = 2


def evaluate_sufficiency(
    citations: list[PassageCitation],
    min_chunks: int = _MIN_RETRIEVED_CHUNKS,
    min_publications: int = _MIN_SUPPORTING_PUBLICATIONS,
) -> EvidenceSufficiency:
    """Return an EvidenceSufficiency for the retrieved citations.

    Policy
    ------
    - ``insufficient``: zero citations, zero supporting publications, or fewer
      than ``min_chunks``/``min_publications``.
    - ``sufficient``: at least ``min_chunks`` citations and at least
      ``min_publications`` distinct supporting publications.

    This function does not call an LLM.
    """
    if min_chunks < 0:
        raise ValueError("min_chunks must be non-negative")
    if min_publications < 0:
        raise ValueError("min_publications must be non-negative")

    chunk_count = len(citations)
    publication_count = len({c.publication_id for c in citations})

    if chunk_count == 0 or publication_count == 0:
        return EvidenceSufficiency(
            status="insufficient",
            reason="No on-topic passages were retrieved from the controlled corpus.",
            retrieved_chunk_count=chunk_count,
            supporting_publication_count=publication_count,
        )

    if chunk_count < min_chunks or publication_count < min_publications:
        return EvidenceSufficiency(
            status="insufficient",
            reason=(
                f"Retrieved {chunk_count} passage(s) from {publication_count} "
                f"publication(s); minimum is {min_chunks} passages from "
                f"{min_publications} publications."
            ),
            retrieved_chunk_count=chunk_count,
            supporting_publication_count=publication_count,
        )

    return EvidenceSufficiency(
        status="sufficient",
        retrieved_chunk_count=chunk_count,
        supporting_publication_count=publication_count,
    )


def build_insufficient_evidence_response(
    question: str, sufficiency: EvidenceSufficiency
) -> GroundedAnswerResponse:
    """Return a grounded response that explicitly declines to answer.

    The response contains no citations and does not invoke an LLM, ensuring the
    system cannot fill gaps with general model knowledge.
    """
    return GroundedAnswerResponse(
        question=question,
        answer_text="Insufficient evidence in the controlled corpus to answer this question.",
        citations=[],
        sufficiency=sufficiency,
        model_name=None,
    )


def build_insufficient_evidence_response_if_needed(
    question: str,
    citations: list[PassageCitation],
    min_chunks: int = _MIN_RETRIEVED_CHUNKS,
    min_publications: int = _MIN_SUPPORTING_PUBLICATIONS,
) -> GroundedAnswerResponse | None:
    """Evaluate citations and return an insufficient-evidence response if weak.

    Returns ``None`` when evidence is sufficient, signalling the caller to
    proceed with grounded generation.
    """
    sufficiency = evaluate_sufficiency(
        citations, min_chunks=min_chunks, min_publications=min_publications
    )
    if sufficiency.status == "insufficient":
        return build_insufficient_evidence_response(question, sufficiency)
    return None

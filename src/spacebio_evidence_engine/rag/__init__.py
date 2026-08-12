"""Retrieval-augmented generation behavior for grounded answers."""

from __future__ import annotations

from spacebio_evidence_engine.rag.answer import (
    DEFAULT_ANSWER_MAX_TOKENS,
    GroundedAnswerError,
    GroundedAnswerService,
    RetrievedEvidenceProvider,
)
from spacebio_evidence_engine.rag.citations import (
    CitationEmissionResult,
    emit_citations_for_answer_text,
    emit_passage_citations,
    extract_citation_markers,
)
from spacebio_evidence_engine.rag.context import (
    DEFAULT_EVIDENCE_TOKEN_BUDGET,
    DEFAULT_INSTRUCTIONS,
    AssembledEvidenceBlock,
    ContextAssemblyResult,
    assemble_context,
)
from spacebio_evidence_engine.rag.prompt import (
    GROUNDED_ANSWER_PROMPT_ID,
    GROUNDED_ANSWER_PROMPT_VERSION,
    GroundedAnswerPrompt,
    render_grounded_answer_prompt,
)
from spacebio_evidence_engine.rag.sufficiency import (
    build_insufficient_evidence_response,
    build_insufficient_evidence_response_if_needed,
    evaluate_sufficiency,
)

__all__ = [
    "AssembledEvidenceBlock",
    "CitationEmissionResult",
    "ContextAssemblyResult",
    "DEFAULT_ANSWER_MAX_TOKENS",
    "DEFAULT_EVIDENCE_TOKEN_BUDGET",
    "DEFAULT_INSTRUCTIONS",
    "GROUNDED_ANSWER_PROMPT_ID",
    "GROUNDED_ANSWER_PROMPT_VERSION",
    "GroundedAnswerPrompt",
    "GroundedAnswerError",
    "GroundedAnswerService",
    "RetrievedEvidenceProvider",
    "assemble_context",
    "build_insufficient_evidence_response",
    "build_insufficient_evidence_response_if_needed",
    "emit_citations_for_answer_text",
    "emit_passage_citations",
    "evaluate_sufficiency",
    "extract_citation_markers",
    "render_grounded_answer_prompt",
]

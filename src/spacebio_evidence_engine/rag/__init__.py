"""Retrieval-augmented generation behavior for grounded answers."""

from __future__ import annotations

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
    "ContextAssemblyResult",
    "DEFAULT_EVIDENCE_TOKEN_BUDGET",
    "DEFAULT_INSTRUCTIONS",
    "GROUNDED_ANSWER_PROMPT_ID",
    "GROUNDED_ANSWER_PROMPT_VERSION",
    "GroundedAnswerPrompt",
    "assemble_context",
    "build_insufficient_evidence_response",
    "build_insufficient_evidence_response_if_needed",
    "evaluate_sufficiency",
    "render_grounded_answer_prompt",
]

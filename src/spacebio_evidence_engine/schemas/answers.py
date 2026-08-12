"""Versioned API / domain schemas for grounded answers (issue #57)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Bump when breaking response fields change; record in RAG_ARCHITECTURE.md.
GROUNDED_ANSWER_SCHEMA_VERSION = "1.0.0"

SufficiencyStatus = Literal["sufficient", "insufficient", "marginal"]


class PassageCitation(BaseModel):
    """Passage-level citation tied to a retrieved chunk."""

    model_config = ConfigDict(extra="forbid")

    citation_id: str = Field(
        ...,
        description="Stable id referenced from answer_text (e.g. C1).",
        min_length=1,
    )
    chunk_id: str = Field(..., description="Retrieved chunk / passage id.", min_length=1)
    publication_id: str = Field(..., description="Corpus publication id.", min_length=1)
    title: str | None = Field(default=None, description="Publication title when known.")
    section: str | None = Field(default=None, description="Section heading when known.")
    page: int | None = Field(default=None, ge=1, description="1-based page when known.")
    source_url: str | None = Field(default=None, description="Link to the source publication.")
    excerpt: str | None = Field(
        default=None,
        description="Short supporting excerpt from the retrieved passage.",
    )


class AnswerClaim(BaseModel):
    """Individual answer claim mapped to supporting passage citations."""

    model_config = ConfigDict(extra="forbid")

    claim_id: str = Field(
        ...,
        description="Stable claim id for UI/evaluation traceability.",
        min_length=1,
    )
    text: str = Field(..., description="Single answer claim.", min_length=1)
    citation_ids: list[str] = Field(
        ...,
        description="Passage citation ids supporting this claim.",
        min_length=1,
    )


class EvidenceSufficiency(BaseModel):
    """Whether retrieved evidence is enough to answer."""

    model_config = ConfigDict(extra="forbid")

    status: SufficiencyStatus
    reason: str | None = Field(
        default=None,
        description="Human-readable explanation when status is not sufficient.",
    )
    retrieved_chunk_count: int = Field(default=0, ge=0)
    supporting_publication_count: int = Field(default=0, ge=0)


class LimitationNote(BaseModel):
    """Study or evidence limitation preserved in the response."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(..., min_length=1)
    citation_ids: list[str] = Field(default_factory=list)


class ConflictFinding(BaseModel):
    """Conflicting findings across cited evidence when detected."""

    model_config = ConfigDict(extra="forbid")

    summary: str = Field(..., min_length=1)
    citation_ids: list[str] = Field(default_factory=list)


class AnswerWarning(BaseModel):
    """Non-fatal warning (sparse evidence, species mix, etc.)."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)


class AskRequest(BaseModel):
    """Request body for grounded `/ask` (endpoint wiring is follow-on)."""

    model_config = ConfigDict(extra="forbid")

    question: str = Field(..., min_length=1)
    top_k: int = Field(default=8, ge=1, le=50)


class GroundedAnswerResponse(BaseModel):
    """Grounded answer payload: text, citations, sufficiency, limitations, conflicts."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(
        default=GROUNDED_ANSWER_SCHEMA_VERSION,
        description="Response schema version for clients and eval harnesses.",
    )
    question: str = Field(..., min_length=1)
    answer_text: str = Field(
        ...,
        description="Answer prose; cite with citation_id markers when evidence exists.",
    )
    claims: list[AnswerClaim] = Field(
        default_factory=list,
        description="Claim-level source mapping for UI and evaluation.",
    )
    citations: list[PassageCitation] = Field(default_factory=list)
    sufficiency: EvidenceSufficiency
    limitations: list[LimitationNote] = Field(default_factory=list)
    conflicts: list[ConflictFinding] = Field(default_factory=list)
    warnings: list[AnswerWarning] = Field(default_factory=list)
    model_name: str | None = Field(
        default=None,
        description="LLM model id used for generation when applicable.",
    )

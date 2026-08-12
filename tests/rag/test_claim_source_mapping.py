"""Unit tests for claim-to-source mapping validation (issue #56)."""

from __future__ import annotations

from dataclasses import replace

from pydantic import ValidationError

from spacebio_evidence_engine.rag import (
    ContextAssemblyResult,
    assemble_context,
    validate_claim_source_mapping,
)
from spacebio_evidence_engine.retrieval import SemanticSearchHit
from spacebio_evidence_engine.schemas import (
    AnswerClaim,
    EvidenceSufficiency,
    GroundedAnswerResponse,
    PassageCitation,
)


def _hit(
    *,
    chunk_id: str,
    publication_id: str = "pub_001",
    title: str = "Microgravity skeletal muscle study",
    section: str = "results",
    page_start: int | None = 4,
    source_url: str = "https://doi.org/10.0/example",
    text: str = "Soleus mass decreased in simulated microgravity.",
) -> SemanticSearchHit:
    return SemanticSearchHit(
        chunk_id=chunk_id,
        score=0.9,
        publication_id=publication_id,
        title=title,
        section=section,
        chunk_text=text,
        source_url=source_url,
        page_start=page_start,
        page_end=page_start,
        section_heading=section.title(),
        model_name="fixture-model",
    )


def _context() -> ContextAssemblyResult:
    return assemble_context(
        [
            _hit(chunk_id="chk_a"),
            _hit(
                chunk_id="chk_b",
                publication_id="pub_002",
                title="Spaceflight muscle fiber study",
                section="methods",
                page_start=8,
                source_url="https://doi.org/10.0/other",
                text="Fiber cross-sectional area was measured after unloading.",
            ),
        ],
        token_budget=500,
    )


def test_claim_source_mapping_preserves_citation_and_chunk_provenance() -> None:
    claims = [
        AnswerClaim(
            claim_id="claim_1",
            text="Skeletal muscle outcomes changed under unloading.",
            citation_ids=["C1", "C2", "C1"],
        )
    ]

    result = validate_claim_source_mapping(claims, _context())

    assert result.valid is True
    assert result.rejected_claim_ids == ()
    assert result.claims[0].citation_ids == ["C1", "C2"]
    assert result.mappings[0].chunk_ids == ("chk_a", "chk_b")
    assert [citation.citation_id for citation in result.citations] == ["C1", "C2"]
    first = result.mappings[0].citations[0]
    assert first.publication_id == "pub_001"
    assert first.title == "Microgravity skeletal muscle study"
    assert first.section == "results"
    assert first.page == 4
    assert first.source_url == "https://doi.org/10.0/example"


def test_claim_without_sources_is_rejected_with_warning() -> None:
    claims = [AnswerClaim(claim_id="claim_1", text="Unsupported claim.", citation_ids=[" "])]

    result = validate_claim_source_mapping(claims, _context())

    assert result.valid is False
    assert result.claims == ()
    assert result.mappings == ()
    assert result.rejected_claim_ids == ("claim_1",)
    assert result.warnings[0].code == "claim_without_sources_rejected"


def test_claim_with_unknown_citation_is_rejected_with_failure_signal() -> None:
    claims = [
        AnswerClaim(
            claim_id="claim_1",
            text="Unsupported claim.",
            citation_ids=["C1", "C404"],
        )
    ]

    result = validate_claim_source_mapping(claims, _context())

    assert result.valid is False
    assert result.claims == ()
    assert result.rejected_claim_ids == ("claim_1",)
    assert result.rejected_citation_ids == ("C404",)
    assert [warning.code for warning in result.warnings] == [
        "claim_sources_rejected",
        "unknown_citation_ids_rejected",
    ]


def test_claim_with_unretrieved_chunk_citation_is_rejected() -> None:
    context = _context()
    tampered = replace(
        context,
        citations=context.citations
        + (
            PassageCitation(
                citation_id="C3",
                chunk_id="chk_not_retrieved",
                publication_id="pub_003",
                title="Unsupported publication",
                section="discussion",
                page=9,
                source_url="https://doi.org/10.0/bad",
                excerpt="This should not be emitted.",
            ),
        ),
    )
    claims = [AnswerClaim(claim_id="claim_1", text="Unsupported claim.", citation_ids=["C3"])]

    result = validate_claim_source_mapping(claims, tampered)

    assert result.valid is False
    assert result.claims == ()
    assert result.rejected_claim_ids == ("claim_1",)
    assert result.rejected_citation_ids == ("C3",)
    assert [warning.code for warning in result.warnings] == [
        "claim_sources_rejected",
        "unretrieved_citation_chunks_rejected",
    ]


def test_grounded_answer_response_accepts_claim_list_with_citation_ids() -> None:
    context = _context()
    mapping = validate_claim_source_mapping(
        [
            AnswerClaim(
                claim_id="claim_1",
                text="Soleus mass decreased in simulated microgravity.",
                citation_ids=["C1"],
            )
        ],
        context,
    )

    response = GroundedAnswerResponse(
        question="What happened to skeletal muscle in microgravity?",
        answer_text="Soleus mass decreased in simulated microgravity [C1].",
        claims=list(mapping.claims),
        citations=list(mapping.citations),
        sufficiency=EvidenceSufficiency(
            status="sufficient",
            retrieved_chunk_count=2,
            supporting_publication_count=2,
        ),
    )

    assert response.claims[0].claim_id == "claim_1"
    assert response.claims[0].citation_ids == ["C1"]
    assert response.citations[0].chunk_id == "chk_a"


def test_answer_claim_requires_at_least_one_citation_id() -> None:
    try:
        AnswerClaim(claim_id="claim_1", text="Unsupported claim.", citation_ids=[])
    except ValidationError as exc:
        assert "citation_ids" in str(exc)
    else:
        raise AssertionError("AnswerClaim accepted an empty citation list")

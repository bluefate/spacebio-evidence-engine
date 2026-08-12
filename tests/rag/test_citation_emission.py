"""Unit tests for passage-level citation emission (issue #54)."""

from __future__ import annotations

from dataclasses import replace

from spacebio_evidence_engine.rag import (
    ContextAssemblyResult,
    assemble_context,
    emit_citations_for_answer_text,
    emit_passage_citations,
    extract_citation_markers,
)
from spacebio_evidence_engine.retrieval import SemanticSearchHit
from spacebio_evidence_engine.schemas import PassageCitation


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


def test_emit_passage_citations_preserves_context_provenance() -> None:
    result = emit_passage_citations(_context())

    assert result.valid is True
    assert result.rejected_citation_ids == ()
    assert result.emitted_citation_ids == ("C1", "C2")
    assert [citation.chunk_id for citation in result.citations] == ["chk_a", "chk_b"]
    first = result.citations[0]
    assert first.publication_id == "pub_001"
    assert first.title == "Microgravity skeletal muscle study"
    assert first.section == "results"
    assert first.page == 4
    assert first.source_url == "https://doi.org/10.0/example"
    assert first.excerpt


def test_emit_requested_citations_only_from_retrieved_context() -> None:
    result = emit_passage_citations(_context(), requested_citation_ids=["C2"])

    assert result.valid is True
    assert result.emitted_citation_ids == ("C2",)
    assert len(result.citations) == 1
    assert result.citations[0].chunk_id == "chk_b"


def test_unknown_citation_ids_are_rejected_with_failure_signal() -> None:
    result = emit_passage_citations(
        _context(),
        requested_citation_ids=["C1", "C999", "C1", ""],
    )

    assert result.valid is False
    assert result.emitted_citation_ids == ("C1",)
    assert result.rejected_citation_ids == ("C999",)
    assert result.unknown_citation_ids == ("C999",)
    assert result.warnings[0].code == "unknown_citation_ids_rejected"
    assert "C999" in result.warnings[0].message


def test_unretrieved_chunk_citations_are_stripped_with_failure_signal() -> None:
    context = _context()
    tampered_citations = context.citations + (
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
    )
    tampered = replace(context, citations=tampered_citations)

    result = emit_passage_citations(tampered, requested_citation_ids=["C3"])

    assert result.valid is False
    assert result.citations == ()
    assert result.unretrieved_chunk_ids == ("chk_not_retrieved",)
    assert result.warnings[0].code == "unretrieved_citation_chunks_rejected"


def test_emit_citations_for_answer_text_uses_markers_in_order() -> None:
    text = "Muscle size decreased [C2]. A repeated marker should not duplicate [C2]."

    result = emit_citations_for_answer_text(text, _context())

    assert extract_citation_markers(text) == ("C2",)
    assert result.valid is True
    assert result.emitted_citation_ids == ("C2",)
    assert result.citations[0].chunk_id == "chk_b"


def test_answer_text_unknown_marker_is_rejected() -> None:
    result = emit_citations_for_answer_text("Unsupported sentence [C404].", _context())

    assert result.valid is False
    assert result.citations == ()
    assert result.rejected_citation_ids == ("C404",)

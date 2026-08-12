"""Unit tests for context assembly from retrieved chunks (issue #52)."""

from __future__ import annotations

from spacebio_evidence_engine.rag import assemble_context
from spacebio_evidence_engine.retrieval import SemanticSearchHit


def _hit(
    *,
    chunk_id: str,
    publication_id: str = "pub_001",
    text: str,
    score: float = 0.9,
    section: str = "results",
    page_start: int | None = 3,
) -> SemanticSearchHit:
    return SemanticSearchHit(
        chunk_id=chunk_id,
        score=score,
        publication_id=publication_id,
        title="Microgravity skeletal muscle study",
        section=section,
        chunk_text=text,
        source_url="https://doi.org/10.0/example",
        page_start=page_start,
        page_end=page_start,
        section_heading="Results",
        model_name="fixture-model",
    )


def test_assemble_context_includes_chunk_ids_and_provenance() -> None:
    hits = [
        _hit(chunk_id="chk_a", text="Soleus mass decreased in flight."),
        _hit(chunk_id="chk_b", publication_id="pub_002", text="Fiber size was reduced."),
    ]

    result = assemble_context(hits, token_budget=500)

    assert result.included_chunk_ids == ("chk_a", "chk_b")
    assert result.omitted_chunk_ids == ()
    assert "### Instructions" in result.prompt_text
    assert "### Evidence" in result.prompt_text
    assert "chunk_id=chk_a" in result.evidence_text
    assert "publication_id=pub_001" in result.evidence_text
    assert "source_url=https://doi.org/10.0/example" in result.evidence_text
    assert result.citations[0].citation_id == "C1"
    assert result.citations[0].chunk_id == "chk_a"
    assert result.citations[1].chunk_id == "chk_b"
    assert all(block.chunk_id for block in result.evidence_blocks)


def test_assemble_context_enforces_token_budget_and_records_omitted_ids() -> None:
    long_text = " ".join(f"token{i}" for i in range(200))
    hits = [
        _hit(chunk_id="chk_keep", text="Short relevant finding."),
        _hit(chunk_id="chk_omit_a", text=long_text),
        _hit(chunk_id="chk_omit_b", text=long_text),
    ]

    # Budget fits the short first hit's provenance+text, but not another header.
    result = assemble_context(hits, token_budget=20)

    assert result.included_chunk_ids == ("chk_keep",)
    assert result.omitted_chunk_ids == ("chk_omit_a", "chk_omit_b")
    evidence_tokens = sum(block.estimated_tokens for block in result.evidence_blocks)
    assert evidence_tokens <= result.token_budget
    for block in result.evidence_blocks:
        assert block.chunk_id
        assert f"chunk_id={block.chunk_id}" in result.evidence_text
        assert f"[{block.citation_id}]" in result.evidence_text


def test_assemble_context_does_not_strip_ids_when_truncating_excerpt() -> None:
    long_text = " ".join(f"word{i}" for i in range(120))
    hits = [_hit(chunk_id="chk_trunc", text=long_text)]

    result = assemble_context(hits, token_budget=80)

    assert result.included_chunk_ids == ("chk_trunc",)
    assert result.omitted_chunk_ids == ()
    block = result.evidence_blocks[0]
    assert block.chunk_id == "chk_trunc"
    assert "chunk_id=chk_trunc" in result.evidence_text
    assert len(block.excerpt.split()) < 120
    assert result.citations[0].chunk_id == "chk_trunc"
    assert block.estimated_tokens <= result.token_budget

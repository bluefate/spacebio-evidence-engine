"""Unit tests for publication chunking (issue #32)."""

from __future__ import annotations

from spacebio_evidence_engine.ingestion import (
    CHUNKING_STRATEGY_VERSION,
    ExtractedPage,
    ExtractionResult,
    SectionLabel,
    chunk_extraction,
    chunk_sections,
    chunk_text,
    detect_sections_from_text,
    estimate_tokens,
    make_chunk_id,
)
from spacebio_evidence_engine.ingestion.chunking import ChunkingPolicy

SYNTHETIC_PAPER = """\
Title of a microgravity muscle study

Abstract
Astronauts lose skeletal muscle mass in microgravity. This abstract only.

1. Introduction
Prior unloading studies show atrophy in rodent models.

2. Methods
Mice underwent hindlimb unloading for 14 days.

3. Results
Soleus mass decreased relative to controls.

4. Discussion
Findings align with prior HU literature.

5. Conclusion
Unloading induces measurable atrophy.

References
1. Example et al. Space Biol. 2020.
"""


def test_stable_chunk_ids_are_deterministic() -> None:
    first = make_chunk_id("pub_001", start_offset=10, end_offset=40, section="methods")
    second = make_chunk_id("pub_001", start_offset=10, end_offset=40, section="methods")
    assert first == second
    assert first.startswith("chk_")
    other = make_chunk_id("pub_001", start_offset=10, end_offset=41, section="methods")
    assert other != first


def test_chunk_preserves_publication_section_pages_and_offsets() -> None:
    extraction = ExtractionResult(
        pages=(
            ExtractedPage(page_number=1, text="Abstract\nShort abstract text."),
            ExtractedPage(
                page_number=2,
                text="Methods\nMice underwent hindlimb unloading for 14 days.",
            ),
        ),
        page_count=2,
        source_key="fixture.pdf",
    )
    result = chunk_extraction(extraction, publication_id="pub_fixture")
    assert result.publication_id == "pub_fixture"
    assert result.chunking_strategy_version == CHUNKING_STRATEGY_VERSION
    assert result.chunks

    methods = [c for c in result.chunks if c.section is SectionLabel.METHODS]
    assert methods
    chunk = methods[0]
    assert chunk.publication_id == "pub_fixture"
    assert chunk.start_offset < chunk.end_offset
    assert chunk.start_page == 2
    assert chunk.end_page == 2
    assert "hindlimb" in chunk.chunk_text
    assert chunk.chunk_id == make_chunk_id(
        "pub_fixture",
        start_offset=chunk.start_offset,
        end_offset=chunk.end_offset,
        section=chunk.section,
    )


def test_does_not_merge_unrelated_sections() -> None:
    result = chunk_text(SYNTHETIC_PAPER, publication_id="pub_syn")
    sections_seen = [chunk.section for chunk in result.chunks]
    assert SectionLabel.ABSTRACT in sections_seen
    assert SectionLabel.METHODS in sections_seen
    # Each chunk stays within one section label; no cross-section merge.
    for chunk in result.chunks:
        span_text = SYNTHETIC_PAPER[chunk.start_offset : chunk.end_offset]
        assert chunk.chunk_text == span_text


def test_unknown_spans_chunked_without_relabel() -> None:
    text = "Front matter only.\nNo recognizable IMRaD headings here.\n"
    result = chunk_text(text, publication_id="pub_unknown")
    assert result.chunks
    assert all(chunk.section is SectionLabel.UNKNOWN for chunk in result.chunks)


def test_large_section_splits_with_overlap_and_size_policy() -> None:
    # Build a methods body large enough to force multiple windows.
    sentences = [
        f"Observation {i} shows muscle fiber area changed under unloading conditions."
        for i in range(120)
    ]
    body = "Methods\n" + " ".join(sentences)
    policy = ChunkingPolicy(target_tokens=80, min_tokens=40, max_tokens=100, overlap_ratio=0.2)
    result = chunk_text(body, publication_id="pub_large", policy=policy)
    methods = [c for c in result.chunks if c.section is SectionLabel.METHODS]
    assert len(methods) >= 2
    for chunk in methods:
        # Soft upper bound: allow a little overshoot from sentence boundaries.
        assert estimate_tokens(chunk.chunk_text) <= policy.max_tokens + 40

    # Overlap: consecutive windows should share some absolute range.
    assert methods[0].end_offset > methods[1].start_offset


def test_chunk_sections_api_uses_detection_result() -> None:
    detection = detect_sections_from_text(SYNTHETIC_PAPER)
    result = chunk_sections(detection, publication_id="pub_api")
    assert result.chunks
    assert all(c.publication_id == "pub_api" for c in result.chunks)
    abstracts = [c for c in result.chunks if c.is_abstract]
    assert abstracts
    assert abstracts[0].section is SectionLabel.ABSTRACT

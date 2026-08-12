"""Unit tests for ingestion chunking provenance edge cases (issue #37)."""

from __future__ import annotations

from spacebio_evidence_engine.ingestion import (
    CHUNKING_STRATEGY_VERSION,
    ChunkingPolicy,
    ExtractedPage,
    ExtractionResult,
    SectionLabel,
    SectionSpan,
    chunk_extraction,
    chunk_sections,
    chunk_text,
    estimate_tokens,
    make_chunk_id,
)


def test_chunk_extraction_preserves_source_key_section_heading_and_page_range() -> None:
    extraction = ExtractionResult(
        pages=(
            ExtractedPage(
                page_number=1,
                text="Abstract\nSkeletal muscle changes during spaceflight.",
            ),
            ExtractedPage(
                page_number=2,
                text="Methods\nMicrogravity analogue protocol continued",
            ),
            ExtractedPage(
                page_number=3,
                text="for fourteen days with matched controls.",
            ),
        ),
        page_count=3,
        source_key="pub_37/muscle.pdf",
    )

    result = chunk_extraction(extraction, publication_id="pub_37")
    methods = [chunk for chunk in result.chunks if chunk.section is SectionLabel.METHODS][0]

    assert result.source_key == "pub_37/muscle.pdf"
    assert methods.publication_id == "pub_37"
    assert methods.section_heading == "Methods"
    assert methods.start_page == 2
    assert methods.end_page == 3
    assert methods.chunking_strategy_version == CHUNKING_STRATEGY_VERSION
    assert methods.chunk_id == make_chunk_id(
        "pub_37",
        start_offset=methods.start_offset,
        end_offset=methods.end_offset,
        section=SectionLabel.METHODS,
    )


def test_chunk_text_uses_supplied_page_starts_for_plain_text_provenance() -> None:
    page_1 = "Abstract\nMicrogravity skeletal muscle abstract."
    page_2 = "Results\nMuscle fiber size changed in unloading."
    text = f"{page_1}\n\n{page_2}"

    result = chunk_text(
        text,
        publication_id="pub_pages",
        page_starts=((0, 1), (len(page_1) + 2, 2)),
        source_key="inline-pages",
    )
    results = [chunk for chunk in result.chunks if chunk.section is SectionLabel.RESULTS][0]

    assert result.source_key == "inline-pages"
    assert results.start_page == 2
    assert results.end_page == 2
    assert text[results.start_offset : results.end_offset] == results.chunk_text


def test_empty_section_spans_are_skipped_without_placeholder_chunks() -> None:
    spans = (
        SectionSpan(
            label=SectionLabel.METHODS,
            text="   ",
            start_offset=10,
            end_offset=13,
            start_page=1,
            end_page=1,
            heading_text="Methods",
            heading_matched=True,
        ),
    )

    result = chunk_sections(spans, publication_id="pub_empty")

    assert result.chunks == ()
    assert result.publication_id == "pub_empty"


def test_chunk_ids_change_with_strategy_version_for_lineage() -> None:
    first = make_chunk_id(
        "pub_lineage",
        start_offset=0,
        end_offset=25,
        section=SectionLabel.RESULTS,
        strategy_version="1.0.0",
    )
    second = make_chunk_id(
        "pub_lineage",
        start_offset=0,
        end_offset=25,
        section=SectionLabel.RESULTS,
        strategy_version="1.0.1",
    )

    assert first != second


def test_punctuation_free_long_section_is_split_with_bounded_chunks() -> None:
    text = "Methods\n" + " ".join(f"unloading{i}" for i in range(180))
    policy = ChunkingPolicy(target_tokens=30, min_tokens=20, max_tokens=40, overlap_ratio=0.25)

    result = chunk_text(text, publication_id="pub_long", policy=policy)
    methods = [chunk for chunk in result.chunks if chunk.section is SectionLabel.METHODS]

    assert len(methods) > 1
    assert all(estimate_tokens(chunk.chunk_text) <= policy.max_tokens for chunk in methods)
    assert methods[0].end_offset > methods[1].start_offset

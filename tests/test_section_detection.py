"""Unit tests for publication section detection (issue #30)."""

from __future__ import annotations

from spacebio_evidence_engine.ingestion import (
    ExtractedPage,
    ExtractionResult,
    SectionDetectionResult,
    SectionLabel,
    detect_sections,
    detect_sections_from_text,
)

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


def test_detects_labeled_spans_with_offsets() -> None:
    result = detect_sections_from_text(SYNTHETIC_PAPER)
    labels = [section.label for section in result.sections]
    assert SectionLabel.ABSTRACT in labels
    assert SectionLabel.METHODS in labels
    assert SectionLabel.RESULTS in labels
    assert SectionLabel.UNKNOWN in labels  # title preamble

    abstract = result.sections_by_label(SectionLabel.ABSTRACT)[0]
    assert abstract.heading_matched is True
    assert "Astronauts lose" in abstract.text
    assert abstract.start_offset < abstract.end_offset
    assert SYNTHETIC_PAPER[abstract.start_offset : abstract.end_offset] == abstract.text


def test_unknown_sections_handled_safely_without_inventing() -> None:
    text = "Front matter only.\nNo recognizable IMRaD headings here.\n"
    result = detect_sections_from_text(text)
    assert len(result.sections) == 1
    assert result.sections[0].label is SectionLabel.UNKNOWN
    assert result.sections[0].heading_matched is False
    # Must not invent methods/results when absent.
    assert result.sections_by_label(SectionLabel.METHODS) == ()
    assert result.sections_by_label(SectionLabel.RESULTS) == ()


def test_abstract_is_not_treated_as_full_study() -> None:
    result = detect_sections_from_text(SYNTHETIC_PAPER)
    assert result.has_abstract is True
    assert result.abstract_is_not_full_study is True
    abstract = result.sections_by_label(SectionLabel.ABSTRACT)[0]
    assert abstract.is_abstract is True
    # Other body sections remain distinct from the abstract span.
    methods = result.sections_by_label(SectionLabel.METHODS)[0]
    assert methods.start_offset >= abstract.end_offset


def test_page_mapping_from_extraction_result() -> None:
    extraction = ExtractionResult(
        pages=(
            ExtractedPage(page_number=1, text="Abstract\nShort abstract text."),
            ExtractedPage(page_number=2, text="Methods\nDetailed protocol here."),
        ),
        page_count=2,
        source_key="pub_test/sample.pdf",
    )
    result = detect_sections(extraction)
    assert result.source_key == "pub_test/sample.pdf"
    abstract = result.sections_by_label(SectionLabel.ABSTRACT)[0]
    methods = result.sections_by_label(SectionLabel.METHODS)[0]
    assert abstract.start_page == 1
    assert methods.start_page == 2


def test_empty_text_returns_no_sections() -> None:
    result = detect_sections_from_text("   ")
    assert result == SectionDetectionResult(sections=(), source_key=None)

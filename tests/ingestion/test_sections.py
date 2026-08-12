"""Unit tests for ingestion section detection edge cases (issue #37)."""

from __future__ import annotations

from spacebio_evidence_engine.ingestion import (
    ExtractedPage,
    ExtractionResult,
    SectionLabel,
    detect_sections,
    detect_sections_from_text,
)


def test_detect_sections_preserves_page_span_across_multi_page_section() -> None:
    extraction = ExtractionResult(
        pages=(
            ExtractedPage(
                page_number=1,
                text="Title\n\nAbstract\nMicrogravity affects skeletal muscle.",
            ),
            ExtractedPage(
                page_number=2,
                text=(
                    "Continued abstract with provenance.\n\n"
                    "Materials and Methods\nCells were unloaded."
                ),
            ),
            ExtractedPage(page_number=3, text="Results and Discussion\nAtrophy markers changed."),
        ),
        page_count=3,
        source_key="pub_skeletal_muscle/sample.pdf",
    )

    result = detect_sections(extraction)
    abstract = result.sections_by_label(SectionLabel.ABSTRACT)[0]
    methods = result.sections_by_label(SectionLabel.METHODS)[0]
    results = result.sections_by_label(SectionLabel.RESULTS)[0]

    assert result.source_key == "pub_skeletal_muscle/sample.pdf"
    assert abstract.heading_text == "Abstract"
    assert abstract.start_page == 1
    assert abstract.end_page == 2
    assert methods.heading_text == "Materials and Methods"
    assert methods.start_page == 2
    assert results.heading_text == "Results and Discussion"
    assert results.start_page == 3


def test_numbered_and_synonym_headings_are_labeled_without_body_rewrite() -> None:
    text = (
        "Front matter\n"
        "1 Background\n"
        "Microgravity context.\n"
        "2.1 Experimental procedures\n"
        "Hindlimb unloading protocol.\n"
        "3 Summary\n"
        "Limits remain.\n"
    )

    result = detect_sections_from_text(text)

    assert [section.label for section in result.sections] == [
        SectionLabel.UNKNOWN,
        SectionLabel.INTRODUCTION,
        SectionLabel.METHODS,
        SectionLabel.CONCLUSION,
    ]
    for section in result.sections:
        assert text[section.start_offset : section.end_offset] == section.text


def test_long_heading_like_line_is_not_misclassified() -> None:
    long_line = "Results " + "microgravity skeletal muscle " * 5
    text = f"{long_line}\nThis should remain unlabeled body text."

    result = detect_sections_from_text(text)

    assert len(result.sections) == 1
    assert result.sections[0].label is SectionLabel.UNKNOWN
    assert result.sections[0].heading_matched is False


def test_abstract_only_document_is_flagged_but_not_promoted_to_full_study() -> None:
    result = detect_sections_from_text("Abstract\nOnly an abstract is available.")

    assert result.has_abstract is True
    assert result.abstract_is_not_full_study is True
    assert result.sections_by_label(SectionLabel.METHODS) == ()
    assert result.sections_by_label(SectionLabel.RESULTS) == ()

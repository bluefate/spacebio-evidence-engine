"""Section detection for extracted publication text (issue #30).

Detects common IMRaD-style headings from plain text. Missing sections are
never invented — unlabeled spans are labeled ``unknown``. Abstract spans
are flagged so downstream metadata must not treat an abstract as a full study.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from spacebio_evidence_engine.ingestion.extract import ExtractionResult


class SectionLabel(StrEnum):
    """Known section kinds plus a safe catch-all for unlabeled text."""

    ABSTRACT = "abstract"
    INTRODUCTION = "introduction"
    METHODS = "methods"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    REFERENCES = "references"
    ACKNOWLEDGEMENTS = "acknowledgements"
    SUPPLEMENTARY = "supplementary"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class SectionSpan:
    """A labeled contiguous span of publication text."""

    label: SectionLabel
    text: str
    start_offset: int
    end_offset: int
    start_page: int | None = None
    end_page: int | None = None
    heading_text: str | None = None
    heading_matched: bool = False

    @property
    def is_abstract(self) -> bool:
        return self.label is SectionLabel.ABSTRACT


@dataclass(frozen=True, slots=True)
class SectionDetectionResult:
    """Ordered section spans for one publication extraction."""

    sections: tuple[SectionSpan, ...]
    source_key: str | None = None

    @property
    def has_abstract(self) -> bool:
        return any(section.is_abstract for section in self.sections)

    @property
    def abstract_is_not_full_study(self) -> bool:
        """Always True: abstracts must never be treated as complete studies."""
        return True

    def sections_by_label(self, label: SectionLabel) -> tuple[SectionSpan, ...]:
        return tuple(section for section in self.sections if section.label is label)


# Heading patterns: (label, compiled regex matching a whole heading line).
# Order within the list does not control document order; first match wins per line.
_HEADING_PATTERNS: tuple[tuple[SectionLabel, re.Pattern[str]], ...] = (
    (
        SectionLabel.ABSTRACT,
        re.compile(r"^(?:\d+(?:\.\d+)*\.?\s+)?abstract\s*$", re.IGNORECASE),
    ),
    (
        SectionLabel.INTRODUCTION,
        re.compile(
            r"^(?:\d+(?:\.\d+)*\.?\s+)?(?:introduction|background)\s*$",
            re.IGNORECASE,
        ),
    ),
    (
        SectionLabel.METHODS,
        re.compile(
            r"^(?:\d+(?:\.\d+)*\.?\s+)?(?:methods?|materials\s+and\s+methods|"
            r"experimental\s+(?:procedures?|methods?)|methodology)\s*$",
            re.IGNORECASE,
        ),
    ),
    (
        SectionLabel.RESULTS,
        re.compile(
            r"^(?:\d+(?:\.\d+)*\.?\s+)?(?:results?(?:\s+and\s+discussion)?)\s*$",
            re.IGNORECASE,
        ),
    ),
    (
        SectionLabel.DISCUSSION,
        re.compile(r"^(?:\d+(?:\.\d+)*\.?\s+)?discussion\s*$", re.IGNORECASE),
    ),
    (
        SectionLabel.CONCLUSION,
        re.compile(
            r"^(?:\d+(?:\.\d+)*\.?\s+)?(?:conclusions?|summary|concluding\s+remarks)\s*$",
            re.IGNORECASE,
        ),
    ),
    (
        SectionLabel.REFERENCES,
        re.compile(
            r"^(?:\d+(?:\.\d+)*\.?\s+)?(?:references|bibliography|literature\s+cited)\s*$",
            re.IGNORECASE,
        ),
    ),
    (
        SectionLabel.ACKNOWLEDGEMENTS,
        re.compile(
            r"^(?:\d+(?:\.\d+)*\.?\s+)?acknowledgeme?nts?\s*$",
            re.IGNORECASE,
        ),
    ),
    (
        SectionLabel.SUPPLEMENTARY,
        re.compile(
            r"^(?:\d+(?:\.\d+)*\.?\s+)?(?:supplementary(?:\s+information|\s+materials?)?|"
            r"supporting\s+information)\s*$",
            re.IGNORECASE,
        ),
    ),
)


@dataclass(frozen=True, slots=True)
class _HeadingMatch:
    label: SectionLabel
    start: int
    end: int  # end of heading line (exclusive), body starts here
    heading_text: str


def detect_sections_from_text(
    text: str,
    *,
    page_starts: tuple[tuple[int, int], ...] | None = None,
    source_key: str | None = None,
) -> SectionDetectionResult:
    """Detect section spans in a single concatenated text string.

    Args:
        text: Full document text (typically ``ExtractionResult.full_text``).
        page_starts: Optional ``(char_offset, page_number)`` pairs sorted by offset
            for mapping span bounds to 1-based pages.
        source_key: Optional lineage key (storage key or path).

    Returns:
        Ordered spans. Leading text before the first heading is ``unknown``.
        Labels are only assigned when a heading matches — no invented sections.
    """
    if not text or not text.strip():
        return SectionDetectionResult(sections=(), source_key=source_key)

    headings = _find_headings(text)
    if not headings:
        span = _make_span(
            label=SectionLabel.UNKNOWN,
            text=text,
            start=0,
            end=len(text),
            page_starts=page_starts,
            heading_text=None,
            heading_matched=False,
        )
        return SectionDetectionResult(sections=(span,), source_key=source_key)

    spans: list[SectionSpan] = []
    first = headings[0]
    if first.start > 0:
        preamble = text[: first.start]
        if preamble.strip():
            spans.append(
                _make_span(
                    label=SectionLabel.UNKNOWN,
                    text=preamble,
                    start=0,
                    end=first.start,
                    page_starts=page_starts,
                    heading_text=None,
                    heading_matched=False,
                )
            )

    for index, heading in enumerate(headings):
        body_end = headings[index + 1].start if index + 1 < len(headings) else len(text)
        # Include heading line with the section body for provenance.
        section_start = heading.start
        section_text = text[section_start:body_end]
        if not section_text.strip():
            continue
        spans.append(
            _make_span(
                label=heading.label,
                text=section_text,
                start=section_start,
                end=body_end,
                page_starts=page_starts,
                heading_text=heading.heading_text,
                heading_matched=True,
            )
        )

    return SectionDetectionResult(sections=tuple(spans), source_key=source_key)


def detect_sections(extraction: ExtractionResult) -> SectionDetectionResult:
    """Detect sections from a page-ordered extraction result."""
    full_text, page_starts = _full_text_with_page_starts(extraction)
    return detect_sections_from_text(
        full_text,
        page_starts=page_starts,
        source_key=extraction.source_key,
    )


def _full_text_with_page_starts(
    extraction: ExtractionResult,
) -> tuple[str, tuple[tuple[int, int], ...]]:
    """Rebuild ``full_text`` and record the char offset where each page begins."""
    parts: list[str] = []
    page_starts: list[tuple[int, int]] = []
    offset = 0
    first = True
    for page in extraction.pages:
        if not page.text:
            continue
        if not first:
            parts.append("\n\n")
            offset += 2
        page_starts.append((offset, page.page_number))
        parts.append(page.text)
        offset += len(page.text)
        first = False
    return "".join(parts), tuple(page_starts)


def _find_headings(text: str) -> list[_HeadingMatch]:
    matches: list[_HeadingMatch] = []
    for match in re.finditer(r"(?m)^([^\n]+)$", text):
        line = match.group(1).strip()
        if not line or len(line) > 80:
            continue
        label = _classify_heading(line)
        if label is None:
            continue
        # Body starts after the newline following the heading (or EOF).
        line_end = match.end()
        if line_end < len(text) and text[line_end] == "\n":
            body_start = line_end + 1
        else:
            body_start = line_end
        matches.append(
            _HeadingMatch(
                label=label,
                start=match.start(),
                end=body_start,
                heading_text=line,
            )
        )
    matches.sort(key=lambda item: item.start)
    return matches


def _classify_heading(line: str) -> SectionLabel | None:
    for label, pattern in _HEADING_PATTERNS:
        if pattern.match(line.strip()):
            return label
    return None


def _page_for_offset(
    offset: int,
    page_starts: tuple[tuple[int, int], ...] | None,
) -> int | None:
    if not page_starts:
        return None
    current: int | None = page_starts[0][1]
    for start, page in page_starts:
        if offset >= start:
            current = page
        else:
            break
    return current


def _make_span(
    *,
    label: SectionLabel,
    text: str,
    start: int,
    end: int,
    page_starts: tuple[tuple[int, int], ...] | None,
    heading_text: str | None,
    heading_matched: bool,
) -> SectionSpan:
    return SectionSpan(
        label=label,
        text=text,
        start_offset=start,
        end_offset=end,
        start_page=_page_for_offset(start, page_starts),
        end_page=_page_for_offset(max(start, end - 1), page_starts),
        heading_text=heading_text,
        heading_matched=heading_matched,
    )

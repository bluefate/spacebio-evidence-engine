"""Section-aware publication chunking (issue #32).

Splits labeled section spans into overlapping text chunks for retrieval.
Does not write embeddings or database rows — persistence is issue #33+.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass

from spacebio_evidence_engine.ingestion.extract import ExtractionResult, PageOffsetMap
from spacebio_evidence_engine.ingestion.sections import (
    SectionDetectionResult,
    SectionLabel,
    SectionSpan,
    detect_sections,
)

# Documented MVP policy (see docs/rag/CHUNKING_STRATEGY.md).
CHUNKING_STRATEGY_VERSION = "1.0.0"

# Approximate tokens via whitespace words (no tokenizer dependency).
TARGET_TOKENS = 700
MIN_TOKENS = 500
MAX_TOKENS = 900
OVERLAP_RATIO = 0.15

_WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True, slots=True)
class TextChunk:
    """One retrieval chunk with provenance relative to the full document text."""

    chunk_id: str
    publication_id: str
    chunk_text: str
    section: SectionLabel
    start_offset: int
    end_offset: int
    start_page: int | None
    end_page: int | None
    chunking_strategy_version: str
    section_heading: str | None = None

    @property
    def is_abstract(self) -> bool:
        return self.section is SectionLabel.ABSTRACT


@dataclass(frozen=True, slots=True)
class ChunkingResult:
    """Ordered chunks for one publication."""

    chunks: tuple[TextChunk, ...]
    publication_id: str
    chunking_strategy_version: str = CHUNKING_STRATEGY_VERSION
    source_key: str | None = None


@dataclass(frozen=True, slots=True)
class ChunkingPolicy:
    """Tunable size/overlap knobs for the MVP chunker."""

    target_tokens: int = TARGET_TOKENS
    min_tokens: int = MIN_TOKENS
    max_tokens: int = MAX_TOKENS
    overlap_ratio: float = OVERLAP_RATIO
    strategy_version: str = CHUNKING_STRATEGY_VERSION


DEFAULT_POLICY = ChunkingPolicy()


def estimate_tokens(text: str) -> int:
    """Estimate token count without a vendor tokenizer (whitespace words)."""
    stripped = text.strip()
    if not stripped:
        return 0
    return len(_WHITESPACE_RE.split(stripped))


def make_chunk_id(
    publication_id: str,
    *,
    start_offset: int,
    end_offset: int,
    section: SectionLabel | str,
    strategy_version: str = CHUNKING_STRATEGY_VERSION,
) -> str:
    """Return a stable chunk id from publication + span + strategy version."""
    section_value = section.value if isinstance(section, SectionLabel) else str(section)
    payload = f"{publication_id}|{strategy_version}|{section_value}|{start_offset}|{end_offset}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
    return f"chk_{digest}"


def chunk_sections(
    sections: SectionDetectionResult | Sequence[SectionSpan],
    *,
    publication_id: str,
    page_map: PageOffsetMap | None = None,
    policy: ChunkingPolicy = DEFAULT_POLICY,
    source_key: str | None = None,
) -> ChunkingResult:
    """Chunk section spans without merging across section boundaries."""
    if isinstance(sections, SectionDetectionResult):
        spans = sections.sections
        source_key = source_key or sections.source_key
    else:
        spans = tuple(sections)

    chunks: list[TextChunk] = []
    for span in spans:
        if not span.text.strip():
            continue
        chunks.extend(
            _chunk_span(
                span,
                publication_id=publication_id,
                page_map=page_map,
                policy=policy,
            )
        )
    return ChunkingResult(
        chunks=tuple(chunks),
        publication_id=publication_id,
        chunking_strategy_version=policy.strategy_version,
        source_key=source_key,
    )


def chunk_extraction(
    extraction: ExtractionResult,
    *,
    publication_id: str,
    policy: ChunkingPolicy = DEFAULT_POLICY,
) -> ChunkingResult:
    """Detect sections then chunk an extraction result."""
    detection = detect_sections(extraction)
    return chunk_sections(
        detection,
        publication_id=publication_id,
        page_map=extraction.page_map,
        policy=policy,
        source_key=extraction.source_key,
    )


def chunk_text(
    text: str,
    *,
    publication_id: str,
    page_starts: tuple[tuple[int, int], ...] | None = None,
    policy: ChunkingPolicy = DEFAULT_POLICY,
    source_key: str | None = None,
) -> ChunkingResult:
    """Detect sections from plain text then chunk."""
    from spacebio_evidence_engine.ingestion.sections import detect_sections_from_text

    detection = detect_sections_from_text(
        text,
        page_starts=page_starts,
        source_key=source_key,
    )
    page_map = (
        PageOffsetMap(page_starts=page_starts, text_length=len(text))
        if page_starts is not None
        else None
    )
    return chunk_sections(
        detection,
        publication_id=publication_id,
        page_map=page_map,
        policy=policy,
        source_key=source_key,
    )


def _chunk_span(
    span: SectionSpan,
    *,
    publication_id: str,
    page_map: PageOffsetMap | None,
    policy: ChunkingPolicy,
) -> list[TextChunk]:
    text = span.text
    token_count = estimate_tokens(text)
    if token_count <= policy.max_tokens:
        return [
            _build_chunk(
                publication_id=publication_id,
                chunk_text=text,
                section=span.label,
                start_offset=span.start_offset,
                end_offset=span.end_offset,
                page_map=page_map,
                fallback_start_page=span.start_page,
                fallback_end_page=span.end_page,
                policy=policy,
                section_heading=span.heading_text,
            )
        ]

    # Prefer sentence boundaries; fall back to whitespace windows.
    windows = _split_with_overlap(text, policy)
    chunks: list[TextChunk] = []
    for local_start, local_end, piece in windows:
        abs_start = span.start_offset + local_start
        abs_end = span.start_offset + local_end
        chunks.append(
            _build_chunk(
                publication_id=publication_id,
                chunk_text=piece,
                section=span.label,
                start_offset=abs_start,
                end_offset=abs_end,
                page_map=page_map,
                fallback_start_page=span.start_page,
                fallback_end_page=span.end_page,
                policy=policy,
                section_heading=span.heading_text,
            )
        )
    return chunks


def _build_chunk(
    *,
    publication_id: str,
    chunk_text: str,
    section: SectionLabel,
    start_offset: int,
    end_offset: int,
    page_map: PageOffsetMap | None,
    fallback_start_page: int | None,
    fallback_end_page: int | None,
    policy: ChunkingPolicy,
    section_heading: str | None,
) -> TextChunk:
    start_page = (
        page_map.page_number_for_offset(start_offset)
        if page_map is not None
        else fallback_start_page
    )
    end_page = (
        page_map.page_number_for_offset(max(start_offset, end_offset - 1))
        if page_map is not None
        else fallback_end_page
    )
    return TextChunk(
        chunk_id=make_chunk_id(
            publication_id,
            start_offset=start_offset,
            end_offset=end_offset,
            section=section,
            strategy_version=policy.strategy_version,
        ),
        publication_id=publication_id,
        chunk_text=chunk_text,
        section=section,
        start_offset=start_offset,
        end_offset=end_offset,
        start_page=start_page,
        end_page=end_page,
        chunking_strategy_version=policy.strategy_version,
        section_heading=section_heading,
    )


def _split_with_overlap(
    text: str,
    policy: ChunkingPolicy,
) -> list[tuple[int, int, str]]:
    """Return (local_start, local_end, substring) windows with overlap."""
    units = _sentence_units(text)
    if not units:
        return [(0, len(text), text)] if text else []

    target = max(policy.min_tokens, min(policy.target_tokens, policy.max_tokens))
    overlap_tokens = max(1, int(target * policy.overlap_ratio))
    windows: list[tuple[int, int, str]] = []

    index = 0
    while index < len(units):
        token_sum = 0
        end = index
        while end < len(units) and token_sum < target:
            token_sum += units[end][2]
            end += 1
            if token_sum >= policy.max_tokens:
                break

        # Always advance at least one unit to avoid infinite loops.
        if end == index:
            end = index + 1

        local_start = units[index][0]
        local_end = units[end - 1][1]
        windows.append((local_start, local_end, text[local_start:local_end]))

        if end >= len(units):
            break

        # Step back by ~overlap_tokens for the next window start.
        back_tokens = 0
        next_index = end - 1
        while next_index > index and back_tokens < overlap_tokens:
            back_tokens += units[next_index][2]
            next_index -= 1
        index = max(index + 1, next_index + 1)

    return windows


def _sentence_units(text: str) -> list[tuple[int, int, int]]:
    """Split into (start, end, token_estimate) units preferring sentence ends."""
    units: list[tuple[int, int, int]] = []
    pattern = re.compile(r"[^.!?]*[.!?]+(?:\s+|$)|[^.!?]+$", re.MULTILINE)
    for match in pattern.finditer(text):
        start, end = match.start(), match.end()
        piece = text[start:end]
        if not piece.strip():
            continue
        units.append((start, end, estimate_tokens(piece)))

    if units:
        return units

    # Whitespace fallback when no sentence punctuation exists.
    for match in re.finditer(r"\S+(?:\s+|$)", text):
        start, end = match.start(), match.end()
        units.append((start, end, estimate_tokens(text[start:end])))
    return units

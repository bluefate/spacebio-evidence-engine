"""Assemble model context from retrieved chunks (issue #52).

Separates instructions from evidence, preserves chunk IDs and provenance on
every included block, and enforces a token budget without silently dropping
citation identifiers (omitted IDs are always recorded).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from spacebio_evidence_engine.ingestion.chunking import estimate_tokens
from spacebio_evidence_engine.retrieval.semantic import SemanticSearchHit
from spacebio_evidence_engine.schemas import PassageCitation

DEFAULT_EVIDENCE_TOKEN_BUDGET = 2400
DEFAULT_INSTRUCTIONS = (
    "Use only the evidence blocks below. Cite claims with the citation IDs "
    "(for example [C1]). Do not invent findings. If the evidence is "
    "insufficient, say so. Separate source evidence from interpretation."
)


@dataclass(frozen=True)
class AssembledEvidenceBlock:
    """One evidence block with stable citation id and full provenance."""

    citation_id: str
    chunk_id: str
    publication_id: str
    title: str
    section: str
    source_url: str
    excerpt: str
    score: float
    page_start: int | None
    page_end: int | None
    section_heading: str | None
    estimated_tokens: int


@dataclass(frozen=True)
class ContextAssemblyResult:
    """Assembled prompt sections plus explicit include/omit accounting."""

    instructions: str
    evidence_blocks: tuple[AssembledEvidenceBlock, ...]
    evidence_text: str
    prompt_text: str
    citations: tuple[PassageCitation, ...]
    included_chunk_ids: tuple[str, ...]
    omitted_chunk_ids: tuple[str, ...]
    estimated_tokens: int
    token_budget: int


def assemble_context(
    hits: Sequence[SemanticSearchHit],
    *,
    token_budget: int = DEFAULT_EVIDENCE_TOKEN_BUDGET,
    instructions: str = DEFAULT_INSTRUCTIONS,
) -> ContextAssemblyResult:
    """Assemble instruction + evidence context from ranked retrieval hits.

    Hits are considered in rank order. When the remaining budget cannot fit the
    next block (including its required provenance header and ``chunk_id``), that
    hit and all later hits are recorded in ``omitted_chunk_ids`` — never dropped
    silently. Included blocks always retain ``chunk_id`` and provenance fields.
    """

    if token_budget < 1:
        raise ValueError("token_budget must be at least 1")
    if not instructions.strip():
        raise ValueError("instructions must be a non-empty string")

    blocks: list[AssembledEvidenceBlock] = []
    omitted: list[str] = []
    used_tokens = 0
    skipping = False

    for index, hit in enumerate(hits, start=1):
        if not hit.chunk_id.strip():
            raise ValueError("retrieved hit is missing chunk_id")
        if skipping:
            omitted.append(hit.chunk_id)
            continue

        citation_id = f"C{index}"
        block_text = _format_evidence_block(citation_id, hit, excerpt=hit.chunk_text)
        block_tokens = estimate_tokens(block_text)
        if used_tokens + block_tokens > token_budget:
            # Try a shorter excerpt while keeping the provenance header intact.
            truncated = _truncate_excerpt_to_budget(
                citation_id,
                hit,
                remaining_budget=token_budget - used_tokens,
            )
            if truncated is None:
                omitted.append(hit.chunk_id)
                skipping = True
                continue
            block_text, excerpt, block_tokens = truncated
        else:
            excerpt = hit.chunk_text

        blocks.append(
            AssembledEvidenceBlock(
                citation_id=citation_id,
                chunk_id=hit.chunk_id,
                publication_id=hit.publication_id,
                title=hit.title,
                section=hit.section,
                source_url=hit.source_url,
                excerpt=excerpt,
                score=hit.score,
                page_start=hit.page_start,
                page_end=hit.page_end,
                section_heading=hit.section_heading,
                estimated_tokens=block_tokens,
            )
        )
        used_tokens += block_tokens

    evidence_text = "\n\n".join(
        _format_evidence_block(block.citation_id, block, excerpt=block.excerpt) for block in blocks
    )
    prompt_text = (
        "### Instructions\n"
        f"{instructions.strip()}\n\n"
        "### Evidence\n"
        f"{evidence_text if evidence_text else '(no evidence blocks within budget)'}"
    )
    citations = tuple(
        PassageCitation(
            citation_id=block.citation_id,
            chunk_id=block.chunk_id,
            publication_id=block.publication_id,
            title=block.title,
            section=block.section,
            page=block.page_start,
            source_url=block.source_url,
            excerpt=_excerpt_for_citation(block.excerpt),
        )
        for block in blocks
    )
    return ContextAssemblyResult(
        instructions=instructions.strip(),
        evidence_blocks=tuple(blocks),
        evidence_text=evidence_text,
        prompt_text=prompt_text,
        citations=citations,
        included_chunk_ids=tuple(block.chunk_id for block in blocks),
        omitted_chunk_ids=tuple(omitted),
        estimated_tokens=estimate_tokens(prompt_text),
        token_budget=token_budget,
    )


def _format_evidence_block(
    citation_id: str,
    hit: SemanticSearchHit | AssembledEvidenceBlock,
    *,
    excerpt: str,
) -> str:
    page = _format_pages(hit.page_start, hit.page_end)
    heading = hit.section_heading or ""
    return (
        f"[{citation_id}] chunk_id={hit.chunk_id} "
        f"publication_id={hit.publication_id} title={hit.title!r} "
        f"section={hit.section} pages={page} source_url={hit.source_url}"
        + (f" heading={heading!r}" if heading else "")
        + f"\n{excerpt.strip()}"
    )


def _truncate_excerpt_to_budget(
    citation_id: str,
    hit: SemanticSearchHit,
    *,
    remaining_budget: int,
) -> tuple[str, str, int] | None:
    """Return (block_text, excerpt, tokens) if provenance+excerpt fits, else None."""

    if remaining_budget < 1:
        return None
    words = hit.chunk_text.split()
    if not words:
        empty_block = _format_evidence_block(citation_id, hit, excerpt="")
        tokens = estimate_tokens(empty_block)
        if tokens > remaining_budget:
            return None
        return empty_block, "", tokens

    low = 0
    high = len(words)
    best: tuple[str, str, int] | None = None
    while low <= high:
        mid = (low + high) // 2
        excerpt = " ".join(words[:mid])
        block_text = _format_evidence_block(citation_id, hit, excerpt=excerpt)
        tokens = estimate_tokens(block_text)
        if tokens <= remaining_budget:
            best = (block_text, excerpt, tokens)
            low = mid + 1
        else:
            high = mid - 1

    # Provenance header alone must still fit; otherwise omit explicitly.
    if best is None:
        header_only = _format_evidence_block(citation_id, hit, excerpt="")
        if estimate_tokens(header_only) <= remaining_budget:
            return header_only, "", estimate_tokens(header_only)
        return None
    return best


def _format_pages(page_start: int | None, page_end: int | None) -> str:
    if page_start is None and page_end is None:
        return "unknown"
    if page_start is not None and page_end is not None and page_start != page_end:
        return f"{page_start}-{page_end}"
    value = page_start if page_start is not None else page_end
    return str(value)


def _excerpt_for_citation(excerpt: str, *, max_chars: int = 280) -> str:
    stripped = excerpt.strip()
    if len(stripped) <= max_chars:
        return stripped
    return stripped[: max_chars - 1].rstrip() + "…"

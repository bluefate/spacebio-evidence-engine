"""Passage-level citation emission and validation (issue #54)."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from spacebio_evidence_engine.rag.context import ContextAssemblyResult
from spacebio_evidence_engine.schemas import AnswerWarning, PassageCitation

_CITATION_MARKER_RE = re.compile(r"\[([A-Za-z][A-Za-z0-9_-]*)\]")


@dataclass(frozen=True, slots=True)
class CitationEmissionResult:
    """Citations selected from retrieved context plus validation signals."""

    citations: tuple[PassageCitation, ...]
    emitted_citation_ids: tuple[str, ...]
    rejected_citation_ids: tuple[str, ...]
    unknown_citation_ids: tuple[str, ...]
    unretrieved_chunk_ids: tuple[str, ...]
    warnings: tuple[AnswerWarning, ...]

    @property
    def valid(self) -> bool:
        """True when no citation references were rejected."""
        return not self.rejected_citation_ids and not self.unretrieved_chunk_ids


def extract_citation_markers(text: str) -> tuple[str, ...]:
    """Return unique citation markers from answer text in first-seen order."""
    seen: set[str] = set()
    markers: list[str] = []
    for match in _CITATION_MARKER_RE.finditer(text):
        citation_id = match.group(1)
        if citation_id in seen:
            continue
        seen.add(citation_id)
        markers.append(citation_id)
    return tuple(markers)


def emit_passage_citations(
    context: ContextAssemblyResult,
    *,
    requested_citation_ids: Sequence[str] | None = None,
) -> CitationEmissionResult:
    """Emit passage citations that are backed by included retrieved chunks only.

    ``requested_citation_ids`` should come from citation markers in generated
    text or another downstream selector. Unknown ids are not emitted; instead
    they appear in ``rejected_citation_ids`` and warnings so callers can fail the
    response rather than silently returning unsupported citations.
    """
    allowed_chunk_ids = set(context.included_chunk_ids)
    citations_by_id: dict[str, PassageCitation] = {}
    unretrieved_citations_by_id: dict[str, PassageCitation] = {}
    unretrieved_chunk_ids: list[str] = []
    warnings: list[AnswerWarning] = []

    for citation in context.citations:
        if citation.chunk_id not in allowed_chunk_ids:
            unretrieved_citations_by_id[citation.citation_id] = citation
            unretrieved_chunk_ids.append(citation.chunk_id)
            continue
        citations_by_id[citation.citation_id] = citation

    if requested_citation_ids is None:
        requested = tuple(citation.citation_id for citation in context.citations)
    else:
        requested = _unique_nonempty(requested_citation_ids)

    emitted: list[PassageCitation] = []
    emitted_ids: list[str] = []
    unknown_ids: list[str] = []
    unretrieved_requested_ids: list[str] = []

    for citation_id in requested:
        citation = citations_by_id.get(citation_id)
        if citation is not None:
            emitted.append(citation)
            emitted_ids.append(citation_id)
        elif citation_id in unretrieved_citations_by_id:
            unretrieved_requested_ids.append(citation_id)
        else:
            unknown_ids.append(citation_id)

    if unknown_ids:
        warnings.append(
            AnswerWarning(
                code="unknown_citation_ids_rejected",
                message=(
                    "Citation ids were not present in retrieved context and were not emitted: "
                    + ", ".join(unknown_ids)
                ),
            )
        )
    if unretrieved_chunk_ids:
        warnings.append(
            AnswerWarning(
                code="unretrieved_citation_chunks_rejected",
                message=(
                    "Citations referenced chunks outside the included retrieved context: "
                    + ", ".join(_unique_nonempty(unretrieved_chunk_ids))
                ),
            )
        )

    return CitationEmissionResult(
        citations=tuple(emitted),
        emitted_citation_ids=tuple(emitted_ids),
        rejected_citation_ids=tuple(unknown_ids + unretrieved_requested_ids),
        unknown_citation_ids=tuple(unknown_ids),
        unretrieved_chunk_ids=tuple(_unique_nonempty(unretrieved_chunk_ids)),
        warnings=tuple(warnings),
    )


def emit_citations_for_answer_text(
    answer_text: str,
    context: ContextAssemblyResult,
) -> CitationEmissionResult:
    """Emit citations referenced by ``[C1]``-style markers in answer text."""
    return emit_passage_citations(
        context,
        requested_citation_ids=extract_citation_markers(answer_text),
    )


def _unique_nonempty(values: Sequence[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique.append(normalized)
    return tuple(unique)

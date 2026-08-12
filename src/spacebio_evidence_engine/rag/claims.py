"""Claim-to-source mapping validation (issue #56)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from spacebio_evidence_engine.rag.citations import emit_passage_citations
from spacebio_evidence_engine.rag.context import ContextAssemblyResult
from spacebio_evidence_engine.schemas import AnswerClaim, AnswerWarning, PassageCitation


@dataclass(frozen=True, slots=True)
class ClaimSourceMapping:
    """One answer claim with resolved passage citations and chunk ids."""

    claim: AnswerClaim
    citations: tuple[PassageCitation, ...]
    chunk_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ClaimSourceMappingResult:
    """Validated claim-source mappings plus rejection signals."""

    claims: tuple[AnswerClaim, ...]
    mappings: tuple[ClaimSourceMapping, ...]
    citations: tuple[PassageCitation, ...]
    rejected_claim_ids: tuple[str, ...]
    rejected_citation_ids: tuple[str, ...]
    warnings: tuple[AnswerWarning, ...]

    @property
    def valid(self) -> bool:
        """True when every claim has at least one retrieved supporting citation."""
        return not self.rejected_claim_ids and not self.rejected_citation_ids


def validate_claim_source_mapping(
    claims: Sequence[AnswerClaim],
    context: ContextAssemblyResult,
) -> ClaimSourceMappingResult:
    """Validate answer claims against citations from included retrieved context.

    Claims are accepted only when every referenced citation id resolves to a
    passage citation backed by ``context.included_chunk_ids``. Claims with no
    sources, unknown citations, or citations tied to unretrieved chunks are
    excluded from ``claims`` / ``mappings`` and reported through warnings.
    """
    citations_by_id = {citation.citation_id: citation for citation in context.citations}
    accepted_claims: list[AnswerClaim] = []
    mappings: list[ClaimSourceMapping] = []
    emitted_citations_by_id: dict[str, PassageCitation] = {}
    rejected_claim_ids: list[str] = []
    rejected_citation_ids: list[str] = []
    warnings: list[AnswerWarning] = []

    for claim in claims:
        citation_ids = _unique_nonempty(claim.citation_ids)
        if not citation_ids:
            rejected_claim_ids.append(claim.claim_id)
            warnings.append(
                AnswerWarning(
                    code="claim_without_sources_rejected",
                    message=f"Claim {claim.claim_id} has no supporting citation ids.",
                )
            )
            continue

        citation_result = emit_passage_citations(context, requested_citation_ids=citation_ids)
        missing_ids = tuple(
            citation_id
            for citation_id in citation_ids
            if citation_id not in citation_result.emitted_citation_ids
        )
        if missing_ids:
            rejected_claim_ids.append(claim.claim_id)
            rejected_citation_ids.extend(missing_ids)
            warnings.append(
                AnswerWarning(
                    code="claim_sources_rejected",
                    message=(
                        f"Claim {claim.claim_id} referenced unsupported citation ids: "
                        + ", ".join(missing_ids)
                    ),
                )
            )
            warnings.extend(citation_result.warnings)
            continue

        normalized_claim = claim.model_copy(update={"citation_ids": list(citation_ids)})
        accepted_claims.append(normalized_claim)
        for citation in citation_result.citations:
            emitted_citations_by_id[citation.citation_id] = citation
        mappings.append(
            ClaimSourceMapping(
                claim=normalized_claim,
                citations=citation_result.citations,
                chunk_ids=tuple(
                    citations_by_id[citation_id].chunk_id for citation_id in citation_ids
                ),
            )
        )

    return ClaimSourceMappingResult(
        claims=tuple(accepted_claims),
        mappings=tuple(mappings),
        citations=tuple(emitted_citations_by_id.values()),
        rejected_claim_ids=tuple(_unique_nonempty(rejected_claim_ids)),
        rejected_citation_ids=tuple(_unique_nonempty(rejected_citation_ids)),
        warnings=tuple(_unique_warnings(warnings)),
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


def _unique_warnings(warnings: Sequence[AnswerWarning]) -> tuple[AnswerWarning, ...]:
    seen: set[tuple[str, str]] = set()
    unique: list[AnswerWarning] = []
    for warning in warnings:
        key = (warning.code, warning.message)
        if key in seen:
            continue
        seen.add(key)
        unique.append(warning)
    return tuple(unique)

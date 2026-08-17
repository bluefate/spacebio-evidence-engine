"""Experimental entity/relationship extraction from passages (issue #74).

Rule-based gazetteer only. Outputs are always ``unverified`` and must not
enter grounded answers or a production graph store.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from spacebio_evidence_engine.graph.gazetteer import GAZETTEER

EXTRACTOR_VERSION = "gazetteer-v1"
PRODUCTION_WARNING = "EXPERIMENTAL_NOT_FOR_PRODUCTION"
VERIFICATION_STATUS = "unverified"
EXTRACTION_METHOD = "gazetteer"


@dataclass(frozen=True)
class PassageInput:
    """One retrieved or fixture passage."""

    chunk_id: str
    publication_id: str
    chunk_text: str
    source_url: str = ""
    section: str | None = None
    page: int | None = None


@dataclass(frozen=True)
class ExtractedEntity:
    entity_id: str
    entity_type: str
    preferred_label: str
    model_class: str | None
    publication_id: str
    chunk_id: str
    source_span: str
    source_url: str
    extraction_method: str
    verification_status: str
    extractor_version: str


@dataclass(frozen=True)
class ExtractedRelationship:
    relationship_id: str
    relationship_type: str
    from_entity_id: str
    to_entity_id: str
    publication_id: str
    chunk_id: str
    source_span: str
    source_url: str
    epistemic_qualifier: str
    extraction_method: str
    verification_status: str
    extractor_version: str


@dataclass(frozen=True)
class ExtractionResult:
    experimental: bool
    warning: str
    extractor_version: str
    entities: tuple[ExtractedEntity, ...]
    relationships: tuple[ExtractedRelationship, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "experimental": self.experimental,
            "warning": self.warning,
            "extractor_version": self.extractor_version,
            "entities": [asdict(item) for item in self.entities],
            "relationships": [asdict(item) for item in self.relationships],
        }


def extract_from_passages(passages: Sequence[PassageInput | dict[str, Any]]) -> ExtractionResult:
    """Extract unverified graph mentions and findings from passage text."""

    entities: list[ExtractedEntity] = []
    relationships: list[ExtractedRelationship] = []
    for raw in passages:
        passage = _as_passage(raw)
        if not passage.chunk_id.strip():
            raise ValueError("every passage must include chunk_id")
        if not passage.publication_id.strip():
            raise ValueError("every passage must include publication_id")
        mentioned = _match_gazetteer(passage)
        entities.extend(mentioned)
        chunk_node_id = _stable_id("Chunk", passage.chunk_id, passage.chunk_id)
        for entity in mentioned:
            relationships.append(
                _edge(
                    "mentions",
                    chunk_node_id,
                    entity.entity_id,
                    passage,
                    entity.source_span,
                )
            )
        finding = _maybe_finding(passage, mentioned)
        if finding is not None:
            entities.append(finding)
            relationships.append(
                _edge(
                    "supported_by",
                    finding.entity_id,
                    chunk_node_id,
                    passage,
                    passage.chunk_text[:180],
                )
            )
            for entity in mentioned:
                rel_type = _binding_type(entity.entity_type)
                if rel_type is None:
                    continue
                relationships.append(
                    _edge(
                        rel_type,
                        finding.entity_id,
                        entity.entity_id,
                        passage,
                        entity.source_span,
                    )
                )

    return ExtractionResult(
        experimental=True,
        warning=PRODUCTION_WARNING,
        extractor_version=EXTRACTOR_VERSION,
        entities=tuple(entities),
        relationships=tuple(relationships),
    )


def load_passages(path: Path) -> list[PassageInput]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("fixture must be a JSON list of passages")
    return [_as_passage(item) for item in payload]


def _as_passage(raw: PassageInput | dict[str, Any]) -> PassageInput:
    if isinstance(raw, PassageInput):
        return raw
    return PassageInput(
        chunk_id=str(raw["chunk_id"]),
        publication_id=str(raw["publication_id"]),
        chunk_text=str(raw["chunk_text"]),
        source_url=str(raw.get("source_url") or ""),
        section=raw.get("section"),
        page=raw.get("page"),
    )


def _match_gazetteer(passage: PassageInput) -> list[ExtractedEntity]:
    text = passage.chunk_text
    lower = text.lower()
    found: list[ExtractedEntity] = []
    occupied: list[tuple[int, int]] = []
    for entity_type, label, model_class, phrases in GAZETTEER:
        for phrase in phrases:
            start = lower.find(phrase)
            if start < 0:
                continue
            end = start + len(phrase)
            if any(start < other_end and end > other_start for other_start, other_end in occupied):
                continue
            if not _bounded(lower, start, end):
                continue
            occupied.append((start, end))
            span = text[start:end]
            found.append(
                ExtractedEntity(
                    entity_id=_stable_id(entity_type, label, passage.chunk_id),
                    entity_type=entity_type,
                    preferred_label=label,
                    model_class=model_class or None,
                    publication_id=passage.publication_id,
                    chunk_id=passage.chunk_id,
                    source_span=span,
                    source_url=passage.source_url,
                    extraction_method=EXTRACTION_METHOD,
                    verification_status=VERIFICATION_STATUS,
                    extractor_version=EXTRACTOR_VERSION,
                )
            )
            break
    return found


def _bounded(lower: str, start: int, end: int) -> bool:
    if start > 0 and lower[start - 1].isalnum():
        return False
    if end < len(lower) and lower[end].isalnum():
        return False
    return True


def _maybe_finding(
    passage: PassageInput,
    mentioned: Sequence[ExtractedEntity],
) -> ExtractedEntity | None:
    types = {item.entity_type for item in mentioned}
    if "Organism" not in types or "Outcome" not in types:
        return None
    labels = ", ".join(item.preferred_label for item in mentioned)
    return ExtractedEntity(
        entity_id=_stable_id("Finding", labels, passage.chunk_id),
        entity_type="Finding",
        preferred_label=labels,
        model_class=None,
        publication_id=passage.publication_id,
        chunk_id=passage.chunk_id,
        source_span=passage.chunk_text[:180],
        source_url=passage.source_url,
        extraction_method=EXTRACTION_METHOD,
        verification_status=VERIFICATION_STATUS,
        extractor_version=EXTRACTOR_VERSION,
    )


def _binding_type(entity_type: str) -> str | None:
    mapping = {
        "Organism": "studied_in",
        "Exposure": "under_condition",
        "AnatomicalStructure": "measured_in",
        "CellType": "measured_in",
        "Assay": "used_assay",
        "Intervention": "treated_with",
        "Outcome": None,
    }
    return mapping.get(entity_type)


def _edge(
    relationship_type: str,
    from_id: str,
    to_id: str,
    passage: PassageInput,
    span: str,
) -> ExtractedRelationship:
    return ExtractedRelationship(
        relationship_id=_stable_id(relationship_type, f"{from_id}->{to_id}", passage.chunk_id),
        relationship_type=relationship_type,
        from_entity_id=from_id,
        to_entity_id=to_id,
        publication_id=passage.publication_id,
        chunk_id=passage.chunk_id,
        source_span=span,
        source_url=passage.source_url,
        epistemic_qualifier="associates",
        extraction_method=EXTRACTION_METHOD,
        verification_status=VERIFICATION_STATUS,
        extractor_version=EXTRACTOR_VERSION,
    )


def _stable_id(kind: str, key: str, chunk_id: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", f"{kind}-{key}-{chunk_id}".lower()).strip("-")
    return slug[:120]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Experimental graph extraction (not for production answers)."
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("tests/fixtures/graph_extraction_passages.json"),
        help="JSON list of passages with chunk_id, publication_id, chunk_text",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    result = extract_from_passages(load_passages(args.fixture))
    print(json.dumps(result.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

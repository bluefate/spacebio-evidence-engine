"""Offline precision/recall for experimental graph extraction (issue #75).

Compares gazetteer mentions and Finding presence to a small labeled fixture.
This does not judge scientific truth of the live corpus and is not a /ask gate.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from spacebio_evidence_engine.graph.extract import extract_from_passages

GRAPH_EXTRACTION_EVAL_VERSION = "1.0.0"
MENTION_TYPES = frozenset(
    {
        "Organism",
        "AnatomicalStructure",
        "CellType",
        "Exposure",
        "Intervention",
        "Assay",
        "Outcome",
        "Limitation",
    }
)


@dataclass(frozen=True, slots=True)
class GoldMention:
    chunk_id: str
    entity_type: str
    preferred_label: str


@dataclass(frozen=True, slots=True)
class ExtractionError:
    category: str
    chunk_id: str
    entity_type: str
    preferred_label: str
    detail: str


@dataclass(frozen=True, slots=True)
class GraphExtractionMetrics:
    schema_version: str
    mention_precision: float
    mention_recall: float
    mention_f1: float
    finding_precision: float
    finding_recall: float
    true_positive_mentions: int
    false_positive_mentions: int
    false_negative_mentions: int
    true_positive_findings: int
    false_positive_findings: int
    false_negative_findings: int
    error_category_counts: dict[str, int]


@dataclass(frozen=True, slots=True)
class GraphExtractionEvalResult:
    metrics: GraphExtractionMetrics
    errors: tuple[ExtractionError, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "metrics": asdict(self.metrics),
            "errors": [asdict(item) for item in self.errors],
        }


def load_labeled_sample(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or "passages" not in payload:
        raise ValueError("labeled sample must be an object with a passages list")
    return payload


def evaluate_labeled_sample(payload: dict[str, Any]) -> GraphExtractionEvalResult:
    predicted = extract_from_passages(payload["passages"])
    gold_mentions = {
        (item["chunk_id"], item["entity_type"], item["preferred_label"])
        for item in payload.get("gold_mentions", [])
    }
    pred_mentions = {
        (entity.chunk_id, entity.entity_type, entity.preferred_label)
        for entity in predicted.entities
        if entity.entity_type in MENTION_TYPES
    }
    gold_findings = {
        str(item["chunk_id"])
        for item in payload.get("passages", [])
        if item.get("expect_finding") is True
    }
    pred_findings = {
        entity.chunk_id for entity in predicted.entities if entity.entity_type == "Finding"
    }

    tp_m = gold_mentions & pred_mentions
    fp_m = pred_mentions - gold_mentions
    fn_m = gold_mentions - pred_mentions
    tp_f = gold_findings & pred_findings
    fp_f = pred_findings - gold_findings
    fn_f = gold_findings - pred_findings

    errors: list[ExtractionError] = []
    for chunk_id, entity_type, label in sorted(fp_m):
        errors.append(
            ExtractionError(
                "false_positive_mention",
                chunk_id,
                entity_type,
                label,
                "Extractor emitted a mention not in the labeled sample.",
            )
        )
    for chunk_id, entity_type, label in sorted(fn_m):
        errors.append(
            ExtractionError(
                "false_negative_mention",
                chunk_id,
                entity_type,
                label,
                "Labeled mention was not extracted.",
            )
        )
    for chunk_id in sorted(fp_f):
        errors.append(
            ExtractionError(
                "false_positive_finding",
                chunk_id,
                "Finding",
                "",
                "Extractor emitted a Finding the labeler did not expect.",
            )
        )
    for chunk_id in sorted(fn_f):
        errors.append(
            ExtractionError(
                "false_negative_finding",
                chunk_id,
                "Finding",
                "",
                "Labeled Finding was not extracted.",
            )
        )

    metrics = GraphExtractionMetrics(
        schema_version=GRAPH_EXTRACTION_EVAL_VERSION,
        mention_precision=_ratio(len(tp_m), len(tp_m) + len(fp_m)),
        mention_recall=_ratio(len(tp_m), len(tp_m) + len(fn_m)),
        mention_f1=_f1(
            _ratio(len(tp_m), len(tp_m) + len(fp_m)),
            _ratio(len(tp_m), len(tp_m) + len(fn_m)),
        ),
        finding_precision=_ratio(len(tp_f), len(tp_f) + len(fp_f)),
        finding_recall=_ratio(len(tp_f), len(tp_f) + len(fn_f)),
        true_positive_mentions=len(tp_m),
        false_positive_mentions=len(fp_m),
        false_negative_mentions=len(fn_m),
        true_positive_findings=len(tp_f),
        false_positive_findings=len(fp_f),
        false_negative_findings=len(fn_f),
        error_category_counts=dict(Counter(error.category for error in errors)),
    )
    return GraphExtractionEvalResult(metrics=metrics, errors=tuple(errors))


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _f1(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)

#!/usr/bin/env python3
"""Evaluate experimental graph extraction against a labeled fixture (issue #75)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from spacebio_evidence_engine.evaluation.graph_extraction import (  # noqa: E402
    evaluate_labeled_sample,
    load_labeled_sample,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "fixture",
        type=Path,
        nargs="?",
        default=ROOT / "evals/fixtures/graph_extraction_labels.json",
        help="Labeled sample JSON (passages + gold_mentions)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    args = parser.parse_args()

    result = evaluate_labeled_sample(load_labeled_sample(args.fixture))
    metrics = result.metrics
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(
            "graph_extraction_eval "
            f"mention_p={metrics.mention_precision:.3f} "
            f"mention_r={metrics.mention_recall:.3f} "
            f"mention_f1={metrics.mention_f1:.3f} "
            f"finding_p={metrics.finding_precision:.3f} "
            f"finding_r={metrics.finding_recall:.3f} "
            f"errors={len(result.errors)}"
        )
        for error in result.errors:
            print(
                f"{error.category}: {error.chunk_id} "
                f"{error.entity_type} {error.preferred_label}".rstrip()
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

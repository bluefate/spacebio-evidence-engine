#!/usr/bin/env python3
"""Run citation correctness evaluation for grounded-answer fixture JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from spacebio_evidence_engine.evaluation.citation_correctness import (  # noqa: E402
    evaluate_cases,
    load_cases,
    result_to_dict,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path, help="JSON file with a 'cases' list")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of a short text report.",
    )
    args = parser.parse_args()

    metrics, *results = evaluate_cases(load_cases(args.fixture))
    if args.json:
        print(
            json.dumps(
                {
                    "metrics": result_to_dict(metrics),
                    "results": [result_to_dict(result) for result in results],
                },
                indent=2,
            )
        )
    else:
        print(
            "citation_correctness_eval "
            f"passed={metrics.passed} "
            f"failed={metrics.failed_count} "
            f"citation_id_precision={metrics.citation_id_precision:.3f} "
            f"claim_citation_precision={metrics.claim_citation_precision:.3f} "
            f"claim_citation_recall={metrics.claim_citation_recall:.3f}"
        )
        for result in results:
            for finding in result.findings:
                print(f"{finding.code}: {result.case_id} :: {finding.text}")
    return 0 if metrics.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

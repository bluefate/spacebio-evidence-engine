#!/usr/bin/env python3
"""Run hallucination checks for grounded-answer fixture JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from spacebio_evidence_engine.evaluation.hallucination import (  # noqa: E402
    evaluate_answers,
    load_answers,
    result_to_dict,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path, help="JSON file with an 'answers' list")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of a short text report.",
    )
    args = parser.parse_args()

    metrics, *results = evaluate_answers(load_answers(args.fixture))
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
            "hallucination_eval "
            f"passed={metrics.passed} "
            f"failed={metrics.failed_count} "
            f"unsupported_claims={metrics.unsupported_claim_count} "
            f"cited_claim_rate={metrics.cited_claim_rate:.3f}"
        )
        for result in results:
            for finding in result.findings:
                print(f"{finding.code}: {result.question} :: {finding.text}")
    return 0 if metrics.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

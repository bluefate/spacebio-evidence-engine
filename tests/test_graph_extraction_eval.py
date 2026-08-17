from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from spacebio_evidence_engine.evaluation.graph_extraction import (
    evaluate_labeled_sample,
    load_labeled_sample,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "evals/fixtures/graph_extraction_labels.json"
SCRIPT = ROOT / "evals/graph_extraction_eval.py"


def test_labeled_sample_reports_precision_recall() -> None:
    result = evaluate_labeled_sample(load_labeled_sample(FIXTURE))
    metrics = result.metrics

    assert 0.0 <= metrics.mention_precision <= 1.0
    assert 0.0 <= metrics.mention_recall <= 1.0
    assert metrics.true_positive_mentions >= 1
    assert "false_negative_mention" in metrics.error_category_counts
    assert "false_positive_mention" in metrics.error_category_counts
    assert "false_negative_finding" in metrics.error_category_counts


def test_eval_script_smoke() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURE), "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    payload = completed.stdout
    assert "mention_precision" in payload
    assert "error_category_counts" in payload

"""Run offline semantic retrieval evaluation against reference questions."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from spacebio_evidence_engine.embeddings import LocalEmbeddingProvider
from spacebio_evidence_engine.evaluation import (
    evaluate_retrieval,
    load_reference_questions,
    write_retrieval_report,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REFERENCE_QUESTIONS = ROOT / "evals" / "fixtures" / "reference_questions.json"
DEFAULT_OUTPUT = ROOT / "evals" / "artifacts" / "retrieval_eval.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate semantic retrieval against approved reference questions."
    )
    parser.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL"),
        help="SQLAlchemy database URL for an already migrated and indexed corpus.",
    )
    parser.add_argument(
        "--reference-questions",
        default=str(DEFAULT_REFERENCE_QUESTIONS),
        help="Path to the approved reference question fixture.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Path for the JSON results artifact.",
    )
    parser.add_argument("--top-k", type=int, default=8, help="Number of chunks to retrieve.")
    args = parser.parse_args()

    if not args.database_url:
        parser.error("--database-url or DATABASE_URL is required")

    questions = load_reference_questions(args.reference_questions)
    try:
        provider = LocalEmbeddingProvider()
    except ImportError as exc:
        parser.error(str(exc))
    engine = create_engine(args.database_url)
    with Session(engine) as session:
        report = evaluate_retrieval(session, provider, questions, top_k=args.top_k)

    artifact_path = write_retrieval_report(
        report,
        args.output,
        reference_question_path=args.reference_questions,
    )
    metrics = report.metrics
    print(f"Wrote retrieval evaluation report: {artifact_path}")
    print(
        f"hit_rate={metrics.hit_rate:.3f} mrr={metrics.mean_reciprocal_rank:.3f} "
        f"hit_count={metrics.hit_count}/{metrics.answerable_question_count} "
        f"unanswerable_with_hits={metrics.unanswerable_with_hits_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

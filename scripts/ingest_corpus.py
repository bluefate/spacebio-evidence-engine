#!/usr/bin/env python3
"""Ingest local corpus PDFs into Postgres (issue #163).

Place files at ``data/pdfs/{publication_id}.pdf`` (gitignored). Then:

  set -a && source .env && set +a
  make ingest

This does not train a model. Optional embeddings use MiniLM (install
``pip install -e ".[embeddings]"``) or ``--skip-embeddings``.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from spacebio_evidence_engine.ingestion.ingest_job import ingest_local_corpus  # noqa: E402


def _load_dotenv(path: Path) -> None:
    """Load KEY=VALUE lines into os.environ when the key is unset."""

    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


def main() -> int:
    _load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser(description="Ingest local PDFs for the approved corpus.")
    parser.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL"),
        help="SQLAlchemy URL (or set DATABASE_URL).",
    )
    parser.add_argument(
        "--pdf-root",
        default=os.environ.get("PDF_STORAGE_LOCAL_ROOT", "data/pdfs"),
        help="Directory of {publication_id}.pdf files.",
    )
    parser.add_argument(
        "--publication-id",
        action="append",
        dest="publication_ids",
        help="Limit to one inventory id (repeatable).",
    )
    parser.add_argument(
        "--skip-embeddings",
        action="store_true",
        help="Persist chunks only (no vectors).",
    )
    parser.add_argument(
        "--include-quality-blocked",
        action="store_true",
        help="Also try rows marked pdf_quality_blocked in the inventory.",
    )
    args = parser.parse_args()
    if not args.database_url:
        parser.error("--database-url or DATABASE_URL is required (load .env first)")

    embedding_provider = None
    if not args.skip_embeddings:
        try:
            from spacebio_evidence_engine.embeddings import LocalEmbeddingProvider

            embedding_provider = LocalEmbeddingProvider()
        except ImportError as exc:
            print(
                "Local embeddings are not installed. "
                'Run: pip install -e ".[embeddings]" '
                "or pass --skip-embeddings to store chunks only.\n"
                f"{exc}",
                file=sys.stderr,
            )
            return 2

    pdf_root = Path(args.pdf_root)
    if not pdf_root.is_absolute():
        pdf_root = ROOT / pdf_root

    engine = create_engine(args.database_url)
    with Session(engine) as session:
        summary = ingest_local_corpus(
            session,
            pdf_root=pdf_root,
            publication_ids=args.publication_ids,
            embedding_provider=embedding_provider,
            include_quality_blocked=args.include_quality_blocked,
        )

    print(
        "ingest complete: "
        f"ingested={summary.ingested_count} "
        f"skipped={summary.skipped_count} "
        f"failed={summary.failed_count}"
    )
    for item in summary.results:
        extra = f" chunks={item.chunk_count} embeddings={item.embedded_count}"
        note = f" ({item.message})" if item.message else ""
        print(f"  {item.publication_id}: {item.outcome}{extra}{note}")
    return 0 if summary.failed_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

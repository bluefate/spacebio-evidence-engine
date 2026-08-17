#!/usr/bin/env python3
"""Download the 23 approved OA PDFs into ``data/pdfs`` (issue #171).

Usage:

    make fetch-pdfs

Or directly:

    python scripts/fetch_corpus_pdfs.py

Existing files are skipped unless ``--force`` is passed. PDFs are validated by
magic bytes; no downloaded content is executed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from spacebio_evidence_engine.corpus.fetch import (  # noqa: E402
    FetchResult,
    fetch_corpus_pdfs,
)
from spacebio_evidence_engine.corpus.inventory import (  # noqa: E402
    MANIFEST_PATH,
)


def _format_result(result: FetchResult, *, root: Path) -> str:
    path = result.path
    path_note = ""
    if path:
        rel = path.relative_to(root) if path.is_relative_to(root) else path
        path_note = f" -> {rel}"
    message = f" ({result.message})" if result.message else ""
    return f"  {result.publication_id}: {result.outcome}{path_note}{message}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download the approved OA PDFs from the corpus manifest."
    )
    parser.add_argument(
        "--output-root",
        default="data/pdfs",
        help="Directory to write {publication_id}.pdf files.",
    )
    parser.add_argument(
        "--manifest",
        default=str(MANIFEST_PATH),
        help="Path to the corpus manifest CSV.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing PDF files.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="HTTP request timeout in seconds.",
    )
    args = parser.parse_args()

    output_root = Path(args.output_root)
    if not output_root.is_absolute():
        output_root = ROOT / output_root

    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = ROOT / manifest_path

    results = fetch_corpus_pdfs(
        output_root,
        manifest_path=manifest_path,
        force=args.force,
        timeout=args.timeout,
    )

    for result in results:
        print(_format_result(result, root=output_root))

    failures = [r for r in results if r.outcome.startswith("failed")]
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

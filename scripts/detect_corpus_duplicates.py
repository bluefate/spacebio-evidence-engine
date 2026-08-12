#!/usr/bin/env python3
"""Report duplicate publication candidates in a corpus manifest CSV."""

from __future__ import annotations

import argparse
from pathlib import Path

from spacebio_evidence_engine.corpus.duplicates import detect_duplicate_publications_from_csv


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "manifest",
        nargs="?",
        default="data/inventory/august_mvp_corpus_manifest.csv",
        help="Path to corpus candidate manifest CSV.",
    )
    args = parser.parse_args()

    duplicate_sets = detect_duplicate_publications_from_csv(Path(args.manifest))
    if not duplicate_sets:
        print("No duplicate publication candidates detected.")
        return 0

    for duplicate_set in duplicate_sets:
        print(
            f"{duplicate_set.duplicate_set_id}: "
            f"canonical={duplicate_set.canonical_publication_id}; "
            f"members={','.join(duplicate_set.publication_ids)}; "
            f"reasons={','.join(duplicate_set.match_reasons)}"
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

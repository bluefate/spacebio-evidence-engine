#!/usr/bin/env python3
"""Show persisted ingestion status for a publication (issue #34)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from spacebio_evidence_engine.ingestion.status import (  # noqa: E402
    DEFAULT_STATUS_EVENT_LOG,
    describe_ingestion_status,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Show ingestion status for a publication ID.")
    parser.add_argument(
        "--publication-id",
        required=True,
        help="Publication ID to inspect.",
    )
    parser.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL"),
        help="SQLAlchemy database URL (or set DATABASE_URL).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the status snapshot as JSON.",
    )
    args = parser.parse_args()
    if not args.database_url:
        parser.error("--database-url or DATABASE_URL is required")

    engine = create_engine(args.database_url)
    with Session(engine) as session:
        try:
            snapshot = describe_ingestion_status(
                session,
                args.publication_id,
                event_log=DEFAULT_STATUS_EVENT_LOG,
            )
        except LookupError as exc:
            print(str(exc), file=sys.stderr)
            return 1

    if args.json:
        print(json.dumps(snapshot, indent=2, sort_keys=True))
    else:
        print(f"publication_id: {snapshot['publication_id']}")
        print(f"ingestion_status: {snapshot['ingestion_status']}")
        next_statuses = ", ".join(snapshot["allowed_next_statuses"])  # type: ignore[arg-type]
        print(f"allowed_next_statuses: {next_statuses or '(none)'}")
        transitions = snapshot["recent_transitions"]
        assert isinstance(transitions, list)
        if not transitions:
            print("recent_transitions: (none in process log)")
        else:
            print("recent_transitions:")
            for event in transitions:
                assert isinstance(event, dict)
                print(
                    f"  - {event['from_status']} -> {event['to_status']} "
                    f"reason={event['reason']!r} at={event['occurred_at']}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

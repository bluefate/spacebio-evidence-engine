"""Load a `.env` file into ``os.environ`` without printing values.

This is a small stdlib loader used by entrypoints (bootstrap, alembic, scripts)
that need environment values before the FastAPI settings layer starts.
"""

from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: Path) -> None:
    """Load KEY=VALUE pairs from ``path`` into ``os.environ`` if not already set.

    No values are printed. Lines that are blank, start with ``#``, or have no
    ``=`` are ignored. Quoted values have their outer matching quotes stripped.
    """
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

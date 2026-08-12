"""Tests for the local setup dry-run checklist (issue #6)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_local_setup import (  # noqa: E402
    REQUIRED_ENV_KEYS,
    check_env_example,
    check_make_targets,
    main,
    run_checks,
)


def test_env_example_documents_required_keys_without_secrets() -> None:
    results = {item.name: item for item in check_env_example()}
    for key in REQUIRED_ENV_KEYS:
        assert results[f".env.example has {key}"].ok
    assert results[".env.example has no committed secret-looking tokens"].ok
    assert results[".gitignore ignores .env"].ok


def test_makefile_exposes_setup_check() -> None:
    assert check_make_targets().ok
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "setup-check:" in makefile


def test_run_checks_includes_python_and_repo_files() -> None:
    names = {item.name for item in run_checks()}
    assert "Python >= 3.12" in names
    assert "file docs/operations/LOCAL_SETUP.md" in names
    assert "Makefile setup targets" in names


def test_main_exits_zero_on_current_repo() -> None:
    assert main([]) == 0

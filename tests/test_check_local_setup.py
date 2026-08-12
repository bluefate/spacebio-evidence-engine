"""Tests for the local setup dry-run checklist (issue #6)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def _load_check_local_setup() -> ModuleType:
    script_path = ROOT / "scripts" / "check_local_setup.py"
    module_name = "check_local_setup"
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


check_local_setup = _load_check_local_setup()
REQUIRED_ENV_KEYS = check_local_setup.REQUIRED_ENV_KEYS
check_env_example = check_local_setup.check_env_example
check_make_targets = check_local_setup.check_make_targets
main = check_local_setup.main
run_checks = check_local_setup.run_checks


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

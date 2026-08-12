#!/usr/bin/env python3
"""Dry-run local setup checklist for issue #6.

Verifies tools, repo files, and `.env.example` hygiene without printing secret
values or requiring Docker/services to be running.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_ENV_KEYS = (
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "DATABASE_URL",
    "APP_ENV",
    "API_HOST",
    "API_PORT",
    "PDF_STORAGE_BACKEND",
    "PDF_STORAGE_LOCAL_ROOT",
    "EMBEDDING_MODEL",
)

SECRET_KEY_HINTS = ("PASSWORD", "SECRET", "TOKEN", "API_KEY", "PRIVATE_KEY")
# High-entropy placeholder patterns that should not appear committed.
FORBIDDEN_SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
)


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


def _have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def check_python() -> CheckResult:
    version = sys.version_info
    ok = version.major == 3 and version.minor >= 12
    return CheckResult(
        "Python >= 3.12",
        ok,
        f"{version.major}.{version.minor}.{version.micro}",
    )


def check_command(name: str, cmd: str) -> CheckResult:
    return CheckResult(name, _have(cmd), "found" if _have(cmd) else f"missing `{cmd}`")


def check_repo_files() -> list[CheckResult]:
    required = [
        ".env.example",
        "Makefile",
        "docker-compose.yml",
        "docs/operations/LOCAL_SETUP.md",
        "apps/api/src/spacebio_api/main.py",
        "apps/web/package.json",
        "scripts/bootstrap_pgvector.py",
    ]
    results: list[CheckResult] = []
    for rel in required:
        path = ROOT / rel
        detail = "present" if path.is_file() else "missing"
        results.append(CheckResult(f"file {rel}", path.is_file(), detail))
    return results


def _parse_env_example(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def check_env_example() -> list[CheckResult]:
    path = ROOT / ".env.example"
    results: list[CheckResult] = []
    if not path.is_file():
        return [CheckResult(".env.example", False, "missing")]

    text = path.read_text(encoding="utf-8")
    values = _parse_env_example(text)

    for key in REQUIRED_ENV_KEYS:
        results.append(
            CheckResult(
                f".env.example has {key}",
                key in values,
                "documented" if key in values else "missing",
            )
        )

    forbidden_hits = [
        pattern.pattern
        for pattern in FORBIDDEN_SECRET_PATTERNS
        if pattern.search(text)
    ]
    results.append(
        CheckResult(
            ".env.example has no committed secret-looking tokens",
            not forbidden_hits,
            "clean" if not forbidden_hits else f"matched {', '.join(forbidden_hits)}",
        )
    )

    # Placeholder passwords are fine; empty secret-like keys are also fine.
    for key, value in values.items():
        if not any(hint in key.upper() for hint in SECRET_KEY_HINTS):
            continue
        if not value:
            continue
        if value.startswith("change-me") or value in {"local", "development", "spacebio"}:
            continue
        # DATABASE_URL embeds the placeholder password; allow that pattern.
        if "change-me-locally" in value:
            continue
        results.append(
            CheckResult(
                f".env.example {key} looks like a placeholder",
                False,
                "replace with a non-secret placeholder before committing",
            )
        )

    gitignore_path = ROOT / ".gitignore"
    if gitignore_path.is_file():
        gitignore = gitignore_path.read_text(encoding="utf-8")
    else:
        gitignore = ""
    gitignore_lines = {line.strip() for line in gitignore.splitlines()}
    results.append(
        CheckResult(
            ".gitignore ignores .env",
            ".env" in gitignore_lines,
            "present" if ".env" in gitignore_lines else "add `.env` to .gitignore",
        )
    )
    return results


def check_make_targets() -> CheckResult:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    needed = ("setup:", "setup-check:", "services:", "api:", "web:", "validate:")
    missing = [target.rstrip(":") for target in needed if target not in makefile]
    return CheckResult(
        "Makefile setup targets",
        not missing,
        "ok" if not missing else f"missing {', '.join(missing)}",
    )


def check_local_env_present() -> CheckResult:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return CheckResult(
            "local .env (optional for dry-run)",
            True,
            "not present yet — copy from .env.example or run `make setup`",
        )
    # Confirm file exists without printing contents.
    size = env_path.stat().st_size
    return CheckResult(
        "local .env (optional for dry-run)",
        True,
        f"present ({size} bytes; contents not shown)",
    )


def run_checks() -> list[CheckResult]:
    checks: list[CheckResult] = [
        check_python(),
        check_command("node", "node"),
        check_command("npm", "npm"),
        check_command("docker", "docker"),
        check_command("make", "make"),
        check_command("git", "git"),
        check_make_targets(),
        check_local_env_present(),
    ]
    checks.extend(check_repo_files())
    checks.extend(check_env_example())
    return checks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-docker",
        action="store_true",
        help="Fail when docker is missing (default: warn-only for docker).",
    )
    args = parser.parse_args(argv)

    results = run_checks()
    soft_fail_names = set() if args.require_docker else {"docker"}

    print("Local setup checklist (issue #6)")
    print(f"Repository root: {ROOT}")
    failures = 0
    for result in results:
        status = "OK" if result.ok else "FAIL"
        if not result.ok and result.name == "docker" and result.name in soft_fail_names:
            status = "WARN"
        elif not result.ok:
            failures += 1
        print(f"[{status}] {result.name}: {result.detail}")

    if failures:
        print(f"\n{failures} check(s) failed.", file=sys.stderr)
        return 1
    print("\nAll required checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

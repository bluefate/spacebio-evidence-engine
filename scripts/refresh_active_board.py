#!/usr/bin/env python3
"""Refresh docs/development/ACTIVE_BOARD.md from GitHub Project + open PRs.

Regenerates the Mermaid tree and Next-options table between HTML markers so
agents can keep a shared snapshot current:

    make refresh-board

In-flight owner labels prefer GitHub issue assignees; if none are set, the
script falls back to the newest issue comment ``**CLAIMED BY:**`` value.

Requires `gh` authenticated against bluefate/spacebio-evidence-engine.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "docs" / "development" / "ACTIVE_BOARD.md"
OWNER = "bluefate"
REPO = "bluefate/spacebio-evidence-engine"
PROJECT_NUMBER = 6

BEGIN = "<!-- ACTIVE_BOARD:BEGIN -->"
END = "<!-- ACTIVE_BOARD:END -->"

# Critical-path edges used only for Mermaid layout (not for Project Status).
CRITICAL_EDGES: list[tuple[int, int]] = [
    (20, 27),
    (27, 28),
    (28, 29),
    (29, 30),
    (30, 31),
    (31, 32),
    (32, 33),
    (33, 42),  # vector schema needs chunk metadata (#33) first
    (27, 39),
    (39, 40),
    (40, 42),
    (42, 43),
    (43, 44),
]

# Issues always shown on the board (August MVP spine + common parallel picks).
TRACKED: dict[int, dict[str, str | bool]] = {
    20: {"title": "Corpus inventory", "critical": True},
    25: {"title": "Assess PDF quality", "critical": False},
    26: {"title": "Reference questions", "critical": False},
    27: {"title": "Publication schema", "critical": True},
    28: {"title": "PDF storage", "critical": True},
    29: {"title": "PDF extract", "critical": True},
    30: {"title": "Sections", "critical": True},
    31: {"title": "Page map", "critical": True},
    32: {"title": "Chunking strategy", "critical": True},
    33: {"title": "Chunk metadata schema", "critical": True},
    37: {"title": "Ingestion unit tests", "critical": False},
    39: {"title": "EmbeddingProvider interface", "critical": True},
    40: {"title": "Local embeddings", "critical": True},
    42: {"title": "Vector storage schema", "critical": True},
    43: {"title": "Vector indexing", "critical": True},
    44: {"title": "Semantic search", "critical": True},
    47: {"title": "Retrieval metadata filters", "critical": False},
    51: {"title": "LLM provider interface", "critical": False},
    55: {"title": "Insufficient evidence", "critical": False},
    57: {"title": "Answer response schema", "critical": False},
    86: {"title": "ACTIVE_BOARD.md", "critical": False},
}

DONE_STATUSES = frozenset({"Done"})
INFLIGHT_STATUSES = frozenset({"Claimed", "In Progress", "PR Open"})


@dataclass
class IssueState:
    number: int
    title: str
    status: str
    assignees: list[str]
    claimed_by: str | None
    branch: str | None
    pr_number: int | None
    critical: bool
    short_title: str

    @property
    def owner_label(self) -> str | None:
        """GitHub assignees first; else claim-comment CLAIMED BY."""
        if self.assignees:
            return ", ".join(self.assignees)
        if self.claimed_by:
            return self.claimed_by
        return None


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)}\n{result.stderr or result.stdout}")
    return result.stdout.strip()


def gql_stdin(query: str, variables: dict | None = None) -> dict:
    payload = json.dumps({"query": query, "variables": variables or {}})
    result = subprocess.run(
        ["gh", "api", "graphql", "--input", "-"],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    data = json.loads(result.stdout)
    if data.get("errors"):
        raise RuntimeError(json.dumps(data["errors"], indent=2))
    return data["data"]


def fetch_project_items() -> dict[int, dict]:
    """Return issue_number -> {title, status, assignees, state} for project items."""
    items: dict[int, dict] = {}
    cursor: str | None = None
    while True:
        data = gql_stdin(
            """
            query($login:String!, $number:Int!, $cursor:String) {
              user(login:$login) {
                projectV2(number:$number) {
                  items(first:100, after:$cursor) {
                    pageInfo { hasNextPage endCursor }
                    nodes {
                      content {
                        ... on Issue {
                          number
                          title
                          state
                          assignees(first:5) { nodes { login } }
                        }
                      }
                      fieldValueByName(name:"Status") {
                        ... on ProjectV2ItemFieldSingleSelectValue { name }
                      }
                    }
                  }
                }
              }
            }
            """,
            {"login": OWNER, "number": PROJECT_NUMBER, "cursor": cursor},
        )
        conn = data["user"]["projectV2"]["items"]
        for node in conn["nodes"]:
            content = node.get("content") or {}
            number = content.get("number")
            if number is None:
                continue
            status_node = node.get("fieldValueByName") or {}
            items[int(number)] = {
                "title": content.get("title") or "",
                "status": status_node.get("name") or "Planning",
                "state": content.get("state") or "OPEN",
                "assignees": [a["login"] for a in content.get("assignees", {}).get("nodes", [])],
            }
        if not conn["pageInfo"]["hasNextPage"]:
            break
        cursor = conn["pageInfo"]["endCursor"]
    return items


def fetch_open_prs() -> dict[int, tuple[int, str]]:
    """Map linked issue number -> (pr_number, head branch) for open PRs."""
    raw = run(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            REPO,
            "--state",
            "open",
            "--limit",
            "50",
            "--json",
            "number,title,headRefName,body",
        ]
    )
    prs = json.loads(raw)
    linked: dict[int, tuple[int, str]] = {}
    issue_pat = re.compile(r"(?:closes|close|fixes|fix|resolves|resolve)\s+#(\d+)", re.I)
    branch_pat = re.compile(r"^(?:feature|fix|docs|test|chore)/(\d+)-")
    for pr in prs:
        pr_number = int(pr["number"])
        branch = pr["headRefName"]
        body = pr.get("body") or ""
        title = pr.get("title") or ""
        numbers: set[int] = set()
        for match in issue_pat.finditer(f"{title}\n{body}"):
            numbers.add(int(match.group(1)))
        branch_match = branch_pat.match(branch)
        if branch_match:
            numbers.add(int(branch_match.group(1)))
        title_match = re.search(r"#(\d+)", title)
        if title_match:
            numbers.add(int(title_match.group(1)))
        for n in numbers:
            linked[n] = (pr_number, branch)
    return linked


def bucket(status: str) -> str:
    if status in DONE_STATUSES:
        return "done"
    if status in INFLIGHT_STATUSES:
        return "inflight"
    return "available"


def esc(text: str) -> str:
    return text.replace('"', "'").replace("[", "(").replace("]", ")")


def node_label(issue: IssueState) -> str:
    parts = [f"#{issue.number} {esc(issue.short_title)}"]
    if issue.branch:
        parts.append(f"branch: {esc(issue.branch)}")
    if issue.pr_number:
        parts.append(f"PR #{issue.pr_number}")
    if bucket(issue.status) == "inflight":
        owner = issue.owner_label
        if owner:
            parts.append(f"owner: {esc(owner)}")
        parts.append(f"status: {issue.status}")
    return "<br/>".join(parts)


def build_mermaid(issues: dict[int, IssueState]) -> str:
    done = [n for n, i in sorted(issues.items()) if bucket(i.status) == "done"]
    inflight = [n for n, i in sorted(issues.items()) if bucket(i.status) == "inflight"]
    critical_next = [
        n
        for n, i in sorted(issues.items())
        if bucket(i.status) == "available" and i.critical
    ]
    parallel_next = [
        n
        for n, i in sorted(issues.items())
        if bucket(i.status) == "available" and not i.critical
    ]

    lines = ["```mermaid", "flowchart TB"]

    def subgraph(name: str, title: str, nums: list[int]) -> None:
        lines.append(f"  subgraph {name} [{title}]")
        if not nums:
            lines.append(f'    {name}_empty["(none)"]')
        for n in nums:
            lines.append(f'    i{n}["{node_label(issues[n])}"]')
        lines.append("  end")

    subgraph("done", "Done", done)
    subgraph("inflight", "In flight — do not claim", inflight)
    subgraph("nextCritical", "Critical path — available / blocked", critical_next)
    subgraph("nextParallel", "Parallel-safe picks — available now", parallel_next)

    # Dependency edges among tracked issues that both appear on the board.
    shown = set(done) | set(inflight) | set(critical_next) | set(parallel_next)
    for src, dst in CRITICAL_EDGES:
        if src in shown and dst in shown:
            lines.append(f"  i{src} --> i{dst}")

    lines.append("```")
    return "\n".join(lines)


def deps_satisfied(number: int, issues: dict[int, IssueState]) -> bool:
    blockers = [src for src, dst in CRITICAL_EDGES if dst == number]
    if not blockers:
        return True
    return all(
        src not in issues or bucket(issues[src].status) == "done" for src in blockers
    )


def build_next_options(issues: dict[int, IssueState]) -> str:
    rows: list[str] = [
        "| Priority | Issue | Status | When to take it | Avoid if… |",
        "| ---: | --- | --- | --- | --- |",
    ]
    priority = 1

    # Critical path: first available whose deps are done.
    for number, issue in sorted(issues.items()):
        if not issue.critical:
            continue
        if bucket(issue.status) != "available":
            continue
        if not deps_satisfied(number, issues):
            blockers = [
                f"#{src}"
                for src, dst in CRITICAL_EDGES
                if dst == number and src in issues and bucket(issues[src].status) != "done"
            ]
            rows.append(
                f"| — | [#{number}](https://github.com/{REPO}/issues/{number}) "
                f"{issue.short_title} | {issue.status} | Wait on {', '.join(blockers)} | Blocked |"
            )
            continue
        rows.append(
            f"| {priority} | [#{number}](https://github.com/{REPO}/issues/{number}) "
            f"{issue.short_title} | {issue.status} | Next on critical path | Overlap on same files |"
        )
        priority += 1

    # Parallel picks.
    for number, issue in sorted(issues.items()):
        if issue.critical:
            continue
        b = bucket(issue.status)
        if b == "done":
            continue
        if b == "inflight":
            rows.append(
                f"| — | [#{number}](https://github.com/{REPO}/issues/{number}) "
                f"{issue.short_title} | {issue.status} | Already claimed | **Do not claim** |"
            )
            continue
        rows.append(
            f"| {priority} | [#{number}](https://github.com/{REPO}/issues/{number}) "
            f"{issue.short_title} | {issue.status} | Parallel-safe now | Overlap with in-flight files |"
        )
        priority += 1

    # In-flight critical (do not claim). Non-critical in-flight rows are
    # already listed above under parallel picks as "Already claimed".
    for number, issue in sorted(issues.items()):
        if not issue.critical:
            continue
        if bucket(issue.status) != "inflight":
            continue
        owner = issue.owner_label or "see claim comment"
        branch = issue.branch or "(branch on issue claim)"
        rows.append(
            f"| — | [#{number}](https://github.com/{REPO}/issues/{number}) "
            f"{issue.short_title} | {issue.status} | In flight ({owner}; `{branch}`) | **Do not claim** |"
        )

    return "\n".join(rows)


def build_generated_block(issues: dict[int, IssueState]) -> str:
    today = date.today().isoformat()
    return "\n".join(
        [
            BEGIN,
            f"**Last refreshed:** {today} via `make refresh-board` (Project #{PROJECT_NUMBER} + open PRs).",
            "",
            "## Live board (auto-generated)",
            "",
            build_mermaid(issues),
            "",
            "## Next options (auto-generated — pick one)",
            "",
            "Agents: choose **one** issue, claim it, run `make refresh-board`, commit this file in the same PR.",
            "",
            build_next_options(issues),
            "",
            END,
        ]
    )


def normalize_status(project_status: str, issue_state: str, has_open_pr: bool) -> str:
    """Reconcile Project Status with issue/PR reality for the Mermaid buckets."""
    if issue_state == "CLOSED" and not has_open_pr:
        return "Done"
    if has_open_pr and project_status not in DONE_STATUSES:
        return "PR Open"
    return project_status


def fetch_latest_claim_owner(number: int) -> str | None:
    """Parse the newest ``CLAIMED BY`` value from issue comments."""
    try:
        raw = run(
            [
                "gh",
                "api",
                f"repos/{REPO}/issues/{number}/comments",
                "--paginate",
            ]
        )
    except RuntimeError:
        return None
    if not raw:
        return None
    try:
        comments = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(comments, list):
        return None
    claimed_by_re = re.compile(
        r"^\s*[-*]?\s*\*\*CLAIMED BY:\*\*\s*(.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    for comment in reversed(comments):
        body = str(comment.get("body") or "")
        if "CLAIMED BY" not in body.upper():
            continue
        match = claimed_by_re.search(body)
        if match:
            return match.group(1).strip().strip("`").strip()
    return None


def load_states() -> dict[int, IssueState]:
    project = fetch_project_items()
    prs = fetch_open_prs()
    states: dict[int, IssueState] = {}
    for number, meta in TRACKED.items():
        info = project.get(number, {})
        pr = prs.get(number)
        title = str(info.get("title") or meta["title"])
        short = str(meta["title"])
        status = normalize_status(
            str(info.get("status") or "Planning"),
            str(info.get("state") or "OPEN"),
            pr is not None,
        )
        assignees = list(info.get("assignees") or [])
        claimed_by: str | None = None
        # Only hit the comments API for in-flight items missing assignees.
        if not assignees and status in INFLIGHT_STATUSES:
            claimed_by = fetch_latest_claim_owner(number)
        states[number] = IssueState(
            number=number,
            title=title,
            status=status,
            assignees=assignees,
            claimed_by=claimed_by,
            branch=pr[1] if pr else None,
            pr_number=pr[0] if pr else None,
            critical=bool(meta["critical"]),
            short_title=short,
        )
    return states


def replace_generated(doc: str, block: str) -> str:
    if BEGIN in doc and END in doc:
        pattern = re.compile(
            re.escape(BEGIN) + r".*?" + re.escape(END),
            flags=re.DOTALL,
        )
        return pattern.sub(block, doc, count=1)
    # Insert after the auto-refresh instructions heading if markers missing.
    anchor = "## Live board"
    idx = doc.find(anchor)
    if idx == -1:
        return doc.rstrip() + "\n\n" + block + "\n"
    # Replace from first Live board section through Related documents, keeping Related.
    related = doc.find("## Related documents")
    if related == -1:
        return doc[:idx] + block + "\n"
    return doc[:idx] + block + "\n\n" + doc[related:]


def main() -> int:
    try:
        states = load_states()
    except Exception as exc:  # noqa: BLE001 — surface gh/auth errors clearly
        print(f"refresh_active_board failed: {exc}", file=sys.stderr)
        return 1

    block = build_generated_block(states)
    original = BOARD_PATH.read_text(encoding="utf-8")
    updated = replace_generated(original, block)
    if not updated.endswith("\n"):
        updated += "\n"
    BOARD_PATH.write_text(updated, encoding="utf-8")
    print(f"Updated {BOARD_PATH.relative_to(ROOT)}")
    print(
        "Buckets:",
        {
            "done": [n for n, i in states.items() if bucket(i.status) == "done"],
            "inflight": [n for n, i in states.items() if bucket(i.status) == "inflight"],
            "available": [n for n, i in states.items() if bucket(i.status) == "available"],
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

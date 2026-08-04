#!/usr/bin/env python3
"""Set GitHub Project fields for seeded backlog issues."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path


OWNER = "bluefate"
PROJECT_NUMBER = 6
SEED = Path("/tmp/spacebio_backlog_seed.json")


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)}\n{result.stderr}\n{result.stdout}")
    return result.stdout.strip()


def gql(query: str, variables: dict) -> dict:
    payload = json.dumps({"query": query, "variables": variables})
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


def main() -> None:
    seed = json.loads(SEED.read_text())
    issues = seed["issues"]

    meta = gql(
        """
        query($owner:String!, $number:Int!) {
          user(login:$owner) {
            projectV2(number:$number) {
              id
              fields(first:50) {
                nodes {
                  ... on ProjectV2SingleSelectField {
                    id
                    name
                    options { id name }
                  }
                }
              }
            }
          }
        }
        """,
        {"owner": OWNER, "number": PROJECT_NUMBER},
    )
    project_id = meta["user"]["projectV2"]["id"]
    fields = {
        n["name"]: n
        for n in meta["user"]["projectV2"]["fields"]["nodes"]
        if n and n.get("name")
    }

    def option_id(field_name: str, option_name: str) -> str:
        field = fields[field_name]
        for opt in field["options"]:
            if opt["name"] == option_name:
                return opt["id"]
        raise KeyError(f"{field_name}: {option_name}")

    # Map issue number -> project item id (paginate)
    item_by_issue: dict[int, str] = {}
    cursor = None
    while True:
        page = gql(
            """
            query($owner:String!, $number:Int!, $cursor:String) {
              user(login:$owner) {
                projectV2(number:$number) {
                  items(first:100, after:$cursor) {
                    pageInfo { hasNextPage endCursor }
                    nodes {
                      id
                      content {
                        ... on Issue { number }
                      }
                    }
                  }
                }
              }
            }
            """,
            {"owner": OWNER, "number": PROJECT_NUMBER, "cursor": cursor},
        )
        conn = page["user"]["projectV2"]["items"]
        for n in conn["nodes"]:
            if n.get("content") and n["content"].get("number"):
                item_by_issue[n["content"]["number"]] = n["id"]
        if not conn["pageInfo"]["hasNextPage"]:
            break
        cursor = conn["pageInfo"]["endCursor"]


    mutation = """
    mutation($projectId:ID!, $itemId:ID!, $fieldId:ID!, $optionId:String!) {
      updateProjectV2ItemFieldValue(input:{
        projectId:$projectId
        itemId:$itemId
        fieldId:$fieldId
        value:{ singleSelectOptionId:$optionId }
      }) { projectV2Item { id } }
    }
    """

    updated = 0
    for issue in issues:
        number = issue["number"]
        item_id = item_by_issue.get(number)
        if not item_id:
            # Add to project
            issue_node = run(
                [
                    "gh",
                    "api",
                    f"repos/bluefate/spacebio-evidence-engine/issues/{number}",
                    "--jq",
                    ".node_id",
                ]
            )
            add = gql(
                """
                mutation($projectId:ID!, $contentId:ID!) {
                  addProjectV2ItemById(input:{projectId:$projectId, contentId:$contentId}) {
                    item { id }
                  }
                }
                """,
                {"projectId": project_id, "contentId": issue_node},
            )
            item_id = add["addProjectV2ItemById"]["item"]["id"]
            item_by_issue[number] = item_id

        mappings = [
            ("Status", issue["status"]),
            ("Priority", issue["priority"]),
            ("Work Type", issue["work_type"]),
            ("Roadmap Milestone", issue["roadmap_milestone"]),
            ("Parallel Safe", issue["parallel"]),
            ("Risk", issue["risk"]),
            ("Estimate", issue["estimate"]),
            ("Owner Type", issue["owner_type"]),
        ]
        for field_name, option_name in mappings:
            gql(
                mutation,
                {
                    "projectId": project_id,
                    "itemId": item_id,
                    "fieldId": fields[field_name]["id"],
                    "optionId": option_id(field_name, option_name),
                },
            )
            time.sleep(0.05)
        updated += 1
        print(f"Updated project fields for #{number}")

    print(f"Done. Updated {updated} issues.")


if __name__ == "__main__":
    main()

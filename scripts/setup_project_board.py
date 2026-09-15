#!/usr/bin/env python
"""Create the Group 9 project board, mirroring the instructor's Team-Planning template
(https://github.com/users/mkaouer/projects/5) and adding the Lean Six Sigma fields.

What it does (idempotent):
  1. Creates a user-owned Projects (v2) board titled from project.yml
     (default "Group 9 Team-Planning").
  2. Sets Status options to: Todo, In progress, Done, Block, Cancelled.
  3. Adds fields: Sprint (single select), Estimate (number), Priority (single select),
     Work type (single select; GitHub reserves the name "Type"), Start date, Target date.
  4. Links the repository and adds every open issue to the board.
  5. Sets the Sprint field of each item from its milestone.

Requires: `gh auth refresh -s project,read:project` (the default token lacks these scopes).

Manual steps it cannot do through the API (print at the end):
  - Board view: set WIP limit 5 on Todo and In progress (column menu > Set limit).
  - Workflows: enable "Item added to project -> Todo", "Item closed -> Done",
    "Pull request merged -> Done", and "Auto-add to project" for the repository.
  - Optional: add the built-in Iteration field (Sprint 1..3) if you want the Roadmap view.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

STATUS_OPTIONS = [
    ("Todo", "GREEN", "This item hasn't been started"),
    ("In progress", "YELLOW", "This is actively being worked on"),
    ("Done", "PURPLE", "This has been completed"),
    ("Block", "RED", "Blocked; raised with the Scrum Master"),
    ("Cancelled", "GRAY", "Will not be done; reason in the issue"),
]
SPRINT_OPTIONS = ["Formation", "Sprint 1", "Sprint 2", "Sprint 3", "Finalization"]
PRIORITY_OPTIONS = ["High", "Medium", "Low"]
TYPE_OPTIONS = ["research", "pipeline", "data", "docs", "test", "process", "report", "presentation"]


def sh(*args: str, input_text: str | None = None) -> str:
    proc = subprocess.run(list(args), capture_output=True, text=True, input=input_text)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(args)}\n{proc.stderr.strip()}")
    return proc.stdout


def gh_json(*args: str) -> object:
    out = sh("gh", *args)
    return json.loads(out) if out.strip() else None


def graphql(query: str, **variables: object) -> dict:
    args = ["api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        args += ["-F" if isinstance(v, (int, bool)) else "-f", f"{k}={v}"]
    return gh_json(*args)


def check_scopes() -> None:
    proc = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
    text = proc.stdout + proc.stderr
    if "project" not in text:
        print(
            "Your gh token lacks the project scope. Run:\n\n"
            "    gh auth refresh -s project,read:project\n",
            file=sys.stderr,
        )
        raise SystemExit(2)


def find_or_create_project(owner: str, title: str) -> dict:
    projects = (
        gh_json("project", "list", "--owner", owner, "--format", "json", "--limit", "100") or {}
    )
    for p in projects.get("projects", []):
        if p["title"] == title:
            print(f"project exists: {title} (#{p['number']})")
            return p
    print(f"project create: {title}")
    return gh_json("project", "create", "--owner", owner, "--title", title, "--format", "json")


def list_fields(number: int, owner: str) -> dict[str, dict]:
    data = (
        gh_json(
            "project",
            "field-list",
            str(number),
            "--owner",
            owner,
            "--format",
            "json",
            "--limit",
            "100",
        )
        or {}
    )
    return {f["name"]: f for f in data.get("fields", [])}


def set_status_options(field_id: str) -> None:
    opts = ", ".join(
        f'{{name: "{n}", color: {c}, description: "{d}"}}' for n, c, d in STATUS_OPTIONS
    )
    query = f"""
    mutation {{
      updateProjectV2Field(input: {{fieldId: "{field_id}", singleSelectOptions: [{opts}]}}) {{
        projectV2Field {{ ... on ProjectV2SingleSelectField {{ id name options {{ id name }} }} }}
      }}
    }}"""
    graphql(query)
    print("status options set: " + ", ".join(n for n, _, _ in STATUS_OPTIONS))


def ensure_field(
    number: int,
    owner: str,
    fields: dict[str, dict],
    name: str,
    data_type: str,
    options: list[str] | None = None,
) -> None:
    if name in fields:
        print(f"field exists: {name}")
        return
    args = [
        "project",
        "field-create",
        str(number),
        "--owner",
        owner,
        "--name",
        name,
        "--data-type",
        data_type,
    ]
    if options:
        args += ["--single-select-options", ",".join(options)]
    gh_json(*args, "--format", "json")
    print(f"field create: {name} ({data_type})")


def add_issues(number: int, owner: str, repo: str) -> None:
    issues = (
        gh_json(
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--limit",
            "500",
            "--json",
            "url,number,milestone",
        )
        or []
    )
    items = (
        gh_json(
            "project",
            "item-list",
            str(number),
            "--owner",
            owner,
            "--format",
            "json",
            "--limit",
            "500",
        )
        or {}
    )
    present = {i.get("content", {}).get("url") for i in items.get("items", [])}
    added = 0
    for issue in issues:
        if issue["url"] in present:
            continue
        sh("gh", "project", "item-add", str(number), "--owner", owner, "--url", issue["url"])
        added += 1
    print(f"issues added to board: {added} (already present: {len(present)})")


def set_sprint_from_milestone(number: int, owner: str, project_id: str, repo: str) -> None:
    """Set each board item's Sprint field from its issue milestone.

    `gh project item-list` does not include milestones, so they are looked up by URL
    from the repository's issue list.
    """
    fields = list_fields(number, owner)
    sprint = fields.get("Sprint")
    if not sprint:
        return
    option_ids = {o["name"]: o["id"] for o in sprint.get("options", [])}
    issues = (
        gh_json(
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "all",
            "--limit",
            "500",
            "--json",
            "url,milestone",
        )
        or []
    )
    milestone_by_url = {i["url"]: (i.get("milestone") or {}).get("title") for i in issues}
    items = (
        gh_json(
            "project",
            "item-list",
            str(number),
            "--owner",
            owner,
            "--format",
            "json",
            "--limit",
            "500",
        )
        or {}
    )
    updated = 0
    for item in items.get("items", []):
        url = (item.get("content") or {}).get("url")
        title = milestone_by_url.get(url)
        if title in option_ids and item.get("sprint") != title:
            sh(
                "gh",
                "project",
                "item-edit",
                "--id",
                item["id"],
                "--project-id",
                project_id,
                "--field-id",
                sprint["id"],
                "--single-select-option-id",
                option_ids[title],
            )
            updated += 1
    print(f"sprint field set from milestone on {updated} item(s)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--owner", default="@me")
    parser.add_argument("--title", default=None)
    args = parser.parse_args(argv)

    cfg = yaml.safe_load((ROOT / "project.yml").read_text(encoding="utf-8"))
    repo = cfg["repo"]
    title = args.title or f"Group {cfg.get('group', 9)} Team-Planning"

    check_scopes()
    project = find_or_create_project(args.owner, title)
    number, project_id = int(project["number"]), project["id"]

    fields = list_fields(number, args.owner)
    if "Status" in fields:
        set_status_options(fields["Status"]["id"])
    ensure_field(number, args.owner, fields, "Sprint", "SINGLE_SELECT", SPRINT_OPTIONS)
    ensure_field(number, args.owner, fields, "Estimate", "NUMBER")
    ensure_field(number, args.owner, fields, "Priority", "SINGLE_SELECT", PRIORITY_OPTIONS)
    ensure_field(number, args.owner, fields, "Work type", "SINGLE_SELECT", TYPE_OPTIONS)
    ensure_field(number, args.owner, fields, "Start date", "DATE")
    ensure_field(number, args.owner, fields, "Target date", "DATE")

    owner_login = (
        args.owner if args.owner != "@me" else sh("gh", "api", "user", "--jq", ".login").strip()
    )
    try:
        sh("gh", "project", "link", str(number), "--owner", owner_login, "--repo", repo)
        print(f"linked repository {repo}")
    except RuntimeError as exc:
        print(f"link skipped: {str(exc).splitlines()[-1]}")

    add_issues(number, args.owner, repo)
    set_sprint_from_milestone(number, args.owner, project_id, repo)

    print(f"\nBoard: {project.get('url', '')}")
    print("Manual steps in the browser:")
    print("  1. Board view > column menu on Todo and In progress > Set limit > 5")
    print(
        "  2. Project settings > Workflows: enable 'Item added -> Todo', 'Item closed -> Done', "
        "'Pull request merged -> Done', and 'Auto-add to project' for this repository"
    )
    print(
        "  3. Optional: add an Iteration field (3-week iterations from 2026-09-17) "
        "for the Roadmap view"
    )
    print("  4. Project settings > Manage access: add teammates as Write, the instructor as Read")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

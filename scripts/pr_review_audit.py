#!/usr/bin/env python
"""Per-sprint review KPIs for merged pull requests (Sprint 3 retrospective, issue #35).

For every merged pull request (any base branch) this counts, per sprint window:

* merged PRs, and how many of them were merged without an APPROVED review from a member
  other than the author submitted before the merge (the charter's Definition of Done);
* the median hours from opening to the first review by another member (any review state),
  over PRs authored by members (bot snapshot PRs excluded);
* the median hours from opening to merge, same population.

Sprint windows are calendar days in US Eastern Time, taken from
``docs/sprints/*/planning.md``: Sprint 1 2026-09-17 to 2026-10-07, Sprint 2 2026-10-08 to
2026-10-28, Sprint 3 2026-10-29 to 2026-11-18.

The data comes from the GitHub GraphQL API. A token is read from ``GITHUB_TOKEN`` or
``GH_TOKEN``, or from ``gh auth token``. ``--save-json`` keeps the raw pull requests so a run
can be repeated offline with ``--from-json``.

Usage::

    python scripts/pr_review_audit.py --repo jeraddunne/csc580-group9-msr2027 \
        --out docs/lean-six-sigma/metrics/pr_review_audit.csv
    python scripts/pr_review_audit.py --from-json raw.json --out /tmp/audit.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import subprocess
import sys
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

EASTERN = ZoneInfo("America/New_York")
SPRINTS = (
    ("Sprint 1", date(2026, 9, 17), date(2026, 10, 7)),
    ("Sprint 2", date(2026, 10, 8), date(2026, 10, 28)),
    ("Sprint 3", date(2026, 10, 29), date(2026, 11, 18)),
)
BOT_LOGINS = frozenset({"github-actions", "github-actions[bot]", "dependabot", "dependabot[bot]"})
COLUMNS = [
    "sprint",
    "start",
    "end",
    "merged_prs",
    "merged_without_nonauthor_approval",
    "without_approval_share",
    "without_approval_prs",
    "bot_prs",
    "member_prs",
    "median_first_review_hours",
    "median_open_to_merge_hours",
]
QUERY = """
query($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequests(first: 100, after: $cursor, states: MERGED) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number baseRefName createdAt mergedAt author { login }
        reviews(first: 100) { nodes { author { login } state submittedAt } }
      }
    }
  }
}
"""


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def login(actor: dict | None) -> str:
    return (actor or {}).get("login") or "ghost"


def is_bot(name: str) -> bool:
    return name in BOT_LOGINS or name.endswith("[bot]") or name.startswith("app/")


def approved_by_other(pr: dict) -> bool:
    """True when a member other than the author approved before the merge."""
    author, merged = login(pr.get("author")), parse_time(pr["mergedAt"])
    for review in pr["reviews"]["nodes"]:
        if review.get("state") != "APPROVED" or not review.get("submittedAt"):
            continue
        if login(review.get("author")) != author and parse_time(review["submittedAt"]) <= merged:
            return True
    return False


def first_review_hours(pr: dict) -> float | None:
    author, opened = login(pr.get("author")), parse_time(pr["createdAt"])
    times = [
        parse_time(r["submittedAt"])
        for r in pr["reviews"]["nodes"]
        if r.get("submittedAt") and login(r.get("author")) != author
    ]
    return (min(times) - opened).total_seconds() / 3600 if times else None


def in_window(moment: datetime, start: date, end: date) -> bool:
    lo = datetime(start.year, start.month, start.day, tzinfo=EASTERN)
    hi = datetime(end.year, end.month, end.day, tzinfo=EASTERN) + timedelta(days=1)
    return lo <= moment < hi


def _median(values: list[float]) -> str:
    return f"{statistics.median(values):.1f}" if values else ""


def audit(prs: list[dict], sprints=SPRINTS) -> list[dict]:
    rows = []
    for name, start, end in sprints:
        merged = sorted(
            (
                p
                for p in prs
                if p.get("mergedAt") and in_window(parse_time(p["mergedAt"]), start, end)
            ),
            key=lambda p: p["number"],
        )
        without = [p["number"] for p in merged if not approved_by_other(p)]
        members = [p for p in merged if not is_bot(login(p.get("author")))]
        first = [h for h in (first_review_hours(p) for p in members) if h is not None]
        to_merge = [
            (parse_time(p["mergedAt"]) - parse_time(p["createdAt"])).total_seconds() / 3600
            for p in members
        ]
        rows.append(
            {
                "sprint": name,
                "start": start.isoformat(),
                "end": end.isoformat(),
                "merged_prs": len(merged),
                "merged_without_nonauthor_approval": len(without),
                "without_approval_share": f"{len(without) / len(merged):.3f}" if merged else "",
                "without_approval_prs": " ".join(f"#{n}" for n in without),
                "bot_prs": len(merged) - len(members),
                "member_prs": len(members),
                "median_first_review_hours": _median(first),
                "median_open_to_merge_hours": _median(to_merge),
            }
        )
    return rows


def _token() -> str:
    for key in ("GITHUB_TOKEN", "GH_TOKEN"):
        if os.environ.get(key):
            return os.environ[key]
    try:
        out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(
            "No GitHub token: set GITHUB_TOKEN or sign in with `gh auth login`."
        ) from exc
    return out.stdout.strip()


def fetch(repo: str) -> list[dict]:
    owner, name = repo.split("/", 1)
    token, cursor, nodes = _token(), None, []
    while True:
        body = json.dumps(
            {"query": QUERY, "variables": {"owner": owner, "name": name, "cursor": cursor}}
        ).encode()
        request = urllib.request.Request(
            "https://api.github.com/graphql",
            data=body,
            headers={"Authorization": f"bearer {token}", "User-Agent": "group9-pr-review-audit"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.load(response)
        if data.get("errors"):
            raise SystemExit(f"GitHub API error: {data['errors']}")
        page = data["data"]["repository"]["pullRequests"]
        nodes.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            return nodes
        cursor = page["pageInfo"]["endCursor"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--repo", help="owner/name on GitHub")
    source.add_argument("--from-json", type=Path, help="raw pull requests saved by --save-json")
    parser.add_argument("--out", type=Path, help="CSV to write (printed to stdout otherwise)")
    parser.add_argument("--save-json", type=Path, help="also save the raw pull requests here")
    args = parser.parse_args(argv)

    if args.from_json:
        prs = json.loads(args.from_json.read_text(encoding="utf-8"))
    else:
        prs = fetch(args.repo)
    if args.save_json:
        args.save_json.write_text(json.dumps(prs, indent=1), encoding="utf-8")
    rows = audit(prs)

    handle = args.out.open("w", newline="", encoding="utf-8") if args.out else sys.stdout
    try:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if args.out:
            handle.close()
    if args.out:
        print(f"wrote {args.out} ({len(prs)} merged PRs read)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

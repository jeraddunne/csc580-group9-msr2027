#!/usr/bin/env python
"""Build docs/workspace/DIGEST.md from GitHub issues.

Collects Work sign-up (`signup`), Research finding (`finding`), and Decision needed
(`decision`) issues plus all open issues with their assignees.

Usage:
    python scripts/workspace_digest.py
    python scripts/workspace_digest.py --repo owner/name --out docs/workspace/DIGEST.md

Requires the GitHub CLI (`gh auth login`).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import yaml  # noqa: E402

from msr_pipeline.workspace import render_digest  # noqa: E402

FIELDS = "number,title,body,author,state,assignees,milestone,url,createdAt,labels"


def gh_issues(repo: str, *extra: str) -> list[dict]:
    cmd = ["gh", "issue", "list", "--repo", repo, "--limit", "300", "--json", FIELDS, *extra]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "gh issue list failed")
    return json.loads(proc.stdout or "[]")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--repo", default=None, help="owner/name (default: project.yml repo)")
    parser.add_argument("--out", default=str(ROOT / "docs" / "workspace" / "DIGEST.md"))
    args = parser.parse_args(argv)

    repo = args.repo
    if repo is None:
        cfg = yaml.safe_load((ROOT / "project.yml").read_text(encoding="utf-8")) or {}
        repo = cfg["repo"]

    try:
        signups = gh_issues(repo, "--label", "signup", "--state", "all")
        findings = gh_issues(repo, "--label", "finding", "--state", "all")
        decisions = gh_issues(repo, "--label", "decision", "--state", "all")
        open_work = gh_issues(repo, "--state", "open")
    except (OSError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    tracking = {"signup", "finding"}
    open_work = [i for i in open_work if not tracking & {lbl for lbl in _labels(i)}]
    markdown = render_digest(signups, findings, decisions, open_work, repo=repo)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(markdown + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


def _labels(issue: dict) -> list[str]:
    return [lbl.get("name", "") for lbl in issue.get("labels") or []]


if __name__ == "__main__":
    raise SystemExit(main())

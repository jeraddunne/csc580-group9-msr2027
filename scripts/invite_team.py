#!/usr/bin/env python
"""Invite team members (and optionally the instructor) as repository collaborators.

Reads handles from project.yml (`team[].github`). Blank handles are skipped with a reminder.

Usage:
    python scripts/invite_team.py                 # members with push access
    python scripts/invite_team.py --instructor    # also invite the instructor (read access)
    python scripts/invite_team.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def sh(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(list(args), capture_output=True, text=True)


def current_collaborators(repo: str) -> set[str]:
    proc = sh("gh", "api", f"repos/{repo}/collaborators?per_page=100")
    if proc.returncode != 0:
        return set()
    return {c["login"].lower() for c in json.loads(proc.stdout)}


def pending_invitations(repo: str) -> set[str]:
    proc = sh("gh", "api", f"repos/{repo}/invitations?per_page=100")
    if proc.returncode != 0:
        return set()
    return {i["invitee"]["login"].lower() for i in json.loads(proc.stdout)}


def invite(repo: str, handle: str, permission: str, dry: bool) -> None:
    if dry:
        print(f"would invite @{handle} ({permission})")
        return
    proc = sh(
        "gh",
        "api",
        "-X",
        "PUT",
        f"repos/{repo}/collaborators/{handle}",
        "-f",
        f"permission={permission}",
    )
    if proc.returncode == 0:
        print(f"invited @{handle} ({permission})")
    else:
        print(f"failed to invite @{handle}: {proc.stderr.strip()}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--instructor", action="store_true", help="also invite the instructor with read access"
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    cfg = yaml.safe_load((ROOT / "project.yml").read_text(encoding="utf-8"))
    repo = cfg["repo"]
    owner = repo.split("/")[0].lower()
    have = current_collaborators(repo) | pending_invitations(repo)

    for member in cfg.get("team", []):
        handle = (member.get("github") or "").strip().lstrip("@")
        if not handle:
            print(
                f"skip {member.get('name')}: no GitHub handle in project.yml yet "
                "(add it from their onboarding issue)"
            )
            continue
        if handle.lower() == owner or handle.lower() in have:
            print(f"already has access or pending: @{handle}")
            continue
        invite(repo, handle, "push", args.dry_run)

    if args.instructor:
        handle = (cfg.get("instructor") or {}).get("github", "")
        if handle and handle.lower() not in have:
            invite(repo, handle, "pull", args.dry_run)
        elif handle:
            print(f"instructor already has access or pending: @{handle}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

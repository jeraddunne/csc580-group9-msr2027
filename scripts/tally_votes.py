#!/usr/bin/env python
"""Tally topic-vote ballots and write docs/proposals/RESULTS.md.

Usage:
    python scripts/tally_votes.py                      # tally ballots, write RESULTS.md
    python scripts/tally_votes.py --no-fetch           # do not call `gh` for proposal titles
    python scripts/tally_votes.py --fail-on-problems   # non-zero exit if any ballot is invalid
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

from msr_pipeline.voting import load_ballots, render_markdown, tally  # noqa: E402


def load_weights(config_path: Path) -> dict[str, float]:
    if not config_path.exists():
        return {}
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    criteria = ((cfg.get("proposals") or {}).get("criteria")) or {}
    weights = {k: float(v.get("weight", 0)) for k, v in criteria.items() if isinstance(v, dict)}
    return weights


def fetch_titles(repo: str | None) -> dict[int, str]:
    """Fetch proposal issue titles with the GitHub CLI. Returns {} if unavailable."""
    cmd = [
        "gh",
        "issue",
        "list",
        "--label",
        "proposal",
        "--state",
        "all",
        "--limit",
        "100",
        "--json",
        "number,title",
    ]
    if repo:
        cmd += ["--repo", repo]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=True)
        return {int(i["number"]): i["title"] for i in json.loads(out.stdout)}
    except (OSError, subprocess.SubprocessError, ValueError, KeyError):
        return {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--ballots", default=str(ROOT / "docs" / "proposals" / "votes" / "ballots"))
    parser.add_argument("--out", default=str(ROOT / "docs" / "proposals" / "RESULTS.md"))
    parser.add_argument("--config", default=str(ROOT / "project.yml"))
    parser.add_argument(
        "--repo", default=None, help="owner/name for title lookup (default: from project.yml)"
    )
    parser.add_argument(
        "--no-fetch", action="store_true", help="do not call gh for proposal titles"
    )
    parser.add_argument("--fail-on-problems", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    weights = load_weights(config_path) or None
    repo = args.repo
    if repo is None and config_path.exists():
        cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        repo = cfg.get("repo")

    ballots, load_problems = load_ballots(args.ballots)
    result = tally(ballots, weights)
    result.problems = load_problems + result.problems
    titles = {} if args.no_fetch else fetch_titles(repo)
    markdown = render_markdown(result, titles)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(markdown, encoding="utf-8")

    if not args.quiet:
        print(markdown)
        print(f"\nWrote {out}")
    if result.problems:
        print(f"\n{len(result.problems)} problem(s) found.", file=sys.stderr)
        if args.fail_on_problems:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

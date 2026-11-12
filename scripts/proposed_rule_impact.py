#!/usr/bin/env python
"""Count what each proposed rule would add if it were activated (issue #132).

A proposed rule (`status: proposed` in rules/skill_risk_rules.yaml) does not run, so it
changes no result. Before the team decides whether to activate one in a later round, this
script reports how many contents of the main population it matches and how many of those
are not already high risk under the active rules.

Usage:
    python scripts/proposed_rule_impact.py              # count, then write the CSV
    python scripts/proposed_rule_impact.py --dry-run    # count and print only

Output:
    results/proposed_rule_impact.csv    one row per proposed rule

The population is the one the analysis uses: one row per distinct content
(`dedup_primary = 1`), kept when `population_flags` marks it `in_main_population`.
"High risk" uses the rule file's `high_risk_severity`.

Reading the numbers: these are signal counts for an unvalidated pattern. None of the
matches has been labelled, so they say how far the headline share would move, not how
many of the added contents are risky.

Safety: dataset text is only read and matched. Nothing is executed, imported, or fetched,
and the output holds rule ids and counts, no dataset text.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from msr_pipeline import skill_risk  # noqa: E402

COLUMNS = [
    "rule_id",
    "status",
    "category",
    "severity",
    "main_population",
    "contents_matched",
    "already_high_risk",
    "newly_high_risk",
    "occurrences_matched",
    "high_risk_contents_now",
    "high_risk_contents_if_activated",
    "high_risk_share_now",
    "high_risk_share_if_activated",
]


def impact(
    main_reps: pd.DataFrame,
    counts: pd.DataFrame,
    active: list[skill_risk.Rule],
    inactive: list[skill_risk.Rule],
    high_risk_severity: int = skill_risk.HIGH_RISK_SEVERITY,
) -> pd.DataFrame:
    """One row per inactive rule: its matches in ``main_reps`` and the change in high risk.

    ``main_reps`` has columns file_sha and content, one row per distinct content.
    ``counts`` is the output of ``skill_risk.copy_counts``.
    """
    scan = skill_risk.scan_contents(main_reps, active, high_risk_severity)
    high_now = set(scan.loc[scan["high_risk"], "file_sha"])
    copies = dict(zip(counts["file_sha"], counts["copies"], strict=True))
    population = len(main_reps)
    rows = []
    for rule in inactive:
        matched = {
            rec["file_sha"]
            for rec in main_reps.to_dict("records")
            if isinstance(rec.get("content"), str) and rule.matches(rec["content"])
        }
        adds_high = rule.severity >= high_risk_severity
        newly = matched - high_now if adds_high else set()
        after = len(high_now | newly)
        rows.append(
            {
                "rule_id": rule.id,
                "status": rule.status,
                "category": rule.category,
                "severity": rule.severity,
                "main_population": population,
                "contents_matched": len(matched),
                "already_high_risk": len(matched & high_now),
                "newly_high_risk": len(newly),
                "occurrences_matched": int(sum(copies.get(sha, 1) for sha in matched)),
                "high_risk_contents_now": len(high_now),
                "high_risk_contents_if_activated": after,
                "high_risk_share_now": round(len(high_now) / population, 4) if population else 0.0,
                "high_risk_share_if_activated": round(after / population, 4) if population else 0.0,
            }
        )
    return pd.DataFrame(rows, columns=COLUMNS)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", type=Path, default=ROOT / "data/samples/agent_skills_sample.db")
    parser.add_argument("--dry-run", action="store_true", help="print the counts, write nothing")
    args = parser.parse_args(argv)

    from msr_pipeline.load import query_gitskills

    rule_file = skill_risk.read_rule_file()
    cutoff = int(rule_file.get("high_risk_severity", skill_risk.HIGH_RISK_SEVERITY))
    every = skill_risk.rules_from_dict(rule_file, include_inactive=True)
    active = [r for r in every if r.status == "active"]
    proposed = [r for r in every if r.status == "proposed"]
    if not proposed:
        print("No proposed rules in the rule file.")
        return 0

    reps = query_gitskills(
        "SELECT a.file_sha, a.name, a.content, a.first_commit_at, a.frontmatter_valid, "
        "a.content_sha_ok FROM artifacts a WHERE a.dedup_primary = 1 ORDER BY a.file_sha",
        args.db,
    )
    occurrences = query_gitskills("SELECT file_sha, repo_full_name FROM artifacts", args.db)
    flags = skill_risk.population_flags(reps)
    main_reps = reps[flags["in_main_population"].to_numpy()].reset_index(drop=True)

    table = impact(main_reps, skill_risk.copy_counts(occurrences), active, proposed, cutoff)
    print(table.to_string(index=False))
    if not args.dry_run:
        out = ROOT / "results/proposed_rule_impact.csv"
        table.to_csv(out, index=False, lineterminator="\n")
        print(f"\nSaved {out.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

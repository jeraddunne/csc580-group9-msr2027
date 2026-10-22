#!/usr/bin/env python
"""Check the scanner against the known-positive skills chosen for issue #97.

The instructor asked for about ten skills known to contain the issues, used as ground
truth before scaling up. A team member who did not write the rules picks the skills and
records, for each one, the capability it is expected to show
(docs/validation/KNOWN_POSITIVES_SELECTION.md). This script finds each skill in the
GitSkills sample, runs the rule file over its SKILL.md text and its bundled scripts, and
reports whether the expected category was detected.

Usage:
    python scripts/ground_truth_check.py              # check, then write the two CSVs
    python scripts/ground_truth_check.py --dry-run    # check and print counts only

Outputs:
    results/ground_truth_check.csv      one row per candidate
    results/ground_truth_summary.csv    one row per expected category, plus a total

"Detected" means a rule of the expected category matched the SKILL.md text. "Detected at
high risk" means one of those rules has severity 6 or more, so the review workflow would
show it to a reviewer (docs/research/REVIEW_WORKFLOW.md). Bundled scripts are reported in
their own columns because the selection was made from SKILL.md text.

Blindness: a candidate that is also in a validation sample would show its selector's
judgement to the primary rater. The script stops when any candidate is in
data/annotations/samples/, and prints only how many, never which. The selector, not the
primary rater, runs it with --list-overlap to find and replace them.

Safety: dataset text is only read and matched. Nothing is executed, imported, or fetched,
and the outputs hold identifiers, paths, and rule ids, no dataset text.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from msr_pipeline.config import gitskills_db_path  # noqa: E402
from msr_pipeline.load import query_gitskills  # noqa: E402
from msr_pipeline.skill_risk import (  # noqa: E402
    HIGH_RISK_SEVERITY,
    SCRIPT_EXTENSIONS,
    Rule,
    load_rules,
    scan_text,
)

SELECTION = ROOT / "docs" / "validation" / "KNOWN_POSITIVES_SELECTION.md"
SAMPLES = ROOT / "data" / "annotations" / "samples"
RESULTS = ROOT / "results"
SAMPLE_SHA_COLUMNS = ("file_sha", "file_sha_a", "file_sha_b")

CHECK_COLUMNS = [
    "candidate_id",
    "skill_path",
    "expected_category",
    "resolved",
    "rule_ids",
    "categories",
    "max_severity",
    "detected",
    "detected_high_risk",
    "scripts_scanned",
    "script_categories",
    "detected_in_scripts",
]
SUMMARY_COLUMNS = [
    "expected_category",
    "candidates",
    "resolved",
    "detected",
    "detected_high_risk",
    "detected_in_scripts",
    "missed",
]

# | f699537c00478727 | `.claude/skills/x/SKILL.md` | NETWORK | evidence ... |
_ROW = re.compile(r"^\|\s*([0-9a-f]{16})\s*\|\s*`?([^`|]+?)`?\s*\|\s*([A-Z_]+)\s*\|")


def candidate_id(repo_full_name: str, path: str) -> str:
    """First 16 hex characters of SHA-256(repo_full_name + newline + path)."""
    return hashlib.sha256(f"{repo_full_name}\n{path}".encode()).hexdigest()[:16]


def read_selection(path: Path) -> list[dict]:
    """Candidate rows (candidate_id, skill_path, expected_category) from the selection table."""
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _ROW.match(line.strip())
        if m:
            rows.append(
                {"candidate_id": m[1], "skill_path": m[2].strip(), "expected_category": m[3]}
            )
    ids = [r["candidate_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{path.name}: a candidate id appears twice")
    return rows


def resolve(candidates: list[dict], db_path: Path) -> dict[str, dict]:
    """Map candidate id to its SKILL.md record (repo_full_name, path, file_sha, content)."""
    wanted = {c["candidate_id"] for c in candidates}
    index = query_gitskills(
        "SELECT repo_full_name, path FROM artifacts WHERE lower(filename) = 'skill.md'",
        db_path=db_path,
    )
    found: dict[str, dict] = {}
    for rec in index.to_dict("records"):
        cid = candidate_id(rec["repo_full_name"], rec["path"])
        if cid in wanted:
            row = query_gitskills(
                "SELECT repo_full_name, path, file_sha, content FROM artifacts "
                "WHERE repo_full_name = ? AND path = ?",
                db_path=db_path,
                params=(rec["repo_full_name"], rec["path"]),
            )
            found[cid] = row.iloc[0].to_dict()
    return found


def bundled_scripts(record: dict, db_path: Path) -> list[str]:
    """Text of the script files bundled next to a SKILL.md (same filter as the pipeline)."""
    rows = query_gitskills(
        "SELECT entry_name, content FROM artifact_siblings "
        "WHERE repo_full_name = ? AND artifact_path = ?",
        db_path=db_path,
        params=(record["repo_full_name"], record["path"]),
    )
    texts = []
    for rec in rows.to_dict("records"):
        name = str(rec.get("entry_name") or "").lower()
        if name.endswith(SCRIPT_EXTENSIONS) and isinstance(rec.get("content"), str):
            texts.append(rec["content"])
    return texts


def sample_overlap(records: dict[str, dict], samples_dir: Path) -> list[str]:
    """Candidate ids whose content is also in a validation sample."""
    shas: set[str] = set()
    for path in sorted(samples_dir.glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                shas.update(row[c] for c in SAMPLE_SHA_COLUMNS if row.get(c))
    return sorted(cid for cid, rec in records.items() if rec.get("file_sha") in shas)


def check(
    candidates: list[dict],
    records: dict[str, dict],
    scripts: dict[str, list[str]],
    rules: list[Rule],
    high_risk_severity: int = HIGH_RISK_SEVERITY,
) -> list[dict]:
    """One result row per candidate."""
    by_id = {r.id: r for r in rules}
    out = []
    for c in candidates:
        rec = records.get(c["candidate_id"])
        expected = c["expected_category"]
        row = dict.fromkeys(CHECK_COLUMNS, "")
        row.update(c)
        row["resolved"] = rec is not None
        if rec is None:
            row.update(detected=False, detected_high_risk=False, detected_in_scripts=False)
            out.append(row)
            continue
        ids = scan_text(rec.get("content") if isinstance(rec.get("content"), str) else "", rules)
        hits = [by_id[i] for i in ids]
        script_cats = sorted(
            {
                by_id[i].category
                for text in scripts.get(c["candidate_id"], [])
                for i in scan_text(text, rules)
            }
        )
        row.update(
            rule_ids=";".join(ids),
            categories=";".join(sorted({r.category for r in hits})),
            max_severity=max((r.severity for r in hits), default=0),
            detected=any(r.category == expected for r in hits),
            detected_high_risk=any(
                r.category == expected and r.severity >= high_risk_severity for r in hits
            ),
            scripts_scanned=len(scripts.get(c["candidate_id"], [])),
            script_categories=";".join(script_cats),
            detected_in_scripts=expected in script_cats,
        )
        out.append(row)
    return out


def summarise(rows: list[dict]) -> list[dict]:
    """Counts per expected category, then a TOTAL row."""
    groups: dict[str, list[dict]] = {}
    for r in rows:
        groups.setdefault(r["expected_category"], []).append(r)
    groups["TOTAL"] = rows

    def count(items: list[dict], key: str) -> int:
        return sum(1 for r in items if r[key] is True)

    return [
        {
            "expected_category": cat,
            "candidates": len(items),
            "resolved": count(items, "resolved"),
            "detected": count(items, "detected"),
            "detected_high_risk": count(items, "detected_high_risk"),
            "detected_in_scripts": count(items, "detected_in_scripts"),
            "missed": sum(1 for r in items if r["resolved"] is True and r["detected"] is not True),
        }
        for cat, items in sorted(groups.items(), key=lambda kv: (kv[0] == "TOTAL", kv[0]))
    ]


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selection", type=Path, default=SELECTION)
    parser.add_argument("--db", type=Path, default=None, help="GitSkills SQLite sample")
    parser.add_argument("--rules", type=Path, default=None, help="rule file")
    parser.add_argument("--samples", type=Path, default=SAMPLES, help="validation samples")
    parser.add_argument("--out", type=Path, default=RESULTS)
    parser.add_argument("--dry-run", action="store_true", help="print counts, write nothing")
    parser.add_argument(
        "--list-overlap",
        action="store_true",
        help="for the selector only: print the candidate ids that are in a validation sample",
    )
    args = parser.parse_args(argv)

    if not args.selection.exists():
        print(f"{args.selection} not found; the selection comes from issue #97 (PR #106)")
        return 2
    candidates = read_selection(args.selection)
    if not candidates:
        print(f"no candidate rows found in {args.selection}")
        return 2
    db_path = args.db or gitskills_db_path()
    records = resolve(candidates, db_path)

    overlap = sample_overlap(records, args.samples)
    if args.list_overlap:
        print("\n".join(overlap) if overlap else "no candidate is in a validation sample")
        return 0
    if overlap:
        print(
            f"{len(overlap)} candidate(s) are also in a validation sample. To keep the primary "
            "rater blind, the selector replaces them (find them with --list-overlap) before "
            "this check runs."
        )
        return 3

    rules = load_rules(args.rules)
    scripts = {cid: bundled_scripts(rec, db_path) for cid, rec in records.items()}
    rows = check(candidates, records, scripts, rules)
    summary = summarise(rows)
    total = summary[-1]
    print(
        f"{total['candidates']} candidates, {total['resolved']} found in the sample, "
        f"{total['detected']} detected, {total['detected_high_risk']} detected at high risk, "
        f"{total['missed']} missed"
    )
    if args.dry_run:
        return 0
    write_csv(args.out / "ground_truth_check.csv", rows, CHECK_COLUMNS)
    write_csv(args.out / "ground_truth_summary.csv", summary, SUMMARY_COLUMNS)
    print(f"wrote {args.out / 'ground_truth_check.csv'} and ground_truth_summary.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())

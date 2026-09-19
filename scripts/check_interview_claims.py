#!/usr/bin/env python
"""Check the notebook interview's data claims against the GitSkills sample.

The elicitation notebook answers from documentation only. The team verifies the
answers that make claims about the data by running these read-only checks on the
sample database and cites the check IDs (V01, V02, ...) in
elicitation/notebook-interview.md. Output is aggregate counts only: no skill
text, commit message, repository name, or author code is printed.

Usage:
    python scripts/check_interview_claims.py            # writes elicitation/verification-checks.md
    python scripts/check_interview_claims.py --stdout   # print instead
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from msr_pipeline.config import gitskills_db_path  # noqa: E402
from msr_pipeline.skill_risk import SCRIPT_EXTENSIONS  # noqa: E402

FULL_DISTINCT_CONTENTS = 1_877_981  # A2 abstract; A9 "Sample vs full dataset"
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
AI_NAMES = re.compile(
    r"claude|copilot|gpt|codex|cursor|gemini|devin|aider|anthropic|openai|junie|windsurf|kiro",
    re.I,
)


def trailer_shape(body: str) -> str:
    """Classify the name part of a Co-authored-by trailer without printing it."""
    if AI_NAMES.search(body):
        return "AI assistant named"
    if body.startswith(("<<redacted>>", "<redacted>")):
        return "fixed marker"
    if "[bot]" in body:
        return "bot login"
    if re.match(r"[0-9a-f]{16}\b", body):
        return "16-character code"
    return "other"


def run_checks(con: sqlite3.Connection) -> list[tuple[str, str, str, str]]:
    """(check id, questions, what is checked, result) for every check."""
    one = lambda sql: con.execute(sql).fetchone()  # noqa: E731
    rows = lambda sql: con.execute(sql).fetchall()  # noqa: E731
    out: list[tuple[str, str, str, str]] = []

    occ, reps, shas = one(
        "SELECT COUNT(*), SUM(dedup_primary), COUNT(DISTINCT file_sha) FROM artifacts"
    )
    out.append(
        (
            "V01",
            "NB-Q01",
            "Occurrences, representatives, distinct contents",
            f"{occ:,} occurrences; {reps:,} rows with dedup_primary = 1; "
            f"{shas:,} distinct file_sha",
        )
    )
    bad = one(
        "SELECT COUNT(*) FROM (SELECT file_sha FROM artifacts GROUP BY file_sha "
        "HAVING SUM(dedup_primary) <> 1)"
    )[0]
    out.append(
        (
            "V02",
            "NB-Q01, NB-Q07a",
            "Every distinct content has exactly one representative",
            f"{bad} violations",
        )
    )
    same, n = one(
        "SELECT SUM(a.content = r.content), COUNT(*) FROM artifacts a JOIN artifacts r "
        "ON r.file_sha = a.file_sha AND r.dedup_primary = 1 "
        "WHERE a.dedup_primary = 0 AND a.content IS NOT NULL"
    )
    out.append(
        (
            "V03",
            "NB-Q01",
            "Non-representative rows that carry `content`",
            f"{n} rows (documentation: representatives only); "
            f"{same or 0} of them identical to their representative's text",
        )
    )
    names = ", ".join(
        f"`{f}` {c:,}"
        for f, c in rows(
            "SELECT filename, COUNT(*) FROM artifacts GROUP BY filename ORDER BY 2 DESC"
        )
    )
    variants = one("SELECT SUM(filename <> 'SKILL.md') FROM artifacts")[0]
    out.append(
        (
            "V04",
            "NB-Q02",
            "Filename case variants",
            f"{names}; non-`SKILL.md` names {variants:,} ({variants / occ:.2%})",
        )
    )
    fm = dict(
        rows("SELECT frontmatter_valid, COUNT(*) FROM artifacts WHERE dedup_primary = 1 GROUP BY 1")
    )
    out.append(
        (
            "V05",
            "NB-Q02",
            "Front matter valid among representatives",
            f"valid {fm.get(1, 0):,}; not valid {fm.get(0, 0):,} ({fm.get(1, 0) / reps:.1%} valid)",
        )
    )
    max_sha = one("SELECT MAX(file_sha) FROM artifacts")[0]
    share = int(max_sha, 16) / 16 ** len(max_sha)
    out.append(
        (
            "V06",
            "NB-Q03",
            "Lowest-hash sampling rule",
            f"largest file_sha starts `{max_sha[:6]}`, at {share:.4%} of the hash space; "
            f"13,000 of {FULL_DISTINCT_CONTENTS:,} is {13000 / FULL_DISTINCT_CONTENTS:.4%}",
        )
    )
    total, text, dirs = one(
        "SELECT COUNT(*), SUM(content IS NOT NULL), SUM(entry_type = 'dir') FROM artifact_siblings"
    )
    fetched = ", ".join(
        f"content_fetched = {cf}: {c:,}"
        for cf, c in rows(
            "SELECT content_fetched, COUNT(*) FROM artifact_siblings "
            "WHERE entry_type = 'file' AND content IS NULL GROUP BY 1"
        )
    )
    big = one(
        "SELECT COUNT(*) FROM artifact_siblings WHERE entry_type = 'file' "
        "AND content IS NULL AND entry_size > 102400"
    )[0]
    reason = one(
        "SELECT COUNT(*) FROM artifact_siblings WHERE skipped_reason IS NOT NULL "
        "AND skipped_reason <> ''"
    )[0]
    out.append(
        (
            "V07",
            "NB-Q04, NB-Q05",
            "Bundled files with and without text",
            f"{total:,} rows; {text:,} with text; {dirs:,} directories; files without "
            f"text: {fetched} ({big:,} over 100 KB); rows with a `skipped_reason`: {reason}",
        )
    )
    orphan = one(
        "SELECT COUNT(*) FROM artifact_siblings s WHERE NOT EXISTS (SELECT 1 FROM artifacts a "
        "WHERE a.repo_full_name = s.repo_full_name AND a.path = s.artifact_path "
        "AND a.dedup_primary = 1)"
    )[0]
    out.append(
        (
            "V08",
            "NB-Q04",
            "Bundled-file rows whose (repo, path) is not a representative",
            f"{orphan} rows",
        )
    )
    sha_ok = ", ".join(
        f"{v}: {c:,}"
        for v, c in rows(
            "SELECT content_sha_ok, COUNT(*) FROM artifacts WHERE dedup_primary = 1 GROUP BY 1"
        )
    )
    out.append(("V09", "NB-Q05, NB-Q05a", "`content_sha_ok` among representatives", sha_ok))
    trunc = ", ".join(
        f"{v}: {c:,}"
        for v, c in rows(
            "SELECT composition_truncated, COUNT(*) FROM artifacts WHERE dedup_primary = 1 "
            "GROUP BY 1"
        )
    )
    avg1, avg0 = one(
        "SELECT AVG(CASE WHEN composition_truncated = 1 THEN sibling_count END), "
        "AVG(CASE WHEN composition_truncated = 0 THEN sibling_count END) "
        "FROM artifacts WHERE dedup_primary = 1"
    )
    nofold = one(
        "SELECT COUNT(*) FROM artifacts WHERE dedup_primary = 1 "
        "AND COALESCE(composition_fetched, 0) = 0"
    )[0]
    out.append(
        (
            "V10",
            "NB-Q05",
            "`composition_truncated` and missing folder listings",
            f"{trunc}; mean sibling_count {avg1:.1f} when truncated vs {avg0:.1f}; "
            f"representatives without a folder listing: {nofold}",
        )
    )
    hist = "; ".join(
        f"{loc}: {h:,} of {c:,}"
        for loc, h, c in rows(
            "SELECT location_class, SUM(history_fetched), COUNT(*) FROM artifacts "
            "WHERE dedup_primary = 1 GROUP BY 1"
        )
    )
    stray = one(
        "SELECT SUM(COALESCE(history_fetched, 0) = 0 AND first_commit_at IS NOT NULL), "
        "SUM(history_fetched = 1 AND first_commit_at IS NULL), SUM(history_fetched = 1 "
        "AND dedup_primary = 0) FROM artifacts"
    )
    out.append(
        (
            "V11",
            "NB-Q06",
            "Commit history coverage by location (representatives)",
            f"{hist}. Dates without history_fetched: {stray[0]}; history_fetched without "
            f"a date: {stray[1]}; history on non-representatives: {stray[2]}",
        )
    )
    multi, copies_max = one(
        "SELECT SUM(c >= 2), MAX(c) FROM (SELECT COUNT(*) c FROM artifacts GROUP BY file_sha)"
    )
    cross = one(
        "SELECT SUM(r >= 2) FROM (SELECT COUNT(DISTINCT repo_full_name) r "
        "FROM artifacts GROUP BY file_sha)"
    )[0]
    out.append(
        (
            "V12",
            "NB-Q07a",
            "Copies kept with each sampled content",
            f"{multi:,} contents have 2 or more copies ({cross:,} in 2 or more "
            f"repositories); most copies of one content: {copies_max:,}",
        )
    )
    fam, fam_rows = one(
        "SELECT COUNT(*), SUM(n) FROM (SELECT LOWER(TRIM(name)) k, COUNT(*) n FROM artifacts "
        "WHERE dedup_primary = 1 AND TRIM(COALESCE(name, '')) <> '' GROUP BY k HAVING n >= 2)"
    )
    out.append(
        (
            "V13",
            "NB-Q07, NB-Q07a",
            "Same-name families with more than one content",
            f"{fam:,} front-matter names shared by {fam_rows:,} distinct contents",
        )
    )
    msgs = [
        m
        for (m,) in rows(
            "SELECT first_commit_message FROM artifacts WHERE first_commit_message IS NOT NULL "
            "UNION ALL SELECT last_commit_message FROM artifacts "
            "WHERE last_commit_message IS NOT NULL"
        )
    ]
    emails = sum(bool(EMAIL.search(m)) for m in msgs)
    markers = Counter(t for m in msgs for t in re.findall(r"<<redacted>>|<redacted>", m))
    out.append(
        (
            "V14",
            "NB-Q12",
            "Email-like strings and masking markers in commit messages",
            f"{len(msgs):,} messages; {emails} contain an email-like string; markers: "
            + ", ".join(f"`{k}` {v:,}" for k, v in markers.most_common()),
        )
    )
    trailers = [
        ln.split(":", 1)[1].strip()
        for m in msgs
        for ln in m.splitlines()
        if re.match(r"\s*co-authored-by:", ln, re.I)
    ]
    shapes = Counter(trailer_shape(b) for b in trailers)
    out.append(
        (
            "V15",
            "NB-Q12",
            "How co-author names in `Co-authored-by` trailers appear",
            f"{len(trailers):,} trailers: "
            + ", ".join(f"{k} {v:,}" for k, v in shapes.most_common()),
        )
    )
    codes = ", ".join(
        f"{t or '(empty)'} length {n}: {c:,}"
        for n, t, c in rows(
            "SELECT LENGTH(first_commit_author), first_commit_author_type, COUNT(*) FROM artifacts "
            "WHERE first_commit_author IS NOT NULL GROUP BY 1, 2 ORDER BY 3 DESC"
        )
    )
    out.append(("V16", "NB-Q12", "First-commit author values by account type", codes))
    lic = rows(
        "SELECT COALESCE(NULLIF(r.license, ''), '(none)') l, COUNT(*) FROM artifacts a "
        "JOIN repos r ON r.full_name = a.repo_full_name WHERE a.dedup_primary = 1 "
        "GROUP BY l ORDER BY 2 DESC"
    )
    none = sum(c for spdx, c in lic if spdx in ("(none)", "NOASSERTION"))
    out.append(
        (
            "V17",
            "NB-Q13",
            "License of each representative's repository",
            ", ".join(f"{spdx} {c:,}" for spdx, c in lic[:5]) + f"; no usable license "
            f"(none or NOASSERTION): {none:,} of {reps:,} ({none / reps:.1%})",
        )
    )
    sib: dict[tuple[str, str], list[str]] = {}
    for repo, path, name in rows(
        "SELECT repo_full_name, artifact_path, entry_name "
        "FROM artifact_siblings WHERE entry_type = 'file'"
    ):
        sib.setdefault((repo, path), []).append(name.lower())
    tab: Counter[tuple[int, bool]] = Counter()
    for repo, path, hs in rows(
        "SELECT repo_full_name, path, has_scripts FROM artifacts "
        "WHERE dedup_primary = 1 AND composition_fetched = 1"
    ):
        has_ext = any(n.endswith(SCRIPT_EXTENSIONS) for n in sib.get((repo, path), []))
        tab[(int(hs or 0), has_ext)] += 1
    out.append(
        (
            "V18",
            "NB-Q14",
            "`has_scripts` against P-01's script-extension list",
            f"has_scripts 1 with a script file {tab[(1, True)]:,}, without {tab[(1, False)]:,}; "
            f"has_scripts 0 with a script file {tab[(0, True)]:,}, without {tab[(0, False)]:,}",
        )
    )
    return out


def render(checks: list[tuple[str, str, str, str]], db: Path) -> str:
    lines = [
        "# Verification checks for the notebook interview",
        "",
        "Generated by `python scripts/check_interview_claims.py` "
        f"on {datetime.now(UTC).strftime('%Y-%m-%d')} from `{db.name}` (read-only). Aggregate "
        "counts only. `elicitation/notebook-interview.md` cites these IDs.",
        "",
        "| Check | Questions | What is checked | Result |",
        "|---|---|---|---|",
    ]
    lines += [f"| {c} | {q} | {what} | {res} |" for c, q, what, res in checks]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--db", type=Path, default=None, help="Sample database path.")
    parser.add_argument("--out", type=Path, default=ROOT / "elicitation" / "verification-checks.md")
    parser.add_argument("--stdout", action="store_true", help="Print instead of writing --out.")
    args = parser.parse_args(argv)
    db = args.db or gitskills_db_path()
    if not db.is_file():
        print(f"Sample database not found at {db}. Run `make data` first.", file=sys.stderr)
        return 1
    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    try:
        text = render(run_checks(con), db)
    finally:
        con.close()
    if args.stdout:
        print(text)
    else:
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

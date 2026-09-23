#!/usr/bin/env python
"""Run the acceptance tests in RESEARCH_SPEC.md and report each requirement's result.

Every requirement in RESEARCH_SPEC.md (a "### RR-01 ..." heading with a table that has
a Status row) must have an entry in CHECKS below. Results:

- PASS      the acceptance test passed
- PARTIAL   the implemented part passes; a part the spec marks In progress is not done yet
- FAIL      it failed
- PENDING   the requirement is Planned and its test does not pass yet
- BLOCKED   the test needs something the team does not have yet (for example second-rater labels)
- MANUAL    the acceptance test is a human check; the evidence column says what to record

The script exits 1 if a requirement whose spec status is Implemented fails, or if a
requirement has no check. It writes results/spec_verification.csv and prints a table.
It only reads the dataset (read-only SQLite) and never runs anything found in it.

Usage:
    python scripts/verify_spec.py                  # every check except the slow ones
    python scripts/verify_spec.py --determinism    # also NFR-02: two full analyses, ~8 min
    python scripts/verify_spec.py --only DR-01 ER-02
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import sqlite3
import subprocess
import sys
import tempfile
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from msr_pipeline.config import get_paths, gitskills_db_path  # noqa: E402

SPEC = ROOT / "RESEARCH_SPEC.md"
RESULTS = ROOT / "results"
OUT = RESULTS / "spec_verification.csv"
Result = tuple[str, str]  # (PASS | FAIL | BLOCKED | MANUAL, evidence)


# --- helpers ---------------------------------------------------------------------------


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def manifest() -> dict:
    return json.loads((RESULTS / "ANALYSIS_MANIFEST.json").read_text(encoding="utf-8"))


def db() -> sqlite3.Connection | None:
    path = gitskills_db_path()
    return sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True) if path.is_file() else None


def pytest(*node_ids: str) -> Result:
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *node_ids]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    last = (proc.stdout.strip().splitlines() or ["no output"])[-1]
    return ("PASS" if proc.returncode == 0 else "FAIL", f"pytest {' '.join(node_ids)}: {last}")


def parse_spec(text: str) -> list[dict[str, str]]:
    """Requirements from RESEARCH_SPEC.md: id, title, and every table row of the block."""
    reqs: list[dict[str, str]] = []
    for block in re.split(r"^### ", text, flags=re.M)[1:]:
        head = block.splitlines()[0]
        match = re.match(r"((?:RR|DR|FR|NFR|VR|ER)-\d{2})\b\s*(.*)", head)
        if not match:
            continue
        req = {"id": match.group(1), "title": match.group(2).strip(" .")}
        for row in re.findall(r"^\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|\s*$", block, flags=re.M):
            req[row[0].strip("* ").lower()] = row[1]
        reqs.append(req)
    return reqs


def dictionary_columns() -> dict[str, set[str]]:
    """File -> documented columns, from DATA_DICTIONARY.md Part C (P-01 analysis tables)."""
    text = (ROOT / "DATA_DICTIONARY.md").read_text(encoding="utf-8")
    section = text.split("### P-01 research analysis tables", 1)[1].split("Figures:", 1)[0]
    cols: dict[str, set[str]] = {}
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and cells[0].startswith("`") and cells[0].endswith(".csv`"):
            same = re.match(r"same as `([^`]+\.csv)`", cells[2])
            if same:  # "same as `other.csv`"
                cols[cells[0].strip("`")] = set(cols.get(same.group(1), set()))
                continue
            listed = re.sub(r"\([^)]*\)", "", cells[2])  # parentheses hold notes, not columns
            cols[cells[0].strip("`")] = set(re.findall(r"`([^`]+)`", listed))
    return cols


# --- research requirements ---------------------------------------------------------------


def rr_01() -> Result:
    flow = {r["step"]: r for r in read_csv("population_flow.csv")}
    first = flow["all_occurrences"]
    con = db()
    if con is None:
        return ("BLOCKED", "sample database not downloaded (make data)")
    occ, shas = con.execute("SELECT COUNT(*), COUNT(DISTINCT file_sha) FROM artifacts").fetchone()
    ok = int(first["distinct_contents"]) == shas and int(first["occurrences"]) == occ
    return (
        "PASS" if ok else "FAIL",
        f"population_flow first step {first['distinct_contents']} contents / "
        f"{first['occurrences']} occurrences; database {shas} / {occ}",
    )


def rr_02() -> Result:
    mwu = {r["outcome"]: r for r in read_csv("rq2_mannwhitney.csv")}
    nb = read_csv("rq2_negbin.csv")
    problems = [
        o
        for o in ("copies", "repos")
        if o not in mwu
        or not (
            int(float(mwu[o]["n_group"])) > 0
            and int(float(mwu[o]["n_reference"])) > 0
            and mwu[o]["p_value"]
        )
    ]
    has_term = any(r["term"] == "high_risk" and r["irr"] for r in nb) or any(
        r.get("status") == "not estimable" for r in nb
    )
    draft = (ROOT / "report" / "draft.md").read_text(encoding="utf-8")
    use_claims = re.findall(
        r"\b(?:used more|more (?:widely |often )?used|more heavily used)\b", draft, flags=re.I
    )
    ok = not problems and has_term and not use_claims
    return (
        "PASS" if ok else "FAIL",
        f"Mann-Whitney rows for copies and repos: {'ok' if not problems else problems}; "
        f"NB2 high_risk term: {'ok' if has_term else 'missing'}; "
        f"'used more' claims in report/draft.md: {len(use_claims)}",
    )


def rr_03() -> Result:
    sweep = read_csv("rq3_threshold_sweep.csv")
    thresholds = sorted(float(r["threshold"]) for r in sweep)
    summary = read_csv("rq3_summary.csv")
    ok = (
        thresholds[0] <= 0.3
        and thresholds[-1] >= 0.8
        and "ordered_pairs" in sweep[0]
        and len(summary) == 2
    )
    by_location = "ordered_pairs_canonical" in sweep[0]
    note = "" if by_location else "; ordered pairs by location class not reported yet (NB-Q06)"
    if not ok:
        return ("FAIL", f"thresholds {thresholds}; summary rows {len(summary)}")
    return (
        "PASS" if by_location else "PARTIAL",
        f"sweep {thresholds[0]} to {thresholds[-1]} with ordered_pairs; "
        f"{len(summary)} summary scopes{note}",
    )


def rr_04() -> Result:
    scenarios = [r["scenario"] for r in read_csv("sensitivity_summary.csv")]
    return (
        "PASS" if len(scenarios) >= 6 else "FAIL",
        f"{len(scenarios)} scenarios: " + ", ".join(scenarios),
    )


# --- data requirements ---------------------------------------------------------------------


def dr_01() -> Result:
    m = manifest()
    rules = ROOT / "rules" / "skill_risk_rules.yaml"
    notes = []
    rules_ok = sha256(rules) == m["rules_file_sha256"]
    notes.append(
        "rule file hash matches the last analysis run"
        if rules_ok
        else "rule file changed since the last analysis run; re-run make pipeline"
    )
    sample_manifest = ROOT / "data" / "samples" / "MANIFEST.json"
    db_path = gitskills_db_path()
    if not db_path.is_file() or not sample_manifest.is_file():
        return (
            "BLOCKED",
            "sample database or data/samples/MANIFEST.json missing (make data); " + notes[0],
        )
    entries = json.loads(sample_manifest.read_text(encoding="utf-8"))["files"]
    db_entry = next(e for e in entries if e["file"].replace("\\", "/").endswith(db_path.name))
    db_ok = sha256(db_path) == db_entry["sha256"] == m["gitskills_db_sha256_from_manifest"]
    commit_ok = db_entry.get("upstream_commit", "").startswith("fff3df9")
    notes.append(f"database SHA-256 {'matches' if db_ok else 'DOES NOT match'} both manifests")
    notes.append(f"sample commit {db_entry.get('upstream_commit', '?')[:7]}")
    readme = re.sub(
        r"\s+", " ", (ROOT / "data" / "README.md").read_text(encoding="utf-8").replace("\n>", "\n")
    )
    specmine_label_ok = "22102779 (SpecMine v1.1)" not in readme
    notes.append(
        "data/README.md SpecMine version label "
        + ("ok" if specmine_label_ok else "still says v1.1 for the Zenodo release")
    )
    ok = rules_ok and db_ok and commit_ok and specmine_label_ok
    return ("PASS" if ok else "FAIL", "; ".join(notes))


def dr_02() -> Result:
    dictionary = (ROOT / "DATA_DICTIONARY.md").read_text(encoding="utf-8")
    files = sorted(p.name for p in RESULTS.glob("*.csv"))
    missing = [f for f in files if f"`{f}`" not in dictionary]
    return (
        "PASS" if not missing else "FAIL",
        f"{len(files) - len(missing)} of {len(files)} results files documented"
        + (f"; undocumented: {', '.join(missing)}" if missing else ""),
    )


def dr_03() -> Result:
    flow = read_csv("population_flow.csv")
    kept = [int(r["distinct_contents"]) for r in flow if not r["step"].startswith("excluded")]
    main = next(int(r["distinct_contents"]) for r in flow if r["step"] == "main_population")
    ok = kept == sorted(kept, reverse=True) and main == manifest()["row_counts"]["main_population"]
    return ("PASS" if ok else "FAIL", f"steps {[r['step'] for r in flow]}; main population {main}")


def dr_04() -> Result:
    scripts = {r["metric"]: r["value"] for r in read_csv("scripts_summary.csv")}
    steps = {r["step"] for r in read_csv("population_flow.csv")}
    need = [
        "script_files_without_text",
        "skills_with_truncated_listing",
        "skills_without_folder_listing",
        "skills_with_unrecovered_content",
        "script_files_with_text_excluding_truncated_listing",
        "skills_with_high_risk_script_excluding_truncated_listing",
    ]
    missing = [m for m in need if m not in scripts]
    if "excluded_unrecovered_content" not in steps:
        missing.append("population_flow step excluded_unrecovered_content")
    if missing:
        return ("FAIL", f"scripts_summary.csv lacks unreadable-input counts: {', '.join(missing)}")
    return (
        "PASS",
        ", ".join(f"{m} {scripts[m]}" for m in need[:4])
        + "; script results also reported without truncated listings",
    )


# --- functional requirements ----------------------------------------------------------------


def fr_03() -> Result:
    expected = dictionary_columns()
    outputs = manifest()["outputs"]
    problems = []
    for name in outputs:
        path = RESULTS / name if name.endswith(".csv") else ROOT / "figures" / name
        if not path.is_file() or path.stat().st_size == 0:
            problems.append(f"{name} missing or empty")
            continue
        if name.endswith(".csv"):
            with path.open(encoding="utf-8", newline="") as handle:
                header = set(next(csv.reader(handle)))
            if name not in expected:
                problems.append(f"{name} not in DATA_DICTIONARY Part C")
            elif header != expected[name]:
                extra, gone = sorted(header - expected[name]), sorted(expected[name] - header)
                problems.append(f"{name} columns differ (extra {extra}, missing {gone})")
    return (
        "PASS" if not problems else "FAIL",
        f"{len(outputs)} outputs checked against DATA_DICTIONARY Part C"
        + (": " + "; ".join(problems) if problems else ": all present, non-empty, columns match"),
    )


def fr_04() -> Result:
    status, evidence = pytest("tests/test_skill_risk.py::test_scan_siblings_only_scripts")
    scanned = {r["metric"]: r["value"] for r in read_csv("scripts_summary.csv")}
    n = int(scanned.get("script_files_with_text", 0))
    ok = status == "PASS" and n > 0
    return ("PASS" if ok else "FAIL", f"{evidence}; script files scanned {n}")


# --- nonfunctional requirements -------------------------------------------------------------


def nfr_01() -> Result:
    from importlib.metadata import PackageNotFoundError, version

    from packaging.requirements import Requirement
    from packaging.version import Version

    versions = manifest()["versions"]
    problems = []
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        req = Requirement(line)
        used, where = versions.get(req.name.lower()), "recorded for the committed results"
        if (
            not used
        ):  # not in the analysis manifest: compare with this environment (as CI builds it)
            try:
                used, where = version(req.name), "installed by `pip install -e .[dev]`"
            except PackageNotFoundError:
                continue
        if not req.specifier.contains(Version(used), prereleases=True):
            problems.append(f"requirements.txt `{line}` excludes {req.name} {used} ({where})")
    if Version(versions["python"]) < Version("3.11"):
        problems.append("Python below 3.11")
    evidence = (
        "declared versions admit the recorded environment" if not problems else "; ".join(problems)
    )
    return (
        "PASS" if not problems else "FAIL",
        evidence + ". Fresh-clone run by a non-author is recorded at sprint review (S1-10)",
    )


def nfr_02(run: bool) -> Result:
    if not run:
        return ("MANUAL", "run `python scripts/verify_spec.py --determinism` (two full analyses)")
    from msr_pipeline import analysis
    from msr_pipeline.config import Paths

    base = get_paths()
    hashes = []
    with tempfile.TemporaryDirectory() as tmp:
        for i in (1, 2):
            out = Path(tmp) / f"run{i}"
            paths = Paths(
                ROOT=base.ROOT,
                DATA=base.DATA,
                SAMPLES=base.SAMPLES,
                RESULTS=out / "results",
                FIGURES=out / "figures",
            )
            analysis.run_analysis(gitskills_db_path(base), paths=paths)
            hashes.append({p.name: sha256(p) for p in (out / "results").glob("*.csv")})
    same = hashes[0] == hashes[1]
    committed = {n: sha256(RESULTS / n) for n in hashes[0] if (RESULTS / n).is_file()}
    stale = sorted(n for n, h in committed.items() if h != hashes[0][n])
    return (
        "PASS" if same else "FAIL",
        f"two runs {'identical' if same else 'DIFFER'} across {len(hashes[0])} CSV files; "
        + (
            f"committed results differ from a fresh run: {', '.join(stale)}"
            if stale
            else "committed results equal a fresh run"
        ),
    )


def nfr_04() -> Result:
    seconds = manifest()["runtime_seconds"]
    return (
        "PASS" if seconds < 900 else "FAIL",
        f"last analysis run took {seconds:.0f} s (limit 900 s)",
    )


# --- validation requirements ------------------------------------------------------------------


def labels(kind: str, raters: tuple[str, ...]) -> list[Path]:
    """Label files for ``kind`` by any of ``raters`` that contain at least one label."""
    found = []
    for rater in raters:
        path = ROOT / "data" / "annotations" / f"{kind}_{rater}_r1.csv"
        if path.is_file():
            with path.open(encoding="utf-8", newline="") as handle:
                if any(row.get("label") for row in csv.DictReader(handle)):
                    found.append(path)
    return found


def vr_01() -> Result:
    sample = json.loads(
        (ROOT / "data" / "annotations" / "samples" / "SAMPLE_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    design = sample.get("seed") == 580 and sample["sizes"]["signals_items"] > 0
    if not design:
        return ("FAIL", "validation sample missing or not seeded")
    if not labels("signals", ("jd",)):
        return (
            "BLOCKED",
            f"stratified sample of {sample['sizes']['signals_items']} signal items "
            "(seed 580) ready; primary-rater labels stay uncommitted under the blindness "
            "rule until a second rater's labels are merged (#53)",
        )
    return pytest("tests/test_validation.py::test_precision_by_rule_and_category")


def vr_02() -> Result:
    second = {k: labels(k, ("la", "ah", "hk")) for k in ("signals", "lineage", "drift")}
    missing = [k for k, files in second.items() if not files]
    if missing:
        return (
            "BLOCKED",
            f"no teammate labels yet for {', '.join(missing)} (issue #53; "
            "due 2026-10-16). Kappa code tested: "
            + pytest("tests/test_validation.py::test_cohen_kappa_textbook_example")[0],
        )
    return pytest("tests/test_validation.py::test_agreement_classifies_comparisons")


def vr_03() -> Result:
    have = [k for k in ("lineage", "drift") if labels(k, ("la", "ah", "hk"))]
    if len(have) < 2:
        return (
            "BLOCKED",
            "lineage (58 pairs) and drift (18 pairs) samples ready; second-rater "
            "labels not yet available (#53)",
        )
    return pytest("tests/test_validation.py::test_lineage_and_drift_summaries")


def vr_04() -> Result:
    """Each interview record answers every prepared question in the five columns the
    assignment requires, and gives each answer a verification result."""
    import yaml

    asked = [
        q["id"]
        for q in yaml.safe_load(
            (ROOT / "elicitation" / "questions.yaml").read_text(encoding="utf-8")
        )["questions"]
    ]
    parts, problems = [], []
    for name in ("google-notebook-interview.md", "notebook-interview.md"):
        record = (ROOT / "elicitation" / name).read_text(encoding="utf-8")
        header = "| Question | Notebook answer | Source cited by notebook | Team interpretation "
        if header + "| Follow-up or uncertainty |" not in record:
            problems.append(f"{name}: the interview table is missing the required headers")
        rows = set(re.findall(r"^\| \*\*(NB-Q\d+a?)\*\*", record, flags=re.M))
        statuses = dict(
            re.findall(
                r"^\| (NB-Q\d+a?) \| \*\*(Verified|Partly verified|Unverified|Contradicted)",
                record,
                flags=re.M,
            )
        )
        if missing := [q for q in asked if q not in rows]:
            problems.append(f"{name}: no interview row for {', '.join(missing)}")
        if unrated := [q for q in asked if q not in statuses]:
            problems.append(f"{name}: no verification result for {', '.join(unrated)}")
        counts = {s: sum(1 for v in statuses.values() if v == s) for s in set(statuses.values())}
        parts.append(
            f"{name.removesuffix('-interview.md')}: {len(rows)} answers ("
            + ", ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda kv: str(kv[0])))
            + ")"
        )
    return ("PASS" if not problems else "FAIL", "; ".join(parts + problems))


# --- ethical and safety requirements ----------------------------------------------------------


def er_02() -> Result:
    con = db()
    if con is None:
        return ("BLOCKED", "sample database not downloaded (make data)")
    repos = {r.lower() for (r,) in con.execute("SELECT full_name FROM repos")}
    codes = {
        c
        for (c,) in con.execute(
            "SELECT first_commit_author FROM artifacts WHERE first_commit_author_type <> 'Bot' "
            "UNION SELECT last_commit_author FROM artifacts WHERE last_commit_author_type <> 'Bot'"
        )
        if c
    }
    bots = {
        c.lower()
        for (c,) in con.execute(
            "SELECT first_commit_author FROM artifacts WHERE first_commit_author_type = 'Bot' "
            "UNION SELECT last_commit_author FROM artifacts WHERE last_commit_author_type = 'Bot'"
        )
        if c
    }
    # Repositories the project cites as sources (dataset and tool repositories), not mined data.
    allowed = {
        "giuseppedestefanis/gitskills-sample",
        "shyamagarwal13/specmine-official",
        "jeraddunne/csc580-group9-msr2027",
        "anthropics/skills",
    }
    targets = [
        *RESULTS.glob("*.csv"),
        ROOT / "elicitation" / "verification-checks.md",
        ROOT / "report" / "draft.md",
    ]
    pair = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9._-]{1,100}")
    word = re.compile(r"[A-Za-z0-9_\[\]-]{7,40}")
    hits: dict[str, int] = {}
    for path in targets:
        if not path.is_file() or path.name == OUT.name:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        n = sum(1 for m in pair.findall(text) if m.lower() in repos and m.lower() not in allowed)
        n += sum(1 for m in word.findall(text) if m in codes or m.lower() in bots)
        if n:
            hits[path.name] = n
    return (
        "PASS" if not hits else "FAIL",
        f"scanned {len(targets)} files for {len(repos):,} repository names, {len(codes):,} "
        f"author codes, and {len(bots)} bot logins: "
        + ("no matches" if not hits else ", ".join(f"{f} {n}" for f, n in hits.items())),
    )


FORBIDDEN = {
    "eval",
    "exec",
    "compile",
    "__import__",
    "os.system",
    "os.popen",
    "os.exec",
    "subprocess.run",
    "subprocess.call",
    "subprocess.Popen",
    "subprocess.check_call",
    "subprocess.check_output",
    "importlib.import_module",
    "runpy.run_path",
    "runpy.run_module",
    "pickle.load",
    "pickle.loads",
    "marshal.loads",
}
# Calls that are allowed because they never receive dataset content.
ALLOWED = {
    ("scripts/build_notebook_sources.py", "subprocess.run"): "fixed `git rev-parse` "
    "and `git status` arguments",
    ("scripts/verify_spec.py", "subprocess.run"): "runs this repository's own pytest",
}


def er_03() -> Result:
    files = [
        *sorted((ROOT / "src" / "msr_pipeline").glob("*.py")),
        *(
            ROOT / "scripts" / n
            for n in (
                "download_samples.py",
                "annotation_kit.py",
                "check_interview_claims.py",
                "build_notebook_sources.py",
                "verify_spec.py",
            )
        ),
    ]
    found, allowed = [], []
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = (
                func.id
                if isinstance(func, ast.Name)
                else f"{func.value.id}.{func.attr}"
                if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name)
                else ""
            )
            if name in FORBIDDEN or name.startswith("os.exec"):
                (allowed if (rel, name) in ALLOWED else found).append(f"{rel}:{node.lineno} {name}")
    return (
        "PASS" if not found else "FAIL",
        f"{len(files)} files that read the dataset scanned for code-execution calls: "
        + (", ".join(found) if found else "none")
        + (
            f"; allowed: {len(allowed)} ({'; '.join(sorted({ALLOWED[k] for k in ALLOWED}))})"
            if allowed
            else ""
        ),
    )


def er_05() -> Result:
    log = (ROOT / "ai-use-log.md").read_text(encoding="utf-8")
    ok = bool(re.search(r"^\| 2026-09-18 \|.*elicitation", log, flags=re.M))
    return (
        "PASS" if ok else "FAIL",
        "ai-use-log.md "
        + ("has" if ok else "lacks")
        + " the 2026-09-18 entry for the elicitation notebook and this specification",
    )


def manual(what: str) -> Callable[[], Result]:
    return lambda: ("MANUAL", what)


def checks(determinism: bool) -> dict[str, Callable[[], Result]]:
    return {
        "RR-01": rr_01,
        "RR-02": rr_02,
        "RR-03": rr_03,
        "RR-04": rr_04,
        "DR-01": dr_01,
        "DR-02": dr_02,
        "DR-03": dr_03,
        "DR-04": dr_04,
        "FR-01": lambda: pytest(
            "tests/test_load.py::test_query_gitskills",
            "tests/test_load.py::test_missing_gitskills_raises_helpful_error",
        ),
        "FR-02": lambda: pytest(
            "tests/test_skill_risk.py::test_rule_examples",
            "tests/test_skill_risk.py::test_rule_file_is_consistent",
        ),
        "FR-03": fr_03,
        "FR-04": fr_04,
        "FR-05": lambda: pytest(
            "tests/test_validation.py::test_kit_end_to_end",
            "tests/test_validation.py::test_precision_by_rule_and_category",
            "tests/test_validation.py::test_cohen_kappa_textbook_example",
        ),
        "FR-06": lambda: pytest(
            "tests/test_skill_risk.py::test_family_pairs_direction_and_threshold",
            "tests/test_analysis.py::test_threshold_sweep_is_monotone_and_counts_direction",
        ),
        "FR-07": lambda: pytest(
            "tests/test_elicitation.py::test_scopes_restrict_tiers_and_datasets",
            "tests/test_elicitation.py::test_transcript_has_provenance_and_locators",
            "tests/test_elicitation.py::test_interview_record_quotes_every_question_word_for_word",
        ),
        "NFR-01": nfr_01,
        "NFR-02": lambda: nfr_02(determinism),
        "NFR-03": lambda: pytest("tests"),
        "NFR-04": nfr_04,
        "NFR-05": manual(
            "each merged pull request that edits RESEARCH_SPEC.md, rules, or the "
            "research question links a decision issue; checked at sprint review"
        ),
        "VR-01": vr_01,
        "VR-02": vr_02,
        "VR-03": vr_03,
        "VR-04": vr_04,
        "ER-01": manual(
            "reviewer confirms every quoted skill excerpt in the report is short, "
            "needed, non-runnable, and from a permissively licensed repository"
        ),
        "ER-02": er_02,
        "ER-03": er_03,
        "ER-04": manual(
            "no suspected actively malicious skill found; if one is, stop and raise "
            "it with the instructor before any further step (THREATS X4)"
        ),
        "ER-05": er_05,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--determinism", action="store_true", help="Also run NFR-02 (slow).")
    parser.add_argument("--only", nargs="*", help="Check only these requirement IDs.")
    parser.add_argument("--no-write", action="store_true", help=f"Do not write {OUT.name}.")
    args = parser.parse_args(argv)

    reqs = parse_spec(SPEC.read_text(encoding="utf-8"))
    table = checks(args.determinism)
    rows, failed = [], []
    for req in reqs:
        rid = req["id"]
        if args.only and rid not in args.only:
            continue
        spec_status = req.get("status", "").split()[0].strip("*.,") if req.get("status") else ""
        if rid not in table:
            result, evidence = "FAIL", "no acceptance check registered in scripts/verify_spec.py"
        else:
            try:
                result, evidence = table[rid]()
            except (OSError, KeyError, ValueError, StopIteration, sqlite3.Error) as exc:
                result, evidence = "FAIL", f"check raised {exc.__class__.__name__}: {exc}"
        if result == "FAIL" and spec_status == "Planned":
            result = "PENDING"
        if result == "FAIL":
            failed.append(rid)
        rows.append(
            {
                "requirement": rid,
                "title": req["title"],
                "spec_status": spec_status,
                "result": result,
                "evidence": evidence,
            }
        )

    width = max(len(r["title"]) for r in rows) if rows else 10
    for r in rows:
        print(f"{r['requirement']:<7} {r['result']:<8} {r['title'][:width]}")
        print(f"        {r['evidence']}")
    summary = {
        s: sum(1 for r in rows if r["result"] == s)
        for s in ("PASS", "PARTIAL", "FAIL", "PENDING", "BLOCKED", "MANUAL")
    }
    print("\n" + ", ".join(f"{k} {v}" for k, v in summary.items() if v))

    if not args.no_write and not args.only:
        stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        with OUT.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=[*rows[0], "checked_at"])
            writer.writeheader()
            writer.writerows({**r, "checked_at": stamp} for r in rows)
        print(f"wrote {OUT}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

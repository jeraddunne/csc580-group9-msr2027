"""Tests for scripts/ground_truth_check.py: ids, the selection table, detection, blindness."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import sqlite3
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _gt():
    spec = importlib.util.spec_from_file_location(
        "ground_truth_check", ROOT / "scripts" / "ground_truth_check.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SKILLS = [
    # repo, path, file_sha, SKILL.md text, expected category
    ("o/net", "skills/a/SKILL.md", "sha-net", "Run `curl https://api.example.com/v1`.", "NETWORK"),
    ("o/per", "skills/b/SKILL.md", "sha-per", "Add a crontab entry for the job.", "PERSISTENCE"),
    ("o/crd", "skills/c/SKILL.md", "sha-crd", "Read the user's keychain first.", "CREDENTIALS"),
    ("o/prv", "skills/d/SKILL.md", "sha-prv", "Run the bundled installer.", "PRIVILEGE"),
]


def _id(repo: str, path: str) -> str:
    return hashlib.sha256(f"{repo}\n{path}".encode()).hexdigest()[:16]


def _fixture(tmp_path: Path) -> dict:
    db = tmp_path / "sample.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE artifacts (repo_full_name, path, filename, file_sha, content)")
    con.execute(
        "CREATE TABLE artifact_siblings (repo_full_name, artifact_path, entry_name, content)"
    )
    for repo, path, sha, text, _ in SKILLS:
        con.execute(
            "INSERT INTO artifacts VALUES (?, ?, 'SKILL.md', ?, ?)", (repo, path, sha, text)
        )
    con.execute(
        "INSERT INTO artifact_siblings VALUES ('o/prv', 'skills/d/SKILL.md', 'install.sh', ?)",
        ("sudo apt-get install jq\n",),
    )
    con.execute(
        "INSERT INTO artifact_siblings VALUES ('o/prv', 'skills/d/SKILL.md', 'notes.md', ?)",
        ("sudo is mentioned in prose only\n",),
    )
    con.commit()
    con.close()

    lines = [
        "# Selection",
        "",
        "| ID | Skill path | Expected category | Evidence |",
        "|---|---|---|---|",
    ]
    for repo, path, _, _, cat in SKILLS:
        lines.append(f"| {_id(repo, path)} | `{path}` | {cat} | line 1 |")
    lines.append(
        "| 0123456789abcdef | `skills/missing/SKILL.md` | OBFUSCATION | not in the sample |"
    )
    selection = tmp_path / "selection.md"
    selection.write_text("\n".join(lines) + "\n", encoding="utf-8")

    samples = tmp_path / "samples"
    samples.mkdir()
    (samples / "signals_sample.csv").write_text("file_sha,stratum\nsha-other,NETWORK\n")
    return {"db": db, "selection": selection, "samples": samples, "out": tmp_path / "results"}


def _args(f: dict, *extra: str) -> list[str]:
    return [
        "--db", str(f["db"]),
        "--selection", str(f["selection"]),
        "--samples", str(f["samples"]),
        "--out", str(f["out"]),
        *extra,
    ]  # fmt: skip


def _rows(path: Path) -> dict[str, dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {r["skill_path"]: r for r in csv.DictReader(handle)}


def test_candidate_id_is_the_documented_hash():
    gt = _gt()
    expected = hashlib.sha256(b"owner/repo\nskills/x/SKILL.md").hexdigest()[:16]
    assert gt.candidate_id("owner/repo", "skills/x/SKILL.md") == expected


def test_selection_table_rows_are_read_and_other_lines_ignored(tmp_path):
    gt = _gt()
    f = _fixture(tmp_path)
    rows = gt.read_selection(f["selection"])
    assert len(rows) == 5
    assert rows[0] == {
        "candidate_id": _id("o/net", "skills/a/SKILL.md"),
        "skill_path": "skills/a/SKILL.md",
        "expected_category": "NETWORK",
    }


def test_duplicate_candidate_ids_are_rejected(tmp_path):
    gt = _gt()
    page = tmp_path / "dup.md"
    row = "| 0123456789abcdef | `a/SKILL.md` | NETWORK | x |\n"
    page.write_text(row + row, encoding="utf-8")
    with pytest.raises(ValueError, match="twice"):
        gt.read_selection(page)


def test_detection_high_risk_scripts_and_misses(tmp_path):
    gt = _gt()
    f = _fixture(tmp_path)
    assert gt.main(_args(f)) == 0
    rows = _rows(f["out"] / "ground_truth_check.csv")

    net = rows["skills/a/SKILL.md"]  # R-NET-001 is severity 4: detected, not high risk
    assert (net["detected"], net["detected_high_risk"]) == ("True", "False")
    per = rows["skills/b/SKILL.md"]  # R-PER-001 is severity 7
    assert (per["detected"], per["detected_high_risk"]) == ("True", "True")
    crd = rows["skills/c/SKILL.md"]  # no rule matches the prose: a miss
    assert (crd["resolved"], crd["detected"]) == ("True", "False")
    prv = rows["skills/d/SKILL.md"]  # sudo only in a bundled .sh file; .md siblings are skipped
    assert (prv["detected"], prv["detected_in_scripts"], prv["scripts_scanned"]) == (
        "False",
        "True",
        "1",
    )
    missing = rows["skills/missing/SKILL.md"]
    assert (missing["resolved"], missing["detected"]) == ("False", "False")

    with (f["out"] / "ground_truth_summary.csv").open(encoding="utf-8", newline="") as handle:
        summary = {r["expected_category"]: r for r in csv.DictReader(handle)}
    total = summary["TOTAL"]
    assert (total["candidates"], total["resolved"], total["detected"]) == ("5", "4", "2")
    assert (total["detected_high_risk"], total["missed"]) == ("1", "2")


def test_outputs_hold_no_dataset_text(tmp_path):
    gt = _gt()
    f = _fixture(tmp_path)
    gt.main(_args(f))
    text = (f["out"] / "ground_truth_check.csv").read_text(encoding="utf-8")
    for _, _, _, skill_text, _ in SKILLS:
        assert skill_text not in text
    assert "sha-" not in text  # content hashes are left out too


def test_overlap_with_a_validation_sample_stops_without_naming_it(tmp_path, capsys):
    gt = _gt()
    f = _fixture(tmp_path)
    (f["samples"] / "drift_sample.csv").write_text("file_sha_a,file_sha_b\nsha-per,sha-zzz\n")
    assert gt.main(_args(f)) == 3
    out = capsys.readouterr().out
    assert "1 candidate(s)" in out
    assert _id("o/per", "skills/b/SKILL.md") not in out
    assert not (f["out"] / "ground_truth_check.csv").exists()

    assert gt.main(_args(f, "--list-overlap")) == 0
    assert _id("o/per", "skills/b/SKILL.md") in capsys.readouterr().out


def test_dry_run_writes_nothing(tmp_path, capsys):
    gt = _gt()
    f = _fixture(tmp_path)
    assert gt.main(_args(f, "--dry-run")) == 0
    assert "5 candidates, 4 found in the sample, 2 detected" in capsys.readouterr().out
    assert not f["out"].exists()

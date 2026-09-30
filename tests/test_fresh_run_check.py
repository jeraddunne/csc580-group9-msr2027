"""Tests for scripts/fresh_run_check.py: comparison, row counts, and reading the commit id."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _check():
    spec = importlib.util.spec_from_file_location(
        "fresh_run_check", ROOT / "scripts" / "fresh_run_check.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_line_endings_do_not_count_as_a_difference(tmp_path):
    frc = _check()
    committed, fresh = tmp_path / "committed", tmp_path / "fresh"
    committed.mkdir()
    fresh.mkdir()
    (committed / "a.csv").write_bytes(b"x,y\n1,2\n3,4\n")
    (fresh / "a.csv").write_bytes(b"x,y\r\n1,2\r\n3,4\r\n")
    (committed / "b.csv").write_bytes(b"x\n1\n")
    (fresh / "b.csv").write_bytes(b"x\n2\n")
    (fresh / "c.csv").write_bytes(b"x\n")

    rows = {r["file"]: r for r in frc.compare(committed, fresh)}

    assert rows["a.csv"]["same"] and rows["a.csv"]["status"] == "identical"
    assert rows["a.csv"]["rows_committed"] == rows["a.csv"]["rows_fresh"] == 2
    assert not rows["b.csv"]["same"] and rows["b.csv"]["status"] == "DIFFERS"
    assert rows["c.csv"]["status"] == "missing from results/"
    assert rows["c.csv"]["rows_committed"] is None


def test_quoted_newlines_count_as_one_row(tmp_path):
    frc = _check()
    path = tmp_path / "q.csv"
    path.write_text('a,b\n"line one\nline two",2\n', encoding="utf-8")
    assert frc.count_rows(path) == 1


def test_summary_numbers_read_the_headline_counts(tmp_path):
    frc = _check()
    (tmp_path / "population_flow.csv").write_text(
        "step,description,distinct_contents,occurrences\n"
        "all_occurrences,x,13000,29786\nmain_population,x,12965,29679\n",
        encoding="utf-8",
    )
    (tmp_path / "rq2_reach_summary.csv").write_text(
        "group,contents\nhigh-risk signal,1159\nno high-risk signal,11806\n", encoding="utf-8"
    )
    assert frc.summary_numbers(tmp_path) == {"main_population": 12965, "high_risk": 1159}


def test_commit_id_from_loose_packed_and_missing_refs(tmp_path):
    frc = _check()
    assert frc.commit_id(tmp_path) is None  # a ZIP download has no .git

    git = tmp_path / ".git"
    (git / "refs" / "heads").mkdir(parents=True)
    (git / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (git / "packed-refs").write_text(
        "# pack-refs with: peeled fully-peeled sorted\n" + "b" * 40 + " refs/heads/main\n",
        encoding="utf-8",
    )
    assert frc.commit_id(tmp_path) == "b" * 12

    (git / "refs" / "heads" / "main").write_text("a" * 40 + "\n", encoding="utf-8")
    assert frc.commit_id(tmp_path) == "a" * 12

    (git / "HEAD").write_text("c" * 40 + "\n", encoding="utf-8")  # detached HEAD
    assert frc.commit_id(tmp_path) == "c" * 12

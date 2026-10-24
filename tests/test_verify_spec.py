"""Tests for scripts/verify_spec.py: finding committed label files for VR-01 to VR-03."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _spec(tmp_path: Path):
    spec = importlib.util.spec_from_file_location(
        "verify_spec", ROOT / "scripts" / "verify_spec.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = tmp_path
    (tmp_path / "data" / "annotations").mkdir(parents=True)
    return module


def _write(tmp_path: Path, name: str, text: str) -> None:
    (tmp_path / "data" / "annotations" / name).write_text(text, encoding="utf-8")


@pytest.mark.parametrize(
    ("kind", "header", "row"),
    [
        ("signals", "file_sha,rule_id,label,missed_category,notes", "s1,R-EXE-001,RISKY,,"),
        ("lineage", "file_sha_a,file_sha_b,same_lineage,notes", "a1,b1,YES,"),
        ("drift", "file_sha_a,file_sha_b,change_type,notes", "a1,b1,TEMPLATE_UPDATE,"),
    ],
)
def test_labels_reads_each_kinds_own_label_column(tmp_path, kind, header, row):
    vs = _spec(tmp_path)
    _write(tmp_path, f"{kind}_la_r1.csv", f"{header}\n{row}\n")
    assert [p.name for p in vs.labels(kind, ("la",))] == [f"{kind}_la_r1.csv"]


def test_vr_03_names_only_the_missing_second_rater(tmp_path):
    vs = _spec(tmp_path)
    _write(
        tmp_path, "drift_la_r1.csv", "file_sha_a,file_sha_b,change_type,notes\na1,b1,HARDENING,x\n"
    )
    result, evidence = vs.vr_03()
    assert result == "BLOCKED"
    assert "lineage labels by hk" in evidence
    assert "drift labels by la" not in evidence


def test_blank_sheets_and_missing_files_do_not_count(tmp_path):
    vs = _spec(tmp_path)
    _write(tmp_path, "drift_la_r1.csv", "file_sha_a,file_sha_b,change_type,notes\na1,b1,,\n")
    assert vs.labels("drift", ("la",)) == []
    assert vs.labels("lineage", ("hk",)) == []

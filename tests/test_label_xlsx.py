"""Tests for the Excel labelling workbook, the studio's work log, and their imports (offline)."""

from __future__ import annotations

import importlib.util
import json
import re
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

openpyxl = pytest.importorskip("openpyxl")

from msr_pipeline import label_ui, label_xlsx  # noqa: E402
from msr_pipeline import validation as v  # noqa: E402
from msr_pipeline.skill_risk import read_rule_file  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = re.compile(r"const DATA = (.*?);\nconst storeKey", re.S)
NOTE = "matched inside the identifier SUDO_USER, not a command"


def _kit():
    spec = importlib.util.spec_from_file_location(
        "annotation_kit", ROOT / "scripts" / "annotation_kit.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SIGNAL_PACKET = """# Signal item 001

> **Read only. Do not run anything in this excerpt.**

- file_sha: `s1`
- front-matter name: demo
- stratum: CREDENTIALS
- matched rules: R-CRD-001

## R-CRD-001 (CREDENTIALS, severity 8; label this rule)

Rule note: Credential file paths.

Line 3:

    =cat ~/.aws/credentials
"""
NONE_PACKET = """# Signal item 002

- file_sha: `s2`
- front-matter name: other
- stratum: NO_SIGNAL
- matched rules: none

No rule matched. Read the text and label NONE_PRESENT, or MISSED_RISKY with the missed category.

    ---
    name: other
    ---
    Say hello.
"""
PAIR_PACKET = """# Lineage pair 001

- file_sha_a: `a1`
- file_sha_b: `b1`
- front-matter names: x / x
- similarity: 0.589
- source: differing

Unified diff, a to b:

    --- a
    +++ b
    -old
    +new
"""


def _kinds() -> dict:
    signals = pd.DataFrame(
        {
            "file_sha": ["s1", "s2"],
            "rule_id": ["R-CRD-001", "NONE"],
            "label": ["", ""],
            "missed_category": ["", ""],
            "notes": ["", ""],
        }
    )
    pairs = {"file_sha_a": ["a1"], "file_sha_b": ["b1"], "notes": [""]}
    lineage = pd.DataFrame({**pairs, "same_lineage": [""]})[v.KIND_COLUMNS["lineage"]]
    drift = pd.DataFrame({**pairs, "change_type": [""]})[v.KIND_COLUMNS["drift"]]
    return {
        "signals": {
            "items": label_ui.build_items(
                "signals", signals, [("s1", SIGNAL_PACKET), ("s2", NONE_PACKET)]
            ),
            "packet_files": {"s1": "001_s1.md", "s2": "002_s2.md"},
            "packet_dir": "signals_zz_r1",
        },
        "lineage": {
            "items": label_ui.build_items("lineage", lineage, [("a1|b1", PAIR_PACKET)]),
            "packet_dir": "lineage_zz_r1",
        },
        "drift": {
            "items": label_ui.build_items("drift", drift, [("a1|b1", PAIR_PACKET)]),
            "packet_dir": "drift_zz_r1",
        },
    }


def _build(tmp_path: Path) -> Path:
    out = tmp_path / "labelling_zz_r1.xlsx"
    label_xlsx.build_workbook(
        out,
        "zz",
        1,
        _kinds(),
        label_ui.load_guideline(),
        read_rule_file(),
        sample_info={"population": {"no_signal_contents": 7540}},
    )
    return out


def _cols(ws, kind: str) -> dict[str, int]:
    head = {c.value: c.column for c in ws[1]}
    return {key: head[header] for key, header, _w, _r in label_xlsx.COLUMNS[kind]}


def test_excerpt_takes_the_rows_part_of_the_packet():
    assert label_xlsx.excerpt("signals", SIGNAL_PACKET, "R-CRD-001").startswith("Line 3:")
    assert "Rule note" not in label_xlsx.excerpt("signals", SIGNAL_PACKET, "R-CRD-001")
    assert label_xlsx.excerpt("signals", NONE_PACKET, "NONE").endswith("Say hello.")
    assert label_xlsx.excerpt("lineage", PAIR_PACKET).splitlines()[-1] == "+new"
    long = NONE_PACKET + "\n".join("    line" for _ in range(500))
    assert "cut here" in label_xlsx.excerpt("signals", long, "NONE")
    assert label_xlsx.packet_fields(PAIR_PACKET)["similarity"] == "0.589"


def test_workbook_has_the_guideline_lists_and_no_label_filled_in(tmp_path: Path):
    wb = openpyxl.load_workbook(_build(tmp_path))
    assert wb.sheetnames[:5] == ["Start here", "How to decide", "Signals", "Lineage", "Drift"]
    assert {"Metrics", "Assignment map", "Rules"} <= set(wb.sheetnames)
    assert wb["_meta"].sheet_state == "hidden" and wb["Lists"].sheet_state == "hidden"
    ws = wb["Signals"]
    c = _cols(ws, "signals")
    for row in (2, 3):
        for key in ("label", "missed_category", "notes", "why", "confidence", "date", "minutes"):
            assert ws.cell(row, c[key]).value is None, key
    # Dataset text that starts with "=" stays text, never a formula.
    excerpt = ws.cell(2, c["excerpt"])
    assert excerpt.data_type == "s" and "~/.aws/credentials" in excerpt.value
    assert ws.cell(2, c["packet"]).hyperlink.target == "signals_zz_r1/001_s1.md"
    # The label dropdown offers exactly the guideline's labels for each kind of row.
    lists = {cell.value: cell.column_letter for cell in wb["Lists"][1]}
    by_cell = {}
    for dv in ws.data_validations.dataValidation:
        for rng in dv.sqref.ranges:
            by_cell[rng.coord] = dv.formula1
    label = ws.cell(2, c["label"]).column_letter
    assert lists["rule_labels"] in by_cell[f"{label}2"]
    assert lists["none_labels"] in by_cell[f"{label}3"]
    assert ws.protection.sheet and not ws.cell(2, c["label"]).protection.locked
    assert ws.cell(2, c["file_sha"]).protection.locked
    start = " ".join(str(x.value) for x in wb["Start here"]["A"] if x.value)
    assert "Never run, paste, or open anything" in start
    assert "annotation_kit.py import data/annotations/work/labelling_zz_r1.xlsx" in start
    howto = " ".join(
        str(x.value) for row in wb["How to decide"].iter_rows() for x in row if x.value
    )
    assert "Is the matched text actually the capability?" in howto
    assert "VR-01" in " ".join(
        str(x.value) for row in wb["Assignment map"].iter_rows() for x in row if x.value
    )
    assert str(wb.defined_names["Z95"].attr_text) == "Metrics!$B$5"
    assert wb["Metrics"]["B5"].value == 1.96 and wb["Metrics"]["B6"].value == 7540


def test_status_formula_follows_the_reason_rules(tmp_path: Path):
    ws = openpyxl.load_workbook(_build(tmp_path))["Signals"]
    c = _cols(ws, "signals")
    status = ws.cell(2, c["status"]).value
    assert status.count("(") == status.count(")")
    assert '"needs a reason"' in status and '"invalid label"' in status
    assert f"<{v.MIN_JUSTIFICATION_CHARS}" in status
    none_status = ws.cell(3, c["status"]).value
    assert '"needs a category"' in none_status and 'EXACT(TRIM(J3),"NONE_PRESENT")' in none_status
    needs = ws.cell(2, c["reason_needed"]).value
    assert all(f'"{lab}"' in needs for lab in v.JUSTIFY_LABELS["signals"])


def test_read_workbook_returns_labels_and_work_log(tmp_path: Path):
    path = _build(tmp_path)
    wb = openpyxl.load_workbook(path)
    ws = wb["Signals"]
    c = _cols(ws, "signals")
    reasons = label_ui.reason_types(label_ui.load_guideline())
    ws.cell(2, c["label"]).value = "NOT_PRESENT"
    ws.cell(2, c["notes"]).value = NOTE
    ws.cell(2, c["why"]).value = reasons[0]["text"]
    ws.cell(2, c["confidence"]).value = "Leaning"
    ws.cell(2, c["date"]).value = date(2026, 10, 5)
    ws.cell(2, c["minutes"]).value = 2.5
    lw = wb["Lineage"]
    lw.cell(2, _cols(lw, "lineage")["label"]).value = "YES"
    wb.save(path)

    book = label_xlsx.read_workbook(path)
    assert (book["rater"], book["round"]) == ("zz", 1)
    sig = book["labels"]["signals"]
    assert list(sig.columns) == v.KIND_COLUMNS["signals"]
    assert sig.loc[0, "label"] == "NOT_PRESENT" and sig.loc[0, "notes"] == NOTE
    assert sig.loc[1, "label"] == "" and sig.loc[1, "rule_id"] == "NONE"
    assert book["labels"]["lineage"].loc[0, "same_lineage"] == "YES"
    log = book["worklog"]["signals"]
    assert list(log.columns) == label_ui.WORKLOG_COLUMNS
    assert log.loc[0, "reason_type"] == "Q1" and log.loc[0, "confidence"] == "Leaning"
    assert (
        log.loc[0, "first_labelled_at"] == "2026-10-05"
        and float(log.loc[0, "active_seconds"]) == 150
    )

    other = tmp_path / "other.xlsx"
    openpyxl.Workbook().save(other)
    with pytest.raises(ValueError):
        label_xlsx.read_workbook(other)


def test_worklog_import_checks_name_columns_and_owner(tmp_path: Path):
    work = tmp_path / "work"
    good = pd.DataFrame(
        [
            [
                "signals",
                "jd",
                "1",
                "1",
                "s1",
                "",
                "R-A",
                "2026-10-05T10:00:00Z",
                "",
                "0",
                "Sure",
                "Q1",
                "30",
            ]
        ],
        columns=label_ui.WORKLOG_COLUMNS,
    )
    src = tmp_path / "worklog_signals_jd_r1 (1).csv"
    good.to_csv(src, index=False)
    assert label_ui.is_worklog(src) and not label_ui.is_worklog(tmp_path / "signals_jd_r1.csv")
    target, problems, n = label_ui.import_worklog(src, work)
    assert problems == [] and n == 1 and target.name == "worklog_signals_jd_r1.csv"
    good.assign(rater="la").to_csv(src, index=False)
    assert "another kind, rater, or round" in label_ui.import_worklog(src, work)[1][0]
    good.drop(columns=["confidence"]).to_csv(src, index=False)
    assert "missing columns" in label_ui.import_worklog(src, work)[1][0]


def test_merge_worklog_keeps_page_values_the_workbook_left_empty():
    cols = label_ui.WORKLOG_COLUMNS
    row = dict.fromkeys(cols, "")
    row.update(kind="signals", rater="zz", round="1", key_a="s1", rule_id="R-A")
    new = pd.DataFrame([{**row, "confidence": "Sure"}], columns=cols)
    old = pd.DataFrame(
        [{**row, "confidence": "Unsure", "active_seconds": "42", "label_changes": "2"}],
        columns=cols,
    )
    merged = label_xlsx.merge_worklog(new, old)
    assert merged.loc[0, "confidence"] == "Sure"
    assert merged.loc[0, "active_seconds"] == "42" and merged.loc[0, "label_changes"] == "2"


def test_studio_carries_the_work_log_and_metrics_settings():
    guide = label_ui.load_guideline()
    items = _kinds()["signals"]["items"]
    page = label_ui.build_html(
        "signals",
        "zz",
        1,
        items,
        ["CREDENTIALS"],
        rules=[],
        guide=guide,
        sample_info={"population": {"no_signal_contents": 7540}},
    )
    data = json.loads(PAYLOAD.search(page).group(1))
    assert [t["id"] for t in data["reasonTypes"]] == ["Q1", "Q2", "Q3", "Q4", "S", "O"]
    assert all(set(t["labels"]) <= {"NOT_PRESENT", "BENIGN_CONTEXT"} for t in data["reasonTypes"])
    assert data["worklogFile"] == "worklog_signals_zz_r1.csv"
    assert data["worklogColumns"] == label_ui.WORKLOG_COLUMNS
    assert data["population"]["noSignal"] == 7540 and data["scoreDue"] == label_ui.SCORE_DUE
    assert data["assignmentUse"] == label_ui.ASSIGNMENT_USE["signals"]
    assert not any(r["label"] for i in data["items"] for r in i["rows"])
    for needle in (
        'id="metricsBtn"',
        'id="loadBtn"',
        'id="saveBanner"',
        "function openMetrics",
        "function loadLabels",
    ):
        assert needle in page
    lineage = label_ui.build_html("lineage", "zz", 1, _kinds()["lineage"]["items"], [], guide=guide)
    assert json.loads(PAYLOAD.search(lineage).group(1))["reasonTypes"] == []


def test_kit_xlsx_and_workbook_import_end_to_end(data_root: Path, tmp_path: Path):
    kit = _kit()
    ann = data_root / "data" / "annotations"
    assert kit.main(["sample", "--negatives", "5"]) == 0
    assert kit.main(["sheet", "--rater", "zz", "--round", "1"]) == 0
    assert kit.main(["xlsx", "--rater", "zz", "--round", "1"]) == 0
    book = ann / "work" / "labelling_zz_r1.xlsx"
    assert book.exists()
    assert kit.main(["xlsx", "--rater", "zz", "--round", "1"]) == 1  # never replaced silently

    wb = openpyxl.load_workbook(book)
    ws = wb["Signals"]
    c = _cols(ws, "signals")
    rows = range(2, ws.max_row + 1)
    for r in rows:
        none = ws.cell(r, c["rule_id"]).value == "NONE"
        ws.cell(r, c["label"]).value = "MISSED_RISKY" if none else "NOT_PRESENT"
    wb.save(book)
    assert kit.main(["import", str(book)]) == 1  # no reason and no missed category: refused
    assert not len(v.labelled_rows(v.read_label_csv(ann / "signals_zz_r1.csv"), "signals"))

    wb = openpyxl.load_workbook(book)
    ws = wb["Signals"]
    for r in rows:
        ws.cell(r, c["notes"]).value = NOTE
        if ws.cell(r, c["label"]).value == "MISSED_RISKY":
            ws.cell(r, c["missed_category"]).value = "REMOTE_CODE"
        ws.cell(r, c["confidence"]).value = "Sure"
    wb.save(book)
    assert kit.main(["xlsx", "--rater", "zz", "--round", "1", "--force"]) == 1  # not imported yet
    assert kit.main(["import", str(book)]) == 0
    saved = v.read_label_csv(ann / "signals_zz_r1.csv")
    assert len(v.labelled_rows(saved, "signals")) == len(saved)
    log = pd.read_csv(ann / "work" / "worklog_signals_zz_r1.csv", dtype=str, keep_default_na=False)
    assert (log["confidence"] == "Sure").all()
    assert kit.main(["xlsx", "--rater", "zz", "--round", "1", "--force"]) == 0
    rebuilt = openpyxl.load_workbook(book)["Signals"]
    assert rebuilt.cell(2, c["label"]).value in ("MISSED_RISKY", "NOT_PRESENT")
    assert rebuilt.cell(2, c["confidence"]).value == "Sure"

    page_log = tmp_path / "worklog_signals_zz_r1.csv"
    log.to_csv(page_log, index=False)
    assert kit.main(["import", str(page_log)]) == 0

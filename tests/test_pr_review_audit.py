"""Tests for scripts/pr_review_audit.py (Sprint 3 retrospective KPI, issue #35)."""

from __future__ import annotations

import importlib.util
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _audit():
    spec = importlib.util.spec_from_file_location(
        "pr_review_audit", ROOT / "scripts" / "pr_review_audit.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pr(number, author, created, merged, reviews=()):
    return {
        "number": number,
        "baseRefName": "main",
        "createdAt": created,
        "mergedAt": merged,
        "author": {"login": author},
        "reviews": {
            "nodes": [
                {"author": {"login": who}, "state": state, "submittedAt": when}
                for who, state, when in reviews
            ]
        },
    }


WINDOW = (("Sprint X", date(2026, 10, 8), date(2026, 10, 28)),)


def test_only_a_prior_approval_by_another_member_counts():
    m = _audit()
    prs = [
        _pr(
            1,
            "ana",
            "2026-10-09T12:00:00Z",
            "2026-10-09T18:00:00Z",
            [("bo", "APPROVED", "2026-10-09T15:00:00Z")],
        ),
        # self-approval does not count
        _pr(
            2,
            "ana",
            "2026-10-09T12:00:00Z",
            "2026-10-09T18:00:00Z",
            [("ana", "APPROVED", "2026-10-09T13:00:00Z")],
        ),
        # approval after the merge does not count
        _pr(
            3,
            "ana",
            "2026-10-09T12:00:00Z",
            "2026-10-09T18:00:00Z",
            [("bo", "APPROVED", "2026-10-09T19:00:00Z")],
        ),
        # a dismissed approval does not count
        _pr(
            4,
            "ana",
            "2026-10-09T12:00:00Z",
            "2026-10-09T18:00:00Z",
            [("bo", "DISMISSED", "2026-10-09T13:00:00Z")],
        ),
    ]
    row = m.audit(prs, WINDOW)[0]
    assert row["merged_prs"] == 4
    assert row["merged_without_nonauthor_approval"] == 3
    assert row["without_approval_prs"] == "#2 #3 #4"
    assert row["without_approval_share"] == "0.750"


def test_windows_use_eastern_time_and_bots_are_left_out_of_the_medians():
    m = _audit()
    prs = [
        # 2026-10-29 01:00 UTC is still Oct 28 in Eastern Time, so it belongs to the window
        _pr(
            5,
            "ana",
            "2026-10-28T20:00:00Z",
            "2026-10-29T01:00:00Z",
            [
                ("bo", "COMMENTED", "2026-10-28T22:00:00Z"),
                ("bo", "APPROVED", "2026-10-29T00:00:00Z"),
            ],
        ),
        # 2026-10-29 05:00 UTC is Oct 29 in Eastern Time: outside the window
        _pr(6, "ana", "2026-10-28T20:00:00Z", "2026-10-29T05:00:00Z"),
        _pr(
            7,
            "github-actions",
            "2026-10-10T00:00:00Z",
            "2026-10-11T00:00:00Z",
            [("bo", "APPROVED", "2026-10-10T12:00:00Z")],
        ),
    ]
    row = m.audit(prs, WINDOW)[0]
    assert row["merged_prs"] == 2
    assert row["bot_prs"] == 1
    assert row["member_prs"] == 1
    assert row["median_first_review_hours"] == "2.0"
    assert row["median_open_to_merge_hours"] == "5.0"


def test_offline_run_writes_the_csv(tmp_path):
    import json

    m = _audit()
    raw = tmp_path / "raw.json"
    raw.write_text(
        json.dumps(
            [
                _pr(8, "ana", "2026-09-20T12:00:00Z", "2026-09-21T12:00:00Z"),
            ]
        ),
        encoding="utf-8",
    )
    out = tmp_path / "audit.csv"
    assert m.main(["--from-json", str(raw), "--out", str(out)]) == 0
    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("sprint,start,end,merged_prs")
    assert lines[1].startswith("Sprint 1,2026-09-17,2026-10-07,1,1,1.000,#8,")

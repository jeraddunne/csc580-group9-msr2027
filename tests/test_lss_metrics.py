"""Offline unit tests for msr_pipeline.lss_metrics (no network, no data files)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from msr_pipeline import lss_metrics as lss

FIXTURE = Path(__file__).parent / "fixtures" / "lss_fixture.json"
NOW = datetime(2026, 10, 1, 12, 0, tzinfo=UTC)
CONFIG = {
    "repo": "jeraddunne/csc580-group9-msr2027",
    "wip_limit": 5,
    "team": [
        {"name": "Leticia Aderhold", "github": "leticia-a"},
        {"name": "Jerad Dunne", "github": "jeraddunne"},
        {"name": "Allie Hodges", "github": "allie-h"},
        {"name": "Hina Kramer", "github": "hina-k"},
    ],
    "timeline": {
        "formation": {"start": "2026-09-10", "end": "2026-09-16"},
        "sprint-1": {"start": "2026-09-17", "end": "2026-10-07"},
        "sprint-2": {"start": "2026-10-08", "end": "2026-10-28"},
        "sprint-3": {"start": "2026-10-29", "end": "2026-11-18"},
        "finalization": {"start": "2026-11-30", "end": "2026-12-04"},
    },
    "metrics": {"cycle_time_days_target": 5, "pr_first_review_hours_target": 48},
}


@pytest.fixture(scope="module")
def data() -> dict:
    with FIXTURE.open(encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def summary(data: dict) -> dict:
    return lss.summarize(
        data["issues"],
        data["prs"],
        data["reviews"],
        data["runs"],
        CONFIG,
        commits=data["commits"],
        now=NOW,
    )


# ----------------------------------------------------------------- basic helpers


def test_parse_iso_variants():
    assert lss.parse_iso("2026-09-17T09:00:00Z") == datetime(2026, 9, 17, 9, tzinfo=UTC)
    assert lss.parse_iso("2026-09-17") == datetime(2026, 9, 17, tzinfo=UTC)
    assert lss.parse_iso(None) is None
    assert lss.parse_iso("not a date") is None
    from datetime import date

    assert lss.parse_iso(date(2026, 9, 17)).day == 17


def test_issue_points_sources():
    assert lss.issue_points({"estimate": 8}) == 8
    assert lss.issue_points({"labels": ["sp:3"]}) == 3
    assert lss.issue_points({"labels": [{"name": "points: 5"}]}) == 5
    assert lss.issue_points({"body": "Some text\nEstimate: 2\n"}) == 2
    assert lss.issue_points({"body": "Story points = 13"}) == 13
    assert lss.issue_points({"labels": ["bug"]}) == 0


def test_closed_completed_excludes_not_planned():
    assert lss.closed_completed({"state": "closed", "closed_at": "2026-09-18T12:00:00Z"})
    assert not lss.closed_completed(
        {"state": "closed", "closed_at": "2026-09-18T12:00:00Z", "state_reason": "not_planned"}
    )
    assert not lss.closed_completed({"state": "open"})


# ----------------------------------------------------------------- cycle / lead / blocked


def test_cycle_time_uses_first_assignment(data: dict):
    issue = data["issues"][0]  # assigned 09-17 10:00, closed 09-21 15:00
    ct = lss.compute_cycle_time(issue)
    assert ct["days"] == pytest.approx(4.208, abs=0.001)
    assert ct["approximated"] is False


def test_cycle_time_uses_in_progress_label(data: dict):
    issue = data["issues"][1]  # labeled in progress 09-18 08:00, closed 09-19 18:00
    ct = lss.compute_cycle_time(issue)
    assert ct["days"] == pytest.approx(1.4167, abs=0.001)
    assert ct["approximated"] is False


def test_cycle_time_falls_back_to_created(data: dict):
    issue = data["issues"][4]  # no assignment events
    ct = lss.compute_cycle_time(issue)
    assert ct["approximated"] is True
    assert ct["days"] == pytest.approx(2.0)


def test_cycle_time_none_for_open_or_cancelled(data: dict):
    assert lss.compute_cycle_time(data["issues"][5]) is None
    assert lss.compute_cycle_time(data["issues"][8]) is None
    assert lss.compute_cycle_time({"pull_request": True, "state": "closed"}) is None


def test_lead_time(data: dict):
    lt = lss.compute_lead_time(data["issues"][0])
    assert lt["days"] == pytest.approx(4.25)


def test_blocked_time_closed_interval_and_open_blocker(data: dict):
    closed = lss.blocked_time(data["issues"][2], NOW)  # blocker 09-22 to 09-24
    assert closed["days"] == pytest.approx(2.0)
    assert closed["still_blocked"] is False
    open_b = lss.blocked_time(data["issues"][6], NOW)  # labeled 09-28 10:00, still open
    assert open_b["still_blocked"] is True
    assert open_b["days"] == pytest.approx(3.083, abs=0.001)


# ----------------------------------------------------------------- PRs


def test_pr_turnarounds_exclude_self_review(data: dict):
    turn = lss.pr_turnarounds(data["prs"], data["reviews"])
    by_num = {t["number"]: t for t in turn["first_review"]}
    assert by_num[10]["hours"] == pytest.approx(24.0)
    assert by_num[12]["hours"] == pytest.approx(24.0)
    assert turn["unreviewed_open"] == [14]
    merge = {t["number"]: t for t in turn["merge"]}
    assert merge[11]["hours"] == pytest.approx(29.0)
    # self-review only should count as unreviewed
    prs = [
        {
            "number": 99,
            "user": "x",
            "created_at": "2026-09-01T00:00:00Z",
            "merged_at": "2026-09-02T00:00:00Z",
            "state": "closed",
        }
    ]
    reviews = [
        {
            "pull_number": 99,
            "user": "x",
            "state": "APPROVED",
            "submitted_at": "2026-09-01T01:00:00Z",
        }
    ]
    t2 = lss.pr_turnarounds(prs, reviews)
    assert t2["first_review"] == []
    assert t2["unreviewed_merged"] == [99]


def test_first_time_right(data: dict):
    ftr = lss.first_time_right(data["prs"], data["reviews"])
    assert ftr["n"] == 4
    assert ftr["merged_without_changes"] == 3
    assert ftr["value"] == pytest.approx(0.75)


# ----------------------------------------------------------------- quality


def test_rework_ratio_counts_label_and_reopen(data: dict):
    rw = lss.rework_ratio(data["issues"])
    assert rw["n_closed"] == 6  # issues 1, 2, 3, 4, 5, 9 are closed (9 as not_planned)
    assert rw["n_rework"] == 1  # only issue 3 carries `rework` and was reopened
    assert rw["value"] == pytest.approx(1 / 6, abs=0.001)
    assert rw["numbers"] == [3]


def test_gini_known_values():
    assert lss.gini([1, 1, 1, 1]) == 0.0
    assert lss.gini([0, 0, 0, 1]) == pytest.approx(0.75)
    assert lss.gini([]) == 0.0
    assert lss.gini([0, 0]) == 0.0
    assert 0.0 < lss.gini([1, 2, 3, 4]) < 0.5


def test_contribution_balance_shares_and_flags(data: dict):
    cb = lss.contribution_balance(
        data["commits"],
        data["prs"],
        data["reviews"],
        data["issues"],
        lss.team_logins(CONFIG),
        CONFIG,
    )
    m = cb["members"]
    assert set(m) == {"leticia-a", "jeraddunne", "allie-h", "hina-k"}
    assert m["allie-h"]["commits"] == 3
    assert m["jeraddunne"]["reviews_given"] == 1  # two reviews on one PR count once
    assert cb["totals"]["prs_authored"] == 5
    assert "github-actions[bot]" in cb["others"]
    for v in m.values():
        assert 0 <= v["share_overall"] <= 1
    assert cb["gini"] is not None


# ----------------------------------------------------------------- SPC


def test_xmr_limits_known_numbers():
    lim = lss.xmr_limits([10, 12, 11, 13, 12])
    assert lim["n"] == 5
    assert lim["mean"] == pytest.approx(11.6)
    assert lim["mr_bar"] == pytest.approx(1.5)
    assert lim["ucl"] == pytest.approx(11.6 + 2.66 * 1.5, abs=0.001)
    assert lim["lcl"] == pytest.approx(11.6 - 2.66 * 1.5, abs=0.001)
    assert lim["mr_ucl"] == pytest.approx(3.267 * 1.5, abs=0.001)


def test_xmr_limits_floor_and_edge_cases():
    assert lss.xmr_limits([])["mean"] is None
    assert lss.xmr_limits([4.0])["ucl"] is None
    assert lss.xmr_limits([0, 10, 0, 10])["lcl"] == 0.0


def test_run_rules_beyond_limits():
    vals = [5, 6, 5, 6, 5, 6, 5, 40]
    signals = lss.run_rules(vals)
    assert any(s["rule"] == "beyond_limits" and s["index"] == 7 for s in signals)


def test_run_rules_eight_same_side():
    vals = [1, 1, 1, 1, 1, 1, 1, 1, 1, 20, 20, 20]
    lim = {"mean": 5.0, "ucl": 100.0, "lcl": 0.0}
    signals = lss.run_rules(vals, lim)
    rule = [s for s in signals if s["rule"] == "eight_same_side"]
    assert rule and rule[0]["start"] == 0 and rule[0]["end"] == 8


def test_run_rules_six_trending():
    vals = [1, 2, 3, 4, 5, 6, 3, 3]
    lim = {"mean": 3.0, "ucl": 100.0, "lcl": 0.0}
    signals = lss.run_rules(vals, lim)
    trend = [s for s in signals if s["rule"] == "six_trending"]
    assert trend == [{"rule": "six_trending", "start": 0, "end": 5}]
    assert lss.run_rules([1, 2, 3, 4, 5, 3, 3], lim) == []


def test_run_rules_needs_six_points():
    assert lss.run_rules([1, 100, 1, 100]) == []


# ----------------------------------------------------------------- config helpers


def test_normalize_timeline_dict_and_list():
    tl = lss.normalize_timeline(CONFIG)
    assert [t["name"] for t in tl] == [
        "Formation",
        "Sprint 1",
        "Sprint 2",
        "Sprint 3",
        "Finalization",
    ]
    tl2 = lss.normalize_timeline(
        {"timeline": [{"name": "Sprint 1", "start": "2026-09-17", "end": "2026-10-07"}]}
    )
    assert tl2[0]["name"] == "Sprint 1"
    assert tl2[0]["end"].hour == 23


def test_sprint_for_milestone_and_fallback():
    tl = lss.normalize_timeline(CONFIG)
    assert lss.sprint_for({"milestone": "sprint-2"}, tl) == "Sprint 2"
    assert (
        lss.sprint_for({"milestone": None, "closed_at": "2026-09-20T00:00:00Z"}, tl) == "Sprint 1"
    )
    assert lss.sprint_for({"milestone": None, "closed_at": None}, tl) == "Unscheduled"
    assert lss.sprint_for({"milestone": "Backlog"}, tl) == "Backlog"


# ----------------------------------------------------------------- summarize


def test_summarize_kpis(summary: dict):
    k = summary["kpis"]
    assert summary["counts"] == {"issues": 9, "prs": 5, "reviews": 5, "runs": 6, "commits": 9}
    assert k["cycle_time_days"]["n"] == 5
    assert k["cycle_time_days"]["approximated"] == 1
    assert k["lead_time_days"]["n"] == 5
    assert k["first_time_right"]["value"] == pytest.approx(0.75)
    assert k["first_time_right"]["status"] == "ok"
    assert k["rework_ratio"]["value"] == pytest.approx(1 / 6, abs=0.001)
    assert k["rework_ratio"]["status"] == "warn"
    assert k["ci_pass_rate"]["n"] == 4  # cancelled and LSS metrics runs excluded
    assert k["ci_pass_rate"]["value"] == pytest.approx(0.75)
    assert k["reproducibility_check"]["value"] == "pass"
    assert k["wip"]["value"] == 2  # issues 7 and 8 assigned and open
    assert k["wip"]["status"] == "ok"
    assert k["defect_count"]["value"] == 1
    assert k["kaizen_closure_rate"]["value"] == pytest.approx(0.5)
    assert k["pr_first_review_hours"]["n"] == 4
    assert k["pr_first_review_hours"]["unreviewed_open"] == [14]
    assert k["blocked_time_days"]["open_blockers"] == 1
    assert summary["open_blockers"][0]["number"] == 7
    assert summary["open_prs_waiting_review"][0]["number"] == 14


def test_summarize_sprint_rows(summary: dict):
    rows = {s["name"]: s for s in summary["sprints"]}
    s1 = rows["Sprint 1"]
    assert s1["status"] == "active"
    assert s1["total_issues"] == 7
    # committed = created by end of 2026-09-18: issues 1,2,3,9 (4 and 7 and 8 were added later)
    assert s1["committed_issues"] == 4
    assert s1["added_after_planning"] == 3
    assert s1["done_issues"] == 4  # 1,2,3,4 (9 is not_planned)
    assert s1["velocity"] == 13  # 3+2+5+3
    assert s1["committed_points"] == 10
    assert s1["commitment_reliability"] == pytest.approx(1.0)
    assert rows["Formation"]["done_issues"] == 1
    assert rows["Sprint 2"]["status"] == "future"


def test_summarize_empty_inputs():
    s = lss.summarize([], [], [], [], CONFIG, commits=[], now=NOW)
    assert s["kpis"]["cycle_time_days"]["status"] == "nodata"
    assert s["kpis"]["reproducibility_check"]["value"] == "nodata"
    assert s["kpis"]["contribution_gini"]["status"] == "nodata"
    assert s["signals"] == []
    assert len(s["sprints"]) == 5


def test_summarize_without_config():
    s = lss.summarize([], [], [], [], None, now=NOW)
    assert s["wip_limit"] == lss.DEFAULT_WIP_LIMIT
    assert s["targets"]["cycle_time_days_target"] == 5
    assert s["sprints"] == []

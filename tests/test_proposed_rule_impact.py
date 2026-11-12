"""Tests for scripts/proposed_rule_impact.py (issue #132; synthetic text only)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

from msr_pipeline.skill_risk import copy_counts, rules_from_dict

ROOT = Path(__file__).resolve().parents[1]


def _module():
    spec = importlib.util.spec_from_file_location(
        "proposed_rule_impact", ROOT / "scripts" / "proposed_rule_impact.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RULE_FILE = {
    "categories": {"NETWORK": "x", "TOOL_GRANT": "y"},
    "rules": [
        {"id": "HIGH", "category": "NETWORK", "severity": 7, "patterns": ["curl"]},
        {"id": "CTX", "category": "TOOL_GRANT", "severity": 1, "patterns": ["allowed-tools"]},
        {
            "id": "NEW",
            "category": "TOOL_GRANT",
            "severity": 6,
            "patterns": ["grant-all"],
            "status": "proposed",
        },
        {
            "id": "NEWCTX",
            "category": "TOOL_GRANT",
            "severity": 3,
            "patterns": ["grant-all"],
            "status": "proposed",
        },
    ],
}


def test_impact_counts_matches_and_new_high_risk():
    every = rules_from_dict(RULE_FILE, include_inactive=True)
    active = [r for r in every if r.status == "active"]
    proposed = [r for r in every if r.status == "proposed"]
    reps = pd.DataFrame(
        {
            "file_sha": ["a", "b", "c", "d"],
            "content": ["curl and grant-all", "grant-all", "allowed-tools only", None],
        }
    )
    occurrences = pd.DataFrame(
        {
            "file_sha": ["a", "a", "b", "b", "b", "c"],
            "repo_full_name": ["r1", "r2", "r1", "r2", "r3", "r1"],
        }
    )
    table = (
        _module().impact(reps, copy_counts(occurrences), active, proposed, 6).set_index("rule_id")
    )

    new = table.loc["NEW"]
    assert new["main_population"] == 4
    assert new["contents_matched"] == 2
    assert new["already_high_risk"] == 1  # "a" already matches HIGH
    assert new["newly_high_risk"] == 1  # "b"
    assert new["occurrences_matched"] == 5
    assert new["high_risk_contents_now"] == 1
    assert new["high_risk_contents_if_activated"] == 2
    assert new["high_risk_share_now"] == 0.25
    assert new["high_risk_share_if_activated"] == 0.5

    # A proposed rule below the cutoff matches but adds no high-risk content.
    ctx = table.loc["NEWCTX"]
    assert ctx["contents_matched"] == 2
    assert ctx["newly_high_risk"] == 0
    assert ctx["high_risk_contents_if_activated"] == 1


def test_committed_impact_table_matches_the_rule_file():
    """The committed CSV lists exactly the proposed rules, and its columns add up."""
    from msr_pipeline.skill_risk import load_rules

    table = pd.read_csv(ROOT / "results" / "proposed_rule_impact.csv")
    proposed = sorted(r.id for r in load_rules(include_inactive=True) if r.status == "proposed")
    assert sorted(table["rule_id"]) == proposed
    for row in table.to_dict("records"):
        if row["severity"] >= 6:
            assert row["contents_matched"] == row["already_high_risk"] + row["newly_high_risk"]
        assert row["high_risk_contents_if_activated"] == (
            row["high_risk_contents_now"] + row["newly_high_risk"]
        )

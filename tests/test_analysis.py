"""Tests for the P-01 analysis (offline, synthetic data, fixtures only)."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from msr_pipeline import analysis, cli
from msr_pipeline.skill_risk import is_symlink_stub, load_rules, population_flags


def test_wilson_ci_known_values():
    low, high = analysis.wilson_ci(5, 10)
    assert low == pytest.approx(0.2366, abs=1e-4)
    assert high == pytest.approx(0.7634, abs=1e-4)
    assert all(math.isnan(v) for v in analysis.wilson_ci(0, 0))
    low, high = analysis.wilson_ci(0, 50)
    assert low == pytest.approx(0.0, abs=1e-12)
    assert 0.0 < high < 0.1


def test_rank_biserial_and_mann_whitney():
    assert analysis.rank_biserial(6, 3, 2) == 1.0
    assert analysis.rank_biserial(0, 3, 2) == -1.0
    assert math.isnan(analysis.rank_biserial(1, 0, 2))
    res = analysis.mann_whitney([3, 4, 5, 6], [1, 2, 1, 2])
    assert res["status"] == "ok"
    assert res["rank_biserial"] == pytest.approx(1.0)
    assert res["p_value"] < 0.1
    same = analysis.mann_whitney([1, 1, 1], [1, 1, 1])
    assert same["rank_biserial"] == 0.0 and same["p_value"] == 1.0
    assert analysis.mann_whitney([], [1, 2])["status"] == "insufficient data"


def test_bootstrap_is_deterministic_and_brackets_estimate():
    x = np.array([1, 1, 2, 3, 5, 8, 13] * 10)
    y = np.array([1, 1, 1, 2, 2, 3] * 10)
    a = analysis.bootstrap_difference(x, y, analysis.row_mean, n_boot=300, seed=7)
    b = analysis.bootstrap_difference(x, y, analysis.row_mean, n_boot=300, seed=7)
    assert a == b
    assert a["status"] == "ok"
    assert a["ci_low"] <= a["estimate"] <= a["ci_high"]
    assert a["estimate"] == pytest.approx(x.mean() - y.mean())
    share = analysis.bootstrap_difference(x, y, analysis.row_share_at_least(2), n_boot=200)
    assert share["estimate"] == pytest.approx((x >= 2).mean() - (y >= 2).mean())
    assert analysis.bootstrap_difference([], y, analysis.row_mean)["status"] == "insufficient data"


def test_holm_adjust():
    assert analysis.holm_adjust([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    out = analysis.holm_adjust([0.2, float("nan"), 0.9])
    assert out[0] == pytest.approx(0.4) and math.isnan(out[1]) and out[2] == pytest.approx(0.9)
    assert analysis.holm_adjust([]) == []


def test_population_flags_and_symlink_stub():
    reps = pd.DataFrame(
        {
            "file_sha": list("abcde"),
            "content": [
                "../shared/skills/foo/SKILL.md",
                "Use the tool.",
                "---\nname: x\n---\nbody",
                float("nan"),
                "docs/SKILL.md",
            ],
            "frontmatter_valid": [0, 0, 1, None, 0],
        }
    )
    flags = population_flags(reps).set_index("file_sha")
    assert flags["is_symlink_stub"].to_dict() == {
        "a": True,
        "b": False,
        "c": False,
        "d": False,
        "e": True,
    }
    assert flags["in_main_population"].to_dict() == {
        "a": False,
        "b": True,
        "c": True,
        "d": False,
        "e": False,
    }
    assert flags["frontmatter_valid"].tolist() == [False, False, True, False, False]
    assert not is_symlink_stub("x/" * 150)
    assert not is_symlink_stub("first line/\nsecond line")


def _pairs() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "family": ["skill-creator", "f", "f", "f", "g", "g"],
            "file_sha_a": list("abcdef"),
            "file_sha_b": list("ghijkl"),
            "similarity": [0.31, 0.45, 0.5, 0.66, 0.72, 0.95],
            "ordered": [True, False, True, False, True, False],
            "only_in_a": ["", "", "REMOTE_CODE", "", "", ""],
            "only_in_b": ["NETWORK", "", "", "", "PERSISTENCE", ""],
            "differs": [True, False, True, False, True, False],
        }
    )


def test_threshold_sweep_is_monotone_and_counts_direction():
    sweep = analysis.threshold_sweep(analysis.mark_templates(_pairs()))
    lineage = sweep["lineage_pairs"].tolist()
    assert lineage == sorted(lineage, reverse=True)
    assert lineage[0] == 6
    row = sweep.set_index("threshold").loc[0.5]
    assert row["lineage_pairs"] == 4
    assert row["ordered_newer_adds"] == 1
    assert row["ordered_newer_drops"] == 1
    summary = analysis.rq3_summary(analysis.mark_templates(_pairs())).set_index("scope")
    assert summary.loc["all_families", "lineage_pairs"] == 6
    assert summary.loc["excluding_template_families", "lineage_pairs"] == 5
    empty = analysis.threshold_sweep(_pairs().iloc[0:0])
    assert empty["lineage_pairs"].sum() == 0


def test_negbin_not_estimable_on_degenerate_data():
    frame = pd.DataFrame(
        {
            "copies": [1, 1, 1],
            "high_risk": [False, False, False],
            "body_chars": [10, 10, 10],
            "has_scripts": [0, 0, 0],
            "location_class": ["other"] * 3,
            "stars": [0, 0, 0],
            "language": ["Python"] * 3,
        }
    )
    out = analysis.rq2_negbin(frame)
    assert len(out) == 1
    assert out.iloc[0]["status"] == "not estimable"
    assert out.iloc[0]["term"] == "high_risk"


def test_negbin_recovers_effect_on_synthetic_data():
    rng = np.random.default_rng(1)
    n = 600
    high = rng.random(n) < 0.3
    mu = np.exp(0.2 + 0.7 * high)
    extra = rng.negative_binomial(2, 2 / (2 + mu))
    frame = pd.DataFrame(
        {
            "copies": 1 + extra,
            "high_risk": high,
            "body_chars": rng.integers(100, 5000, n),
            "has_scripts": rng.integers(0, 2, n),
            "location_class": rng.choice(["skills-dir", "other", "canonical"], n),
            "stars": rng.integers(0, 1000, n),
            "language": rng.choice(["Python", "TypeScript", ""], n),
        }
    )
    out = analysis.rq2_negbin(frame).set_index("term")
    assert out.loc["high_risk", "status"] in ("ok", "not converged")
    assert 1.3 < out.loc["high_risk", "irr"] < 3.2
    assert out.loc["high_risk", "irr_ci_low"] < out.loc["high_risk", "irr"]
    assert "alpha" in out.index


def test_category_tests_holm_and_minimum_size():
    rules = load_rules()
    reference = [1] * 80 + [2] * 20
    remote = [5] * 20 + [8] * 20
    privilege = [1] * 28 + [2] * 7
    credentials = [3] * 10
    copies = reference + remote + privilege + credentials
    cats = [""] * 100 + ["REMOTE_CODE"] * 40 + ["PRIVILEGE"] * 35 + ["CREDENTIALS"] * 10
    frame = pd.DataFrame(
        {
            "copies": copies,
            "high_risk_categories": cats,
            "high_risk": [c != "" for c in cats],
        }
    )
    out = analysis.rq2_category_tests(frame, rules).set_index("category")
    assert out.loc["REMOTE_CODE", "tested"] and out.loc["REMOTE_CODE", "significant_holm_05"]
    assert out.loc["REMOTE_CODE", "p_holm"] >= out.loc["REMOTE_CODE", "p_value"]
    assert out.loc["PRIVILEGE", "tested"] and not out.loc["PRIVILEGE", "significant_holm_05"]
    assert not out.loc["CREDENTIALS", "tested"]
    assert math.isnan(out.loc["CREDENTIALS", "p_holm"])


def test_with_severity_cutoff_changes_flags():
    rules = load_rules()
    scan = pd.DataFrame(
        {
            "rule_ids": ["R-PRV-002", "R-PRV-001", "R-PER-001", ""],
            "high_risk_categories": ["", "PRIVILEGE", "PERSISTENCE", ""],
            "high_risk": [False, True, True, False],
        }
    )
    assert analysis.with_severity_cutoff(scan, rules, 5)["high_risk"].tolist() == [
        True,
        True,
        True,
        False,
    ]
    assert analysis.with_severity_cutoff(scan, rules, 7)["high_risk"].tolist() == [
        False,
        False,
        True,
        False,
    ]


def test_cli_analyze_writes_outputs(data_root: Path):
    assert cli.main(["analyze", "--seed", "580"]) == 0
    results = data_root / "results"
    for name in analysis.OUTPUT_TABLES:
        assert (results / f"{name}.csv").exists(), name
    for name in analysis.OUTPUT_FIGURES:
        assert (data_root / "figures" / f"{name}.png").exists(), name
    manifest = json.loads((results / "ANALYSIS_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["seed"] == 580
    assert manifest["row_counts"]["representatives"] > 0
    flow = pd.read_csv(results / "population_flow.csv").set_index("step")
    assert (
        flow.loc["main_population", "distinct_contents"]
        <= flow.loc["with_content", "distinct_contents"]
    )
    negbin = pd.read_csv(results / "rq2_negbin.csv")
    assert negbin.iloc[0]["status"] == "not estimable"


def test_cli_analyze_missing_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MSR_DATA_DIR", str(tmp_path))
    assert cli.main(["analyze"]) == 1


def test_high_risk_by_category_excludes_context_rules():
    from msr_pipeline import analysis, skill_risk

    rules = skill_risk.rules_from_dict(
        {
            "categories": {"TOOL_GRANT": "x"},
            "rules": [
                {
                    "id": "HI",
                    "category": "TOOL_GRANT",
                    "severity": 6,
                    "patterns": ["Bash[(][*][)]"],
                },
                {
                    "id": "LO",
                    "category": "TOOL_GRANT",
                    "severity": 1,
                    "patterns": ["allowed-tools"],
                },
            ],
        }
    )
    reps = pd.DataFrame(
        {
            "file_sha": ["a", "b", "c"],
            "content": ["allowed-tools: Bash(*)", "allowed-tools: Read", "plain text"],
        }
    )
    scan = skill_risk.scan_contents(reps, rules)
    counts = pd.DataFrame({"file_sha": ["a", "b", "c"], "copies": [3, 1, 1], "repos": [2, 1, 1]})
    _, by_category = analysis.rq1_tables(scan, counts, rules)
    row = by_category.set_index("category").loc["TOOL_GRANT"]
    assert row["contents"] == 2
    assert row["high_risk_contents"] == 1
    assert row["high_risk_occurrences"] == 3
    assert row["high_risk_share"] < row["content_share"]

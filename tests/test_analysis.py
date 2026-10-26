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
    assert flags["content_recovered"].all()


def test_population_flags_exclude_unrecovered_content():
    reps = pd.DataFrame(
        {
            "file_sha": list("abc"),
            "content": ["Use the tool.", "Use the tool.", "Use the tool."],
            "content_sha_ok": [1, 2, 0],
        }
    )
    flags = population_flags(reps).set_index("file_sha")
    assert flags["content_recovered"].to_dict() == {"a": True, "b": True, "c": False}
    assert flags["in_main_population"].to_dict() == {"a": True, "b": True, "c": False}


def test_scripts_summary_with_and_without_truncated_listings():
    rules = load_rules()
    sib_scan = pd.DataFrame(
        {
            "repo_full_name": ["r/a", "r/b"],
            "artifact_path": ["s/SKILL.md", "t/SKILL.md"],
            "entry_name": ["install.sh", "tool.py"],
            "rule_ids": ["", ""],
            "high_risk": [True, False],
        }
    )
    unread = pd.DataFrame([("script_files_without_text", 3)], columns=["metric", "value"])
    out = analysis.scripts_summary(
        sib_scan, rules, unread=unread, truncated={("r/a", "s/SKILL.md")}
    ).set_index("metric")["value"]
    assert out["script_files_with_text"] == 2
    assert out["script_files_without_text"] == 3
    assert out["script_files_with_text_excluding_truncated_listing"] == 1
    assert out["skills_with_high_risk_script"] == 1
    assert out["skills_with_high_risk_script_excluding_truncated_listing"] == 0
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


def test_threshold_sweep_splits_ordered_pairs_by_location():
    # ordered pairs: a-g (0.31), c-i (0.5), e-k (0.72)
    locations = {"a": "canonical", "g": "canonical", "c": "canonical", "i": "skills-dir"}
    sweep = analysis.threshold_sweep(_pairs(), locations=locations).set_index("threshold")
    by_loc = ["ordered_pairs_canonical", "ordered_pairs_mixed", "ordered_pairs_non_canonical"]
    assert sweep.loc[0.3, by_loc].tolist() == [1, 1, 1]
    assert sweep.loc[0.5, by_loc].tolist() == [0, 1, 1]
    assert (sweep[by_loc].sum(axis=1) == sweep["ordered_pairs"]).all()
    assert "ordered_pairs_canonical" not in analysis.threshold_sweep(_pairs()).columns
    empty = analysis.threshold_sweep(_pairs().iloc[0:0], locations=locations)
    assert empty[by_loc].to_numpy().sum() == 0


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


def test_rq2_reach_summary_values():
    # Expected values worked out by hand from the seven contents below.
    frame = pd.DataFrame(
        {
            "high_risk": [True, True, True, False, False, False, False],
            "copies": [1, 5, 12, 1, 1, 2, 3],
            "repos": [1, 2, 3, 1, 1, 1, 2],
        }
    )
    out = analysis.rq2_reach_summary(frame).set_index("group")
    hr, other = out.loc["high-risk signal"], out.loc["no high-risk signal"]
    assert (hr["contents"], hr["occurrences"], hr["max_copies"]) == (3, 18, 12)
    assert (hr["mean_copies"], hr["median_copies"]) == (6.0, 5.0)
    assert hr["share_copied_2plus"] == pytest.approx(0.6667)
    assert hr["share_copied_5plus"] == pytest.approx(0.6667)
    assert hr["share_copied_10plus"] == pytest.approx(0.3333)
    assert hr["share_cross_repo"] == pytest.approx(0.6667)
    assert (other["contents"], other["occurrences"], other["max_copies"]) == (4, 7, 3)
    assert (other["mean_copies"], other["median_copies"]) == (1.75, 1.5)
    assert other["share_copied_2plus"] == pytest.approx(0.5)
    assert other["share_copied_5plus"] == 0.0 and other["share_copied_10plus"] == 0.0
    assert other["share_cross_repo"] == pytest.approx(0.25)

    # The Mann-Whitney and bootstrap tables compare the same two groups.
    mw = analysis.rq2_mannwhitney(frame).set_index("outcome")
    assert (mw.loc["copies", "n_group"], mw.loc["copies", "n_reference"]) == (3, 4)
    assert (mw.loc["copies", "mean_group"], mw.loc["copies", "mean_reference"]) == (6.0, 1.75)
    assert (mw.loc["repos", "mean_group"], mw.loc["repos", "mean_reference"]) == (2.0, 1.25)
    boot = analysis.rq2_bootstrap(frame, n_boot=200, seed=1).set_index("metric")
    assert boot.loc["difference_in_mean_copies", "estimate"] == pytest.approx(4.25)
    assert boot.loc["difference_in_share_copied_2plus", "estimate"] == pytest.approx(2 / 3 - 0.5)

    # A group with no contents reports zeros and undefined means rather than failing.
    empty = analysis.rq2_reach_summary(frame[~frame["high_risk"]]).set_index("group")
    none = empty.loc["high-risk signal"]
    assert (none["contents"], none["occurrences"], none["max_copies"]) == (0, 0, 0)
    assert math.isnan(none["mean_copies"]) and none["share_copied_2plus"] == 0.0


def _sensitivity_frame() -> pd.DataFrame:
    # R-PRV-002 is severity 5, R-PRV-001 severity 6, R-PER-001 severity 7 or more, so the
    # main cutoff (6) flags PRV-001 and PER-001; cutoff 5 adds PRV-002; cutoff 7 keeps PER-001.
    rows = [
        # file_sha, rule_ids, name, frontmatter_valid, copies
        ("a", "R-PER-001", "skill-creator", True, 100),
        ("b", "R-PRV-001", "alpha", True, 90),
        ("c", "R-PRV-002", "beta", True, 80),
        ("d", "", "gamma", True, 70),
        ("e", "R-PRV-001", "Skill-Creator", False, 60),
        ("f", "", "delta", True, 50),
        ("g", "R-PRV-002", "epsilon", False, 40),
        ("h", "", "zeta", True, 30),
        ("i", "R-PER-001", "eta", True, 20),
        ("j", "", "theta", False, 10),
        ("k", "", "iota", True, 5),
        ("l", "R-PRV-002", "kappa", True, 4),
        ("m", "", "lambda", True, 3),
        ("n", "R-PRV-001", "mu", True, 2),
    ]
    frame = pd.DataFrame(
        rows, columns=["file_sha", "rule_ids", "name", "frontmatter_valid", "copies"]
    )
    frame["high_risk"] = frame["rule_ids"].isin(["R-PRV-001", "R-PER-001"])
    return frame


def test_sensitivity_summary_membership_and_results():
    out = analysis.sensitivity_summary(_sensitivity_frame(), load_rules()).set_index("scenario")
    # scenario: (contents, high-risk contents, mean copies high-risk, mean copies other).
    # Membership: cutoff 5 adds c, g, l; cutoff 7 keeps a, i; the front-matter subset drops
    # e, g, j; the top-10 exclusion keeps k, l, m, n; the template exclusion drops a and e.
    expected = {
        "main (severity 6, main population)": (14, 5, 272 / 5, 292 / 9),
        "severity cutoff 5": (14, 8, 396 / 8, 168 / 6),
        "severity cutoff 7": (14, 2, 120 / 2, 444 / 12),
        "front-matter-valid subset": (11, 4, 212 / 4, 242 / 7),
        "excluding top 10 most-copied contents": (4, 1, 2.0, 12 / 3),
        "excluding template families": (12, 3, 112 / 3, 292 / 9),
    }
    assert list(out.index) == list(expected)
    for scenario, (n, k, mean_high, mean_other) in expected.items():
        row = out.loc[scenario]
        assert (row["contents"], row["high_risk_contents"]) == (n, k), scenario
        assert row["high_risk_share"] == pytest.approx(round(k / n, 4)), scenario
        assert row["share_ci_low"] < k / n < row["share_ci_high"], scenario
        assert row["mean_copies_high_risk"] == pytest.approx(mean_high), scenario
        assert row["mean_copies_other"] == pytest.approx(mean_other), scenario
        assert row["mean_copies_ratio"] == pytest.approx(mean_high / mean_other), scenario
    # With a single high-risk content left, the test is not run, but the means still are.
    top = out.loc["excluding top 10 most-copied contents"]
    assert math.isnan(top["mwu_p_copies"]) and math.isnan(top["rank_biserial_copies"])
    assert 0.0 <= out.loc["severity cutoff 5", "mwu_p_copies"] <= 1.0


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
    scripts = pd.read_csv(results / "scripts_summary.csv").set_index("metric")["value"]
    for metric in (
        "script_files_without_text",
        "skills_with_truncated_listing",
        "skills_without_folder_listing",
        "skills_with_unrecovered_content",
        "script_files_with_text_excluding_truncated_listing",
    ):
        assert metric in scripts.index, metric


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


def test_rq1_prevalence_by_rule_values():
    from msr_pipeline import skill_risk

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
            "file_sha": ["a", "b", "c", "d"],
            "content": [
                "allowed-tools: Bash(*)",
                "allowed-tools: Read",
                "plain text",
                "run Bash(*)",
            ],
        }
    )
    scan = skill_risk.scan_contents(reps, rules)
    counts = pd.DataFrame({"file_sha": list("abcd"), "copies": [3, 1, 1, 5], "repos": [1, 1, 1, 1]})
    by_rule, _ = analysis.rq1_tables(scan, counts, rules)
    by_rule = by_rule.set_index("rule_id")
    # rule: (contents, content share, occurrences, occurrence share) over 4 contents, 10 copies
    expected = {"HI": (2, 0.5, 8, 0.8), "LO": (2, 0.5, 4, 0.4), "ANY_HIGH_RISK": (2, 0.5, 8, 0.8)}
    low, high = analysis.wilson_ci(2, 4)
    for rule_id, (contents, share, occ, occ_share) in expected.items():
        row = by_rule.loc[rule_id]
        assert (row["contents"], row["occurrences"]) == (contents, occ), rule_id
        assert row["content_share"] == pytest.approx(share), rule_id
        assert row["occurrence_share"] == pytest.approx(occ_share), rule_id
        assert row["content_ci_low"] == pytest.approx(round(low, 4)), rule_id
        assert row["content_ci_high"] == pytest.approx(round(high, 4)), rule_id


def test_population_flow_counts_each_step():
    reps = pd.DataFrame(
        {
            "file_sha": list("abcdef"),
            "content": [
                "../shared/skills/foo/SKILL.md",
                "Use the tool.",
                "---\nname: x\n---\nbody",
                float("nan"),
                "docs/SKILL.md",
                "Use the tool.",
            ],
            "frontmatter_valid": [0, 0, 1, None, 0, 1],
            "content_sha_ok": [1, 1, 2, 1, 1, 0],
        }
    )
    copies = {"a": 2, "b": 3, "c": 1, "d": 2, "e": 1, "f": 4}
    occurrences = pd.DataFrame(
        [(sha, f"repo{i}") for sha, n in copies.items() for i in range(n)],
        columns=["file_sha", "repo_full_name"],
    )
    flow = analysis.population_flow(reps, population_flags(reps), occurrences).set_index("step")
    # a and e are symlink stubs, d has no text, f was not recovered; b and c remain.
    assert flow[["distinct_contents", "occurrences"]].to_dict("index") == {
        "all_occurrences": {"distinct_contents": 6, "occurrences": 13},
        "with_content": {"distinct_contents": 5, "occurrences": 11},
        "excluded_symlink_stubs": {"distinct_contents": 2, "occurrences": 3},
        "excluded_unrecovered_content": {"distinct_contents": 1, "occurrences": 4},
        "main_population": {"distinct_contents": 2, "occurrences": 4},
        "frontmatter_valid_subset": {"distinct_contents": 1, "occurrences": 1},
    }

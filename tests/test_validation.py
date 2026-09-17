"""Tests for the P-01 validation kit (offline; synthetic labels only)."""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import pandas as pd
import pytest

from msr_pipeline import validation as v
from msr_pipeline.skill_risk import load_rules

RULES = load_rules()
ROOT = Path(__file__).resolve().parents[1]


def _kit():
    spec = importlib.util.spec_from_file_location(
        "annotation_kit", ROOT / "scripts" / "annotation_kit.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def signals(rows: list[tuple[str, str, str, str]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"file_sha": s, "rule_id": r, "label": lab, "missed_category": m, "notes": ""}
            for s, r, lab, m in rows
        ],
        columns=v.KIND_COLUMNS["signals"],
    )


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


def test_wilson_ci_known_values():
    low, high = v.wilson_ci(8, 10)
    assert low == pytest.approx(0.4902, abs=1e-4)
    assert high == pytest.approx(0.9433, abs=1e-4)
    assert v.wilson_ci(0, 10)[0] == 0.0
    assert all(math.isnan(x) for x in v.wilson_ci(0, 0))


def test_cohen_kappa_textbook_example():
    # 2x2 table: yes/yes 20, yes/no 5, no/yes 10, no/no 15 -> po 0.7, pe 0.5, kappa 0.4
    a = ["yes"] * 25 + ["no"] * 25
    b = ["yes"] * 20 + ["no"] * 5 + ["yes"] * 10 + ["no"] * 15
    kappa, note = v.cohen_kappa(a, b)
    assert kappa == pytest.approx(0.4)
    assert note == ""
    assert v.percent_agreement(a, b) == pytest.approx(0.7)


def test_cohen_kappa_degenerate_and_empty():
    kappa, note = v.cohen_kappa(["RISKY"] * 5, ["RISKY"] * 5)
    assert math.isnan(kappa) and "single category" in note
    kappa, note = v.cohen_kappa([], [])
    assert math.isnan(kappa) and note == "no matched items"
    with pytest.raises(ValueError):
        v.cohen_kappa(["a"], [])


# ---------------------------------------------------------------------------
# Label files
# ---------------------------------------------------------------------------


def test_parse_label_filename_and_rater_kind():
    f = v.parse_label_filename("data/annotations/signals_jd_r2.csv")
    assert (f.kind, f.rater, f.round, f.is_human) == ("signals", "jd", 2, True)
    assert not v.parse_label_filename("lineage_llm-claude_r1.csv").is_human
    assert v.parse_label_filename("notes.csv") is None
    assert v.label_filename("drift", "jd", 1) == "drift_jd_r1.csv"
    with pytest.raises(ValueError):
        v.label_filename("drift", "Bad Name", 1)


def test_validate_labels_reports_problems():
    rule = RULES[0].id
    df = signals(
        [
            ("a", rule, "RISKY", ""),
            ("a", rule, "RISKY", ""),  # duplicate key
            ("b", "R-NOPE-999", "", ""),  # unknown rule
            ("c", "NONE", "RISKY", ""),  # wrong label set for NONE
            ("d", rule, "MISSED_RISKY", ""),  # wrong label set for a rule row
            ("e", "NONE", "MISSED_RISKY", ""),  # missing category
            ("f", "NONE", "MISSED_RISKY", "NOT_A_CATEGORY"),
            ("g", rule, "BENIGN_CONTEXT", "REMOTE_CODE"),  # category on a rule row
            ("h", "NONE", "", ""),  # unlabelled is fine
        ]
    )
    categories = {r.category for r in RULES}
    problems = "\n".join(
        v.validate_labels(df, "signals", [r.id for r in RULES], categories, "x.csv")
    )
    for fragment in (
        "duplicate key",
        "unknown rule_id 'R-NOPE-999'",
        "not allowed for rule_id 'NONE'",
        f"not allowed for rule_id '{rule}'",
        "needs missed_category",
        "unknown missed_category",
        "only goes with MISSED_RISKY",
    ):
        assert fragment in problems, fragment
    assert v.validate_labels(pd.DataFrame({"file_sha": []}), "lineage")[0].startswith(
        "missing columns"
    )
    bad_drift = pd.DataFrame(
        [{"file_sha_a": "a", "file_sha_b": "b", "change_type": "MAYBE", "notes": ""}]
    )
    assert "not in" in v.validate_labels(bad_drift, "drift")[0]
    assert len(v.valid_labelled_rows(df, "signals")) == 5


# ---------------------------------------------------------------------------
# Precision, recall, agreement
# ---------------------------------------------------------------------------


def test_precision_by_rule_and_category():
    df = signals(
        [
            ("s1", "R-RCE-001", "RISKY", ""),
            ("s2", "R-RCE-001", "BENIGN_CONTEXT", ""),
            ("s3", "R-RCE-001", "NOT_PRESENT", ""),
            ("s4", "R-RCE-001", "RISKY", ""),
            ("s4", "R-RCE-002", "NOT_PRESENT", ""),
            ("n1", "NONE", "NONE_PRESENT", ""),
        ]
    )
    by_rule = v.precision_by_rule(df, RULES).set_index("rule_id")
    row = by_rule.loc["R-RCE-001"]
    assert row["n"] == 4 and row["risky"] == 2
    assert row["strict_precision"] == pytest.approx(0.5)
    assert row["capability_precision"] == pytest.approx(0.75)
    assert row["strict_ci_low"] < 0.5 < row["strict_ci_high"]
    assert by_rule.loc["R-EXF-001", "n"] == 0 and math.isnan(
        by_rule.loc["R-EXF-001", "strict_precision"]
    )
    assert "R-SHL-001" not in by_rule.index  # low severity and unlabelled

    by_cat = v.precision_by_category(df, RULES).set_index("category")
    remote = by_cat.loc["REMOTE_CODE"]
    # item-level: s1 RISKY, s2 BENIGN, s3 NOT_PRESENT, s4 RISKY (any RISKY wins)
    assert remote["n"] == 4 and remote["risky"] == 2 and remote["not_present"] == 1


def test_recall_estimate_scales_to_population():
    df = signals(
        [(f"n{i}", "NONE", "NONE_PRESENT", "") for i in range(8)]
        + [
            ("m1", "NONE", "MISSED_RISKY", "REMOTE_CODE"),
            ("m2", "NONE", "MISSED_RISKY", "CREDENTIALS"),
        ]
    )
    rec = v.recall_estimate(
        df, no_signal_stratum_size=40, population_no_signal_count=1000
    ).set_index("scope")
    assert rec.loc["ALL", "n_labelled"] == 10
    assert rec.loc["ALL", "miss_rate"] == pytest.approx(0.2)
    assert rec.loc["ALL", "est_missed"] == pytest.approx(200)
    assert rec.loc["ALL", "est_missed_low"] < 200 < rec.loc["ALL", "est_missed_high"]
    assert rec.loc["REMOTE_CODE", "missed"] == 1
    empty = v.recall_estimate(signals([]), 40, 1000)
    assert empty.loc[0, "n_labelled"] == 0 and math.isnan(empty.loc[0, "miss_rate"])


def test_agreement_classifies_comparisons():
    base = signals(
        [
            ("a", "R-RCE-001", "RISKY", ""),
            ("b", "R-RCE-001", "NOT_PRESENT", ""),
            ("c", "NONE", "NONE_PRESENT", ""),
        ]
    )
    changed = base.copy()
    changed.loc[1, "label"] = "RISKY"
    files = [
        (v.parse_label_filename("signals_jd_r1.csv"), base),
        (v.parse_label_filename("signals_jd_r2.csv"), changed),
        (v.parse_label_filename("signals_ab_r1.csv"), base),
        (v.parse_label_filename("signals_llm-model_r1.csv"), base),
    ]
    out = v.agreement(files)
    kinds = sorted(out["comparison"].tolist())
    assert kinds.count("intra-rater") == 1
    assert kinds.count("inter-rater") == 1
    assert kinds.count("human-vs-llm") == 3
    intra = out[out["comparison"] == "intra-rater"].iloc[0]
    assert intra["n"] == 3 and intra["percent_agreement"] == pytest.approx(2 / 3)
    inter = out[out["comparison"] == "inter-rater"].iloc[0]
    assert inter["percent_agreement"] == 1.0


def test_lineage_and_drift_summaries():
    lin = pd.DataFrame(
        [
            {"file_sha_a": str(i), "file_sha_b": "x", "same_lineage": lab, "notes": ""}
            for i, lab in enumerate(["YES", "YES", "YES", "NO", "UNSURE", ""])
        ]
    )
    out = v.lineage_precision(lin).iloc[0]
    assert out["n_labelled"] == 5 and out["lineage_precision"] == pytest.approx(0.75)
    assert out["share_unsure"] == pytest.approx(0.2)
    drift = pd.DataFrame(
        [
            {"file_sha_a": str(i), "file_sha_b": "x", "change_type": lab, "notes": ""}
            for i, lab in enumerate(["TEMPLATE_UPDATE", "TEMPLATE_UPDATE", "HARDENING"])
        ]
    )
    dist = v.drift_distribution(drift).set_index("change_type")
    assert dist.loc["TEMPLATE_UPDATE", "count"] == 2
    assert dist.loc["CAPABILITY_ADDITION", "count"] == 0
    assert dist["count"].sum() == 3


# ---------------------------------------------------------------------------
# FMEA
# ---------------------------------------------------------------------------


def test_fmea_bins():
    assert v.occurrence_score(0.2) == 10
    assert v.occurrence_score(0.01) == 7
    assert v.occurrence_score(0.00005) == 1
    assert v.occurrence_score(float("nan")) == 1
    assert v.detection_score(0.99) == 1
    assert v.detection_score(0.55) == 6
    assert v.detection_score(0.05) == 10
    assert v.detection_score(None) == 10


def test_fmea_ranking_orders_by_rpn_and_notes_missing_data():
    prevalence = pd.DataFrame(
        {
            "category": ["REMOTE_CODE", "CREDENTIALS"],
            "contents": [73, 1000],
            "content_share": [0.0056, 0.0769],
        }
    )
    labels = signals(
        [("a", "R-RCE-001", "RISKY", ""), ("b", "R-RCE-001", "RISKY", "")]
        + [(f"n{i}", "NONE", "NONE_PRESENT", "") for i in range(9)]
        + [("m", "NONE", "MISSED_RISKY", "REMOTE_CODE")]
    )
    precision = v.precision_by_category(labels, RULES)
    recall = v.recall_estimate(labels, 40, 1000)
    fmea = v.fmea_ranking(prevalence, precision, recall, RULES)
    assert fmea["RPN"].is_monotonic_decreasing
    remote = fmea.set_index("category").loc["REMOTE_CODE"]
    # validated prevalence 0.0056 x 1.0 -> O 6; miss rate 1/10 x 1000 = 100 missed;
    # recall 73 / (73 + 100) = 0.42 -> D 7; S 9
    assert (remote["S"], remote["O"], remote["D"]) == (9, 6, 7)
    assert remote["RPN"] == 9 * 6 * 7
    cred = fmea.set_index("category").loc["CREDENTIALS"]
    assert "unvalidated prevalence" in cred["notes"]
    no_recall = v.fmea_ranking(
        prevalence, precision, v.recall_estimate(signals([]), 40, 1000), RULES
    )
    assert (no_recall["D"] == 10).all()
    assert no_recall["notes"].str.contains("no recall estimate").all()


# ---------------------------------------------------------------------------
# Kit end to end on the tiny fixture database
# ---------------------------------------------------------------------------


def test_kit_end_to_end(data_root: Path, capsys: pytest.CaptureFixture[str]):
    kit = _kit()
    ann = data_root / "data" / "annotations"

    assert kit.main(["score"]) == 0  # nothing to score yet
    assert "No label files" in capsys.readouterr().out

    assert kit.main(["sample", "--negatives", "5"]) == 0
    samples = ann / "samples"
    for name in (
        "signals_sample.csv",
        "lineage_sample.csv",
        "drift_sample.csv",
        "intra_rater_subset.csv",
        "SAMPLE_MANIFEST.json",
    ):
        assert (samples / name).exists(), name
    sample = pd.read_csv(samples / "signals_sample.csv")
    assert list(sample.columns) == ["file_sha", "stratum", "rule_ids"]
    assert set(sample["stratum"]) == {"NO_SIGNAL"}
    assert kit.main(["sample"]) == 1  # refuses to overwrite without --force

    assert kit.main(["sheet", "--rater", "jd", "--round", "1"]) == 0
    label_path = ann / "signals_jd_r1.csv"
    labels = v.read_label_csv(label_path)
    assert len(labels) == len(sample) and set(labels["rule_id"]) == {"NONE"}
    packets = list((ann / "work" / "signals_jd_r1").glob("*.md"))
    assert len(packets) == len(sample) + 1  # plus INDEX.md
    text = next(p for p in packets if p.name != "INDEX.md").read_text(encoding="utf-8")
    assert "Read only. Do not run anything" in text
    assert "```" not in text

    results = data_root / "results"
    assert kit.main(["score"]) == 0  # sheets exist but nothing labelled: no outputs
    assert "no rows are labelled" in capsys.readouterr().out
    assert not (results / "validation_recall.csv").exists()

    labels["label"] = "NONE_PRESENT"
    labels.loc[0, "label"] = "MISSED_RISKY"
    labels.loc[0, "missed_category"] = "REMOTE_CODE"
    # MISSED_RISKY is a judgement call, so it carries a written reason.
    labels.loc[0, "notes"] = "downloads and pipes a remote installer to a shell"
    labels.to_csv(label_path, index=False)
    assert kit.main(["sheet", "--rater", "jd", "--round", "1"]) == 0  # does not overwrite labels
    assert v.read_label_csv(label_path).loc[0, "label"] == "MISSED_RISKY"

    assert kit.main(["sheet", "--rater", "jd", "--round", "2", "--kind", "signals"]) == 0
    round2 = v.read_label_csv(ann / "signals_jd_r2.csv")
    subset = pd.read_csv(samples / "intra_rater_subset.csv")
    assert len(round2) == int((subset["kind"] == "signals").sum())
    merged = round2.merge(
        v.read_label_csv(label_path), on=["file_sha", "rule_id"], suffixes=("", "_r1")
    )
    round2["label"] = merged["label_r1"].tolist()
    round2["missed_category"] = merged["missed_category_r1"].tolist()
    round2["notes"] = merged["notes_r1"].tolist()
    round2.to_csv(ann / "signals_jd_r2.csv", index=False)

    assert kit.main(["status"]) == 0
    assert "signals_jd_r1.csv" in capsys.readouterr().out

    results.mkdir(exist_ok=True)
    pd.DataFrame({"category": ["REMOTE_CODE"], "contents": [1], "content_share": [0.1]}).to_csv(
        results / "pilot_skill_risk_categories.csv", index=False
    )
    assert kit.main(["score"]) == 0
    for name in (
        "validation_precision_by_rule",
        "validation_precision_by_category",
        "validation_recall",
        "validation_agreement",
        "validation_lineage",
        "validation_drift",
        "fmea_category_ranking",
    ):
        assert (results / f"{name}.csv").exists(), name
    recall = pd.read_csv(results / "validation_recall.csv").set_index("scope")
    assert recall.loc["ALL", "missed"] == 1
    assert recall.loc["ALL", "n_labelled"] == len(sample)
    agree = pd.read_csv(results / "validation_agreement.csv")
    assert agree.loc[0, "comparison"] == "intra-rater"
    assert agree.loc[0, "percent_agreement"] == 1.0

    bad = v.read_label_csv(label_path)
    bad.loc[1, "label"] = "RISKY"
    bad.to_csv(label_path, index=False)
    assert kit.main(["score"]) == 2  # problems reported, scores still written


def test_justification_required_only_for_judgement_labels():
    """Labels that contradict the detector need a written reason; agreeing ones do not."""
    frame = pd.DataFrame(
        {
            "file_sha": ["a", "b", "c", "d"],
            "rule_id": ["R-A", "R-A", "R-A", "NONE"],
            "label": ["RISKY", "NOT_PRESENT", "BENIGN_CONTEXT", "NONE_PRESENT"],
            "missed_category": ["", "", "", ""],
            "notes": ["", "", "quoted as an example of what not to do", ""],
        }
    )
    problems = v.validate_labels(frame, "signals", rule_ids=["R-A"])
    joined = " ".join(problems)
    assert "line 2" not in joined, "RISKY agrees with the rule and needs no reason"
    assert "line 5" not in joined, "NONE_PRESENT agrees with the rule and needs no reason"
    assert "line 3" in joined, "NOT_PRESENT without a reason must be reported"
    assert "line 4" not in joined, "BENIGN_CONTEXT with a reason is fine"

    cov = v.justification_coverage(frame, "signals")
    assert cov == {"owed": 2, "given": 1, "missing": 1}


def test_justification_rejects_a_token_reason():
    frame = pd.DataFrame(
        {
            "file_sha": ["a"],
            "rule_id": ["R-A"],
            "label": ["NOT_PRESENT"],
            "missed_category": [""],
            "notes": ["fp"],  # too short to be a reason
        }
    )
    problems = v.validate_labels(frame, "signals", rule_ids=["R-A"])
    assert any("needs a reason" in p for p in problems)


def test_justification_applies_to_lineage_and_drift():
    lineage = pd.DataFrame(
        {
            "file_sha_a": ["a", "b"],
            "file_sha_b": ["x", "y"],
            "same_lineage": ["YES", "UNSURE"],
            "notes": ["", ""],
        }
    )
    problems = v.validate_labels(lineage, "lineage")
    assert len(problems) == 1 and "UNSURE" in problems[0]

    drift = pd.DataFrame(
        {
            "file_sha_a": ["a", "b"],
            "file_sha_b": ["x", "y"],
            "change_type": ["TEMPLATE_UPDATE", "HARDENING"],
            "notes": ["", ""],
        }
    )
    problems = v.validate_labels(drift, "drift")
    assert len(problems) == 1 and "HARDENING" in problems[0]


def test_proposals_aggregates_false_positives_by_rule(data_root: Path, tmp_path: Path):
    """Rule-level rollup: counts and evidence generated, rater prose preserved."""
    kit = _kit()
    ann = data_root / "data" / "annotations"
    ann.mkdir(parents=True, exist_ok=True)
    rule = RULES[0].id
    pd.DataFrame(
        [
            {
                "file_sha": "aaaaaaaa11",
                "rule_id": rule,
                "label": "NOT_PRESENT",
                "missed_category": "",
                "notes": "matched inside identifier SUDO_USER",
            },
            {
                "file_sha": "bbbbbbbb22",
                "rule_id": rule,
                "label": "BENIGN_CONTEXT",
                "missed_category": "",
                "notes": "shown as an example of what not to do",
            },
            {
                "file_sha": "cccccccc33",
                "rule_id": rule,
                "label": "RISKY",
                "missed_category": "",
                "notes": "",
            },
            {
                "file_sha": "dddddddd44",
                "rule_id": "NONE",
                "label": "NONE_PRESENT",
                "missed_category": "",
                "notes": "",
            },
        ]
    ).to_csv(ann / "signals_jd_r1.csv", index=False)

    out = tmp_path / "RULE_CHANGE_PROPOSALS.md"
    assert kit.main(["proposals", "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert f"## {rule}" in text
    assert "false positives: 2" in text
    assert "observed precision: 0.33" in text  # 1 RISKY of 3 labelled matches
    assert "matched inside identifier SUDO_USER" in text
    assert "Why it misfires: TODO" in text
    assert "NONE" not in text.split("## ")[1]  # NONE rows are not a rule

    # The rater's prose survives a regeneration; the counts do not.
    out.write_text(
        text.replace("Why it misfires: TODO", "Why it misfires: matches bare tokens").replace(
            "What I would do: TODO", "What I would do: require a fenced shell block"
        ),
        encoding="utf-8",
    )
    assert kit.main(["proposals", "--out", str(out)]) == 0
    text2 = out.read_text(encoding="utf-8")
    assert "Why it misfires: matches bare tokens" in text2
    assert "What I would do: require a fenced shell block" in text2

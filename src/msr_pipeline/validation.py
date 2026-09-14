"""Validation of the P-01 risk-signal scanner: label files, agreement, precision, recall, FMEA.

Everything here is pure (DataFrames and lists in, DataFrames out) and covered by
tests/test_validation.py. Reading dataset text for annotation happens in
scripts/annotation_kit.py; nothing in the dataset is ever executed.

Label files (CSV, UTF-8) live in ``data/annotations/`` and are named
``<kind>_<rater>_r<round>.csv``:

* ``signals``: columns file_sha, rule_id, label, missed_category, notes.
  Rows for flagged items use a real rule id and a label in RISKY, BENIGN_CONTEXT,
  NOT_PRESENT. Rows for NO_SIGNAL items use rule_id NONE and a label in MISSED_RISKY,
  NONE_PRESENT; MISSED_RISKY rows name the missed capability category.
* ``lineage``: columns file_sha_a, file_sha_b, same_lineage (YES, NO, UNSURE), notes.
* ``drift``: columns file_sha_a, file_sha_b, change_type (TEMPLATE_UPDATE,
  LOCAL_ADAPTATION, HARDENING, CAPABILITY_ADDITION, UNRELATED), notes.

Rater ids are short lower-case ids such as ``jd``. Ids starting with ``llm-`` mark a
non-human rater: its agreement is reported as ``human-vs-llm`` and never counted as
human inter-rater reliability.
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

NONE_RULE = "NONE"
SIGNAL_LABELS = ("RISKY", "BENIGN_CONTEXT", "NOT_PRESENT")
NO_SIGNAL_LABELS = ("MISSED_RISKY", "NONE_PRESENT")
LINEAGE_LABELS = ("YES", "NO", "UNSURE")
DRIFT_LABELS = (
    "TEMPLATE_UPDATE",
    "LOCAL_ADAPTATION",
    "HARDENING",
    "CAPABILITY_ADDITION",
    "UNRELATED",
)
KINDS = ("signals", "lineage", "drift")
KIND_COLUMNS = {
    "signals": ["file_sha", "rule_id", "label", "missed_category", "notes"],
    "lineage": ["file_sha_a", "file_sha_b", "same_lineage", "notes"],
    "drift": ["file_sha_a", "file_sha_b", "change_type", "notes"],
}
KIND_KEYS = {
    "signals": ["file_sha", "rule_id"],
    "lineage": ["file_sha_a", "file_sha_b"],
    "drift": ["file_sha_a", "file_sha_b"],
}
KIND_LABEL_COLUMN = {"signals": "label", "lineage": "same_lineage", "drift": "change_type"}
RATER_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_FILENAME = re.compile(r"^(signals|lineage|drift)_([a-z0-9][a-z0-9-]*)_r(\d+)\.csv$")

# FMEA bins. Occurrence is scored on validated prevalence (share of distinct contents).
# Each tuple is (lower bound inclusive, score); the first bound met wins.
OCCURRENCE_BINS: tuple[tuple[float, int], ...] = (
    (0.10, 10),
    (0.05, 9),
    (0.02, 8),
    (0.01, 7),
    (0.005, 6),
    (0.002, 5),
    (0.001, 4),
    (0.0005, 3),
    (0.0001, 2),
)
# Detection is scored on estimated recall: the lower the recall, the harder a real
# capability is to detect, the higher the score.
DETECTION_BINS: tuple[tuple[float, int], ...] = (
    (0.95, 1),
    (0.90, 2),
    (0.80, 3),
    (0.70, 4),
    (0.60, 5),
    (0.50, 6),
    (0.40, 7),
    (0.30, 8),
    (0.20, 9),
)


# ---------------------------------------------------------------------------
# Label files
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LabelFile:
    path: Path
    kind: str
    rater: str
    round: int

    @property
    def is_human(self) -> bool:
        return not self.rater.startswith("llm-")

    @property
    def name(self) -> str:
        return self.path.name


def label_filename(kind: str, rater: str, round_: int) -> str:
    if kind not in KINDS:
        raise ValueError(f"unknown kind {kind!r}; expected one of {KINDS}")
    if not RATER_PATTERN.match(rater):
        raise ValueError(f"rater id {rater!r} must be lower-case letters, digits, or hyphens")
    if round_ < 1:
        raise ValueError("round must be 1 or more")
    return f"{kind}_{rater}_r{round_}.csv"


def parse_label_filename(path: Path | str) -> LabelFile | None:
    """Return a LabelFile for a conforming file name, else None."""
    path = Path(path)
    match = _FILENAME.match(path.name)
    if not match:
        return None
    return LabelFile(
        path=path, kind=match.group(1), rater=match.group(2), round=int(match.group(3))
    )


def discover_label_files(directory: Path) -> list[LabelFile]:
    if not directory.exists():
        return []
    found = [parse_label_filename(p) for p in sorted(directory.glob("*.csv"))]
    return [f for f in found if f is not None]


def read_label_csv(path: Path | str) -> pd.DataFrame:
    """Read a label file with every column as text and blanks as empty strings."""
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")


def blank_labels(kind: str, keys: pd.DataFrame) -> pd.DataFrame:
    """A label sheet with key columns filled and label columns empty."""
    df = pd.DataFrame(columns=KIND_COLUMNS[kind])
    if len(keys):
        body = {c: keys[c].astype(str).tolist() for c in KIND_KEYS[kind]}
        n = len(keys)
        for col in KIND_COLUMNS[kind]:
            if col not in body:
                body[col] = [""] * n
        df = pd.DataFrame(body, columns=KIND_COLUMNS[kind])
    return df


def labelled_rows(df: pd.DataFrame, kind: str) -> pd.DataFrame:
    col = KIND_LABEL_COLUMN[kind]
    if col not in df.columns:
        return df.iloc[0:0]
    return df[df[col].astype(str).str.strip() != ""]


def validate_labels(
    df: pd.DataFrame,
    kind: str,
    rule_ids: Iterable[str] | None = None,
    categories: Iterable[str] | None = None,
    source: str = "",
) -> list[str]:
    """Return human-readable problems. Unlabelled rows are allowed (work in progress)."""
    where = f"{source}: " if source else ""
    missing = [c for c in KIND_COLUMNS[kind] if c not in df.columns]
    if missing:
        return [f"{where}missing columns {missing}"]
    problems: list[str] = []
    keys = KIND_KEYS[kind]
    dupes = df.duplicated(subset=keys, keep=False)
    if dupes.any():
        problems.append(f"{where}{int(dupes.sum())} rows share a duplicate key {keys}")
    rule_set = set(rule_ids) if rule_ids is not None else None
    cat_set = set(categories) if categories is not None else None
    label_col = KIND_LABEL_COLUMN[kind]
    for i, row in enumerate(df.to_dict("records"), start=2):  # line 1 is the header
        label = str(row[label_col]).strip()
        if kind == "signals":
            rule = str(row["rule_id"]).strip()
            missed = str(row["missed_category"]).strip()
            if rule != NONE_RULE and rule_set is not None and rule not in rule_set:
                problems.append(f"{where}line {i}: unknown rule_id {rule!r}")
            if not label:
                continue
            allowed = NO_SIGNAL_LABELS if rule == NONE_RULE else SIGNAL_LABELS
            if label not in allowed:
                problems.append(
                    f"{where}line {i}: label {label!r} not allowed for rule_id {rule!r}; "
                    f"use one of {allowed}"
                )
            if label == "MISSED_RISKY":
                if not missed:
                    problems.append(f"{where}line {i}: MISSED_RISKY needs missed_category")
                elif cat_set is not None and missed not in cat_set:
                    problems.append(f"{where}line {i}: unknown missed_category {missed!r}")
            elif missed:
                problems.append(f"{where}line {i}: missed_category only goes with MISSED_RISKY")
        else:
            if not label:
                continue
            allowed = LINEAGE_LABELS if kind == "lineage" else DRIFT_LABELS
            if label not in allowed:
                problems.append(f"{where}line {i}: {label_col} {label!r} not in {allowed}")
    return problems


def valid_labelled_rows(df: pd.DataFrame, kind: str) -> pd.DataFrame:
    """Labelled rows whose label value is allowed for the row (invalid rows dropped)."""
    rows = labelled_rows(df, kind)
    col = KIND_LABEL_COLUMN[kind]
    if kind == "signals":
        is_none = rows["rule_id"].astype(str).str.strip() == NONE_RULE
        label = rows[col].astype(str).str.strip()
        ok = (is_none & label.isin(NO_SIGNAL_LABELS)) | (~is_none & label.isin(SIGNAL_LABELS))
        return rows[ok]
    allowed = LINEAGE_LABELS if kind == "lineage" else DRIFT_LABELS
    return rows[rows[col].astype(str).str.strip().isin(allowed)]


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion; (nan, nan) when n is 0."""
    if n <= 0:
        return (math.nan, math.nan)
    p = successes / n
    z2 = z * z
    denom = 1 + z2 / n
    centre = (p + z2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def percent_agreement(labels_a: Sequence[str], labels_b: Sequence[str]) -> float:
    if len(labels_a) != len(labels_b):
        raise ValueError("label sequences must have the same length")
    if not labels_a:
        return math.nan
    return float(np.mean([a == b for a, b in zip(labels_a, labels_b, strict=True)]))


def cohen_kappa(labels_a: Sequence[str], labels_b: Sequence[str]) -> tuple[float, str]:
    """Cohen's kappa for two raters over matched items.

    Returns (kappa, note). The note is empty for a normal result and explains why kappa
    is undefined (nan) otherwise, for example when both raters used a single category.
    """
    if len(labels_a) != len(labels_b):
        raise ValueError("label sequences must have the same length")
    n = len(labels_a)
    if n == 0:
        return (math.nan, "no matched items")
    cats = sorted(set(labels_a) | set(labels_b))
    index = {c: i for i, c in enumerate(cats)}
    table = np.zeros((len(cats), len(cats)))
    for a, b in zip(labels_a, labels_b, strict=True):
        table[index[a], index[b]] += 1
    po = np.trace(table) / n
    pe = float(np.sum(table.sum(axis=1) * table.sum(axis=0))) / (n * n)
    if math.isclose(pe, 1.0):
        return (math.nan, "undefined: both raters used a single category")
    return (float((po - pe) / (1 - pe)), "")


def _rule_maps(rules) -> tuple[dict[str, str], dict[str, int]]:
    return {r.id: r.category for r in rules}, {r.id: r.severity for r in rules}


def _precision_row(risky: int, benign: int, not_present: int) -> dict:
    n = risky + benign + not_present
    strict = wilson_ci(risky, n)
    capability = wilson_ci(risky + benign, n)
    return {
        "n": n,
        "risky": risky,
        "benign_context": benign,
        "not_present": not_present,
        "strict_precision": risky / n if n else math.nan,
        "strict_ci_low": strict[0],
        "strict_ci_high": strict[1],
        "capability_precision": (risky + benign) / n if n else math.nan,
        "capability_ci_low": capability[0],
        "capability_ci_high": capability[1],
    }


def precision_by_rule(
    signal_labels: pd.DataFrame, rules, high_risk_severity: int = 6
) -> pd.DataFrame:
    """Strict (RISKY) and capability (RISKY or BENIGN_CONTEXT) precision per rule.

    Includes every rule with severity at or above ``high_risk_severity`` plus any other
    rule that has labels. Unlabelled rules have n = 0 and nan precision.
    """
    category, severity = _rule_maps(rules)
    rows = valid_labelled_rows(signal_labels, "signals")
    rows = rows[rows["rule_id"] != NONE_RULE]
    counts = rows.groupby(["rule_id", "label"]).size().unstack(fill_value=0)
    rule_order = [r.id for r in rules if r.severity >= high_risk_severity]
    rule_order += [rid for rid in counts.index if rid not in rule_order]
    out = []
    for rid in rule_order:
        c = counts.loc[rid] if rid in counts.index else {}
        out.append(
            {
                "rule_id": rid,
                "category": category.get(rid, ""),
                "severity": severity.get(rid, math.nan),
                **_precision_row(
                    int(c.get("RISKY", 0)),
                    int(c.get("BENIGN_CONTEXT", 0)),
                    int(c.get("NOT_PRESENT", 0)),
                ),
            }
        )
    return pd.DataFrame(out)


def precision_by_category(
    signal_labels: pd.DataFrame, rules, high_risk_severity: int = 6
) -> pd.DataFrame:
    """Precision per capability category, counted once per item.

    An item's label for a category is RISKY if any of its rule rows in that category is
    RISKY, else BENIGN_CONTEXT if any is, else NOT_PRESENT.
    """
    category, _ = _rule_maps(rules)
    rows = valid_labelled_rows(signal_labels, "signals")
    rows = rows[rows["rule_id"] != NONE_RULE].assign(
        category=lambda d: d["rule_id"].map(category).fillna("")
    )
    rank = {"RISKY": 2, "BENIGN_CONTEXT": 1, "NOT_PRESENT": 0}
    names = {v: k for k, v in rank.items()}
    max_sev: dict[str, int] = {}
    for r in rules:
        max_sev[r.category] = max(max_sev.get(r.category, 0), r.severity)
    order = sorted(c for c, s in max_sev.items() if s >= high_risk_severity)
    item_labels = pd.Series(dtype=str)
    if len(rows):
        item_labels = (
            rows.assign(rank=rows["label"].map(rank))
            .groupby(["category", "file_sha"])["rank"]
            .max()
            .map(names)
        )
    out = []
    for cat in order + [c for c in sorted({k[0] for k in item_labels.index}) if c not in order]:
        labels = item_labels.loc[cat] if cat in item_labels.index.get_level_values(0) else []
        labels = list(labels)
        out.append(
            {
                "category": cat,
                "max_rule_severity": max_sev.get(cat, math.nan),
                **_precision_row(
                    labels.count("RISKY"),
                    labels.count("BENIGN_CONTEXT"),
                    labels.count("NOT_PRESENT"),
                ),
            }
        )
    return pd.DataFrame(out)


def recall_estimate(
    signal_labels: pd.DataFrame, no_signal_stratum_size: int, population_no_signal_count: int
) -> pd.DataFrame:
    """Miss rate among NO_SIGNAL items and the implied number of missed contents.

    Row ``ALL`` covers any missed high-risk capability; one further row per
    ``missed_category``. Population estimates scale the rate and its Wilson interval by
    ``population_no_signal_count``. Contents that matched only low-severity rules are
    outside this estimate (a stated limitation).
    """
    rows = valid_labelled_rows(signal_labels, "signals")
    rows = rows[rows["rule_id"] == NONE_RULE]
    n = len(rows)
    missed = rows[rows["label"] == "MISSED_RISKY"]

    def row(scope: str, k: int) -> dict:
        low, high = wilson_ci(k, n)
        rate = k / n if n else math.nan
        return {
            "scope": scope,
            "n_labelled": n,
            "stratum_size": no_signal_stratum_size,
            "missed": k,
            "miss_rate": rate,
            "ci_low": low,
            "ci_high": high,
            "population_no_signal": population_no_signal_count,
            "est_missed": rate * population_no_signal_count if n else math.nan,
            "est_missed_low": low * population_no_signal_count if n else math.nan,
            "est_missed_high": high * population_no_signal_count if n else math.nan,
        }

    out = [row("ALL", len(missed))]
    for cat, k in missed["missed_category"].value_counts().sort_index().items():
        out.append(row(str(cat), int(k)))
    return pd.DataFrame(out)


def classify_comparison(a: LabelFile, b: LabelFile) -> str | None:
    """intra-rater, inter-rater, human-vs-llm, or None when the pair is not compared."""
    if a.kind != b.kind:
        return None
    if a.is_human != b.is_human:
        return "human-vs-llm"
    if not a.is_human:
        return None
    if a.rater == b.rater and a.round != b.round:
        return "intra-rater"
    if a.rater != b.rater and a.round == b.round:
        return "inter-rater"
    return None


def agreement(files: Sequence[tuple[LabelFile, pd.DataFrame]]) -> pd.DataFrame:
    """Kappa and percent agreement for every comparable pair of label files."""
    cols = [
        "kind",
        "comparison",
        "file_a",
        "file_b",
        "n",
        "percent_agreement",
        "kappa",
        "kappa_note",
    ]
    out = []
    for (fa, da), (fb, db) in combinations(files, 2):
        comparison = classify_comparison(fa, fb)
        if comparison is None:
            continue
        kind = fa.kind
        keys, col = KIND_KEYS[kind], KIND_LABEL_COLUMN[kind]
        left = valid_labelled_rows(da, kind)[keys + [col]]
        right = valid_labelled_rows(db, kind)[keys + [col]]
        merged = left.merge(right, on=keys, suffixes=("_a", "_b"))
        a = merged[f"{col}_a"].str.strip().tolist()
        b = merged[f"{col}_b"].str.strip().tolist()
        kappa, note = cohen_kappa(a, b)
        out.append(
            {
                "kind": kind,
                "comparison": comparison,
                "file_a": fa.name,
                "file_b": fb.name,
                "n": len(merged),
                "percent_agreement": percent_agreement(a, b),
                "kappa": kappa,
                "kappa_note": note,
            }
        )
    return pd.DataFrame(out, columns=cols)


def lineage_precision(lineage_labels: pd.DataFrame) -> pd.DataFrame:
    """Share of labelled pairs judged YES among YES or NO; UNSURE reported separately."""
    rows = valid_labelled_rows(lineage_labels, "lineage")
    labels = rows["same_lineage"].str.strip()
    yes, no, unsure = (
        int((labels == "YES").sum()),
        int((labels == "NO").sum()),
        int((labels == "UNSURE").sum()),
    )
    decided = yes + no
    low, high = wilson_ci(yes, decided)
    return pd.DataFrame(
        [
            {
                "n_labelled": len(rows),
                "yes": yes,
                "no": no,
                "unsure": unsure,
                "lineage_precision": yes / decided if decided else math.nan,
                "ci_low": low,
                "ci_high": high,
                "share_unsure": unsure / len(rows) if len(rows) else math.nan,
            }
        ]
    )


def drift_distribution(drift_labels: pd.DataFrame) -> pd.DataFrame:
    rows = valid_labelled_rows(drift_labels, "drift")
    counts = rows["change_type"].str.strip().value_counts()
    n = len(rows)
    out = []
    for label in DRIFT_LABELS:
        k = int(counts.get(label, 0))
        low, high = wilson_ci(k, n)
        out.append(
            {
                "change_type": label,
                "count": k,
                "share": k / n if n else math.nan,
                "ci_low": low,
                "ci_high": high,
            }
        )
    return pd.DataFrame(out)


# ---------------------------------------------------------------------------
# FMEA
# ---------------------------------------------------------------------------


def occurrence_score(prevalence: float) -> int:
    """Map a validated prevalence share (0 to 1) to 1-10 using OCCURRENCE_BINS."""
    if prevalence is None or (isinstance(prevalence, float) and math.isnan(prevalence)):
        return 1
    for bound, score in OCCURRENCE_BINS:
        if prevalence >= bound:
            return score
    return 1


def detection_score(recall: float | None) -> int:
    """Map estimated recall (0 to 1) to 1-10 using DETECTION_BINS; missing recall is 10."""
    if recall is None or (isinstance(recall, float) and math.isnan(recall)):
        return 10
    for bound, score in DETECTION_BINS:
        if recall >= bound:
            return score
    return 10


def fmea_ranking(
    category_prevalence_df: pd.DataFrame,
    precision_df: pd.DataFrame,
    recall_df: pd.DataFrame,
    rules,
    high_risk_severity: int = 6,
) -> pd.DataFrame:
    """Rank high-risk capability categories by RPN = S x O x D.

    * S: maximum rule severity in the category (from the rule file).
    * O: ``occurrence_score(content_share x capability_precision)``; if the category has
      no labels, the unvalidated content share is used and noted.
    * D: ``detection_score(recall)`` where recall is estimated as
      detected / (detected + missed), detected = contents x capability_precision and
      missed = the category's miss rate among NO_SIGNAL items x the NO_SIGNAL population.
      When no NO_SIGNAL items are labelled, D = 10 with the note "no recall estimate".
    """
    max_sev: dict[str, int] = {}
    for r in rules:
        max_sev[r.category] = max(max_sev.get(r.category, 0), r.severity)
    prev = (
        category_prevalence_df.set_index("category")
        if len(category_prevalence_df)
        else pd.DataFrame()
    )
    prec = precision_df.set_index("category") if len(precision_df) else pd.DataFrame()
    recall_all = recall_df[recall_df["scope"] == "ALL"] if len(recall_df) else recall_df
    have_recall = len(recall_all) and int(recall_all["n_labelled"].iloc[0]) > 0
    by_scope = recall_df.set_index("scope") if len(recall_df) else pd.DataFrame()
    out = []
    for cat in sorted(c for c, s in max_sev.items() if s >= high_risk_severity):
        notes = []
        share = float(prev.loc[cat, "content_share"]) if cat in prev.index else math.nan
        contents = (
            float(prev.loc[cat, "contents"])
            if cat in prev.index and "contents" in prev.columns
            else math.nan
        )
        cap = math.nan
        if cat in prec.index and int(prec.loc[cat, "n"]) > 0:
            cap = float(prec.loc[cat, "capability_precision"])
        if math.isnan(share):
            notes.append("no prevalence")
        if math.isnan(cap):
            notes.append("unvalidated prevalence")
            validated = share
        else:
            validated = share * cap
        recall = math.nan
        if have_recall:
            miss_rate = float(by_scope.loc[cat, "miss_rate"]) if cat in by_scope.index else 0.0
            population = float(recall_all["population_no_signal"].iloc[0])
            detected = contents * (cap if not math.isnan(cap) else 1.0)
            missed = miss_rate * population
            if not math.isnan(detected) and detected + missed > 0:
                recall = detected / (detected + missed)
        else:
            notes.append("no recall estimate")
        s = max_sev[cat]
        o = occurrence_score(validated)
        d = detection_score(recall)
        out.append(
            {
                "category": cat,
                "S": s,
                "validated_prevalence": validated,
                "O": o,
                "estimated_recall": recall,
                "D": d,
                "RPN": s * o * d,
                "notes": "; ".join(notes),
            }
        )
    df = pd.DataFrame(
        out,
        columns=[
            "category",
            "S",
            "validated_prevalence",
            "O",
            "estimated_recall",
            "D",
            "RPN",
            "notes",
        ],
    )
    return df.sort_values(["RPN", "S", "category"], ascending=[False, False, True]).reset_index(
        drop=True
    )

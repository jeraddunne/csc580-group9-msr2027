"""P-01 research analysis: prevalence, reach, and drift of risk signals in GitSkills.

``python -m msr_pipeline analyze`` runs the whole analysis on the GitSkills sample and
writes every table to ``results/`` and every figure to ``figures/``. The functions
below are pure (DataFrames in, DataFrames out) so the tests can run them on synthetic
data. Nothing found in the dataset is executed, imported, or fetched.

Design decisions (see RESEARCH_QUESTION.md and DATA_DICTIONARY.md Part B):

- Unit of analysis: one distinct content (``file_sha``). Copies are an outcome.
- Main population: representatives with content, excluding symlink stubs.
- High risk: at least one matching rule with severity 6 or more. Cutoffs 5 and 7 are
  derived from the stored rule ids without rescanning.
- RQ2 model: negative binomial (NB2, statsmodels ``discrete.NegativeBinomial``) of
  additional copies (``copies - 1``) on the high-risk flag and controls taken from the
  representative row and its repository row. NB2 estimates the dispersion parameter
  instead of fixing it, which matters for the heavy-tailed copy counts.
- RQ3 lineage: same front-matter name and word-shingle Jaccard similarity at or above a
  threshold (0.5 main, swept from 0.3 to 0.8).
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import time
import warnings
from collections.abc import Callable, Iterable, Sequence
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from . import skill_risk  # noqa: E402
from .config import Paths, get_paths, repo_root  # noqa: E402

MAIN_CUTOFF = skill_risk.HIGH_RISK_SEVERITY
SEVERITY_CUTOFFS = (5, 6, 7)
SIMILARITY_THRESHOLDS = (0.3, 0.4, 0.5, 0.6, 0.7, 0.8)
MAIN_SIMILARITY = 0.5
MIN_CATEGORY_CONTENTS = 30
N_BOOT = 2000
DEFAULT_SEED = 580
TOP_LANGUAGES = 8
EXCLUDE_TOP_COPIED = 10
Z_95 = 1.959963984540054

# Names of the example skills Anthropic published as starting points. They are copied
# and edited widely, so differences between their variants often reflect template
# updates rather than local changes. Used only to label and exclude families.
TEMPLATE_FAMILIES = frozenset(
    {
        "algorithmic-art",
        "artifacts-builder",
        "brand-guidelines",
        "canvas-design",
        "docx",
        "frontend-design",
        "internal-comms",
        "mcp-builder",
        "pdf",
        "pptx",
        "skill-creator",
        "slack-gif-creator",
        "template-skill",
        "theme-factory",
        "webapp-testing",
        "xlsx",
    }
)

OUTPUT_TABLES = (
    "population_flow",
    "rq1_prevalence_by_rule",
    "rq1_prevalence_by_category",
    "rq2_reach_summary",
    "rq2_mannwhitney",
    "rq2_bootstrap",
    "rq2_negbin",
    "rq2_category_tests",
    "rq3_threshold_sweep",
    "rq3_summary",
    "rq3_lineage_pairs",
    "rq3_differing_pairs",
    "scripts_summary",
    "sensitivity_summary",
)
OUTPUT_FIGURES = (
    "rq1_prevalence_by_category",
    "rq2_copies_by_group",
    "rq3_threshold_sweep",
)

_split = skill_risk._split


# ---------------------------------------------------------------------------
# Statistics helpers
# ---------------------------------------------------------------------------


def wilson_ci(successes: float, n: float, z: float = Z_95) -> tuple[float, float]:
    """Wilson score interval for a proportion. Returns (nan, nan) when n is 0."""
    if n <= 0:
        return (math.nan, math.nan)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def rank_biserial(u_statistic: float, n1: int, n2: int) -> float:
    """Rank-biserial correlation from the Mann-Whitney U of the first sample.

    Positive values mean the first sample tends to be larger; the range is -1 to 1.
    """
    if n1 == 0 or n2 == 0:
        return math.nan
    return 2.0 * float(u_statistic) / (n1 * n2) - 1.0


def _mean(values: np.ndarray) -> float:
    return float(np.mean(values)) if len(values) else math.nan


def _median(values: np.ndarray) -> float:
    return float(np.median(values)) if len(values) else math.nan


def mann_whitney(group: Iterable[float], reference: Iterable[float]) -> dict:
    """Two-sided Mann-Whitney U test of ``group`` against ``reference``."""
    from scipy.stats import mannwhitneyu

    x = np.asarray(list(group), dtype=float)
    y = np.asarray(list(reference), dtype=float)
    out = {
        "n_group": int(len(x)),
        "n_reference": int(len(y)),
        "median_group": _median(x),
        "median_reference": _median(y),
        "mean_group": _mean(x),
        "mean_reference": _mean(y),
        "u_statistic": math.nan,
        "p_value": math.nan,
        "rank_biserial": math.nan,
        "status": "insufficient data",
    }
    if len(x) < 2 or len(y) < 2:
        return out
    if np.all(x == x[0]) and np.all(y == x[0]):
        out.update(u_statistic=len(x) * len(y) / 2, p_value=1.0, rank_biserial=0.0, status="ok")
        return out
    res = mannwhitneyu(x, y, alternative="two-sided")
    out.update(
        u_statistic=float(res.statistic),
        p_value=float(res.pvalue),
        rank_biserial=rank_biserial(res.statistic, len(x), len(y)),
        status="ok",
    )
    return out


def holm_adjust(p_values: Sequence[float]) -> list[float]:
    """Holm step-down adjusted p-values. NaN inputs stay NaN and are not counted."""
    p = [float(v) for v in p_values]
    idx = [i for i, v in enumerate(p) if not math.isnan(v)]
    order = sorted(idx, key=lambda i: p[i])
    m = len(order)
    adjusted = [math.nan] * len(p)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * p[i]))
        adjusted[i] = running
    return adjusted


def row_mean(samples: np.ndarray) -> np.ndarray:
    return samples.mean(axis=1)


def row_share_at_least(k: int) -> Callable[[np.ndarray], np.ndarray]:
    def statistic(samples: np.ndarray) -> np.ndarray:
        return (samples >= k).mean(axis=1)

    return statistic


def bootstrap_difference(
    group: Iterable[float],
    reference: Iterable[float],
    statistic: Callable[[np.ndarray], np.ndarray],
    n_boot: int = N_BOOT,
    seed: int = DEFAULT_SEED,
    chunk: int = 100,
) -> dict:
    """Percentile bootstrap CI for statistic(group) minus statistic(reference).

    Each group is resampled independently with replacement. ``statistic`` maps a
    2-D array of resamples (one per row) to a 1-D array.
    """
    x = np.asarray(list(group), dtype=float)
    y = np.asarray(list(reference), dtype=float)
    out = {
        "estimate": math.nan,
        "ci_low": math.nan,
        "ci_high": math.nan,
        "n_boot": int(n_boot),
        "seed": int(seed),
        "status": "insufficient data",
    }
    if len(x) == 0 or len(y) == 0:
        return out
    rng = np.random.default_rng(seed)
    estimate = float(statistic(x[None, :])[0] - statistic(y[None, :])[0])
    diffs = np.empty(n_boot)
    done = 0
    while done < n_boot:
        k = min(chunk, n_boot - done)
        bx = x[rng.integers(0, len(x), size=(k, len(x)))]
        by = y[rng.integers(0, len(y), size=(k, len(y)))]
        diffs[done : done + k] = statistic(bx) - statistic(by)
        done += k
    low, high = np.percentile(diffs, [2.5, 97.5])
    out.update(estimate=estimate, ci_low=float(low), ci_high=float(high), status="ok")
    return out


# ---------------------------------------------------------------------------
# Population and frames
# ---------------------------------------------------------------------------


def with_severity_cutoff(
    scan: pd.DataFrame, rules: list[skill_risk.Rule], cutoff: int
) -> pd.DataFrame:
    """Recompute high-risk columns from stored rule ids for another severity cutoff."""
    by_id = {r.id: r for r in rules}

    def high(ids: str) -> str:
        cats = {
            by_id[i].category for i in _split(ids) if i in by_id and by_id[i].severity >= cutoff
        }
        return ";".join(sorted(cats))

    out = scan.copy()
    out["high_risk_categories"] = out["rule_ids"].fillna("").astype(str).map(high)
    out["high_risk"] = out["high_risk_categories"] != ""
    return out


def population_flow(
    reps: pd.DataFrame, flags: pd.DataFrame, occurrences: pd.DataFrame
) -> pd.DataFrame:
    """How many distinct contents and occurrences survive each inclusion step."""
    counts = skill_risk.copy_counts(occurrences)
    f = flags.merge(counts, on="file_sha", how="left")
    f["copies"] = f["copies"].fillna(1).astype(int)
    steps = [
        (
            "all_occurrences",
            "Every SKILL.md occurrence in the sample",
            int(counts["file_sha"].nunique()) if len(counts) else int(len(reps)),
            int(len(occurrences)),
        ),
        (
            "with_content",
            "Distinct contents whose representative text was fetched",
            int(f["has_content"].sum()),
            int(f.loc[f["has_content"], "copies"].sum()),
        ),
        (
            "excluded_symlink_stubs",
            "Excluded: content is a single path-like line (symlink target)",
            int(f["is_symlink_stub"].sum()),
            int(f.loc[f["is_symlink_stub"], "copies"].sum()),
        ),
        (
            "excluded_unrecovered_content",
            "Excluded: content changed before it was fetched and was not recovered "
            "(content_sha_ok not 1 or 2)",
            int((~f["content_recovered"]).sum()),
            int(f.loc[~f["content_recovered"], "copies"].sum()),
        ),
        (
            "main_population",
            "Main population: with recovered content, not a symlink stub",
            int(f["in_main_population"].sum()),
            int(f.loc[f["in_main_population"], "copies"].sum()),
        ),
        (
            "frontmatter_valid_subset",
            "Sensitivity subset: main population with valid YAML front matter",
            int((f["in_main_population"] & f["frontmatter_valid"]).sum()),
            int(f.loc[f["in_main_population"] & f["frontmatter_valid"], "copies"].sum()),
        ),
    ]
    return pd.DataFrame(steps, columns=["step", "description", "distinct_contents", "occurrences"])


CONTROL_COLUMNS = ["body_chars", "has_scripts", "location_class", "stars", "language"]


def build_frame(
    scan: pd.DataFrame, counts: pd.DataFrame, reps: pd.DataFrame, flags: pd.DataFrame
) -> pd.DataFrame:
    """Scan results joined with copy counts, controls, and population flags."""
    controls = reps.reindex(columns=["file_sha", *CONTROL_COLUMNS])
    frame = skill_risk._with_counts(scan, counts)
    frame = frame.merge(controls, on="file_sha", how="left")
    frame = frame.merge(flags[["file_sha", "frontmatter_valid"]], on="file_sha", how="left")
    frame["frontmatter_valid"] = frame["frontmatter_valid"].fillna(False).astype(bool)
    frame["high_risk"] = frame["high_risk"].astype(bool)
    return frame


# ---------------------------------------------------------------------------
# RQ1
# ---------------------------------------------------------------------------


def _add_wilson(table: pd.DataFrame, n: int) -> pd.DataFrame:
    cis = [wilson_ci(k, n) for k in table["contents"]]
    out = table.copy()
    out["content_ci_low"] = [round(lo, 4) if not math.isnan(lo) else lo for lo, _ in cis]
    out["content_ci_high"] = [round(hi, 4) if not math.isnan(hi) else hi for _, hi in cis]
    return out


def rq1_tables(
    scan: pd.DataFrame, counts: pd.DataFrame, rules: list[skill_risk.Rule]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    n = len(scan)
    by_rule = _add_wilson(skill_risk.rule_prevalence(scan, counts, rules), n)
    by_category = _add_wilson(skill_risk.category_prevalence(scan, counts, rules), n)
    by_category = by_category.merge(high_risk_by_category(scan, counts, rules), on="category")
    by_category = by_category.sort_values(
        ["high_risk_share", "content_share"], ascending=[False, False]
    ).reset_index(drop=True)
    return by_rule, by_category


def high_risk_by_category(
    scan: pd.DataFrame, counts: pd.DataFrame, rules: list[skill_risk.Rule]
) -> pd.DataFrame:
    """Per category, contents matching a rule at or above the high-risk cutoff.

    `category_prevalence` counts any rule in a category, including low-severity context
    rules (for example an `allowed-tools` declaration). This table counts only the
    high-risk rules, so mixed categories are not overstated.
    """
    merged = scan.merge(counts, on="file_sha", how="left")
    copies = merged["copies"].fillna(1).astype(int)
    n, n_occ = len(merged), int(copies.sum())
    rows = []
    for cat in sorted({r.category for r in rules}):
        mask = (
            merged["high_risk_categories"]
            .fillna("")
            .astype(str)
            .map(lambda s, c=cat: c in _split(s))
        )
        k = int(mask.sum())
        occ = int(copies[mask].sum())
        lo, hi = wilson_ci(k, n)
        rows.append(
            {
                "category": cat,
                "high_risk_contents": k,
                "high_risk_share": round(k / n, 4) if n else 0.0,
                "high_risk_ci_low": lo if math.isnan(lo) else round(lo, 4),
                "high_risk_ci_high": hi if math.isnan(hi) else round(hi, 4),
                "high_risk_occurrences": occ,
                "high_risk_occurrence_share": round(occ / n_occ, 4) if n_occ else 0.0,
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# RQ2
# ---------------------------------------------------------------------------


def rq2_reach_summary(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    hr = frame["high_risk"].astype(bool)
    for label, mask in (("high-risk signal", hr), ("no high-risk signal", ~hr)):
        g = frame[mask]
        n = len(g)

        def share(cond: pd.Series, n: int = n) -> float:
            return round(float(cond.sum()) / n, 4) if n else 0.0

        rows.append(
            {
                "group": label,
                "contents": n,
                "occurrences": int(g["copies"].sum()),
                "mean_copies": round(float(g["copies"].mean()), 3) if n else math.nan,
                "median_copies": float(g["copies"].median()) if n else math.nan,
                "share_copied_2plus": share(g["copies"] >= 2),
                "share_copied_5plus": share(g["copies"] >= 5),
                "share_copied_10plus": share(g["copies"] >= 10),
                "share_cross_repo": share(g["repos"] >= 2),
                "max_copies": int(g["copies"].max()) if n else 0,
            }
        )
    return pd.DataFrame(rows)


def rq2_mannwhitney(frame: pd.DataFrame) -> pd.DataFrame:
    hr = frame["high_risk"].astype(bool)
    rows = []
    for outcome in ("copies", "repos"):
        res = mann_whitney(frame.loc[hr, outcome], frame.loc[~hr, outcome])
        rows.append({"outcome": outcome, "group": "high-risk signal", **res})
    return pd.DataFrame(rows)


def rq2_bootstrap(frame: pd.DataFrame, n_boot: int = N_BOOT, seed: int = DEFAULT_SEED):
    hr = frame["high_risk"].astype(bool)
    x, y = frame.loc[hr, "copies"], frame.loc[~hr, "copies"]
    rows = [
        {
            "metric": "difference_in_mean_copies",
            **bootstrap_difference(x, y, row_mean, n_boot=n_boot, seed=seed),
        },
        {
            "metric": "difference_in_share_copied_2plus",
            **bootstrap_difference(x, y, row_share_at_least(2), n_boot=n_boot, seed=seed),
        },
    ]
    return pd.DataFrame(rows)


def negbin_design(
    frame: pd.DataFrame, top_languages: int = TOP_LANGUAGES
) -> tuple[pd.Series, pd.DataFrame, dict[str, str]]:
    """Outcome (copies - 1) and design matrix with a constant for the NB2 model."""
    y = pd.to_numeric(frame["copies"], errors="coerce").fillna(1).astype(float) - 1.0
    X = pd.DataFrame(index=frame.index)
    X["const"] = 1.0
    X["high_risk"] = frame["high_risk"].astype(bool).astype(float)
    body = pd.to_numeric(frame.get("body_chars"), errors="coerce").fillna(0).clip(lower=0)
    X["log1p_body_chars"] = np.log1p(body)
    scripts = pd.to_numeric(frame.get("has_scripts"), errors="coerce").fillna(0)
    X["has_scripts"] = (scripts > 0).astype(float)
    stars = pd.to_numeric(frame.get("stars"), errors="coerce").fillna(0).clip(lower=0)
    X["log1p_stars"] = np.log1p(stars)
    loc = frame.get("location_class", pd.Series(index=frame.index, dtype=object))
    loc = loc.fillna("unknown").astype(str)
    loc_base = loc.value_counts().idxmax() if len(loc) else "unknown"
    for value in sorted(set(loc) - {loc_base}):
        X[f"location_{value}"] = (loc == value).astype(float)
    lang = frame.get("language", pd.Series(index=frame.index, dtype=object))
    lang = lang.fillna("").astype(str).replace("", "(none)")
    top = set(lang.value_counts().head(top_languages).index)
    lang = lang.where(lang.isin(top), "other")
    lang_base = lang.value_counts().idxmax() if len(lang) else "(none)"
    for value in sorted(set(lang) - {lang_base}):
        X[f"language_{value}"] = (lang == value).astype(float)
    return y, X, {"location_baseline": loc_base, "language_baseline": lang_base}


NEGBIN_COLUMNS = [
    "term",
    "coef",
    "irr",
    "irr_ci_low",
    "irr_ci_high",
    "p_value",
    "n",
    "status",
    "note",
]


def rq2_negbin(frame: pd.DataFrame) -> pd.DataFrame:
    """NB2 regression of additional copies on high_risk plus controls.

    Returns one row per term. Estimation failures return a single ``high_risk`` row
    with status "not estimable" and the error text instead of raising.
    """
    try:
        import statsmodels.api as sm

        y, X, baselines = negbin_design(frame)
        if len(y) < X.shape[1] + 5:
            raise ValueError(f"too few rows ({len(y)}) for {X.shape[1]} parameters")
        if X["high_risk"].nunique() < 2:
            raise ValueError("high_risk has no variation")
        if y.nunique() < 2:
            raise ValueError("outcome has no variation")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = sm.NegativeBinomial(y, X).fit(disp=0, maxiter=300)
            ci = result.conf_int()
        params = result.params
        if not np.all(np.isfinite(params.to_numpy())):
            raise ValueError("non-finite parameter estimates")
        converged = bool(result.mle_retvals.get("converged", False))
        alpha = float(params.get("alpha", math.nan))
        note = (
            f"NB2 (statsmodels discrete NegativeBinomial); outcome = copies - 1; "
            f"baselines: location={baselines['location_baseline']}, "
            f"language={baselines['language_baseline']}; alpha={alpha:.4f}; "
            f"converged={converged}"
        )
        status = "ok" if converged else "not converged"
        rows = []
        for term in params.index:
            is_alpha = term == "alpha"
            coef = float(params[term])
            rows.append(
                {
                    "term": term,
                    "coef": coef,
                    "irr": math.nan if is_alpha else math.exp(coef),
                    "irr_ci_low": math.nan if is_alpha else math.exp(float(ci.loc[term, 0])),
                    "irr_ci_high": math.nan if is_alpha else math.exp(float(ci.loc[term, 1])),
                    "p_value": float(result.pvalues[term]),
                    "n": int(len(y)),
                    "status": status,
                    "note": note,
                }
            )
        return pd.DataFrame(rows, columns=NEGBIN_COLUMNS)
    except Exception as exc:  # noqa: BLE001 - any estimation failure is reported, not raised
        row = dict.fromkeys(NEGBIN_COLUMNS, math.nan)
        row.update(
            term="high_risk",
            n=int(len(frame)),
            status="not estimable",
            note=f"{type(exc).__name__}: {exc}",
        )
        return pd.DataFrame([row], columns=NEGBIN_COLUMNS)


def rq2_category_tests(
    frame: pd.DataFrame,
    rules: list[skill_risk.Rule],
    cutoff: int = MAIN_CUTOFF,
    min_contents: int = MIN_CATEGORY_CONTENTS,
) -> pd.DataFrame:
    """Per high-risk category: copies versus contents with no high-risk signal (Holm)."""
    categories = sorted({r.category for r in rules if r.severity >= cutoff})
    hr = frame["high_risk"].astype(bool)
    reference = frame.loc[~hr, "copies"]
    rows = []
    for cat in categories:
        mask = frame["high_risk_categories"].fillna("").map(lambda s, c=cat: c in _split(s))
        n = int(mask.sum())
        row = {
            "category": cat,
            "contents": n,
            "reference_contents": int(len(reference)),
            "tested": n >= min_contents,
            "mean_copies": _mean(frame.loc[mask, "copies"].to_numpy(dtype=float)),
            "reference_mean_copies": _mean(reference.to_numpy(dtype=float)),
            "u_statistic": math.nan,
            "p_value": math.nan,
            "rank_biserial": math.nan,
        }
        if row["tested"]:
            res = mann_whitney(frame.loc[mask, "copies"], reference)
            row.update(
                u_statistic=res["u_statistic"],
                p_value=res["p_value"],
                rank_biserial=res["rank_biserial"],
            )
        rows.append(row)
    table = pd.DataFrame(rows)
    if table.empty:
        return pd.DataFrame(
            columns=[
                "category",
                "contents",
                "reference_contents",
                "tested",
                "mean_copies",
                "reference_mean_copies",
                "u_statistic",
                "p_value",
                "rank_biserial",
                "p_holm",
                "significant_holm_05",
            ]
        )
    table["p_holm"] = holm_adjust(table["p_value"].tolist())
    table["significant_holm_05"] = table["p_holm"].map(
        lambda p: bool(p < 0.05) if not math.isnan(p) else False
    )
    return table


# ---------------------------------------------------------------------------
# RQ3
# ---------------------------------------------------------------------------


def mark_templates(pairs: pd.DataFrame) -> pd.DataFrame:
    out = pairs.copy()
    out["is_template_family"] = out["family"].astype(str).isin(TEMPLATE_FAMILIES)
    return out


def _pair_counts(pairs: pd.DataFrame) -> dict[str, int]:
    if pairs.empty:
        return {
            "lineage_pairs": 0,
            "families": 0,
            "differing_pairs": 0,
            "families_with_differences": 0,
            "ordered_pairs": 0,
            "ordered_newer_adds": 0,
            "ordered_newer_drops": 0,
        }
    ordered = pairs["ordered"].astype(bool)
    differs = pairs["differs"].astype(bool)
    return {
        "lineage_pairs": int(len(pairs)),
        "families": int(pairs["family"].nunique()),
        "differing_pairs": int(differs.sum()),
        "families_with_differences": int(pairs.loc[differs, "family"].nunique()),
        "ordered_pairs": int(ordered.sum()),
        "ordered_newer_adds": int((ordered & (pairs["only_in_b"].fillna("") != "")).sum()),
        "ordered_newer_drops": int((ordered & (pairs["only_in_a"].fillna("") != "")).sum()),
    }


def _ordered_by_location(pairs: pd.DataFrame, locations: dict[str, str]) -> dict[str, int]:
    """Ordered pairs by how many of the two variants sit in the canonical location.

    Commit history covers nearly every canonical skill but few others (NB-Q06, V11), so
    datable pairs lean canonical; RR-03 reports the split. The three counts sum to
    ``ordered_pairs``.
    """
    if pairs.empty:
        canonical = pd.Series(dtype=int)
    else:
        ordered = pairs[pairs["ordered"].astype(bool)]
        canonical = sum(
            ordered[col].map(locations).eq("canonical").astype(int)
            for col in ("file_sha_a", "file_sha_b")
        )
    return {
        "ordered_pairs_canonical": int((canonical == 2).sum()),
        "ordered_pairs_mixed": int((canonical == 1).sum()),
        "ordered_pairs_non_canonical": int((canonical == 0).sum()),
    }


def threshold_sweep(
    pairs: pd.DataFrame,
    thresholds: Sequence[float] = SIMILARITY_THRESHOLDS,
    locations: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Pair counts at each similarity threshold (pairs computed once at the lowest).

    With ``locations`` (``file_sha`` to ``location_class``), ordered pairs are also split
    by location (RR-03).
    """
    rows = []
    for t in thresholds:
        subset = pairs[pairs["similarity"].astype(float) >= t] if len(pairs) else pairs
        row = {"threshold": float(t), **_pair_counts(subset)}
        if locations is not None:
            row.update(_ordered_by_location(subset, locations))
        rows.append(row)
    return pd.DataFrame(rows)


def rq3_summary(pairs: pd.DataFrame) -> pd.DataFrame:
    """Counts at the main threshold, with and without template families."""
    if "is_template_family" not in pairs.columns:
        pairs = mark_templates(pairs)
    non_template = pairs[~pairs["is_template_family"].astype(bool)] if len(pairs) else pairs
    rows = [
        {"scope": "all_families", "threshold": MAIN_SIMILARITY, **_pair_counts(pairs)},
        {
            "scope": "excluding_template_families",
            "threshold": MAIN_SIMILARITY,
            **_pair_counts(non_template),
        },
    ]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sensitivity and scripts
# ---------------------------------------------------------------------------


def key_metrics(scenario: str, frame: pd.DataFrame) -> dict:
    n = int(len(frame))
    hr = frame["high_risk"].astype(bool) if n else pd.Series(dtype=bool)
    k = int(hr.sum())
    low, high = wilson_ci(k, n)
    mw = mann_whitney(frame.loc[hr, "copies"], frame.loc[~hr, "copies"]) if n else None
    mean_h = mw["mean_group"] if mw else math.nan
    mean_o = mw["mean_reference"] if mw else math.nan
    ratio = mean_h / mean_o if mw and mean_o and not math.isnan(mean_o) else math.nan
    return {
        "scenario": scenario,
        "contents": n,
        "high_risk_contents": k,
        "high_risk_share": round(k / n, 4) if n else math.nan,
        "share_ci_low": low,
        "share_ci_high": high,
        "mean_copies_high_risk": mean_h,
        "mean_copies_other": mean_o,
        "mean_copies_ratio": ratio,
        "mwu_p_copies": mw["p_value"] if mw else math.nan,
        "rank_biserial_copies": mw["rank_biserial"] if mw else math.nan,
    }


def _family_names(frame: pd.DataFrame) -> pd.Series:
    return frame["name"].fillna("").astype(str).str.strip().str.lower()


def sensitivity_summary(frame: pd.DataFrame, rules: list[skill_risk.Rule]) -> pd.DataFrame:
    top = frame.nlargest(EXCLUDE_TOP_COPIED, "copies")["file_sha"] if len(frame) else []
    scenarios = [
        ("main (severity 6, main population)", frame),
        ("severity cutoff 5", with_severity_cutoff(frame, rules, 5)),
        ("severity cutoff 7", with_severity_cutoff(frame, rules, 7)),
        ("front-matter-valid subset", frame[frame["frontmatter_valid"].astype(bool)]),
        (
            f"excluding top {EXCLUDE_TOP_COPIED} most-copied contents",
            frame[~frame["file_sha"].isin(set(top))],
        ),
        ("excluding template families", frame[~_family_names(frame).isin(TEMPLATE_FAMILIES)]),
    ]
    return pd.DataFrame([key_metrics(name, f) for name, f in scenarios])


def scripts_summary(
    sib_scan: pd.DataFrame,
    rules: list[skill_risk.Rule],
    unread: pd.DataFrame | None = None,
    truncated: set[tuple[str, str]] | None = None,
) -> pd.DataFrame:
    """Bundled-script metrics. With DR-04 inputs, also the unread-input counts and the
    script metrics again without the skills whose folder listing was truncated, since
    script signals are only a lower bound for those skills."""
    parts = [_script_signal_metrics(sib_scan, rules)]
    if unread is not None:
        parts.append(unread)
    if truncated is not None:
        keys = list(zip(sib_scan["repo_full_name"], sib_scan["artifact_path"], strict=True))
        kept = sib_scan[[k not in truncated for k in keys]] if len(sib_scan) else sib_scan
        rest = skill_risk.sibling_summary(kept)
        rest["metric"] = rest["metric"] + "_excluding_truncated_listing"
        parts.append(rest)
    return pd.concat(parts, ignore_index=True)


def _script_signal_metrics(sib_scan: pd.DataFrame, rules: list[skill_risk.Rule]) -> pd.DataFrame:
    base = skill_risk.sibling_summary(sib_scan)
    by_id = {r.id: r for r in rules}
    cats = sorted({r.category for r in rules if r.severity >= MAIN_CUTOFF})
    rows = []
    for cat in cats:
        count = 0
        if len(sib_scan):
            count = int(
                sib_scan["rule_ids"]
                .fillna("")
                .map(
                    lambda s, c=cat: any(
                        i in by_id and by_id[i].category == c and by_id[i].severity >= MAIN_CUTOFF
                        for i in _split(s)
                    )
                )
                .sum()
            )
        rows.append((f"script_files_high_risk_{cat}", count))
    return pd.concat([base, pd.DataFrame(rows, columns=["metric", "value"])], ignore_index=True)


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------


def plot_prevalence(categories: pd.DataFrame, path: Path) -> Path:
    df = categories.sort_values(["high_risk_share", "content_share"])
    labels = df["category"].astype(str)
    hr = df["high_risk_share"].astype(float).to_numpy()
    low = np.nan_to_num(hr - df["high_risk_ci_low"].astype(float).to_numpy())
    high = np.nan_to_num(df["high_risk_ci_high"].astype(float).to_numpy() - hr)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(
        labels,
        df["content_share"].astype(float),
        color="#D9D9D9",
        label="Any rule in the category (includes context rules)",
    )
    ax.barh(
        labels,
        hr,
        xerr=[low, high],
        color="#C44E52",
        capsize=3,
        label=f"High-risk rules only (severity {MAIN_CUTOFF} or more), 95% Wilson CI",
    )
    ax.set_xlabel("Share of distinct skills")
    ax.set_title("RQ1: signal prevalence by category (unvalidated)")
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_copies_by_group(reach: pd.DataFrame, path: Path) -> Path:
    labels = ["2 or more", "5 or more", "10 or more"]
    cols = ["share_copied_2plus", "share_copied_5plus", "share_copied_10plus"]
    x = np.arange(len(labels))
    width = 0.38
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for i, (_, row) in enumerate(reach.iterrows()):
        values = [float(row[c]) for c in cols]
        ax.bar(x + (i - 0.5) * width, values, width, label=str(row["group"]))
    ax.set_xticks(x, labels)
    ax.set_xlabel("Copies of the same content")
    ax.set_ylabel("Share of distinct skills")
    ax.set_title("RQ2: copy reach by group")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_threshold_sweep(sweep: pd.DataFrame, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(sweep["threshold"], sweep["lineage_pairs"], marker="o", label="lineage pairs")
    ax.plot(
        sweep["threshold"],
        sweep["differing_pairs"],
        marker="s",
        label="pairs differing in high-risk categories",
    )
    ax.plot(sweep["threshold"], sweep["ordered_pairs"], marker="^", label="pairs with both dates")
    ax.axvline(MAIN_SIMILARITY, color="#888888", linestyle="--", linewidth=1)
    ax.set_xlabel("Word-shingle Jaccard threshold")
    ax.set_ylabel("Pairs")
    ax.set_title("RQ3: same-name variant pairs by similarity threshold")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def _sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _manifest_db_sha(paths: Paths) -> str | None:
    manifest = paths.SAMPLES / "MANIFEST.json"
    if not manifest.exists():
        return None
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    for entry in data.get("files", []):
        name = str(entry.get("file", "")).replace("\\", "/")
        if name.endswith("agent_skills_sample.db"):
            return entry.get("sha256")
    return None


def _versions() -> dict[str, str]:
    out = {"python": platform.python_version()}
    for pkg in ("pandas", "numpy", "scipy", "statsmodels", "matplotlib", "pyyaml"):
        try:
            out[pkg] = metadata.version(pkg)
        except metadata.PackageNotFoundError:
            out[pkg] = "not installed"
    return out


def run_analysis(
    db_path: Path,
    paths: Paths | None = None,
    rules_path: Path | str | None = None,
    seed: int = DEFAULT_SEED,
) -> list[Path]:
    """Run RQ1 to RQ3 and sensitivity checks; write tables, figures, and a manifest."""
    from . import explore
    from .load import query_gitskills

    started = time.perf_counter()
    paths = paths or get_paths()
    paths.ensure_output_dirs()
    rules = skill_risk.load_rules(rules_path)

    reps = query_gitskills(
        "SELECT a.file_sha, a.name, a.content, a.first_commit_at, a.frontmatter_valid, "
        "a.body_chars, a.has_scripts, a.location_class, r.stars, r.language, "
        "a.repo_full_name, a.path, a.content_sha_ok, a.composition_fetched, "
        "a.composition_truncated "
        "FROM artifacts a LEFT JOIN repos r ON r.full_name = a.repo_full_name "
        "WHERE a.dedup_primary = 1 ORDER BY a.file_sha",
        db_path,
    )
    occurrences = query_gitskills("SELECT file_sha, repo_full_name FROM artifacts", db_path)
    siblings = query_gitskills(
        "SELECT repo_full_name, artifact_path, entry_name, content FROM artifact_siblings "
        "WHERE entry_type = 'file' AND content IS NOT NULL",
        db_path,
    )
    siblings_without_text = query_gitskills(
        "SELECT entry_name FROM artifact_siblings "
        "WHERE entry_type = 'file' AND (content IS NULL OR content_fetched = 2)",
        db_path,
    )
    truncated_reps = reps[pd.to_numeric(reps["composition_truncated"], errors="coerce") == 1]
    truncated = set(zip(truncated_reps["repo_full_name"], truncated_reps["path"], strict=True))

    flags = skill_risk.population_flags(reps)
    main_reps = reps[flags["in_main_population"].to_numpy()].reset_index(drop=True)
    scan = skill_risk.scan_contents(main_reps, rules)
    counts = skill_risk.copy_counts(occurrences)
    frame = build_frame(scan, counts, main_reps, flags)

    by_rule, by_category = rq1_tables(scan, counts, rules)
    reach = rq2_reach_summary(frame)

    pairs_all = mark_templates(
        skill_risk.family_pairs(main_reps, scan, min_similarity=min(SIMILARITY_THRESHOLDS))
    )
    if len(pairs_all):
        pairs_main = pairs_all[pairs_all["similarity"].astype(float) >= MAIN_SIMILARITY]
    else:
        pairs_main = pairs_all
    sweep = threshold_sweep(
        pairs_all,
        locations=dict(zip(main_reps["file_sha"], main_reps["location_class"], strict=True)),
    )
    sib_scan = skill_risk.scan_siblings(siblings, rules)

    tables = {
        "population_flow": population_flow(reps, flags, occurrences),
        "rq1_prevalence_by_rule": by_rule,
        "rq1_prevalence_by_category": by_category,
        "rq2_reach_summary": reach,
        "rq2_mannwhitney": rq2_mannwhitney(frame),
        "rq2_bootstrap": rq2_bootstrap(frame, seed=seed),
        "rq2_negbin": rq2_negbin(frame),
        "rq2_category_tests": rq2_category_tests(frame, rules),
        "rq3_threshold_sweep": sweep,
        "rq3_summary": rq3_summary(pairs_main),
        "rq3_lineage_pairs": pairs_main,
        "rq3_differing_pairs": pairs_main[pairs_main["differs"].astype(bool)]
        if len(pairs_main)
        else pairs_main,
        "scripts_summary": scripts_summary(
            sib_scan,
            rules,
            unread=skill_risk.unreadable_inputs(reps, siblings_without_text),
            truncated=truncated,
        ),
        "sensitivity_summary": sensitivity_summary(frame, rules),
    }
    produced: list[Path] = [explore.write_table(df, name, paths) for name, df in tables.items()]
    produced.append(plot_prevalence(by_category, paths.FIGURES / "rq1_prevalence_by_category.png"))
    produced.append(plot_copies_by_group(reach, paths.FIGURES / "rq2_copies_by_group.png"))
    produced.append(plot_threshold_sweep(sweep, paths.FIGURES / "rq3_threshold_sweep.png"))

    rules_file = Path(rules_path) if rules_path else repo_root() / skill_risk.DEFAULT_RULES_PATH
    manifest = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "command": "python -m msr_pipeline analyze",
        "seed": seed,
        "gitskills_db": Path(db_path).name,
        "gitskills_db_sha256_from_manifest": _manifest_db_sha(paths),
        "rules_file": rules_file.name,
        "rules_file_sha256": _sha256(rules_file),
        "rules_active": len(rules),
        "high_risk_severity_cutoff": MAIN_CUTOFF,
        "main_similarity_threshold": MAIN_SIMILARITY,
        "row_counts": {
            "occurrences": int(len(occurrences)),
            "representatives": int(len(reps)),
            "main_population": int(len(main_reps)),
            "script_files_scanned": int(len(sib_scan)),
            "lineage_pairs_at_lowest_threshold": int(len(pairs_all)),
        },
        "versions": _versions(),
        "outputs": [p.name for p in produced],
        "runtime_seconds": round(time.perf_counter() - started, 1),
    }
    manifest_path = paths.RESULTS / "ANALYSIS_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    produced.append(manifest_path)
    return produced

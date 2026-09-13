"""Exploratory summaries for the GitSkills and SpecMine samples.

Every function takes DataFrames and returns a DataFrame, so the same code
runs on the samples, on the full datasets, and on the tiny fixtures used by
the tests. Writing to disk is separated into ``write_table`` and ``plot_bar``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from .config import Paths, get_paths  # noqa: E402

# ---------------------------------------------------------------------------
# GitSkills
# ---------------------------------------------------------------------------


def gitskills_location_summary(artifacts: pd.DataFrame) -> pd.DataFrame:
    """File occurrences by ``location_class`` (canonical, skills-dir, other)."""
    out = (
        artifacts.groupby("location_class", dropna=False)
        .size()
        .rename("files")
        .reset_index()
        .sort_values("files", ascending=False, kind="stable")
    )
    out["share"] = (out["files"] / out["files"].sum()).round(4)
    return out.reset_index(drop=True)


def gitskills_copy_distribution(artifacts: pd.DataFrame) -> pd.DataFrame:
    """How many distinct contents have 1, 2, 3, ... verbatim copies.

    A distinct content is identified by ``file_sha``. The result has one row
    per copy count with the number of distinct contents at that count.
    """
    copies = artifacts.groupby("file_sha").size().rename("copies")
    out = copies.value_counts().rename("distinct_contents").reset_index()
    out = out.rename(columns={"index": "copies"}).sort_values("copies", kind="stable")
    out["share_of_contents"] = (out["distinct_contents"] / out["distinct_contents"].sum()).round(4)
    return out.reset_index(drop=True)


def gitskills_language_summary(
    artifacts: pd.DataFrame, repos: pd.DataFrame, top: int = 15
) -> pd.DataFrame:
    """Skill file occurrences by the primary language of the repository."""
    merged = artifacts[["repo_full_name"]].merge(
        repos[["full_name", "language"]], left_on="repo_full_name", right_on="full_name", how="left"
    )
    merged["language"] = merged["language"].fillna("(unknown)")
    out = (
        merged.groupby("language")
        .size()
        .rename("skills")
        .reset_index()
        .sort_values("skills", ascending=False, kind="stable")
        .head(top)
    )
    return out.reset_index(drop=True)


# ---------------------------------------------------------------------------
# SpecMine
# ---------------------------------------------------------------------------


def specmine_tool_summary(spec_files: pd.DataFrame) -> pd.DataFrame:
    """Spec files and repositories per attributed SDD tool."""
    out = (
        spec_files.groupby("spec_tool", dropna=False)
        .agg(specs=("repo_name", "size"), repos=("repo_name", "nunique"))
        .reset_index()
        .sort_values("specs", ascending=False, kind="stable")
    )
    out["share"] = (out["specs"] / out["specs"].sum()).round(4)
    return out.reset_index(drop=True)


def specmine_feature_summary(spec_content_features: pd.DataFrame) -> pd.DataFrame:
    """Share of specs carrying each boolean ``has_*`` structural feature."""
    flags = [c for c in spec_content_features.columns if c.startswith("has_")]
    if "is_tiny" in spec_content_features.columns:
        flags.append("is_tiny")
    rows = []
    n = len(spec_content_features)
    for flag in flags:
        series = pd.to_numeric(spec_content_features[flag], errors="coerce").fillna(0)
        count = int((series > 0).sum())
        rows.append({"feature": flag, "specs_with_feature": count, "share": round(count / n, 4)})
    return (
        pd.DataFrame(rows)
        .sort_values("share", ascending=False, kind="stable")
        .reset_index(drop=True)
    )


def specmine_pr_code_cochange(pull_requests: pd.DataFrame, pr_files: pd.DataFrame) -> pd.DataFrame:
    """Per tool: PRs touching specs, and how many also touch code.

    Mirrors the flagship SpecMine query ("which specs change in the same PR as
    code?"). ``touches_code`` lives on ``pull_requests``; ``is_spec`` on
    ``pr_files``. The join key is whichever PR identifier both tables share.
    """
    key = _shared_pr_key(pull_requests, pr_files)
    spec_prs = pr_files.loc[
        pd.to_numeric(pr_files["is_spec"], errors="coerce").fillna(0) > 0, [key]
    ]
    spec_prs = spec_prs.drop_duplicates()
    prs = pull_requests.merge(spec_prs, on=key, how="inner")
    prs["touches_code"] = pd.to_numeric(prs["touches_code"], errors="coerce").fillna(0) > 0
    out = (
        prs.groupby("tool", dropna=False)
        .agg(spec_prs=(key, "nunique"), spec_and_code_prs=("touches_code", "sum"))
        .reset_index()
    )
    out["spec_and_code_prs"] = out["spec_and_code_prs"].astype(int)
    out["cochange_rate"] = (out["spec_and_code_prs"] / out["spec_prs"]).round(4)
    return out.sort_values("spec_prs", ascending=False, kind="stable").reset_index(drop=True)


def _shared_pr_key(pull_requests: pd.DataFrame, pr_files: pd.DataFrame) -> str:
    for candidate in ("pr_id", "pr_node_id", "pr_url", "id", "pr_number"):
        if candidate in pull_requests.columns and candidate in pr_files.columns:
            return candidate
    shared = [c for c in pull_requests.columns if c in pr_files.columns and "pr" in c.lower()]
    if shared:
        return shared[0]
    raise KeyError("pull_requests and pr_files share no PR identifier column")


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def write_table(df: pd.DataFrame, name: str, paths: Paths | None = None) -> Path:
    """Write ``df`` to results/<name>.csv and return the path."""
    paths = paths or get_paths()
    paths.ensure_output_dirs()
    path = paths.RESULTS / f"{name}.csv"
    df.to_csv(path, index=False)
    return path


def plot_bar(
    df: pd.DataFrame,
    x: str,
    y: str,
    name: str,
    title: str | None = None,
    log_y: bool = False,
    paths: Paths | None = None,
) -> Path:
    """Draw a bar chart of ``y`` by ``x`` into figures/<name>.png and return the path."""
    paths = paths or get_paths()
    paths.ensure_output_dirs()
    path = paths.FIGURES / f"{name}.png"
    fig, ax = plt.subplots(figsize=(8, 4.5))
    labels = df[x].astype(str).tolist()
    ax.bar(labels, df[y].tolist(), color="#4C72B0")
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(title or name)
    if log_y:
        ax.set_yscale("log")
    if len(labels) > 6:
        ax.tick_params(axis="x", rotation=45)
        for label in ax.get_xticklabels():
            label.set_horizontalalignment("right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path

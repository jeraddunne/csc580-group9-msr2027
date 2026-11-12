"""Describe reach within the selected round 1 validation sample.

These groups do not estimate population prevalence or establish safety.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from msr_pipeline.load import query_gitskills  # noqa: E402
from msr_pipeline.skill_risk import copy_counts  # noqa: E402


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    labels_path = ROOT / "data/annotations/signals_jd_r1.csv"
    database_path = ROOT / "data/samples/agent_skills_sample.db"
    output_path = ROOT / "results/label_based_reach.csv"
    metadata_path = ROOT / "results/label_based_reach_metadata.json"

    labels = pd.read_csv(labels_path, dtype=str, keep_default_na=False)
    required = {"file_sha", "rule_id", "label"}
    if not required.issubset(labels.columns):
        raise SystemExit("Required annotation columns are missing.")

    for column in required:
        labels[column] = labels[column].str.strip()

    if labels.empty or labels["file_sha"].eq("").any():
        raise SystemExit("Annotations are empty or contain missing file_sha values.")

    allowed = {"RISKY", "BENIGN_CONTEXT", "NOT_PRESENT", "NONE_PRESENT"}
    if not labels["label"].isin(allowed).all():
        raise SystemExit("Unexpected or unfinished labels found.")

    if labels.duplicated(["file_sha", "rule_id"]).any():
        raise SystemExit("Duplicate file_sha/rule_id annotation keys found.")

    grouped = labels.groupby("file_sha", sort=True)["label"]
    items = grouped.agg(
        recorded_risky=lambda values: values.eq("RISKY").any(),
        no_signal_judgment=lambda values: values.eq("NONE_PRESENT").any(),
    ).reset_index()

    label_sets = grouped.agg(set)
    mixed = label_sets.map(lambda values: "NONE_PRESENT" in values and len(values) > 1)
    if mixed.any():
        raise SystemExit("NONE_PRESENT is mixed with other labels for a content.")

    occurrences = query_gitskills(
        "SELECT file_sha, repo_full_name FROM artifacts",
        database_path,
    )
    if occurrences["file_sha"].isna().any():
        raise SystemExit("Database occurrences contain missing file_sha values.")

    counts = copy_counts(occurrences)
    if counts["file_sha"].duplicated().any():
        raise SystemExit("Duplicate copy-count join keys found.")

    joined = items.merge(
        counts,
        on="file_sha",
        how="left",
        validate="one_to_one",
        indicator=True,
    )
    unmatched = int(joined["_merge"].ne("both").sum())
    if unmatched or joined["copies"].isna().any():
        raise SystemExit(f"Unmatched labeled contents: {unmatched}")

    joined["group"] = "Flagged sample: no recorded RISKY finding"
    joined.loc[joined["no_signal_judgment"], "group"] = "No-signal sample: NONE_PRESENT judgment"
    joined.loc[joined["recorded_risky"], "group"] = "At least one recorded RISKY finding"

    summary = (
        joined.groupby("group", sort=True)
        .agg(
            contents=("file_sha", "size"),
            mean_copies=("copies", "mean"),
            median_copies=("copies", "median"),
        )
        .reset_index()
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_path, index=False, float_format="%.6f")

    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    metadata = {
        "input_commit": commit,
        "labels_path": labels_path.relative_to(ROOT).as_posix(),
        "labels_sha256": sha256(labels_path),
        "database_path": database_path.relative_to(ROOT).as_posix(),
        "database_sha256": sha256(database_path),
        "script_sha256": sha256(Path(__file__)),
        "annotation_rows": len(labels),
        "distinct_labeled_contents": len(items),
        "matched_contents": len(joined),
        "unmatched_contents": unmatched,
        "duplicate_annotation_keys": 0,
        "duplicate_copy_count_keys": 0,
        "python_version": sys.version.split()[0],
        "pandas_version": pd.__version__,
        "command": "python scripts/label_based_reach.py",
        "copy_definition": "Number of artifacts rows per file_sha.",
        "limitations": [
            "Descriptive comparison within a category-selected validation sample.",
            "Sample proportions are not population prevalence estimates.",
            "No recorded RISKY finding does not establish safety.",
            "Hina reported truncated-excerpt notes for 38 of 40 NONE_PRESENT contents.",
            "Independent reproduction and acceptance review remain pending.",
        ],
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    print(f"Matched labeled contents: {len(joined)}")
    print(f"Unmatched labeled contents: {unmatched}")
    print(summary.to_string(index=False))
    print("\nSaved results/label_based_reach.csv")
    print("Saved results/label_based_reach_metadata.json")


if __name__ == "__main__":
    main()

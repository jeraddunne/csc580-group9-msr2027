"""Command-line interface: ``python -m msr_pipeline <command>`` or ``msr-pipeline``."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

import pandas as pd

from . import __version__, explore, skill_risk
from .config import get_paths, gitskills_db_path, specmine_dir
from .load import (
    SPECMINE_ALL_TABLES,
    DatasetNotFoundError,
    load_gitskills,
    load_specmine,
    query_gitskills,
    specmine_table_path,
)

DATASETS = ("gitskills", "specmine", "all")


def _print_df(df: pd.DataFrame, max_rows: int = 30) -> None:
    with pd.option_context("display.max_rows", max_rows, "display.width", 120):
        print(df.head(max_rows).to_string(index=False))


def cmd_info(_: argparse.Namespace) -> int:
    paths = get_paths()
    print(f"msr-pipeline {__version__}")
    print(f"ROOT     {paths.ROOT}")
    print(f"DATA     {paths.DATA}")
    print(f"SAMPLES  {paths.SAMPLES}")
    print(f"RESULTS  {paths.RESULTS}")
    print(f"FIGURES  {paths.FIGURES}")
    db = gitskills_db_path(paths)
    db_state = "present" if db.exists() else "missing"
    print(f"\nGitSkills sample: {db_state}  ({db})")
    sm = specmine_dir(paths)
    present = [t for t in SPECMINE_ALL_TABLES if specmine_table_path(t, sm).exists()]
    print(f"SpecMine sample:  {len(present)}/{len(SPECMINE_ALL_TABLES)} tables present  ({sm})")
    for table in present:
        print(f"  - {table}")
    if not db.exists() or not present:
        print("\nRun `python scripts/download_samples.py` to fetch missing samples.")
    return 0


def explore_gitskills(limit: int | None) -> list[str]:
    paths = get_paths()
    data = load_gitskills(gitskills_db_path(paths), limit=limit)
    produced: list[str] = []

    loc = explore.gitskills_location_summary(data.artifacts)
    produced.append(str(explore.write_table(loc, "gitskills_location_summary", paths)))
    produced.append(
        str(
            explore.plot_bar(
                loc,
                "location_class",
                "files",
                "gitskills_location_summary",
                title="GitSkills: file occurrences by location class",
                paths=paths,
            )
        )
    )

    copies = explore.gitskills_copy_distribution(data.artifacts)
    produced.append(str(explore.write_table(copies, "gitskills_copy_distribution", paths)))
    produced.append(
        str(
            explore.plot_bar(
                copies.head(20),
                "copies",
                "distinct_contents",
                "gitskills_copy_distribution",
                title="GitSkills: distinct contents by number of verbatim copies (top 20)",
                log_y=True,
                paths=paths,
            )
        )
    )

    lang = explore.gitskills_language_summary(data.artifacts, data.repos)
    produced.append(str(explore.write_table(lang, "gitskills_language_summary", paths)))
    produced.append(
        str(
            explore.plot_bar(
                lang,
                "language",
                "skills",
                "gitskills_language_summary",
                title="GitSkills: skill occurrences by repository language",
                paths=paths,
            )
        )
    )
    return produced


def explore_specmine(limit: int | None) -> list[str]:
    paths = get_paths()
    tables = load_specmine(specmine_dir(paths))
    if limit is not None:
        tables = {k: v.head(limit) for k, v in tables.items()}
    produced: list[str] = []

    if "spec_files" in tables:
        tools = explore.specmine_tool_summary(tables["spec_files"])
        produced.append(str(explore.write_table(tools, "specmine_tool_summary", paths)))
        produced.append(
            str(
                explore.plot_bar(
                    tools,
                    "spec_tool",
                    "specs",
                    "specmine_tool_summary",
                    title="SpecMine: spec files by attributed tool",
                    paths=paths,
                )
            )
        )

    if "spec_content_features" in tables:
        feats = explore.specmine_feature_summary(tables["spec_content_features"])
        produced.append(str(explore.write_table(feats, "specmine_feature_summary", paths)))
        produced.append(
            str(
                explore.plot_bar(
                    feats,
                    "feature",
                    "share",
                    "specmine_feature_summary",
                    title="SpecMine: share of specs with each structural feature",
                    paths=paths,
                )
            )
        )

    if "pull_requests" in tables and "pr_files" in tables:
        co = explore.specmine_pr_code_cochange(tables["pull_requests"], tables["pr_files"])
        produced.append(str(explore.write_table(co, "specmine_pr_code_cochange", paths)))
        produced.append(
            str(
                explore.plot_bar(
                    co,
                    "tool",
                    "cochange_rate",
                    "specmine_pr_code_cochange",
                    title="SpecMine: share of spec-touching PRs that also touch code",
                    paths=paths,
                )
            )
        )
    return produced


def cmd_explore(args: argparse.Namespace) -> int:
    produced: list[str] = []
    failures = 0
    targets = ["gitskills", "specmine"] if args.dataset == "all" else [args.dataset]
    for target in targets:
        try:
            if target == "gitskills":
                produced += explore_gitskills(args.limit)
            else:
                produced += explore_specmine(args.limit)
        except DatasetNotFoundError as exc:
            failures += 1
            print(f"[skip] {exc}", file=sys.stderr)
    for path in produced:
        print(f"wrote {path}")
    if not produced:
        print("Nothing produced. Download a sample first.", file=sys.stderr)
        return 1
    return 0 if failures == 0 or args.dataset == "all" else 1


def cmd_query(args: argparse.Namespace) -> int:
    if args.dataset != "gitskills":
        print("query currently supports --dataset gitskills only.", file=sys.stderr)
        return 2
    try:
        df = query_gitskills(args.sql)
    except DatasetNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    _print_df(df, max_rows=args.max_rows)
    return 0


def cmd_risk_pilot(args: argparse.Namespace) -> int:
    paths = get_paths()
    try:
        produced = skill_risk.run_pilot(
            gitskills_db_path(paths),
            paths=paths,
            rules_path=args.rules,
            limit=args.limit,
            min_similarity=args.min_similarity,
        )
    except DatasetNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    for path in produced:
        print(f"wrote {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="msr-pipeline",
        description="Group 9 mining pipeline for the MSR 2027 GitSkills and SpecMine datasets.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_info = sub.add_parser("info", help="Show paths and which samples are present.")
    p_info.set_defaults(func=cmd_info)

    p_explore = sub.add_parser("explore", help="Write exploratory tables and figures.")
    p_explore.add_argument("--dataset", choices=DATASETS, default="all")
    p_explore.add_argument(
        "--limit", type=int, default=None, help="Read at most N rows per table (for quick runs)."
    )
    p_explore.set_defaults(func=cmd_explore)

    p_query = sub.add_parser("query", help="Run a read-only SQL query against a sample.")
    p_query.add_argument("--dataset", choices=("gitskills",), default="gitskills")
    p_query.add_argument("--sql", required=True, help="SQL statement to run.")
    p_query.add_argument("--max-rows", type=int, default=30)
    p_query.set_defaults(func=cmd_query)

    p_risk = sub.add_parser(
        "risk-pilot",
        help="Proposal P-01 pilot: rule-based risk signals in GitSkills (static text only).",
    )
    p_risk.add_argument(
        "--rules", default=None, help="Rule file (default rules/skill_risk_rules.yaml)."
    )
    p_risk.add_argument("--limit", type=int, default=None, help="Scan at most N distinct contents.")
    p_risk.add_argument(
        "--min-similarity", type=float, default=0.5, help="Jaccard threshold for variant lineage."
    )
    p_risk.set_defaults(func=cmd_risk_pilot)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

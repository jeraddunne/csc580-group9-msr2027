#!/usr/bin/env python
"""Configure the GitHub repository from project.yml. Idempotent; safe to re-run.

Creates or updates labels, milestones (with rubric due dates), the seed backlog of rubric
deliverable issues, repository merge settings, and the branch protection ruleset on main.

Usage:
    python scripts/bootstrap_github.py                 # everything
    python scripts/bootstrap_github.py --only labels,milestones
    python scripts/bootstrap_github.py --require-checks "test (3.12)"   # add CI checks to the ruleset
    python scripts/bootstrap_github.py --dry-run

Requires the GitHub CLI (`gh auth login`) with the `repo` scope.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

LABELS: list[tuple[str, str, str]] = [
    ("type:research", "1d76db", "Research framing, analysis design, interpretation"),
    ("type:pipeline", "0e8a16", "Loading, extraction, analysis code"),
    ("type:data", "fbca04", "Dataset acquisition, sampling, data dictionary"),
    ("type:docs", "c5def5", "README, process docs, decision records"),
    ("type:test", "5319e7", "Automated tests and validation protocols"),
    ("type:process", "bfd4f2", "Scrum and Lean Six Sigma process work"),
    ("type:report", "d4c5f9", "Report writing and figures"),
    ("type:presentation", "f9d0c4", "Demo and presentation materials"),
    ("proposal", "e99695", "Topic proposal for the Formation vote"),
    ("onboarding", "c2e0c6", "Team member onboarding"),
    ("decision", "fef2c0", "Needs a decision; outcome becomes an ADR"),
    ("blocker", "b60205", "Blocked; needs help within a day"),
    ("bug", "d73a4a", "Wrong result, crash, or non-reproducible behaviour"),
    ("kaizen", "0052cc", "Process improvement from a retrospective or check-in"),
    ("rework", "e4e669", "Work reopened after being marked Done (counts toward rework KPI)"),
    ("rubric", "006b75", "Rubric deliverable (parent issue)"),
    ("sprint-goal", "0075ca", "The sprint goal issue"),
    ("priority:high", "ff7b72", "Sprint goal at risk if not done"),
    ("priority:medium", "ffd33d", "Planned for this sprint"),
    ("priority:low", "cfd8dc", "Nice to have"),
    ("good first issue", "7057ff", "Small, well-defined, good for a first PR"),
    ("finding", "5ab1ef", "Research finding with evidence (team workspace)"),
    ("signup", "c5f015", "Work sign-up for a sprint (team workspace)"),
]

# (milestone key, labels, title, body)
SEED_ISSUES: list[tuple[str, str, str, str]] = [
    (
        "formation",
        "rubric,type:process",
        "Formation: team charter signed by all four members",
        "Every member signs TEAM_CHARTER.md section 13 in their first PR and completes the onboarding issue.\n\n"
        "Acceptance: four signature rows; four onboarding issues closed; four profiles in docs/team/.\nEstimate: 1",
    ),
    (
        "formation",
        "rubric,type:data",
        "Formation: dataset samples inspected by every member",
        "Run `make data` and `python -m msr_pipeline explore --dataset all`; read data/README.md and both upstream READMEs.\n\n"
        "Acceptance: each member comments here with the row counts printed by the download script.\nEstimate: 1",
    ),
    (
        "formation",
        "rubric,type:research",
        "Formation: topic proposals submitted (at least one per member)",
        "Use the Project proposal issue form by 2026-09-14 23:59. See docs/proposals/README.md.\n\n"
        "Acceptance: at least four issues labelled `proposal`.\nEstimate: 2",
    ),
    (
        "formation",
        "decision,type:process",
        "Formation: ballot vote tallied and topic decided (ADR-0004)",
        "Ballots in docs/proposals/votes/ballots/ by 2026-09-15 23:59; `make tally` at kickoff; ADR-0004 written.\n\n"
        "Acceptance: docs/proposals/RESULTS.md committed; ADR-0004 status Accepted.\nEstimate: 1",
    ),
    (
        "formation",
        "rubric,type:research",
        "Formation: RESEARCH_QUESTION.md completed and topic brief submitted",
        "Product Owner fills every section from the winning proposal; topic brief submitted to the instructor.\n\n"
        "Acceptance: no placeholders remain in RESEARCH_QUESTION.md; brief submitted by 2026-09-16.\nEstimate: 2",
    ),
    (
        "formation",
        "rubric,type:process",
        "Formation: Sprint 1 backlog created, estimated, and on the board",
        "Create issues for every Sprint 1 rubric bullet mapped to the chosen question; estimate; assign; add to the project board.\n\n"
        "Acceptance: milestone Sprint 1 has issues covering all eight review bullets; each meets the Definition of Ready.\nEstimate: 2",
    ),
    (
        "formation",
        "type:process",
        "Formation: project board created from the instructor template with LSS fields",
        "Run `python scripts/setup_project_board.py` (needs `gh auth refresh -s project`). Add WIP limits (5) on Todo and In progress in the Board view.\n\n"
        "Acceptance: board has Todo/In progress/Done/Block/Cancelled, Sprint, Estimate, Priority, Type fields; all open issues added.\nEstimate: 1",
    ),
    (
        "formation",
        "type:process",
        "Formation: invite team members and instructor as collaborators",
        "Add handles to project.yml as onboarding issues arrive, then `python scripts/invite_team.py --instructor`.\n\n"
        "Acceptance: all four members have push access; instructor invited.\nEstimate: 1",
    ),
    (
        "formation",
        "kaizen,type:process",
        "Kaizen: branch protection enabled on main",
        "Ruleset: no direct pushes, one approving review, conversation resolution, no force push. Verified by an attempted direct push being rejected.\n\nRaised in: repository setup 2026-09-13.",
    ),
    (
        "formation",
        "kaizen,type:process",
        "Kaizen: 48-hour pull request review SLA tracked as a KPI",
        "Reviewer rotation agreed at kickoff; PR first-review turnaround appears on the weekly dashboard with a 48 h target.\n\nMeasure: median first-review time under 48 h in Sprint 1.",
    ),
    (
        "formation",
        "kaizen,type:process",
        "Kaizen: weekly process metrics automated",
        "The LSS metrics workflow opens a PR every Sunday; the Scrum Master reviews it at the Thursday check-in.\n\nMeasure: a metrics PR exists for every week of Sprint 1.",
    ),
    (
        "sprint-1",
        "rubric,type:research",
        "S1: precise research question with motivation, contribution, and competing explanation",
        "Rubric: 'A selected MSR-inspired topic and a precise research question' and 'Motivation, expected contribution, and at least one competing or simpler explanation.'\n\nAcceptance: RESEARCH_QUESTION.md sections 1 to 4 and 7 complete and reviewed.\nEstimate: 3",
    ),
    (
        "sprint-1",
        "rubric,type:research",
        "S1: unit of analysis, population, sample, variables, outcome measures defined",
        "Rubric: 'A defined unit of analysis, population, sample, variables, and outcome measures.'\n\nAcceptance: RESEARCH_QUESTION.md sections 5 and 6 and DATA_DICTIONARY.md Part B complete.\nEstimate: 3",
    ),
    (
        "sprint-1",
        "rubric,type:data",
        "S1: dataset acquisition or sampling instructions and data dictionary",
        "Rubric: 'Dataset acquisition or sampling instructions and a data dictionary.'\n\nAcceptance: data/README.md instructions verified by a second member; MANIFEST.json hashes recorded; inclusion/exclusion rules implemented in code.\nEstimate: 3",
    ),
    (
        "sprint-1",
        "rubric,type:pipeline",
        "S1: first working data-loading and extraction pipeline for the selected question",
        "Rubric: 'A first working data-loading and extraction pipeline.'\n\nAcceptance: `python -m msr_pipeline <command>` runs end to end on the sample and writes results/; tested; documented in README.\nEstimate: 5",
    ),
    (
        "sprint-1",
        "rubric,type:pipeline",
        "S1: at least one exploratory table or visualization generated by code",
        "Rubric: 'At least one exploratory table or visualization generated by code.'\n\nAcceptance: a table in results/ and a figure in figures/ produced by the pipeline and referenced in report/draft.md.\nEstimate: 2",
    ),
    (
        "sprint-1",
        "rubric,type:process",
        "S1: repository practice: issues, milestones, branch protection, first reviewed pull request",
        "Rubric: 'A repository with issues, milestones, branch protection or equivalent review practice, and a first pull request.'\n\nAcceptance: every member has authored and reviewed at least one merged PR.\nEstimate: 1",
    ),
    (
        "sprint-1",
        "rubric,type:research",
        "S1: primary risks and threats to validity identified",
        "Rubric acceptance: 'the group has identified the primary risks and threats to validity.'\n\nAcceptance: THREATS_TO_VALIDITY.md rows for the chosen question have status set; FMEA top 5 reviewed at planning.\nEstimate: 2",
    ),
    (
        "sprint-1",
        "type:process",
        "S1: baseline process metrics captured (Measure phase)",
        "First three weekly metrics PRs merged; baseline values recorded in docs/lean-six-sigma/metrics/DASHBOARD.md and referenced in the retrospective.\n\nAcceptance: retrospective.md 'Data first' section filled from the dashboard.\nEstimate: 1",
    ),
    (
        "sprint-1",
        "rubric,type:process",
        "S1: sprint review package and retrospective",
        "Rubric: 'A retrospective explaining what the group learned and what changed in the backlog.'\n\nAcceptance: docs/sprints/sprint-1/review.md and retrospective.md complete; kaizen issues created; package submitted by 2026-10-07.\nEstimate: 2",
    ),
    (
        "sprint-2",
        "rubric,type:pipeline",
        "S2: working implementation of the core mining, extraction, similarity, classification, traceability, or visualization method",
        "Rubric Sprint 2 bullet 1. Acceptance: runs end to end on the approved sample from `run_pipeline.sh`.\nEstimate: 8 (split at planning)",
    ),
    (
        "sprint-2",
        "rubric,type:test",
        "S2: automated tests for parsing, transformation, matching, or metric functions",
        "Rubric Sprint 2 bullet 2. Acceptance: every function whose output appears in the report has a test; CI green.\nEstimate: 3",
    ),
    (
        "sprint-2",
        "rubric,type:research",
        "S2: validation sample, manual annotation protocol, or other evaluation design",
        "Rubric Sprint 2 bullet 3. Acceptance: written protocol; two annotators; agreement statistic reported; sample size justified.\nEstimate: 5",
    ),
    (
        "sprint-2",
        "rubric,type:report",
        "S2: preliminary results with reproducible figures or tables",
        "Rubric Sprint 2 bullet 4. Acceptance: results/ and figures/ regenerated by the pipeline; referenced in report/draft.md.\nEstimate: 3",
    ),
    (
        "sprint-2",
        "rubric,type:report",
        "S2: updated research report (background, method, implementation, preliminary results)",
        "Rubric Sprint 2 bullet 6. Acceptance: sections drafted with citations; observation and interpretation separated.\nEstimate: 3",
    ),
    (
        "sprint-2",
        "rubric,type:process",
        "S2: sprint review package and retrospective recording changes to question, method, scope, or interpretation",
        "Rubric Sprint 2 bullet 7 and acceptance criteria. Acceptance: review.md and retrospective.md complete; package submitted by 2026-10-28.\nEstimate: 2",
    ),
    (
        "sprint-3",
        "rubric,type:research",
        "S3: final or near-final results addressing the research question",
        "Rubric Sprint 3 bullet 1.\nEstimate: 5",
    ),
    (
        "sprint-3",
        "rubric,type:research",
        "S3: robustness checks, sensitivity analysis, or comparison across meaningful subgroups",
        "Rubric Sprint 3 bullet 2.\nEstimate: 5",
    ),
    (
        "sprint-3",
        "rubric,type:research",
        "S3: error analysis and manually inspected examples",
        "Rubric Sprint 3 bullet 3.\nEstimate: 3",
    ),
    (
        "sprint-3",
        "rubric,type:report",
        "S3: final figures and tables generated from the repository pipeline",
        "Rubric Sprint 3 bullet 4.\nEstimate: 3",
    ),
    (
        "sprint-3",
        "rubric,type:report",
        "S3: complete draft report with citations and clear separation of findings and interpretation",
        "Rubric Sprint 3 bullet 5.\nEstimate: 5",
    ),
    (
        "sprint-3",
        "rubric,type:report",
        "S3: threats-to-validity section (dataset bias, measurement error, confounding, missing data, reproducibility, generalizability)",
        "Rubric Sprint 3 bullet 6.\nEstimate: 2",
    ),
    (
        "sprint-3",
        "rubric,type:process",
        "S3: documented release or tagged version of the repository",
        "Rubric Sprint 3 bullet 7. Acceptance: tag v0.9.0-rc1 with release notes; fresh clone reproduces primary results.\nEstimate: 2",
    ),
    (
        "sprint-3",
        "rubric,type:presentation",
        "S3: final demonstration plan and presentation materials",
        "Rubric Sprint 3 bullet 8. See docs/PRESENTATION_PLAN.md.\nEstimate: 3",
    ),
    (
        "sprint-3",
        "rubric,type:process",
        "S3: retrospective identifying the group's most important process improvement",
        "Rubric Sprint 3 bullet 9. Acceptance: improvement named with before/after KPI evidence.\nEstimate: 1",
    ),
    (
        "finalization",
        "rubric,type:report",
        "Final: respond to feedback and finalize the report",
        "Acceptance: feedback log in docs/sprints/finalization/checklist.md complete; report/final.pdf built.\nEstimate: 3",
    ),
    (
        "finalization",
        "rubric,type:process",
        "Final: repository release v1.0.0 and fresh-machine reproduction by a non-author",
        "Acceptance: release with report PDF and figures attached; gemba walk recorded.\nEstimate: 2",
    ),
    (
        "finalization",
        "rubric,type:presentation",
        "Final: presentation and live demonstration",
        "Acceptance: rehearsed twice; backup recording available.\nEstimate: 3",
    ),
    (
        "finalization",
        "rubric,type:docs",
        "Final: individual contribution and reflection (one per member)",
        "Acceptance: four files in docs/reflections/ with links to evidence.\nEstimate: 1",
    ),
    (
        "finalization",
        "rubric,type:docs",
        "Final: AI-use log and disclosure complete",
        "Acceptance: every AI-assisted PR has a log row; disclosure paragraph in the report matches the log.\nEstimate: 1",
    ),
]


def sh(*args: str, check: bool = True, input_text: str | None = None) -> str:
    proc = subprocess.run(list(args), capture_output=True, text=True, input=input_text)
    if check and proc.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(args)}\n{proc.stderr.strip()}")
    return proc.stdout


def gh_json(*args: str) -> object:
    out = sh("gh", *args)
    return json.loads(out) if out.strip() else None


def load_config() -> dict:
    return yaml.safe_load((ROOT / "project.yml").read_text(encoding="utf-8"))


def ensure_labels(repo: str, dry: bool) -> None:
    for name, color, desc in LABELS:
        print(f"label: {name}")
        if not dry:
            sh(
                "gh",
                "label",
                "create",
                name,
                "--repo",
                repo,
                "--color",
                color,
                "--description",
                desc,
                "--force",
            )


def ensure_milestones(repo: str, timeline: dict, dry: bool) -> dict[str, int]:
    existing = gh_json("api", f"repos/{repo}/milestones?state=all&per_page=100") or []
    by_title = {m["title"]: m for m in existing}
    numbers: dict[str, int] = {}
    for key, spec in timeline.items():
        title = spec["title"]
        end: date = spec["end"]
        due = f"{end.isoformat()}T12:00:00Z"
        desc = f"{spec.get('dmaic', '')} phase. {spec['start']} to {spec['end']}. Rubric weight {spec.get('weight', '')}%."
        if title in by_title:
            m = by_title[title]
            numbers[key] = m["number"]
            print(f"milestone exists: {title} (#{m['number']}); updating due date")
            if not dry:
                sh(
                    "gh",
                    "api",
                    "-X",
                    "PATCH",
                    f"repos/{repo}/milestones/{m['number']}",
                    "-f",
                    f"due_on={due}",
                    "-f",
                    f"description={desc}",
                )
        else:
            print(f"milestone create: {title} due {due}")
            if not dry:
                created = gh_json(
                    "api",
                    "-X",
                    "POST",
                    f"repos/{repo}/milestones",
                    "-f",
                    f"title={title}",
                    "-f",
                    f"due_on={due}",
                    "-f",
                    f"description={desc}",
                )
                numbers[key] = created["number"]
    return numbers


def ensure_issues(repo: str, milestones: dict[str, int], timeline: dict, dry: bool) -> None:
    existing = (
        gh_json(
            "issue", "list", "--repo", repo, "--state", "all", "--limit", "500", "--json", "title"
        )
        or []
    )
    titles = {i["title"] for i in existing}
    for key, labels, title, body in SEED_ISSUES:
        if title in titles:
            print(f"issue exists: {title}")
            continue
        print(f"issue create: {title}")
        if dry:
            continue
        args = [
            "gh",
            "issue",
            "create",
            "--repo",
            repo,
            "--title",
            title,
            "--body",
            body,
            "--label",
            labels,
        ]
        if key in milestones:
            args += ["--milestone", timeline[key]["title"]]
        sh(*args)


def repo_settings(repo: str, dry: bool) -> None:
    print("repo settings: issues on, projects on, wiki off, squash-only, delete branch on merge")
    if dry:
        return
    sh(
        "gh",
        "repo",
        "edit",
        repo,
        "--enable-issues",
        "--enable-projects",
        "--enable-wiki=false",
        "--enable-squash-merge",
        "--enable-merge-commit=false",
        "--enable-rebase-merge=false",
        "--delete-branch-on-merge",
        "--allow-update-branch",
    )


def ensure_ruleset(
    repo: str, required_checks: list[str], dry: bool, min_approvals: int = 1
) -> None:
    name = "protect-main"
    rules: list[dict] = [
        {"type": "deletion"},
        {"type": "non_fast_forward"},
        {
            "type": "pull_request",
            "parameters": {
                "required_approving_review_count": min_approvals,
                "dismiss_stale_reviews_on_push": True,
                "require_code_owner_review": False,
                "require_last_push_approval": False,
                "required_review_thread_resolution": True,
                "allowed_merge_methods": ["squash"],
            },
        },
    ]
    if required_checks:
        rules.append(
            {
                "type": "required_status_checks",
                "parameters": {
                    "strict_required_status_checks_policy": False,
                    "required_status_checks": [{"context": c} for c in required_checks],
                },
            }
        )
    payload = {
        "name": name,
        "target": "branch",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "rules": rules,
        "bypass_actors": [],
    }
    existing = gh_json("api", f"repos/{repo}/rulesets") or []
    match = next((r for r in existing if r["name"] == name), None)
    if match:
        print(f"ruleset exists: {name} (id {match['id']}); updating")
        if not dry:
            sh(
                "gh",
                "api",
                "-X",
                "PUT",
                f"repos/{repo}/rulesets/{match['id']}",
                "--input",
                "-",
                input_text=json.dumps(payload),
            )
    else:
        print(f"ruleset create: {name}")
        if not dry:
            sh(
                "gh",
                "api",
                "-X",
                "POST",
                f"repos/{repo}/rulesets",
                "--input",
                "-",
                input_text=json.dumps(payload),
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--only",
        default="labels,milestones,issues,settings,ruleset",
        help="comma-separated subset of: labels,milestones,issues,settings,ruleset",
    )
    parser.add_argument(
        "--require-checks",
        default="",
        help="comma-separated CI check names to require in the ruleset",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--min-approvals",
        type=int,
        default=None,
        help="required PR approvals (default: process.min_reviewers in project.yml, else 1)",
    )
    args = parser.parse_args(argv)

    cfg = load_config()
    repo = cfg["repo"]
    steps = {s.strip() for s in args.only.split(",") if s.strip()}
    min_approvals = args.min_approvals
    if min_approvals is None:
        min_approvals = int((cfg.get("process") or {}).get("min_reviewers", 1))
    dry = args.dry_run
    print(f"repository: {repo} (dry run: {dry})")

    if "labels" in steps:
        ensure_labels(repo, dry)
    milestones: dict[str, int] = {}
    if "milestones" in steps or "issues" in steps:
        milestones = ensure_milestones(repo, cfg["timeline"], dry)
    if "issues" in steps:
        ensure_issues(repo, milestones, cfg["timeline"], dry)
    if "settings" in steps:
        repo_settings(repo, dry)
    if "ruleset" in steps:
        checks = [c.strip() for c in args.require_checks.split(",") if c.strip()]
        ensure_ruleset(repo, checks, dry, min_approvals)
    print("done")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

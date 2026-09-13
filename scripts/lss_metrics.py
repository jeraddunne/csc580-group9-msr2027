#!/usr/bin/env python
"""Generate the Lean Six Sigma process dashboard for the Group 9 repository.

Fetches issues, pull requests, reviews, workflow runs, and commits from the GitHub
REST API (or loads them from an offline fixture), computes the KPIs defined in
``docs/lean-six-sigma/KPIS.md`` via ``msr_pipeline.lss_metrics``, and writes:

* ``<out>/snapshots/<YYYY-MM-DD>.json``
* ``<out>/history.csv``
* ``<out>/DASHBOARD.md``
* ``<out>/charts/cycle_time_xmr.png`` and ``<out>/charts/pr_first_review_xmr.png``

Usage::

    python scripts/lss_metrics.py --repo owner/name [--since 2026-09-10] [--out DIR]
    python scripts/lss_metrics.py --offline-fixture tests/fixtures/lss_fixture.json --out /tmp/x
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from msr_pipeline import lss_metrics as lss  # noqa: E402

API = "https://api.github.com"
STATUS_ICON = {"ok": "🟢", "warn": "🔴", "info": "🔵", "nodata": "⚪"}


# --------------------------------------------------------------------------- config


def load_config(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        import yaml
    except ImportError:  # pragma: no cover
        return {}
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


# --------------------------------------------------------------------------- GitHub fetch


class GitHub:
    def __init__(self, repo: str, token: str | None):
        import requests

        self.repo = repo
        self.session = requests.Session()
        self.session.headers.update(
            {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        )
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def get(self, path: str, params: dict | None = None) -> list:
        url = f"{API}{path}"
        items: list = []
        params = dict(params or {})
        params.setdefault("per_page", 100)
        while url:
            resp = self.session.get(url, params=params, timeout=60)
            if resp.status_code in (404, 409):  # empty repository or feature disabled
                return items
            if resp.status_code == 403 and "rate limit" in resp.text.lower():
                raise SystemExit("GitHub rate limit hit; set GITHUB_TOKEN and retry")
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict):
                for key in ("workflow_runs", "items"):
                    if key in data:
                        data = data[key]
                        break
            items.extend(data)
            url = resp.links.get("next", {}).get("url")
            params = {}
        return items

    def fetch_all(self, since: str | None) -> dict[str, list]:
        r = self.repo
        issue_params = {"state": "all"}
        if since:
            issue_params["since"] = since
        issues = []
        for it in self.get(f"/repos/{r}/issues", issue_params):
            if "pull_request" in it:
                continue
            events = self.get(f"/repos/{r}/issues/{it['number']}/events")
            issues.append(normalize_issue(it, events))
        prs, reviews = [], []
        for pr in self.get(f"/repos/{r}/pulls", {"state": "all"}):
            prs.append(normalize_pr(pr))
            for rv in self.get(f"/repos/{r}/pulls/{pr['number']}/reviews"):
                reviews.append(
                    {
                        "pull_number": pr["number"],
                        "user": (rv.get("user") or {}).get("login"),
                        "state": rv.get("state"),
                        "submitted_at": rv.get("submitted_at"),
                    }
                )
        run_params = {"created": f">={since}"} if since else None
        runs = [
            {
                "id": run.get("id"),
                "name": run.get("name"),
                "conclusion": run.get("conclusion"),
                "status": run.get("status"),
                "created_at": run.get("created_at"),
                "head_branch": run.get("head_branch"),
            }
            for run in self.get(f"/repos/{r}/actions/runs", run_params)
        ]
        commits = []
        for c in self.get(f"/repos/{r}/commits", {"since": since} if since else None):
            meta = c.get("commit", {}).get("author") or {}
            author = (c.get("author") or {}).get("login") or meta.get("name")
            commits.append({"sha": c.get("sha"), "author": author, "date": meta.get("date")})
        return {"issues": issues, "prs": prs, "reviews": reviews, "runs": runs, "commits": commits}


def normalize_issue(it: dict, events: list[dict]) -> dict:
    milestone = it.get("milestone") or {}
    return {
        "number": it.get("number"),
        "title": it.get("title"),
        "state": it.get("state"),
        "state_reason": it.get("state_reason"),
        "created_at": it.get("created_at"),
        "closed_at": it.get("closed_at"),
        "labels": [lb.get("name") for lb in it.get("labels") or [] if isinstance(lb, dict)],
        "assignees": [a.get("login") for a in it.get("assignees") or [] if isinstance(a, dict)],
        "milestone": milestone.get("title") if milestone else None,
        "body": it.get("body") or "",
        "events": [
            {
                "event": ev.get("event"),
                "created_at": ev.get("created_at"),
                "label": (ev.get("label") or {}).get("name"),
                "assignee": (ev.get("assignee") or {}).get("login"),
            }
            for ev in events
        ],
    }


def normalize_pr(pr: dict) -> dict:
    return {
        "number": pr.get("number"),
        "title": pr.get("title"),
        "user": (pr.get("user") or {}).get("login"),
        "created_at": pr.get("created_at"),
        "merged_at": pr.get("merged_at"),
        "closed_at": pr.get("closed_at"),
        "state": pr.get("state"),
        "draft": bool(pr.get("draft")),
        "head_branch": (pr.get("head") or {}).get("ref"),
    }


# --------------------------------------------------------------------------- rendering


def fmt(value: Any, digits: int = 2) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def _kpi_rows(k: dict) -> list[tuple[str, dict, str, str, str]]:
    """(label, kpi object, value text, target text, note) for the KPI table."""
    vel = k["velocity"]
    rel = k["commitment_reliability"]
    ct = k["cycle_time_days"]
    lt = k["lead_time_days"]
    tp = k["throughput_per_week"]
    wip = k["wip"]
    bl = k["blocked_time_days"]
    fr = k["pr_first_review_hours"]
    mg = k["pr_merge_hours"]
    ftr = k["first_time_right"]
    rw = k["rework_ratio"]
    df = k["defect_count"]
    ci = k["ci_pass_rate"]
    cg = k["contribution_gini"]
    kz = k["kaizen_closure_rate"]
    rp = k["reproducibility_check"]

    escaped = ", ".join(f"{n}={v}" for n, v in df["escaped_by_sprint"].items())
    flagged = ", ".join(cg["flagged"]) if cg["flagged"] else ""
    return [
        (
            "Velocity (points done, all sprints)",
            vel,
            fmt(vel["value"], 0),
            "trend",
            ", ".join(f"{n}: {v}" for n, v in vel["per_sprint"].items()),
        ),
        (
            "Commitment reliability",
            rel,
            fmt(rel["value"]),
            f">= {fmt(rel['target'])}",
            f"sprint: {rel.get('sprint') or 'n/a'}",
        ),
        (
            "Cycle time (median days)",
            ct,
            fmt(ct["value"]),
            f"<= {fmt(ct['target'], 0)}",
            f"n={ct['n']}, mean={fmt(ct['mean'])}, approximated={ct['approximated']}",
        ),
        (
            "Lead time (median days)",
            lt,
            fmt(lt["value"]),
            f"<= {fmt(lt['target'], 0)}",
            f"n={lt['n']}, mean={fmt(lt['mean'])}",
        ),
        (
            "Throughput (issues/week)",
            tp,
            fmt(tp["value"]),
            "trend",
            f"{tp['closed']} closed over {tp['window_days']} days",
        ),
        (
            "WIP (open, in progress)",
            wip,
            fmt(wip["value"], 0),
            f"<= {wip['limit']}",
            ", ".join(f"#{n}" for n in wip["numbers"]),
        ),
        (
            "Blocked time (total days)",
            bl,
            fmt(bl["value"]),
            "trend",
            f"n={bl['n']}, open blockers={bl['open_blockers']}",
        ),
        (
            "PR first review (median hours)",
            fr,
            fmt(fr["value"]),
            f"<= {fmt(fr['target'], 0)}",
            f"n={fr['n']}, unreviewed open={len(fr['unreviewed_open'])}, "
            f"unreviewed merged={len(fr['unreviewed_merged'])}",
        ),
        (
            "PR merge (median hours)",
            mg,
            fmt(mg["value"]),
            f"<= {fmt(mg['target'], 0)}",
            f"n={mg['n']}",
        ),
        (
            "First-time-right",
            ftr,
            fmt(ftr["value"]),
            f">= {fmt(ftr['target'])}",
            f"{ftr['merged_without_changes']} of {ftr['n']} merged PRs",
        ),
        (
            "Rework ratio",
            rw,
            fmt(rw["value"]),
            f"<= {fmt(rw['target'])}",
            f"{rw['n_rework']} of {rw['n_closed']} closed issues",
        ),
        (
            "Defect count (bug issues)",
            df,
            fmt(df["value"], 0),
            "trend",
            f"open={df['open']}; escaped: {escaped}",
        ),
        (
            "CI pass rate",
            ci,
            fmt(ci["value"]),
            f">= {fmt(ci['target'])}",
            f"{ci['success']} of {ci['n']} completed runs",
        ),
        (
            "Contribution balance (Gini)",
            cg,
            fmt(cg["value"]),
            f"each share in [{cg['band'][0]}, {cg['band'][1]}]",
            f"flagged: {flagged}" if flagged else "no member flagged",
        ),
        (
            "Kaizen closure rate",
            kz,
            fmt(kz["value"]),
            f">= {fmt(kz['target'])}",
            f"{kz['closed']} of {kz['opened']} kaizen issues",
        ),
        (
            "Reproducibility check",
            rp,
            rp["value"],
            "pass",
            f"latest `{rp['workflow']}` run on default branch",
        ),
    ]


def render_dashboard(summary: dict, repo: str) -> str:
    k = summary["kpis"]
    c = summary["counts"]
    win = summary["window"]
    out: list[str] = []
    add = out.append

    add("# LSS process dashboard")
    add("")
    add(f"Repository: `{repo}`  ")
    add(f"Generated: {summary['generated_at'][:16].replace('T', ' ')} UTC  ")
    add(f"Window: {(win['since'] or 'beginning')[:10]} to {win['until'][:10]}  ")
    add(
        f"Inputs: {c['issues']} issues, {c['prs']} PRs, {c['reviews']} reviews, "
        f"{c['runs']} workflow runs, {c['commits']} commits"
    )
    add("")
    add(
        "Generated by `scripts/lss_metrics.py`; definitions in [KPIS.md](../KPIS.md). "
        "Do not edit by hand."
    )
    add("")
    if not any([c["issues"], c["prs"], c["runs"], c["commits"]]):
        add(
            "> **No data yet.** The repository has no issues, pull requests, workflow runs, "
            "or commits in the window."
        )
        add("")

    add("## KPIs vs targets")
    add("")
    add("| KPI | Value | Target | Status | Notes |")
    add("|---|---|---|---|---|")
    for name, obj, value, target, note in _kpi_rows(k):
        icon = STATUS_ICON[obj["status"]]
        add(f"| {name} | {value} | {target} | {icon} {obj['status']} | {note} |")
    add("")

    add("## Sprint summary")
    add("")
    if summary["sprints"]:
        add(
            "| Sprint | Dates | Status | Committed (issues / pts) | Done (issues / pts) | "
            "Added after planning | Velocity | Reliability | Escaped defects |"
        )
        add("|---|---|---|---|---|---|---|---|---|")
        for s in summary["sprints"]:
            dates = f"{s['start']} to {s['end']}" if s["start"] else ""
            committed = f"{s['committed_issues']} / {s['committed_points']}"
            done = f"{s['done_issues']} / {s['done_points']}"
            add(
                f"| {s['name']} | {dates} | {s['status']} | {committed} | {done} | "
                f"{s['added_after_planning']} | {s['velocity']} | "
                f"{fmt(s['commitment_reliability'])} | {s['escaped_defects']} |"
            )
    else:
        add("No sprint timeline in `project.yml` and no milestones found.")
    add("")

    add("## Contribution balance")
    add("")
    members = summary["contribution"]["members"]
    if members:
        add("| Member | Commits | PRs authored | Reviews given | Issues closed | Share | Flag |")
        add("|---|---|---|---|---|---|---|")
        for login, v in members.items():
            flag = "⚠️ outside band" if v["flag"] else ""
            add(
                f"| @{login} | {v['commits']} | {v['prs_authored']} | {v['reviews_given']} | "
                f"{v['issues_closed']} | {fmt(v['share_overall'])} | {flag} |"
            )
        others = summary["contribution"]["others"]
        if others:
            add("")
            names = ", ".join(f"{k2} ({v['commits']} commits)" for k2, v in others.items())
            add(f"Other authors (not in `project.yml` team): {names}")
    else:
        add("No contribution data yet.")
    add("")

    add("## Open blockers")
    add("")
    if summary["open_blockers"]:
        add("| Issue | Blocked for (days) | Since |")
        add("|---|---|---|")
        for b in summary["open_blockers"]:
            since = (b["since"] or "")[:10]
            add(f"| #{b['number']} {b['title']} | {fmt(b['days'], 1)} | {since} |")
    else:
        add("None.")
    add("")

    add("## Open PRs waiting for a first review")
    add("")
    waiting = summary["open_prs_waiting_review"]
    if waiting:
        add("| PR | Author | Open for (hours) | Over 48 h |")
        add("|---|---|---|---|")
        for p in waiting:
            over = "yes" if p["hours_open"] > 48 else ""
            hours = fmt(p["hours_open"], 1)
            add(f"| #{p['number']} {p['title']} | @{p['user']} | {hours} | {over} |")
    else:
        add("None.")
    add("")

    add("## Control chart signals")
    add("")
    charts = (("cycle_time", "Cycle time (days)"), ("pr_first_review", "PR first review (hours)"))
    for key, label in charts:
        chart = summary["control_charts"][key]
        lim = chart["limits"]
        if lim.get("ucl") is None:
            n = lim.get("n", 0)
            add(f"- {label}: {n} points; limits need at least {lss.MIN_POINTS_FOR_LIMITS}.")
        else:
            add(
                f"- {label}: n={lim['n']}, mean={fmt(lim['mean'])}, UNPL={fmt(lim['ucl'])}, "
                f"LNPL={fmt(lim['lcl'])}, target={chart['target']}. "
                f"Chart: `charts/{key}_xmr.png`"
            )
    add("")
    if summary["signals"]:
        add("| Chart | Rule | Items |")
        add("|---|---|---|")
        for s in summary["signals"]:
            if "item" in s:
                items = f"#{s['item']} ({fmt(s.get('value'))})"
            else:
                items = ", ".join(f"#{n}" for n in s["items"])
            add(f"| {s['chart']} | {s['rule']} | {items} |")
    else:
        add("No run-rule signals.")
    add("")
    add("## Next steps")
    add("")
    add(
        "- Review at the Thursday check-in. Two consecutive weeks of `warn` on the same KPI "
        "require a 5 Whys (`docs/lean-six-sigma/ROOT_CAUSE_TEMPLATE.md`)."
    )
    add(f"- Full data for this snapshot: `snapshots/{summary['generated_at'][:10]}.json`.")
    add("")
    return "\n".join(out)


def render_chart(
    points: list[dict],
    value_key: str,
    limits: dict,
    target: float,
    title: str,
    ylabel: str,
    path: Path,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    values = [p[value_key] for p in points]
    labels = [f"#{p['number']}" for p in points]
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 6), sharex=True, gridspec_kw={"height_ratios": [3, 1.5]}
    )
    x = list(range(1, len(values) + 1))
    if values:
        ax1.plot(x, values, marker="o", color="#1f77b4", label=ylabel)
        ax1.axhline(target, linestyle="--", color="#2ca02c", label=f"target {target}")
        if limits.get("ucl") is not None:
            ax1.axhline(limits["mean"], color="#7f7f7f", label=f"mean {limits['mean']}")
            ax1.axhline(limits["ucl"], color="#d62728", label=f"UNPL {limits['ucl']}")
            ax1.axhline(limits["lcl"], color="#d62728", label=f"LNPL {limits['lcl']}")
            for i, v in enumerate(values):
                if v > limits["ucl"]:
                    ax1.annotate(
                        labels[i],
                        (x[i], v),
                        textcoords="offset points",
                        xytext=(0, 6),
                        ha="center",
                        fontsize=8,
                    )
        ranges = [abs(values[i] - values[i - 1]) for i in range(1, len(values))]
        if ranges:
            ax2.plot(x[1:], ranges, marker="o", color="#ff7f0e")
            if limits.get("mr_ucl") is not None:
                ax2.axhline(limits["mr_bar"], color="#7f7f7f")
                ax2.axhline(limits["mr_ucl"], color="#d62728")
        ax1.set_xticks(x)
        ax1.set_xticklabels(labels, rotation=45, fontsize=8)
    else:
        ax1.text(0.5, 0.5, "no data yet", ha="center", va="center", transform=ax1.transAxes)
    ax1.set_title(title)
    ax1.set_ylabel(ylabel)
    ax2.set_ylabel("moving range")
    ax1.legend(loc="upper left", fontsize=8)
    ax1.grid(alpha=0.3)
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    plt.close(fig)


HISTORY_COLUMNS = [
    "date",
    "velocity_total",
    "commitment_reliability",
    "cycle_time_median_days",
    "lead_time_median_days",
    "throughput_per_week",
    "wip",
    "blocked_time_days",
    "pr_first_review_median_hours",
    "pr_merge_median_hours",
    "first_time_right",
    "rework_ratio",
    "defect_count",
    "ci_pass_rate",
    "contribution_gini",
    "kaizen_closure_rate",
    "reproducibility_check",
]


def history_row(summary: dict) -> dict:
    k = summary["kpis"]
    return {
        "date": summary["generated_at"][:10],
        "velocity_total": k["velocity"]["value"],
        "commitment_reliability": k["commitment_reliability"]["value"],
        "cycle_time_median_days": k["cycle_time_days"]["value"],
        "lead_time_median_days": k["lead_time_days"]["value"],
        "throughput_per_week": k["throughput_per_week"]["value"],
        "wip": k["wip"]["value"],
        "blocked_time_days": k["blocked_time_days"]["value"],
        "pr_first_review_median_hours": k["pr_first_review_hours"]["value"],
        "pr_merge_median_hours": k["pr_merge_hours"]["value"],
        "first_time_right": k["first_time_right"]["value"],
        "rework_ratio": k["rework_ratio"]["value"],
        "defect_count": k["defect_count"]["value"],
        "ci_pass_rate": k["ci_pass_rate"]["value"],
        "contribution_gini": k["contribution_gini"]["value"],
        "kaizen_closure_rate": k["kaizen_closure_rate"]["value"],
        "reproducibility_check": k["reproducibility_check"]["value"],
    }


def update_history(path: Path, row: dict) -> None:
    rows: list[dict] = []
    if path.exists():
        with path.open(newline="", encoding="utf-8") as fh:
            rows = [r for r in csv.DictReader(fh) if r.get("date") != row["date"]]
    rows.append({col: ("" if row.get(col) is None else row.get(col)) for col in HISTORY_COLUMNS})
    rows.sort(key=lambda r: r["date"])
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=HISTORY_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


# --------------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--repo", help="owner/name (default: `repo` in project.yml)")
    parser.add_argument("--out", default=str(REPO_ROOT / "docs" / "lean-six-sigma" / "metrics"))
    parser.add_argument("--since", help="ISO date; default is the formation start in project.yml")
    parser.add_argument(
        "--token", default=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    )
    parser.add_argument(
        "--offline-fixture", help="JSON with issues/prs/reviews/runs/commits; no network"
    )
    parser.add_argument("--config", default=str(REPO_ROOT / "project.yml"))
    parser.add_argument("--now", help="override the snapshot timestamp (ISO); for tests")
    args = parser.parse_args(argv)

    config = load_config(Path(args.config))
    repo = args.repo or config.get("repo") or "unknown/unknown"
    timeline = lss.normalize_timeline(config)
    since = args.since or (timeline[0]["start"].date().isoformat() if timeline else None)

    if args.offline_fixture:
        with open(args.offline_fixture, encoding="utf-8") as fh:
            data = json.load(fh)
        data = data.get("inputs", data)
        if "now" in data and not args.now:
            args.now = data["now"]
    else:
        if repo == "unknown/unknown":
            parser.error("--repo is required when project.yml has no `repo` key")
        data = GitHub(repo, args.token).fetch_all(since)

    now = lss.parse_iso(args.now) if args.now else datetime.now(UTC)
    summary = lss.summarize(
        data.get("issues", []),
        data.get("prs", []),
        data.get("reviews", []),
        data.get("runs", []),
        config,
        commits=data.get("commits", []),
        now=now,
        since=since,
    )
    summary["repo"] = repo
    summary["inputs"] = data

    out = Path(args.out)
    (out / "snapshots").mkdir(parents=True, exist_ok=True)
    (out / "charts").mkdir(parents=True, exist_ok=True)
    stamp = summary["generated_at"][:10]
    with (out / "snapshots" / f"{stamp}.json").open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, default=str)
    update_history(out / "history.csv", history_row(summary))
    (out / "DASHBOARD.md").write_text(render_dashboard(summary, repo), encoding="utf-8")
    cc = summary["control_charts"]
    render_chart(
        cc["cycle_time"]["points"],
        "days",
        cc["cycle_time"]["limits"],
        cc["cycle_time"]["target"],
        "Issue cycle time (XmR)",
        "days",
        out / "charts" / "cycle_time_xmr.png",
    )
    render_chart(
        cc["pr_first_review"]["points"],
        "hours",
        cc["pr_first_review"]["limits"],
        cc["pr_first_review"]["target"],
        "PR first-review turnaround (XmR)",
        "hours",
        out / "charts" / "pr_first_review_xmr.png",
    )

    warn = [name for name, obj in summary["kpis"].items() if obj["status"] == "warn"]
    print(f"Snapshot {stamp} written to {out}")
    print(
        f"KPIs in warn: {', '.join(warn) if warn else 'none'}; signals: {len(summary['signals'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

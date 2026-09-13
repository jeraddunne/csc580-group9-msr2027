"""Pure Lean Six Sigma metric computations for the Group 9 process dashboard.

Every function here works on plain dictionaries and lists so that it can be
tested offline. Network access and file output live in ``scripts/lss_metrics.py``.

Input shapes (all timestamps are ISO-8601 strings, ``None`` allowed):

* issue: ``number, title, state, state_reason, created_at, closed_at, labels [str],
  assignees [str], milestone (str|None), events [{event, created_at, label, assignee}],
  body (str), estimate (int, optional), pull_request (bool, optional)``
* pr: ``number, title, user, created_at, merged_at, closed_at, state, draft``
* review: ``pull_number, user, state, submitted_at``
* run: ``id, name, conclusion, status, created_at, head_branch``
* commit: ``sha, author, date``

The KPI definitions are documented in ``docs/lean-six-sigma/KPIS.md``; that file
and this module must stay in sync.
"""

from __future__ import annotations

import re
import statistics
from datetime import UTC, date, datetime, timedelta
from typing import Any

XMR_E2 = 2.66
XMR_D4 = 3.267
MIN_POINTS_FOR_LIMITS = 6

DEFAULT_TARGETS: dict[str, float] = {
    "cycle_time_days_target": 5,
    "lead_time_days_target": 10,
    "pr_first_review_hours_target": 48,
    "pr_merge_hours_target": 96,
    "commitment_reliability_target": 0.8,
    "first_time_right_target": 0.75,
    "rework_ratio_max": 0.15,
    "contribution_share_min": 0.15,
    "contribution_share_max": 0.45,
    "ci_pass_rate_target": 0.9,
    "kaizen_closure_rate_target": 0.7,
}
DEFAULT_WIP_LIMIT = 5
DEFAULT_REPRO_WORKFLOW = "CI"
METRICS_WORKFLOW_NAME = "LSS metrics"

IN_PROGRESS_LABELS = {"in progress", "status:in progress", "status: in progress", "in-progress"}
_POINT_LABEL = re.compile(r"^(?:sp|points?|estimate)\s*[:=]\s*(\d+)$", re.IGNORECASE)
_POINT_BODY = re.compile(r"^\s*(?:estimate|story points?)\s*[:=]\s*(\d+)\s*$", re.IGNORECASE | re.M)


# --------------------------------------------------------------------------- time helpers


def parse_iso(value: Any) -> datetime | None:
    """Parse an ISO-8601 string (or date/datetime) into an aware UTC datetime."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, date):
        dt = datetime(value.year, value.month, value.day)
    else:
        text = str(value).strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _now(now: datetime | None) -> datetime:
    return now.astimezone(UTC) if now else datetime.now(UTC)


def _days(start: datetime, end: datetime) -> float:
    return round((end - start).total_seconds() / 86400.0, 3)


def _hours(start: datetime, end: datetime) -> float:
    return round((end - start).total_seconds() / 3600.0, 3)


def _median(values: list[float]) -> float | None:
    return round(statistics.median(values), 3) if values else None


def _mean(values: list[float]) -> float | None:
    return round(statistics.fmean(values), 3) if values else None


def _ratio(num: float, den: float) -> float | None:
    return round(num / den, 3) if den else None


# --------------------------------------------------------------------------- issue helpers


def is_pull(issue: dict) -> bool:
    return bool(issue.get("pull_request"))


def labels_of(issue: dict) -> set[str]:
    out = set()
    for label in issue.get("labels") or []:
        name = label.get("name") if isinstance(label, dict) else label
        if name:
            out.add(str(name).lower())
    return out


def assignees_of(issue: dict) -> list[str]:
    out = []
    for a in issue.get("assignees") or []:
        login = a.get("login") if isinstance(a, dict) else a
        if login:
            out.append(str(login))
    return out


def milestone_of(issue: dict) -> str | None:
    ms = issue.get("milestone")
    if isinstance(ms, dict):
        return ms.get("title")
    return ms


def closed_completed(issue: dict) -> bool:
    """Closed and not cancelled (GitHub ``state_reason`` ``not_planned``)."""
    if issue.get("state") != "closed" or not issue.get("closed_at"):
        return False
    return (issue.get("state_reason") or "completed") != "not_planned"


def issue_points(issue: dict) -> int:
    """Story points from ``estimate``, a points label, or an ``Estimate: N`` body line."""
    est = issue.get("estimate")
    if isinstance(est, (int, float)) and est >= 0:
        return int(est)
    for label in labels_of(issue):
        m = _POINT_LABEL.match(label)
        if m:
            return int(m.group(1))
    body = issue.get("body") or ""
    m = _POINT_BODY.search(body)
    return int(m.group(1)) if m else 0


def _events(issue: dict) -> list[dict]:
    evs = []
    for ev in issue.get("events") or []:
        ts = parse_iso(ev.get("created_at"))
        if ts is None:
            continue
        label = ev.get("label")
        if isinstance(label, dict):
            label = label.get("name")
        assignee = ev.get("assignee")
        if isinstance(assignee, dict):
            assignee = assignee.get("login")
        evs.append(
            {
                "event": ev.get("event"),
                "at": ts,
                "label": (str(label).lower() if label else None),
                "assignee": assignee,
            }
        )
    evs.sort(key=lambda e: e["at"])
    return evs


def work_start(issue: dict) -> tuple[datetime | None, bool]:
    """Approximate start of work: first assignment or first in-progress label.

    Returns ``(timestamp, approximated)``. ``approximated`` is True when neither
    event exists and ``created_at`` is used instead.
    """
    candidates = [
        e["at"]
        for e in _events(issue)
        if e["event"] == "assigned"
        or (e["event"] == "labeled" and e["label"] in IN_PROGRESS_LABELS)
    ]
    if candidates:
        return min(candidates), False
    created = parse_iso(issue.get("created_at"))
    return created, True


def compute_cycle_time(issue: dict) -> dict | None:
    """Days from start of work to closure for a completed issue."""
    if is_pull(issue) or not closed_completed(issue):
        return None
    closed = parse_iso(issue.get("closed_at"))
    start, approximated = work_start(issue)
    if closed is None or start is None:
        return None
    if start > closed:
        start = closed
    return {
        "number": issue.get("number"),
        "title": issue.get("title"),
        "days": _days(start, closed),
        "start": start.isoformat(),
        "closed_at": closed.isoformat(),
        "approximated": approximated,
    }


def compute_lead_time(issue: dict) -> dict | None:
    """Days from creation to closure for a completed issue."""
    if is_pull(issue) or not closed_completed(issue):
        return None
    created = parse_iso(issue.get("created_at"))
    closed = parse_iso(issue.get("closed_at"))
    if created is None or closed is None:
        return None
    return {
        "number": issue.get("number"),
        "title": issue.get("title"),
        "days": _days(created, closed),
        "created_at": created.isoformat(),
        "closed_at": closed.isoformat(),
    }


def blocked_time(issue: dict, now: datetime | None = None) -> dict:
    """Total days an issue carried the ``blocker`` label, and whether it still does."""
    end_default = parse_iso(issue.get("closed_at")) or _now(now)
    total = 0.0
    open_since: datetime | None = None
    for e in _events(issue):
        if e["label"] != "blocker":
            continue
        if e["event"] == "labeled" and open_since is None:
            open_since = e["at"]
        elif e["event"] == "unlabeled" and open_since is not None:
            total += (e["at"] - open_since).total_seconds() / 86400.0
            open_since = None
    if open_since is None and "blocker" in labels_of(issue) and issue.get("state") == "open":
        open_since = parse_iso(issue.get("created_at"))
    still_blocked = False
    if open_since is not None:
        total += (end_default - open_since).total_seconds() / 86400.0
        still_blocked = issue.get("state") == "open"
    return {
        "number": issue.get("number"),
        "title": issue.get("title"),
        "days": round(total, 3),
        "still_blocked": still_blocked,
        "since": open_since.isoformat() if (still_blocked and open_since) else None,
    }


def is_in_progress(issue: dict) -> bool:
    return issue.get("state") == "open" and (
        bool(assignees_of(issue)) or bool(labels_of(issue) & IN_PROGRESS_LABELS)
    )


# --------------------------------------------------------------------------- PR helpers


def _reviews_by_pr(reviews: list[dict]) -> dict[int, list[dict]]:
    out: dict[int, list[dict]] = {}
    for r in reviews or []:
        num = r.get("pull_number")
        if num is None:
            continue
        out.setdefault(int(num), []).append(r)
    return out


def pr_turnarounds(prs: list[dict], reviews: list[dict]) -> dict:
    """First-review hours (excluding self-reviews) and merge hours per PR."""
    by_pr = _reviews_by_pr(reviews)
    first_review: list[dict] = []
    merge: list[dict] = []
    unreviewed_open: list[int] = []
    unreviewed_merged: list[int] = []
    for pr in sorted(prs or [], key=lambda p: parse_iso(p.get("created_at")) or _now(None)):
        created = parse_iso(pr.get("created_at"))
        if created is None:
            continue
        number = int(pr.get("number"))
        author = pr.get("user")
        others = [
            parse_iso(r.get("submitted_at"))
            for r in by_pr.get(number, [])
            if r.get("user") != author and parse_iso(r.get("submitted_at"))
        ]
        if others:
            first = min(others)
            first_review.append(
                {
                    "number": number,
                    "title": pr.get("title"),
                    "hours": _hours(created, first),
                    "created_at": created.isoformat(),
                    "first_review_at": first.isoformat(),
                }
            )
        elif pr.get("merged_at"):
            unreviewed_merged.append(number)
        elif pr.get("state") == "open":
            unreviewed_open.append(number)
        merged = parse_iso(pr.get("merged_at"))
        if merged is not None:
            merge.append(
                {
                    "number": number,
                    "title": pr.get("title"),
                    "hours": _hours(created, merged),
                    "created_at": created.isoformat(),
                    "merged_at": merged.isoformat(),
                }
            )
    return {
        "first_review": first_review,
        "merge": merge,
        "unreviewed_open": unreviewed_open,
        "unreviewed_merged": unreviewed_merged,
    }


def first_time_right(prs: list[dict], reviews: list[dict]) -> dict:
    """Share of merged PRs with no CHANGES_REQUESTED review."""
    by_pr = _reviews_by_pr(reviews)
    merged = [p for p in prs or [] if p.get("merged_at")]
    clean = 0
    for pr in merged:
        states = {str(r.get("state", "")).upper() for r in by_pr.get(int(pr["number"]), [])}
        if "CHANGES_REQUESTED" not in states:
            clean += 1
    return {"value": _ratio(clean, len(merged)), "n": len(merged), "merged_without_changes": clean}


# --------------------------------------------------------------------------- quality helpers


def rework_ratio(issues: list[dict]) -> dict:
    """Closed issues that carry ``rework`` or were reopened, over closed issues."""
    closed = [i for i in issues or [] if not is_pull(i) and i.get("state") == "closed"]
    rework = [
        i
        for i in closed
        if "rework" in labels_of(i) or any(e["event"] == "reopened" for e in _events(i))
    ]
    return {
        "value": _ratio(len(rework), len(closed)),
        "n_closed": len(closed),
        "n_rework": len(rework),
        "numbers": [i.get("number") for i in rework],
    }


def gini(values: list[float]) -> float:
    """Gini coefficient of a non-negative vector (0 = even, 1 = concentrated)."""
    vals = sorted(float(v) for v in values if v is not None and v >= 0)
    n = len(vals)
    total = sum(vals)
    if n == 0 or total == 0:
        return 0.0
    cum = sum((i + 1) * v for i, v in enumerate(vals))
    return round((2.0 * cum) / (n * total) - (n + 1.0) / n, 4)


def contribution_balance(
    commits: list[dict],
    prs: list[dict],
    reviews: list[dict],
    issues: list[dict],
    team_logins: list[str],
    config: dict | None = None,
) -> dict:
    """Per-member counts and shares across commits, PRs, reviews, closed issues."""
    targets = _targets(config)
    lo, hi = targets["contribution_share_min"], targets["contribution_share_max"]
    counts: dict[str, dict[str, int]] = {}

    def bump(login: Any, key: str) -> None:
        if not login:
            login = "unknown"
        counts.setdefault(
            str(login), {"commits": 0, "prs_authored": 0, "reviews_given": 0, "issues_closed": 0}
        )
        counts[str(login)][key] += 1

    for c in commits or []:
        bump(c.get("author"), "commits")
    for p in prs or []:
        bump(p.get("user"), "prs_authored")
    seen_review_pairs: set[tuple[int, str]] = set()
    for r in reviews or []:
        key = (int(r.get("pull_number") or 0), str(r.get("user")))
        if key in seen_review_pairs:
            continue
        seen_review_pairs.add(key)
        bump(r.get("user"), "reviews_given")
    for i in issues or []:
        if is_pull(i) or not closed_completed(i):
            continue
        for a in assignees_of(i):
            bump(a, "issues_closed")

    categories = ["commits", "prs_authored", "reviews_given", "issues_closed"]
    members = [str(m) for m in team_logins] if team_logins else sorted(counts)
    for m in members:
        counts.setdefault(m, {k: 0 for k in categories})
    totals = {k: sum(counts[m][k] for m in members) for k in categories}
    result_members: dict[str, dict] = {}
    for m in members:
        shares = {}
        for k in categories:
            shares[f"share_{k}"] = _ratio(counts[m][k], totals[k])
        present = [v for v in shares.values() if v is not None]
        overall = round(statistics.fmean(present), 3) if present else None
        flag = overall is not None and not (lo <= overall <= hi)
        result_members[m] = {**counts[m], **shares, "share_overall": overall, "flag": flag}
    others = {k: v for k, v in counts.items() if k not in members}
    overall_vec = [v["share_overall"] or 0.0 for v in result_members.values()]
    return {
        "members": result_members,
        "others": others,
        "totals": totals,
        "gini": gini(overall_vec) if any(overall_vec) else None,
        "band": [lo, hi],
    }


# --------------------------------------------------------------------------- SPC helpers


def xmr_limits(values: list[float]) -> dict:
    """Individuals (X) and moving range (mR) chart limits.

    ``ucl``/``lcl`` = mean +/- 2.66 * mR-bar (lcl floored at 0); ``mr_ucl`` = 3.267 * mR-bar.
    Returns ``None`` limits when fewer than two points exist.
    """
    vals = [float(v) for v in values]
    n = len(vals)
    if n == 0:
        return {"n": 0, "mean": None, "mr_bar": None, "ucl": None, "lcl": None, "mr_ucl": None}
    mean = statistics.fmean(vals)
    if n < 2:
        return {
            "n": n,
            "mean": round(mean, 3),
            "mr_bar": None,
            "ucl": None,
            "lcl": None,
            "mr_ucl": None,
        }
    ranges = [abs(vals[i] - vals[i - 1]) for i in range(1, n)]
    mr_bar = statistics.fmean(ranges)
    return {
        "n": n,
        "mean": round(mean, 3),
        "mr_bar": round(mr_bar, 3),
        "ucl": round(mean + XMR_E2 * mr_bar, 3),
        "lcl": round(max(0.0, mean - XMR_E2 * mr_bar), 3),
        "mr_ucl": round(XMR_D4 * mr_bar, 3),
    }


def run_rules(values: list[float], limits: dict | None = None) -> list[dict]:
    """Western-Electric style signals: beyond limits, 8 same side, 6 trending."""
    vals = [float(v) for v in values]
    if len(vals) < MIN_POINTS_FOR_LIMITS:
        return []
    lim = limits or xmr_limits(vals)
    signals: list[dict] = []
    mean, ucl, lcl = lim.get("mean"), lim.get("ucl"), lim.get("lcl")
    if ucl is not None:
        for i, v in enumerate(vals):
            if v > ucl or (lcl is not None and v < lcl and lcl > 0):
                signals.append({"rule": "beyond_limits", "index": i, "value": v})
    if mean is not None:
        side = [1 if v > mean else (-1 if v < mean else 0) for v in vals]
        start = 0
        for i in range(1, len(side) + 1):
            if i == len(side) or side[i] != side[start] or side[start] == 0:
                if side[start] != 0 and i - start >= 8:
                    signals.append({"rule": "eight_same_side", "start": start, "end": i - 1})
                start = i

    def sign(a: float, b: float) -> int:
        return 1 if b > a else (-1 if b < a else 0)

    i = 1
    while i < len(vals):
        d = sign(vals[i - 1], vals[i])
        if d == 0:
            i += 1
            continue
        j = i
        while j + 1 < len(vals) and sign(vals[j], vals[j + 1]) == d:
            j += 1
        if (j - i + 2) >= 6:
            signals.append({"rule": "six_trending", "start": i - 1, "end": j})
        i = j + 1
    return signals


# --------------------------------------------------------------------------- config helpers


def _targets(config: dict | None) -> dict[str, float]:
    out = dict(DEFAULT_TARGETS)
    metrics = (config or {}).get("metrics") or {}
    for k in out:
        if metrics.get(k) is not None:
            out[k] = float(metrics[k])
    return out


def sprint_name(key: str) -> str:
    text = str(key).replace("_", " ").replace("-", " ").strip()
    return " ".join(w.capitalize() for w in text.split())


def normalize_timeline(config: dict | None) -> list[dict]:
    """Return ``[{name, start, end}]`` sorted by start from a dict or list timeline."""
    raw = (config or {}).get("timeline") or []
    items: list[dict] = []
    if isinstance(raw, dict):
        for key, val in raw.items():
            if isinstance(val, dict):
                items.append(
                    {
                        "name": sprint_name(val.get("name") or key),
                        "start": val.get("start"),
                        "end": val.get("end"),
                    }
                )
    else:
        for val in raw:
            if isinstance(val, dict):
                items.append(
                    {
                        "name": sprint_name(val.get("name") or val.get("key") or "Sprint"),
                        "start": val.get("start"),
                        "end": val.get("end"),
                    }
                )
    out = []
    for it in items:
        s, e = parse_iso(it["start"]), parse_iso(it["end"])
        if s is None or e is None:
            continue
        e = e.replace(hour=23, minute=59, second=59)
        out.append({"name": it["name"], "start": s, "end": e})
    out.sort(key=lambda x: x["start"])
    return out


def team_logins(config: dict | None) -> list[str]:
    out = []
    for m in (config or {}).get("team") or []:
        login = m.get("github") if isinstance(m, dict) else m
        if login:
            out.append(str(login).lstrip("@"))
    return out


def sprint_for(issue: dict, timeline: list[dict]) -> str:
    """Milestone title if it matches a sprint, else the sprint containing ``closed_at``."""
    ms = milestone_of(issue)
    names = {t["name"].lower(): t["name"] for t in timeline}
    if ms:
        key = sprint_name(ms).lower()
        if key in names:
            return names[key]
        return sprint_name(ms)
    closed = parse_iso(issue.get("closed_at"))
    if closed:
        for t in timeline:
            if t["start"] <= closed <= t["end"]:
                return t["name"]
    return "Unscheduled"


# --------------------------------------------------------------------------- summary


def _status(value: float | None, target: float | None, higher_is_better: bool) -> str:
    if value is None:
        return "nodata"
    if target is None:
        return "info"
    ok = value >= target if higher_is_better else value <= target
    return "ok" if ok else "warn"


def _sprint_rows(issues: list[dict], timeline: list[dict], now: datetime) -> list[dict]:
    by_sprint: dict[str, list[dict]] = {}
    for i in issues:
        if is_pull(i):
            continue
        by_sprint.setdefault(sprint_for(i, timeline), []).append(i)
    windows = {t["name"]: t for t in timeline}
    rows = []
    ordered = [t["name"] for t in timeline] + sorted(k for k in by_sprint if k not in windows)
    for name in ordered:
        items = by_sprint.get(name, [])
        win = windows.get(name)
        if not items and win is None:
            continue
        plan_cutoff = (
            (win["start"] + timedelta(days=1)).replace(hour=23, minute=59) if win else None
        )
        committed = [
            i
            for i in items
            if plan_cutoff is None or (parse_iso(i.get("created_at")) or now) <= plan_cutoff
        ]
        added = [i for i in items if i not in committed]
        done = [i for i in items if closed_completed(i)]
        committed_pts = sum(issue_points(i) for i in committed)
        done_pts = sum(issue_points(i) for i in done if i in committed)
        if committed_pts > 0:
            reliability = _ratio(done_pts, committed_pts)
        else:
            reliability = _ratio(len([i for i in done if i in committed]), len(committed))
        escaped = 0
        if win:
            escaped = len(
                [
                    i
                    for i in items
                    if "bug" in labels_of(i)
                    and (parse_iso(i.get("created_at")) or now) > win["end"]
                ]
            )
        rows.append(
            {
                "name": name,
                "start": win["start"].date().isoformat() if win else None,
                "end": win["end"].date().isoformat() if win else None,
                "total_issues": len(items),
                "committed_issues": len(committed),
                "committed_points": committed_pts,
                "done_issues": len(done),
                "done_points": sum(issue_points(i) for i in done),
                "added_after_planning": len(added),
                "velocity": sum(issue_points(i) for i in done),
                "commitment_reliability": reliability,
                "escaped_defects": escaped,
                "status": "active"
                if win and win["start"] <= now <= win["end"]
                else ("past" if win and now > win["end"] else "future"),
            }
        )
    return rows


def summarize(
    issues: list[dict],
    prs: list[dict],
    reviews: list[dict],
    runs: list[dict],
    config: dict | None = None,
    commits: list[dict] | None = None,
    now: datetime | None = None,
    since: Any = None,
) -> dict:
    """Compute every KPI in ``docs/lean-six-sigma/KPIS.md`` from normalized inputs."""
    config = config or {}
    now_dt = _now(now)
    targets = _targets(config)
    wip_limit = int(config.get("wip_limit") or DEFAULT_WIP_LIMIT)
    timeline = normalize_timeline(config)
    since_dt = parse_iso(since) or (timeline[0]["start"] if timeline else None)
    issues = [i for i in issues or [] if not is_pull(i)]
    if since_dt:
        issues = [i for i in issues if (parse_iso(i.get("created_at")) or now_dt) >= since_dt]
        prs = [p for p in prs or [] if (parse_iso(p.get("created_at")) or now_dt) >= since_dt]
        runs = [r for r in runs or [] if (parse_iso(r.get("created_at")) or now_dt) >= since_dt]
        commits = [c for c in commits or [] if (parse_iso(c.get("date")) or now_dt) >= since_dt]
    prs = list(prs or [])
    runs = list(runs or [])
    commits = list(commits or [])
    reviews = list(reviews or [])

    # flow
    closed_done = [i for i in issues if closed_completed(i)]
    cycle = [c for c in (compute_cycle_time(i) for i in issues) if c]
    cycle.sort(key=lambda c: c["closed_at"])
    lead = [lt for lt in (compute_lead_time(i) for i in issues) if lt]
    window_days = max(1.0, (now_dt - since_dt).total_seconds() / 86400.0) if since_dt else 7.0
    throughput = round(len(closed_done) / max(1.0, window_days / 7.0), 3)
    wip_items = [i for i in issues if is_in_progress(i)]
    blocked = [blocked_time(i, now_dt) for i in issues]
    blocked_nonzero = [b for b in blocked if b["days"] > 0 or b["still_blocked"]]
    open_blockers = sorted([b for b in blocked if b["still_blocked"]], key=lambda b: -b["days"])

    # PRs
    turn = pr_turnarounds(prs, reviews)
    first_review_hours = [t["hours"] for t in turn["first_review"]]
    merge_hours = [t["hours"] for t in turn["merge"]]
    ftr = first_time_right(prs, reviews)
    open_prs_waiting = []
    for pr in prs:
        if pr.get("state") == "open" and int(pr["number"]) in turn["unreviewed_open"]:
            created = parse_iso(pr.get("created_at")) or now_dt
            open_prs_waiting.append(
                {
                    "number": pr["number"],
                    "title": pr.get("title"),
                    "user": pr.get("user"),
                    "hours_open": _hours(created, now_dt),
                }
            )

    # quality
    rework = rework_ratio(issues)
    defects = [i for i in issues if "bug" in labels_of(i)]
    completed_runs = [
        r
        for r in runs
        if r.get("name") != METRICS_WORKFLOW_NAME
        and str(r.get("conclusion") or "").lower() in {"success", "failure", "timed_out"}
    ]
    ci_success = len([r for r in completed_runs if r.get("conclusion") == "success"])
    ci_rate = _ratio(ci_success, len(completed_runs))
    repro_name = str(
        (config.get("metrics") or {}).get("reproducibility_workflow") or DEFAULT_REPRO_WORKFLOW
    )
    default_branch = str(config.get("default_branch") or "main")
    repro_runs = [
        r
        for r in runs
        if r.get("name") == repro_name
        and (r.get("head_branch") in (None, default_branch))
        and str(r.get("conclusion") or "").lower() in {"success", "failure", "timed_out"}
    ]
    repro_runs.sort(key=lambda r: parse_iso(r.get("created_at")) or now_dt)
    if repro_runs:
        repro = "pass" if repro_runs[-1].get("conclusion") == "success" else "fail"
    else:
        repro = "nodata"

    kaizen = [i for i in issues if "kaizen" in labels_of(i)]
    kaizen_closed = [i for i in kaizen if i.get("state") == "closed"]

    # people
    contribution = contribution_balance(commits, prs, reviews, issues, team_logins(config), config)

    # sprints
    sprints = _sprint_rows(issues, timeline, now_dt)
    active = next((s for s in sprints if s["status"] == "active"), None)
    latest_past = next(
        (s for s in reversed(sprints) if s["status"] == "past" and s["committed_issues"]), None
    )
    reliability_ref = active or latest_past
    velocity_total = sum(s["velocity"] for s in sprints)

    # control charts
    cycle_vals = [c["days"] for c in cycle]
    cycle_limits = (
        xmr_limits(cycle_vals) if len(cycle_vals) >= MIN_POINTS_FOR_LIMITS else xmr_limits([])
    )
    cycle_signals = (
        run_rules(cycle_vals, cycle_limits) if cycle_limits.get("ucl") is not None else []
    )
    fr_limits = (
        xmr_limits(first_review_hours)
        if len(first_review_hours) >= MIN_POINTS_FOR_LIMITS
        else xmr_limits([])
    )
    fr_signals = (
        run_rules(first_review_hours, fr_limits) if fr_limits.get("ucl") is not None else []
    )

    def annotate(signals: list[dict], points: list[dict], key: str) -> list[dict]:
        out = []
        for s in signals:
            s = dict(s)
            if "index" in s:
                s["item"] = points[s["index"]]["number"]
            else:
                s["items"] = [points[i]["number"] for i in range(s["start"], s["end"] + 1)]
            s["chart"] = key
            out.append(s)
        return out

    signals = annotate(cycle_signals, cycle, "cycle_time") + annotate(
        fr_signals, turn["first_review"], "pr_first_review"
    )

    member_flags = [m for m, v in contribution["members"].items() if v.get("flag")]
    any_share = any(v.get("share_overall") is not None for v in contribution["members"].values())

    kpis = {
        "velocity": {
            "value": velocity_total,
            "unit": "points",
            "target": None,
            "status": "info",
            "per_sprint": {s["name"]: s["velocity"] for s in sprints},
        },
        "commitment_reliability": {
            "value": reliability_ref["commitment_reliability"] if reliability_ref else None,
            "sprint": reliability_ref["name"] if reliability_ref else None,
            "unit": "ratio",
            "target": targets["commitment_reliability_target"],
            "status": _status(
                reliability_ref["commitment_reliability"] if reliability_ref else None,
                targets["commitment_reliability_target"],
                True,
            ),
        },
        "cycle_time_days": {
            "value": _median(cycle_vals),
            "median": _median(cycle_vals),
            "mean": _mean(cycle_vals),
            "n": len(cycle_vals),
            "approximated": len([c for c in cycle if c["approximated"]]),
            "unit": "days",
            "target": targets["cycle_time_days_target"],
            "status": _status(_median(cycle_vals), targets["cycle_time_days_target"], False),
        },
        "lead_time_days": {
            "value": _median([lt["days"] for lt in lead]),
            "median": _median([lt["days"] for lt in lead]),
            "mean": _mean([lt["days"] for lt in lead]),
            "n": len(lead),
            "unit": "days",
            "target": targets["lead_time_days_target"],
            "status": _status(
                _median([lt["days"] for lt in lead]), targets["lead_time_days_target"], False
            ),
        },
        "throughput_per_week": {
            "value": throughput,
            "closed": len(closed_done),
            "window_days": round(window_days, 1),
            "unit": "issues/week",
            "target": None,
            "status": "info",
        },
        "wip": {
            "value": len(wip_items),
            "limit": wip_limit,
            "numbers": [i.get("number") for i in wip_items],
            "unit": "issues",
            "target": wip_limit,
            "status": _status(len(wip_items), wip_limit, False),
        },
        "blocked_time_days": {
            "value": round(sum(b["days"] for b in blocked_nonzero), 3),
            "total": round(sum(b["days"] for b in blocked_nonzero), 3),
            "mean": _mean([b["days"] for b in blocked_nonzero]),
            "n": len(blocked_nonzero),
            "open_blockers": len(open_blockers),
            "unit": "days",
            "target": None,
            "status": "info",
        },
        "pr_first_review_hours": {
            "value": _median(first_review_hours),
            "median": _median(first_review_hours),
            "mean": _mean(first_review_hours),
            "n": len(first_review_hours),
            "unreviewed_open": turn["unreviewed_open"],
            "unreviewed_merged": turn["unreviewed_merged"],
            "unit": "hours",
            "target": targets["pr_first_review_hours_target"],
            "status": _status(
                _median(first_review_hours), targets["pr_first_review_hours_target"], False
            ),
        },
        "pr_merge_hours": {
            "value": _median(merge_hours),
            "median": _median(merge_hours),
            "mean": _mean(merge_hours),
            "n": len(merge_hours),
            "unit": "hours",
            "target": targets["pr_merge_hours_target"],
            "status": _status(_median(merge_hours), targets["pr_merge_hours_target"], False),
        },
        "first_time_right": {
            **ftr,
            "unit": "ratio",
            "target": targets["first_time_right_target"],
            "status": _status(ftr["value"], targets["first_time_right_target"], True),
        },
        "rework_ratio": {
            **rework,
            "unit": "ratio",
            "target": targets["rework_ratio_max"],
            "status": _status(rework["value"], targets["rework_ratio_max"], False),
        },
        "defect_count": {
            "value": len(defects),
            "open": len([d for d in defects if d.get("state") == "open"]),
            "escaped_by_sprint": {s["name"]: s["escaped_defects"] for s in sprints},
            "unit": "issues",
            "target": None,
            "status": "info",
        },
        "ci_pass_rate": {
            "value": ci_rate,
            "n": len(completed_runs),
            "success": ci_success,
            "unit": "ratio",
            "target": targets["ci_pass_rate_target"],
            "status": _status(ci_rate, targets["ci_pass_rate_target"], True),
        },
        "contribution_gini": {
            "value": contribution["gini"],
            "flagged": member_flags,
            "band": contribution["band"],
            "unit": "gini",
            "target": None,
            "status": ("nodata" if not any_share else ("warn" if member_flags else "ok")),
        },
        "kaizen_closure_rate": {
            "value": _ratio(len(kaizen_closed), len(kaizen)),
            "opened": len(kaizen),
            "closed": len(kaizen_closed),
            "unit": "ratio",
            "target": targets["kaizen_closure_rate_target"],
            "status": _status(
                _ratio(len(kaizen_closed), len(kaizen)), targets["kaizen_closure_rate_target"], True
            ),
        },
        "reproducibility_check": {
            "value": repro,
            "workflow": repro_name,
            "unit": "pass/fail",
            "target": "pass",
            "status": ("nodata" if repro == "nodata" else ("ok" if repro == "pass" else "warn")),
        },
    }

    return {
        "generated_at": now_dt.isoformat(),
        "window": {
            "since": since_dt.isoformat() if since_dt else None,
            "until": now_dt.isoformat(),
        },
        "counts": {
            "issues": len(issues),
            "prs": len(prs),
            "reviews": len(reviews),
            "runs": len(runs),
            "commits": len(commits),
        },
        "targets": targets,
        "wip_limit": wip_limit,
        "sprints": sprints,
        "kpis": kpis,
        "contribution": contribution,
        "control_charts": {
            "cycle_time": {
                "points": cycle,
                "limits": cycle_limits,
                "signals": cycle_signals,
                "target": targets["cycle_time_days_target"],
            },
            "pr_first_review": {
                "points": turn["first_review"],
                "limits": fr_limits,
                "signals": fr_signals,
                "target": targets["pr_first_review_hours_target"],
            },
        },
        "open_blockers": open_blockers,
        "open_prs_waiting_review": sorted(open_prs_waiting, key=lambda p: -p["hours_open"]),
        "signals": signals,
    }

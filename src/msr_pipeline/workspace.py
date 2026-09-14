"""Team workspace digest: sign-ups, findings, decisions, and who is working on what.

Issues created from the Work sign-up, Research finding, and Decision needed forms are
parsed into a single Markdown page (docs/workspace/DIGEST.md). The GitHub calls live in
scripts/workspace_digest.py; everything here is pure and tested.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import UTC, datetime

NO_RESPONSE = "_No response_"
_HEADING = re.compile(r"^###\s+(.+?)\s*$")


def parse_form_body(body: str | None) -> dict[str, str]:
    """Split a GitHub issue-form body into {heading: value}. Empty answers become ""."""
    sections: dict[str, str] = {}
    current: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        if current is not None:
            value = "\n".join(buffer).strip()
            sections[current] = "" if value == NO_RESPONSE else value

    for line in (body or "").splitlines():
        match = _HEADING.match(line)
        if match:
            flush()
            current, buffer = match.group(1), []
        elif current is not None:
            buffer.append(line)
    flush()
    return sections


def cell(value: object, limit: int = 120) -> str:
    """Make a value safe for a Markdown table cell."""
    text = " ".join(str(value if value is not None else "").split())
    text = text.replace("|", "\\|")
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _link(issue: dict) -> str:
    return f"[#{issue['number']}]({issue['url']})" if issue.get("url") else f"#{issue['number']}"


def _login(issue: dict) -> str:
    author = issue.get("author") or {}
    return author.get("login", "") if isinstance(author, dict) else str(author)


def _milestone(issue: dict) -> str:
    ms = issue.get("milestone") or {}
    return ms.get("title", "") if isinstance(ms, dict) else str(ms)


def _first(fields: dict[str, str], *names: str) -> str:
    for name in names:
        for key, value in fields.items():
            if key.lower().startswith(name.lower()) and value:
                return value
    return ""


def signup_rows(issues: list[dict]) -> list[list[str]]:
    rows = []
    for issue in issues:
        f = parse_form_body(issue.get("body"))
        rows.append(
            [
                cell(_first(f, "Member") or _login(issue)),
                cell(_first(f, "Sprint")),
                cell(_first(f, "First choice")),
                cell(_first(f, "Second choice")),
                cell(_first(f, "Third choice")),
                cell(_first(f, "Hours")),
                cell(_first(f, "Specific issues")),
                _link(issue),
            ]
        )
    return sorted(rows, key=lambda r: (r[1], r[0]))


def finding_rows(issues: list[dict]) -> list[list[str]]:
    rows = []
    for issue in issues:
        f = parse_form_body(issue.get("body"))
        title = re.sub(r"^\[Finding\]\s*", "", issue.get("title", ""))
        rows.append(
            [
                _link(issue),
                cell(title),
                cell(_first(f, "Dataset")),
                cell(_first(f, "Confidence")),
                cell(_login(issue)),
                cell(issue.get("state", "").lower()),
            ]
        )
    return rows


def decision_rows(issues: list[dict]) -> list[list[str]]:
    rows = []
    for issue in issues:
        f = parse_form_body(issue.get("body"))
        title = re.sub(r"^\[Decision\]\s*", "", issue.get("title", ""))
        state = "decided" if issue.get("state", "").upper() == "CLOSED" else "open"
        rows.append([_link(issue), cell(title), cell(_first(f, "Decide by")), state])
    return rows


def work_by_assignee(issues: list[dict]) -> dict[str, list[list[str]]]:
    grouped: dict[str, list[list[str]]] = defaultdict(list)
    for issue in issues:
        assignees = [a.get("login", "") for a in issue.get("assignees") or []] or ["(unassigned)"]
        for login in assignees:
            grouped[login].append([_link(issue), cell(issue.get("title", "")), _milestone(issue)])
    return dict(sorted(grouped.items(), key=lambda kv: (kv[0] == "(unassigned)", kv[0])))


def _table(headers: list[str], rows: list[list[str]], empty: str) -> list[str]:
    if not rows:
        return [f"_{empty}_", ""]
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return out + [""]


def render_digest(
    signups: list[dict],
    findings: list[dict],
    decisions: list[dict],
    open_work: list[dict],
    repo: str = "",
    generated_at: datetime | None = None,
) -> str:
    ts = (generated_at or datetime.now(UTC)).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Team workspace digest",
        "",
        f"Generated {ts} by `scripts/workspace_digest.py`"
        + (f" from `{repo}`" if repo else "")
        + ". Do not edit by hand; see [README.md](README.md).",
        "",
        "## Who is working on what",
        "",
    ]
    grouped = work_by_assignee(open_work)
    if not grouped:
        lines += ["_No open issues._", ""]
    for login, rows in grouped.items():
        who = login if login == "(unassigned)" else f"@{login}"
        lines += [f"### {who} ({len(rows)})", ""]
        lines += _table(["Issue", "Title", "Milestone"], rows, "none")
    lines += ["## Work sign-ups", ""]
    lines += _table(
        ["Member", "Sprint", "1st", "2nd", "3rd", "Hours", "Wants issues", "Issue"],
        signup_rows(signups),
        "No sign-ups yet. Use the Work sign-up form.",
    )
    lines += ["## Findings (issues labelled `finding`)", ""]
    lines += _table(
        ["Issue", "Finding", "Dataset", "Confidence", "By", "State"],
        finding_rows(findings),
        "No findings filed yet. Use the Research finding form.",
    )
    lines += ["## Decisions (issues labelled `decision`)", ""]
    lines += _table(
        ["Issue", "Decision", "Decide by", "State"],
        decision_rows(decisions),
        "No decision issues yet.",
    )
    return "\n".join(lines)

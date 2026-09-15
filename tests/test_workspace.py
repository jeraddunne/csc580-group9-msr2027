"""Tests for the team workspace digest (offline)."""

from __future__ import annotations

from datetime import UTC, datetime

from msr_pipeline.workspace import cell, parse_form_body, render_digest, work_by_assignee

SIGNUP_BODY = """### Member

Allie Hodges

### Sprint

Sprint 1

### Hours available this sprint

7 to 9

### First choice

W5 Validation and annotation

### Second choice

W7 Visualization and results tables

### Third choice

_No response_

### Specific issues you want

#14, #16
"""


def test_parse_form_body_handles_no_response_and_multiline():
    body = SIGNUP_BODY + "\n### Notes\n\nline one\nline two\n"
    fields = parse_form_body(body)
    assert fields["Member"] == "Allie Hodges"
    assert fields["Third choice"] == ""
    assert fields["Notes"] == "line one\nline two"
    assert parse_form_body(None) == {}
    assert parse_form_body("no headings at all") == {}


def test_cell_escapes_and_truncates():
    assert cell("a | b\nc") == "a \\| b c"
    assert cell("x" * 200, limit=10) == "xxxxxxx..."
    assert cell(None) == ""


def test_work_by_assignee_groups_and_puts_unassigned_last():
    issues = [
        {"number": 1, "title": "A", "assignees": [{"login": "zed"}], "milestone": None},
        {"number": 2, "title": "B", "assignees": [], "milestone": {"title": "Sprint 1"}},
        {"number": 3, "title": "C", "assignees": [{"login": "amy"}, {"login": "zed"}]},
    ]
    grouped = work_by_assignee(issues)
    assert list(grouped) == ["amy", "zed", "(unassigned)"]
    assert len(grouped["zed"]) == 2
    assert grouped["(unassigned)"][0][2] == "Sprint 1"


def test_render_digest_sections_and_empty_states():
    ts = datetime(2026, 9, 14, 12, 0, tzinfo=UTC)
    empty = render_digest([], [], [], [], generated_at=ts)
    assert "Generated 2026-09-14 12:00 UTC" in empty
    assert "sign-up process is retired" in empty and "No findings filed yet" in empty

    signup = {"number": 30, "title": "[Sign-up] Allie", "body": SIGNUP_BODY, "url": "u30"}
    finding = {
        "number": 31,
        "title": "[Finding] 56% of occurrences are copies",
        "body": "### Dataset\n\nGitSkills\n\n### Confidence\n\nMeasured by code",
        "author": {"login": "jeraddunne"},
        "state": "OPEN",
        "url": "u31",
    }
    decision = {
        "number": 32,
        "title": "[Decision] Use the sample only",
        "body": "### Decide by\n\n2026-09-24",
        "state": "CLOSED",
    }
    md = render_digest([signup], [finding], [decision], [], repo="o/r", generated_at=ts)
    assert "| Allie Hodges | Sprint 1 | W5 Validation and annotation |" in md
    assert "| [#31](u31) | 56% of occurrences are copies | GitSkills | Measured by code |" in md
    assert "| #32 | Use the sample only | 2026-09-24 | decided |" in md
    assert "from `o/r`" in md

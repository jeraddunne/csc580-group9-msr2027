#!/usr/bin/env python
"""Write docs/research/RULE_CATALOG.md, one rule card per rule, from the rule file.

The instructor asked for the rationale and a reference behind every detection rule, in the
style of SpotBugs and SonarSource rule pages: the problem, a bad example, and the source
(Sprint 1 feedback, issue #95). The cards are generated from rules/skill_risk_rules.yaml so
the page and the scanner cannot disagree; edit the rule file, then rerun this script.

Usage:
    python scripts/make_rule_catalog.py           # write the page
    python scripts/make_rule_catalog.py --check   # exit 1 if the page is out of date
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from msr_pipeline.skill_risk import HIGH_RISK_SEVERITY, read_rule_file  # noqa: E402

RULES = ROOT / "rules" / "skill_risk_rules.yaml"
OUT = ROOT / "docs" / "research" / "RULE_CATALOG.md"
KINDS = {
    "weakness": "CWE weakness",
    "technique": "MITRE ATT&CK technique",
    "guidance": "OWASP guidance",
    "tool-rule": "Rule in an established analyser",
    "platform": "Agent platform documentation",
    "paper": "Research paper",
}

INTRO = (
    "# Rule catalog: what each rule detects and where it comes from\n\n"
    "How to use: one card per rule in `rules/skill_risk_rules.yaml`, laid out like a "
    "SpotBugs or SonarSource rule page: the problem, the bad pattern, what is not "
    "flagged, known false positives, and the established sources the rule corresponds to. "
    "**This page is generated**; edit the rule file and run `python "
    "scripts/make_rule_catalog.py`. The instructor asked for it in the Sprint 1 feedback "
    "(`docs/sprints/sprint-2/instructor-feedback.md`, F3; issue #95).\n\n"
    "**Where the rules come from.** The rules were written from the capability categories "
    "in `docs/research/THREAT_MODEL.md` section 5: each pattern is a literal form of a "
    "capability, such as the command, file path, or front-matter field a skill would "
    "contain. Eighteen rules have `source: expert`; R-OVR-001 has `source: literature` "
    "(Greshake et al. 2023). The references below were added in Sprint 2, after the rules "
    "were written, to show which documented weakness, attack technique, or analyser rule "
    "each pattern corresponds to. They did not shape the patterns, and a reference does "
    "not turn a match into a vulnerability: a match is a signal for a reviewer "
    "(`THREAT_MODEL.md` section 6, `docs/research/REVIEW_WORKFLOW.md`). Every reference "
    "was checked against its source page on 2026-10-22. Where no established source "
    "covers part of a rule, the card says so.\n\n"
    "**Kinds of reference.** CWE entries name a weakness in code. MITRE ATT&CK techniques "
    "name what an attacker does on a host. OWASP Top 10 for LLM Applications (2025) "
    "entries name risks specific to LLM applications, which is where most skill-specific "
    "rules belong. Analyser rules (Bandit, ShellCheck, Find Security Bugs for SpotBugs) "
    "are the nearest existing static checks; which of those tools can run on skills at "
    "all is the subject of `docs/research/APPLICABILITY.md` (#96).\n\n"
    "**Severity.** 1 to 10, the FMEA severity score; the scale and the reason for each "
    "category's top severity are in `THREAT_MODEL.md` section 5. A rule with severity "
    "{high} or more makes a skill high risk, which is what the review workflow shows a "
    "reviewer.\n"
)


def _fence(text: str) -> str:
    """A fenced block that survives backticks inside the example."""
    ticks = "````" if "```" in text else "```"
    return f"{ticks}text\n{text}\n{ticks}"


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def card(rule: dict, categories: dict, high: int) -> str:
    rid, cat, sev = rule["id"], rule["category"], int(rule["severity"])
    examples = rule.get("examples") or {}
    lines = [
        f"## {rid}: {rule.get('title', '')}",
        "",
        "| Category | Severity | High risk | Source | Status |",
        "|---|---|---|---|---|",
        f"| {cat}: {_cell(str(categories.get(cat, '')))} | {sev} | "
        f"{'yes' if sev >= high else 'no (context)'} | {rule.get('source', 'expert')} | "
        f"{rule.get('status', 'active')} |",
        "",
        f"**Problem.** {rule.get('description', '')}",
        "",
        "**Flagged (bad pattern)**",
        "",
    ]
    for text in examples.get("match") or []:
        lines += [_fence(str(text)), ""]
    if examples.get("no_match"):
        lines += ["**Not flagged**", ""]
        for text in examples["no_match"]:
            lines += [_fence(str(text)), ""]
    lines += [f"**Notes and known false positives.** {rule.get('note', '')}", ""]
    if rule.get("reference_gaps"):
        lines += [f"**Not covered by a reference.** {rule['reference_gaps']}", ""]
    lines += ["**References**", ""]
    for ref in rule.get("references") or []:
        line = (
            f"- [{ref['id']}: {ref['title']}]({ref['url']}) "
            f"({KINDS.get(ref['kind'], ref['kind'])}). {ref['relation']}."
        )
        if ref.get("note"):
            line += f" {ref['note']}."
        lines.append(line)
    lines += ["", "<details><summary>Patterns</summary>", ""]
    flags = "case-sensitive" if rule.get("case_sensitive") else "case-insensitive"
    lines += [f"Regular expressions, {flags}, multiline:", ""]
    lines += [_fence("\n".join(str(p) for p in rule["patterns"])), "", "</details>", ""]
    return "\n".join(lines)


def render(data: dict) -> str:
    high = int(data.get("high_risk_severity", HIGH_RISK_SEVERITY))
    categories = data.get("categories") or {}
    rules = [r for r in data.get("rules") or [] if str(r.get("status", "active")) == "active"]
    index = [
        "| Rule | Title | Category | Severity | References |",
        "|---|---|---|---|---|",
    ]
    for r in rules:
        anchor = f"{r['id'].lower()}-{r.get('title', '')}"
        anchor = "".join(c if c.isalnum() or c == "-" else "" for c in anchor.replace(" ", "-"))
        refs = ", ".join(x["id"] for x in r.get("references") or [])
        index.append(
            f"| [{r['id']}](#{anchor.lower()}) | {_cell(r.get('title', ''))} | {r['category']} | "
            f"{r['severity']} | {_cell(refs)} |"
        )
    parts = [INTRO.replace("{high}", str(high)), "## Index", "", *index, ""]
    parts += [card(r, categories, high) for r in rules]
    return "\n".join(parts).rstrip("\n") + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="Exit 1 if the page is out of date.")
    args = parser.parse_args(argv)
    text = render(read_rule_file(RULES))
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current.replace("\r\n", "\n") != text:
            print(f"{OUT.relative_to(ROOT)} is out of date; run scripts/make_rule_catalog.py")
            return 1
        print(f"{OUT.relative_to(ROOT)} is up to date")
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

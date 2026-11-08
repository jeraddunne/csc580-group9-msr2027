"""skill-scan: check one agent skill for risk signals before a person reviews it (#150).

This is the final artifact of proposal P-01. It runs steps 2 to 4 of the human-in-the-loop
review workflow (``docs/research/REVIEW_WORKFLOW.md``) on a skill folder: it reads SKILL.md and
the bundled scripts with the validated rule file (``rules/skill_risk_rules.yaml``), lists every
match with its rule, category, severity, file and line, and gives the skill one outcome:

* ``high_risk``: at least one match at or above the cutoff (severity 6, the threat model's
  "high risk"). A security reviewer labels each finding RISKY, BENIGN_CONTEXT or NOT_PRESENT
  (step 5).
* ``no_high_risk_signal``: nothing at or above the cutoff. Matches below it are listed as
  context. This is not a statement that the skill is safe; the reviewer still approves (step 4).
* ``incomplete``: a bundled script could not be read as text, so the skill never takes the
  no-signal path; the reviewer resolves the gap or reads the file by hand (step 3).

A rule match is a signal, not a verdict. Nothing scanned is executed, imported or fetched.

Usage::

    skill-scan path/to/skill-folder [more paths] [--format text|markdown|json|sarif]
    msr-pipeline scan path/to/skill-folder        # the same command
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from . import __version__
from .config import repo_root
from .skill_risk import (
    DEFAULT_RULES_PATH,
    HIGH_RISK_SEVERITY,
    SCRIPT_EXTENSIONS,
    Rule,
    is_symlink_stub,
    read_rule_file,
    rules_from_dict,
)

TOOL_NAME = "skill-scan"
SCHEMA_VERSION = 1
REPO_URL = "https://github.com/jeraddunne/csc580-group9-msr2027"
RULE_CATALOG_URL = f"{REPO_URL}/blob/main/docs/research/RULE_CATALOG.md"
SKILL_FILE_NAMES = frozenset({"skill.md"})
SKIP_DIRS = frozenset({".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__"})
MAX_FILE_BYTES = 1_000_000
FORMATS = ("text", "markdown", "json", "sarif")
FAIL_ON = ("never", "high-risk", "incomplete", "any")

HIGH_RISK = "high_risk"
NO_SIGNAL = "no_high_risk_signal"
INCOMPLETE = "incomplete"
OUTCOME_LABEL = {
    HIGH_RISK: "High-risk signal",
    NO_SIGNAL: "No high-risk signal",
    INCOMPLETE: "Incomplete scan",
}
NEXT_STEP = {
    HIGH_RISK: (
        "A security reviewer labels each high-risk finding RISKY, BENIGN_CONTEXT or NOT_PRESENT "
        "(review workflow step 5), then approves, asks for a change, or blocks (steps 6 and 7)."
    ),
    NO_SIGNAL: (
        "No match at or above the cutoff. This is not a statement that the skill is safe: "
        "a reviewer still approves the change (review workflow step 4)."
    ),
    INCOMPLETE: (
        "Some files could not be scanned, so this skill does not take the no-signal path. "
        "Fix the files so they can be rescanned, or read them by hand, then triage any findings "
        "(review workflow step 3)."
    ),
}


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RuleInfo:
    """What a reviewer needs to know about a rule, from the rule file."""

    id: str
    title: str
    category: str
    category_description: str
    severity: int
    description: str
    note: str
    references: tuple[str, ...]


@dataclass(frozen=True)
class RuleSet:
    path: Path
    sha256: str
    cutoff: int
    rules: tuple[Rule, ...]
    info: dict[str, RuleInfo]


@dataclass(frozen=True)
class Finding:
    rule_id: str
    title: str
    category: str
    severity: int
    high_risk: bool
    path: str
    line: int
    column: int
    end_line: int
    end_column: int
    match: str
    line_text: str


@dataclass
class SkillReport:
    """One scanned unit: a skill folder (with SKILL.md) or a single file outside any skill."""

    path: str
    kind: str  # "skill" or "file"
    skill_file: str | None = None
    skill_sha256: str | None = None
    folder_sha256: str | None = None
    files_scanned: list[str] = field(default_factory=list)
    unreadable: list[dict] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    @property
    def high_risk_findings(self) -> list[Finding]:
        return [f for f in self.findings if f.high_risk]

    @property
    def context_findings(self) -> list[Finding]:
        return [f for f in self.findings if not f.high_risk]

    @property
    def outcome(self) -> str:
        if self.unreadable:
            return INCOMPLETE
        return HIGH_RISK if self.high_risk_findings else NO_SIGNAL


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------


def default_rules_path() -> Path:
    env = os.environ.get("SKILL_SCAN_RULES")
    return Path(env) if env else repo_root() / DEFAULT_RULES_PATH


def load_ruleset(path: Path | str | None = None, cutoff: int | None = None) -> RuleSet:
    path = Path(path) if path else default_rules_path()
    if not path.is_file():
        raise FileNotFoundError(
            f"rule file not found: {path}. Pass --rules or set SKILL_SCAN_RULES "
            "to rules/skill_risk_rules.yaml from the repository."
        )
    raw_bytes = path.read_bytes()
    data = read_rule_file(path)
    rules = tuple(rules_from_dict(data))
    categories = data.get("categories") or {}
    info = {}
    for raw in data.get("rules") or []:
        rid = str(raw["id"])
        info[rid] = RuleInfo(
            id=rid,
            title=str(raw.get("title") or rid),
            category=str(raw["category"]),
            category_description=str(categories.get(raw["category"], "")),
            severity=int(raw["severity"]),
            description=" ".join(str(raw.get("description") or "").split()),
            note=" ".join(str(raw.get("note") or "").split()),
            references=tuple(str(r.get("id")) for r in raw.get("references") or [] if r.get("id")),
        )
    if cutoff is None:
        cutoff = int(data.get("high_risk_severity", HIGH_RISK_SEVERITY))
    return RuleSet(
        path=path,
        sha256=hashlib.sha256(raw_bytes).hexdigest(),
        cutoff=cutoff,
        rules=rules,
        info=info,
    )


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------


def _position(text: str, offset: int) -> tuple[int, int]:
    """1-based line and column of a character offset."""
    line = text.count("\n", 0, offset) + 1
    column = offset - (text.rfind("\n", 0, offset) + 1) + 1
    return line, column


def _clip(value: str, limit: int) -> str:
    value = value.replace("\r", "").replace("\n", " ").replace("\t", " ").strip()
    return value if len(value) <= limit else value[: limit - 3] + "..."


def scan_text(text: str, path: str, ruleset: RuleSet) -> list[Finding]:
    """Every rule match in ``text``, one finding per rule and line."""
    lines = text.splitlines()
    findings: list[Finding] = []
    seen: set[tuple[str, int]] = set()
    for rule in ruleset.rules:
        info = ruleset.info.get(rule.id)
        for pattern in rule.patterns:
            for m in pattern.finditer(text):
                matched = m.group(0)
                start = m.start() + (len(matched) - len(matched.lstrip("\r\n")))
                line, column = _position(text, start)
                if (rule.id, line) in seen:
                    continue
                seen.add((rule.id, line))
                end_line, end_column = _position(text, max(m.end(), m.start() + 1))
                findings.append(
                    Finding(
                        rule_id=rule.id,
                        title=info.title if info else rule.id,
                        category=rule.category,
                        severity=rule.severity,
                        high_risk=rule.severity >= ruleset.cutoff,
                        path=path,
                        line=line,
                        column=column,
                        end_line=end_line,
                        end_column=end_column,
                        match=_clip(matched, 120),
                        line_text=_clip(lines[line - 1] if line <= len(lines) else "", 200),
                    )
                )
    findings.sort(key=lambda f: (f.path, f.line, -f.severity, f.rule_id))
    return findings


def _display(path: Path) -> str:
    """Path relative to the working directory when possible, with forward slashes."""
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix() or "."
    except ValueError:
        return path.resolve().as_posix()


def _is_skill_file(path: Path) -> bool:
    return path.name.lower() in SKILL_FILE_NAMES


def _skill_file_in(folder: Path) -> Path | None:
    try:
        for child in sorted(folder.iterdir()):
            if child.is_file() and _is_skill_file(child):
                return child
    except OSError:
        return None
    return None


def _read(path: Path, root: Path) -> tuple[str | None, str | None]:
    """Text of a file, or (None, reason) when it cannot be scanned as text."""
    try:
        if path.is_symlink():
            target = path.resolve()
            if not target.exists():
                return None, "broken symbolic link"
            if root not in target.parents and target != root:
                return None, "symbolic link to a file outside the skill folder (not followed)"
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            return None, f"larger than {MAX_FILE_BYTES // 1_000_000} MB ({size:,} bytes)"
        data = path.read_bytes()
    except OSError as exc:
        return None, f"could not be read ({exc.strerror or exc})"
    if b"\x00" in data:
        return None, "binary content, not text"
    return data.decode("utf-8", errors="replace"), None


def _bundled_files(folder: Path) -> list[Path]:
    """Scripts under a skill folder, skipping nested skills and tool folders."""
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(folder):
        current = Path(dirpath)
        keep = []
        for name in sorted(dirnames):
            sub = current / name
            if name in SKIP_DIRS or _skill_file_in(sub) is not None:
                continue
            keep.append(name)
        dirnames[:] = keep
        for name in sorted(filenames):
            candidate = current / name
            if candidate.suffix.lower() in SCRIPT_EXTENSIONS:
                out.append(candidate)
    return out


def _folder_hash(entries: list[tuple[str, bytes]]) -> str:
    digest = hashlib.sha256()
    for rel, data in sorted(entries):
        digest.update(rel.encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(data).hexdigest().encode())
        digest.update(b"\n")
    return digest.hexdigest()


def scan_skill(folder: Path, ruleset: RuleSet) -> SkillReport:
    folder = folder.resolve()
    skill_file = _skill_file_in(folder)
    report = SkillReport(path=_display(folder), kind="skill")
    entries: list[tuple[str, bytes]] = []
    files = ([skill_file] if skill_file else []) + _bundled_files(folder)
    for file in files:
        rel = file.relative_to(folder).as_posix()
        text, reason = _read(file, folder)
        if text is None:
            report.unreadable.append({"path": _display(file), "reason": reason})
            continue
        entries.append((rel, text.encode("utf-8")))
        report.files_scanned.append(_display(file))
        if file == skill_file:
            report.skill_file = _display(file)
            report.skill_sha256 = hashlib.sha256(file.read_bytes()).hexdigest()
            if is_symlink_stub(text):
                report.unreadable.append(
                    {
                        "path": _display(file),
                        "reason": "SKILL.md holds a single path, not instructions "
                        "(a symlink stub); scan the target instead",
                    }
                )
                continue
        report.findings.extend(scan_text(text, _display(file), ruleset))
    report.folder_sha256 = _folder_hash(entries) if entries else None
    report.findings.sort(key=lambda f: (f.path, f.line, -f.severity, f.rule_id))
    return report


def scan_single_file(path: Path, ruleset: RuleSet) -> SkillReport:
    path = path.resolve()
    report = SkillReport(path=_display(path), kind="file")
    text, reason = _read(path, path.parent)
    if text is None:
        report.unreadable.append({"path": _display(path), "reason": reason})
        return report
    report.files_scanned.append(_display(path))
    report.skill_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    report.findings = scan_text(text, _display(path), ruleset)
    return report


def _enclosing_skill(path: Path, stop: Path | None) -> Path | None:
    """The nearest folder at or above ``path`` that holds a SKILL.md, not going above ``stop``."""
    folder = path if path.is_dir() else path.parent
    folder = folder.resolve()
    if stop is None:
        # Outside the working folder: look only at the folder itself, never above it.
        return folder if _skill_file_in(folder) is not None else None
    stop = stop.resolve()
    while True:
        if _skill_file_in(folder) is not None:
            return folder
        if folder.parent == folder or (stop is not None and folder == stop):
            return None
        folder = folder.parent


def discover(paths: Iterable[str | Path], skills_only: bool = False) -> list[tuple[str, Path]]:
    """Units to scan: ("skill", folder) or ("file", path), each once, in a stable order."""
    units: dict[Path, str] = {}
    cwd = Path.cwd().resolve()
    for raw in paths:
        p = Path(raw)
        if not p.exists():
            raise FileNotFoundError(f"no such file or folder: {raw}")
        if p.is_dir():
            found = False
            enclosing = _enclosing_skill(p, cwd if cwd in p.resolve().parents else None)
            if enclosing is not None:
                units.setdefault(enclosing, "skill")
                found = True
            for dirpath, dirnames, filenames in os.walk(p):
                dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
                if any(n.lower() in SKILL_FILE_NAMES for n in filenames):
                    units.setdefault(Path(dirpath).resolve(), "skill")
                    found = True
            if not found and not skills_only:
                for file in _bundled_files(p):
                    units.setdefault(file.resolve(), "file")
            continue
        stop = cwd if cwd in p.resolve().parents else None
        enclosing = _enclosing_skill(p, stop)
        if enclosing is not None:
            units.setdefault(enclosing, "skill")
        elif not skills_only:
            units.setdefault(p.resolve(), "file")
    return [(kind, path) for path, kind in sorted(units.items(), key=lambda kv: str(kv[0]))]


def scan(paths: Iterable[str | Path], ruleset: RuleSet, skills_only: bool = False):
    reports = []
    for kind, path in discover(paths, skills_only=skills_only):
        reports.append(
            scan_skill(path, ruleset) if kind == "skill" else scan_single_file(path, ruleset)
        )
    return reports


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def summary(reports: Sequence[SkillReport]) -> dict:
    counts = {HIGH_RISK: 0, NO_SIGNAL: 0, INCOMPLETE: 0}
    for r in reports:
        counts[r.outcome] += 1
    return {
        "units": len(reports),
        "high_risk": counts[HIGH_RISK],
        "no_high_risk_signal": counts[NO_SIGNAL],
        "incomplete": counts[INCOMPLETE],
        "high_risk_findings": sum(len(r.high_risk_findings) for r in reports),
        "context_matches": sum(len(r.context_findings) for r in reports),
        "with_high_risk_findings": sum(1 for r in reports if r.high_risk_findings),
    }


def _finding_dict(f: Finding, ruleset: RuleSet) -> dict:
    info = ruleset.info.get(f.rule_id)
    return {
        "rule_id": f.rule_id,
        "title": f.title,
        "category": f.category,
        "category_description": info.category_description if info else "",
        "severity": f.severity,
        "high_risk": f.high_risk,
        "path": f.path,
        "line": f.line,
        "column": f.column,
        "end_line": f.end_line,
        "end_column": f.end_column,
        "match": f.match,
        "line_text": f.line_text,
        "guidance": info.description if info else "",
        "references": list(info.references) if info else [],
    }


def to_json(reports: Sequence[SkillReport], ruleset: RuleSet) -> dict:
    return {
        "tool": TOOL_NAME,
        "version": __version__,
        "schema_version": SCHEMA_VERSION,
        "rules": {
            "path": _display(ruleset.path),
            "sha256": ruleset.sha256,
            "count": len(ruleset.rules),
            "cutoff": ruleset.cutoff,
        },
        "summary": summary(reports),
        "units": [
            {
                "path": r.path,
                "kind": r.kind,
                "outcome": r.outcome,
                "outcome_label": OUTCOME_LABEL[r.outcome],
                "next_step": NEXT_STEP[r.outcome],
                "skill_file": r.skill_file,
                "skill_sha256": r.skill_sha256,
                "folder_sha256": r.folder_sha256,
                "files_scanned": r.files_scanned,
                "unreadable": r.unreadable,
                "high_risk_findings": [_finding_dict(f, ruleset) for f in r.high_risk_findings],
                "context_matches": [_finding_dict(f, ruleset) for f in r.context_findings],
            }
            for r in reports
        ],
    }


def _header(ruleset: RuleSet) -> str:
    return (
        f"{TOOL_NAME} {__version__} | rules {_display(ruleset.path)} "
        f"({len(ruleset.rules)} rules, sha256 {ruleset.sha256[:12]}) | "
        f"high-risk cutoff: severity {ruleset.cutoff}"
    )


def to_text(reports: Sequence[SkillReport], ruleset: RuleSet, show_context: bool = True) -> str:
    out = [_header(ruleset), ""]
    if not reports:
        out.append("No skill folders or files to scan.")
    for r in reports:
        label = OUTCOME_LABEL[r.outcome].upper()
        extra = ""
        if r.high_risk_findings:
            n = len(r.high_risk_findings)
            extra = f": {n} finding{'s' if n != 1 else ''} to triage"
        out.append(f"{r.path}  [{label}{extra}]")
        for u in r.unreadable:
            out.append(f"  not scanned: {u['path']} ({u['reason']})")
        for f in r.high_risk_findings:
            out.append(
                f"  {f.path}:{f.line}:{f.column}  {f.rule_id}  {f.category}  "
                f"severity {f.severity}  {f.title}"
            )
            out.append(f"      {f.line_text}")
        if show_context and r.context_findings:
            out.append(f"  context (below severity {ruleset.cutoff}, not findings to triage):")
            for f in r.context_findings:
                out.append(
                    f"    {f.path}:{f.line}  {f.rule_id}  {f.category}  severity {f.severity}  "
                    f"{f.title}"
                )
        out.append(f"  next: {NEXT_STEP[r.outcome]}")
        out.append("")
    s = summary(reports)
    out.append(
        f"Summary: {s['units']} scanned: {s['high_risk']} high-risk, "
        f"{s['no_high_risk_signal']} no high-risk signal, {s['incomplete']} incomplete; "
        f"{s['high_risk_findings']} high-risk findings, {s['context_matches']} context matches."
    )
    out.append("A rule match is a signal, not a verdict.")
    return "\n".join(out) + "\n"


def _cell(value: object) -> str:
    text = str(value).replace("|", "\\|").replace("`", "'")
    return text.replace("\n", " ")


def to_markdown(reports: Sequence[SkillReport], ruleset: RuleSet, show_context: bool = True) -> str:
    s = summary(reports)
    out = [
        "## Skill scan",
        "",
        f"`{TOOL_NAME}` {__version__}, rule file `{_display(ruleset.path)}` "
        f"({len(ruleset.rules)} rules, sha256 `{ruleset.sha256[:12]}`), "
        f"high-risk cutoff severity {ruleset.cutoff}. A rule match is a signal, not a verdict: "
        "a person decides (see the "
        f"[review workflow]({REPO_URL}/blob/main/docs/research/REVIEW_WORKFLOW.md)).",
        "",
        f"**{s['units']} scanned:** {s['high_risk']} high-risk, "
        f"{s['no_high_risk_signal']} no high-risk signal, {s['incomplete']} incomplete.",
        "",
    ]
    if not reports:
        out.append("No skill folders or files to scan.")
        return "\n".join(out) + "\n"
    out += [
        "| Skill | Outcome | High-risk findings | Context matches | Files scanned |",
        "|---|---|---|---|---|",
    ]
    for r in reports:
        out.append(
            f"| `{_cell(r.path)}` | {OUTCOME_LABEL[r.outcome]} | {len(r.high_risk_findings)} "
            f"| {len(r.context_findings)} | {len(r.files_scanned)} |"
        )
    out.append("")
    used: dict[str, RuleInfo] = {}
    for r in reports:
        out.append(f"### `{_cell(r.path)}`: {OUTCOME_LABEL[r.outcome]}")
        out.append("")
        if r.skill_sha256:
            version = f"Skill version: `{r.skill_file or r.path}` sha256 `{r.skill_sha256[:16]}`"
            if r.folder_sha256 and r.kind == "skill":
                version += f", folder sha256 `{r.folder_sha256[:16]}`"
            out += [version + ".", ""]
        if r.unreadable:
            out.append("Not scanned:")
            out.append("")
            out += [f"- `{_cell(u['path'])}`: {u['reason']}" for u in r.unreadable]
            out.append("")
        if r.high_risk_findings:
            out += [
                "| # | Location | Rule | Category | Severity | Line | "
                "Label (RISKY / BENIGN_CONTEXT / NOT_PRESENT) |",
                "|---|---|---|---|---|---|---|",
            ]
            for i, f in enumerate(r.high_risk_findings, start=1):
                used[f.rule_id] = ruleset.info.get(f.rule_id) or used.get(f.rule_id)
                out.append(
                    f"| {i} | `{_cell(f.path)}:{f.line}` | {f.rule_id} {_cell(f.title)} "
                    f"| {f.category} | {f.severity} | `{_cell(f.line_text)}` | |"
                )
            out.append("")
        if show_context and r.context_findings:
            out += [
                "<details><summary>Context matches below severity "
                f"{ruleset.cutoff} ({len(r.context_findings)}), not findings to triage</summary>",
                "",
                "| Location | Rule | Category | Severity | Line |",
                "|---|---|---|---|---|",
            ]
            for f in r.context_findings:
                out.append(
                    f"| `{_cell(f.path)}:{f.line}` | {f.rule_id} {_cell(f.title)} | {f.category} "
                    f"| {f.severity} | `{_cell(f.line_text)}` |"
                )
            out += ["", "</details>", ""]
        out += [f"**Next:** {NEXT_STEP[r.outcome]}", ""]
        if r.outcome != INCOMPLETE:
            out += [
                "**Review record (step 7):** reviewer: ____; decision: approve / request a change "
                "/ block; reason: ____",
                "",
            ]
    used = {k: v for k, v in used.items() if v}
    if used:
        out += ["<details><summary>What each high-risk rule looks for</summary>", ""]
        for rid in sorted(used):
            info = used[rid]
            out.append(f"- **{rid} {info.title}** ({info.category}, severity {info.severity}). ")
            out[-1] += info.description
        out += ["", f"Full rule pages: [rule catalog]({RULE_CATALOG_URL}).", "", "</details>", ""]
    return "\n".join(out) + "\n"


def to_sarif(reports: Sequence[SkillReport], ruleset: RuleSet) -> dict:
    rules = []
    index = {}
    for rid, info in sorted(ruleset.info.items()):
        if rid not in {r.id for r in ruleset.rules}:
            continue
        index[rid] = len(rules)
        rules.append(
            {
                "id": rid,
                "name": "".join(w.capitalize() for w in info.title.replace("-", " ").split()),
                "shortDescription": {"text": info.title},
                "fullDescription": {"text": info.description or info.title},
                "help": {"text": " ".join(x for x in (info.description, info.note) if x)},
                "helpUri": RULE_CATALOG_URL,
                # No "security-severity": GitHub would rate a severity-9 rule "critical" and
                # fail the pull request's code-scanning check. The scan reports and a person
                # decides, so findings upload as warnings (high-risk) and notes (context).
                "properties": {
                    "category": info.category,
                    "severity": info.severity,
                    "tags": ["skill-risk", info.category.lower()],
                },
            }
        )
    results = []
    for r in reports:
        for f in r.findings:
            fingerprint = hashlib.sha256(f"{f.rule_id}|{f.path}|{f.line_text}".encode()).hexdigest()
            results.append(
                {
                    "ruleId": f.rule_id,
                    "ruleIndex": index.get(f.rule_id, 0),
                    "level": "warning" if f.high_risk else "note",
                    "message": {
                        "text": (
                            f"{f.title} ({f.category}, severity {f.severity}). "
                            + (
                                "High-risk signal: a reviewer labels it RISKY, BENIGN_CONTEXT or "
                                "NOT_PRESENT."
                                if f.high_risk
                                else f"Context match below severity {ruleset.cutoff}."
                            )
                        )
                    },
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": f.path},
                                "region": {
                                    "startLine": f.line,
                                    "startColumn": f.column,
                                    "endLine": f.end_line,
                                    "endColumn": f.end_column,
                                },
                            }
                        }
                    ],
                    "partialFingerprints": {"skillScan/v1": fingerprint},
                }
            )
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": TOOL_NAME,
                        "version": __version__,
                        "informationUri": REPO_URL,
                        "rules": rules,
                    }
                },
                "results": results,
            }
        ],
    }


def render(fmt: str, reports, ruleset: RuleSet, show_context: bool = True) -> str:
    if fmt == "text":
        return to_text(reports, ruleset, show_context)
    if fmt == "markdown":
        return to_markdown(reports, ruleset, show_context)
    if fmt == "json":
        return json.dumps(to_json(reports, ruleset), indent=2) + "\n"
    if fmt == "sarif":
        return json.dumps(to_sarif(reports, ruleset), indent=2) + "\n"
    raise ValueError(f"unknown format {fmt}")


def should_fail(reports: Sequence[SkillReport], fail_on: str) -> bool:
    high = any(r.high_risk_findings for r in reports)
    incomplete = any(r.outcome == INCOMPLETE for r in reports)
    return {
        "never": False,
        "high-risk": high,
        "incomplete": incomplete,
        "any": high or incomplete,
    }[fail_on]


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog=TOOL_NAME,
        description=(
            "Scan agent skills (SKILL.md and bundled scripts) for risk signals and report them "
            "for human review. A rule match is a signal, not a verdict."
        ),
    )
    p.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Skill folders, SKILL.md files, bundled scripts, or folders holding skills "
        "(default: the current folder).",
    )
    p.add_argument(
        "--format", choices=FORMATS, default="text", help="Output format (default text)."
    )
    p.add_argument("--output", "-o", default=None, help="Write the report here instead of stdout.")
    p.add_argument(
        "--write",
        action="append",
        default=[],
        metavar="FORMAT:PATH",
        help="Also write another format to a file, for example markdown:report.md. Repeatable.",
    )
    p.add_argument("--rules", default=None, help="Rule file (default rules/skill_risk_rules.yaml).")
    p.add_argument(
        "--cutoff",
        type=int,
        default=None,
        help="High-risk severity cutoff (default from the rule file: 6).",
    )
    p.add_argument(
        "--fail-on",
        choices=FAIL_ON,
        default="never",
        help="Exit with status 1 when this happens (default never: the scan reports, a person "
        "decides).",
    )
    p.add_argument(
        "--skills-only",
        action="store_true",
        help="Ignore files that are not inside a skill folder (used by the GitHub Action).",
    )
    p.add_argument("--no-context", action="store_true", help="Leave context matches out.")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def _write(path: str, text: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(text, encoding="utf-8", newline="\n")


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    extra = []
    for spec in args.write:
        fmt, sep, path = spec.partition(":")
        if not sep or fmt not in FORMATS or not path:
            print(
                f"{TOOL_NAME}: --write expects FORMAT:PATH with FORMAT in {FORMATS}",
                file=sys.stderr,
            )
            return 2
        extra.append((fmt, path))
    try:
        ruleset = load_ruleset(args.rules, args.cutoff)
        reports = scan(args.paths, ruleset, skills_only=args.skills_only)
    except (FileNotFoundError, ValueError) as exc:
        print(f"{TOOL_NAME}: {exc}", file=sys.stderr)
        return 2
    show_context = not args.no_context
    text = render(args.format, reports, ruleset, show_context)
    if args.output:
        _write(args.output, text)
    else:
        sys.stdout.write(text)
    for fmt, path in extra:
        _write(path, render(fmt, reports, ruleset, show_context))
    return 1 if should_fail(reports, args.fail_on) else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

#!/usr/bin/env python
"""Build the source pack for the Group 9 elicitation notebook.

The notebook (`notebooks/01_elicitation_notebook.ipynb`, backed by
`msr_pipeline.elicitation`) is a bounded domain-information source for
requirements elicitation (assignment Phase B). It answers only from this pack.
The pack has three tiers of sources, and the tier sets what a source may be
used for:

- A, authoritative: the nine sources the assignment names, fetched at pinned
  versions. They are the only authority for facts about GitSkills and SpecMine.
- G, group: this repository's own documents, bundled into topic files at the
  current commit. They are the authority for what Group 9 decided and how it works.
- P, practitioner (optional): a member's personal build method, bundled from
  --practice-dir. It is used only for process questions, never for dataset facts.

Every source is written as Markdown, which the notebook indexes. Each preprint is
also kept as the original PDF, and its Markdown copy marks every page ("## Page 3")
so answers can cite pages. The script writes SOURCES_MANIFEST.json (size, SHA-256,
origin, and version of every file) and SOURCE_REGISTER.md into --record-dir, so
the interview record names the exact source an answer came from. Nothing
downloaded is executed.

Usage:
    python scripts/build_notebook_sources.py
    python scripts/build_notebook_sources.py --practice-dir "../CSC-580 Project"
    python scripts/build_notebook_sources.py --out ~/notebook-pack --skip-fetch
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "build" / "notebook_sources"
DEFAULT_RECORD = ROOT / "elicitation" / "notebook"
TIMEOUT = 60

# Pinned versions, checked on 2026-09-18. Update deliberately, never to "latest":
# the interview record cites these exact versions.
MSR_URL = "https://2027.msrconf.org/track/msr-2027-mining-challenge"
ARXIV = {"A2": ("2608.10906", "v3"), "A3": ("2608.25202", "v3")}
ZENODO = {"A4": "21875637", "A5": "22102780"}  # A5 is the version record behind 22102779
HF = {
    "A6": ("mvaccargiu/gitskills", "ebab17454a7c236f8f26b183567f1a126f42e3f8"),
    "A7": ("ShyAgarwal/specmine", "ca682c69725fd476cd8a44bf39f1a4ba6969e67c"),
}
SPECMINE_GH = ("shyamagarwal13/specmine-official", "9fbb61541046cb2fb770fa944192a3fc0b64a9b1")
GITSKILLS_GH = ("giuseppedestefanis/gitskills-sample", "fff3df93beeee51a5444450891751f143e38da3e")


@dataclass
class Source:
    """One notebook source. ``file`` is the Markdown the notebook indexes; ``original``
    is the untouched download when that differs (the preprint PDFs)."""

    id: str
    tier: str
    priority: int
    title: str
    file: str
    role: str
    origin: list[str] = field(default_factory=list)
    version: dict = field(default_factory=dict)
    status: str = "pending"
    original: str | None = None


# ---------------------------------------------------------------------------
# Text conversion helpers (pure; unit-tested)
# ---------------------------------------------------------------------------


class _TextExtractor(HTMLParser):
    SKIP = {"script", "style", "nav", "footer", "noscript"}
    BLOCK = {"p", "br", "li", "tr", "div", "section", "article", "table"}

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in self.SKIP:
            self._skip += 1
        elif tag in {"h1", "h2", "h3", "h4", "h5"}:
            self.parts.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "li":
            self.parts.append("\n- ")
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP and self._skip:
            self._skip -= 1
        elif tag in {"h1", "h2", "h3", "h4", "h5"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self.parts.append(data)


def html_to_text(raw: str) -> str:
    """Readable text from HTML: headings become Markdown, scripts and navigation are dropped."""
    parser = _TextExtractor()
    parser.feed(raw)
    lines = [line.rstrip() for line in "".join(parser.parts).splitlines()]
    text = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


def slice_between(text: str, start: str, end: str | None) -> str:
    """The part of ``text`` from the first ``start`` up to (not including) ``end``."""
    i = text.find(start)
    if i < 0:
        return text
    j = text.find(end, i) if end else -1
    return text[i:j].rstrip() + "\n" if j > 0 else text[i:]


def notebook_to_markdown(nb: dict) -> str:
    """Render a Jupyter notebook's cells as Markdown with fenced code. Outputs are dropped."""
    out: list[str] = []
    for cell in nb.get("cells", []):
        body = "".join(cell.get("source", []))
        if cell.get("cell_type") == "code":
            out.append(f"```python\n{body.rstrip()}\n```")
        else:
            out.append(body.rstrip())
    return "\n\n".join(out) + "\n"


def zenodo_to_markdown(record: dict) -> str:
    """Summarise a Zenodo record: identity, version, license, files, and description."""
    meta = record.get("metadata", {})
    creators = "; ".join(c.get("name", "") for c in meta.get("creators", []))
    lines = [
        f"- Title: {meta.get('title', '')}",
        f"- Record id: {record.get('id')}",
        f"- Version DOI: {record.get('doi')}",
        f"- Concept DOI (resolves to the latest version): {record.get('conceptdoi')}",
        f"- Version: {meta.get('version')}",
        f"- Publication date: {meta.get('publication_date')}",
        f"- License: {(meta.get('license') or {}).get('id')}",
        f"- Creators: {creators}",
        "",
        "## Files",
        "",
        "| File | Bytes |",
        "|---|---:|",
    ]
    for f in record.get("files", []):
        lines.append(f"| {f.get('key')} | {f.get('size'):,} |")
    description = html_to_text(meta.get("description", "") or "")
    lines += ["", "## Description (from the record)", "", description]
    return "\n".join(lines)


def pdf_to_markdown(data: bytes) -> str:
    """Text of every PDF page under a "## Page N" heading, so passages carry a page."""
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    pages = []
    for i, page in enumerate(reader.pages, 1):
        # A "#" line in a PDF is content (the GitSkills preprint reproduces a SKILL.md in
        # Figure 2), not a heading; escape it so the page stays the passage locator.
        lines = [
            ("\\" + ln if ln.lstrip().startswith("#") else ln)
            for ln in (page.extract_text() or "").strip().splitlines()
        ]
        pages.append(f"## Page {i}\n\n" + "\n".join(lines) + "\n")
    return "\n".join(pages)


def fence(text: str, lang: str) -> str:
    return f"```{lang}\n{text.rstrip()}\n```\n"


def api_reference(py_file: Path) -> str:
    """Module docstring plus the signature and docstring of every public function."""
    tree = ast.parse(py_file.read_text(encoding="utf-8"))
    out = [f"### Module `{py_file.stem}`", "", (ast.get_docstring(tree) or "").strip(), ""]
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
            args = ", ".join(a.arg for a in node.args.args)
            out.append(f"- `{node.name}({args})`: {(ast.get_docstring(node) or '').strip()}")
    return "\n".join(out).rstrip() + "\n"


def header(src: Source, retrieved: str) -> str:
    origin = "; ".join(src.origin)
    version = ", ".join(f"{k} {v}" for k, v in src.version.items())
    return (
        f"# {src.id}: {src.title}\n\n"
        f"Source ID: {src.id} | Tier: {src.tier} | Priority: {src.priority}\n"
        f"Origin: {origin}\n"
        f"Version: {version or 'n/a'}\n"
        f"Retrieved: {retrieved} by scripts/build_notebook_sources.py\n"
        f"Use in the notebook: {src.role}\n\n---\n\n"
    )


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Tier A: authoritative sources, fetched at pinned versions
# ---------------------------------------------------------------------------


def _get(url: str) -> requests.Response:
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return response


def _raw_github(repo: tuple[str, str], path: str) -> str:
    return _get(f"https://raw.githubusercontent.com/{repo[0]}/{repo[1]}/{path}").text


def authoritative_sources() -> list[Source]:
    gh_sm = {"commit": SPECMINE_GH[1][:12]}
    return [
        Source(
            "A1",
            "authoritative",
            1,
            "MSR 2027 Mining Challenge page",
            "A1 MSR 2027 Mining Challenge page.md",
            "Challenge purpose, GitSkills and SpecMine scope, example research directions, "
            "dataset links, submission expectations, open-science policy, version guidance.",
            [MSR_URL],
        ),
        Source(
            "A2",
            "authoritative",
            2,
            "GitSkills preprint",
            f"A2 GitSkills preprint arXiv {ARXIV['A2'][0]}{ARXIV['A2'][1]}.md",
            "GitSkills construction, entities, collection process, fields, sampling, limitations.",
            [f"https://arxiv.org/abs/{ARXIV['A2'][0]}{ARXIV['A2'][1]}"],
            {"arxiv": ARXIV["A2"][1]},
            original=f"A2 GitSkills preprint arXiv {ARXIV['A2'][0]}{ARXIV['A2'][1]}.pdf",
        ),
        Source(
            "A3",
            "authoritative",
            3,
            "SpecMine preprint",
            f"A3 SpecMine preprint arXiv {ARXIV['A3'][0]}{ARXIV['A3'][1]}.md",
            "SpecMine construction, corpus scope, structural features, traceability, limitations.",
            [f"https://arxiv.org/abs/{ARXIV['A3'][0]}{ARXIV['A3'][1]}"],
            {"arxiv": ARXIV["A3"][1]},
            original=f"A3 SpecMine preprint arXiv {ARXIV['A3'][0]}{ARXIV['A3'][1]}.pdf",
        ),
        Source(
            "A4",
            "authoritative",
            4,
            "GitSkills Zenodo record",
            "A4 GitSkills Zenodo record.md",
            "Archived GitSkills release and version identity (metadata only; the 44 GB file "
            "is not uploaded).",
            [f"https://doi.org/10.5281/zenodo.{ZENODO['A4']}"],
        ),
        Source(
            "A5",
            "authoritative",
            5,
            "SpecMine Zenodo record",
            "A5 SpecMine Zenodo record.md",
            "Archived SpecMine release and version identity (metadata only).",
            [
                "https://doi.org/10.5281/zenodo.22102779",
                f"https://zenodo.org/records/{ZENODO['A5']}",
            ],
        ),
        Source(
            "A6",
            "authoritative",
            6,
            "GitSkills dataset card (Hugging Face)",
            "A6 GitSkills dataset card.md",
            "Table-level documentation, column types, schema, license, access.",
            [f"https://huggingface.co/datasets/{HF['A6'][0]}"],
            {"revision": HF["A6"][1][:12]},
        ),
        Source(
            "A7",
            "authoritative",
            7,
            "SpecMine dataset card (Hugging Face)",
            "A7 SpecMine dataset card.md",
            "Table-level documentation and access information.",
            [f"https://huggingface.co/datasets/{HF['A7'][0]}"],
            {"revision": HF["A7"][1][:12]},
        ),
        Source(
            "A8",
            "authoritative",
            8,
            "SpecMine GitHub mirror: README",
            "A8a SpecMine GitHub mirror README.md",
            "Sample scope and loader instructions.",
            [f"https://github.com/{SPECMINE_GH[0]}/blob/{SPECMINE_GH[1]}/README.md"],
            gh_sm,
        ),
        Source(
            "A8",
            "authoritative",
            8,
            "SpecMine GitHub mirror: data dictionary",
            "A8b SpecMine GitHub mirror DATA_DICTIONARY.md",
            "Column-level data dictionary of the released tables.",
            [f"https://github.com/{SPECMINE_GH[0]}/blob/{SPECMINE_GH[1]}/DATA_DICTIONARY.md"],
            gh_sm,
        ),
        Source(
            "A8",
            "authoritative",
            8,
            "SpecMine GitHub mirror: schema, loader, example",
            "A8c SpecMine GitHub mirror schema loader example.md",
            "schema.sql, load.py, and example.ipynb as text.",
            [f"https://github.com/{SPECMINE_GH[0]}/tree/{SPECMINE_GH[1]}"],
            gh_sm,
        ),
        Source(
            "A9",
            "authoritative",
            9,
            "GitSkills sample repository README",
            "A9 GitSkills sample repository README.md",
            "Inspectable sample: sampling rule, schema, anonymisation, limitations, example "
            "queries.",
            [f"https://github.com/{GITSKILLS_GH[0]}/blob/{GITSKILLS_GH[1]}/README.md"],
            {"commit": GITSKILLS_GH[1][:12]},
        ),
    ]


def fetch_authoritative(src: Source, out: Path, retrieved: str) -> None:
    """Fetch one tier-A source into ``out``. Raises on network or HTTP errors."""
    target = out / src.file
    if src.id in ARXIV:
        number, ver = ARXIV[src.id]
        data = _get(f"https://arxiv.org/pdf/{number}{ver}").content
        (out / src.original).write_bytes(data)
        body = pdf_to_markdown(data)
    elif src.id == "A1":
        text = html_to_text(_get(MSR_URL).text)
        body = slice_between(text, "## Call for Mining Challenge Papers", "Important Dates AoE")
    elif src.id in ZENODO:
        record = _get(f"https://zenodo.org/api/records/{ZENODO[src.id]}").json()
        src.version = {
            "version": record.get("metadata", {}).get("version"),
            "record": record.get("id"),
            "concept_doi": record.get("conceptdoi"),
        }
        body = zenodo_to_markdown(record)
    elif src.id in HF:
        repo, rev = HF[src.id]
        body = _get(f"https://huggingface.co/datasets/{repo}/raw/{rev}/README.md").text
    elif src.file.startswith("A8a"):
        body = _raw_github(SPECMINE_GH, "README.md")
    elif src.file.startswith("A8b"):
        body = _raw_github(SPECMINE_GH, "DATA_DICTIONARY.md")
    elif src.file.startswith("A8c"):
        notebook = json.loads(_raw_github(SPECMINE_GH, "example.ipynb"))
        body = (
            "## schema.sql\n\n"
            + fence(_raw_github(SPECMINE_GH, "schema.sql"), "sql")
            + "\n## load.py\n\n"
            + fence(_raw_github(SPECMINE_GH, "load.py"), "python")
            + "\n## example.ipynb (cells only)\n\n"
            + notebook_to_markdown(notebook)
        )
    elif src.id == "A9":
        body = _raw_github(GITSKILLS_GH, "README.md")
    else:
        raise ValueError(f"no fetch rule for {src.id}")
    target.write_text(header(src, retrieved) + body, encoding="utf-8")


# ---------------------------------------------------------------------------
# Tiers G and P: bundles of local files
# ---------------------------------------------------------------------------

# (id, title, file, role, [paths relative to the repository root])
GROUP_BUNDLES: list[tuple[str, str, str, str, list[str]]] = [
    (
        "G1",
        "Project overview and research design (P-01)",
        "G1 Research design P-01.md",
        "What Group 9 studies and why: research question, unit, population, hypotheses, "
        "threat model, topic decision.",
        [
            "README.md",
            "RESEARCH_QUESTION.md",
            "docs/proposals/P-01-jerad-dunne-skill-risk-propagation.md",
            "docs/research/THREAT_MODEL.md",
            "docs/decisions/ADR-0004-topic-selection.md",
        ],
    ),
    (
        "G2",
        "Data intake, provenance, and data dictionary",
        "G2 Data intake and dictionary.md",
        "How data enters the project, which snapshot is pinned, every derived variable, and "
        "what the first inspection found.",
        [
            "data/README.md",
            "DATA_DICTIONARY.md",
            "results/ANALYSIS_MANIFEST.json",
            "results/population_flow.csv",
            "docs/workspace/FINDINGS_LOG.md",
        ],
    ),
    (
        "G3",
        "Detection rules and validation protocol",
        "G3 Rules and validation.md",
        "The risk-signal rules, the annotation guideline, rater protocol, and blindness rule.",
        [
            "rules/skill_risk_rules.yaml",
            "docs/validation/README.md",
            "docs/validation/ANNOTATION_GUIDELINE.md",
            "docs/validation/RULE_CHANGE_PROPOSALS.md",
            "data/annotations/README.md",
            "data/annotations/samples/SAMPLE_MANIFEST.json",
        ],
    ),
    (
        "G4",
        "Threats, risks, and the draft report",
        "G4 Threats risks and draft report.md",
        "Threats to validity, FMEA risk register, and the living report with unvalidated results.",
        ["THREATS_TO_VALIDITY.md", "docs/lean-six-sigma/FMEA_RISK_REGISTER.md", "report/draft.md"],
    ),
    (
        "G5",
        "Process: Scrum with a Lean Six Sigma overlay",
        "G5 Process Scrum and Lean Six Sigma.md",
        "Ceremonies, DMAIC tollgates, KPIs and targets, SIPOC and CTQ, value stream, control "
        "plan, kaizen and waste logs.",
        [
            "docs/PROCESS.md",
            "docs/lean-six-sigma/README.md",
            "docs/lean-six-sigma/DMAIC.md",
            "docs/lean-six-sigma/KPIS.md",
            "docs/lean-six-sigma/SIPOC_AND_CTQ.md",
            "docs/lean-six-sigma/VALUE_STREAM_MAP.md",
            "docs/lean-six-sigma/CONTROL_PLAN.md",
            "docs/lean-six-sigma/KAIZEN_BACKLOG.md",
            "docs/lean-six-sigma/WASTE_LOG.md",
            "docs/lean-six-sigma/metrics/DASHBOARD.md",
        ],
    ),
    (
        "G6",
        "Project management, team, and decisions",
        "G6 Project management and decisions.md",
        "Plan, charter, RACI, roles, sprint plan, decision log, and architecture decisions.",
        [
            "PROJECT_PLAN.md",
            "TEAM_CHARTER.md",
            "project.yml",
            "docs/team/RACI.md",
            "docs/sprints/sprint-1/planning.md",
            "docs/workspace/DECISION_LOG.md",
            "docs/workspace/WORK_SIGNUP.md",
            "docs/decisions/ADR-0001-scrum-with-lean-six-sigma.md",
            "docs/decisions/ADR-0002-proposal-and-voting-process.md",
            "docs/decisions/ADR-0003-repository-structure-and-tooling.md",
            "docs/decisions/ADR-0005-solo-execution.md",
            "docs/decisions/ADR-0006-group-reinstated.md",
        ],
    ),
    (
        "G7",
        "Git, documentation, and work intake",
        "G7 Git documentation and work intake.md",
        "Branch and review rules, onboarding, issue forms (how work enters), PR template, CI, "
        "AI-use disclosure, build commands.",
        [
            "CONTRIBUTING.md",
            "docs/GETTING_STARTED.md",
            ".github/PULL_REQUEST_TEMPLATE.md",
            ".github/ISSUE_TEMPLATE/03-task.yml",
            ".github/ISSUE_TEMPLATE/05-decision.yml",
            ".github/ISSUE_TEMPLATE/08-research-finding.yml",
            ".github/ISSUE_TEMPLATE/09-work-signup.yml",
            ".github/workflows/ci.yml",
            "docs/workspace/README.md",
            "ai-use-log.md",
            "Makefile",
            "pyproject.toml",
        ],
    ),
]

PRACTICE_BUNDLES: list[tuple[str, str, str, str, list[str]]] = [
    (
        "P1",
        "Build method and phase gates",
        "P1 Build method and phase gates.md",
        "How the member builds applications: source-first builds, phases with exit gates.",
        ["docs/00_METHOD.md"],
    ),
    (
        "P2",
        "Intake: charter, discovery, and policy rules",
        "P2 Intake charter discovery and rules.md",
        "How project information, constraints, and governing rules are gathered before building.",
        [
            ".claude/skills/ppf-charter/SKILL.md",
            ".claude/skills/ppf-discover/SKILL.md",
            "docs/02_CONSTRAINTS_CARD.md",
            "docs/12_POLICY_REGISTER.md",
        ],
    ),
    (
        "P3",
        "Source control, change control, and release",
        "P3 Git change control and release.md",
        "Commit gates, change-impact classes, promotion, and handoff.",
        ["docs/11_GIT_ALM.md", "docs/15_CHANGE_CONTROL.md", ".claude/skills/ppf-change/SKILL.md"],
    ),
    (
        "P4",
        "Testing and validation gates",
        "P4 Testing and validation gates.md",
        "Validators, self-test harness, negative assertions, and what counts as passing.",
        ["docs/13_TESTING_VALIDATION.md", ".claude/skills/ppf-validate/SKILL.md"],
    ),
    (
        "P5",
        "Lessons learned",
        "P5 Lessons learned.md",
        "Failures from real builds and the rule each one produced.",
        ["docs/14_LESSONS_LEARNED.md"],
    ),
]

LANG = {
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".csv": "csv",
    ".toml": "toml",
    ".py": "python",
    ".sql": "sql",
}


def bundle(base: Path, paths: list[str], label: str) -> tuple[str, list[str], list[str]]:
    """Concatenate files under ``base``. Returns (text, included paths, missing paths)."""
    parts: list[str] = []
    included: list[str] = []
    missing: list[str] = []
    for rel in paths:
        path = base / rel
        if not path.is_file():
            missing.append(rel)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix.lower() in LANG or path.name == "Makefile":
            text = fence(text, LANG.get(path.suffix.lower(), "make"))
        parts.append(f"\n\n## File: {label}{rel}\n\n{text.strip()}\n")
        included.append(f"{label}{rel}")
    return "".join(parts), included, missing


# The notebook's own code is not domain information: indexing it lets the notebook
# cite itself (seen in the first trial run, question NB-Q11).
REFERENCE_EXCLUDE = {"__init__.py", "__main__.py", "elicitation.py"}


def pipeline_reference(root: Path) -> str:
    modules = sorted((root / "src" / "msr_pipeline").glob("*.py"))
    return "\n".join(api_reference(m) for m in modules if m.name not in REFERENCE_EXCLUDE)


def git_commit(root: Path) -> tuple[str, bool]:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=root,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown", True
    return sha, dirty


# ---------------------------------------------------------------------------
# Record files
# ---------------------------------------------------------------------------


def render_register(sources: list[Source], manifest: dict) -> str:
    lines = [
        "# Notebook source register",
        "",
        "Generated by `python scripts/build_notebook_sources.py` from the definitions in that "
        "script. Do not edit by hand; change the script and re-run it. Hashes and byte sizes "
        "are in `SOURCES_MANIFEST.json` next to this file.",
        "",
        f"- Generated: {manifest['generated_at']}",
        f"- Repository commit for tier G: `{manifest['repo_commit'][:12]}`"
        + (" (working tree had uncommitted changes)" if manifest["repo_dirty"] else ""),
        f"- Tier P included: {'yes' if manifest['practice_included'] else 'no'}",
        "",
        "Tiers: **A** authoritative (dataset facts), **G** group (what Group 9 decided and how it "
        "works), **P** practitioner (a member's personal build method; process questions only).",
        "",
        "| ID | Tier | Priority | Indexed file (citation title) | Use in the notebook | Origin | "
        "Version | Status |",
        "|---|---|---:|---|---|---|---|---|",
    ]
    for s in sources:
        version = ", ".join(f"{k} {v}" for k, v in s.version.items()) or "n/a"
        origin = "<br>".join(s.origin[:3]) + (
            f"<br>(+{len(s.origin) - 3} more)" if len(s.origin) > 3 else ""
        )
        lines.append(
            f"| {s.id} | {s.tier} | {s.priority} | {s.file} | {s.role} | {origin} | "
            f"{version} | {s.status} |"
        )
    lines += [
        "",
        "Not included, by design: the full GitSkills SQLite file (44,388,249,600 bytes on "
        "Zenodo), the sample database, and the SpecMine archive. The notebook documents the "
        "datasets; it is not a substitute for them.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Where the pack is written.")
    parser.add_argument(
        "--record-dir",
        type=Path,
        default=DEFAULT_RECORD,
        help="Where SOURCES_MANIFEST.json and SOURCE_REGISTER.md are written.",
    )
    parser.add_argument(
        "--practice-dir",
        type=Path,
        help="Root of a personal build-method folder for tier P (optional).",
    )
    parser.add_argument(
        "--practice-label",
        default="practice",
        help="Name recorded for --practice-dir; the local path is never recorded.",
    )
    parser.add_argument("--skip-fetch", action="store_true", help="Build tiers G and P only.")
    args = parser.parse_args(argv)

    out: Path = args.out.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    retrieved = datetime.now(UTC).strftime("%Y-%m-%d")
    commit, dirty = git_commit(ROOT)
    sources: list[Source] = []
    failures = 0

    if not args.skip_fetch:
        for src in authoritative_sources():
            try:
                fetch_authoritative(src, out, retrieved)
                src.status = "fetched"
            except (requests.RequestException, ValueError, KeyError, ImportError) as exc:
                src.status = f"fetch failed: {exc.__class__.__name__}"
                failures += 1
                print(f"  {src.file}: {exc}", file=sys.stderr)
            sources.append(src)

    for sid, title, fname, role, paths in GROUP_BUNDLES:
        src = Source(sid, "group", 10, title, fname, role, version={"commit": commit[:12]})
        text, included, missing = bundle(ROOT, paths, "")
        src.origin, src.status = included, "bundled" if not missing else f"missing {missing}"
        (out / fname).write_text(header(src, retrieved) + text, encoding="utf-8")
        sources.append(src)

    ref = Source(
        "G8",
        "group",
        10,
        "Pipeline API reference",
        "G8 Pipeline API reference.md",
        "Every public function in src/msr_pipeline with its docstring, generated from the code.",
        ["src/msr_pipeline/*.py"],
        {"commit": commit[:12]},
        "generated",
    )
    (out / ref.file).write_text(header(ref, retrieved) + pipeline_reference(ROOT), encoding="utf-8")
    sources.append(ref)

    if args.practice_dir:
        base = args.practice_dir.expanduser().resolve()
        for sid, title, fname, role, paths in PRACTICE_BUNDLES:
            src = Source(sid, "practitioner", 20, title, fname, role)
            text, included, missing = bundle(base, paths, f"{args.practice_label}:")
            src.origin = included
            src.status = "bundled" if not missing else f"missing {missing}"
            (out / fname).write_text(header(src, retrieved) + text, encoding="utf-8")
            sources.append(src)

    manifest = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "generator": "scripts/build_notebook_sources.py",
        "repo_commit": commit,
        "repo_dirty": dirty,
        "practice_included": bool(args.practice_dir),
        "practice_label": args.practice_label if args.practice_dir else None,
        "sources": [],
    }
    for s in sources:
        path = out / s.file
        entry = {
            "id": s.id,
            "tier": s.tier,
            "priority": s.priority,
            "title": s.title,
            "file": s.file,
            "role": s.role,
            "origin": s.origin,
            "version": s.version,
            "status": s.status,
        }
        if path.is_file():
            entry |= {"bytes": path.stat().st_size, "sha256": sha256_of(path)}
        if s.original and (out / s.original).is_file():
            entry["original"] = {
                "file": s.original,
                "bytes": (out / s.original).stat().st_size,
                "sha256": sha256_of(out / s.original),
            }
        manifest["sources"].append(entry)

    record: Path = args.record_dir.resolve()
    record.mkdir(parents=True, exist_ok=True)
    (out / "SOURCES_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    (record / "SOURCES_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    (record / "SOURCE_REGISTER.md").write_text(render_register(sources, manifest), encoding="utf-8")

    print(f"{len(sources)} sources written to {out} ({failures} fetch failures)")
    print(f"Register: {record / 'SOURCE_REGISTER.md'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

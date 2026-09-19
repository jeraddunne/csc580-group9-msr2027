"""Tests for the elicitation notebook, its source-pack builder, and the elicit command."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest
import yaml

from msr_pipeline import cli
from msr_pipeline import elicitation as el

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_KINDS = {
    "meaning": "Meaning and scope",
    "schema": "Schema and relationships",
    "feasibility": "Feasibility",
    "implementation or validation": ("Implementation", "Validation"),
    "ethics": "Ethics",
    "not established": "Not established",
}


def _builder():
    spec = importlib.util.spec_from_file_location(
        "build_notebook_sources", ROOT / "scripts" / "build_notebook_sources.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolve their module through sys.modules
    spec.loader.exec_module(module)
    return module


def _pack(tmp_path: Path) -> Path:
    """A two-tier pack: GitSkills facts in tier A, a process rule in tier G, SpecMine in A3."""
    files = {
        ("A9", "authoritative", "A9 sample.md"): (
            "# A9: sample\n\nSource ID: A9\n\n---\n\n"
            "## Known limitations\n\n"
            "Commit history follows the file's current path: for a renamed file, "
            "`first_commit_at` dates the rename and `commit_count` covers the current path "
            "only. History is collected for standard locations.\n\n"
            "## Anonymisation\n\n"
            "Commit author accounts are replaced by keyed one-way codes. Bot accounts keep "
            "their login and emails in commit messages are masked with a fixed marker.\n"
        ),
        ("A3", "authoritative", "A3 specmine.md"): (
            "## Page 1\n\nSpecMine records commit history status for every spec file, "
            "with a first commit date per file path and renamed files tracked.\n"
        ),
        ("G6", "group", "G6 plan.md"): (
            "## 11. Change management\n\n"
            "- **Research changes:** a decision issue, discussion, an ADR, and a line in the "
            "retrospective.\n- **Process changes:** a kaizen issue with a measurable effect.\n"
        ),
    }
    manifest = {
        "generated_at": "2026-09-18T00:00:00+00:00",
        "repo_commit": "abc123",
        "practice_included": False,
        "sources": [],
    }
    for (sid, tier, name), text in files.items():
        (tmp_path / name).write_text(text, encoding="utf-8")
        manifest["sources"].append({"id": sid, "tier": tier, "file": name})
    (tmp_path / "SOURCES_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path


# --- tokenising and passages ---------------------------------------------------------


def test_tokenize_keeps_identifiers_and_strips_plurals() -> None:
    toks = el.tokenize("The `content_sha_ok` flag for skills that reaches copies")
    assert "content_sha_ok" in toks and "content" in toks and "sha" in toks
    assert "skill" in toks and "reach" in toks and "copy" in toks
    assert "the" not in toks and "for" not in toks
    assert el.tokenize("malicious access analysis") == ["malicious", "access", "analysis"]


def test_split_passages_tracks_sections_lines_and_fences() -> None:
    text = (
        "# A1: Title\n\nSource ID: A1\n\n---\n\n"  # pack header, skipped
        "## Schema\n\n### `artifacts`\n\n"
        "One row per discovered file occurrence with its repository and path and hash.\n\n"
        "## Rules\n\n```yaml\n# a YAML comment, not a heading\nid: R-1\n"
        "category: SHELL severity five patterns list of regular expressions here\n```\n"
    )
    passages = el.split_passages(text, "A1", "authoritative", "a.md")
    assert passages[0].section == "Schema > `artifacts`"
    assert passages[0].line == 11
    assert "Source ID" not in " ".join(p.text for p in passages)
    fenced = [p for p in passages if "YAML comment" in p.text]
    assert fenced and fenced[0].section == "Rules"


def test_split_passages_cuts_long_blocks_on_lines() -> None:
    body = "\n".join(f"line {i} " + "word " * 30 for i in range(10))
    passages = el.split_passages(body, "G1", "group", "g.md", max_words=100)
    assert len(passages) > 1
    assert all(len(p.text.split()) <= 100 for p in passages)
    assert passages[1].line > passages[0].line


# --- asking -------------------------------------------------------------------------


def test_ask_ranks_the_relevant_passage_first(tmp_path: Path) -> None:
    nb = el.Notebook.from_pack(_pack(tmp_path))
    ans = nb.ask("What does first_commit_at mean for a renamed file?", "gitskills")
    assert ans.hits[0][0].source_id == "A9"
    assert ans.hits[0][0].section == "Known limitations"
    assert ans.status == "match"
    assert "A9" in ans.sources_cited


def test_scopes_restrict_tiers_and_datasets(tmp_path: Path) -> None:
    nb = el.Notebook.from_pack(_pack(tmp_path))
    q = "commit history for renamed files and change management"
    assert {p.source_id for p, _ in nb.ask(q, "gitskills").hits} == {"A9"}
    assert "A3" in {p.source_id for p, _ in nb.ask(q, "dataset").hits}
    assert {p.tier for p, _ in nb.ask(q, "group").hits} == {"group"}
    with pytest.raises(ValueError):
        nb.ask(q, "everything")


def test_no_match_and_missing_terms(tmp_path: Path) -> None:
    nb = el.Notebook.from_pack(_pack(tmp_path))
    ans = nb.ask("quantum chromodynamics lattice", "gitskills")
    assert ans.status == "no match" and not ans.hits
    assert "No passage in this scope matches" in ans.to_markdown()
    weak = nb.ask("keyed codes zebra giraffe elephant walrus", "gitskills")
    assert weak.status == "weak match"
    assert "zebra" in weak.missing


def test_per_source_cap(tmp_path: Path) -> None:
    nb = el.Notebook.from_pack(_pack(tmp_path))
    ans = nb.ask("commit author accounts renamed file history", "dataset", k=3)
    assert sum(1 for p, _ in ans.hits if p.file == "A9 sample.md") <= el.PER_SOURCE


def test_from_pack_needs_a_manifest(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="build_notebook_sources"):
        el.Notebook.from_pack(tmp_path)


def test_transcript_has_provenance_and_locators(tmp_path: Path) -> None:
    nb = el.Notebook.from_pack(_pack(tmp_path))
    qs = [
        {
            "id": "NB-Q01",
            "kind": "Schema",
            "scope": "gitskills",
            "question": "What does first_commit_at mean for a renamed file?",
        },
        {
            "id": "NB-Q01a",
            "kind": "Schema",
            "scope": "group",
            "follow_up_of": "NB-Q01",
            "question": "What do research changes need?",
        },
    ]
    text = el.render_transcript(nb.interview(qs), nb, k=3)
    assert "repository commit `abc123`" in text
    assert "A9 · A9 sample.md · Known limitations · line" in text
    assert "follow-up to NB-Q01" in text


# --- the prepared question set ---------------------------------------------------------


def test_load_questions_rejects_bad_sets(tmp_path: Path) -> None:
    path = tmp_path / "q.yaml"
    for questions, message in [
        ([{"id": "Q1", "question": "a"}, {"id": "Q1", "question": "b"}], "duplicate"),
        ([{"id": "Q1", "question": "a", "scope": "web"}], "unknown scope"),
        (
            [{"id": "Q1a", "question": "a", "follow_up_of": "Q1"}, {"id": "Q1", "question": "b"}],
            "not asked before",
        ),
    ]:
        path.write_text(yaml.safe_dump({"questions": questions}), encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            el.load_questions(path)


def test_prepared_questions_meet_the_assignment() -> None:
    questions = el.load_questions(ROOT / "elicitation" / "questions.yaml")
    primary = [q for q in questions if not q.get("follow_up_of")]
    assert len(primary) >= 10
    kinds = " | ".join(q["kind"] for q in primary)
    for need, labels in REQUIRED_KINDS.items():
        labels = labels if isinstance(labels, tuple) else (labels,)
        assert any(label in kinds for label in labels), f"no {need} question"


def test_interview_record_quotes_every_question_word_for_word() -> None:
    record = (ROOT / "elicitation" / "notebook-interview.md").read_text(encoding="utf-8")
    flat = re.sub(r"\s+", " ", record)
    for q in el.load_questions(ROOT / "elicitation" / "questions.yaml"):
        assert re.sub(r"\s+", " ", q["question"]) in flat, q["id"]
        assert f"### {q['id']}" in record, q["id"]


# --- the builder's pure functions --------------------------------------------------------


def test_builder_text_conversions() -> None:
    b = _builder()
    text = b.html_to_text(
        "<html><nav>menu</nav><h2>Call</h2><p>Body <b>bold</b></p><script>x()</script>"
        "<ul><li>one</li></ul></html>"
    )
    assert "## Call" in text and "Body bold" in text and "- one" in text
    assert "menu" not in text and "x()" not in text
    assert b.slice_between("aa START bb END cc", "START", "END") == "START bb\n"
    nb = {
        "cells": [
            {"cell_type": "markdown", "source": ["# T"]},
            {"cell_type": "code", "source": ["print(1)"]},
        ]
    }
    assert "```python\nprint(1)\n```" in b.notebook_to_markdown(nb)
    record = {
        "id": 1,
        "doi": "d/1",
        "conceptdoi": "d/0",
        "metadata": {
            "title": "T",
            "version": "1.0",
            "license": {"id": "cc-by-4.0"},
            "creators": [{"name": "A, B"}],
            "description": "<p>Desc</p>",
        },
        "files": [{"key": "x.db", "size": 1234}],
    }
    md = b.zenodo_to_markdown(record)
    assert "Version: 1.0" in md and "| x.db | 1,234 |" in md and "Desc" in md


def test_builder_bundle_reports_missing_files(tmp_path: Path) -> None:
    b = _builder()
    (tmp_path / "a.md").write_text("# A\nbody", encoding="utf-8")
    (tmp_path / "r.yaml").write_text("k: v", encoding="utf-8")
    text, included, missing = b.bundle(tmp_path, ["a.md", "r.yaml", "gone.md"], "lbl:")
    assert included == ["lbl:a.md", "lbl:r.yaml"] and missing == ["gone.md"]
    assert "## File: lbl:a.md" in text and "```yaml\nk: v\n```" in text


def test_builder_escapes_hash_lines_in_pdf_text(monkeypatch: pytest.MonkeyPatch) -> None:
    b = _builder()

    class Page:
        def extract_text(self) -> str:
            return "Figure 2\n# Web Artifacts Builder\nbody"

    class Reader:
        def __init__(self, _stream: object) -> None:
            self.pages = [Page()]

    import pypdf

    monkeypatch.setattr(pypdf, "PdfReader", Reader)
    md = b.pdf_to_markdown(b"%PDF")
    assert "## Page 1" in md and "\\# Web Artifacts Builder" in md
    passages = el.split_passages(md, "A2", "authoritative", "a2.md")
    assert {p.section for p in passages} == {"Page 1"}


# --- command line ---------------------------------------------------------------------


def test_cli_elicit_writes_transcript(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "pack").mkdir()
    pack = _pack(tmp_path / "pack")
    qfile = tmp_path / "q.yaml"
    qfile.write_text(
        yaml.safe_dump(
            {
                "questions": [
                    {
                        "id": "NB-Q01",
                        "kind": "Schema",
                        "scope": "gitskills",
                        "question": "What does first_commit_at mean for a renamed file?",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    out = tmp_path / "t.md"
    assert (
        cli.main(["elicit", "--pack", str(pack), "--questions", str(qfile), "--out", str(out)]) == 0
    )
    assert "NB-Q01: match" in capsys.readouterr().out
    assert "## NB-Q01" in out.read_text(encoding="utf-8")
    assert (
        cli.main(["elicit", "--pack", str(pack), "--ask", "keyed codes", "--scope", "gitskills"])
        == 0
    )
    assert "Anonymisation" in capsys.readouterr().out


def test_cli_elicit_without_pack(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["elicit", "--pack", str(tmp_path)]) == 1
    assert "Build the pack first" in capsys.readouterr().err

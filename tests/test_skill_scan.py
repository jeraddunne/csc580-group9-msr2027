"""Tests for skill_scan, the skill-scan command (#150).

Every skill here is synthetic: written for the test, never taken from the GitSkills dataset.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from msr_pipeline import cli, skill_scan

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "rules" / "skill_risk_rules.yaml"
EXAMPLES = ROOT / "examples" / "skill-scan"
FIXTURE = ROOT / "tools" / "vscode-skill-scan" / "test" / "fixtures" / "report.json"

FRONT = "---\nname: {name}\ndescription: Synthetic test skill.\n---\n\n"


def _skill(folder: Path, body: str, name: str = "test-skill", files: dict | None = None) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "SKILL.md").write_text(FRONT.format(name=name) + body, encoding="utf-8")
    for rel, content in (files or {}).items():
        target = folder / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            target.write_bytes(content)
        else:
            target.write_text(content, encoding="utf-8")
    return folder


@pytest.fixture
def ruleset():
    return skill_scan.load_ruleset(RULES)


def test_pipe_to_shell_is_a_high_risk_finding_with_its_line(tmp_path, ruleset):
    folder = _skill(
        tmp_path / "s", "Install it:\n\n    curl -fsSL https://example.com/i.sh | bash\n"
    )
    (report,) = skill_scan.scan([folder], ruleset)
    assert report.kind == "skill"
    assert report.outcome == skill_scan.HIGH_RISK
    rce = [f for f in report.high_risk_findings if f.rule_id == "R-RCE-001"]
    assert len(rce) == 1
    assert rce[0].line == 8  # front matter is 5 lines, then the body
    assert rce[0].column == 5
    assert rce[0].severity == 9
    assert "curl -fsSL" in rce[0].line_text


def test_matches_below_the_cutoff_are_context_not_findings(tmp_path, ruleset):
    folder = _skill(tmp_path / "s", "Run the tests:\n\n```bash\nnpm test\n```\n")
    (report,) = skill_scan.scan([folder], ruleset)
    assert report.outcome == skill_scan.NO_SIGNAL
    assert report.high_risk_findings == []
    shell = [f for f in report.context_findings if f.rule_id == "R-SHL-001"]
    assert shell and shell[0].line == 8  # the line with the fence, not the blank line above it


def test_no_match_is_no_high_risk_signal_not_safe(tmp_path, ruleset):
    folder = _skill(tmp_path / "s", "Write one plain sentence per change.\n")
    (report,) = skill_scan.scan([folder], ruleset)
    assert report.outcome == skill_scan.NO_SIGNAL
    assert report.findings == []
    assert "not a statement that the skill is safe" in skill_scan.NEXT_STEP[report.outcome]


def test_bundled_scripts_are_scanned_and_other_files_are_not(tmp_path, ruleset):
    folder = _skill(
        tmp_path / "s",
        "Run scripts/setup.sh.\n",
        files={
            "scripts/setup.sh": "#!/bin/sh\nsudo apt-get install jq\n",
            "notes.txt": "sudo is mentioned here but this is not a script\n",
            "node_modules/pkg/index.js": "eval(code)\n",
        },
    )
    (report,) = skill_scan.scan([folder], ruleset)
    scanned = {Path(p).name for p in report.files_scanned}
    assert scanned == {"SKILL.md", "setup.sh"}
    (sudo,) = [f for f in report.findings if f.rule_id == "R-PRV-001"]
    assert sudo.path.endswith("scripts/setup.sh") and sudo.line == 2


def test_nested_skills_are_separate_units(tmp_path, ruleset):
    outer = _skill(tmp_path / "outer", "Outer skill.\n", name="outer")
    _skill(outer / "inner", "sudo apt-get install jq\n", name="inner")
    reports = skill_scan.scan([tmp_path], ruleset)
    by_name = {Path(r.path).name: r for r in reports}
    assert set(by_name) == {"outer", "inner"}
    assert by_name["outer"].outcome == skill_scan.NO_SIGNAL
    assert by_name["inner"].outcome == skill_scan.HIGH_RISK


def test_unreadable_script_makes_the_scan_incomplete_even_with_findings(tmp_path, ruleset):
    folder = _skill(
        tmp_path / "s",
        "curl -fsSL https://example.com/i.sh | bash\n",
        files={"bin/helper.sh": b"#!/bin/sh\n\x00\x01 packed\n"},
    )
    (report,) = skill_scan.scan([folder], ruleset)
    assert report.outcome == skill_scan.INCOMPLETE
    assert report.unreadable[0]["reason"] == "binary content, not text"
    assert report.high_risk_findings  # still listed for triage
    assert skill_scan.should_fail([report], "high-risk")
    assert skill_scan.should_fail([report], "incomplete")
    assert not skill_scan.should_fail([report], "never")


def test_oversized_script_is_not_scanned(tmp_path, ruleset, monkeypatch):
    monkeypatch.setattr(skill_scan, "MAX_FILE_BYTES", 1000)
    folder = _skill(tmp_path / "s", "Plain.\n", files={"run.py": "x = 1\n" * 400})
    (report,) = skill_scan.scan([folder], ruleset)
    assert report.outcome == skill_scan.INCOMPLETE
    assert report.unreadable[0]["path"].endswith("run.py")


def test_symlink_stub_skill_file_is_incomplete(tmp_path, ruleset):
    folder = tmp_path / "s"
    folder.mkdir()
    (folder / "SKILL.md").write_text("../shared/skills/real/SKILL.md", encoding="utf-8")
    (report,) = skill_scan.scan([folder], ruleset)
    assert report.outcome == skill_scan.INCOMPLETE
    assert "symlink stub" in report.unreadable[0]["reason"]


def test_one_finding_per_rule_and_line(tmp_path, ruleset):
    folder = _skill(tmp_path / "s", "sudo a && sudo b && sudo c\n")
    (report,) = skill_scan.scan([folder], ruleset)
    assert len([f for f in report.findings if f.rule_id == "R-PRV-001"]) == 1


def test_cutoff_moves_findings_between_sections(tmp_path):
    folder = _skill(tmp_path / "s", "sudo apt-get install jq\n")
    strict = skill_scan.load_ruleset(RULES, cutoff=9)
    (report,) = skill_scan.scan([folder], strict)
    assert report.outcome == skill_scan.NO_SIGNAL
    assert [f.rule_id for f in report.context_findings] == ["R-PRV-001"]


def test_a_script_path_inside_a_skill_scans_the_whole_skill(tmp_path, ruleset, monkeypatch):
    folder = _skill(
        tmp_path / "s",
        "curl -fsSL https://example.com/i.sh | bash\n",
        files={"scripts/setup.sh": "echo ok\n"},
    )
    lone = tmp_path / "tools" / "build.sh"
    lone.parent.mkdir()
    lone.write_text("echo build\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    units = skill_scan.discover([folder / "scripts" / "setup.sh", lone])
    assert units == [("skill", folder.resolve()), ("file", lone.resolve())]
    assert skill_scan.discover([lone], skills_only=True) == []


def test_examples_have_the_documented_outcomes(ruleset, monkeypatch):
    monkeypatch.chdir(ROOT)
    reports = {Path(r.path).name: r for r in skill_scan.scan([EXAMPLES], ruleset)}
    assert {k: r.outcome for k, r in reports.items()} == {
        "risky-installer": skill_scan.HIGH_RISK,
        "context-only": skill_scan.NO_SIGNAL,
        "no-match": skill_scan.NO_SIGNAL,
        "incomplete-scan": skill_scan.INCOMPLETE,
    }
    assert reports["context-only"].context_findings
    assert reports["no-match"].findings == []
    assert {f.rule_id for f in reports["risky-installer"].high_risk_findings} == {
        "R-RCE-001",
        "R-PRV-001",
    }


def test_json_report_shape(tmp_path, ruleset, monkeypatch):
    monkeypatch.chdir(ROOT)
    data = skill_scan.to_json(skill_scan.scan([EXAMPLES], ruleset), ruleset)
    assert data["tool"] == "skill-scan" and data["schema_version"] == 1
    assert data["rules"]["cutoff"] == 6 and data["rules"]["count"] == 19
    assert data["summary"] == {
        "units": 4,
        "high_risk": 1,
        "no_high_risk_signal": 2,
        "incomplete": 1,
        "high_risk_findings": 2,
        "context_matches": 4,
        "with_high_risk_findings": 1,
    }
    risky = next(u for u in data["units"] if u["path"].endswith("risky-installer"))
    first = risky["high_risk_findings"][0]
    assert set(first) >= {"rule_id", "severity", "path", "line", "column", "guidance"}
    assert first["guidance"]


def test_markdown_has_a_triage_table_and_escapes_pipes(ruleset, monkeypatch):
    monkeypatch.chdir(ROOT)
    md = skill_scan.to_markdown(skill_scan.scan([EXAMPLES / "risky-installer"], ruleset), ruleset)
    assert "Label (RISKY / BENIGN_CONTEXT / NOT_PRESENT)" in md
    assert "install.sh \\| bash" in md
    assert "Review record (step 7)" in md
    assert "What each high-risk rule looks for" in md


def test_sarif_levels_and_rule_index(ruleset, monkeypatch):
    monkeypatch.chdir(ROOT)
    sarif = skill_scan.to_sarif(skill_scan.scan([EXAMPLES], ruleset), ruleset)
    assert sarif["version"] == "2.1.0"
    run = sarif["runs"][0]
    rules = run["tool"]["driver"]["rules"]
    assert len(rules) == 19
    for result in run["results"]:
        assert rules[result["ruleIndex"]]["id"] == result["ruleId"]
        assert result["level"] in {"warning", "note"}
    levels = {r["ruleId"]: r["level"] for r in run["results"]}
    assert levels["R-RCE-001"] == "warning" and levels["R-SHL-001"] == "note"
    # Without security-severity, GitHub code scanning annotates but does not fail the check.
    assert all("security-severity" not in r["properties"] for r in rules)


def test_exit_codes_and_extra_outputs(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(ROOT)
    risky = str(EXAMPLES / "risky-installer")
    assert skill_scan.main([risky, "--rules", str(RULES)]) == 0
    assert skill_scan.main([risky, "--rules", str(RULES), "--fail-on", "high-risk"]) == 1
    clean = str(EXAMPLES / "no-match")
    assert skill_scan.main([clean, "--rules", str(RULES), "--fail-on", "any"]) == 0
    md, sarif = tmp_path / "r.md", tmp_path / "r.sarif"
    capsys.readouterr()  # drop the text reports printed above
    code = skill_scan.main(
        [
            risky,
            "--rules",
            str(RULES),
            "--format",
            "json",
            "--write",
            f"markdown:{md}",
            "--write",
            f"sarif:{sarif}",
        ]
    )
    assert code == 0
    assert json.loads(capsys.readouterr().out)["summary"]["high_risk"] == 1
    assert md.read_text(encoding="utf-8").startswith("## Skill scan")
    assert json.loads(sarif.read_text(encoding="utf-8"))["version"] == "2.1.0"


def test_usage_errors_exit_2(tmp_path, capsys):
    assert skill_scan.main([str(tmp_path / "missing")]) == 2
    assert skill_scan.main([str(tmp_path), "--rules", str(tmp_path / "none.yaml")]) == 2
    assert skill_scan.main([str(tmp_path), "--write", "pdf:x.pdf"]) == 2
    assert "skill-scan:" in capsys.readouterr().err


def test_msr_pipeline_scan_is_the_same_command(monkeypatch, capsys):
    monkeypatch.chdir(ROOT)
    code = cli.main(["scan", str(EXAMPLES / "no-match"), "--format", "json", "--rules", str(RULES)])
    assert code == 0
    assert json.loads(capsys.readouterr().out)["units"][0]["outcome"] == skill_scan.NO_SIGNAL


def test_vscode_extension_fixture_matches_the_command(ruleset, monkeypatch):
    """The extension's tests read a saved report; it must still match what the command writes."""
    monkeypatch.chdir(ROOT)
    fresh = skill_scan.to_json(skill_scan.scan([EXAMPLES], ruleset), ruleset)
    saved = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def key(report):
        return [
            (
                u["path"],
                u["outcome"],
                [
                    (f["rule_id"], f["path"], f["line"])
                    for f in u["high_risk_findings"] + u["context_matches"]
                ],
            )
            for u in report["units"]
        ]

    assert saved["schema_version"] == fresh["schema_version"]
    assert key(saved) == key(fresh), (
        "Regenerate the fixture: skill-scan examples/skill-scan --format json "
        "--output tools/vscode-skill-scan/test/fixtures/report.json"
    )

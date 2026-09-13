"""End-to-end tests for the command-line interface."""

from __future__ import annotations

from pathlib import Path

import pytest

from msr_pipeline import cli

EXPECTED_TABLES = [
    "gitskills_location_summary",
    "gitskills_copy_distribution",
    "gitskills_language_summary",
    "specmine_tool_summary",
    "specmine_feature_summary",
    "specmine_pr_code_cochange",
]


def test_info_lists_samples(data_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["info"]) == 0
    out = capsys.readouterr().out
    assert "GitSkills sample: present" in out
    assert "4/13 tables present" in out
    assert str(data_root) in out


def test_info_when_samples_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("MSR_DATA_DIR", str(tmp_path))
    assert cli.main(["info"]) == 0
    out = capsys.readouterr().out
    assert "GitSkills sample: missing" in out
    assert "download_samples.py" in out


def test_explore_all_writes_tables_and_figures(
    data_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(["explore", "--dataset", "all"]) == 0
    for name in EXPECTED_TABLES:
        assert (data_root / "results" / f"{name}.csv").is_file(), name
        assert (data_root / "figures" / f"{name}.png").is_file(), name
    out = capsys.readouterr().out
    assert out.count("wrote ") == 2 * len(EXPECTED_TABLES)


def test_explore_single_dataset_with_limit(data_root: Path) -> None:
    assert cli.main(["explore", "--dataset", "gitskills", "--limit", "5"]) == 0
    assert (data_root / "results" / "gitskills_location_summary.csv").is_file()
    assert not (data_root / "results" / "specmine_tool_summary.csv").exists()


def test_explore_missing_dataset_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("MSR_DATA_DIR", str(tmp_path))
    assert cli.main(["explore", "--dataset", "specmine"]) == 1
    err = capsys.readouterr().err
    assert "[skip]" in err


def test_query(data_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = cli.main(["query", "--sql", "SELECT COUNT(*) AS n FROM artifacts"])
    assert code == 0
    assert "10" in capsys.readouterr().out


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["--version"])
    assert exc.value.code == 0
    assert "msr-pipeline" in capsys.readouterr().out

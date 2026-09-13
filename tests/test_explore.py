"""Tests for the exploratory summary functions and output helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from msr_pipeline import explore, load
from msr_pipeline.config import get_paths


@pytest.fixture
def gitskills(gitskills_db: Path) -> load.GitSkillsData:
    return load.load_gitskills(gitskills_db)


@pytest.fixture
def specmine(specmine_dir_fixture: Path) -> dict[str, pd.DataFrame]:
    return load.load_specmine(specmine_dir_fixture)


def test_gitskills_location_summary(gitskills: load.GitSkillsData) -> None:
    out = explore.gitskills_location_summary(gitskills.artifacts)
    assert list(out.columns) == ["location_class", "files", "share"]
    assert out.set_index("location_class")["files"].to_dict() == {
        "canonical": 5,
        "skills-dir": 3,
        "other": 2,
    }
    assert out["share"].sum() == pytest.approx(1.0, abs=1e-3)


def test_gitskills_copy_distribution(gitskills: load.GitSkillsData) -> None:
    out = explore.gitskills_copy_distribution(gitskills.artifacts)
    # sha-A has 4 copies, sha-B has 2, four singletons
    assert out.set_index("copies")["distinct_contents"].to_dict() == {1: 4, 2: 1, 4: 1}
    assert out["copies"].is_monotonic_increasing


def test_gitskills_language_summary(gitskills: load.GitSkillsData) -> None:
    out = explore.gitskills_language_summary(gitskills.artifacts, gitskills.repos, top=3)
    assert len(out) == 3
    assert out.iloc[0]["language"] == "Python"
    assert int(out.iloc[0]["skills"]) == 5
    full = explore.gitskills_language_summary(gitskills.artifacts, gitskills.repos)
    assert "(unknown)" in set(full["language"])


def test_specmine_tool_summary(specmine: dict[str, pd.DataFrame]) -> None:
    out = explore.specmine_tool_summary(specmine["spec_files"])
    kiro = out.set_index("spec_tool").loc["kiro"]
    assert int(kiro["specs"]) == 4
    assert int(kiro["repos"]) == 3
    assert out.iloc[0]["spec_tool"] == "kiro"


def test_specmine_feature_summary(specmine: dict[str, pd.DataFrame]) -> None:
    out = explore.specmine_feature_summary(specmine["spec_content_features"])
    assert set(out.columns) == {"feature", "specs_with_feature", "share"}
    by = out.set_index("feature")
    assert int(by.loc["has_user_story", "specs_with_feature"]) == 5
    assert by.loc["has_gherkin", "share"] == pytest.approx(0.125)
    assert "is_tiny" in by.index
    assert out["share"].is_monotonic_decreasing


def test_specmine_pr_code_cochange(specmine: dict[str, pd.DataFrame]) -> None:
    out = explore.specmine_pr_code_cochange(specmine["pull_requests"], specmine["pr_files"])
    by = out.set_index("tool")
    assert int(by.loc["kiro", "spec_prs"]) == 2
    assert int(by.loc["kiro", "spec_and_code_prs"]) == 1
    assert by.loc["spec-kit", "cochange_rate"] == pytest.approx(0.5)
    assert by.loc["openspec", "cochange_rate"] == pytest.approx(0.5)


def test_pr_key_detection_fails_clearly() -> None:
    prs = pd.DataFrame({"x": [1], "tool": ["kiro"], "touches_code": [1]})
    files = pd.DataFrame({"y": [1], "is_spec": [1]})
    with pytest.raises(KeyError):
        explore.specmine_pr_code_cochange(prs, files)


def test_write_table_and_plot_bar(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MSR_DATA_DIR", str(tmp_path))
    paths = get_paths()
    df = pd.DataFrame({"k": ["a", "b", "c"], "v": [3, 2, 1]})
    csv = explore.write_table(df, "unit_table", paths)
    png = explore.plot_bar(df, "k", "v", "unit_plot", title="t", paths=paths)
    assert csv == tmp_path / "results" / "unit_table.csv"
    assert png == tmp_path / "figures" / "unit_plot.png"
    assert pd.read_csv(csv).equals(df)
    assert png.stat().st_size > 1000

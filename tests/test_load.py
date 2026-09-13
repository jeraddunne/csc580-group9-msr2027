"""Tests for msr_pipeline.load against the offline fixtures."""

from __future__ import annotations

import gzip
import json
from pathlib import Path

import pytest

from msr_pipeline import load


def test_load_gitskills_returns_four_tables(gitskills_db: Path) -> None:
    data = load.load_gitskills(gitskills_db)
    names = [name for name, _ in data]
    assert names == list(load.GITSKILLS_TABLES)
    assert len(data.artifacts) == 10
    assert len(data.repos) == 6
    assert len(data.artifact_siblings) == 3
    assert len(data.mining_runs) == 1


def test_load_gitskills_drops_content_by_default(gitskills_db: Path) -> None:
    data = load.load_gitskills(gitskills_db)
    assert "content" not in data.artifacts.columns
    assert "content" not in data.artifact_siblings.columns
    with_content = load.load_gitskills(gitskills_db, include_content=True)
    assert "content" in with_content.artifacts.columns
    assert with_content.artifacts["content"].notna().sum() == 6  # one per dedup primary


def test_load_gitskills_columns_and_limit(gitskills_db: Path) -> None:
    data = load.load_gitskills(
        gitskills_db, columns={"artifacts": ["repo_full_name", "file_sha"]}, limit=4
    )
    assert list(data.artifacts.columns) == ["repo_full_name", "file_sha"]
    assert len(data.artifacts) == 4
    assert len(data.repos) == 4  # limit applies to every table


def test_gitskills_table_rejects_unknown_table(gitskills_db: Path) -> None:
    with pytest.raises(ValueError, match="Unknown GitSkills table"):
        load.gitskills_table("nope", db_path=gitskills_db)


def test_query_gitskills(gitskills_db: Path) -> None:
    df = load.query_gitskills(
        "SELECT file_sha, COUNT(*) AS copies FROM artifacts GROUP BY file_sha ORDER BY copies DESC",
        db_path=gitskills_db,
    )
    assert df.iloc[0]["file_sha"] == "sha-A"
    assert int(df.iloc[0]["copies"]) == 4


def test_missing_gitskills_raises_helpful_error(tmp_path: Path) -> None:
    with pytest.raises(load.DatasetNotFoundError, match="download_samples.py"):
        load.load_gitskills(tmp_path / "missing.db")


def test_load_specmine_default_tables(specmine_dir_fixture: Path) -> None:
    tables = load.load_specmine(specmine_dir_fixture)
    assert set(tables) == {"spec_files", "spec_content_features", "pull_requests", "pr_files"}
    assert len(tables["spec_files"]) == 8
    assert "spec_tool" in tables["spec_files"].columns


def test_load_specmine_explicit_tables_and_columns(specmine_dir_fixture: Path) -> None:
    tables = load.load_specmine(
        specmine_dir_fixture,
        tables=["spec_files"],
        columns={"spec_files": ["repo_name", "spec_tool"]},
    )
    assert list(tables) == ["spec_files"]
    assert list(tables["spec_files"].columns) == ["repo_name", "spec_tool"]


def test_load_specmine_missing_requested_table(specmine_dir_fixture: Path) -> None:
    with pytest.raises(load.DatasetNotFoundError, match="spec_links"):
        load.load_specmine(specmine_dir_fixture, tables=["spec_links"])


def test_load_specmine_empty_dir(tmp_path: Path) -> None:
    with pytest.raises(load.DatasetNotFoundError, match="No SpecMine"):
        load.load_specmine(tmp_path)


def test_read_specmine_text(tmp_path: Path) -> None:
    path = tmp_path / "specs.jsonl.gz"
    records = [
        {"file_url_sha16": f"{i:016x}", "repo_name": "r/a", "content": f"# Spec {i}"}
        for i in range(5)
    ]
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")
        handle.write("\n")  # blank line must be ignored
    got = list(load.read_specmine_text(path, limit=3))
    assert [r["content"] for r in got] == ["# Spec 0", "# Spec 1", "# Spec 2"]
    assert len(list(load.read_specmine_text(path))) == 5

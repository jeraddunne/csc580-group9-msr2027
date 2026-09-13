"""Loaders for the GitSkills (SQLite) and SpecMine (Parquet) samples.

Safety note (course rule): the datasets contain scripts and instructions that
were mined from public repositories. This module only reads them as data.
Nothing loaded here is ever executed, imported, or passed to a shell.
"""

from __future__ import annotations

import gzip
import json
import sqlite3
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from .config import gitskills_db_path, specmine_dir

GITSKILLS_TABLES = ("artifacts", "repos", "artifact_siblings", "mining_runs")

SPECMINE_CORE_TABLES = (
    "spec_files",
    "spec_content_features",
    "spec_links",
    "pull_requests",
    "pr_files",
    "kiro_files",
    "kiro_repos",
    "kiro_content_features",
    "repo_trees",
)
SPECMINE_LARGE_TABLES = (
    "spec_file_commits",
    "kiro_file_commits",
    "openspec_artifact_files",
    "openspec_code_refs",
)
SPECMINE_ALL_TABLES = SPECMINE_CORE_TABLES + SPECMINE_LARGE_TABLES

DOWNLOAD_HINT = "Run `python scripts/download_samples.py` (or `make data`) to fetch the samples."


class DatasetNotFoundError(FileNotFoundError):
    """Raised when a dataset sample is missing from data/samples."""


@dataclass
class GitSkillsData:
    """The four GitSkills tables as DataFrames."""

    artifacts: pd.DataFrame
    repos: pd.DataFrame
    artifact_siblings: pd.DataFrame
    mining_runs: pd.DataFrame

    def __iter__(self) -> Iterator[tuple[str, pd.DataFrame]]:
        for name in GITSKILLS_TABLES:
            yield name, getattr(self, name)


def _require_file(path: Path, what: str) -> Path:
    if not path.exists():
        raise DatasetNotFoundError(f"{what} not found at {path}. {DOWNLOAD_HINT}")
    return path


def _select(columns: Iterable[str] | None) -> str:
    if not columns:
        return "*"
    return ", ".join(f'"{c}"' for c in columns)


def query_gitskills(sql: str, db_path: Path | None = None, params: tuple = ()) -> pd.DataFrame:
    """Run a read-only SQL query against the GitSkills SQLite file."""
    path = _require_file(db_path or gitskills_db_path(), "GitSkills SQLite sample")
    uri = f"file:{path.as_posix()}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    try:
        return pd.read_sql_query(sql, con, params=params)
    finally:
        con.close()


def gitskills_table(
    table: str,
    db_path: Path | None = None,
    columns: Iterable[str] | None = None,
    limit: int | None = None,
) -> pd.DataFrame:
    """Load one GitSkills table, optionally restricting columns and row count."""
    if table not in GITSKILLS_TABLES:
        raise ValueError(f"Unknown GitSkills table {table!r}; expected one of {GITSKILLS_TABLES}")
    sql = f'SELECT {_select(columns)} FROM "{table}"'
    if limit is not None:
        sql += f" LIMIT {int(limit)}"
    return query_gitskills(sql, db_path=db_path)


def load_gitskills(
    db_path: Path | None = None,
    columns: dict[str, Iterable[str]] | None = None,
    limit: int | None = None,
    include_content: bool = False,
) -> GitSkillsData:
    """Load all four GitSkills tables.

    ``columns`` maps table name to the columns to keep. By default the large
    ``content`` text columns are dropped unless ``include_content`` is True.
    """
    columns = columns or {}
    frames: dict[str, pd.DataFrame] = {}
    for table in GITSKILLS_TABLES:
        cols = columns.get(table)
        frame = gitskills_table(table, db_path=db_path, columns=cols, limit=limit)
        if not include_content and cols is None and "content" in frame.columns:
            frame = frame.drop(columns=["content"])
        frames[table] = frame
    return GitSkillsData(**frames)


def specmine_table_path(table: str, directory: Path | None = None) -> Path:
    """Path of one SpecMine Parquet table."""
    return (directory or specmine_dir()) / f"{table}.parquet"


def load_specmine(
    directory: Path | None = None,
    tables: Iterable[str] | None = None,
    columns: dict[str, Iterable[str]] | None = None,
) -> dict[str, pd.DataFrame]:
    """Load SpecMine Parquet tables into a dict of DataFrames.

    Defaults to every core table that is present on disk. A table that is
    requested explicitly but missing raises DatasetNotFoundError.
    """
    directory = directory or specmine_dir()
    columns = columns or {}
    if tables is None:
        wanted = [t for t in SPECMINE_CORE_TABLES if specmine_table_path(t, directory).exists()]
        if not wanted:
            raise DatasetNotFoundError(
                f"No SpecMine Parquet files found in {directory}. {DOWNLOAD_HINT}"
            )
    else:
        wanted = list(tables)
    out: dict[str, pd.DataFrame] = {}
    for table in wanted:
        path = _require_file(specmine_table_path(table, directory), f"SpecMine table {table!r}")
        cols = list(columns[table]) if table in columns else None
        out[table] = pq.read_table(path, columns=cols).to_pandas()
    return out


def read_specmine_text(path: Path, limit: int | None = None) -> Iterator[dict]:
    """Stream records from specs.jsonl.gz or kiro_specs.jsonl.gz.

    Each record carries ``file_url_sha16``, ``repo_name``, ``file_path``,
    ``spec_tool``, ``spec_role``, and ``content`` (raw Markdown, read as data).
    """
    path = _require_file(Path(path), "SpecMine text file")
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for index, line in enumerate(handle):
            if limit is not None and index >= limit:
                break
            line = line.strip()
            if line:
                yield json.loads(line)

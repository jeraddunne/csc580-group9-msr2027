"""Shared fixtures: tiny offline replicas of the GitSkills and SpecMine samples.

The fixtures mirror the real schemas closely enough that every loader and
summary function runs unchanged against them. Nothing is downloaded.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

GITSKILLS_ARTIFACT_COLS = [
    "repo_full_name",
    "path",
    "filename",
    "location_class",
    "file_sha",
    "discovered_at",
    "dedup_primary",
    "content",
    "content_fetched",
    "content_sha_ok",
    "frontmatter_valid",
    "name",
    "description",
    "body_chars",
    "sibling_count",
    "sibling_bytes",
    "has_scripts",
    "has_references",
    "composition_fetched",
    "composition_truncated",
    "first_commit_at",
    "last_commit_at",
    "commit_count",
    "first_commit_author",
    "last_commit_author",
    "first_commit_author_type",
    "last_commit_author_type",
    "first_commit_message",
    "last_commit_message",
    "history_fetched",
]

# (repo, path, location_class, file_sha, dedup_primary, name, body_chars)
_ARTIFACT_BASE = [
    ("org-a/repo-1", ".claude/skills/deploy/SKILL.md", "canonical", "sha-A", 1, "deploy", 1200),
    ("org-a/repo-1", "skills/lint/SKILL.md", "skills-dir", "sha-B", 1, "lint", 800),
    ("org-b/repo-2", ".claude/skills/deploy/SKILL.md", "canonical", "sha-A", 0, "deploy", 1200),
    ("org-c/repo-3", "docs/SKILL.md", "other", "sha-C", 1, "docs", 300),
    ("org-c/repo-3", ".claude/skills/deploy/SKILL.md", "canonical", "sha-A", 0, "deploy", 1200),
    ("org-d/repo-4", "skills/test/SKILL.md", "skills-dir", "sha-D", 1, "test", 2500),
    ("org-d/repo-4", "skills/lint/SKILL.md", "skills-dir", "sha-B", 0, "lint", 800),
    ("org-e/repo-5", "tools/SKILL.md", "other", "sha-E", 1, "tools", 100),
    ("org-e/repo-5", ".claude/skills/review/SKILL.md", "canonical", "sha-F", 1, "review", 950),
    ("org-f/repo-6", ".claude/skills/deploy/SKILL.md", "canonical", "sha-A", 0, "deploy", 1200),
]


def _artifact_rows() -> list[tuple]:
    rows = []
    for repo, path, loc, sha, primary, name, chars in _ARTIFACT_BASE:
        rows.append(
            (
                repo,
                path,
                "SKILL.md",
                loc,
                sha,
                "2026-07-10T00:00:00Z",
                primary,
                f"---\nname: {name}\n---\nBody of {name}" if primary else None,
                1,
                1,
                1,
                name,
                f"{name} skill",
                chars,
                2 if primary else None,
                4096 if primary else None,
                1 if name == "deploy" else 0,
                0,
                1,
                0,
                "2026-01-01T00:00:00Z",
                "2026-06-01T00:00:00Z",
                3,
                "u-001",
                "u-002",
                "User",
                "User",
                "add skill",
                "update skill",
                1,
            )
        )
    return rows


_REPO_ROWS = [
    ("org-a/repo-1", "org-a", 120, 10, 0, "Python", "MIT", "d", "2025-11-01", "2026-07-01", 1),
    ("org-b/repo-2", "org-b", 5, 0, 0, "TypeScript", "MIT", "d", "2026-01-01", "2026-07-01", 1),
    ("org-c/repo-3", "org-c", 0, 0, 0, "Python", None, "d", "2026-02-01", "2026-07-01", 1),
    ("org-d/repo-4", "org-d", 300, 40, 0, "Rust", "Apache-2.0", "d", "2025-12-01", "2026-07-01", 1),
    ("org-e/repo-5", "org-e", 2, 0, 0, None, None, "d", "2026-03-01", "2026-07-01", 1),
    ("org-f/repo-6", "org-f", 15, 1, 0, "Python", "MIT", "d", "2026-04-01", "2026-07-01", 1),
]

_SIBLING_ROWS = [
    (
        "org-a/repo-1",
        ".claude/skills/deploy/SKILL.md",
        "deploy.sh",
        "file",
        120,
        "s1",
        "x",
        1,
        None,
    ),
    (
        "org-a/repo-1",
        ".claude/skills/deploy/SKILL.md",
        "README.md",
        "file",
        40,
        "s2",
        "notes",
        1,
        None,
    ),
    ("org-d/repo-4", "skills/test/SKILL.md", "fixtures", "dir", 0, "s3", None, 0, None),
]


@pytest.fixture
def gitskills_db(tmp_path: Path) -> Path:
    """A miniature GitSkills SQLite database with the four real tables."""
    db = tmp_path / "agent_skills_sample.db"
    con = sqlite3.connect(db)
    try:
        cols = ", ".join(GITSKILLS_ARTIFACT_COLS)
        placeholders = ", ".join("?" * len(GITSKILLS_ARTIFACT_COLS))
        con.execute(f"CREATE TABLE artifacts ({cols}, PRIMARY KEY (repo_full_name, path))")
        con.executemany(f"INSERT INTO artifacts VALUES ({placeholders})", _artifact_rows())
        con.execute(
            "CREATE TABLE repos (full_name, owner, stars, forks, is_fork, language, license, "
            "description, created_at, pushed_at, metadata_fetched)"
        )
        con.executemany("INSERT INTO repos VALUES (?,?,?,?,?,?,?,?,?,?,?)", _REPO_ROWS)
        con.execute(
            "CREATE TABLE artifact_siblings (repo_full_name, artifact_path, entry_name, "
            "entry_type, entry_size, entry_sha, content, content_fetched, skipped_reason)"
        )
        con.executemany("INSERT INTO artifact_siblings VALUES (?,?,?,?,?,?,?,?,?)", _SIBLING_ROWS)
        con.execute("CREATE TABLE mining_runs (query, started_at, finished_at, result_count)")
        con.execute(
            "INSERT INTO mining_runs VALUES (?,?,?,?)",
            ("filename:SKILL.md", "2026-07-01T00:00:00Z", "2026-07-02T00:00:00Z", 10),
        )
        con.commit()
    finally:
        con.close()
    return db


def _write_parquet(df: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(df, preserve_index=False), path)
    return path


@pytest.fixture
def specmine_dir_fixture(tmp_path: Path) -> Path:
    """A miniature SpecMine directory with four core Parquet tables."""
    d = tmp_path / "specmine"
    tools = ["kiro", "kiro", "openspec", "spec-kit", "kiro", "openspec", "generic", "kiro"]
    roles = [
        "feature",
        "feature",
        "change_proposal",
        "living",
        "feature",
        "archived",
        "na",
        "feature",
    ]
    spec_files = pd.DataFrame(
        {
            "file_url_sha16": [f"{i:016x}" for i in range(8)],
            "repo_name": ["r/a", "r/a", "r/b", "r/c", "r/c", "r/d", "r/e", "r/f"],
            "file_path": [f"specs/{i}.md" for i in range(8)],
            "spec_tool": tools,
            "spec_role": roles,
            "file_first_commit_at": ["2026-01-01T00:00:00Z"] * 8,
            "file_last_commit_at": ["2026-06-01T00:00:00Z"] * 8,
            "file_total_commits": [1, 3, 2, 5, 1, 1, 2, 4],
            "n_linked_prs": [0, 1, 0, 2, 0, 0, 1, 1],
            "n_code_links": [0, 4, 2, 6, 0, 1, 0, 3],
            "has_tasks": [1, 1, 0, 1, 0, 0, 0, 1],
            "has_plan": [0, 1, 0, 1, 0, 0, 0, 0],
            "has_design": [1, 1, 0, 0, 0, 0, 0, 1],
            "repo_stars": [500, 500, 20, 1500, 1500, 3, 0, 80],
            "repo_language": ["Python", "Python", "TypeScript", "Go", "Go", "Rust", None, "Python"],
        }
    )
    _write_parquet(spec_files, d / "spec_files.parquet")

    families = [
        "requirements",
        "requirements",
        "proposal",
        "spec",
        "requirements",
        "design",
        "spec",
        "requirements",
    ]
    features = pd.DataFrame(
        {
            "file_url_sha16": spec_files["file_url_sha16"],
            "n_bytes": [100, 2400, 900, 5000, 60, 300, 700, 3100],
            "n_lines": [5, 80, 30, 200, 3, 12, 25, 110],
            "n_words": [20, 400, 150, 900, 8, 50, 120, 520],
            "n_headings": [1, 6, 3, 12, 0, 2, 3, 8],
            "n_code_fences": [0, 2, 1, 4, 0, 0, 1, 3],
            "n_checkboxes": [0, 10, 0, 25, 0, 0, 0, 12],
            "n_checked": [0, 4, 0, 25, 0, 0, 0, 6],
            "n_shall": [0, 8, 0, 15, 0, 0, 2, 5],
            "n_gherkin": [0, 0, 0, 3, 0, 0, 0, 0],
            "n_todo": [0, 1, 0, 0, 0, 2, 0, 0],
            "has_ears": [0, 1, 0, 1, 0, 0, 0, 1],
            "has_gherkin": [0, 0, 0, 1, 0, 0, 0, 0],
            "has_user_story": [0, 1, 1, 1, 0, 0, 1, 1],
            "has_acceptance_criteria": [0, 1, 0, 1, 0, 0, 0, 1],
            "has_unfilled_placeholder": [1, 0, 0, 0, 1, 1, 0, 0],
            "is_tiny": [1, 0, 0, 0, 1, 0, 0, 0],
            "lang": ["en"] * 8,
            "content_family": families,
        }
    )
    _write_parquet(features, d / "spec_content_features.parquet")

    pull_requests = pd.DataFrame(
        {
            "pr_id": [1, 2, 3, 4, 5, 6],
            "repo_name": ["r/a", "r/a", "r/b", "r/c", "r/c", "r/d"],
            "tool": ["kiro", "kiro", "openspec", "spec-kit", "spec-kit", "openspec"],
            "number": [10, 11, 12, 13, 14, 15],
            "touches_code": [1, 0, 1, 1, 0, 0],
        }
    )
    _write_parquet(pull_requests, d / "pull_requests.parquet")

    pr_files = pd.DataFrame(
        {
            "pr_id": [1, 1, 2, 3, 3, 4, 5, 6],
            "file_path": [
                "specs/0.md",
                "src/a.py",
                "specs/1.md",
                "specs/2.md",
                "src/b.ts",
                "specs/3.md",
                "specs/4.md",
                "specs/5.md",
            ],
            "is_spec": [1, 0, 1, 1, 0, 1, 1, 1],
            "is_code": [0, 1, 0, 0, 1, 0, 0, 0],
        }
    )
    _write_parquet(pr_files, d / "pr_files.parquet")
    return d


@pytest.fixture
def data_root(
    tmp_path: Path, gitskills_db: Path, specmine_dir_fixture: Path, monkeypatch: pytest.MonkeyPatch
) -> Path:
    """Point MSR_DATA_DIR at a temp tree laid out like the repository."""
    root = tmp_path / "root"
    samples = root / "data" / "samples"
    samples.mkdir(parents=True)
    gitskills_db.rename(samples / "agent_skills_sample.db")
    specmine_dir_fixture.rename(samples / "specmine")
    monkeypatch.setenv("MSR_DATA_DIR", str(root))
    return root

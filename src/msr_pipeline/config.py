"""Filesystem layout and dataset locations.

All paths resolve relative to the repository root unless ``MSR_DATA_DIR`` is
set, in which case the data, results, and figures directories live under that
directory instead. Tests use the environment variable to work in a temp dir.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ENV_DATA_DIR = "MSR_DATA_DIR"

GITSKILLS_DB_NAME = "agent_skills_sample.db"
SPECMINE_DIR_NAME = "specmine"


def repo_root() -> Path:
    """Repository root, three levels above this file (src/msr_pipeline/config.py)."""
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Paths:
    """Resolved directories used by the pipeline."""

    ROOT: Path
    DATA: Path
    SAMPLES: Path
    RESULTS: Path
    FIGURES: Path

    def ensure_output_dirs(self) -> None:
        self.RESULTS.mkdir(parents=True, exist_ok=True)
        self.FIGURES.mkdir(parents=True, exist_ok=True)


def get_paths() -> Paths:
    """Return the current path layout, honouring ``MSR_DATA_DIR``."""
    root = repo_root()
    override = os.environ.get(ENV_DATA_DIR)
    base = Path(override).resolve() if override else root
    data = base / "data"
    return Paths(
        ROOT=root,
        DATA=data,
        SAMPLES=data / "samples",
        RESULTS=base / "results",
        FIGURES=base / "figures",
    )


def gitskills_db_path(paths: Paths | None = None) -> Path:
    """Location of the GitSkills SQLite sample."""
    paths = paths or get_paths()
    return paths.SAMPLES / GITSKILLS_DB_NAME


def specmine_dir(paths: Paths | None = None) -> Path:
    """Directory holding the SpecMine Parquet files."""
    paths = paths or get_paths()
    return paths.SAMPLES / SPECMINE_DIR_NAME

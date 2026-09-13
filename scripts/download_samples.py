#!/usr/bin/env python
"""Download the GitSkills and SpecMine dataset samples into data/samples.

The script only downloads and unpacks files. It never executes anything found
inside the archives (course rule: do not run untrusted scripts from the
datasets). Every file is recorded in data/samples/MANIFEST.json with its size,
SHA-256, source URL, and download time so the report can cite the exact
snapshot used.

Usage:
    python scripts/download_samples.py                     # both samples, core SpecMine tables
    python scripts/download_samples.py --dataset gitskills
    python scripts/download_samples.py --dataset specmine --all-specmine
    python scripts/download_samples.py --force             # re-download everything
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEST = ROOT / "data" / "samples"

GITSKILLS_REPO = "giuseppedestefanis/gitskills-sample"
GITSKILLS_RAW = f"https://raw.githubusercontent.com/{GITSKILLS_REPO}/HEAD"
GITSKILLS_ZIP = "agent_skills_sample.zip"
GITSKILLS_DB = "agent_skills_sample.db"

SPECMINE_REPO = "shyamagarwal13/specmine-official"
SPECMINE_RAW = f"https://raw.githubusercontent.com/{SPECMINE_REPO}/HEAD"
SPECMINE_CORE = [
    "spec_files",
    "spec_content_features",
    "spec_links",
    "pull_requests",
    "pr_files",
    "kiro_files",
    "kiro_repos",
    "kiro_content_features",
    "repo_trees",
]
SPECMINE_LARGE = [
    "spec_file_commits",
    "kiro_file_commits",
    "openspec_artifact_files",
    "openspec_code_refs",
]
SPECMINE_DOCS = ["DATA_DICTIONARY.md", "schema.sql", "sample_repos.txt"]
SPECMINE_TEXT = ["specs.jsonl.gz", "kiro_specs.jsonl.gz"]

CHUNK = 1 << 20  # 1 MiB


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def download(url: str, dest: Path, force: bool = False) -> bool:
    """Stream ``url`` to ``dest``. Returns True if a download happened."""
    if dest.exists() and not force:
        print(f"  skip   {dest.name} (exists, {human(dest.stat().st_size)})")
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        with requests.get(url, stream=True, timeout=60) as resp:
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code} for {url}")
            total = int(resp.headers.get("Content-Length") or 0)
            done = 0
            with tmp.open("wb") as out:
                for block in resp.iter_content(chunk_size=CHUNK):
                    out.write(block)
                    done += len(block)
                    if total:
                        pct = 100 * done / total
                        print(
                            f"\r  get    {dest.name} {human(done)} / {human(total)} ({pct:4.1f}%)",
                            end="",
                        )
                    else:
                        print(f"\r  get    {dest.name} {human(done)}", end="")
        print()
        tmp.replace(dest)
        return True
    except (requests.RequestException, RuntimeError) as exc:
        print(f"\n  ERROR  {dest.name}: {exc}")
        print(f"         Download it manually from {url} and place it at {dest}")
        if tmp.exists():
            tmp.unlink()
        return False


def manifest_entry(path: Path, url: str, extra: dict | None = None) -> dict:
    entry = {
        "file": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256_of(path),
        "source_url": url,
        "downloaded_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    if extra:
        entry.update(extra)
    return entry


def upstream_commit(repo: str) -> str | None:
    """Best-effort HEAD commit SHA of the upstream sample repository."""
    try:
        resp = requests.get(f"https://api.github.com/repos/{repo}/commits/HEAD", timeout=30)
        if resp.status_code == 200:
            return resp.json().get("sha")
    except requests.RequestException:
        pass
    return None


def fetch_gitskills(dest: Path, force: bool) -> list[dict]:
    print("GitSkills sample")
    zip_path = dest / GITSKILLS_ZIP
    db_path = dest / GITSKILLS_DB
    url = f"{GITSKILLS_RAW}/{GITSKILLS_ZIP}"
    entries: list[dict] = []
    if db_path.exists() and not force:
        print(f"  skip   {GITSKILLS_DB} (exists, {human(db_path.stat().st_size)})")
    else:
        download(url, zip_path, force=force)
        if not zip_path.exists():
            return entries
        print(f"  unzip  {GITSKILLS_ZIP}")
        with zipfile.ZipFile(zip_path) as archive:
            members = [m for m in archive.namelist() if m.endswith(".db")]
            if not members:
                print("  ERROR  no .db file inside the archive")
                return entries
            # Extract only the database, flattening any folder prefix. Nothing is executed.
            with archive.open(members[0]) as src, db_path.open("wb") as out:
                shutil.copyfileobj(src, out, CHUNK)
    commit = upstream_commit(GITSKILLS_REPO)
    if zip_path.exists():
        entries.append(manifest_entry(zip_path, url, {"upstream_commit": commit}))
    if db_path.exists():
        entries.append(
            manifest_entry(
                db_path, url, {"upstream_commit": commit, "extracted_from": GITSKILLS_ZIP}
            )
        )
        verify_sqlite(db_path)
    return entries


def verify_sqlite(db_path: Path) -> None:
    print(f"  verify {db_path.name}")
    con = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    try:
        for table in ("artifacts", "repos", "artifact_siblings", "mining_runs"):
            n = con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            print(f"         {table:18s} {n:>10,} rows")
    except sqlite3.DatabaseError as exc:
        print(f"  ERROR  SQLite verification failed: {exc}")
    finally:
        con.close()


def fetch_specmine(dest: Path, force: bool, everything: bool) -> list[dict]:
    print("SpecMine sample")
    sm = dest / "specmine"
    tables = SPECMINE_CORE + (SPECMINE_LARGE if everything else [])
    files = [f"data/{t}.parquet" for t in tables] + SPECMINE_DOCS
    if everything:
        files += SPECMINE_TEXT
    commit = upstream_commit(SPECMINE_REPO)
    entries: list[dict] = []
    for rel in files:
        url = f"{SPECMINE_RAW}/{rel}"
        target = sm / Path(rel).name
        download(url, target, force=force)
        if target.exists():
            entries.append(manifest_entry(target, url, {"upstream_commit": commit}))
    present = [t for t in tables if (sm / f"{t}.parquet").exists()]
    print(f"  {len(present)}/{len(tables)} Parquet tables present in {sm}")
    return entries


def write_manifest(dest: Path, entries: list[dict]) -> None:
    path = dest / "MANIFEST.json"
    existing: dict[str, dict] = {}
    if path.exists():
        try:
            for entry in json.loads(path.read_text(encoding="utf-8")).get("files", []):
                existing[entry["file"]] = entry
        except (json.JSONDecodeError, KeyError, TypeError):
            existing = {}
    for entry in entries:
        existing[entry["file"]] = entry
    payload = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "note": "Dataset samples for the MSR 2027 Mining Challenge (July 2026 snapshot).",
        "files": sorted(existing.values(), key=lambda e: e["file"]),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Manifest written to {path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--dataset", choices=("gitskills", "specmine", "all"), default="all")
    parser.add_argument(
        "--all-specmine",
        action="store_true",
        help="Also fetch the large commit-history and OpenSpec tables and the raw spec text.",
    )
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST, help="Target directory.")
    parser.add_argument("--force", action="store_true", help="Re-download existing files.")
    args = parser.parse_args(argv)

    dest: Path = args.dest.resolve()
    dest.mkdir(parents=True, exist_ok=True)
    entries: list[dict] = []
    if args.dataset in ("gitskills", "all"):
        entries += fetch_gitskills(dest, args.force)
    if args.dataset in ("specmine", "all"):
        entries += fetch_specmine(dest, args.force, args.all_specmine)
    write_manifest(dest, entries)
    return 0 if entries else 1


if __name__ == "__main__":
    sys.exit(main())

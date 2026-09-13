#!/usr/bin/env bash
# One-command reproduction for the Group 9 MSR 2027 pipeline.
#
# Creates a virtual environment, installs the package, downloads the dataset
# samples if they are missing, regenerates the exploratory tables and figures,
# and runs the test suite. Safe to re-run; each step skips work already done.
#
# Usage:
#   ./run_pipeline.sh              # full run
#   SKIP_DATA=1 ./run_pipeline.sh  # skip the download step
#   SKIP_TESTS=1 ./run_pipeline.sh # skip the tests

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PY="${PY:-python}"
VENV="${VENV:-.venv}"

log() { printf '\n==> %s\n' "$*"; }

if [ ! -d "$VENV" ]; then
  log "Creating virtual environment in $VENV"
  "$PY" -m venv "$VENV"
fi

if [ -f "$VENV/Scripts/activate" ]; then
  # Windows (Git Bash / MSYS)
  # shellcheck disable=SC1091
  source "$VENV/Scripts/activate"
elif [ -f "$VENV/bin/activate" ]; then
  # Linux / macOS
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
else
  echo "Could not find an activate script in $VENV" >&2
  exit 1
fi

log "Installing the package and development tools"
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -e ".[dev]"

if [ "${SKIP_DATA:-0}" != "1" ]; then
  if [ -f data/samples/agent_skills_sample.db ] && [ -f data/samples/specmine/spec_files.parquet ]; then
    log "Dataset samples already present; skipping download"
  else
    log "Downloading dataset samples (this can take several minutes)"
    python scripts/download_samples.py --dataset all
  fi
fi

log "Regenerating exploratory tables and figures"
python -m msr_pipeline explore --dataset all

if [ "${SKIP_TESTS:-0}" != "1" ]; then
  log "Running the test suite"
  python -m pytest -q
fi

log "Done"
echo "  Tables:  $ROOT/results/"
echo "  Figures: $ROOT/figures/"
echo "  Data:    $ROOT/data/samples/ (see data/samples/MANIFEST.json for provenance)"

#!/usr/bin/env bash
# Clean-environment check run by the documented container (Dockerfile, issue #71).
# Stages: sample, lint and tests, analysis compared with the committed results, spec checks.
# Every stage runs even if an earlier one fails; the exit code is 0 only if all pass.
# Output is counts and file names only; no dataset text is printed.

set -uo pipefail
cd "$(dirname "$0")/.."

declare -a SUMMARY=()
failed=0
stage() { printf '\n==> %s\n' "$*"; }
record() {
  local name=$1 rc=$2
  if [ "$rc" -eq 0 ]; then SUMMARY+=("PASS  $name"); else SUMMARY+=("FAIL  $name (exit $rc)"); failed=1; fi
}

stage "Environment"
python - <<'EOF'
import platform
import numpy, pandas, scipy, statsmodels
print(f"{platform.platform()}; Python {platform.python_version()}")
print(f"pandas {pandas.__version__}, numpy {numpy.__version__}, scipy {scipy.__version__}, "
      f"statsmodels {statsmodels.__version__}")
EOF
echo "commit: ${GIT_COMMIT:-unknown}"

stage "1/4 GitSkills sample (downloaded once into the data volume)"
python scripts/download_samples.py --dataset gitskills
rc=$?; record "sample downloaded and verified" $rc
if [ $rc -ne 0 ]; then
  echo "The sample is required for every later stage; stopping." >&2
  printf '\n%s\n' "${SUMMARY[@]}"; exit 1
fi

stage "2/4 Lint and automated tests"
ruff check . && ruff format --check . && python -m pytest -q -p no:cacheprovider
record "lint and tests" $?

stage "3/4 P-01 analysis, compared with the committed results"
python scripts/fresh_run_check.py --steps "docker build, then docker run (docs/REPRODUCE.md)"
record "analysis reproduces results/ (build/fresh_run/REPORT.md)" $?

stage "4/4 RESEARCH_SPEC.md acceptance checks"
python scripts/verify_spec.py --no-write
record "spec checks: no FAIL" $?

stage "Summary"
printf '%s\n' "${SUMMARY[@]}"
exit $failed

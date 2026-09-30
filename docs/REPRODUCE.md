# Reproducing the results

This page lists every tested way to rerun the P-01 pipeline, what each one proves, and the recorded results. It answers these assignment requirements:

- Scope rule, reproducibility: "A new user should be able to install dependencies, run the pipeline, and reproduce the main tables or figures."
- Final submission checklist: "The main pipeline runs from a clean environment or documented container" and "The primary tables and figures can be regenerated."
- Sprint 3 acceptance: "A new user can follow the README to reproduce the primary results."
- `RESEARCH_SPEC.md` NFR-01 (reproducible from a clean environment) and NFR-02 (deterministic outputs).

Reproduction shows that the same code and data give the same numbers anywhere. It does not show that the numbers are right; that is validation, at the end of this page.

## Pick a way

| Way | For | How | What a pass proves | Time |
|---|---|---|---|---|
| Documented container | Graders, anyone with Docker | [below](#documented-container) | A pinned, clean Linux environment reproduces `results/` | About 4 minutes the first time, 2 after |
| README on Linux, macOS, or Git Bash | A new developer | The [README Setup block](../README.md#setup) | The README's own instructions work on a fresh machine | About 5 minutes |
| Windows double-click files | Members without git | [windows/README.md](../windows/README.md) | The no-git path works; counts as S1-10 when run by a non-author on their own machine | About 5 minutes plus the Python install |
| GitHub runner | Anyone, nothing installed | Actions > **Container check** > Run workflow | The container passes on a machine none of us controls | About 5 minutes |
| CI | Every pull request, automatic | `.github/workflows/ci.yml` | Lint and tests pass on Linux with Python 3.11 and 3.12 (no dataset) | About 1 minute |

## Documented container

Needs only Docker. Python and every package are pinned to the versions in `results/ANALYSIS_MANIFEST.json` (`docker/constraints.txt`).

```bash
# straight from GitHub, no clone needed
docker build -t group9-p01 https://github.com/jeraddunne/csc580-group9-msr2027.git#main
docker run --rm -v group9-data:/app/data/samples group9-p01

# or from a clone, recording the commit in the report
docker build --build-arg GIT_COMMIT=$(git rev-parse --short HEAD) -t group9-p01 .
docker run --rm -v group9-data:/app/data/samples group9-p01
```

The run (`docker/check.sh`) prints four stages and a summary, and exits 0 only if all pass:

1. Downloads the GitSkills sample into the `group9-data` volume (about 83 MB, once) and verifies its SHA-256.
2. Runs lint and the test suite.
3. Reruns the analysis into `build/fresh_run/` and compares it with the committed `results/` (`scripts/fresh_run_check.py`).
4. Runs the `RESEARCH_SPEC.md` acceptance checks without writing any file.

To keep the report, drop `--rm`, add `--name check`, then `docker cp check:/app/build/fresh_run/REPORT.md .` and `docker rm check`. To free the disk space afterwards: `docker volume rm group9-data` and `docker image rm group9-p01`.

Nothing from the dataset is executed; the scanner reads text only, and the container runs as an unprivileged user.

## What "reproduced" means

`scripts/fresh_run_check.py` compares every table the analysis writes with the committed one:

- **Identical** apart from line endings (git stores LF, Windows writes CRLF).
- **Equal within 1e-9 relative**: every difference is a number, and no number differs by more than one part in a billion. Maths libraries round the last digits differently on different operating systems. On Linux, even with the same package versions, `rq2_negbin.csv` differs from the Windows run by at most 3.1e-10 relative; its incidence rate ratios are unchanged at the printed precision. The report names the files that matched this way and the largest difference.
- **DIFFERS**: anything else, including a different row count, a changed label, or a number beyond the tolerance.

Figures are not compared byte for byte, because image rendering depends on fonts and platform. They are drawn from the same tables, so matching tables mean matching figures. `results/ANALYSIS_MANIFEST.json` always differs, because it records the run's time and package versions.

## Recorded runs

| Date | Environment | Who | Python and key packages | Result | Evidence |
|---|---|---|---|---|---|
| 2026-09-23 | Windows 11, author's clone | Jerad (author) | 3.12.10; pandas 3.0.5, numpy 2.5.3, statsmodels 0.15.0 | NFR-02 pass: two runs identical, committed results equal a fresh run | `results/spec_verification.csv` |
| 2026-09-30 | Windows 11, ZIP of the branch, `windows/*.bat` | Jerad (author) | 3.12.10, same packages | 14 of 14 tables identical | PR #70 |
| 2026-09-30 | Docker `python:3.12.10-slim-bookworm`, pinned (this page) | Jerad (author) | 3.12.10, same packages | All four stages pass: 164 tests; 14 of 14 tables match (13 identical, `rq2_negbin.csv` within 3.1e-10); spec checks 22 pass, 3 blocked, 4 manual, 0 fail | PR for #71 |
| 2026-09-30 | Docker `ubuntu:26.04`, README followed literally, `main` at 446285a | Jerad (author) | 3.14.4; pandas 3.0.6 | **Failed at the first step**: `make setup` called `python`, which stock Ubuntu does not have. With `PY=python3` the rest ran and 163 tests passed; 13 of 14 tables byte-identical, `rq2_negbin.csv` differed. Fixed in #71 | Issue #71 |
| 2026-09-30 | Docker `ubuntu:26.04`, README followed literally, #71 branch | Jerad (author) | 3.14.4; latest packages | All four README steps pass with no workaround in 3.1 minutes; 164 tests pass; 14 of 14 tables match (13 identical, `rq2_negbin.csv` within 3.1e-10, the same Linux rounding as the pinned container), so newer package versions did not change any result | PR for #71 |
| pending | A member's own computer, not the author | a non-author | | Required for S1-10 and each review's gemba walk | Guided task |

Every run so far is by the author. The sprint reviews need one by another member on their own machine; the container and the GitHub runner are the fallback evidence if that cannot happen.

## Using WSL instead of Docker

Ubuntu under WSL works like any Linux machine, but stock Ubuntu lacks two packages the README needs:

```bash
sudo apt install -y python3-venv make git
cd ~                    # clone into the Linux home, not /mnt/c: faster, and outside OneDrive
git clone https://github.com/jeraddunne/csc580-group9-msr2027.git && cd csc580-group9-msr2027
make setup && make data && make test && make pipeline
.venv/bin/python scripts/fresh_run_check.py    # reruns into build/fresh_run/ and compares with results/
```

## What these checks do not cover: validation

| Question | How it is answered | Status on 2026-09-30 |
|---|---|---|
| Do the parsing, matching, and metric functions do what they claim? | 164 automated tests, on every pull request | Automated, passing |
| Does the pipeline meet its written requirements? | `make verify-spec` over the 29 requirements in `RESEARCH_SPEC.md` | 23 pass, 0 fail; 3 wait on labels |
| Is a rule match a real risk (precision per rule)? | VR-01: Jerad labels 147 signal items from the guideline | Human; due 2026-10-13 |
| Are linked variants really copies of each other? | VR-03: Jerad labels 58 lineage pairs, round 2 at least 14 days later | Human; due 2026-10-13, round 2 by 2026-10-27 |
| Do two raters agree on drift? | VR-02: Jerad and Leticia each label 18 drift pairs; Cohen's kappa | Human; due 2026-10-16 |
| Scores | `python scripts/annotation_kit.py score` | Automated once the labels exist; due 2026-10-27 |

No container can do the labelling: it is the human judgement the rubric asks for. `docs/validation/README.md` has the protocol.

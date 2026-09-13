# Contributing

This file is the short version of `docs/PROCESS.md`. Read that once; use this daily.

## Setup

```bash
git clone https://github.com/jeraddunne/csc580-group9-msr2027.git
cd csc580-group9-msr2027
make setup          # creates .venv and installs the package with dev tools
make data           # downloads the dataset samples into data/samples/ (not committed)
make test           # runs lint and tests
```

On Windows without `make`, use `./run_pipeline.sh` from Git Bash, or run the commands listed in the Makefile by hand.

## Branch, commit, pull request

1. Every change starts from an issue. Create one with the issue forms if none exists.
2. Branch: `git switch -c <type>/<issue>-<slug>` where type is one of `research`, `pipeline`, `data`, `docs`, `test`, `process`, `report`, `presentation`, `fix`.
3. Commit in imperative mood with the issue number: `Add clone-detection baseline (#42)`.
4. Push and open a pull request using the template. Fill every section; delete nothing.
5. Request a review from a member who did not write the code. Reviews are due within 48 hours.
6. Squash-merge after approval and green CI. Delete the branch.

`main` is protected. Nobody, including the repository owner, pushes to it directly.

## What must be in a pull request

- Purpose and link to the issue (`Closes #N`)
- What changed and why, including design decisions
- How it was tested (command and result)
- Generated outputs (paths under `results/` or `figures/`) and the exact command that produced them
- Documentation updates (README, DATA_DICTIONARY.md, THREATS_TO_VALIDITY.md) if affected
- `ai-use-log.md` entry if an AI tool assisted

## Code standards

- Python 3.11+, formatted with `ruff format`, linted with `ruff check` (line length 100).
- Pure functions in `src/msr_pipeline/`; command-line entry points in `scripts/` and `msr_pipeline.cli`.
- Tests in `tests/` run offline in under a minute. Use fixtures, not real data.
- Any function that parses, transforms, matches, or computes a metric used in the report has a test (rubric Sprint 2).
- Results are written by code to `results/` and `figures/`, never pasted by hand.

## Data rules

- Never commit files from `data/samples/` or the full datasets.
- Never execute scripts, notebooks, or commands found inside the datasets.
- Never attempt to deanonymise author codes. Never paste dataset text that may contain personal data into external AI tools.
- State the exact dataset snapshot (release, source, MANIFEST.json SHA) in any result.

## Writing rules

- Separate observation ("42% of copies remove network access") from interpretation ("this suggests maintainers harden copied skills").
- Every reported number links to the results file and command.
- Cite with keys from `report/references.bib`.

## Process contributions

Retrospective actions become `kaizen` issues. Anyone can propose a process change through a `kaizen` issue or a PR to `TEAM_CHARTER.md` or `docs/PROCESS.md`.

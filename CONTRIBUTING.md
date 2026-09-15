# Contributing

This is a solo course project run by Jerad Dunne (ADR-0005). This file is the short version of `docs/PROCESS.md`: the rules the author follows, and what an external reviewer (the instructor or a classmate) should know.

## Setup

```bash
git clone https://github.com/jeraddunne/csc580-group9-msr2027.git
cd csc580-group9-msr2027
make setup          # creates .venv and installs the package with dev tools
make data           # downloads the dataset samples into data/samples/ (not committed)
make test           # runs lint and tests
make pipeline       # runs the P-01 analysis
```

On Windows without `make`, use `./run_pipeline.sh` from Git Bash, or run the commands in the Makefile by hand.

## Branch, commit, pull request

1. Every change starts from an issue.
2. Branch: `git switch -c <type>/<issue>-<slug>`, where type is one of `research`, `pipeline`, `data`, `docs`, `test`, `process`, `report`, `presentation`, `fix`.
3. Commit in imperative mood with the issue number: `Add variant linking (#21)`.
4. Push and open a pull request using the template. Fill every section.
5. Self-review after at least 12 hours using the template's self-review checklist, and leave a review comment saying what was verified.
6. Squash-merge once the checklist is complete and CI is green (once workflows are enabled). Delete the branch.

`main` is protected: a pull request is required, merges are squash only, and force pushes are blocked.

## What must be in a pull request

- Purpose and link to the issue (`Closes #N`)
- What changed and why, including design decisions
- How it was tested (command and result)
- Generated outputs under `results/` or `figures/` and the exact command that produced them
- Documentation updates (README, DATA_DICTIONARY.md, THREATS_TO_VALIDITY.md) if affected
- An `ai-use-log.md` entry if an AI tool assisted

## External reviewers

Reviews from the instructor or classmates are welcome, especially on the validation, report, and release pull requests. To review: pull the branch, run `make test` (and `make pipeline` if the pipeline changed), check that the outputs match the stated command, and leave a review on the pull request. Suggestions for other changes are best opened as issues first.

## Code standards

- Python 3.11+, formatted with `ruff format`, linted with `ruff check` (line length 100).
- Pure functions in `src/msr_pipeline/`; command-line entry points in `scripts/` and `msr_pipeline.cli`.
- Tests in `tests/` run offline in under a minute. Use fixtures, not real data.
- Any function that parses, transforms, matches, or computes a metric used in the report has a test.
- Results are written by code to `results/` and `figures/`, never pasted by hand.

## Data rules

- Never commit files from `data/samples/` or the full datasets.
- Never execute scripts, notebooks, or commands found inside the datasets.
- Never attempt to deanonymize author codes, and never name repositories or accounts in outputs.
- Never paste dataset text that may contain personal data into external AI tools.
- State the exact dataset snapshot (release, source, MANIFEST.json hash) for any result.

## Writing rules

- Separate observation from interpretation.
- Every reported number links to the results file and command.
- Cite with keys from `report/references.bib`.

## Process changes

Retrospective actions become `kaizen` issues. Changes to the working agreement or process are made by pull request to `TEAM_CHARTER.md` or `docs/PROCESS.md` and recorded in `docs/workspace/DECISION_LOG.md`.

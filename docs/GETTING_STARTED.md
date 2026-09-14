# Getting started (reproducing or reviewing this project)

Time needed: about 10 minutes of reading, then 20 to 30 minutes of setup. This project is run solo by Jerad Dunne (ADR-0005); this page is written for a reader, reviewer, or grader.

## 1. Understand the project

1. `README.md`: the research question, status, and commands.
2. `RESEARCH_QUESTION.md` and `docs/proposals/P-01-jerad-dunne-skill-risk-propagation.md`: what is asked, why, and how.
3. `docs/decisions/ADR-0004-topic-selection.md` and `ADR-0005-solo-execution.md`: why this topic, and how a solo project substitutes for team practices.
4. The MSR 2027 Mining Challenge page: https://2027.msrconf.org/track/msr-2027-mining-challenge

## 2. Reproduce the results

Prerequisites: Git, Python 3.11 or newer. On Windows, use **Git Bash**. Clone to a folder outside OneDrive or iCloud; sync tools interfere with git working trees.

```bash
git clone https://github.com/jeraddunne/csc580-group9-msr2027.git
cd csc580-group9-msr2027
make setup                          # or: python -m venv .venv && . .venv/Scripts/activate && pip install -e ".[dev]"
make test                           # offline tests and lint; must be green
make data                           # downloads the GitSkills and SpecMine samples
make pipeline                       # P-01 analysis: results/rq*_*.csv, results/sensitivity_*.csv, figures/rq*_*.png
```

If `make` is missing, `./run_pipeline.sh` runs setup, download, and tests.

To check reproduction, run the pipeline on a clean clone and compare with the committed outputs:

```bash
git status --short results figures   # expect no changes other than timestamps
```

The dataset snapshot used for committed results is recorded in `data/samples/MANIFEST.json` (sha256 of each file).

## 3. Where the evidence is

| Need | Go to |
|---|---|
| What is due when | `docs/sprints/README.md` |
| Sprint evidence (planning, review, retrospective) | `docs/sprints/<sprint>/` |
| Findings with reproducible evidence | `docs/workspace/FINDINGS_LOG.md` |
| Decisions, big and small | `docs/workspace/DECISION_LOG.md`, `docs/decisions/` |
| Validation guideline and protocol | `docs/validation/` |
| Process metrics | `docs/lean-six-sigma/metrics/DASHBOARD.md` |
| Review history | Pull requests, including self-review comments and any external reviews |
| AI assistance and verification | `ai-use-log.md` |
| Report draft | `report/draft.md` |

## 4. Reviewing a pull request

External reviews are welcome, especially on the validation, report, and release pull requests.

1. Check out the branch: `gh pr checkout <number>`.
2. Run `make test`, and `make pipeline` if the pipeline changed.
3. Confirm the outputs match the command stated in the pull request.
4. Check that text separates observation from interpretation, and that numbers are traceable to a results file.
5. Leave a review on the pull request with what you verified.

## 5. The author's weekly routine

- Work-log entries on Monday, Wednesday, and Friday in `docs/meeting-notes/`.
- Thursday self check-in with the metrics dashboard.
- Every change through a pull request, self-reviewed after at least 12 hours.
- AI use logged in `ai-use-log.md` in the same pull request as the work.

## 6. Questions

Open an issue in the repository, or contact the author through the course channel.

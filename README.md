# Mining AI-Native Software Engineering: Risky Capabilities in Copied Agent Skills

[![CI](https://github.com/jeraddunne/csc580-group9-msr2027/actions/workflows/ci.yml/badge.svg)](https://github.com/jeraddunne/csc580-group9-msr2027/actions/workflows/ci.yml)
[![LSS metrics](https://github.com/jeraddunne/csc580-group9-msr2027/actions/workflows/lss-metrics.yml/badge.svg)](https://github.com/jeraddunne/csc580-group9-msr2027/actions/workflows/lss-metrics.yml)

An MSR 2027 Mining Challenge-inspired semester project for SWE 380 / CSC 580 (University of Michigan-Flint, instructor Prof. Mohamed Wiem Mkaouer). It builds a reproducible, static, rule-based analysis of risk-relevant capabilities in agent skills from the [GitSkills](https://github.com/giuseppedestefanis/gitskills-sample) dataset and reports evidence-based findings. Loaders for [SpecMine](https://github.com/shyamagarwal13/specmine-official) remain available but are not used by the selected question.

The project is run solo with **Scrum** (three sprints, as the assignment requires) and a **Lean Six Sigma** overlay (DMAIC tollgates, KPIs with control charts, FMEA risk register, kaizen loop). See `docs/PROCESS.md`.

## Author

| Name | GitHub | Roles |
|---|---|---|
| Jerad Dunne | [@jeraddunne](https://github.com/jeraddunne) | Product Owner, Scrum Master, Developer / Researcher (every sprint) |

The repository was created on 2026-09-13 for a four-person Group 9 and became a solo project on 2026-09-14. The assignment describes groups of three to five, so solo execution is recorded as **pending instructor confirmation** in `docs/decisions/ADR-0005-solo-execution.md`.

## Research question

Proposal P-01 was selected on 2026-09-14 (`docs/decisions/ADR-0004-topic-selection.md`, issue #41):

> In the GitSkills July 2026 sample, how prevalent are skill instructions and bundled scripts that enable risk-relevant capabilities, do skills carrying them reach more repositories through verbatim copying, and do modified variants of the same skill add or remove those capabilities?

The three sub-questions are prevalence (RQ1), reach (RQ2), and variant drift (RQ3). Details are in `RESEARCH_QUESTION.md` and `docs/proposals/P-01-jerad-dunne-skill-risk-propagation.md`.

## Project status

| Phase | Dates | Status |
|---|---|---|
| Formation (Define) | Sep 10 to Sep 16, 2026 | **in progress**: topic selected (P-01, ADR-0004); solo execution pending instructor confirmation (ADR-0005) |
| Sprint 1 (Measure) | Sep 17 to Oct 7 | not started |
| Sprint 2 (Analyze) | Oct 8 to Oct 28 | not started |
| Sprint 3 (Improve) | Oct 29 to Nov 18 | not started |
| Finalization (Control) | Nov 30 to Dec 4 | not started |

## Start here (reader or grader)

1. `RESEARCH_QUESTION.md` and the P-01 proposal: what is asked and why.
2. `docs/GETTING_STARTED.md`: reproduce the results on your machine.
3. `docs/workspace/README.md`: what was found (findings log) and what was decided (decision log).
4. `docs/sprints/`: planning, review, and retrospective evidence for each sprint.
5. `ai-use-log.md`: how AI assistance was used and verified.

## Setup

Requirements: Git, Python 3.11 or newer, and the GitHub CLI (`gh`) for the process scripts. `make` is optional.

```bash
git clone https://github.com/jeraddunne/csc580-group9-msr2027.git
cd csc580-group9-msr2027
make setup          # python -m venv .venv && pip install -e ".[dev]"
make data           # downloads dataset samples into data/samples/ (not committed)
make test           # ruff + pytest, runs offline
make pipeline       # P-01 analysis: results/rq*_*.csv, results/sensitivity_*.csv, figures/rq*_*.png
```

Without `make`: `./run_pipeline.sh` runs the setup, download, and test steps from Git Bash or a Linux shell.

## Dataset acquisition

Both datasets come from the MSR 2027 Mining Challenge (July 2026 snapshot). The samples used here are downloaded by `scripts/download_samples.py`. The full datasets (a 41 GB SQLite file for GitSkills and a MySQL dump for SpecMine) are on Zenodo and Hugging Face. Provenance, licensing, and ethics rules are in `data/README.md`. The exact snapshot and file hashes used for any result are recorded in `data/samples/MANIFEST.json` and cited in the report.

Never execute scripts, notebooks, or commands found inside the datasets.

## Execution

| Command | What it does |
|---|---|
| `python -m msr_pipeline info` | Shows configured paths and which samples are present |
| `python -m msr_pipeline analyze` | Full P-01 analysis: RQ1 prevalence, RQ2 reach statistics, RQ3 variant drift, sensitivity checks; writes `results/rq*_*.csv`, `results/sensitivity_*.csv`, `figures/rq*_*.png` |
| `make pipeline` | Runs the P-01 analysis end to end |
| `python -m msr_pipeline risk-pilot` | Original P-01 pilot scan of the GitSkills sample (static text only) |
| `python scripts/annotation_kit.py sample` | Draws the stratified validation sample |
| `python scripts/annotation_kit.py sheet` | Builds annotation sheets for labelling and re-labelling |
| `python scripts/annotation_kit.py score` | Scores labels: precision per rule, recall estimate, Cohen's kappa |
| `python -m msr_pipeline explore --dataset all` | Regenerates exploratory tables and figures |
| `python -m msr_pipeline query --dataset gitskills --sql "..."` | Ad-hoc read-only SQL against the GitSkills sample |
| `python scripts/lss_metrics.py` | Computes process KPIs from GitHub and renders `docs/lean-six-sigma/metrics/DASHBOARD.md` |
| `python scripts/workspace_digest.py` | Rebuilds `docs/workspace/DIGEST.md` from finding and decision issues |
| `make reproduce` | Fresh end-to-end run: data, explore, test |

Retired: `python scripts/tally_votes.py` (topic vote, superseded by ADR-0005).

## Outputs

- `results/` tables (CSV) generated by code, including `rq*_*.csv` and `sensitivity_*.csv`
- `figures/` figures (PNG) generated by code
- `report/draft.md` living report; `report/final.pdf` attached to the release
- `docs/lean-six-sigma/metrics/DASHBOARD.md` weekly process metrics

## Repository map

```
.
├── README.md, RESEARCH_QUESTION.md, DATA_DICTIONARY.md, THREATS_TO_VALIDITY.md
├── TEAM_CHARTER.md (solo working agreement), PROJECT_PLAN.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, LICENSE
├── ai-use-log.md                 AI assistance disclosure log (required by the rubric)
├── project.yml                   single source of truth: author, dates, roles, KPI targets
├── pyproject.toml, requirements*.txt, Makefile, run_pipeline.sh
├── src/msr_pipeline/             loaders, scanner, analysis, metrics, CLI
├── tests/                        offline unit tests
├── scripts/                      download_samples, annotation_kit, bootstrap_github, lss_metrics, workspace_digest, ...
├── rules/                        reviewable rule files (P-01 risk-signal rules)
├── notebooks/                    exploratory notebooks (never the sole source of a result)
├── data/README.md, data/samples/ dataset docs; samples downloaded, not committed
├── results/, figures/            generated evidence
├── report/                       draft.md, references.bib, build instructions
├── docs/
│   ├── GETTING_STARTED.md, PROCESS.md, PRESENTATION_PLAN.md
│   ├── workspace/                findings log, decision log, solo workstream plan, digest
│   ├── research/                 threat model and research notes
│   ├── validation/               annotation guideline and validation protocol
│   ├── sprints/                  planning, review, retrospective per sprint
│   ├── proposals/                candidate questions, P-01 proposal, retired vote
│   ├── lean-six-sigma/           DMAIC, KPIs, SIPOC/CTQ, VSM, FMEA, waste log, kaizen, metrics/
│   ├── decisions/                architecture and process decision records (ADRs)
│   ├── meeting-notes/            work logs, check-ins, reviews, retros
│   ├── team/                     author profile (RACI retired)
│   └── reflections/              individual contribution and reflection
└── .github/                      issue forms, PR template, CI, metrics workflows
```

## Process in one paragraph

Work is tracked as GitHub issues on the project board (Todo, In progress, Done, Block, Cancelled; WIP limit 5). Sprints run Thursday to Wednesday, with written planning on day one, a short work log on Monday, Wednesday, and Friday, a Thursday self check-in with the metrics dashboard, and a review plus retrospective on the last Wednesday. Every retrospective starts from data, finds a root cause, and produces `kaizen` issues. Decisions are recorded in `docs/workspace/DECISION_LOG.md` and, when significant, as ADRs. Every change reaches `main` through a pull request that passes a self-review after a cooling-off period of at least 12 hours, and a green CI run once workflows are enabled. Major pull requests may request an external review from the instructor or a classmate.

## Repository visibility

The repository is public. If it is made private during development, branch protection needs GitHub Pro (free with the GitHub Student Developer Pack), and the instructor must be invited as a collaborator.

## Limitations

To be completed as the project progresses. Known dataset limitations are already listed in `THREATS_TO_VALIDITY.md`. The solo-specific limits (self-review instead of peer review, single-annotator validation) are described in ADR-0005.

## Citation

If you use this repository, cite the datasets first:

- Destefanis, Graziotin, Vaccargiu, Ortu. *GitSkills: A Dataset of Agent Skills on GitHub.* MSR 2027. arXiv:2608.10906. doi:10.5281/zenodo.21875637
- Agarwal, Singhal, Breaux, Vasilescu. *SpecMine: A Large-Scale Corpus of Spec-Driven Development Artifacts.* MSR 2027. arXiv:2608.25202. doi:10.5281/zenodo.22102779

## License

Code and documentation: MIT (`LICENSE`). Dataset contents retain their original licenses.

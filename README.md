# Mining AI-Native Software Engineering: Risky Capabilities in Copied Agent Skills

[![CI](https://github.com/jeraddunne/csc580-group9-msr2027/actions/workflows/ci.yml/badge.svg)](https://github.com/jeraddunne/csc580-group9-msr2027/actions/workflows/ci.yml)
[![LSS metrics](https://github.com/jeraddunne/csc580-group9-msr2027/actions/workflows/lss-metrics.yml/badge.svg)](https://github.com/jeraddunne/csc580-group9-msr2027/actions/workflows/lss-metrics.yml)

An MSR 2027 Mining Challenge-inspired semester project for SWE 380 / CSC 580 (University of Michigan-Flint, instructor Prof. Mohamed Wiem Mkaouer), carried out by Group 9. It builds a reproducible, static, rule-based analysis of risk-relevant capabilities in agent skills from the [GitSkills](https://github.com/giuseppedestefanis/gitskills-sample) dataset and reports evidence-based findings. Loaders for [SpecMine](https://github.com/shyamagarwal13/specmine-official) remain available but are not used by the selected question.

The group works with **Scrum** (three sprints, as the assignment requires) and a **Lean Six Sigma** overlay (DMAIC tollgates, KPIs with control charts, FMEA risk register, kaizen loop). See `docs/PROCESS.md`.

## Team

| Member | GitHub | Sprint 1 role (proposed) |
|---|---|---|
| Leticia Aderhold | [@angel06la](https://github.com/angel06la) | Scrum Master, Developer / Researcher |
| Jerad Dunne | [@jeraddunne](https://github.com/jeraddunne) | Product Owner, Developer / Researcher |
| Allie Hodges | [@AllieHgs](https://github.com/AllieHgs) | Developer / Researcher |
| Hina Kramer | [@hinak786](https://github.com/hinak786) | Developer / Researcher |

Roles rotate every sprint (`TEAM_CHARTER.md` section 3) and are confirmed at the kickoff on 2026-09-16. Everyone is a Developer / Researcher every sprint. The repository briefly ran as a solo project on 2026-09-14 (ADR-0005); the four-person group was reinstated on 2026-09-15 (`docs/decisions/ADR-0006-group-reinstated.md`).

## Research question

Proposal P-01 was selected on 2026-09-14 (`docs/decisions/ADR-0004-topic-selection.md`, issue #41):

> In the GitSkills July 2026 sample, how prevalent are skill instructions and bundled scripts that enable risk-relevant capabilities, do skills carrying them reach more repositories through verbatim copying, and do modified variants of the same skill add or remove those capabilities?

The three sub-questions are prevalence (RQ1), reach (RQ2), and variant drift (RQ3). Details are in `RESEARCH_QUESTION.md` and `docs/proposals/P-01-jerad-dunne-skill-risk-propagation.md`. Any member may open a Decision needed issue to revisit the topic before Sprint 1 planning on 2026-09-17.

## Project status

| Phase | Dates | Status |
|---|---|---|
| Formation (Define) | Sep 10 to Sep 16, 2026 | **in progress**: topic selected (P-01); group reinstated (ADR-0006); members onboarding and signing the charter |
| Sprint 1 (Measure) | Sep 17 to Oct 7 | not started |
| Sprint 2 (Analyze) | Oct 8 to Oct 28 | not started |
| Sprint 3 (Improve) | Oct 29 to Nov 18 | not started |
| Finalization (Control) | Nov 30 to Dec 4 | not started |

## New member? Start here

1. Accept the repository invitation: https://github.com/jeraddunne/csc580-group9-msr2027/invitations
2. Read `docs/GETTING_STARTED.md` and follow the onboarding path (setup, onboarding issue, first pull request).
3. Sign `TEAM_CHARTER.md` section 14 and add your profile under `docs/team/` in that first pull request; another member reviews it.
4. If you are a second rater for validation, follow `docs/validation/README.md`.
5. Bookmark the team workspace, `docs/workspace/README.md`: sign up for work, log findings, and see what the team decided.

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
| `python scripts/annotation_kit.py sheet --rater <id> --round 1` | Builds your label sheets and reading packets |
| `python scripts/annotation_kit.py ui --rater <id> --round 1` | Writes local labelling pages to `data/annotations/work/` |
| `python scripts/annotation_kit.py import <downloaded.csv>` | Validates and saves labels downloaded from a labelling page |
| `python scripts/annotation_kit.py score` | Scores labels: precision per rule, recall estimate, Cohen's kappa |
| `python -m msr_pipeline explore --dataset all` | Regenerates exploratory tables and figures |
| `python -m msr_pipeline query --dataset gitskills --sql "..."` | Ad-hoc read-only SQL against the GitSkills sample |
| `python scripts/lss_metrics.py` | Computes process KPIs from GitHub and renders `docs/lean-six-sigma/metrics/DASHBOARD.md` |
| `python scripts/workspace_digest.py` | Rebuilds `docs/workspace/DIGEST.md` from sign-up, finding, and decision issues |
| `make reproduce` | Fresh end-to-end run: data, explore, test |

Retired: `python scripts/tally_votes.py` (the topic vote was not held; P-01 was selected directly, ADR-0004).

## Outputs

- `results/` tables (CSV) generated by code, including `rq*_*.csv` and `sensitivity_*.csv`
- `figures/` figures (PNG) generated by code
- `report/draft.md` living report; `report/final.pdf` attached to the release
- `docs/lean-six-sigma/metrics/DASHBOARD.md` weekly process metrics

## Repository map

```
.
├── README.md, RESEARCH_QUESTION.md, DATA_DICTIONARY.md, THREATS_TO_VALIDITY.md
├── TEAM_CHARTER.md (working agreement v2.0), PROJECT_PLAN.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, LICENSE
├── ai-use-log.md                 AI assistance disclosure log (required by the rubric)
├── project.yml                   single source of truth: team, dates, roles, raters, KPI targets
├── pyproject.toml, requirements*.txt, Makefile, run_pipeline.sh
├── src/msr_pipeline/             loaders, scanner, analysis, validation, metrics, CLI
├── tests/                        offline unit tests
├── scripts/                      download_samples, annotation_kit, bootstrap_github, lss_metrics, workspace_digest, ...
├── rules/                        reviewable rule files (P-01 risk-signal rules)
├── notebooks/                    exploratory notebooks (never the sole source of a result)
├── data/README.md, data/samples/ dataset docs; samples downloaded, not committed
├── data/annotations/             validation samples and label files (reading packets stay local)
├── results/, figures/            generated evidence
├── report/                       draft.md, references.bib, build instructions
├── docs/
│   ├── GETTING_STARTED.md, PROCESS.md, PRESENTATION_PLAN.md
│   ├── workspace/                work sign-up, findings log, decision log, digest
│   ├── research/                 threat model and research notes
│   ├── validation/               annotation guideline and second-rater protocol
│   ├── sprints/                  planning, review, retrospective per sprint
│   ├── proposals/                candidate questions, P-01 proposal, retired vote
│   ├── lean-six-sigma/           DMAIC, KPIs, SIPOC/CTQ, VSM, FMEA, waste log, kaizen, metrics/
│   ├── decisions/                architecture and process decision records (ADRs)
│   ├── meeting-notes/            stand-ups, check-ins, reviews, retros
│   ├── team/                     member profiles, RACI
│   └── reflections/              individual contribution and reflection (one per member)
└── .github/                      issue forms, PR template, CI, metrics workflows
```

## Process in one paragraph

Work is tracked as GitHub issues on the project board (Todo, In progress, Done, Block, Cancelled; WIP limit 5). Sprints run Thursday to Wednesday, with planning on day one, written stand-ups on Monday, Wednesday, and Friday, a Thursday check-in with the metrics dashboard, and a review plus retrospective on the last Wednesday. Members choose work through the Work sign-up form before each planning. Every retrospective starts from data, finds a root cause, and produces `kaizen` issues. Decisions are recorded in `docs/workspace/DECISION_LOG.md` and, when significant, as ADRs. Every change reaches `main` through a pull request approved by a member other than the author, with a green CI run.

## Repository visibility

The repository is public. If it is made private during development, branch protection needs GitHub Pro (free with the GitHub Student Developer Pack), and the instructor must be invited as a collaborator.

## Limitations

To be completed as the project progresses. Known dataset and validation limitations are listed in `THREATS_TO_VALIDITY.md`.

## Citation

If you use this repository, cite the datasets first:

- Destefanis, Graziotin, Vaccargiu, Ortu. *GitSkills: A Dataset of Agent Skills on GitHub.* MSR 2027. arXiv:2608.10906. doi:10.5281/zenodo.21875637
- Agarwal, Singhal, Breaux, Vasilescu. *SpecMine: A Large-Scale Corpus of Spec-Driven Development Artifacts.* MSR 2027. arXiv:2608.25202. doi:10.5281/zenodo.22102779

## License

Code and documentation: MIT (`LICENSE`). Dataset contents retain their original licenses.

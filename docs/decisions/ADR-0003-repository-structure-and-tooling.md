# ADR-0003: Repository structure, tooling, and branch policy

- **Status:** Accepted
- **Date:** 2026-09-13
- **Deciders:** Jerad Dunne (proposed); to be ratified at kickoff
- **Decision issue:** Formation issue "Repository practice"
- **Affects research question / method / scope:** no

## Context

The rubric prescribes a repository layout (README, RESEARCH_QUESTION, DATA_DICTIONARY, THREATS_TO_VALIDITY, LICENSE, requirements or pyproject, Makefile or run_pipeline.sh, src, tests, notebooks, data, results, figures, report, docs/decisions, docs/meeting-notes, ai-use-log) and requires branch protection or an equivalent review practice, reviewed pull requests, milestones, issues, and a documented release. The datasets are SQLite (GitSkills) and Parquet (SpecMine). The team uses Windows, macOS, and Linux.

## Options considered

1. **Language:** Python (pandas, pyarrow, DuckDB, matplotlib) vs R vs mixed. Python is shared by all members and has first-class SQLite and Parquet support.
2. **Layout:** flat scripts vs src layout with an installable package. The src layout keeps tests honest and makes `python -m msr_pipeline` the single execution path.
3. **Quality gates:** none vs ruff plus pytest in GitHub Actions on every PR.
4. **Repository visibility:** private vs public. Branch protection rulesets are free only on public repositories for personal accounts; the MSR open-science norm favours public; no personal data is stored in the repository.
5. **Merge policy:** merge commits vs squash. Squash keeps `main` readable as one commit per issue.

## Decision

- Python 3.11+, src layout, package `msr_pipeline`, CLI via `python -m msr_pipeline`, `Makefile` plus `run_pipeline.sh`.
- ruff (lint and format) and pytest in CI; CI must pass to merge.
- Public repository under `jeraddunne/csc580-group9-msr2027` with a ruleset on `main`: no direct pushes, one approving review, conversation resolution, no force pushes or deletion. Squash merges only; branches deleted on merge.
- Dataset samples are downloaded by script and never committed; `data/samples/MANIFEST.json` records hashes for the report's snapshot statement.
- `project.yml` is the single source of truth for team, dates, roles, and KPI targets; scripts read it.

## Consequences

- Positive: the layout matches the rubric exactly; reproducibility is enforced by CI and the gemba walk; the story of the project is readable from `main` history, issues, and PRs.
- Negative / risks: public visibility means care with personal data (no emails in the repository; onboarding form says so). Squash merges lose intermediate commits (acceptable; PR history keeps them).
- Follow-up issues: add required status checks to the ruleset once the CI job names are stable; invite members and instructor.

## Revisit trigger

If the team needs a private repository (instructor request), switch visibility and replace the ruleset with a documented "review before merge" practice, which the rubric allows as an equivalent.

# Formation planning (Define phase)

How to use: keep this list current until 2026-09-16. Every row needs a completion date. Move anything unfinished into Sprint 1 planning with a note. The project became solo on 2026-09-14 (ADR-0005); rows that only applied to a group are marked retired.

Period: Thu 2026-09-10 to Wed 2026-09-16. Rubric weight: 10% (topic selection, research question, initial backlog).
Owner of every row: Jerad Dunne.

## Formation goal

Inspect the datasets, select and document the research question, and start Sprint 1 with a repository, a signed solo working agreement, a topic brief, and an estimated initial backlog.

## Checklist

| # | Item | Evidence | Target date | Done date | Status |
|---|---|---|---|---|---|
| F1 | Repository created from the recommended structure, public, instructor has access | Repo URL | 2026-09-13 | 2026-09-13 | [x] |
| F2 | Onboarding issues for every member | Retired (ADR-0005) | - | - | n/a |
| F3 | Author profile in `docs/team/` | `docs/team/jerad-dunne.md` | 2026-09-16 | | [ ] |
| F4 | Solo working agreement (`TEAM_CHARTER.md`) signed | Signature row | 2026-09-16 | | [ ] |
| F5 | Dataset samples downloaded and inspected (`scripts/download_samples.py`) | `data/samples/MANIFEST.json`; findings F-006 to F-012 | 2026-09-14 | | [ ] |
| F6 | Topic proposal written | Issue #41, `docs/proposals/P-01-jerad-dunne-skill-risk-propagation.md` | 2026-09-14 | | [ ] |
| F7 | Ballots cast | Retired (ADR-0005) | - | - | n/a |
| F8 | Tally run | Retired (ADR-0005) | - | - | n/a |
| F9 | Topic decision record | `docs/decisions/ADR-0004-topic-selection.md` | 2026-09-14 | | [ ] |
| F10 | Solo execution recorded; instructor confirmation requested | `docs/decisions/ADR-0005-solo-execution.md`; date the request was sent | 2026-09-16 | | [ ] |
| F11 | `RESEARCH_QUESTION.md` filled: question, motivation, unit of analysis, population, variables, competing explanation | File merged under the self-review protocol | 2026-09-17 | | [ ] |
| F12 | Repository settings: branch protection on `main` (PR required, 0 approvals, squash only), labels, milestones with due dates | Link to rules | 2026-09-14 | | [ ] |
| F13 | GitHub Project board created from the instructor template (statuses Todo, In progress, Done, Block, Cancelled; Sprint and Estimate fields) and linked to the repo | Project URL in README | 2026-09-16 | | [ ] |
| F14 | Initial backlog: Sprint 1 rubric deliverables as issues with acceptance criteria, estimates, milestone `Sprint 1` | Milestone shows issues | 2026-09-16 | | [ ] |
| F15 | Roles confirmed: Jerad Dunne holds all roles | ADR-0005 | 2026-09-14 | | [ ] |
| F16 | Topic brief submitted to the instructor (question, dataset, approach, backlog link, solo request) | Submission record | 2026-09-16 | | [ ] |
| F17 | FMEA risk register reviewed, including solo risks | `docs/lean-six-sigma/FMEA_RISK_REGISTER.md` | 2026-09-16 | | [ ] |
| F18 | AI-use log up to date | `ai-use-log.md` | 2026-09-16 | | [ ] |

## Define phase exit criteria (DMAIC)

- [ ] Problem statement and research question are written in one sentence each and recorded in ADR-0004 and `RESEARCH_QUESTION.md`.
- [ ] Customer of the work is named (instructor rubric criteria, and the MSR research community as secondary).
- [ ] Critical-to-quality items are listed in `docs/lean-six-sigma/KPIS.md` and match the rubric quality criteria.
- [ ] Scope is bounded: dataset, sample, and what is out of scope are recorded in `RESEARCH_QUESTION.md`.
- [ ] SIPOC for the pipeline exists (`docs/lean-six-sigma/SIPOC_AND_CTQ.md`).

## Notes and carry-over

- Items not done by 2026-09-16 (list issue numbers):
- Reason and new date:

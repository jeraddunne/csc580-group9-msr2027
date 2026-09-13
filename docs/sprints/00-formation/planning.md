# Formation planning (Define phase)

How to use: the acting Scrum Master keeps this list current until 2026-09-16. Every row needs an owner and a completion date. Move anything unfinished into Sprint 1 planning with a note.

Period: Thu 2026-09-10 to Wed 2026-09-16. Rubric weight: 10% (topic selection, research question, initial backlog).

## Formation goal

Form the team, inspect both datasets, propose and vote on a research question, and leave Sprint 1 with a repository, a signed charter, an approved topic brief, and an estimated initial backlog.

## Checklist

| # | Item | Evidence | Owner | Target date | Done date | Status |
|---|---|---|---|---|---|---|
| F1 | Repository created from the recommended structure, public, instructor has access | Repo URL, collaborator list | Jerad Dunne | 2026-09-13 | | [ ] |
| F2 | Every member has completed an onboarding issue (`onboarding` label) with GitHub handle, availability, strengths | 4 closed onboarding issues | Each member | 2026-09-14 | | [ ] |
| F3 | Every member has accepted the repository invitation and pushed at least one commit (profile file in `docs/team/`) | Contributor graph | Each member | 2026-09-14 | | [ ] |
| F4 | Team charter (`TEAM_CHARTER.md`) read and signed by all four | Signature block | Each member | 2026-09-16 | | [ ] |
| F5 | Both dataset samples downloaded and inspected (`scripts/download_samples.py`), notes in `data/README.md` | Data notes, one exploratory query each | Each member | 2026-09-14 | | [ ] |
| F6 | Proposals submitted (at least one per member, `proposal` label, issue form) | Proposal issues | Each member | 2026-09-14 23:59 | | [ ] |
| F7 | Ballots cast (`docs/proposals/votes/ballots/<handle>.yml`) | 4 ballot files | Each member | 2026-09-15 23:59 | | [ ] |
| F8 | Tally run (`scripts/tally_votes.py`), `docs/proposals/RESULTS.md` committed | RESULTS.md | Leticia Aderhold | 2026-09-16 | | [ ] |
| F9 | Decision ADR written (next free number in `docs/decisions/`, research question selection) | ADR merged | Jerad Dunne | 2026-09-16 | | [ ] |
| F10 | `RESEARCH_QUESTION.md` filled: question, motivation, unit of analysis, population, variables, competing explanation | File merged via reviewed PR | Product Owner | 2026-09-16 | | [ ] |
| F11 | Repository settings: branch protection on `main` (1 review, CI required), labels, milestones with due dates | Link to rules | Jerad Dunne | 2026-09-13 | | [ ] |
| F12 | GitHub Project board created from the instructor template (views Backlog, Board, Current iteration, Roadmap, My items; statuses Todo, In progress, Done, Block, Cancelled; Iteration and Estimate fields) and linked to the repo | Project URL in README | Jerad Dunne | 2026-09-16 | | [ ] |
| F13 | Initial backlog: Sprint 1 rubric deliverables turned into issues with acceptance criteria, owners, estimates, milestone `Sprint 1` | Milestone shows issues | Product Owner | 2026-09-16 | | [ ] |
| F14 | Roles confirmed for all sprints (see `docs/sprints/README.md`) | Kickoff notes | Team | 2026-09-16 | | [ ] |
| F15 | Topic brief submitted to the instructor (question, dataset, approach, initial backlog link) | Submission record | Product Owner | 2026-09-16 | | [ ] |
| F16 | FMEA risk register started with at least 5 risks (`docs/lean-six-sigma/FMEA_RISK_REGISTER.md`) | File merged | Scrum Master | 2026-09-16 | | [ ] |
| F17 | AI-use log started (`ai-use-log.md`) with entries for any generated content so far | File | Each member | 2026-09-16 | | [ ] |

## Define phase exit criteria (DMAIC)

- [ ] Problem statement and research question are written in one sentence each and agreed by all four.
- [ ] Customer of the work is named (instructor rubric criteria, and the MSR research community as secondary).
- [ ] Critical-to-quality items are listed in `docs/lean-six-sigma/KPIS.md` and match the rubric quality criteria.
- [ ] Scope is bounded: dataset(s), sample size, and what is out of scope are recorded in `RESEARCH_QUESTION.md`.
- [ ] SIPOC for the pipeline exists (`docs/lean-six-sigma/SIPOC_AND_CTQ.md`).

## Notes and carry-over

- Items not done by 2026-09-16 (list issue numbers):
- Reason and new date:

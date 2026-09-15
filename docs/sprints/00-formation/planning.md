# Formation planning (Define phase)

How to use: the Formation Scrum Master keeps this list current until 2026-09-16. Every row needs an owner and a completion date. Move anything unfinished into Sprint 1 planning with a note. The project was briefly solo on 2026-09-14 (ADR-0005); the four-person group was reinstated on 2026-09-15 (ADR-0006), so the group rows are active again.

Period: Thu 2026-09-10 to Wed 2026-09-16. Rubric weight: 10% (topic selection, research question, initial backlog).
Product Owner and Scrum Master for formation: Jerad Dunne.

## Formation goal

Form the team, inspect the data, confirm the research question, and leave Sprint 1 with a repository, a charter signed by all four members, an approved topic brief, and an estimated initial backlog.

## Checklist

| # | Item | Evidence | Owner | Target date | Done date | Status |
|---|---|---|---|---|---|---|
| F1 | Repository created from the recommended structure, public, instructor has access | Repo URL | Jerad Dunne | 2026-09-13 | 2026-09-13 | [x] |
| F2 | Every member accepted the repository invitation and has board write access | Collaborator list | Each member | 2026-09-16 | | [ ] |
| F3 | Every member completed a Team member onboarding issue | 4 closed onboarding issues | Each member | 2026-09-16 | | [ ] |
| F4 | Every member added a profile in `docs/team/` in their first pull request | 4 profiles | Each member | 2026-09-17 | | [ ] |
| F5 | Team charter v2.0 (`TEAM_CHARTER.md`) signed by all four, each in their own onboarding pull request | Section 14 signature rows | Each member | 2026-09-17 | | [ ] |
| F6 | Dataset sample downloaded and inspected (`make data`) | `data/samples/MANIFEST.json`; findings F-006 to F-012 | Jerad Dunne; each member runs `make data` | 2026-09-16 | | [ ] |
| F7 | Topic proposal written | Issue #41, `docs/proposals/P-01-jerad-dunne-skill-risk-propagation.md` | Jerad Dunne | 2026-09-14 | | [ ] |
| F8 | Ballots cast and tally run | Retired: P-01 was selected directly (ADR-0004) | - | - | - | n/a |
| F9 | Topic decision record | `docs/decisions/ADR-0004-topic-selection.md` | Jerad Dunne | 2026-09-14 | | [ ] |
| F10 | Group reinstated and recorded | `docs/decisions/ADR-0006-group-reinstated.md` | Jerad Dunne | 2026-09-15 | | [ ] |
| F11 | P-01 confirmed by the group, or a Decision needed issue opened to revisit it | Kickoff notes or decision issue | Each member | 2026-09-17 | | [ ] |
| F12 | `RESEARCH_QUESTION.md` filled: question, motivation, unit of analysis, population, variables, competing explanation | File merged after review by another member | Product Owner | 2026-09-17 | | [ ] |
| F13 | Repository settings: branch protection on `main` (PR required, 1 approving review, squash only), labels, milestones with due dates | Link to rules | Jerad Dunne | 2026-09-15 | | [ ] |
| F14 | GitHub Project board created from the instructor template (statuses Todo, In progress, Done, Block, Cancelled; Sprint and Estimate fields) and linked to the repo | Project URL in README | Jerad Dunne | 2026-09-16 | | [ ] |
| F15 | Initial backlog: Sprint 1 rubric deliverables as issues with acceptance criteria, owners, estimates, milestone `Sprint 1` | Milestone shows issues | Product Owner | 2026-09-16 | | [ ] |
| F16 | Roles confirmed for all sprints (see `docs/sprints/README.md`) | Kickoff notes, `project.yml` | Team | 2026-09-16 | | [ ] |
| F17 | Second rater chosen for each validation kind (signals, lineage, drift) | `docs/workspace/WORK_SIGNUP.md` section 6 | Team | 2026-09-16 | | [ ] |
| F18 | Sprint 1 work sign-ups filed | Work sign-up issues | Each member | 2026-09-16 | | [ ] |
| F19 | Topic brief submitted to the instructor (question, dataset, approach, team, backlog link) | Submission record | Product Owner | 2026-09-16 | | [ ] |
| F20 | FMEA risk register reviewed, including group risks | `docs/lean-six-sigma/FMEA_RISK_REGISTER.md` | Scrum Master | 2026-09-16 | | [ ] |
| F21 | AI-use log up to date | `ai-use-log.md` | Each member | 2026-09-16 | | [ ] |

## Define phase exit criteria (DMAIC)

- [ ] Problem statement and research question are written in one sentence each and agreed by all four.
- [ ] Customer of the work is named (instructor rubric criteria, and the MSR research community as secondary).
- [ ] Critical-to-quality items are listed in `docs/lean-six-sigma/KPIS.md` and match the rubric quality criteria.
- [ ] Scope is bounded: dataset, sample, and what is out of scope are recorded in `RESEARCH_QUESTION.md`.
- [ ] SIPOC for the pipeline exists (`docs/lean-six-sigma/SIPOC_AND_CTQ.md`).

## Notes and carry-over

- Items not done by 2026-09-16 (list issue numbers):
- Reason and new date:

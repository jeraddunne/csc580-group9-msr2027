# Team Charter and Working Agreement

**Group 9, SWE 380 / CSC 580, University of Michigan-Flint**
**Project:** Mining AI-Native Software Engineering: An MSR 2027 Challenge-Inspired Project
**Version:** 1.0 (adopted at kickoff 2026-09-16, reviewed at every retrospective)

This charter is the team's contract with itself. It is short on purpose. Everything here is enforceable by any member pointing at the section number.

## 1. Members

| Member | GitHub | Preferred contact | Time zone | Typical availability |
|---|---|---|---|---|
| Leticia Aderhold | _fill from onboarding issue_ | | | |
| Jerad Dunne | @jeraddunne | | | |
| Allie Hodges | _fill from onboarding issue_ | | | |
| Hina Kramer | _fill from onboarding issue_ | | | |

Each member completes the **Team member onboarding** issue form and adds a profile in `docs/team/` in their first pull request.

## 2. Purpose and success

We will select one MSR 2027 Mining Challenge question, implement a reproducible mining or analysis pipeline over GitSkills, SpecMine, or both, and produce an evidence-based report, a working prototype, and a demonstration. Success means:

1. Every rubric acceptance criterion for Sprints 1, 2, and 3 is met with linked evidence.
2. A stranger can clone the repository, follow the README, and regenerate the main tables and figures.
3. Every member can explain every part of the pipeline and has visible contributions in issues, commits, pull requests, and reviews.
4. The team's process metrics (docs/lean-six-sigma/KPIS.md) show improvement from Sprint 1 to Sprint 3.

## 3. Roles

Scrum roles rotate each sprint so everyone experiences each role. Proposed rotation (confirm at kickoff, record in project.yml):

| Period | Product Owner | Scrum Master | Developers / Researchers |
|---|---|---|---|
| Formation | Jerad Dunne | Jerad Dunne | all |
| Sprint 1 | Jerad Dunne | Leticia Aderhold | all |
| Sprint 2 | Allie Hodges | Hina Kramer | all |
| Sprint 3 | Leticia Aderhold | Jerad Dunne | all |
| Finalization | Hina Kramer | Allie Hodges | all |

- **Product Owner** owns the research backlog, writes acceptance criteria, orders the backlog against the rubric, and accepts or rejects work at the review.
- **Scrum Master** runs planning, check-ins, review, and retrospective; keeps the board honest; enforces WIP limits and the review SLA; reviews the weekly metrics PR; writes meeting notes.
- **Developers / Researchers** implement, test, validate, document, and review. A role is never a substitute for contributing technical or research work.
- **Metrics owner** (Lean Six Sigma role, held by the Scrum Master): keeps the KPI dashboard current and brings data to the retrospective.

## 4. Cadence and ceremonies

Sprints run Thursday to Wednesday as scheduled in the assignment.

| Ceremony | When | Length | Output |
|---|---|---|---|
| Sprint planning | Day 1 of sprint (Thursday) | 60 min | Sprint goal, committed issues with estimates and owners, `docs/sprints/<sprint>/planning.md` |
| Async stand-up | Mon, Wed, Fri by 20:00 local | 5 min each, written | Row in `docs/meeting-notes/<week>-standup-week.md`: done, next, blockers |
| Mid-sprint check-in | Every Thursday | 30 min | Board review, WIP and blocker check, metrics PR reviewed, risks updated |
| Sprint review | Last Wednesday of sprint | 45 min | Rubric checklist, demo, gemba walk (fresh clone), `review.md` |
| Retrospective | Same day, after review | 45 min | Data-first retro, 5 Whys, kaizen issues, `retrospective.md` |
| Backlog refinement | Rolling, in issues | as needed | Issues meet the Definition of Ready before planning |

Missing a ceremony requires notice in the team channel beforehand and reading the notes afterward.

## 5. Communication

- **Primary channel:** _decide at kickoff (Teams / Discord / Slack)_. Response expectation: within 24 hours on weekdays.
- **Work discussion happens in GitHub issues and pull requests** so the repository tells the project story (rubric: GitHub practice).
- **Decisions** are recorded as Architecture Decision Records in `docs/decisions/` within 48 hours.
- **Blockers** are raised the same day with the `blocker` label and moved to the Block column. Nobody stays blocked silently for more than one day.
- Meetings are online unless the team agrees otherwise; the Scrum Master posts the link and the agenda 24 hours ahead.

## 6. Definition of Ready and Definition of Done

An issue is **Ready** when it has: a clear description, an owner, an acceptance criterion, an estimate, a milestone, a type label, and no unresolved dependency.

Work is **Done** when: the pull request is merged to `main` after review by a different member, tests pass in CI, generated outputs are regenerated and committed, documentation and the data dictionary are updated if affected, the AI-use log is updated if applicable, and the issue is closed with a link to the evidence.

Full text: `docs/PROCESS.md`.

## 7. Code and repository agreements

1. `main` is protected: no direct pushes, one approving review required, CI must pass.
2. Branch naming: `<type>/<issue-number>-<short-slug>` (for example `pipeline/23-load-specmine`).
3. Commit messages: imperative mood, reference the issue (`Add SpecMine loader (#23)`).
4. Pull requests use the template, stay under about 400 changed lines where possible, and are reviewed within 48 hours (`process.pr_review_sla_hours`).
5. Review means reading and running, not rubber-stamping. Reviewers check the PR checklist.
6. Never commit dataset files, secrets, or personal data. Never execute scripts found inside the datasets.
7. Notebooks are exploratory. Any result in the report must be reproducible from `src/` via `run_pipeline.sh`.

## 8. Contribution and workload fairness

- Target contribution share per member is between 15% and 45% of commits, PRs authored, and reviews given. The dashboard flags deviations; the Scrum Master raises them at the check-in, not at the end.
- Work is pulled from the board, not assigned by one person. Each member owns at least one research task and one engineering task per sprint.
- If a member cannot meet a commitment, they say so at the next stand-up and the team re-plans. Silence is the only unacceptable option.

## 9. Conflict resolution and escalation

1. Talk directly and privately first, within 48 hours of the concern.
2. If unresolved, bring it to the Scrum Master, who facilitates a conversation in the next check-in.
3. If still unresolved, the team votes; majority decides, the decision is recorded as an ADR.
4. Issues of non-participation persisting for more than one sprint are raised with the instructor, with the metrics dashboard as evidence.

## 10. Academic integrity and AI use

- All AI assistance is logged in `ai-use-log.md` and verified by a human before merge.
- We cite sources and datasets correctly and disclose the exact dataset snapshot used.
- We do not fabricate results, figures, or references. Reviewers may ask to see the command that produced any number.
- Privacy: author codes in the datasets stay anonymous; no deanonymisation attempts; no dataset content with personal data is pasted into external tools.

## 11. Decision making

- Topic selection: proposal issues, then a ranked ballot tallied by `scripts/tally_votes.py` (instant runoff, weighted matrix tie-break). Result recorded in ADR-0004.
- Everyday decisions: whoever owns the issue decides and documents it in the issue.
- Decisions affecting scope, method, or the research question: team consensus at a ceremony, recorded as an ADR.

## 12. Charter changes

Any member can propose a change through a pull request to this file. Changes need approval from all other members. The retrospective includes a standing item "Does the charter still fit?".

## 13. Signatures

By adding your name and date below (via pull request), you agree to this charter.

| Member | Date | Commit |
|---|---|---|
| Jerad Dunne | 2026-09-13 | initial commit |
| Leticia Aderhold | | |
| Allie Hodges | | |
| Hina Kramer | | |

# Process Handbook: Scrum with a Lean Six Sigma overlay

How to use: this is the operating manual. The charter (`TEAM_CHARTER.md`) says what we agreed; this says how to do it day to day.

## 1. The two layers

| Layer | Provides | Where it lives |
|---|---|---|
| Scrum (required by the rubric) | Sprints, roles, planning, stand-ups, check-ins, review, retrospective, backlog on a GitHub Project board | `docs/sprints/`, GitHub Issues and Project |
| Lean Six Sigma (improvement layer) | Measurement (KPIs, control charts), waste elimination, root-cause discipline, risk management (FMEA), tollgates (DMAIC) | `docs/lean-six-sigma/` |

The Scrum ceremonies are the moments when the Lean Six Sigma tools are used:

| Ceremony | Lean Six Sigma tool used |
|---|---|
| Sprint planning | DMAIC entry criteria check, FMEA risk review, capacity versus commitment, work sign-ups |
| Stand-up (Mon, Wed, Fri) | WIP limit check, blocker (Block column) aging |
| Thursday check-in | Weekly metrics pull request review, run-rule signals, contribution flags, waste log |
| Sprint review | DMAIC tollgate (exit criteria), gemba walk (fresh-clone reproduction by a non-author) |
| Retrospective | Data-first review of KPIs, 5 Whys or fishbone, kaizen issues, A3 for bigger problems |

## 2. Backlog and board

- Every task is a GitHub issue created from an issue form, with an owner, description, acceptance criterion, estimate, milestone, and type label.
- The board (https://github.com/users/jeraddunne/projects/1) mirrors the instructor's template: **Todo, In progress, Done, Block, Cancelled**, with a WIP limit of 5 in Todo and In progress. Custom fields: Sprint, Estimate, Priority, Work type, Start date, Target date.
- Milestones: Formation, Sprint 1, Sprint 2, Sprint 3, Finalization, each with the rubric due date.
- Large rubric deliverables (`rubric` label) are parent issues; implementation tasks are sub-issues, so "Sub-issues progress" shows deliverable completeness.

### Definition of Ready (an issue may enter a sprint)

- [ ] Title states the outcome, not the activity
- [ ] Description explains why and links the rubric bullet or research need
- [ ] Acceptance criterion is testable (a command, a file, a number)
- [ ] Estimate in points (1, 2, 3, 5, 8); anything 8 is split
- [ ] Owner assigned, milestone set, type label set
- [ ] Dependencies linked and not blocking

### Definition of Done (an issue may be closed)

- [ ] Pull request merged to `main` after an approving review by a member other than the author
- [ ] CI green (lint, tests)
- [ ] Generated results or figures regenerated and committed, with the producing command in the pull request
- [ ] README, DATA_DICTIONARY.md, or THREATS_TO_VALIDITY.md updated if affected
- [ ] `ai-use-log.md` updated if AI assisted
- [ ] Issue closed with a comment linking the evidence

## 3. Workflow for one task

1. Pick the top Ready issue in Todo that you own or can take. Assign yourself and move it to In progress (respect the WIP limit; at most two per person).
2. Branch from `main`: `<type>/<issue>-<slug>`.
3. Commit small and often, referencing the issue number.
4. Open a pull request early as a draft if you want feedback; mark it Ready for review when the author checklist passes.
5. Request one reviewer who did not write the change (rotate; do not always ask the same person). The reviewer responds within 48 hours.
6. Address the review, squash-merge after approval and green CI, delete the branch. The issue closes through `Closes #N`.
7. If blocked more than a day, add the `blocker` label and move the issue to Block. Say what would unblock you.

## 4. Pull request review standard

- `main` requires one approving review from a member other than the author (`process.min_reviewers: 1`).
- The reviewer pulls the branch and runs `make test` (and `make pipeline` for pipeline changes).
- The reviewer checks the PR template's reviewer checklist and that outputs match the described command.
- The reviewer checks that observation and interpretation are separated in any text, and that AI-assisted work is logged.
- "Request changes" is for correctness or rubric issues only; style suggestions are comments.
- The approval comment summarizes what was verified.

## 5. Estimation and capacity

- Points are relative effort: 1 = an hour or two, 2 = half a day, 3 = a day, 5 = two to three days, 8 = too big, split it.
- At planning each member states available hours; the team commits to a points total that past sprints show it can finish (commitment reliability target 0.8).

## 6. Sprint ceremonies in detail

**Planning (Thursday, 60 min).** Confirm roles. Read the rubric deliverables for the sprint. Draft the sprint goal (one sentence). Turn work sign-ups into the assignment matrix. Pull Ready issues until capacity is reached. Record in `docs/sprints/<sprint>/planning.md`. Review the top FMEA risks.

**Stand-up (Monday, Wednesday, Friday, written).** Each member writes one row: done since last entry, next, blockers, hours. The Scrum Master checks the Block column and WIP.

**Check-in (Thursday, 30 min).** Walk the board. Merge the weekly metrics pull request and read the dashboard: anything marked warn gets an owner. Check contribution flags. Curate findings and decisions into `docs/workspace/`. Update the waste log and FMEA if something changed.

**Review (last Wednesday, 45 min).** The Product Owner walks the rubric checklist in `review.md` with evidence links. Gemba walk: a member who did not write the README does a fresh clone and follows only the README. Record the outcome and prepare the sprint package for the instructor.

**Retrospective (same day, 45 min).** Start with the KPI table. Pick the biggest problem; do 5 Whys. Write kaizen issues with owners. Record changes to the research question, method, scope, or interpretation (the rubric requires this). Check the charter.

## 7. Documentation rules

- Meeting notes and stand-ups: `docs/meeting-notes/YYYY-MM-DD-<type>.md`, written by the Scrum Master (stand-up rows by each member) within 24 hours.
- Decisions: `docs/decisions/ADR-NNNN-<slug>.md` within 48 hours for significant decisions, plus a row in `docs/workspace/DECISION_LOG.md` for every decision.
- Findings: file a Research finding issue; the Scrum Master curates confirmed findings into `docs/workspace/FINDINGS_LOG.md` at the Thursday check-in.
- Work choice: file a Work sign-up issue before each sprint planning (`docs/workspace/WORK_SIGNUP.md`).
- Every number in the report links to the results file and the command that produced it.

## 8. Tooling checklist for each member

- Git and the GitHub CLI installed; `gh auth login` done.
- Python 3.11+; `make setup` and `make test` green.
- Data samples downloaded with `make data` (not committed).
- Repository cloned outside OneDrive or iCloud.
- Two-factor authentication on GitHub.
- Notifications: watch the repository for issues, pull requests, and review requests.
- Only the repository owner needs `gh auth refresh -s workflow,project,read:project`, for the workflow and board setup scripts.

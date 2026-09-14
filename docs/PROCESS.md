# Process Handbook: Scrum with a Lean Six Sigma overlay

How to use: this is the operating manual. The charter says what we agreed; this says how to do it day to day.

## 1. The two layers

| Layer | Provides | Where it lives |
|---|---|---|
| Scrum (required by the rubric) | Sprints, roles, planning, check-ins, review, retrospective, backlog on a GitHub Project board | `docs/sprints/`, GitHub Issues and Project |
| Lean Six Sigma (our improvement) | Measurement (KPIs, control charts), waste elimination, root-cause discipline, risk management (FMEA), tollgates (DMAIC) | `docs/lean-six-sigma/` |

The Scrum ceremonies are the moments when the LSS tools are used:

| Ceremony | LSS tool used |
|---|---|
| Sprint planning | DMAIC entry criteria check, FMEA risk review, capacity vs commitment |
| Stand-up | WIP limit check, blocker (Block column) aging |
| Thursday check-in | Weekly metrics PR review, run-rule signals, waste log |
| Sprint review | DMAIC tollgate (exit criteria), gemba walk (fresh-clone reproduction) |
| Retrospective | Data-first review of KPIs, 5 Whys or fishbone, kaizen issues, A3 for bigger problems |

## 2. Backlog and board

- Every task is a GitHub issue created from an issue form. Every issue has an owner, description, acceptance criterion, estimate, milestone, and type label.
- The board mirrors the instructor's template: **Todo, In progress, Done, Block, Cancelled**, with a WIP limit of 5 in Todo and In progress. Custom fields: Iteration, Estimate, Priority, Type.
- Milestones: Formation, Sprint 1, Sprint 2, Sprint 3, Finalization, each with the rubric due date.
- Sub-issues: large rubric deliverables (`rubric` label) are parent issues; implementation tasks are sub-issues so "Sub-issues progress" on the board shows deliverable completeness.

### Definition of Ready (an issue may enter a sprint)

- [ ] Title states the outcome, not the activity
- [ ] Description explains why and links the rubric bullet or research need
- [ ] Acceptance criterion is testable (a command, a file, a number)
- [ ] Estimate in points (1, 2, 3, 5, 8); anything 8 is split
- [ ] Owner assigned, milestone set, type label set
- [ ] Dependencies linked and not blocking

### Definition of Done (an issue may be closed)

- [ ] Pull request merged to `main` after approval by a different member
- [ ] CI green (lint, tests)
- [ ] Generated results or figures regenerated and committed, with the producing command in the PR
- [ ] README, DATA_DICTIONARY.md, or THREATS_TO_VALIDITY.md updated if affected
- [ ] `ai-use-log.md` updated if AI assisted
- [ ] Issue closed with a comment linking the evidence

## 3. Workflow for one task

1. Pick the top Ready issue in Todo that you own or can take. Move it to In progress (respect WIP 5).
2. Branch from `main`: `<type>/<issue>-<slug>`.
3. Commit small and often, referencing the issue number.
4. Open a PR early as a draft if you want feedback; mark Ready for review when the checklist passes.
5. Request one reviewer (rotate; do not always ask the same person). Reviewer responds within 48 hours.
6. Address review, squash-merge, delete the branch. The issue closes via `Closes #N` in the PR.
7. If blocked more than a day, add the `blocker` label and move to Block. Say what would unblock you.

## 4. Pull request review standard

The reviewer:
- Pulls the branch and runs `make test` (or `run_pipeline.sh` for pipeline changes).
- Checks the PR template checklist and that outputs match the described command.
- Checks that observation and interpretation are separated in any text.
- Uses "Request changes" only for correctness or rubric issues; style nits are comments.
- Approves with a one-line summary of what was verified.

## 5. Estimation and capacity

- Points are relative effort: 1 = an hour or two, 2 = half a day, 3 = a day, 5 = two to three days, 8 = too big, split it.
- At planning each member states available hours; the team commits to a points total that history shows it can finish (commitment reliability target 80%).

## 6. Sprint ceremonies in detail

**Planning (Thursday, 60 min).** Confirm roles. Read the rubric deliverables for the sprint. Draft the sprint goal (one sentence). Pull Ready issues until capacity is reached. Record in `docs/sprints/<sprint>/planning.md`. Review FMEA top risks.

**Stand-up (Mon/Wed/Fri, written).** Each member writes three lines: done since last, next, blockers. Scrum Master checks the Block column and WIP.

**Check-in (Thursday, 30 min).** Walk the board. Merge the weekly metrics PR and read the dashboard: anything red gets an owner. Update the waste log and FMEA if something changed.

**Review (last Wednesday, 45 min).** Product Owner walks the rubric checklist in `review.md` with evidence links. Gemba walk: one member does a fresh clone on a machine that has not run the project and follows the README. Record the outcome. Prepare the sprint package for the instructor.

**Retrospective (same day, 45 min).** Start with the KPI table. Pick the biggest problem; do 5 Whys. Write kaizen issues with owners. Record changes to the research question, method, scope, or interpretation (the rubric requires this). Check the charter.

## 7. Documentation rules

- Meeting notes: `docs/meeting-notes/YYYY-MM-DD-<type>.md`, written by the Scrum Master within 24 hours.
- Decisions: `docs/decisions/ADR-NNNN-<slug>.md` within 48 hours of the decision, plus a row in `docs/workspace/DECISION_LOG.md` for every decision, big or small.
- Findings: file a Research finding issue; the Scrum Master curates confirmed findings into `docs/workspace/FINDINGS_LOG.md` at the Thursday check-in.
- Work choice: file a Work sign-up issue before each sprint planning (`docs/workspace/WORK_SIGNUP.md`).
- Every number in the report links to the results file and the command that produced it.

## 8. Tooling checklist for each member

- Git and GitHub CLI installed, `gh auth login` done.
- Python 3.11+ and `make setup` run successfully; `make test` green.
- Data samples downloaded with `make data` (not committed).
- Two-factor authentication on GitHub.
- Notification settings: watch the repository for issues, PRs, and reviews.

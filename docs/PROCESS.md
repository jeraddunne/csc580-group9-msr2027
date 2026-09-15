# Process Handbook: Scrum with a Lean Six Sigma overlay (solo)

How to use: this is the operating manual. The solo working agreement (`TEAM_CHARTER.md`) says what I committed to; this says how to do it day to day. The project is run solo by Jerad Dunne (ADR-0005).

## 1. The two layers

| Layer | Provides | Where it lives |
|---|---|---|
| Scrum (required by the rubric) | Sprints, roles, planning, check-ins, review, retrospective, backlog on a GitHub Project board | `docs/sprints/`, GitHub Issues and Project |
| Lean Six Sigma (improvement layer) | Measurement (KPIs, control charts), waste elimination, root-cause discipline, risk management (FMEA), tollgates (DMAIC) | `docs/lean-six-sigma/` |

The Scrum ceremonies are the moments when the Lean Six Sigma tools are used:

| Ceremony | Lean Six Sigma tool used |
|---|---|
| Sprint planning | DMAIC entry criteria check, FMEA risk review, hours versus commitment |
| Work log (Mon, Wed, Fri) | WIP check, blocker aging |
| Thursday self check-in | Weekly metrics review, run-rule signals, waste log |
| Sprint review | DMAIC tollgate (exit criteria), gemba walk (fresh-clone reproduction) |
| Retrospective | Data-first review of KPIs, 5 Whys or fishbone, kaizen issues, A3 for bigger problems |

## 2. Backlog and board

- Every task is a GitHub issue created from an issue form, with a description, acceptance criterion, estimate, milestone, and type label. I assign issues to myself when I start them so cycle-time metrics work.
- The board mirrors the instructor's template: **Todo, In progress, Done, Block, Cancelled**, with a WIP limit of 5 on the board and at most two issues In progress at once. Custom fields: Sprint, Estimate, Priority, Type.
- Milestones: Formation, Sprint 1, Sprint 2, Sprint 3, Finalization, each with the rubric due date.
- Large rubric deliverables (`rubric` label) are parent issues; implementation tasks are sub-issues.

### Definition of Ready (an issue may enter a sprint)

- [ ] Title states the outcome, not the activity
- [ ] Description explains why and links the rubric bullet or research need
- [ ] Acceptance criterion is testable (a command, a file, a number)
- [ ] Estimate in points (1, 2, 3, 5, 8); anything 8 is split
- [ ] Milestone and type label set
- [ ] Dependencies linked and not blocking

### Definition of Done (an issue may be closed)

- [ ] Pull request merged to `main` under the self-review protocol (section 4)
- [ ] Tests and lint pass (in CI once workflows are enabled)
- [ ] Generated results or figures regenerated and committed, with the producing command in the pull request
- [ ] README, DATA_DICTIONARY.md, or THREATS_TO_VALIDITY.md updated if affected
- [ ] `ai-use-log.md` updated if AI assisted
- [ ] Issue closed with a comment linking the evidence

## 3. Workflow for one task

1. Pick the top Ready issue in Todo. Assign it and move it to In progress (at most two at once).
2. Branch from `main`: `<type>/<issue>-<slug>`.
3. Commit small and often, referencing the issue number.
4. Open the pull request when the author checklist passes. Note the time it was opened.
5. Wait at least 12 hours, then self-review (section 4).
6. Address anything found, squash-merge, delete the branch. The issue closes through `Closes #N`.
7. If blocked more than a day, add the `blocker` label and move the issue to Block with the reason.

## 4. Self-review protocol

This replaces review by a different team member (ADR-0005).

- `main` is protected: a pull request is required, merges are squash only, force pushes and deletion are blocked. The ruleset requires 0 approvals because there is no second member.
- Cooling-off: at least 12 hours between opening a pull request and reviewing it (`process.self_review_cooling_off_hours`). Typo-level documentation fixes may skip it when marked "trivial".
- Review steps: pull the branch into a clean environment; run `make test` (and `make pipeline` for pipeline changes); check outputs against the stated command; re-read text for observation versus interpretation; read AI-assisted parts line by line.
- Leave a review comment that summarizes what was verified.
- Major pull requests (validation results, report draft, release): request a review from the instructor or a classmate when possible, and record who reviewed. External review is the evidence offered for the rubric bullet about review by a different member.

## 5. Estimation and capacity

- Points are relative effort: 1 = an hour or two, 2 = half a day, 3 = a day, 5 = two to three days, 8 = too big, split it.
- At planning I state available hours and commit to a points total that past sprints show I can finish (commitment reliability target 0.8).

## 6. Sprint ceremonies in detail

**Planning (Thursday, 45 min, written).** Read the rubric deliverables for the sprint. Draft the sprint goal (one sentence). Record hours. Pull Ready issues until capacity is reached. Record in `docs/sprints/<sprint>/planning.md`. Review the top FMEA risks.

**Work log (Monday, Wednesday, Friday).** Three short cells: done since last entry, next, blockers, plus hours. Check the Block column and WIP.

**Self check-in (Thursday, 30 min).** Walk the board. Read the metrics dashboard: anything marked warn gets an issue. Curate findings and decisions into `docs/workspace/`. Update the waste log and FMEA if something changed.

**Review (last Wednesday, 45 min).** Walk the rubric checklist in `review.md` with evidence links. Gemba walk: a fresh clone in a clean environment, following only the README, ideally by a classmate or the instructor. Record the outcome and prepare the sprint package.

**Retrospective (same day, 30 min).** Start with the KPI table. Pick the biggest problem; do 5 Whys. Write kaizen issues. Record changes to the research question, method, scope, or interpretation (the rubric requires this). Check the working agreement.

## 7. Documentation rules

- Notes and work logs: `docs/meeting-notes/YYYY-MM-DD-<type>.md`, written within 24 hours.
- Decisions: `docs/decisions/ADR-NNNN-<slug>.md` within 48 hours for significant decisions, plus a row in `docs/workspace/DECISION_LOG.md` for every decision.
- Findings: file a Research finding issue; curate confirmed findings into `docs/workspace/FINDINGS_LOG.md` at the Thursday check-in.
- Work plan: `docs/workspace/WORK_SIGNUP.md` (solo workstream plan) is updated at each planning.
- Every number in the report links to the results file and the command that produced it.

## 8. Tooling checklist

- Git and the GitHub CLI installed; `gh auth login` done, and `gh auth refresh -s workflow,project,read:project` for workflow and board scripts.
- Python 3.11+; `make setup` and `make test` green.
- Data samples downloaded with `make data` (not committed).
- Repository cloned outside OneDrive for daily work.
- Two-factor authentication on GitHub.

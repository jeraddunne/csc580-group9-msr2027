# KPI catalogue

This is the authoritative list of what the team measures. Every KPI here is emitted by `scripts/lss_metrics.py` (implemented in `src/msr_pipeline/lss_metrics.py`) under the JSON key shown, and rendered in `metrics/DASHBOARD.md`. Targets come from `project.yml` under `metrics:`; the defaults listed here apply when a key is missing.

## Summary table

| KPI | JSON key | Unit | Target (default) | Status rule |
|---|---|---|---|---|
| Velocity | `kpis.velocity` | story points per sprint | none (trend only) | info |
| Commitment reliability | `kpis.commitment_reliability` | ratio | >= 0.80 | ok if >= target |
| Cycle time | `kpis.cycle_time_days` | days (median) | <= 5 | ok if median <= target |
| Lead time | `kpis.lead_time_days` | days (median) | <= 10 | ok if median <= target |
| Throughput | `kpis.throughput_per_week` | issues closed per week | none (trend only) | info |
| WIP | `kpis.wip` | open in-progress issues | <= `wip_limit` (5) | ok if <= limit |
| Blocked time | `kpis.blocked_time_days` | days (total and mean) | none (trend only) | info |
| PR first-review turnaround | `kpis.pr_first_review_hours` | hours (median) | <= 48 | ok if median <= target |
| PR open-to-merge cycle time (extra KPI) | `kpis.pr_merge_hours` | hours (median) | <= 96 | ok if median <= target |
| First-time-right | `kpis.first_time_right` | ratio | >= 0.75 | ok if >= target |
| Rework ratio | `kpis.rework_ratio` | ratio | <= 0.15 | ok if <= max |
| Defect count | `kpis.defect_count` | count | none (trend only) | info |
| CI pass rate | `kpis.ci_pass_rate` | ratio | >= 0.90 | ok if >= target |
| Contribution balance | `kpis.contribution_gini` and `contribution.*` | Gini, shares | each share in [0.15, 0.45] | warn if any member outside |
| Kaizen closure rate | `kpis.kaizen_closure_rate` | ratio | >= 0.70 (informational until Sprint 3) | ok if >= 0.70 |
| Reproducibility check | `kpis.reproducibility_check` | pass / fail / nodata | pass | ok if pass |

Status values used in the dashboard: `ok`, `warn`, `info`, `nodata`. A `warn` on a targeted KPI is reviewed at the Thursday check-in; two consecutive weeks of `warn` on the same KPI require a 5 Whys.

History: while the project was briefly run by one member (2026-09-14, ADR-0005), contribution balance and first-review turnaround were paused. Both were restored on 2026-09-15 (ADR-0006, decision D-021). PR open-to-merge cycle time was kept as an extra KPI.

## Definitions

### Velocity
- **Definition.** Sum of story points of issues in a sprint milestone that were closed as completed (`state_reason` = `completed`, not `not_planned`).
- **Formula.** `sum(points(issue) for issue in milestone if closed_completed)`. Points come from, in order: an `estimate` field if the fixture provides it, a label of the form `sp:N`, `points:N`, or `estimate:N`, or a line `Estimate: N` or `Story points: N` in the issue body. Issues without points count 0 points but still count as issues.
- **Data source.** GitHub Issues, milestones.
- **Owner.** Product Owner.
- **Signal action.** A drop of more than 30 percent between sprints triggers a retro question on scope or capacity.

### Commitment reliability
- **Definition.** Share of the sprint commitment that was completed.
- **Formula.** `done_points / committed_points` when committed points > 0, else `done_issues / committed_issues`. Committed = issues in the milestone created no later than the end of sprint day 1 (start date plus one day). Items added later are scope change and are reported separately as `added_after_planning`.
- **Data source.** Issues, milestones, `project.yml` timeline.
- **Target.** >= 0.80. **Owner.** Scrum Master.
- **Signal action.** Below target: retro must identify whether planning over-committed or execution stalled; adjust the next sprint commitment.

### Cycle time
- **Definition.** Time an issue spends being worked on, from start of work to closure.
- **Approximation.** The Project board Status field is not exposed in the REST issue timeline, so the start of work is approximated as the earliest of: the first `assigned` event, or the first `labeled` event whose label is `in progress` (case-insensitive, also `status:in progress`). If neither exists, `created_at` is used and the record is flagged `approximated: true`. End is `closed_at`.
- **Formula.** `(closed_at - start) / 1 day`, median and mean over issues closed in the window, excluding PRs and issues closed as `not_planned`.
- **Control chart.** XmR individuals chart in closure order; limits and run rules per `metrics/README.md`.
- **Target.** median <= 5 days. **Owner.** Scrum Master.
- **Signal action.** Run-rule signal triggers a 5 Whys on the specific issues beyond the limit; a systematic shift triggers WIP limit review.

### Lead time
- **Definition.** Time from issue creation to closure. Includes waiting in the backlog.
- **Formula.** `(closed_at - created_at) / 1 day`, median and mean.
- **Target.** median <= 10 days. **Owner.** Product Owner.
- **Signal action.** Large gap between lead and cycle time means items wait too long in Todo; refine the backlog or reduce batch size.

### Throughput
- **Definition.** Issues closed as completed per week over the reporting window.
- **Formula.** `closed_completed_count / max(1, window_weeks)`.
- **Owner.** Scrum Master. Trend only.

### WIP
- **Definition.** Open issues that are assigned to someone or labeled `in progress`.
- **Formula.** Count at snapshot time. Compared with `wip_limit` from `project.yml` (default 5).
- **Owner.** Scrum Master.
- **Signal action.** Above the limit: stop starting, start finishing; discuss at the next stand-up.

### Blocked time
- **Definition.** Time issues carry the `blocker` label.
- **Formula.** For each issue, sum intervals between a `labeled: blocker` event and the next `unlabeled: blocker` event, or `closed_at`, or the snapshot time if still open. Reported as total days, mean days per blocked issue, and the count of currently open blockers.
- **Owner.** Scrum Master.
- **Signal action.** Any blocker open more than 3 days is listed in the dashboard and raised at the next stand-up.

### PR first-review turnaround
- **Definition.** Hours from PR creation to the first review submitted by someone other than the PR author (any review state, including comments).
- **Formula.** `(first_review.submitted_at - pr.created_at) / 1 hour`, median and mean over PRs that received a review. PRs without a review are counted separately as `unreviewed_open` and `unreviewed_merged`.
- **Control chart.** XmR individuals chart in PR creation order.
- **Target.** median <= 48 hours (`pr_first_review_hours_target`). **Owner.** Scrum Master.
- **Signal action.** Above target for two weeks: enforce the review SLA in the charter and rotate reviewer duty. Any `unreviewed_merged` PR is raised at the next check-in, because `main` requires one approving review.

### PR open-to-merge cycle time (extra KPI)
- **Definition.** Hours from PR creation to merge.
- **Formula.** `(merged_at - created_at) / 1 hour`, median and mean over merged PRs.
- **Target.** median <= 96 hours (`pr_merge_hours_target`). **Owner.** Scrum Master.
- **Signal action.** Above target for two weeks while first review is within target: PRs are too large or review comments wait too long for a response; split PRs and agree a response time for authors.

### First-time-right rate
- **Definition.** Share of merged PRs that were approved without any `CHANGES_REQUESTED` review.
- **Formula.** `merged_prs_without_changes_requested / merged_prs`.
- **Target.** >= 0.75. **Owner.** Developers.
- **Signal action.** Below target: look at the review comments for recurring causes (missing tests, unclear issue) and add a checklist item to the PR template.

### Rework ratio
- **Definition.** Share of closed issues that needed rework.
- **Formula.** `count(closed issues with label rework OR with a reopened event) / count(closed issues)`.
- **Target.** <= 0.15. **Owner.** Product Owner.
- **Signal action.** Above target: the acceptance criteria on issues are not clear enough; run a Definition of Ready review.

### Defect count
- **Definition.** Issues labeled `bug`.
- **Formula.** `defect_count` = bug issues created in the window. `escaped_defects` per sprint = bug issues whose milestone is that sprint and whose `created_at` is after the sprint end date.
- **Owner.** Developers. Trend only.

### CI pass rate
- **Definition.** Share of completed workflow runs that succeeded.
- **Formula.** `success_runs / (success_runs + failure_runs + timed_out_runs)`. Cancelled and skipped runs are excluded. Runs of the `LSS metrics` workflow are excluded.
- **Target.** >= 0.90. **Owner.** Developers.
- **Signal action.** Below target: no new feature PRs until `main` is green.

### Contribution balance
- **Definition.** How evenly work is shared across the four members.
- **Formula.** For each member: `commits`, `prs_authored`, `reviews_given`, `issues_closed` (issue closed as completed with the member as assignee). Share per category = member count divided by the category total. `share_overall` = mean of the category shares over categories whose total is > 0. `contribution_gini` = Gini coefficient of the `share_overall` vector (0 = perfectly even, 1 = one person did everything). Members are taken from `project.yml` `team[].github`; other authors (bots, instructor) are listed under `others`.
- **Target.** Every member `share_overall` in [0.15, 0.45] (`contribution_share_min`, `contribution_share_max`); `flag` is set on members outside the band.
- **Owner.** Scrum Master.
- **Signal action.** A flagged member is a conversation at the Thursday check-in about rebalancing assignments, not a judgment. Early Sprint 1 values are skewed by the repository setup work done before the group was reinstated; read the trend, not the first snapshot.

### Kaizen closure rate
- **Definition.** Share of process-improvement items that were completed.
- **Formula.** `closed kaizen issues / all kaizen issues` (label `kaizen`).
- **Target.** >= 0.70 by the Sprint 3 review. **Owner.** Scrum Master.

### Pipeline reproducibility check
- **Definition.** Result of the most recent completed run of the CI workflow (name from `project.yml` `metrics.reproducibility_workflow`, default `CI`) on the default branch.
- **Values.** `pass` if the latest run succeeded, `fail` if it failed, `nodata` if no run exists.
- **Owner.** Developers.
- **Signal action.** `fail` blocks the sprint review until fixed.

## Review cadence

| When | Who | What is read |
|---|---|---|
| Monday | Scrum Master, with one approving reviewer | Merge the weekly metrics PR, note any `warn` |
| Thursday check-in | Whole team, 15 minutes | KPI table, run-rule signals, open blockers, contribution flags |
| Sprint review | Whole team, Product Owner presents | Sprint summary table (velocity, reliability, added after planning) |
| Retrospective | Whole team, Scrum Master facilitates | Two-week trend of any `warn`, waste log, kaizen closure |

## Data window

By default the script reports on everything since the `since` date given on the command line, or the formation start date in `project.yml` when omitted. Sprint-level rows use milestone titles first (`Sprint 1`, `Sprint 2`, `Sprint 3`, `Formation`, `Finalization`) and fall back to the closing date against the timeline in `project.yml`.

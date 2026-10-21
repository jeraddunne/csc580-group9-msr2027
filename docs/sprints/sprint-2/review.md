# Sprint 2 review: implementation and validation

How to use: the Product Owner runs the review on Wed 2026-10-28. Every rubric bullet must link to evidence in this repository. Rubric weight: 20%.

Date: 2026-10-28. Product Owner: Allie Hodges. Scrum Master: Hina Kramer.
Present: [ ] Leticia Aderhold [ ] Jerad Dunne [ ] Allie Hodges [ ] Hina Kramer [ ] Instructor (if present)

## Sprint goal check

## Sprint goal check

- Sprint goal (proposed; confirm with the Product Owner): By October 28, the risk-signal scanner, variant linking, and reach analysis run end to end on the approved GitSkills sample, automated tests cover core functions, and human validation produces precision and agreement results supported by reproducible tables and figures.
- Met: partially (provisional as of October 21). The repository contains the core implementation, automated tests, preliminary results, a research-report draft, and a written validation protocol. Final validation scores, updated process metrics, a fresh reproduction run, and the completed Sprint 2 retrospective still need confirmation before the goal can be marked fully met.

## Rubric review checklist (verbatim from the assignment)

The Sprint 2 review must include:

- [x] A working implementation of the core mining, extraction, similarity, classification, traceability, or visualization method. Evidence: [Recorded pipeline runs](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/docs/REPRODUCE.md#recorded-runs). The September 30, 2026 reproduction records report successful end-to-end runs and matching results for all 14 generated tables. This is historical implementation evidence; a fresh Sprint 2 demonstration remains pending.
- [x] A validation sample, manual annotation protocol, or other evaluation design. Evidence: [Validation protocol and evaluation design](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/docs/validation/README.md). Documents the samples, reviewer assignments, independent labeling procedure, scoring metrics, and disagreement handling. This confirms the evaluation design; completed labeling and validation scores are tracked separately.
- [x] A validation sample, manual annotation protocol, or other evaluation design. Evidence: [Validation protocol](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/docs/validation/README.md), documenting sample sizes, reviewer assignments, independent labeling, scoring, and disagreement handling. Evaluation design is documented; completed validation results are tracked separately.
- [x] Preliminary results with reproducible figures or tables. Evidence: [RQ1 prevalence](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/results/rq1_prevalence_by_rule.csv), [RQ2 reach](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/results/rq2_reach_summary.csv), and [RQ3 variant differences](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/results/rq3_differing_pairs.csv). Reproduction command: `make pipeline`; see [recorded reproduction runs](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/docs/REPRODUCE.md#recorded-runs). These are existing preliminary scanner results; human validation and a fresh Sprint 2 run are tracked separately.
- [x] At least one pull request reviewed by a different team member than the author. Evidence: [PR #105](https://github.com/jeraddunne/csc580-group9-msr2027/pull/105), authored by Jerad Dunne and approved by Leticia Aderhold (angel06la); merged with five checks passing.
- [x] An updated research report containing the background, method, implementation, and preliminary results. Evidence: [Report update PR #91](https://github.com/jeraddunne/csc580-group9-msr2027/pull/91). The draft includes introduction and related work, dataset preparation, method and implementation, and preliminary RQ1–RQ3 results. Human validation remains pending.
- [ ] A retrospective that records changes to the research question, method, scope, or interpretation. Evidence:

## Sprint 2 acceptance criteria (verbatim)

| Criterion | Pass / Fail | Evidence link | Notes |
|---|---|---|---|
| The core implementation runs end to end on the approved sample | Pass (historical run) | [Recorded reproduction runs](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/docs/REPRODUCE.md#recorded-runs) | September 30 runs report successful execution and matching results for all 14 tables. A fresh Sprint 2 demonstration remains pending. |
| The method is tested | Pass (automated tests); human validation pending | [Evaluation and validation](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/report/draft.md#evaluation-and-validation), [PR #93 checks](https://github.com/jeraddunne/csc580-group9-msr2027/pull/93/checks) | Documented test coverage includes rule examples, scanning, variant linking, missing-value handling, statistics, and validation scoring. Python 3.11 and 3.12 lint-and-test checks passed. Completed human validation scores remain pending. |
| The group can explain why the result should be trusted or where it may fail | Pass (documented explanation) | [Discussion and limitations](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/report/draft.md#discussion), [Validation protocol](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/docs/validation/README.md) | The report discusses alternative explanations, sampling limits, and unvalidated keyword matches. Reproducibility does not establish detection accuracy; human validation remains pending. |
| The preliminary analysis is supported by generated evidence rather than screenshots alone | Pass | [RQ1 prevalence](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/results/rq1_prevalence_by_rule.csv), [RQ2 reach](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/results/rq2_reach_summary.csv), [RQ3 differences](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/results/rq3_differing_pairs.csv) | Populated CSV outputs are committed. The documented reproduction command is `make pipeline`. These are preliminary scanner results, not completed human validation findings. |

## Validation status

Status as of October 21, 2026. Pending entries indicate evidence or scores not yet confirmed.

| Kind | Primary rater | Second rater | Second-rater labels committed (PR #, date) | Primary labels committed after (PR #, date) | Cohen's kappa |
|---|---|---|---|---|---|
| Signals | Jerad Dunne (jd) | None; intra-rater repeat check planned | Not applicable: no teammate second rater | Round 1 commit status pending confirmation | Pending; intra-rater check planned for Sprint 3, at least 14 days after round 1 |
| Lineage | Jerad Dunne (jd) | Hina Kramer (hk) | Pending confirmation; target October 22 under D-024 | Pending; primary labels must follow the second-rater file merge | Pending scoring |
| Drift | Jerad Dunne (jd) | Leticia Aderhold (la) | [PR #90](https://github.com/jeraddunne/csc580-group9-msr2027/pull/90) contains the proposed round 1 labels; merge status and commit date pending confirmation | Pending confirmation; primary labels must follow the second-rater file merge | Pending scoring |

Drift and lineage ratings remain independent under the blindness rule. Signals reliability will be reported separately as intra-rater agreement. No agreement scores are claimed until the required labels are available and scoring is complete.

## Demo script (12 minutes)

Proposed presenter assignments; confirm with the team before the review.

| Step | Content | Time | Presenter |
|---|---|---|---|
| 1 | Restate the research question: How prevalent are risk-relevant signals in copied agent skills, how widely are they copied, and how do variants differ? Explain that the method uses static rule matching, copy analysis, and variant comparison on the GitSkills sample. | 1 min | Leticia Aderhold |
| 2 | Demonstrate `make test` and `make pipeline` in a prepared environment; show CI status. Rehearse timing beforehand and keep a completed run log available if execution exceeds the allotted time. | 3 min | Jerad Dunne |
| 3 | Show one preliminary results table and one generated figure. Explain the denominator, main observation, and reproduction command. Identify the script or function that generates each output before the demo. | 3 min | Jerad Dunne |
| 4 | Explain the validation sample, labeling protocol, and independent reviewer assignments: Jerad is primary rater, Leticia second-rates drift, and Hina second-rates lineage. Present precision and agreement scores only if generated and verified; otherwise state what remains pending. Signals repeat labeling is planned for Sprint 3. | 2 min | Hina Kramer |
| 5 | Show PR #105 and Leticia's approving review, explain D-024 and D-025, and show the metrics dashboard with its snapshot date. Identify any stale or unavailable metrics. | 2 min | Leticia Aderhold |
| 6 | Explain limitations: keyword matches do not establish harmful behavior, the sample limits generalization, and variant similarity requires human review. Outline Sprint 3 follow-up work based on validation findings and the signals repeat-labeling check. | 1 min | Hina Kramer |

## Gemba walk: fresh-clone reproduction record

Pending: a member who did not write the README must follow its instructions in a fresh checkout and record the actual outcome.

| Field | Value |
|---|---|
| Who (a member who did not write the README) and environment | Pending: record the member's name, operating system, and Python version |
| Date | Pending: actual run date |
| Commit SHA | Pending: exact repository commit used |
| Steps followed (from README) | Planned: follow README setup, sample acquisition, tests, and pipeline instructions; record the exact commands actually used |
| Time to first result (minutes) | Pending: measure during the run |
| Result matched committed output | Pending: compare generated tables with committed results and record any differences |
| Problems found (open issues) | Pending: record observed problems and issue links, or “None observed” after completing the run |

Historical author-run reproduction records are available in [docs/REPRODUCE.md](../../REPRODUCE.md). They support reproducibility but do not replace this non-author fresh-clone record.

## Instructor feedback

| Feedback | Action | Owner | Issue # |
|---|---|---|---|
| | | | |

## Velocity and KPIs at review

Status as of October 21, 2026. Sprint 2 remains in progress. Pending values must be filled from a dated metrics snapshot before the final review.

| Metric | Sprint 1 | Sprint 2 |
|---|---|---|
| Points planned / completed | Pending final Sprint 1 totals | Pending reconciliation of planned points; completed total pending |
| Issues closed | Pending sprint-filtered count | Pending sprint-filtered count |
| PRs merged / merged with an approving review from another member | Pending sprint totals | PR #105 is a confirmed merged PR with non-author approval; sprint totals pending |
| Median PR first-review turnaround (hours) | Pending dated dashboard value | Pending dated dashboard value |
| Median cycle time (days) | Pending dated dashboard value | Pending dated dashboard value |
| Median PR open-to-merge time (hours) | Pending dated dashboard value | Pending dated dashboard value |
| CI pass rate | Pending sprint-wide calculation | Pending sprint-wide calculation |
| Rework items | Pending documented count | Pending documented count |
| Contribution share per member (min / max) | Pending calculation using Sprint 1 membership | Pending calculation for the three current members |
| Test count / coverage | September 30 reproduction record reports 164 passing tests; coverage percentage not confirmed | PR #105 description reports 179 passing Python tests and 35 passing app tests; final review count and coverage percentage pending |

Sources: [Metrics dashboard](../../lean-six-sigma/metrics/DASHBOARD.md), [reproduction records](../../REPRODUCE.md#recorded-runs), and [PR #105](https://github.com/jeraddunne/csc580-group9-msr2027/pull/105).

Record the dashboard snapshot date and commit when adding final values. Historical test counts describe their recorded runs and are not current coverage measurements.

## Backlog changes agreed at the review

Pending the Sprint 2 review on October 28, 2026. The items below distinguish existing backlog work from decisions still to be made.

- Added: Existing instructor-feedback follow-up work is tracked in #95–#104, including rule documentation, applicability analysis, known-positive validation, the human review workflow, labeling and scoring, process evidence, metrics workflow repair, and AI-use logging. Any additional items agreed during the review will be recorded here.
- Removed or cancelled: No review-specific removals or cancellations confirmed. Record any agreed changes with issue links and reasons.
- Re-estimated: No review-specific estimate changes confirmed. Record each agreed change with its issue link, previous estimate, revised estimate, and reason.

Signals repeat labeling is planned for Sprint 3 under #101, at least 14 days after round 1. Confirm remaining priorities, owners, and estimates with the team at the review.

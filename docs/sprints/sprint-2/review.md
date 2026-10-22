# Sprint 2 review: implementation and validation

Status: Preliminary draft. Attendance, completion, metrics, validation results, and Sprint 2 reproduction evidence remain pending verification.
Date: 2026-10-28. Product Owner: Jerad Dunne. Scrum Master: Hina Kramer.

Present: [ ] Leticia Aderhold [ ] Jerad Dunne [ ] Hina Kramer [ ] Instructor

## Sprint goal check

## Sprint goal check

- Sprint goal (proposed; confirm with the Product Owner): By October 28, the risk-signal scanner, variant linking, and reach analysis run end to end on the approved GitSkills sample, automated tests cover core functions, and human validation produces precision and agreement results supported by reproducible tables and figures.
- Met: partially (provisional as of October 21). The repository contains the core implementation, automated tests, preliminary results, a research-report draft, and a written validation protocol. Final validation scores, updated process metrics, a fresh reproduction run, and the completed Sprint 2 retrospective still need confirmation before the goal can be marked fully met.
> By 2026-10-28, the team will have the core mining and analysis pipeline running end-to-end on the approved sample, automated tests, reproducible preliminary results, updated report sections, and documented validation including second-rater labels and inter-rater agreement.

Met: [ ] Yes [ ] Partly [ ] No

## Rubric review checklist

The Sprint 2 review must include:

- [x] A working implementation of the core mining, extraction, similarity, classification, traceability, or visualization method. Evidence: [Recorded pipeline runs](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/docs/REPRODUCE.md#recorded-runs). The September 30, 2026 reproduction records report successful end-to-end runs and matching results for all 14 generated tables. This is historical implementation evidence; a fresh Sprint 2 demonstration remains pending.
- [x] A validation sample, manual annotation protocol, or other evaluation design. Evidence: [Validation protocol and evaluation design](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/docs/validation/README.md). Documents the samples, reviewer assignments, independent labeling procedure, scoring metrics, and disagreement handling. This confirms the evaluation design; completed labeling and validation scores are tracked separately.
- [x] A validation sample, manual annotation protocol, or other evaluation design. Evidence: [Validation protocol](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/docs/validation/README.md), documenting sample sizes, reviewer assignments, independent labeling, scoring, and disagreement handling. Evaluation design is documented; completed validation results are tracked separately.
- [x] Preliminary results with reproducible figures or tables. Evidence: [RQ1 prevalence](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/results/rq1_prevalence_by_rule.csv), [RQ2 reach](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/results/rq2_reach_summary.csv), and [RQ3 variant differences](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/results/rq3_differing_pairs.csv). Reproduction command: `make pipeline`; see [recorded reproduction runs](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/docs/REPRODUCE.md#recorded-runs). These are existing preliminary scanner results; human validation and a fresh Sprint 2 run are tracked separately.
- [x] At least one pull request reviewed by a different team member than the author. Evidence: [PR #105](https://github.com/jeraddunne/csc580-group9-msr2027/pull/105), authored by Jerad Dunne and approved by Leticia Aderhold (angel06la); merged with five checks passing.
- [x] An updated research report containing the background, method, implementation, and preliminary results. Evidence: [Report update PR #91](https://github.com/jeraddunne/csc580-group9-msr2027/pull/91). The draft includes introduction and related work, dataset preparation, method and implementation, and preliminary RQ1–RQ3 results. Human validation remains pending.
- [ ] A retrospective that records changes to the research question, method, scope, or interpretation. Evidence:
- [ ] Working core implementation. Evidence: issue #21; add the merged PR and output path when complete.
- [ ] Automated tests for the implemented method. Evidence: issue #22; add CI run and test results.
- [ ] Validation sample and protocol. Evidence: issue #23 and `docs/validation/README.md`.
- [ ] Preliminary results with reproducible figures or tables. Evidence: issue #24; add paths under `results/` or `figures/`.
- [ ] At least one pull request reviewed by a member other than its author. Evidence: add reviewed PR link.
- [ ] Updated research report. Evidence: issue #25 and `report/draft.md`.
- [ ] Sprint 2 retrospective. Evidence: issue #26 and `docs/sprints/sprint-2/retrospective.md`.

## Sprint 2 acceptance criteria

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
| Acceptance criterion | Status | Evidence |
|---|---|---|
| Core implementation runs end-to-end on the approved sample | Pending | Issue #21; add command, commit SHA, and generated output |
| Method has automated tests | Pending | Issue #22; add test and CI results |
| Group can explain why the method is trustworthy and where it may fail | Pending | Issue #23; validation results and threats-to-validity discussion |
| Preliminary analysis is supported by generated evidence rather than screenshots alone | Pending | Issue #24; add reproducible table and figure paths and the scripts that generated them |

## Validation status

Assignments follow D-024. Pending entries require evidence from the relevant validation issue or pull request.

| Kind | Primary rater | Second rater | Label PR/date | Agreement result |
|---|---|---|---|---|
| Signals | Jerad (`jd`) | None; intra-rater round 2 is deferred to Sprint 3 under #101 | Pending | Inter-rater kappa not applicable; intra-rater result pending |
| Lineage | Jerad (`jd`) | Hina (`hk`) | Pending; see #99 and #100 | Pending |
| Drift | Jerad (`jd`) | Leticia (`la`) | See #90; confirm label PR and date | Pending |

Preserve rater independence and follow the documented blindness protocol.

## Demo script (12 minutes)

| Step | Time | Presenter |
|---|---:|---|
| Research question and method | 1 min | Leticia |
| `make test`, `make pipeline`, and CI | 3 min | Jerad |
| Preliminary table and figure; identify the script and command that produced each | 3 min | Leticia |
| Validation protocol, precision per rule, and agreement results; explain limitations | 2 min | Hina |
| PR review, ADR, and process metrics | 2 min | Hina |
| Known failure and Sprint 3 plan | 1 min | Jerad |

## Sprint 2 Gemba walk: fresh-clone reproduction

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
A new Sprint 2 run is required. The historical Sprint 1 record below does not satisfy this requirement.

| Field | Evidence |
|---|---|
| Status | Pending new Sprint 2 run |
| Person and environment | Pending |
| Run date | Pending |
| Commit SHA | Pending; capture using `git rev-parse HEAD` |
| README steps and commands followed | Pending; record the actual commands |
| Time to first result | Pending; measure during the run |
| Generated output and comparison | Pending; link output and compare with the expected result |
| Problems and resolutions | Pending |

## Historical Sprint 1 reproduction record — September 26

| Field | Evidence |
|---|---|
| Who and environment | Leticia Aderhold; Windows 11; Python 3.12.1 |
| Date | 2026-09-26 |
| Commit SHA | Not recorded for the September 26 run |
| README steps followed | Created and activated a virtual environment; installed development dependencies; ran the sample-download script and checked the manifest |
| Time to first result | Not recorded |
| Output matched | Dataset acquisition succeeded; full pipeline output was not independently compared |
| Problems found | Missing requests dependency caused the initial failure. Installing development dependencies resolved it; documented in issue #14 |

## Instructor feedback

Source: [Sprint 2 instructor feedback](instructor-feedback.md). These are tracked requests; completion requires linked evidence.

| Feedback | Action | Owner | Issue # |
|---|---|---|---|
| Complete validation | Follow D-024, complete labels, score validation, and report agreement and limitations | Jerad, Hina, and Leticia | #99, #100, #90 |
| Start with known-positive skills | Select about ten skills independently of rule patterns and report detections and misses | Jerad; selection checked by another member | #97 |
| Explain rule provenance | Document each rule's rationale, example, source, and known false positives | Jerad | #95 |
| Analyze applicability | Explain which established rules apply to skill text or bundled scripts | Jerad | #96 |
| Define intended use | Document the human-in-the-loop risk-review workflow and diagrams | Jerad; reviewed by Hina and Leticia | #98 |
| Document team process | Maintain check-in notes, retrospective, obstacles, and contributions | Hina and Leticia | #102, #26 |
| Define task completion | Include acceptance criteria and a definition of done for each open Sprint 2 task | Hina | #102 |
| Report obstacles | Record reduced capacity, validation timing constraints, and metrics-workflow problems | Hina | #102, #101, #103 |
| Keep AI-use records current | Each member records assistance or states none was used | Everyone | #104 |
| Check feedback video for further requests | Watch the Canvas video and add requests not already documented | Jerad | See instructor-feedback.md |

## Obstacles

| Obstacle | Impact | Response / tracking |
|---|---|---|
| Team decreased from four members to three | Reduced capacity and reassignment needs | Update ownership and priorities; see planning.md and D-025 |
| Signals intra-rater validation requires a 14-day gap | Round 2 moves to Sprint 3 | Track in #101 |
| Metrics workflow failure | Delays reliable process metrics | Track in #103; verify resolution before reporting values |

Confirm obstacle status and add supporting evidence at the review.

## Contributions per member

Record verified completed work, distinct from planned assignments.

| Member | Planned responsibility | Verified contribution and issue/PR evidence |
|---|---|---|
| Leticia Aderhold | Report and preliminary-results documentation; drift second-rating; reviews | Pending verification |
| Jerad Dunne | Product Owner; implementation, tests, validation scoring, and technical integration | Pending verification |
| Hina Kramer | Scrum Master; validation coordination, lineage second-rating, process evidence, and retrospective | Pending verification |

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

## Backlog changes proposed for review

Pending the Sprint 2 review on October 28, 2026. The items below distinguish existing backlog work from decisions still to be made.

- Added: Existing instructor-feedback follow-up work is tracked in #95–#104, including rule documentation, applicability analysis, known-positive validation, the human review workflow, labeling and scoring, process evidence, metrics workflow repair, and AI-use logging. Any additional items agreed during the review will be recorded here.
- Removed or cancelled: No review-specific removals or cancellations confirmed. Record any agreed changes with issue links and reasons.
- Re-estimated: No review-specific estimate changes confirmed. Record each agreed change with its issue link, previous estimate, revised estimate, and reason.

Signals repeat labeling is planned for Sprint 3 under #101, at least 14 days after round 1. Confirm remaining priorities, owners, and estimates with the team at the review.
- Added: redistribute work previously associated with Allie and update team documentation.
- Removed/cancelled: Allie from capacity, attendance, assignments, and review rotation because she dropped the course.
- Re-estimation proposed: reconcile remaining work and instructor-feedback tasks with three-person capacity; final estimates require team agreement.

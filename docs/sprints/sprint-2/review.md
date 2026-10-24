# Sprint 2 review: implementation and validation

Status: Preliminary draft. Attendance, completion, metrics, validation results, and Sprint 2 reproduction evidence remain pending verification.
Date: 2026-10-28. Product Owner: Jerad Dunne. Scrum Master: Hina Kramer.

Present: [ ] Leticia Aderhold [ ] Jerad Dunne [ ] Hina Kramer [ ] Instructor

## Sprint goal check

> By 2026-10-28, the team will have the core mining and analysis pipeline running end-to-end on the approved sample, automated tests, reproducible preliminary results, updated report sections, and documented validation including second-rater labels and inter-rater agreement.

Met: [ ] Yes [ ] Partly [ ] No

## Rubric review checklist

The Sprint 2 review must include:

- [x] Working core implementation (carried in). Evidence: [PR #44](https://github.com/jeraddunne/csc580-group9-msr2027/pull/44), merged September 14, closed issue #21. The PR records an end-to-end sample run using `python -m msr_pipeline analyze`, producing `results/population_flow.csv`, `results/ANALYSIS_MANIFEST.json`, and `figures/rq1_prevalence_by_category.png`. A fresh Sprint 2 reproduction remains pending.
- [ ] Automated tests for the implemented method. Evidence: issue #22 records 179 tests passing in 38.96 seconds on commit `ee52bce` and successful CI run #114. Confirmation that every function contributing output to the report has a corresponding automated test remains pending.
- [ ] Validation sample and protocol. Evidence: issue #23 and `docs/validation/README.md` document the frozen sample, annotation workflow, and rater assignments. Samples include 147 signal items (209 label rows), 58 lineage pairs, and 18 drift pairs. Completed two-rater agreement results remain to be verified; signals intra-rater round 2 is deferred to Sprint 3 (#101).
- [x] Preliminary results with reproducible figures or tables. Evidence: issue #24 records verification of `results/population_flow.csv`, `results/rq1_prevalence_by_category.csv`, `results/rq2_reach_summary.csv`, and `results/rq3_summary.csv` against `report/draft.md`, plus checks of all three RQ figures. `results/ANALYSIS_MANIFEST.json` records the September 23 pipeline run, command, input hashes, software versions, and generated outputs. Verification reviewed committed outputs and recorded run evidence; Leticia did not personally rerun the pipeline.
- [x] At least one pull request reviewed by a member other than its author. Evidence: [PR #90](https://github.com/jeraddunne/csc580-group9-msr2027/pull/90), authored by Leticia Aderhold, received Hina Kramer’s approving file-validity review and was merged into `main`. The review preserved the independently submitted labels; three checks passed.
- [ ] Updated research report. Evidence: issue #25 and `report/draft.md`.
- [ ] Sprint 2 retrospective. Evidence: issue #26 and `docs/sprints/sprint-2/retrospective.md`.

## Sprint 2 acceptance criteria

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
| Start with known-positive skills | Select about ten skills independently of rule patterns and report detections and misses | Leticia: skill selection; Jerad: scanner check and results | #97 |
| Explain rule provenance | Document each rule's rationale, example, source, and known false positives | Jerad | #95 |
| Analyze applicability | Explain which established rules apply to skill text or bundled scripts; [Applicability comparison](../../research/APPLICABILITY.md) (PR #107) | Leticia | #96 |
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
| One primary rater | Signals lack an independent second-rater comparison | Follow D-024: Hina second-rates lineage, Leticia second-rates drift; signals intra-rater round 2 is tracked in #101 |
| Signals intra-rater validation requires a 14-day gap | Round 2 moves to Sprint 3 | Track in #101 |
| Metrics workflow failure | Delays reliable process metrics | Track in #103; verify resolution before reporting values |

Confirm obstacle status and add supporting evidence at the review.

## Contributions per member

Record documented contributions separately from planned responsibilities. Open PRs are not counted as merged deliverables; final status requires teammate confirmation.

| Member | Planned responsibility | Documented contribution and issue/PR evidence |
|---|---|---|
| Leticia Aderhold | Report and preliminary-results documentation; drift second-rating; reviews | Authored Sprint 2 review updates merged in PR #94. Prepared planning corrections in PR #92, known-positive skill selection and revisions in PR #106 (#97), and the applicability comparison in PR #107 (#96); these three PRs remain open pending review/merge. Submitted 18 round 1 drift labels in PR #90, approved by Hina and merged into main. confirm final status before recording completion. |
| Jerad Dunne | Product Owner; implementation, tests, validation scoring, and technical integration | Contributed Sprint 2 rater, team-role, and instructor-feedback updates in merged PR #105. Implemented the ground-truth checking script in merged PR #112 (#97). Provided review feedback on PRs #92 and #106. Scanner evaluation results remain pending. |
| Hina Kramer | Scrum Master; validation coordination, lineage second-rating, process evidence, and retrospective | Provided review feedback on PRs #92, #106, and #107. Recorded AI-assisted review activity in merged PR #114 (#104). Lineage-label completion and remaining process evidence require confirmation. |

## Velocity and KPIs at review

| Metric | Sprint 1 | Sprint 2 |
|---|---|---|
| Points planned / completed | Completed velocity: 15 points per October 4 dashboard snapshot; planned total requires confirmation | Planning records 3 points; committed items and member allocations require reconciliation in PR #92; completed total pending |
| Issues closed | Pending dashboard verification | Pending dated Sprint 2 metrics snapshot |
| PRs merged / merged with an approving review from another member | Pending dashboard verification | Pending verification of merged PRs and approving reviews |
| Median PR first-review turnaround (hours) | Pending dashboard verification | Pending metrics output |
| Median cycle time (days) | Pending dashboard verification | Pending metrics output |
| Median PR open-to-merge time (hours) | Pending dashboard verification | Pending metrics output |
| CI pass rate | Pending dashboard verification | Pending aggregate metrics; individual passing PR checks do not establish the sprint pass rate |
| Rework items | Pending dashboard verification | Pending metrics output |
| Contribution share per member (min / max) | Pending dashboard verification | Pending verified contribution counts |
| Test count / coverage | Pending recorded test results | Pending test and coverage results for the reviewed commit |

## Backlog changes proposed for review

- Added: redistribute work previously associated with Allie and update team documentation.
- Removed/cancelled: Allie from capacity, attendance, assignments, and review rotation because she dropped the course.
- Re-estimation proposed: reconcile remaining work and instructor-feedback tasks with three-person capacity; final estimates require team agreement.

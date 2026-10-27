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
- [x] Automated tests for the implemented method. Evidence: issue #22 and merged [PR #125](https://github.com/jeraddunne/csc580-group9-msr2027/pull/125). [CI run #268, Python 3.11 test job](https://github.com/jeraddunne/csc580-group9-msr2027/actions/runs/40329088987/job/121593400923) reports 216 tests passed in 20.55 seconds with 97% total coverage. [docs/TEST_MAP.md](../../TEST_MAP.md) maps report outputs to their tests; PR #125 added four report-output value tests.
- [x] Validation sample and protocol. Evidence: issue #23 and [validation protocol](../../validation/README.md) document the frozen sample: 147 signal items (209 label rows), 58 lineage pairs, and 18 drift pairs. [Agreement results](../../../results/validation_agreement.csv) report drift agreement of 83.3% across 18 pairs (kappa 0.745), and lineage agreement of 57/58 pairs (98.3%). Lineage kappa is 0 because one rater used a single category; interpret it alongside percent agreement. Signals intra-rater round 2 remains Sprint 3 work (#101).
- [x] Automated tests for the implemented method. Evidence: issue #22 records 179 tests passing in 38.96 seconds on commit `ee52bce` and successful CI run #114. [`docs/TEST_MAP.md`](../../TEST_MAP.md) maps every table and figure in the report to the tests that check its values; PR #125 added value checks for the four outputs that had none (population flow, prevalence by rule, reach summary, sensitivity summary), and CI runs them on every pull request. On 2026-10-27, `make test` passed 219 tests on `main` (8e2ce36), and [CI run #276](https://github.com/jeraddunne/csc580-group9-msr2027/actions/runs/40535530556) passed; issue #22 closed on October 26.
- [ ] Validation sample and protocol. Evidence: issue #23 and `docs/validation/README.md` document the frozen sample, annotation workflow, and rater assignments: 147 signal items (209 label rows), 58 lineage pairs, and 18 drift pairs. Merged PR #119 reports drift inter-rater agreement across 18 pairs: 83.3% agreement and Cohen’s kappa 0.745 (`results/validation_agreement.csv`). Lineage: Hina’s labels merged in PR #121 and Jerad’s in PR #124; the raters agree on 57 of 58 pairs (98.3%), and Cohen’s kappa is 0 because one rater used a single label, so percent agreement is the lineage figure (`results/validation_agreement.csv`). Signals intra-rater round 2 is deferred to Sprint 3 (#101). Ground truth (#97): on 2026-10-27 the scanner detected all ten known-positive skills Leticia selected, 0 missed, five of them at high risk ([results](../../validation/KNOWN_POSITIVES_SELECTION.md#results-2026-10-27), `results/ground_truth_summary.csv`).
- [x] Preliminary results with reproducible figures or tables. Evidence: issue #24 records Leticia’s October 10 verification of the September 23 run. That historical verification is separate from the current `ANALYSIS_MANIFEST.json`, which records an October 24 run. See the committed outputs under `results/` and `figures/`.
- [x] At least one pull request reviewed by a member other than its author. Evidence: [PR #90](https://github.com/jeraddunne/csc580-group9-msr2027/pull/90), authored by Leticia Aderhold, received Hina Kramer’s approving file-validity review and was merged into `main`. The review preserved the independently submitted labels; three checks passed.
- [x] Updated research report. Evidence: issue #25 and `report/draft.md`.
- [ ] Sprint 2 retrospective. Evidence: issue #26 and `docs/sprints/sprint-2/retrospective.md`.

## Sprint 2 acceptance criteria

| Acceptance criterion | Status | Evidence |
|---|---|---|
| Core implementation runs end-to-end on the approved sample | Met; fresh-clone rerun pending | Issue #21, closed by PR #44. `results/ANALYSIS_MANIFEST.json` records the latest run of `python -m msr_pipeline analyze` on 2026-10-24 (102.8 s); it does not record a commit SHA, so the fresh-clone run below supplies one |
| Method has automated tests | Met | Issue #22; 219 tests passed in 30.72 seconds with 97% total coverage using Python 3.12.15 on `main` (`8e2ce36`) on 2026-10-27; [CI run #276](https://github.com/jeraddunne/csc580-group9-msr2027/actions/runs/40535530556). [Report-to-test map](../../TEST_MAP.md) maps report tables and figures to their tests. |
| Group can explain why the method is trustworthy and where it may fail | Evidence linked; discuss at the review | Precision per category with Wilson intervals, miss rate, and drift and lineage agreement (`results/validation_*.csv`; report Table 2, PR #127); ground truth on ten known positives (#97); a rule card with rationale and references for every rule ([`RULE_CATALOG.md`](../../research/RULE_CATALOG.md), #95); applicability of established tools ([`APPLICABILITY.md`](../../research/APPLICABILITY.md), #96); `THREATS_TO_VALIDITY.md`. Known weak points: strict precision of 0.20 for dynamic code execution and 0.27 for credential file paths and hard-coded IP endpoints, and five known positives detected only by context rules |
| Preliminary analysis is supported by generated evidence rather than screenshots alone | Met | Issue #24 (closed). Tables in `results/` and figures in `figures/` are written by `make pipeline` and `python scripts/annotation_kit.py score`; [`docs/TEST_MAP.md`](../../TEST_MAP.md) names the function and tests behind each; `results/spec_verification.csv` NFR-02 confirms that two runs give identical outputs |

## Validation status

Assignments follow D-024. Pending entries require evidence from the relevant validation issue or pull request.

| Kind | Primary rater | Second rater | Label PR/date | Agreement result |
|---|---|---|---|---|
| Signals | Jerad (`jd`) | None; intra-rater round 2 is deferred to Sprint 3 under #101 | Round 1 labels merged in #118; first scores merged in #119 | Inter-rater kappa not applicable; intra-rater result pending |
| Lineage | Jerad (`jd`) | Hina (`hk`) | Second-rater labels merged in #121; primary labels and scores in #124 | 58 pairs; 98.3% agreement; Cohen’s kappa 0 because one rater used a single label (`kappa_note`); source: `results/validation_agreement.csv` |
| Drift | Jerad (`jd`) | Leticia (`la`) | Second-rater labels merged in #90; primary labels merged in #118; scores merged in #119 | 18 pairs; 83.3% agreement; Cohen’s kappa 0.745; source: `results/validation_agreement.csv` |

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
| Start with known-positive skills | Select about ten skills independently of rule patterns and report detections and misses; run 2026-10-27: 10 of 10 detected, 0 missed, 5 at high risk ([results](../../validation/KNOWN_POSITIVES_SELECTION.md#results-2026-10-27)) | Leticia: skill selection; Jerad: scanner check and results | #97 |
| Explain rule provenance | Document each rule's rationale, example, source, and known false positives | Jerad | #95 |
| Analyze applicability | Explain which established rules apply to skill text or bundled scripts; [Applicability comparison](../../research/APPLICABILITY.md) (PR #107) | Leticia | #96 |
| Define intended use | Document the human-in-the-loop risk-review workflow and diagrams | Jerad; reviewed by Hina and Leticia | #98; [review workflow](../../research/REVIEW_WORKFLOW.md) revised in PR #126 |
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
| Metrics workflow failure | Delayed reliable process metrics | Fix and October 22 dashboard snapshot merged in PR #113 (#103); the snapshot captured no workflow runs, so aggregate CI pass rate is unavailable |

Confirm obstacle status and add supporting evidence at the review.

## Contributions per member

Record documented contributions separately from planned responsibilities. Open PRs are not counted as merged deliverables; final status requires teammate confirmation.

| Member | Planned responsibility | Documented contribution and issue/PR evidence |
|---|---|---|
| Leticia Aderhold | Report and preliminary-results documentation; drift second-rating; reviews | Authored Sprint 2 review updates merged in PR #94. Prepared planning corrections in PR #92 and known-positive skill selection in PR #106 (#97), both pending review/merge. Completed the applicability comparison in merged PR #107 (#96). Submitted 18 independent round 1 drift labels in PR #90, approved by Hina and merged into main. |
| Jerad Dunne | Product Owner; implementation, tests, validation scoring, and technical integration | Recorded rater assignments, team-role updates, and the instructor-feedback page (merged PR #105). Wrote rule cards with verified references (merged PR #111, #95). Added the ground-truth script (merged PR #112) and ran it on Leticia's selection (#97). Fixed the metrics workflow and committed the October 22 snapshot (merged PR #113, #103). Labelled round 1 as primary rater for all three kinds and scored them: drift and signals (merged PR #118), first scores (merged PR #119), spec-check fix (merged PR #120), lineage labels and scores (merged PR #124) (#100). Wrote value tests and the report-to-test map (merged PR #125, #22). Finalized the human-in-the-loop review workflow and diagrams after both teammates' reviews (merged PR #126, #98). Wrote the validation results into the report and fixed the FMEA calculation after Hina's review (PR #127, open). Measured the pending Sprint 1 baseline values (#19). Reviewed PRs #92 and #106. |
| Hina Kramer | Scrum Master; validation coordination, lineage second-rating, process evidence, and retrospective | Provided review feedback on PRs #92, #106, and #107. Recorded AI-assisted review activity in merged PR #114 (#104). Lineage-label completion and remaining process evidence require confirmation. |

## Velocity and KPIs at review

| Metric | Sprint 1 | Sprint 2 |
|---|---|---|
| Points planned / completed | October 22 dashboard: 19 committed / 16 completed | October 22 dashboard: 16 committed / 3 completed; reconcile with planning PR #92; final review totals pending |
| Issues closed | Pending dashboard verification | Pending dated Sprint 2 metrics snapshot |
| PRs merged / merged with an approving review from another member | Pending dashboard verification | Pending verification of merged PRs and approving reviews |
| Median PR first-review turnaround (hours) | Pending dashboard verification | Pending metrics output |
| Median cycle time (days) | Pending dashboard verification | Pending metrics output |
| Median PR open-to-merge time (hours) | Pending dashboard verification | Pending metrics output |
| CI pass rate | Pending dashboard verification | Pending aggregate metrics; individual passing PR checks do not establish the sprint pass rate |
| Rework items | Pending dashboard verification | Pending metrics output |
| Contribution share per member (min / max) | Pending dashboard verification | Pending verified contribution counts |
| Test count / coverage | Pending recorded test results | 219 passed in 30.72 seconds; 97% total coverage; Python 3.12.15; commit `8e2ce36`; [CI run #276](https://github.com/jeraddunne/csc580-group9-msr2027/actions/runs/40535530556) |

### October 22 process snapshot

Source: [LSS dashboard](../../lean-six-sigma/metrics/DASHBOARD.md), generated October 22, 2026, in merged PR #113. These figures cover September 10–October 22 across the repository, rather than either sprint separately.

| Metric | Snapshot value |
|---|---|
| Median PR first-review turnaround | 34.32 hours |
| Median issue cycle time | 2.66 days |
| Median PR open-to-merge time | 24.88 hours |
| Contribution shares | Leticia 0.28; Jerad 0.60; Hina 0.11 |
| Aggregate CI pass rate | Unavailable: no workflow runs captured |

Final October 28 review measurements remain pending.

## Backlog changes proposed for review

- Added: redistribute work previously associated with Allie and update team documentation.
- Removed/cancelled: Allie from capacity, attendance, assignments, and review rotation because she dropped the course.
- Re-estimation proposed: reconcile remaining work and instructor-feedback tasks with three-person capacity; final estimates require team agreement.

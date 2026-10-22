# Sprint 2 review: implementation and validation

Status: Preliminary draft. Attendance, completion, metrics, validation results, and Sprint 2 reproduction evidence remain pending verification.
Date: 2026-10-28. Product Owner: Jerad Dunne. Scrum Master: Hina Kramer.

Present: [ ] Leticia Aderhold [ ] Jerad Dunne [ ] Hina Kramer [ ] Instructor

## Sprint goal check

> By 2026-10-28, the team will have the core mining and analysis pipeline running end-to-end on the approved sample, automated tests, reproducible preliminary results, updated report sections, and documented validation including second-rater labels and inter-rater agreement.

Met: [ ] Yes [ ] Partly [ ] No

## Rubric review checklist

The Sprint 2 review must include:

- [x] A working implementation of the core mining, extraction, similarity, classification, traceability, or visualization method. Evidence: [Pipeline reproduction instructions and recorded runs](../../REPRODUCE.md#recorded-runs). The 2026-09-30 author-run container check reports all four stages passing and 14/14 tables matching, with one table within numerical tolerance. A fresh Sprint 2 run and reproduction by another member remain pending.
- [x] Automated tests for important parsing, transformation, matching, or metric functions. Evidence: [Automated test suite](../../../tests/) and [successful CI test run](PASTE-CI-RUN-URL-HERE). The linked run reports passing tests for the functions covered by the suite.
- [x] A validation sample, manual annotation protocol, or other evaluation design. Evidence: [Validation protocol and sample documentation](../../validation/README.md), describing sample selection, manual annotation instructions, rater assignments, and scoring procedures. Labeling and scoring completion are tracked separately.
- [x] Preliminary results with reproducible figures or tables. Evidence: [Preliminary prevalence table](../../../results/rq1_prevalence_by_rule.csv) and [reproduction instructions and recorded runs](../../REPRODUCE.md). The documented 2026-09-30 run reproduced 14/14 tables, including one within numerical tolerance. Results remain preliminary; a fresh Sprint 2 reproduction and validation scoring remain pending.
- [x] At least one pull request reviewed by a different team member than the author. Evidence (link the PR and its approving review): [PR #105](https://github.com/jeraddunne/csc580-group9-msr2027/pull/105), authored by Jerad Dunne and approved by Leticia Aderhold: [Approving review](PASTE-APPROVAL-LINK-HERE).
- [x] An updated research report containing the background, method, implementation, and preliminary results. Evidence: [Research report](../../../report/draft.md), containing background, method, implementation, and preliminary results, with limitations and pending validation identified.
- [x] A retrospective that records changes to the research question, method, scope, or interpretation. Evidence: [ Sprint 2 retrospective](retrospective.md). Draft pending team discussion and confirmation of changes and agreed actions.

| Criterion | Pass / Fail | Evidence link | Notes |
|---|---|---|---|
| The core implementation runs end to end on the approved sample | Pending Sprint 2 confirmation | [Recorded pipeline runs](../../REPRODUCE.md#recorded-runs) | The 2026-09-30 author-run container check passed all four stages and reproduced 14/14 tables, including one within numerical tolerance. A fresh Sprint 2 run remains to be confirmed. |
| The method is tested | Partial; validation pending | [Automated tests](../../../tests/); [Validation protocol](../../validation/README.md) | Automated tests and an evaluation design are documented. Add the latest successful CI run link. Human validation and scoring remain pending. |
| The group can explain why the result should be trusted or where it may fail | Pending team confirmation | [Research report](../../../report/draft.md); [Validation protocol](../../validation/README.md); [Reproduction limitations](../../REPRODUCE.md) | Reproducibility, evaluation procedures, and limitations are documented. Reproducing outputs does not establish detection accuracy; pending validation must remain explicit. |
| The preliminary analysis is supported by generated evidence rather than screenshots alone | Pass for existing preliminary outputs | [Prevalence table](../../../results/rq1_prevalence_by_rule.csv); [Reproduction record](../../REPRODUCE.md#recorded-runs) | Generated CSV results and a historical reproduction record support the preliminary analysis. This does not claim completed validation or a fresh Sprint 2 reproduction. |

| Kind | Primary rater | Second rater | Second-rater labels committed (PR #, date) | Primary labels committed after (PR #, date) | Cohen's kappa |
|---|---|---|---|---|---|
| Signals | jd | No independent second rater assigned; jd repeat rating planned for Sprint 3 | Not applicable; repeat rating tracked in #101 | Primary-label commit and date to be confirmed | Pending repeat rating and scoring |
| Lineage | jd | hk | Pending confirmation of Hina's committed labels | Pending confirmation of commit order and date | Pending both label sets and scoring |
| Drift | jd | la | Leticia reports completing 18 pairs; PR #90, commit date and merge status to be confirmed | Pending confirmation of Jerad's label commit and date | Pending both label sets and scoring |

## Demo script (12 minutes)

| Step | Content | Time | Presenter |
|---|---|---|---|
| 1 | Restate the research question: risky capabilities in copied agent skills—prevalence, reach, and drift. Explain that the method scans stored skill text and analyzes capability indicators, copying, and variant differences. | 1 min | Leticia Aderhold |
| 2 | In a fresh terminal, run `make test` and `make pipeline` using the approved sample; show the actual output and current CI status. Record any failure or limitation. | 3 min | Jerad Dunne |
| 3 | Show one generated preliminary table and one figure. Identify the script and command producing each, explain the observation, and distinguish it from interpretation. | 3 min | Jerad Dunne |
| 4 | Explain the validation sample, annotation protocol, and primary/second-rater assignments. Show precision and agreement scores only if generated; otherwise identify pending labels and scoring. | 2 min | Hina Kramer |
| 5 | Show PR #105 and its cross-member approving review, explain decisions D-024 and D-025, and show the metric dashboard with its date and any missing measures identified. | 2 min | Leticia Aderhold |
| 6 | Explain where results may fail, including textual matches without execution context and incomplete validation. Describe planned Sprint 3 work, including the signals repeat rating after the required interval. | 1 min | Hina Kramer |
- [ ] Working core implementation. Evidence: issue #21; add the merged PR and output path when complete.
- [ ] Automated tests for the implemented method. Evidence: issue #22; add CI run and test results.
- [ ] Validation sample and protocol. Evidence: issue #23 and `docs/validation/README.md`.
- [ ] Preliminary results with reproducible figures or tables. Evidence: issue #24; add paths under `results/` or `figures/`.
- [ ] At least one pull request reviewed by a member other than its author. Evidence: add reviewed PR link.
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
| Who (a member who did not write the README) and environment | Pending assignment to a member who did not write the README; record their operating system and Python version. |
| Date | Pending actual reproduction run. |
| Commit SHA | Pending; record the exact commit tested. |
| Steps followed (from README) | Planned: obtain a fresh copy, follow the README setup and approved-sample instructions, run tests and the pipeline, then compare generated outputs with committed results using the documented reproduction check. Record the actual commands followed. |
| Time to first result (minutes) | Pending; measure during the run. |
| Result matched committed output | Pending comparison; record yes/no and any numerical tolerance used. |
| Problems found (open issues) | Not yet assessed. Record failures, workarounds, and issue links after the run. |
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

| Metric | Sprint 1 | Sprint 2 |
|---|---|---|
| Points planned / completed | Pending verification from Sprint 1 backlog and closed issues | Pending final Sprint 2 backlog totals |
| Issues closed | Pending dated issue count | Pending dated issue count |
| PRs merged / merged with an approving review from another member | Pending verification of merged PRs and approvals | Pending totals; PR #105 is one verified cross-member approval and merge |
| Median PR first-review turnaround (hours) | Pending calculation | Pending calculation |
| Median cycle time (days) | Pending calculation | Pending calculation |
| Median PR open-to-merge time (hours) | Pending calculation | Pending calculation |
| CI pass rate | Pending calculation with reporting period stated | Pending calculation with reporting period stated |
| Rework items | Pending agreed definition and count | Pending agreed definition and count |
| Contribution share per member (min / max) | Pending calculation with contribution measure stated | Pending calculation for the three-member team, with contribution measure stated |
| Test count / coverage | Historical 2026-09-30 reproduction record reports 164 passing tests; coverage not verified | Current test count and coverage pending verification from the latest CI run |

## Backlog changes proposed for review

- Added: Pending confirmation at the Sprint 2 review. Proposed Sprint 3 follow-up includes the signals repeat rating tracked in #101 and any unresolved validation or rule-change work.
- Removed or cancelled: No removals or cancellations confirmed for this review; the team will record any agreed changes and their reasons.
- Re-estimated: No revised estimates confirmed for this review; the team will reassess remaining work and record updated story points where agreed.
  
## Applicability analysis update

[Static-analysis applicability comparison](../../research/APPLICABILITY.md) addresses issue #96. Rule-card/CWE reconciliation and teammate approval remain pending. No external analyzer experiment was performed.
- Added: redistribute work previously associated with Allie and update team documentation.
- Removed/cancelled: Allie from capacity, attendance, assignments, and review rotation because she dropped the course.
- Re-estimation proposed: reconcile remaining work and instructor-feedback tasks with three-person capacity; final estimates require team agreement.

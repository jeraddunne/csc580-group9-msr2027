# Sprint 3 review: analysis, integration, and communication

How to use: the Product Owner runs the review on Wed 2026-11-18. Every rubric bullet must link to evidence in this repository. Rubric weight: 25%.

Date: 2026-11-18. Product Owner: Leticia Aderhold. Scrum Master: Jerad Dunne.
Status: Prepared for the scheduled November 18 review. Attendance and the final sprint-goal assessment will be recorded after the review.

## Sprint goal check

- Sprint goal (draft wording from the updated planning document): By November 18, deliver a reviewed research report answering RQ1–RQ3 with traceable results, validation evidence, and clearly stated limitations; reproducible tables and figures; a documented release candidate; and complete presentation materials supported by an end-to-end demonstration rehearsal. Keep findings separate from interpretation and document the team's most important process improvement with before/after KPI evidence.
- Met: Pending assessment at the November 18 review.
- Current progress: Issues #28, #29, #32, #33, and #35 are completed. Final report review, presentation/rehearsal evidence, and remaining finalization checks must be assessed against their acceptance criteria before declaring the sprint goal achieved.

## Rubric review checklist (verbatim from the assignment)

The Sprint 3 review must include:

- [x] Final or near-final results addressing the research question. Evidence: completed #27; `report/draft.md`, Results and Evaluation and validation sections; linked result files and reviewer acceptance recorded in #27.
- [x] Robustness checks, sensitivity analysis, or comparison across meaningful subgroups. Evidence: completed #28; `results/sensitivity_summary.csv`; `results/rq3_threshold_sweep.csv`; Hina's acceptance confirmation.
- [x] Error analysis and manually inspected examples. Evidence: completed #29; `docs/validation/ERROR_ANALYSIS.md`; merged and reviewed PRs #145, #152, and #162.
- [x] Final figures and tables generated from the repository pipeline. Evidence: #30; successful clean-checkout regeneration at `18892ed` on November 10; report table-and-figure source map.
- [x] A complete draft report with citations and a clear separation between findings and interpretation. Evidence: #31; `report/draft.md`; confirm complete-draft review and acceptance.
- [x] A threat-to-validity section addressing dataset bias, measurement error, confounding, missing data, reproducibility, and generalizability. Evidence: completed #32; `THREATS_TO_VALIDITY.md`; report threats section; PRs #143 and #149.
- [x] A documented release or tagged version of the repository. Evidence: completed #33; published `v0.9.0-rc1` at `5211619`; release notes and recorded reproduction evidence.
- [x] A final demonstration plan and presentation materials. Evidence: #34; `docs/PRESENTATION_PLAN.md`; record the November 12 rehearsal outcome after it occurs.
- [x] A retrospective identifying the group's most important process improvement. Evidence: completed #35; Sprint 3 retrospective Section 9; PR review audit; Jerad's confirmation and Hina's acceptance review.

## Sprint 3 acceptance criteria (verbatim)

| Criterion | Pass / Fail | Evidence link | Notes |
|---|---|---|---|
| A new user can follow the README to reproduce the primary results | Pending final acceptance check | [Issue #33](https://github.com/jeraddunne/csc580-group9-msr2027/issues/33); Gemba walk below | Fresh-clone reproduction matched all 14 primary result CSVs. Confirm the recorded steps followed the README and satisfy the new-user requirement; the final-release fresh-machine check is tracked under #37. |
| The report answers the question with evidence | Pending final report review | [Report](../../../report/draft.md); [Issue #27](https://github.com/jeraddunne/csc580-group9-msr2027/issues/27); [Issue #31](https://github.com/jeraddunne/csc580-group9-msr2027/issues/31) | The draft presents RQ1–RQ3 findings with numerical evidence and validation limitations. Confirm final results integration and complete-draft acceptance before marking Pass. |
| Limitations are explicit | Pass | [Threats register](../../../THREATS_TO_VALIDITY.md); [Issue #32](https://github.com/jeraddunne/csc580-group9-msr2027/issues/32); [Report](../../../report/draft.md) | Completed #32 documents all six required threat areas, mitigations, and acknowledged limitations. |
| All major artifacts are traceable to issues, commits, pull requests, or decisions | Pending traceability audit | Traceability audit below; [Report source map](../../../report/draft.md#table-and-figure-sources) | The report maps tables and figures to sources and generation targets. Complete the audit of other major artifacts and record any missing links before marking Pass. |

## Traceability audit

| Artifact (figure, table, decision, dataset step) | Produced by (script) | Issue # | PR # | ADR | OK? |
|---|---|---|---|---|---|
| Table 1: population flow | Analysis pipeline via `make figures`, then `scripts/make_report_tables.py` via `make report-tables` | #30 | #153 | Not applicable | Regeneration recorded at `18892ed`; final report comparison pending |
| Table 2: validation precision | `scripts/annotation_kit.py` via `make validation-score`, then `scripts/make_report_tables.py` | #30, #31 | #153 | Not applicable | Regeneration recorded; final report comparison pending |
| Table 3: high-risk signal prevalence | Analysis pipeline via `make figures`, then `scripts/make_report_tables.py` | #30 | #153 | Not applicable | Regeneration recorded; final report comparison pending |
| Review workflow activity diagram | `scripts/make_workflow_diagrams.py` via `make workflow-diagrams` | #30 | #153 | Verify applicable decision reference | Regeneration recorded; workflow remains a proposed design |
| Supporting prevalence, reach, and drift plots | Analysis pipeline via `make figures` | #28, #30 | #44, #153 | Not applicable | Successful regeneration recorded; final report comparison pending |
| Sensitivity and subgroup results | Analysis pipeline; `results/sensitivity_summary.csv` and `results/rq3_threshold_sweep.csv` | #28 | #44 | Not applicable | Yes; acceptance confirmed in completed #28 |
| Manually inspected error examples | Authored `docs/validation/ERROR_ANALYSIS.md` with source and annotation evidence | #29 | #145, #152, #162 | Rule-change decisions tracked separately under #132 | Yes; Hina confirmed acceptance at `383d9c2` |
| Signal repeat-labeling agreement | Validation scoring; `results/validation_agreement.csv` | #101 | #166 | Verify applicable protocol decision reference | Completed; report consistency review tracked under #31 |
| Threats register and report coverage | Authored `THREATS_TO_VALIDITY.md` and report threats section | #32 | #143, #149 | Relevant decisions cited in register | Yes; six-area acceptance completed and row statuses documented |
| Release candidate and primary-result reproduction | Release notes, fresh-clone record, and fresh-runner checks | #33 | Release publication; no PR number confirmed here | Not applicable | Yes for #33: `v0.9.0-rc1` at `5211619`; final release tracked under #37 |
| Most important process improvement | `scripts/pr_review_audit.py`; retrospective Section 9 | #35 | #141, #148, #180 | Existing team merge rule; verify ADR reference if needed | Yes; team agreement and acceptance recorded in #35 |
| Dataset download and provenance | `scripts/download_samples.py`; `data/samples/MANIFEST.json` | Verify original dataset tracking issue | Verify original PR | Verify applicable dataset decision reference | Pending provenance-link check |

## Demo script (15 minutes, rehearsal for the final)

| Step | Content | Time | Presenter |
|---|---|---|---|
| 1 | Introduce the problem of copied agent skills and explain RQ1 prevalence, RQ2 reach, and RQ3 drift. Explain why scanner findings require human interpretation. | 1 min | Proposed: Leticia Aderhold |
| 2 | Describe the July 2026 GitSkills snapshot, the 12,965-content main population, content hashes as the unit of analysis, copy counts, and the severity-6 high-risk threshold. | 2 min | Proposed: Jerad Dunne |
| 3 | Demonstrate the documented setup and reproduction steps using a prepared clean checkout. Show the revision, run `make pipeline` and `make figures`, and inspect generated outputs. Explain validation and report-generation targets. If runtime exceeds the slot, use a clearly identified recording and saved run evidence. | 4 min | Proposed: Jerad Dunne |
| 4 | Show the main prevalence table and reach plot: 8.9% of contents match high-risk rules, or 11.2% weighted by copies; mean copies are 2.87 versus 2.23. Summarize variant differences and robustness checks. Distinguish association from causation. | 4 min | Proposed: Hina Kramer |
| 5 | Present worked false-positive and false-negative examples. Explain sample limits and agreement: drift 15/18 with kappa 0.745; lineage 57/58; signal repeat-labeling 61/69 with kappa 0.839. Distinguish inter-rater from intra-rater agreement. | 2 min | Proposed: Hina Kramer |
| 6 | Explain early reviewer assignment and approval from another member before merging. Show unapproved merges decreasing from 8/21 (38.1%) to 0/36 (0%) and median first-review time from 51.1 to 4.2 hours. Discuss alternative explanations; use other process metrics only where verified. | 2 min | Proposed: Leticia Aderhold |

## Gemba walk: fresh-clone reproduction record

| Field | Value |
|---|---|
| Who (a member who did not write the README; README only, no help) and environment | Leticia Aderhold; Windows 11 (10.0.26300-SP0), Python 3.12.1. README authorship and compliance with the README-only/no-help condition were not established by this record. |
| Date | 2026-11-03, 12:06 |
| Tag or commit SHA | Tested commit: `2cc74079245c14a452137d50dcf1fd6d11a7b9f9`. Issue #33 records release `v0.9.0-rc1` at `5211619`, with unchanged pipeline code and inputs and a separate fresh-runner check. |
| Steps followed | Created a fresh Git clone in `C:\dev\rc1-check`, checked out the tested commit, ran `windows/1-set-up.bat`, then `windows/2-run-pipeline.bat`. |
| Time to primary result (minutes) | 2.6 minutes for analysis; setup time was not recorded. |
| Result matched committed output | Yes. All 14 compared primary-result CSVs matched apart from line endings. Main population: 12,965; contents with a high-risk signal: 1,159. |
| Problems found (open issues) | None reported during the fresh Git-clone run. The final-release fresh-machine check is tracked separately under #37. |

Evidence: [Issue #33](https://github.com/jeraddunne/csc580-group9-msr2027/issues/33). This is a historical reproduction record, not a new November 18 review-day run. It demonstrates primary-result reproduction but does not establish the README-only/no-help acceptance condition or reproduction of every current report figure and table.

## Instructor feedback

| Feedback | Action | Owner | Issue # | Due (finalization) |
|---|---|---|---|---|
| | | | | |

## Velocity and KPIs at review

| Metric | Sprint 1 | Sprint 2 | Sprint 3 |
|---|---|---|---|
| Points planned / completed | Final totals require reconciliation with the dated dashboard | Final totals not verified; interim values are not final velocity | Pending sprint completion |
| Issues closed | Not verified | Not verified | Pending final issue count |
| PRs merged / merged with an approving review from another member | 21 / 13 (61.9% approved) | 36 / 36 (100% approved) | 5 / 5 through 2026-11-08; interim audit |
| Median PR first-review turnaround (hours) | 51.1 | 4.2 | Not verified |
| Median cycle time (days) | Not verified against the selected reporting window | Not verified | Pending final dashboard |
| Median PR open-to-merge time (hours) | 48.1 | 16.7 | Not verified |
| CI pass rate | Not verified for the full sprint window | Not verified for the full sprint window | Pending final measurement |
| Rework items | Not verified | Not verified | Pending final measurement |
| Contribution share per member (min / max) | Not verified for the selected roster and reporting window | Not verified | Pending final measurement |
| Test count / coverage | Review-revision evidence not verified here | Historical run at `8e2ce36`: 219 tests and 97% coverage; not a sprint-wide aggregate | Final review revision not yet verified |

Sources and scope: PR review figures come from `docs/lean-six-sigma/metrics/pr_review_audit.csv` and the evidence recorded in #35, PR #148, and PR #160. Sprint 3 approval figures are an interim snapshot through November 8, not current or final totals. Test count and coverage describe a specific historical revision. Final review metrics will be recorded with their source, revision, and reporting window; unavailable values must not be treated as zero.

## Backlog changes for finalization

Status: Proposed priorities prepared on 2026-11-12. Record team agreement and any changes after the Sprint 3 review.

- Must fix before submission:
  - Complete final report review and resolve outdated or inconsistent status statements under #31.
  - Confirm final results and generated tables and figures match the report; link the reproduction evidence and designated release revision.
  - Complete the presentation rehearsal, record its actual outcome, and address blocking problems under #34.
  - Complete the final-release reproduction requirements tracked under #37.
  - Verify the control plan, artifact traceability, AI-use disclosures, and required submission materials.
  - Update completed issues' project statuses to Done.

- Nice to have:
  - Improve slide readability, transitions, and speaker notes after rehearsal.
  - Add explanatory examples or visual refinements where they improve clarity without delaying required work.
  - Document future research and rule improvements that are outside the submission scope.

- Cancelled:
  - No additional cancellations are recorded in this update. Record any team-approved cancellation with its issue number, reason, and effect on the deliverables.

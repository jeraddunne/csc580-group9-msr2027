# Sprint 3 planning: analysis, integration, and communication (Improve phase)

How to use: the Scrum Master fills this in during Sprint 3 planning on Thu 2026-10-29. Candidate items become GitHub issues in milestone `Sprint 3`. This sprint carries the largest weight (25%) and feeds the final demonstration (20%). Plan the report and presentation work as first-class backlog items, not leftovers.

Dates: Thu 2026-10-29 to Wed 2026-11-18. Review and retro: Wed 2026-11-18. Check-ins: Thu 2026-11-05, Thu 2026-11-12 (also rehearsal 1).
Product Owner: Leticia Aderhold. Scrum Master: Jerad Dunne. Developers/Researchers: Leticia Aderhold, Jerad Dunne, and Hina Kramer. The team has three members following Allie Hodges's departure, recorded in D-025.

## Sprint goal

By November 18, deliver a reviewed research report answering RQ1–RQ3 with traceable results, validation evidence, and clearly stated limitations; reproducible tables and figures; a documented release candidate; and complete presentation materials supported by an end-to-end demonstration rehearsal. Keep observed findings separate from interpretation, distinguish scanner signals from confirmed risky capabilities, and document the team's most important process improvement with before/after KPI evidence.

## Progress update — 2026-11-12

- Report: complete final consistency checks and teammate review under #31.
- Reproducibility: report-generation work was addressed in merged PR #176 under #30.
- Presentation: complete the rehearsal scheduled for November 12 at 5 p.m. Eastern and record its actual outcome under #34.
- Process improvement: team agreement is confirmed in #35; record the confirmation and supporting PR review metrics in the retrospective and report appendix.
- Finalization: verify remaining acceptance criteria and release evidence before marking the sprint goal achieved.

This update records current work and remaining tasks; it does not indicate that the sprint or its final review has been completed.

## Capacity

| Member | Available hours this sprint | Planned points | Notes |
|---|---|---|---|
| Leticia Aderhold | Pending member confirmation | Pending planning record verification | Product Owner; contributes to research, documentation, and presentation work. |
| Jerad Dunne | Pending member confirmation | Pending planning record verification | Scrum Master; contributes to research, implementation, and review. |
| Hina Kramer | Pending member confirmation | Pending planning record verification | Contributes to research, validation, and review. |
| Total | Not calculated; member estimates pending | Not calculated; verified allocations pending | Sprint 2 final velocity requires verification; do not substitute interim completed points. |

Capacity update — 2026-11-12: Original Sprint 3 capacity estimates have not yet been verified. Members should confirm any recorded planning estimates and separately report remaining availability through November 18. Actual hours worked must not be substituted for planned capacity.

## Candidate backlog (rubric deliverables for Sprint 3)

| # | Item (rubric deliverable) | Acceptance criteria | Estimate | Owner | Issue # |
|---|---|---|---|---|---|
| S3-1 | Final or near-final results addressing the research question | Report answers RQ1–RQ3 with traceable pipeline results, validation evidence, and sample limitations; label-based reach results are reviewed before use. | Verify issue estimate | Verify assigned owner | #27 |
| S3-2 | Robustness checks and sensitivity analysis | Document similarity-threshold, severity-cutoff, valid-front-matter, template-family, and most-copied-content sensitivity checks with reproducible outputs and stated limitations. | Verify issue estimate | Verify assigned owner | #28 |
| S3-3 | Error analysis and manually inspected examples | Provide an error taxonomy with counts, adjudicated disagreements, and at least five inspected examples; distinguish category misses from file-level detection. | Verify issue estimate | Verify assigned owner | #29 |
| S3-4 | Final figures and tables generated from the repository pipeline | Document generation targets and sources for every numbered table and figure; reproduce outputs from a clean checkout using the required Make targets. | Verify issue estimate | Verify assigned owner | #30 |
| S3-5 | Complete draft report with citations and separate findings and interpretation | All required sections are drafted; citations resolve; numerical claims trace to evidence; Results and Discussion are separate; a member other than the author reviews the complete draft. | 5; shown in issue | Jerad Dunne; shown in issue | #31 |
| S3-6 | Threats to validity | Address dataset bias, measurement error, confounding, missing data, reproducibility, and generalizability in `THREATS_TO_VALIDITY.md` and the report; accurately describe rater and sample limitations. | Verify issue estimate | Verify assigned owner | #32 |
| S3-7 | Documented release or tagged repository version | Verify the designated release tag, release notes, reproduction commands, and associated outputs; identify the exact revision used for the final demonstration. | Verify issue estimate | Verify assigned owner | #33 |
| S3-8 | Final demonstration plan and presentation materials | `docs/PRESENTATION_PLAN.md` covers the research question, pipeline, implementation, results, and limitations; final slides are linked; at least one end-to-end rehearsal has a recorded outcome. | 3; shown in issue | Jerad Dunne; shown in issue | #34 |
| S3-9 | Retrospective naming the most important process improvement | Section 9 names the team-confirmed improvement, when introduced, before/after KPI values, evidence sources, and alternative explanations; wording is aligned with the report and presentation. | 1; shown in issue | Jerad Dunne; shown in issue | #35 |
| S3-10 | README reproduction in a clean environment | A member other than the README author reproduces primary results from a fresh clone using the README; record revision, environment, commands, duration, problems, and output comparison. | Not yet verified | Confirm independent reproducer | Confirm tracking issue |
| S3-11 | Traceability audit | Check that report figures, tables, and substantive claims link to their source results and relevant issues, PRs, commits, or ADRs; record audit findings and fixes. | Not yet verified | To be confirmed | Confirm tracking issue |
| S3-12 | Related work with verified citations | Include at least six relevant sources in `report/references.bib`; verify bibliographic details against original publications and confirm citations resolve in the report. | Not yet verified | To be confirmed | Confirm tracking issue |
| S3-13 | FMEA-style ranking of capability categories | Provide a reproducible ranking with documented severity, occurrence, and detection definitions; trace inputs to validation results and explain uncertainty, including the limits of zero observed misses. | Not yet verified | To be confirmed | Confirm tracking issue |

## Risks pulled from the FMEA register

| Risk | RPN | Mitigation this sprint | Owner |
|---|---|---|---|
| Results change late and figures become stale | Verify in FMEA register | Regenerate affected tables and figures using documented Make targets after result changes. Check that the report and slides use outputs from the same revision. | Proposed: result author and reviewing teammate |
| Report writing is concentrated on one member (R06) | 147; verify against current register | Confirm section owners and backups in `docs/workspace/WORK_SIGNUP.md`; use teammate review and the documented P-01 section 10 scope priorities if time runs short. | Product Owner: Leticia Aderhold |
| A member is unavailable near the deadline (R05) | 108; verify against current register | Confirm a backup for each report section and demonstration segment. Keep slides, notes, commands, and evidence accessible to the three-member team. | Scrum Master: Jerad Dunne |
| Live demonstration fails | Verify in FMEA register | Rehearse end to end, record failures and fixes, and prepare a recording and static figures as backups. Document the tested revision, commands, and fallback steps in `docs/PRESENTATION_PLAN.md`. | Proposed: demonstration presenter and backup; confirm in presentation plan |

Risk update — 2026-11-12: Confirm RPN values against the current FMEA register and agree on proposed owners. Backup materials and rehearsal outcomes must be verified before they are recorded as complete.

## Improve phase exit criteria (DMAIC)

- [x] The improvement to the analysis (robustness, error analysis) is implemented and its effect on the answer is stated. Evidence: completed issues #28 and #29. In #28, the mean-copy ratio remains above 1 across all six sensitivity scenarios, while its magnitude and signal prevalence vary; these are scanner-defined associations, not causal findings.
- [x] The process improvement with the largest measured effect this semester is named with before and after numbers.
- [x] Every report figure and table is reproducible from a tagged commit.
- [x] The threats-to-validity table has a status for every row. Evidence: `THREATS_TO_VALIDITY.md`; completed issue #32.
- [x] Control plan drafted for finalization (`docs/lean-six-sigma/CONTROL_PLAN.md`): what is checked, by whom, and when, before submission.

## Planning meeting notes

- Date: 2026-10-29. Facilitator: Jerad Dunne.
- Attendees: [ ] Leticia Aderhold [ ] Jerad Dunne [ ] Hina Kramer
- Items pulled into the sprint (issue numbers):
- Items explicitly deferred and why:
- Carry-over from Sprint 2:

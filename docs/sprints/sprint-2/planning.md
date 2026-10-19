# Sprint 2 planning: implementation and validation (Analyze phase)

How to use: review team capacity, prioritize the backlog, and confirm an owner, estimate in story points, acceptance criteria, and definition of done for each committed task. Track instructor-feedback requests in `docs/sprints/sprint-2/instructor-feedback.md`.

Dates: Thu 2026-10-08 to Wed 2026-10-28. Review and retrospective: Wed 2026-10-28. Check-ins: Thu 2026-10-15 and Thu 2026-10-22. Product Owner: Jerad Dunne. Scrum Master: Hina Kramer. Developers/Researchers: Leticia Aderhold, Jerad Dunne, and Hina Kramer.

## Sprint goal

By October 28, the team will have the core mining and analysis pipeline running end to end on the approved sample, with automated tests, reproducible preliminary results, updated report sections, and documented validation evidence, including second-rater labels and inter-rater agreement.

## Capacity

| Member | Available hours this sprint | Planned points | Notes |
|---|---:|---|---|
| Leticia Aderhold | 8 | Pending reconciliation | Preliminary-results documentation, research-report updates, drift second-rating, and pull-request reviews |
| Jerad Dunne | 12 | Pending reconciliation | Product Owner; core implementation, automated tests, scoring, and technical integration |
| Hina Kramer | 6 | Pending reconciliation | Scrum Master; validation protocol, lineage second-rating, coordination, retrospective, and pull-request reviews |
| **Total** | **26** | **Pending reconciliation** | Sprint 1 velocity: **15 points** (October 4 dashboard snapshot) |

Planned points remain pending until the team reconciles backlog estimates, completed carry-in work, and newly added instructor-feedback tasks with available capacity.

Include second-rater labeling time in available hours. Per D-024, Leticia Aderhold second-rates drift and Hina Kramer second-rates lineage. Signals have no second rater. Allow approximately 4 minutes per drift pair and 2 minutes per lineage pair.

## Candidate backlog

Estimates are story points, not hours. Added feedback tasks require team estimates and prioritization before the committed total is finalized. Pending means the current status must be checked on the linked issue.

| # | Item | Estimate (points) | Owner | Issue # | Acceptance criteria | Status |
|---|---|---|---|---|---|---|
| S2-1 | Core mining and analysis implementation | 5 | Jerad Dunne | #21 | Core method runs on the approved sample with documented inputs and outputs. | Carried in / done |
| S2-2 | Automated tests | 3 | Jerad Dunne | #22 | Tests cover important parsing, transformation, matching, or metric functions; results are linked. | Pending |
| S2-3 | Validation sample and annotation protocol | 3 | Hina Kramer | #23 | Sample, labeling instructions, blindness rules, and evaluation procedure are documented. | Pending |
| S2-4 | Reproducible preliminary results | 2 | Leticia Aderhold | #24 | Figures or tables include the commands and evidence needed to reproduce them. | Carried in / done |
| S2-5 | Non-author pull-request reviews | Confirm team estimate | Every remaining member | Record reviewed PR numbers | Each member reviews at least one other member's PR and records what was verified. | Pending |
| S2-6 | Updated research report | 3 | Leticia Aderhold | #25 | Background, method, implementation, and preliminary results are drafted with citations; observations and interpretations are separated. | Pending |
| S2-7 | Sprint retrospective | 2 | Hina Kramer | #26; PR #93 | Retrospective records evidence, proposed improvements, and changes to question, method, scope, or interpretation; final outcomes are confirmed October 28. | Draft pending review |
| S2-8 | Second-rater round-one labels | 3 | Leticia Aderhold: drift; Hina Kramer: lineage | #90; #99; #100 | D-024 assignments are followed, independent labels are committed, and blindness is preserved. Signals have no second rater. | Pending |
| S2-9 | Validation scoring and error analysis | 3 | Jerad Dunne | #90; #99; #100 | Validation outputs and agreement measures are reported with error analysis and limitations. | Pending |
| S2-10 | Lean Six Sigma capability check | 2 | Hina Kramer | Confirm linked process-metrics issue | Capability analysis identifies the metric, method, evidence, and limitations. | Pending |
| S2-11 | Rule rationale and provenance | Team estimate pending | Jerad Dunne | #95 | Each rule documents its problem, bad example, source, and known false positives; threat-model and severity rationale are explained. | Pending |
| S2-12 | Applicability of established rules | Team estimate pending | Jerad Dunne | #96 | Applicability to SKILL.md text, bundled scripts, or neither is documented with reasons. | Pending |
| S2-13 | Known-positive skills check | Team estimate pending | Jerad Dunne; selection checked by another member | #97 | About ten known-positive skills are selected without inspecting rule patterns; detections and misses are reported. | Pending |
| S2-14 | Human-in-the-loop risk-review workflow | Team estimate pending | Jerad Dunne; reviewed by Hina Kramer and Leticia Aderhold | #98 | Use case and swimlane activity diagrams explain how people use scanner results; the report describes the workflow. | Pending |
| S2-15 | Team-process evidence and task definitions of done | Team estimate pending | Hina Kramer and Leticia Aderhold | #102 | Check-in notes, obstacles, and contributions are documented; each open Sprint 2 task has acceptance criteria and a definition of done. | Pending |
| S2-16 | Current AI-use log | Team estimate pending | Every member | #104 | Each member records Sprint 2 AI assistance or explicitly states none was used. | Pending |

Definition of done: the task's acceptance criteria are met, evidence is linked, applicable tests or documentation checks are recorded, required non-author review is completed, and AI assistance is logged.

Signals intra-rater round 2 is tracked in #101 for Sprint 3 because of the required 14-day gap. It is excluded from the Sprint 2 commitment.

## Sprint risks: registered and additional

| Risk | RPN | Mitigation this sprint | Owner |
|---|---:|---|---|
| Method produces results that cannot be validated | Not scored in current FMEA register | Guideline fixed before scoring; rules frozen once round one starts | Hina Kramer |
| Second-rater disagreement or primary labels seen by the second rater (R11) | 140 | Practice items, blindness rule, adjudication during error analysis, and kappa reported | Jerad Dunne |
| Review delays block merges (R12) | 90 | 48-hour review SLA, reviewer rotation, and first-review KPI checked at each check-in | Hina Kramer |
| Uneven contribution (R06) | 147 | Contribution shares checked at each check-in and work reassigned when necessary | Hina Kramer |
| Test coverage lags implementation | Not scored in current FMEA register | Tests included in the Definition of Done for every pipeline PR | Jerad Dunne |
| Report writing left to the end | Not scored in current FMEA register | Report sections assigned as issues and drafted before the final week | Leticia Aderhold |

The validation-method, test-coverage, and report-writing risks are additional planning risks without scores in the current FMEA register. The team must assess their severity, occurrence, and detection before assigning RPNs. No scores have been estimated here.

## Analyze phase exit criteria (DMAIC)

- [ ] The core method is implemented and its inputs and outputs are documented (SIPOC updated).
- [ ] Preliminary results exist, with a stated reason to trust them and where they may fail.
- [ ] Manual validation has produced an inter-rater agreement statistic between the primary rater and a teammate second rater.
- [ ] Sources of variation in results are listed (sampling, thresholds, parsing failures, rater disagreement) and at least one is quantified.
- [ ] Process KPIs are compared against the Sprint 1 baseline; Sprint 1 kaizen actions are checked for effect.

## Planning meeting notes

- Date: 2026-10-08. Facilitator: Hina Kramer.
- Attendees: [x] Leticia Aderhold [x] Jerad Dunne [x] Hina Kramer
- Team change: Allie Hodges dropped the course and was removed from Sprint 2 capacity, assignments, and review rotation. Jerad Dunne assumed the Product Owner responsibilities.
- Items pulled into the sprint: #21, #22, #23, #24, #25, and #26, plus the applicable second-rater labelling, validation-scoring, and process-capability work.
- Items explicitly deferred and why: Work requiring more capacity than the three remaining members can provide will be prioritized according to the Sprint 2 rubric and carried forward with a documented reason.
- Carry-over from Sprint 1: Complete any outstanding reviewed-PR, process-metrics, and sprint-documentation requirements; obtain required approvals on open pull requests.

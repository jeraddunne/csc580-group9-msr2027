## Sprint 2 planning: implementation and validation (Analyze phase)

Dates: Thu 2026-10-08 to Wed 2026-10-28. Review and retrospective: Wed 2026-10-28. Check-ins: Thu 2026-10-15 and Thu 2026-10-22. Product Owner: Jerad Dunne. Scrum Master: Hina Kramer. Developers/Researchers: Leticia Aderhold, Jerad Dunne, and Hina Kramer.

## Sprint goal

By October 28, the team will have the core mining and analysis pipeline running end to end on the approved sample, with automated tests, reproducible preliminary results, updated report sections, and documented validation evidence, including second-rater labels and inter-rater agreement.

## Capacity

| Member | Available hours this sprint | Planned points | Notes |
|---|---:|---:|---|
| Leticia Aderhold | 8 | 3 | Preliminary-results documentation, research-report updates, Drift second-rating work, and pull-request reviews |
| Jerad Dunne | 12 | 4 | Product Owner; core implementation, automated tests, scoring, and technical integration |
| Hina Kramer | 6 | 2 | Scrum Master; validation protocol, coordination, retrospective, and pull-request reviews |
| **Total** | **26** | **9** | Sprint 1 velocity: **9 points** |

Include each second rater’s labelling time in their hours: approximately 3 minutes per signal item, 2 minutes per lineage pair, and 4 minutes per drift pair.

## Candidate backlog

| # | Item | Estimate | Owner | Issue # |
|---|---|---:|---|---|
| S2-1 | Working implementation of the core mining, extraction, similarity, classification, traceability, or visualization method | 5 | Jerad Dunne | #21 |
| S2-2 | Automated tests for important parsing, transformation, matching, or metric functions | 3 | Jerad Dunne | #22 |
| S2-3 | Validation sample, manual annotation protocol, or other evaluation design | 3 | Hina Kramer | #23 |
| S2-4 | Preliminary results with reproducible figures or tables | 2 | Leticia Aderhold | #24 |
| S2-5 | At least one pull request reviewed by a different team member than the author | 1 each | Every remaining member | — |
| S2-6 | Updated research report containing the background, method, implementation, and preliminary results | 3 | Leticia Aderhold | #25 |
| S2-7 | Retrospective recording changes to the research question, method, scope, or interpretation | 2 | Hina Kramer | #26 |
| S2-8 | Second-rater round-one labels committed | 3 | Leticia Aderhold and Hina Kramer | #53/related validation issues |
| S2-9 | Validation scored and error analysis started | 3 | Jerad Dunne | Related validation issue |
| S2-10 | Lean Six Sigma capability check of the pipeline | 2 | Hina Kramer | Related process-metrics issue |

## Risks pulled from the FMEA register

| Risk | RPN | Mitigation this sprint | Owner |
|---|---:|---|---|
| Method produces results that cannot be validated | Confirm from FMEA | Guideline fixed before scoring; rules frozen once round one starts | Hina Kramer |
| Second-rater disagreement or primary labels seen by the second rater (R11) | 140 | Practice items, blindness rule, adjudication during error analysis, and kappa reported | Jerad Dunne |
| Review delays block merges (R12) | 90 | 48-hour review SLA, reviewer rotation, and first-review KPI checked at each check-in | Hina Kramer |
| Uneven contribution (R06) | 147 | Contribution shares checked at each check-in and work reassigned when necessary | Hina Kramer |
| Test coverage lags implementation | Confirm from FMEA | Tests included in the Definition of Done for every pipeline PR | Jerad Dunne |
| Report writing left to the end | Confirm from FMEA | Report sections assigned as issues and drafted before the final week | Leticia Aderhold |

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

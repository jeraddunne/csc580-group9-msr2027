# Sprint 2 planning: implementation and validation (Analyze phase)

How to use: the Scrum Master fills this in during Sprint 2 planning on Thu 2026-10-08. Candidate items become GitHub issues in milestone `Sprint 2`. Use the Sprint 1 velocity as the planning ceiling. Rubric weight: 20%.

Dates: Thu 2026-10-08 to Wed 2026-10-28. Review and retro: Wed 2026-10-28. Check-ins: Thu 2026-10-15, Thu 2026-10-22.
Product Owner: Allie Hodges. Scrum Master: Hina Kramer. Developers/Researchers: all four.

## Sprint goal

> Example shape: "By Oct 28 the scanner, variant linking, and reach statistics run end to end on the sample, are covered by tests, and validation reports precision and inter-rater agreement."

Sprint goal:

## Capacity

| Member | Available hours this sprint | Planned points | Notes |
|---|---|---|---|
| Leticia Aderhold | | | |
| Jerad Dunne | | | |
| Allie Hodges | | | |
| Hina Kramer | | | |
| Total | | | Sprint 1 velocity: ___ points |

Include each second rater's labelling time in their hours: about 3 minutes per signal item, 2 per lineage pair, 4 per drift pair.

## Candidate backlog (rubric deliverables for Sprint 2)

| # | Item (rubric deliverable) | Acceptance criteria | Estimate | Owner | Issue # |
|---|---|---|---|---|---|
| S2-1 | Working implementation of the core mining, extraction, similarity, classification, traceability, or visualization method | `make pipeline` runs end to end on the sample and writes to `results/` and `figures/`; design decision recorded as an ADR | | | #21 |
| S2-2 | Automated tests for important parsing, transformation, matching, or metric functions | `pytest` covers each core function with at least one normal and one edge case; CI green on `main` | | | #22 |
| S2-3 | Validation sample, manual annotation protocol, or other evaluation design | Protocol in `docs/validation/` with sample sizes, labels, primary rater and teammate second rater, blindness rule, inter-rater Cohen's kappa, optional intra-rater round 2; tools `python scripts/annotation_kit.py sample`, `sheet`, `ui`, `import`, `score` | | | #23 |
| S2-4 | Preliminary results with reproducible figures or tables | Every figure or table in the report is produced by a script and named in `results/README.md` or `figures/README.md` | | | #24 |
| S2-5 | At least one pull request reviewed by a different team member than the author | Every PR merged with an approving review from another member; link at least one review with substantive comments in the sprint review | | Every member | |
| S2-6 | Updated research report containing the background, method, implementation, and preliminary results | Sections in `report/draft.md` written in prose with citations from `report/references.bib`; sections owned by different members | | | #25 |
| S2-7 | Retrospective that records changes to the research question, method, scope, or interpretation | `docs/sprints/sprint-2/retrospective.md` section 8 completed | | | #26 |
| S2-8 | Second-rater round 1 labels committed | Each second rater's label file merged by Fri 2026-10-16 in a PR containing only that file; primary-rater files for a kind committed only afterwards | | Second raters | |
| S2-9 | Validation scored and error analysis started | `annotation_kit.py score` run by Tue 2026-10-27; precision, recall estimate, and inter-rater kappa in `results/`; disagreements listed with adjudicated readings | | | |
| S2-10 | Lean Six Sigma: capability check of the pipeline | Pipeline runtime and output stability recorded across 3 runs on at least two machines; variance noted in the dashboard | | | |

## Risks pulled from the FMEA register

| Risk | RPN | Mitigation this sprint | Owner |
|---|---|---|---|
| Method produces results that cannot be validated | | Guideline fixed before scoring; rules frozen once round 1 starts | |
| Second-rater disagreement or primary labels seen by the second rater (R11) | 140 | Practice items, blindness rule, adjudication in error analysis, kappa reported | Product Owner |
| Review delays block merges (R12) | 90 | 48-hour review SLA; reviewer rotation; first-review KPI read at each check-in | Scrum Master |
| Uneven contribution (R06) | 147 | Contribution shares read at each check-in; rebalance sign-ups | Scrum Master |
| Test coverage lags implementation | | Tests are part of the Definition of Done for every pipeline PR | |
| Report writing left to the end | | Report sections scheduled as issues in week 1 | |

## Analyze phase exit criteria (DMAIC)

- [ ] The core method is implemented and its inputs and outputs are documented (SIPOC updated).
- [ ] Preliminary results exist, with a stated reason to trust them and where they may fail.
- [ ] Manual validation has produced an inter-rater agreement statistic between the primary rater and a teammate second rater.
- [ ] Sources of variation in results are listed (sampling, thresholds, parsing failures, rater disagreement) and at least one is quantified.
- [ ] Process KPIs are compared against the Sprint 1 baseline; Sprint 1 kaizen actions are checked for effect.

## Planning meeting notes

- Date: 2026-10-08. Facilitator: Hina Kramer.
- Attendees: [ ] Leticia Aderhold [ ] Jerad Dunne [ ] Allie Hodges [ ] Hina Kramer
- Items pulled into the sprint (issue numbers):
- Items explicitly deferred and why:
- Carry-over from Sprint 1:

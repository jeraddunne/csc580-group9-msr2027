# Sprint 2 planning: implementation and validation (Analyze phase)

How to use: the Scrum Master fills this in during Sprint 2 Planning on Thu 2026-10-08. Candidate items become GitHub issues in milestone `Sprint 2`. Use the Sprint 1 velocity as the planning ceiling. Rubric weight: 20%.

Dates: Thu 2026-10-08 to Wed 2026-10-28. Review and retro: Wed 2026-10-28. Check-ins: Thu 2026-10-15, Thu 2026-10-22.
Product Owner: Allie Hodges. Scrum Master: Hina Kramer. Developers/Researchers: all four.

## Sprint goal

> Example shape: "By Oct 28 the core method runs end to end on the approved sample, is covered by tests, and produces preliminary tables and figures with a written validation protocol."

Sprint goal:

## Capacity

| Member | Available hours this sprint | Planned points | Notes |
|---|---|---|---|
| Leticia Aderhold | | | |
| Jerad Dunne | | | |
| Allie Hodges | | | |
| Hina Kramer | | | |
| Total | | | Sprint 1 velocity: ___ points |

## Candidate backlog (rubric deliverables for Sprint 2)

| # | Item (rubric deliverable) | Acceptance criteria | Estimate | Owner | Issue # |
|---|---|---|---|---|---|
| S2-1 | Working implementation of the core mining, extraction, similarity, classification, traceability, or visualization method | `make pipeline` runs end to end on the approved sample and writes to `results/` and `figures/`; design decision recorded as an ADR | | | |
| S2-2 | Automated tests for important parsing, transformation, matching, or metric functions | `pytest` covers each core function with at least one normal and one edge case; CI green on `main` | | | |
| S2-3 | Validation sample, manual annotation protocol, or other evaluation design | Protocol document in `docs/` with sample size, sampling method, labels, and inter-rater agreement plan (Cohen's kappa or percent agreement) | | | |
| S2-4 | Preliminary results with reproducible figures or tables | Every figure or table in the report is produced by a script and named in `results/README.md` or `figures/README.md` | | | |
| S2-5 | At least one pull request reviewed by a different team member than the author | Review comments visible; reviewer differs from author; reviewer ran the code | | | |
| S2-6 | Updated research report containing the background, method, implementation, and preliminary results | Sections in `report/draft.md` written in prose with citations from `report/references.bib` | | | |
| S2-7 | Retrospective that records changes to the research question, method, scope, or interpretation | `docs/sprints/sprint-2/retrospective.md` section 8 completed | | | |
| S2-8 | Manual validation executed on a first batch | At least 30 items labeled by two members; agreement computed and stored in `results/` | | | |
| S2-9 | Error analysis started | Failure modes listed with examples in `docs/` or the report | | | |
| S2-10 | Lean Six Sigma: capability check of the pipeline | Pipeline runtime and output stability recorded across 3 runs; variance noted in the dashboard | | | |

## Risks pulled from the FMEA register

| Risk | RPN | Mitigation this sprint | Owner |
|---|---|---|---|
| Method produces results that cannot be validated | | Design the annotation protocol before running the method at scale | |
| Test coverage lags implementation | | Tests are part of the Definition of Done for every pipeline PR | |
| Report writing left to the end | | Assign report sections as issues with owners in week 1 | |
| | | | |

## Analyze phase exit criteria (DMAIC)

- [ ] The core method is implemented and its inputs and outputs are documented (SIPOC updated).
- [ ] Preliminary results exist and the group can state why they should be trusted and where they may fail.
- [ ] Manual validation has produced an agreement statistic.
- [ ] Sources of variation in results are listed (sampling, thresholds, parsing failures) and at least one has been quantified.
- [ ] Process KPIs compared against the Sprint 1 baseline; the Sprint 1 kaizen actions are checked for effect.

## Planning meeting notes

- Date: 2026-10-08. Facilitator: Hina Kramer.
- Items pulled into the sprint (issue numbers):
- Items explicitly deferred and why:
- Carry-over from Sprint 1:

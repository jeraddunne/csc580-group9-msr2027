# Sprint 2 planning: implementation and validation (Analyze phase)

How to use: fill this in during Sprint 2 planning on Thu 2026-10-08. Candidate items become GitHub issues in milestone `Sprint 2`. Use the Sprint 1 velocity as the planning ceiling. Rubric weight: 20%.

Dates: Thu 2026-10-08 to Wed 2026-10-28. Review and retro: Wed 2026-10-28. Check-ins: Thu 2026-10-15, Thu 2026-10-22.
Product Owner, Scrum Master, Developer/Researcher: Jerad Dunne (solo, ADR-0005).

## Sprint goal

> Example shape: "By Oct 28 the scanner, variant linking, and reach statistics run end to end on the sample, are covered by tests, and the first validation batch has an agreement statistic."

Sprint goal:

## Capacity

| Member | Available hours this sprint | Planned points | Notes |
|---|---|---|---|
| Jerad Dunne | | | Sprint 1 velocity: ___ points |

## Candidate backlog (rubric deliverables for Sprint 2)

| # | Item (rubric deliverable) | Acceptance criteria | Estimate | Issue # |
|---|---|---|---|---|
| S2-1 | Working implementation of the core mining, extraction, similarity, classification, traceability, or visualization method | `make pipeline` runs end to end on the sample and writes to `results/` and `figures/`; design decision recorded as an ADR | | #21 |
| S2-2 | Automated tests for important parsing, transformation, matching, or metric functions | `pytest` covers each core function with at least one normal and one edge case; CI green on `main` | | #22 |
| S2-3 | Validation sample, manual annotation protocol, or other evaluation design | Protocol in `docs/validation/` with sample size (about 150 items, stratified), labels, intra-rater agreement plan (re-label a random 30% at least 7 days later, Cohen's kappa), and optional second rater; tools `python scripts/annotation_kit.py sample`, `sheet`, `score` | | #23 |
| S2-4 | Preliminary results with reproducible figures or tables | Every figure or table in the report is produced by a script and named in `results/README.md` or `figures/README.md` | | #24 |
| S2-5 | At least one pull request reviewed by a different team member than the author | Solo substitute: self-review protocol (ADR-0005). Request an external review from the instructor or a classmate on the validation or report PR and link it if obtained | | |
| S2-6 | Updated research report containing the background, method, implementation, and preliminary results | Sections in `report/draft.md` written in prose with citations from `report/references.bib` | | #25 |
| S2-7 | Retrospective that records changes to the research question, method, scope, or interpretation | `docs/sprints/sprint-2/retrospective.md` section 8 completed | | #26 |
| S2-8 | Manual validation executed on a first batch | At least 30 items labeled; re-label batch scheduled at least 7 days later; agreement stored in `results/` | | |
| S2-9 | Error analysis started | Failure modes listed with examples in `docs/validation/` or the report | | |
| S2-10 | Lean Six Sigma: capability check of the pipeline | Pipeline runtime and output stability recorded across 3 runs; variance noted in the dashboard | | |

## Risks pulled from the FMEA register

| Risk | RPN | Mitigation this sprint |
|---|---|---|
| Method produces results that cannot be validated | | Write the annotation guideline before labeling at scale |
| Single-annotator validation is unreliable or biased (R11) | | Written guideline, intra-rater re-label, request a second rater |
| Test coverage lags implementation | | Tests are part of the Definition of Done for every pipeline PR |
| Report writing left to the end | | Report sections scheduled as issues in week 1 |

## Analyze phase exit criteria (DMAIC)

- [ ] The core method is implemented and its inputs and outputs are documented (SIPOC updated).
- [ ] Preliminary results exist, with a stated reason to trust them and where they may fail.
- [ ] Manual validation has produced an agreement statistic (intra-rater kappa, plus second-rater agreement if available).
- [ ] Sources of variation in results are listed (sampling, thresholds, parsing failures) and at least one is quantified.
- [ ] Process KPIs are compared against the Sprint 1 baseline; Sprint 1 kaizen actions are checked for effect.

## Planning notes

- Date: 2026-10-08. Facilitator: Jerad Dunne.
- Items pulled into the sprint (issue numbers):
- Items explicitly deferred and why:
- Carry-over from Sprint 1:

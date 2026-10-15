# Sprint 2 review: implementation and validation

Review on Wed 2026-10-28.
Date: 2026-10-28. Product Owner: Jerad Dunne. Scrum Master: Hina Kramer.

Present: [ ] Leticia Aderhold [ ] Jerad Dunne [ ] Hina Kramer [ ] Instructor

## Sprint goal check

> By 2026-10-28, the team will have the core mining and analysis pipeline running end-to-end on the approved sample, automated tests, reproducible preliminary results, updated report sections, and documented validation including second-rater labels and inter-rater agreement.

Met: [ ] Yes [ ] Partly [ ] No

## Rubric review checklist (verbatim from the assignment)

The Sprint 2 review must include:

- [ ] Working core implementation. Evidence: issue #21; add the merged PR and output path when complete.
- [ ] Automated tests for the implemented method. Evidence: issue #22; add CI run and test results.
- [ ] Validation sample and protocol. Evidence: issue #23 and `docs/validation/README.md`.
- [ ] Preliminary results with reproducible figures or tables. Evidence: issue #24; add paths under `results/` or `figures/`.
- [ ] At least one pull request reviewed by a member other than its author. Evidence: add reviewed PR link.
- [ ] Updated research report. Evidence: issue #25 and `report/draft.md`.
- [ ] Sprint 2 retrospective. Evidence: issue #26 and `docs/sprints/sprint-2/retrospective.md`.

## Sprint 2 acceptance criteria (verbatim)

| Acceptance criterion | Status | Evidence |
|---|---|---|
| Core implementation runs end-to-end on the approved sample | Pending | Issue #21; add command, commit SHA, and generated output |
| Method has automated tests | Pending | Issue #22; add test and CI results |
| Group can explain why the method is trustworthy and where it may fail | Pending | Issue #23; validation results and threats-to-validity discussion |
| Preliminary analysis is supported by generated evidence | Pending | Issue #24; add reproducible table and figure paths |

## Validation status

| Kind | Primary rater | Second rater | Second-rater PR/date | Primary labels after PR/date | Cohen’s kappa |
|---|---|---|---|---|---|
| Signals | `jd` | TBD — must be someone other than `jd` | Pending | Pending | Pending |
| Lineage | `jd` | TBD — must be someone other than `jd` | Pending | Pending | Pending |
| Drift | `jd` | Leticia (`la`) | Pending | Pending | Pending |

## Demo script (12 minutes)

| Step | Time | Presenter |
|---|---:|---|
| Research question and method | 1 min | Leticia |
| `make test`, `make pipeline`, and CI | 3 min | Jerad |
| Preliminary table and figure | 3 min | Leticia |
| Validation protocol, precision, and agreement | 2 min | Hina |
| PR review, ADR, and process metrics | 2 min | Hina |
| Known failure and Sprint 3 plan | 1 min | Jerad |

## Gemba walk: fresh-clone reproduction record

| Field | Evidence |
|---|---|
| Who and environment | Leticia Aderhold; Windows 11; Python 3.12.1 |
| Date | 2026-09-26 |
| Commit SHA | Not recorded; capture during the review with `git rev-parse HEAD` |
| README steps followed | `python -m venv .venv`; `.venv\Scripts\activate`; `python -m pip install -e ".[dev]"`; `python scripts\download_samples.py`; `python -m json.tool data\samples\MANIFEST.json` |
| Time to first result | Not recorded |
| Output matched | Dataset acquisition succeeded; full pipeline output has not yet been independently compared |
| Problems found | A fresh clone initially failed with `ModuleNotFoundError: No module named 'requests'`. Installation with `python -m pip install -e ".[dev]"` resolved it. The missing setup instruction was documented in issue #14. |

## Instructor feedback

| Feedback | Action | Owner | Issue # |
|---|---|---|---|
| | | | |

## Velocity and KPIs at review

| Metric | Sprint 1 | Sprint 2 |
|---|---|---|
| Points planned / completed | | |
| Issues closed | | |
| PRs merged / merged with an approving review from another member | | |
| Median PR first-review turnaround (hours) | | |
| Median cycle time (days) | | |
| Median PR open-to-merge time (hours) | | |
| CI pass rate | | |
| Rework items | | |
| Contribution share per member (min / max) | | |
| Test count / coverage | | |

## Backlog changes proposed for review

- Added: redistribute work previously associated with Allie and update team documentation.
- Removed/cancelled: Allie from capacity, attendance, assignments, and review rotation because she dropped the course.
- Re-estimated: remaining Sprint 2 work based on the three active team members.

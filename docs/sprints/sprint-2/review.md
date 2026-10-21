# Sprint 2 review: implementation and validation

How to use: the Product Owner runs the review on Wed 2026-10-28. Every rubric bullet must link to evidence in this repository. Rubric weight: 20%.

Date: 2026-10-28. Product Owner: Allie Hodges. Scrum Master: Hina Kramer.
Present: [ ] Leticia Aderhold [ ] Jerad Dunne [ ] Allie Hodges [ ] Hina Kramer [ ] Instructor (if present)

## Sprint goal check

- Sprint goal (from planning):
- Met: yes / partially / no. Explain in two sentences:

## Rubric review checklist (verbatim from the assignment)

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

## Gemba walk: fresh-clone reproduction record

| Field | Value |
|---|---|
| Who (a member who did not write the README) and environment | Pending assignment to a member who did not write the README; record their operating system and Python version. |
| Date | Pending actual reproduction run. |
| Commit SHA | Pending; record the exact commit tested. |
| Steps followed (from README) | Planned: obtain a fresh copy, follow the README setup and approved-sample instructions, run tests and the pipeline, then compare generated outputs with committed results using the documented reproduction check. Record the actual commands followed. |
| Time to first result (minutes) | Pending; measure during the run. |
| Result matched committed output | Pending comparison; record yes/no and any numerical tolerance used. |
| Problems found (open issues) | Not yet assessed. Record failures, workarounds, and issue links after the run. |

## Instructor feedback

| Feedback | Action | Owner | Issue # |
|---|---|---|---|
| | | | |

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

## Backlog changes agreed at the review

- Added: Pending confirmation at the Sprint 2 review. Proposed Sprint 3 follow-up includes the signals repeat rating tracked in #101 and any unresolved validation or rule-change work.
- Removed or cancelled: No removals or cancellations confirmed for this review; the team will record any agreed changes and their reasons.
- Re-estimated: No revised estimates confirmed for this review; the team will reassess remaining work and record updated story points where agreed.
  
## Applicability analysis update

[Static-analysis applicability comparison](../../research/APPLICABILITY.md) addresses issue #96. Rule-card/CWE reconciliation and teammate approval remain pending. No external analyzer experiment was performed.

# Sprint 3 retrospective

How to use: the Scrum Master facilitates on Wed 2026-11-18 right after the review. Data first, then discussion, then root cause, then actions. The rubric requires this retrospective to identify the group's most important process improvement; section 9 is mandatory and should be supported by numbers from the dashboard.

Date: 2026-11-18. Facilitator: Jerad Dunne.
Attendees: [ ] Leticia Aderhold [ ] Jerad Dunne [ ] Hina Kramer

## 1. Data first

Paste all three sprints from `docs/lean-six-sigma/metrics/DASHBOARD.md`.

| KPI | Target | Sprint 1 | Sprint 2 | Sprint 3 | Trend | In control? |
|---|---|---|---|---|---|---|
| Points completed / planned | 0.80 | Pending dashboard verification | Pending final dashboard verification | Pending final sprint totals | Not yet assessed | Not assessed |
| Median issue cycle time (days) | 5 | Pending dashboard verification | Pending dashboard verification | Pending dashboard verification | Not yet assessed | Not assessed |
| Median PR first-review turnaround (hours) | 48 | 51.1 | 4.2 | Not yet verified | Decreased by 46.9 hours from Sprint 1 to Sprint 2 | Not assessed; Sprint 2 met target |
| Median PR open-to-merge time (hours) | 96 | 48.1 | 16.7 | Not yet verified | Decreased by 31.4 hours from Sprint 1 to Sprint 2 | Not assessed; both recorded sprints met target |
| PRs merged without an approving review from another member | 0 | 8 / 21 (38.1%) | 0 / 36 (0%) | 0 / 5 (0%); interim through 2026-11-08 | Decreased by 38.1 percentage points from Sprint 1 to Sprint 2 | Not assessed; Sprint 2 and interim Sprint 3 met target |
| CI pass rate on main | 0.90 | Pending dashboard verification | Pending dashboard verification | Pending dashboard verification | Not yet assessed | Not assessed |
| Rework items (`rework` label) | Not specified | Pending dashboard verification | Pending dashboard verification | Pending dashboard verification | Not yet assessed | Not assessed |
| Stand-ups posted / expected | Not specified | Pending dashboard verification | Pending dashboard verification | Pending dashboard verification | Not yet assessed | Not assessed |
| Contribution share per member (min / max) | 0.15 to 0.45 | Pending dashboard verification | Pending dashboard verification | Pending dashboard verification | Not yet assessed | Not assessed |
| Hours logged per member (min / max) | Not specified | Pending dashboard verification | Pending dashboard verification | Pending dashboard verification | Not yet assessed | Not assessed |

Sources: PR review audit documented in PRs #148 and #160, with per-PR evidence in `docs/lean-six-sigma/metrics/pr_review_audit.csv` and the audit script at `scripts/pr_review_audit.py`. Sprint 3 approval figures are an interim snapshot through 2026-11-08, not final sprint totals. Other metrics require verification against `docs/lean-six-sigma/metrics/DASHBOARD.md`. Meeting a target does not by itself establish statistical process control.

## 2. Did the Sprint 2 kaizen actions work?

| Kaizen issue # | Action | Owner | Effect seen in the data? | Keep / adjust / drop |
|---|---|---|---|---|
| Kaizen #10; related evidence in #35 | Assign a reviewer when each PR opens and wait for approval from another member before merging. | All PR authors and reviewers; verify the original action owner in the Sprint 2 retrospective. | Merges without another member's approval decreased from 8/21 (38.1%) in Sprint 1 to 0/36 (0%) in Sprint 2. Median first-review time decreased from 51.1 to 4.2 hours. Hina reviewed the sources, and Jerad confirmed this as the team's most important improvement in #35. The comparison does not establish causation. | Keep. Continue early reviewer assignment and independent approval before merging. |

Evidence: `docs/lean-six-sigma/metrics/pr_review_audit.csv`, PR #148, and the team confirmation in issue #35. Review the Sprint 2 retrospective's action list before finalizing this section; add any other recorded actions with their actual owners and outcomes.

## 3. What went well

- The team confirmed that early reviewer assignment and approval from another member before merging were its most important process improvement (#35).
- Merges without another member's approval decreased from 8/21 (38.1%) in Sprint 1 to 0/36 (0%) in Sprint 2. Median first-review time decreased from 51.1 to 4.2 hours.
- Hina checked Section 9 against the PR review audit, and Jerad confirmed the team's choice in #35.
- The report distinguishes scanner signals from confirmed risky capabilities and separates Results from Discussion.
- Signal repeat-labeling was completed, with agreement on 61 of 69 rule matches and Cohen's kappa of 0.839.

## 4. What did not go well

- Some report passages still described signal repeat-labeling as pending after it was completed. PR #177 was opened to reconcile that wording.
- Several retrospective KPI entries still require dashboard verification, limiting the completeness of the three-sprint comparison.
- The documented process-improvement choice remained marked as awaiting team agreement after Jerad supplied confirmation.
- Signal validation relies on one rater. Repeat-labeling measures that rater's consistency but does not replace independent signal labeling.

## 5. Puzzles and open questions

- Which remaining dashboard metrics can be verified before the retrospective, and which must be recorded as unavailable?
- Did every recorded Sprint 2 kaizen action produce an observable benefit, and should each action be kept, adjusted, or dropped?
- Will the final Sprint 3 PR audit continue to show approval from another member before every merge?
- How much of the faster review turnaround reflects early reviewer assignment, smaller PRs, or increased reviewer participation?
- Does the final presentation and demonstration complete successfully during rehearsal, and what changes are needed afterward?

Draft status: These observations are prepared from documented evidence. Final discussion outcomes and action decisions will be recorded after the team retrospective.

## 6. Root cause on the top issue (5 Whys)

- Problem statement: Some report passages continued to describe signal repeat-labeling as pending after it had been completed, creating inconsistent status information.
- Why 1: The completed result was not reflected in every passage that mentioned the work.
- Why 2: The same validation status appeared in several places, including the Abstract, validation section, and Discussion.
- Why 3: Proposed explanation: updates were checked locally without a complete search for related wording across the report.
- Why 4: Proposed explanation: the review checklist did not explicitly require checking every affected passage when a validation task changed status.
- Why 5: Proposed explanation: responsibility for reconciling completed work with report-wide status statements was not explicit.
- Root cause: Proposed gap in the documentation closeout process: completed validation work needs a report-wide consistency check and a named person responsible for that check. Confirm this explanation with the team.
- Waste category: Defects and extra processing, because inconsistent documentation requires additional correction and review.

Evidence: Issue #101 records completed signal repeat-labeling; PR #177 addresses outdated report wording. This 5 Whys analysis is a draft, not a confirmed team finding.

## 7. Kaizen actions for finalization

| Action | Owner | Kaizen issue # | Due | How we will know it worked |
|---|---|---|---|---|
| Add a report-wide status consistency check to documentation PR reviews. Search for outdated pending/completed wording and check it against source evidence. | Proposed: PR author, checked by another member | Not yet created; related work #31 and PR #177 | Before final report approval | Abstract, validation results, Discussion, and status notes agree; a teammate records the consistency review. |
| Verify remaining retrospective KPI entries against the dashboard. Record unavailable values explicitly and distinguish interim from final figures. | To be assigned by the team | Not yet created; related work #35 | Before finalizing the Sprint 3 retrospective | Every KPI has a source and reporting period, or an explicit unavailable status. |
| Continue assigning a reviewer when each PR opens and obtaining approval from another member before merging. | All PR authors and reviewers; team confirmation pending | Existing kaizen #10; evidence in #35 | Through project completion | The final Sprint 3 PR audit records zero merges without another member's approval. |

## 8. Changes recorded (rubric)

| What changed | From | To | Reason | Where recorded |
|---|---|---|---|---|
| Research question | RQ1–RQ3 presented in a summary table | RQ1–RQ3 presented as an authored list with measure definitions; research scope retained | Clarify the distinction between authored research questions and generated result tables | `report/draft.md`; PR #176 |
| Method | Signal validation based on round 1 labels | Added a within-rater repeat-labeling check: 61 of 69 rule matches agreed, with Cohen's kappa 0.839 | Measure consistency within the primary signal rater | Issue #101; `results/validation_agreement.csv`; `report/draft.md` |
| Scope | Proposed review workflow described alongside the implemented analysis | Explicit distinction between the implemented batch pipeline and the proposed workflow, whose effectiveness remains unevaluated | Keep claims within the implemented and evaluated work | `report/draft.md`; `docs/research/REVIEW_WORKFLOW.md` |
| Interpretation | Some passages still described signal repeat-labeling as pending | Proposed correction reports the completed check while retaining the limitation that signals have one rater | Reconcile report status and distinguish within-rater consistency from independent validation | PR #177; `report/draft.md` |
| Backlog | Remaining report, presentation, and retrospective closeout work | Track report review under #31, presentation and rehearsal under #34, and process-improvement evidence under #35 | Make remaining deliverables and their acceptance evidence explicit | Issues #31, #34, and #35; project board |

This table records documented changes and proposed corrections. PR #177 remains subject to review and merge. Final backlog status and any additional changes will be confirmed during finalization.

## 9. Most important process improvement this semester (rubric, mandatory)

Write one paragraph agreed by the team. Name the improvement, when it was introduced (kaizen issue #), the KPI it moved, and the before and after values. This paragraph goes into the final presentation and the report's artifact appendix.

Status: Team agreement confirmed by Jerad Dunne in issue #35 on 2026-11-11, following Leticia Aderhold's agreement and Hina Kramer's source review. The full Sprint 3 retrospective remains scheduled for 2026-11-18.

The team's most important process improvement was assigning a reviewer when each pull request opened and waiting for approval from another member before merging. The reviewer-assignment action was introduced in the Sprint 1 retrospective on 2026-10-07 and supported the existing merge rule and kaizen #10's 48-hour review target. Merges without another member's approval decreased from 8 of 21 (38.1%) in Sprint 1 to 0 of 36 (0%) in Sprint 2, a decrease of 38.1 percentage points. Median first-review time decreased from 51.1 to 4.2 hours, and median open-to-merge time decreased from 48.1 to 16.7 hours. The team confirmed this choice in issue #35; supporting evidence is recorded in PR #148 and `docs/lean-six-sigma/metrics/pr_review_audit.csv`. These observations support the improvement, although smaller PRs and increased reviewer participation may also explain part of the change.

- **Improvement:** every pull request now waits for an approving review from a member other than its author before
  it is merged. In practice a reviewer is asked when the pull request opens, and open pull requests are checked
  against the 48-hour review target. Merges through the repository owner's bypass of the `protect-main` ruleset
  stopped.
- **Introduced in sprint / kaizen issue #:** Sprint 1 retrospective (2026-10-07), section 6: "Assign a reviewer when
  each PR is opened and check daily for PRs approaching the 48-hour review target." It puts into practice the
  charter's merge rule (one approving review from a member other than the author) and kaizen #10 (48-hour review
  SLA by a member other than the author). No separate kaizen issue was opened for the Sprint 1 action (Sprint 2
  retrospective, section 2).
- **KPI affected:** pull requests merged without an approving review from another member (target 0). Supporting:
  median hours from opening to the first review by another member, and median hours from opening to merge.
- **Before (Sprint 1, 2026-09-17 to 2026-10-07):** 8 of 21 merged pull requests (38.1%) had no approving review from
  another member before the merge: #54, #55, #62, #63, #64, #70, #72 and #74, all authored and merged by the
  repository owner (#62 went into a feature branch, the other seven into `main`). Median first review 51.1 hours;
  median open-to-merge 48.1 hours.
- **After (Sprint 2, 2026-10-08 to 2026-10-28):** 0 of 36 (34 by members, plus the weekly metrics pull requests #113
  and #122, which were also approved). Median first review 4.2 hours; median open-to-merge 16.7 hours. Sprint 3 to
  2026-11-08: 0 of 5. That is a drop of 38.1 percentage points, the same figure as Leticia Aderhold's audit in
  #141.
- **Why the evidence supports the improvement, and alternative explanations:** The `protect-main` ruleset has required one approval since 2026-09-14 and did not change between the sprints. The repository administrator can bypass that requirement, and every Sprint 1 exception involved the owner's own pull request. The unchanged setting is consistent with a change in team practice, but this comparison cannot isolate its causal effect.

  Other explanations may also contribute. In Sprint 1, the group was still forming: the solo plan in ADR-0005 was replaced by ADR-0006 on 2026-09-15, and members were still learning GitHub, so fewer reviewers were active early on. Sprint 2 pull requests were mostly small documentation changes, which are quicker to review. To sustain the improvement, the team should consider removing the administrator bypass or checking approval compliance at every review.
- **Evidence:** `python scripts/pr_review_audit.py --repo jeraddunne/csc580-group9-msr2027 --out
  docs/lean-six-sigma/metrics/pr_review_audit.csv --save-json docs/lean-six-sigma/metrics/pr_review_audit_raw.json`
  (run 2026-11-08; `--from-json` repeats it offline). Windows are calendar days in Eastern Time; any base branch
  counts; an approval counts only if it was submitted before the merge and not dismissed. The Sprint 1 list matches
  the [Sprint 1 retrospective](../sprint-1/retrospective.md). The medians cover pull requests by members and use a
  different population from the weekly dashboard's `pr_first_review_hours`, so the two are not compared.

## 10. Retro on the retro

- Does the charter still fit? yes / no. Proposed change:
- Format worked: yes / no. Change for next time:

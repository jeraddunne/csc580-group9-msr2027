# Sprint 3 retrospective

How to use: the Scrum Master facilitates on Wed 2026-11-18 right after the review. Data first, then discussion, then root cause, then actions. The rubric requires this retrospective to identify the group's most important process improvement; section 9 is mandatory and should be supported by numbers from the dashboard.

Date: 2026-11-18. Facilitator: Jerad Dunne.
Attendees: [ ] Leticia Aderhold [ ] Jerad Dunne [ ] Hina Kramer

## 1. Data first

Paste all three sprints from `docs/lean-six-sigma/metrics/DASHBOARD.md`.

| KPI | Target | Sprint 1 | Sprint 2 | Sprint 3 | Trend | In control? |
|---|---|---|---|---|---|---|
| Points completed / planned | 0.80 | | | | | |
| Median issue cycle time (days) | 5 | | | | | |
| Median PR first-review turnaround (hours) | 48 | | | | | |
| Median PR open-to-merge time (hours) | 96 | | | | | |
| PRs merged without an approving review from another member | 0 | 8 / 21 (0.381) | 0 / 36 (0.000) | 0 / 5 to 2026-11-08 | Down to target from Sprint 2 | Not assessed. `scripts/pr_review_audit.py`, `docs/lean-six-sigma/metrics/pr_review_audit.csv` |
| CI pass rate on main | 0.90 | | | | | |
| Rework items (`rework` label) | | | | | | |
| Stand-ups posted / expected | | | | | | |
| Contribution share per member (min / max) | 0.15 to 0.45 | | | | | |
| Hours logged per member (min / max) | | | | | | |

## 2. Did the Sprint 2 kaizen actions work?

| Kaizen issue # | Action | Owner | Effect seen in the data? | Keep / adjust / drop |
|---|---|---|---|---|
| | | | | |

## 3. What went well

-

## 4. What did not go well

-

## 5. Puzzles and open questions

-

## 6. Root cause on the top issue (5 Whys)

- Problem statement:
- Why 1:
- Why 2:
- Why 3:
- Why 4:
- Why 5:
- Root cause:
- Waste category:

## 7. Kaizen actions for finalization

| Action | Owner | Kaizen issue # | Due | How we will know it worked |
|---|---|---|---|---|
| | | | | |

## 8. Changes recorded (rubric)

| What changed | From | To | Reason | Where recorded |
|---|---|---|---|---|
| Research question | | | | |
| Method | | | | |
| Scope | | | | |
| Interpretation | | | | |
| Backlog | | | | Milestone `Finalization` |

## 9. Most important process improvement this semester (rubric, mandatory)

Write one paragraph agreed by the team. Name the improvement, when it was introduced (kaizen issue #), the KPI it moved, and the before and after values. This paragraph goes into the final presentation and the report's artifact appendix.

Status: drafted 2026-11-08 by Jerad Dunne from the audit below, for the team to agree at the review on 2026-11-18.

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
- **Why we believe the improvement caused the change (and the alternative explanation):** the `protect-main` ruleset
  has required one approval since 2026-09-14 and was not changed between the sprints. It lets the repository admin
  role bypass that requirement, and every Sprint 1 exception was the owner's own pull request. So the drop came from
  how the team worked, not from a new GitHub setting. The alternative explanations: in Sprint 1 the group was still
  forming (the solo plan in ADR-0005 was replaced by ADR-0006 on 2026-09-15, and members were still learning
  GitHub), so fewer reviewers were active early on; and Sprint 2 pull requests were mostly small documentation
  changes, which are quicker to review. Because the rule depends on the admin not bypassing it, the control plan
  for finalization should either remove the admin bypass or check this KPI at every review.
- **Evidence:** `python scripts/pr_review_audit.py --repo jeraddunne/csc580-group9-msr2027 --out
  docs/lean-six-sigma/metrics/pr_review_audit.csv --save-json docs/lean-six-sigma/metrics/pr_review_audit_raw.json`
  (run 2026-11-08; `--from-json` repeats it offline). Windows are calendar days in Eastern Time; any base branch
  counts; an approval counts only if it was submitted before the merge and not dismissed. The Sprint 1 list matches
  the [Sprint 1 retrospective](../sprint-1/retrospective.md). The medians cover pull requests by members and use a
  different population from the weekly dashboard's `pr_first_review_hours`, so the two are not compared.

## 10. Retro on the retro

- Does the charter still fit? yes / no. Proposed change:
- Format worked: yes / no. Change for next time:

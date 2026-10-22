# Sprint 2 retrospective

How to use: the Scrum Master facilitates on Wed 2026-10-28 right after the review. Data first, then discussion, then root cause, then actions. Every agreed action becomes a `kaizen` issue and a row in `docs/lean-six-sigma/KAIZEN_BACKLOG.md`. Record changes to the research question, method, scope, or interpretation.

Status: Preliminary draft. Final metrics, attendance, outcomes, and decisions remain pending until the October 28 retrospective.
Date: 2026-10-28. Facilitator: Hina Kramer. Attendees: [ ] Leticia Aderhold [ ] Jerad Dunne [ ] Hina Kramer

> Team update: Allie Hodges dropped the course during Sprint 2. Sprint responsibilities were redistributed among the three remaining members.

## 1. Data first

Populate Sprint 1 and Sprint 2 values from `docs/lean-six-sigma/metrics/DASHBOARD.md`. Leave unavailable values pending; do not estimate.

| KPI | Target | Sprint 1 | Sprint 2 | Trend | In control? |
|---|---|---|---|---|---|
| Points completed / planned | 0.80 | Pending | Pending | Pending | Pending |
| Median issue cycle time (days) | 5 | Pending | Pending | Pending | Pending |
| Median PR first-review turnaround (hours) | 48 | Pending | Pending | Pending | Pending |
| Median PR open-to-merge time (hours) | 96 | Pending | Pending | Pending | Pending |
| PRs merged without an approving review from another member | 0 | Pending | Pending | Pending | Pending |
| CI pass rate on main | 0.90 | Pending | Pending | Pending | Pending |
| Rework items (`rework` label) | Not specified | Pending | Pending | Pending | Pending |
| Stand-ups posted / expected | Not specified | Pending | Pending | Pending | Pending |
| Contribution share per member (min / max) | 0.15 to 0.45 | Pending | Pending | Pending | Pending |
| Hours logged per member (min / max) | Not specified | Pending | Pending | Pending | Pending |

## 2. Did the Sprint 1 kaizen actions work?

| Kaizen issue # | Action | Owner | Effect seen in the data? | Keep / adjust / drop |
|---|---|---|---|---|
| TBD | Maintain the 48-hour pull-request review goal | Hina Kramer | Complete from the Sprint 2 first-review turnaround metric | TBD at retrospective |
| TBD | Monitor contribution balance at each check-in | Hina Kramer | Complete from the Sprint 2 contribution-share metric | TBD at retrospective |
| TBD | Require tests and CI evidence for pipeline changes | Jerad Dunne | Complete from the Sprint 2 CI pass rate and rework count | TBD at retrospective |

## 3. What went well

- Expected benefit: redistributing responsibilities among the three remaining members will help maintain progress.
- Expected benefit: repository issues and pull requests will provide traceability for completed and remaining work.
- Expected benefit: continued documentation will support implementation, validation, and research-report evidence.
- Confirm actual outcomes and supporting evidence during the October 28 review and retrospective.

## 4. What did not go well

- The original Sprint 2 plan still listed a member who dropped the course.
- Capacity, ownership, and review assignments were not immediately updated after the team change.
- Reducing the team from four members to three increased the workload for each remaining member.
- Some work depended on reviews or approvals from another member, creating possible merge delays.
- The retrospective and planning documents contained blank fields that should have been maintained throughout the sprint.

## 5. Puzzles and open questions

- Can all required Sprint 2 work be completed with three members?
- Which incomplete items should be moved to Sprint 3?
- Are the second-rater assignments still achievable without violating the blindness rule?
- Are pull requests receiving reviews within the 48-hour target?
- Does the team need to adjust its Product Owner or reviewer rotation after Allie’s departure?

## 6. Root cause on the top issue (5 Whys)

- **Problem statement:** The Sprint 2 plan no longer accurately represented the team’s membership, capacity, and work ownership.
- **Why 1:** Allie Hodges dropped the course during Sprint 2.
- **Why 2:** Work and team roles had originally been planned for four members.
- **Why 3:** The planning document was not immediately updated when the team membership changed.
- **Why 4:** There was no defined procedure for handling a member leaving during an active sprint.
- **Why 5:** Membership changes were not included in the team’s regular check-in and documentation process.
- **Root cause:** The team lacked a formal process for immediately updating capacity, roles, ownership, and backlog commitments after a membership change.
- **Waste category:** Waiting and uneven workload/overburden.

## 7. Kaizen actions

These are proposed actions and deadlines, subject to team agreement on October 28.

| Action | Owner | Kaizen issue # | Due | How we will know it worked |
|---|---|---|---|---|
| Update capacity, roles, and issue ownership within 24 hours of any membership change | Hina Kramer | Create after the retrospective | 2026-11-04 | Planning documents and assigned issues match the active team |
| Rebalance Allie’s unfinished work across the remaining members | Jerad Dunne | Create after the retrospective | 2026-11-04 | Every committed Sprint 2 item has an active owner |
| Establish a three-person pull-request review rotation | Hina Kramer | Create after the retrospective | 2026-11-04 | Every merged PR has an approving review from a non-author |
| Record progress and blockers at each check-in | Leticia Aderhold | Create after the retrospective | 2026-11-04 | Check-in notes identify completed work, blockers, and reassigned work |

## 8. Changes recorded (rubric)

The following records Sprint 2 plans and design changes responding to instructor feedback. Completion and final results must be confirmed with evidence.

| What changed | From | To | Reason | Where recorded |
|---|---|---|---|---|
| Research question | Existing P-01 research question | No change recorded here | Feedback focuses on supporting the method, validation, and intended use | `RESEARCH_QUESTION.md`; `docs/sprints/sprint-2/instructor-feedback.md` |
| Method: rule provenance | Detection patterns without sufficiently documented rationale and sources | Document each rule's problem, bad example, source, and known false positives; explain threat-model and severity rationale | Instructor requested justification and references for detection rules | Issue #95; `docs/research/RULE_CATALOG.md`; `rules/skill_risk_rules.yaml`; `docs/research/THREAT_MODEL.md` section 8 |
| Method: applicability | Applicability of established code-analysis rules to skills needed clarification | Analyze which rules apply to SKILL.md text, bundled scripts, or neither, and explain why | Skills combine natural language and code | Issue #96; `docs/research/APPLICABILITY.md` |
| Method: validation | Validation study remained incomplete | Follow D-024 second-rater assignments for drift and lineage; report validation metrics and agreement; test about ten independently selected known-positive skills | Instructor requested completed validation and a small ground-truth check before scaling | D-024; issues #99, #100, #90, and #97; `results/validation_*.csv`; `report/draft.md` |
| Scope: intended use | Scanner results without a sufficiently defined human review process | Define a human-in-the-loop risk-review workflow using a use case diagram, swimlane activity diagram, and report section | Instructor requested an explanation of how the scanner's results will be used | Issue #98; `docs/research/REVIEW_WORKFLOW.md`; `report/draft.md` |
| Scope: team capacity | Work planned for four members | Reprioritize work for Leticia Aderhold, Jerad Dunne, and Hina Kramer | Allie Hodges dropped the course | `docs/sprints/sprint-2/planning.md` |
| Interpretation | Preliminary findings awaiting validation | Keep conclusions provisional until validation and agreement results are available | Final claims must be supported by evidence | `report/draft.md`; `docs/sprints/sprint-2/instructor-feedback.md` |
| Backlog | Four-person capacity and unfinished validation/process tasks | Track revised ownership, acceptance criteria, definition of done, and obstacles; move signals round 2 to Sprint 3 | Reduced capacity and the required 14-day intra-rater gap | Issues #101 and #102; `docs/sprints/sprint-2/review.md`; Sprint 3 milestone |

## 9. Retro on the retro

- **Does the charter still fit?** Partially. Proposed change: add a procedure requiring roles, capacity, reviewers, and issue ownership to be updated within 24 hours when team membership changes.
- **Format worked?** Pending confirmation on October 28. Proposed change: update the retrospective throughout the sprint instead of waiting until the final meeting.

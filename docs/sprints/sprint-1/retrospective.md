# Sprint 1 retrospective

How to use: the Scrum Master facilitates on Wed 2026-10-07 right after the review. Data first, then discussion, then root cause, then actions. Every action becomes a `kaizen` issue and a row in `docs/lean-six-sigma/KAIZEN_BACKLOG.md`. The rubric requires this retrospective to explain what the group learned and what changed in the backlog.

Date: 2026-10-07. Facilitator: Leticia Aderhold.
Attendees: [x] Leticia Aderhold [ ] Jerad Dunne [ ] Allie Hodges [ ] Hina Kramer

## 1. Data first

Source: October 4, 2026 baseline snapshot in docs/lean-six-sigma/metrics/DASHBOARD.md. These are baseline values, not final October 7 totals. “In control?” records statistical control where assessed; meeting a target alone does not establish control.

| KPI | Target | Sprint 1 value | In control? | Comment |
| --- | --- | --- | --- | --- |
| Points completed / planned | 0.80 | 15 / 22 = 0.68 | Not assessed | Below target. |
| Median issue cycle time (days) | 5 | 0.03 | No—signals reported | Median meets target, but the dashboard reports beyond-limit observations and eight observations on the same side. |
| Median PR first-review turnaround (hours) | 48 | 33.38 | Not established | Median meets target; four open PRs exceeded 48 hours at the snapshot. |
| Median PR open-to-merge time (hours) | 96 | 1.17 | Not assessed | Meets target; 17 merged PRs measured. |
| PRs merged without an approving review from another member | 0 | Verification pending | Not assessed | Dashboard reports 13 unreviewed merged PRs; confirm approval status and Sprint 1 scope. |
| CI pass rate on main | 0.90 | Main-only rate pending | Not assessed | Dashboard reports 0.99 (171 / 172 completed runs); confirm branch scope. |
| Rework items (`rework` label) | — | Sprint 1 count pending | Not assessed | Dashboard reports 0 rework items among 21 closed issues across its reporting scope. |
| Stand-ups posted / expected | — | Not available in dashboard | Not assessed | Confirm totals from stand-up records. |
| Contribution share per member (min / max) | 0.15 to 0.45 | 0.00 / 0.71 | Not assessed | Outside target band. Shares: Leticia 0.15, Jerad 0.71, Allie 0.00, Hina 0.14. |
| Hours logged per member (min / max) | — | Not available in dashboard | Not assessed | Confirm totals from members’ time records. |


## 2. What went well

- One team member had experience with GitHub and helped others learn the project workflow.
- Google Chat and Zoom meetings gave us ways to communicate, ask questions, and coordinate work. Email notifications helped us track project activity.
- Three team members worked hard together to complete the project tasks, contributing their research skills and ability to find and use resources.
- Having another team member review and approve changes before merging provided an opportunity to catch problems and improve the work.

## 3. What did not go well

- Learning GitHub and understanding how to find, complete, and submit tasks took more time than expected.
- Attendance at Zoom meetings was inconsistent, which made coordination more difficult.
- One team member had not participated in the project by the time of this retrospective, leaving more work for the active members.
- Uneven participation and limited familiarity with GitHub contributed to last-minute work near the deadline.


## 4. Puzzles and open questions

- How can we make GitHub tasks and review steps easier for members who are still learning the platform?
- How can we improve meeting attendance and participation so that work is shared more evenly?
- What should the team do when a member is not participating or responding?
- How can we identify unfinished tasks and request reviews earlier to reduce last-minute work?
- Does the dashboard’s high work-in-progress count reflect tasks actively being worked on, or issues whose statuses need updating?
- Why are the recorded issue cycle times so short, and do they accurately reflect when work started?

## 5. Root cause on the top issue (5 Whys)

Use `docs/lean-six-sigma/ROOT_CAUSE_TEMPLATE.md` for the long form. Pick the single item with the largest effect on the sprint goal.

- Problem statement: Sprint 1 work became concentrated among three active members, and difficulty learning GitHub contributed to a last-minute rush to complete tasks.

- Why 1: Why was work rushed near the deadline? Some tasks and reviews remained unfinished until late in the sprint.

- Why 2: Why did tasks remain unfinished? Participation was uneven, and members needed additional time and help to understand the GitHub workflow.

- Why 3: Why did these difficulties delay progress? Experienced members had to spend time helping others while also completing their own tasks and covering gaps in participation.

- Why 4: Why were the gaps not resolved earlier? Our communication channels helped us coordinate, but inconsistent meeting attendance made it harder to confirm progress and identify where support was needed.

- Why 5: Why did coordination not prevent the last-minute rush? Our process needed earlier checks that each member could complete the workflow, report progress, and raise problems before the deadline.

- Root cause: The proposed root cause is insufficient early verification of workflow readiness and participation, which allowed learning difficulties and unfinished work to accumulate.

- Waste category: Waiting—tasks and reviews were delayed while members needed guidance or responses. Uneven workload also placed additional pressure on the active members.

## 6. Kaizen actions

| Action | Owner | Kaizen issue # | Due | How we will know it worked |
|---|---|---|---|---|
| Create a short GitHub checklist covering finding an assigned issue, updating its status, opening a PR, and requesting a review. Walk through it with members who need help. | Proposed: Jerad, with Leticia checking clarity | To be created | 2026-10-09 | Each participating member completes the workflow and identifies any remaining difficulties. |
| Confirm each member’s availability and Sprint 2 tasks. Require a progress update or blocker report at each scheduled check-in; contact members who miss an update. | Proposed: Leticia | To be created | 2026-10-09; check throughout Sprint 2 | Every member has a recorded participation plan, and missed updates are followed up within one working day. |
| Assign a reviewer when each PR is opened and check daily for PRs approaching the 48-hour review target. | Proposed: PR authors and assigned reviewers | To be created | Start 2026-10-08; evaluate 2026-10-28 | Every ready PR has a reviewer, median first-review time is at most 48 hours, and overdue reviews receive follow-up. |
| Review unfinished tasks and submission requirements at least three days before the next deadline. Record blockers, owners, and next steps. | Proposed: Leticia coordinates; all members report | To be created | 2026-10-25 | Remaining work is identified before the deadline, with an owner and completion plan for each item. |

## 7. What we learned (rubric)

- About the dataset: We learned that reproducible dataset acquisition requires clear setup instructions, installed dependencies, and a manifest recording file hashes and sources. Independent verification on Windows revealed missing setup steps and helped improve the instructions. We also learned that findings from a sample must be interpreted within its scope.

- About the research question: Our question examines the prevalence, reach, and drift of risky capabilities in copied agent skills. We learned to distinguish automated signals from confirmed risky behavior and to use human validation before interpreting results. Lineage and drift findings also require care because the selected pairs may not represent all pairs in the full dataset.

- About working together (onboarding, reviews, communication): We learned that GitHub experience varied across the team and that practical guidance was needed alongside written instructions. Google Chat, Zoom, and email notifications helped us coordinate. Reviewing another member’s changes provided opportunities to catch problems before merging. Inconsistent attendance and participation increased the workload for active members, showing the need for earlier progress checks, clearer responsibilities, and timely review requests.

## 8. Changes recorded (rubric)

| What changed | From | To | Reason | Where recorded |
|---|---|---|---|---|
| Research question | Risky capabilities in copied agent skills: prevalence, reach, and drift | Same research question; no change reported in this retrospective | Keep the study focused while improving its execution | `RESEARCH_QUESTION.md` |
| Method | Sample-download instructions without the required Windows environment setup steps | Add virtual-environment and dependency-installation steps before downloading samples; documentation PR awaiting confirmation of merge | Independent Windows verification found a missing dependency when running the download script | Verification comments in issue #14; PR “docs: add Windows setup steps for sample download” |
| Scope | Full-dataset expansion remained an open decision | Proposed decision: retain the official sample for RQ1–RQ3 | Keep the work manageable and avoid extending sample findings beyond their supported scope | ADR-0007 / PR #68; confirm final decision and merge status |
| Interpretation | Automated signals and selected pairs could be mistaken for confirmed or representative findings | Treat signals as candidates requiring human validation; state limitations of selected lineage and drift pairs | Avoid overstating risky behavior or generalizing pair findings to the full dataset | Retrospective section 7; ADR-0007 / PR #68 |
| Backlog (added / removed / re-estimated) | GitHub learning difficulties, uneven participation, and delayed reviews identified during Sprint 1 | Proposed Sprint 2 additions: GitHub checklist, participation checks, reviewer assignment, and an earlier deadline-readiness check | Address the causes of delays and last-minute work | Retrospective section 6; add kaizen issue links and assign them to the Sprint 2 milestone |

## 9. Retro on the retro

- Does the charter still fit? Yes, overall, but participation and communication expectations need clarification. Proposed change: clarify how members report progress, notify the team when they cannot attend meetings, request help, and follow up on missed commitments. Retain review by another member before merging changes.

- Format worked: Yes, the structured retrospective helped connect our experiences with dashboard measurements and improvement actions. Change for next time: collect metrics, hours, and stand-up totals throughout the sprint; have each member contribute observations before the retrospective; and confirm action owners, issue numbers, and due dates during the discussion.

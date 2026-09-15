# Team Charter and Working Agreement

**Group 9, SWE 380 / CSC 580, University of Michigan-Flint**
**Project:** Mining AI-Native Software Engineering: risky capabilities in copied agent skills (proposal P-01)
**Version:** 2.0, 2026-09-15 (ADR-0006). Reviewed at every retrospective.

Version history: 1.0 (2026-09-13) was the original four-person charter. On 2026-09-14 it was replaced by a solo working agreement (ADR-0005), which Jerad Dunne signed in pull request #43. On 2026-09-15 the group was reinstated (ADR-0006) and this version replaces the solo agreement. Earlier versions are in git history.

This charter is the team's contract with itself. It is short on purpose. Any member can enforce any section by pointing at its number.

## 1. Members

| Member | GitHub | Preferred contact | Time zone | Typical availability |
|---|---|---|---|---|
| Leticia Aderhold | @angel06la | _team channel_ | | |
| Jerad Dunne | @jeraddunne (repository owner) | _team channel_ | | |
| Allie Hodges | @AllieHgs | _team channel_ | | |
| Hina Kramer | @hinak786 | _team channel_ | | |

Each member completes the **Team member onboarding** issue form, adds a profile in `docs/team/`, and signs section 14 in their first pull request. No email addresses or phone numbers go in this public repository.

## 2. Purpose and success

We will answer the P-01 research question (`RESEARCH_QUESTION.md`) with a reproducible, static analysis of risk-relevant capabilities in copied GitSkills agent skills, and produce an evidence-based report, a working prototype, and a demonstration. Success means:

1. Every rubric acceptance criterion for Sprints 1, 2, and 3 is met with linked evidence.
2. A stranger can clone the repository, follow the README, and regenerate the main tables and figures.
3. Every member can explain every part of the pipeline and has visible contributions in issues, commits, pull requests, and reviews.
4. Validation labels are independent: at least one teammate labels as a second rater, and inter-rater agreement is reported.
5. The team's process metrics (`docs/lean-six-sigma/KPIS.md`) improve from Sprint 1 to Sprint 3.

## 3. Roles

Scrum roles rotate each sprint so everyone experiences each role. Proposed rotation, to be confirmed at the 2026-09-16 kickoff and recorded in `project.yml`:

| Period | Product Owner | Scrum Master | Developers / Researchers |
|---|---|---|---|
| Formation | Jerad Dunne | Jerad Dunne | all |
| Sprint 1 | Jerad Dunne | Leticia Aderhold | all |
| Sprint 2 | Allie Hodges | Hina Kramer | all |
| Sprint 3 | Leticia Aderhold | Jerad Dunne | all |
| Finalization | Hina Kramer | Allie Hodges | all |

- **Product Owner** owns the research backlog, writes acceptance criteria, orders the backlog against the rubric, and accepts or rejects work at the review.
- **Scrum Master** runs planning, check-ins, review, and retrospective; keeps the board honest; enforces the WIP limit and the review SLA; reviews the weekly metrics pull request; writes meeting notes.
- **Developers / Researchers** implement, test, validate, document, and review. A role never replaces technical or research work.
- **Metrics owner** (Lean Six Sigma role, held by the Scrum Master) keeps the KPI dashboard current and brings data to the retrospective.

## 4. Cadence and ceremonies

Sprints run Thursday to Wednesday as scheduled in the assignment.

| Ceremony | When | Length | Output |
|---|---|---|---|
| Sprint planning | Day 1 of the sprint (Thursday) | 60 min | Sprint goal, committed issues with estimates and owners, `docs/sprints/<sprint>/planning.md` |
| Async stand-up | Monday, Wednesday, Friday by 21:00 local | 5 min each, written | Row in `docs/meeting-notes/YYYY-MM-DD-standup-week.md`: done, next, blockers, hours |
| Mid-sprint check-in | Every Thursday | 30 min | Board review, WIP and blocker check, metrics pull request reviewed, risks updated |
| Sprint review | Last Wednesday of the sprint | 45 min | Rubric checklist, demo, gemba walk (fresh clone), `review.md` |
| Retrospective | Same day, after the review | 45 min | Data-first retro, 5 Whys, kaizen issues, `retrospective.md` |
| Backlog refinement | Rolling, in issues | as needed | Issues meet the Definition of Ready before planning |

Missing a ceremony requires notice in the team channel beforehand and reading the notes afterward.

## 5. Communication

- **Primary channel:** _decide at the 2026-09-16 kickoff (Teams, Discord, Slack, or a text group)_. Response expectation: within 24 hours on weekdays.
- **Work discussion happens in GitHub issues and pull requests** so the repository tells the project story (rubric: GitHub practice).
- **Decisions** are recorded in `docs/workspace/DECISION_LOG.md` within 48 hours, and as ADRs in `docs/decisions/` when significant.
- **Blockers** are raised the same day with the `blocker` label and moved to the Block column. Nobody stays blocked silently for more than one day.
- Meetings are online unless the team agrees otherwise; the Scrum Master posts the link and agenda 24 hours ahead.

## 6. Definition of Ready and Definition of Done

An issue is **Ready** when it has a clear description, an owner, an acceptance criterion, an estimate, a milestone, a type label, and no unresolved dependency.

Work is **Done** when the pull request is merged to `main` after an approving review by a member other than the author, CI passes, generated outputs are regenerated and committed, affected documentation and the data dictionary are updated, the AI-use log is updated if AI assisted, and the issue is closed with a link to the evidence.

Full text: `docs/PROCESS.md`.

## 7. Code and repository agreements

1. `main` is protected: a pull request is required, **one approving review from a member other than the author** is required, merges are squash only, and force pushes and deletion are blocked.
2. Reviews are due within 48 hours of the request (`process.pr_review_sla_hours`). Rotate reviewers; do not always ask the same person.
3. Review means reading and running, not rubber-stamping. The reviewer completes the PR template's reviewer checklist and states what they verified in the approval comment.
4. Branch naming: `<type>/<issue-number>-<short-slug>` (for example `pipeline/21-variant-linking`).
5. Commit messages use imperative mood and reference the issue (`Add variant linking (#21)`).
6. Keep pull requests under about 400 changed lines where possible.
7. Never commit dataset files, secrets, or personal data. Never execute scripts found inside the datasets.
8. Notebooks are exploratory. Every result in the report is reproducible from `src/` through `make pipeline`.
9. The repository is public. If it becomes private, branch protection needs GitHub Pro (free with the GitHub Student Developer Pack), and the instructor must be invited as a collaborator.

## 8. Contribution and workload fairness

- Each member's contribution share (commits, pull requests authored, reviews given, issues closed) should stay between 15% and 45%. The dashboard flags deviations; the Scrum Master raises them at the check-in, not at the end.
- Work is pulled from the board, not assigned by one person. Each member owns at least one research item and one engineering item per sprint (`docs/workspace/WORK_SIGNUP.md`).
- Every member reviews at least one pull request per week.
- If a member cannot meet a commitment, they say so at the next stand-up and the team re-plans. Silence is the only unacceptable option.

## 9. Validation independence

- Jerad Dunne (rater id `jd`) is the primary rater. At least one teammate labels round 1 independently as a second rater: Leticia `la`, Allie `ah`, Hina `hk`. The team decides at the kickoff who second-rates which kind (signals, lineage, drift); a split is allowed.
- **Blindness rule.** The primary rater's label files are not committed until the second rater's labels for the same kind are committed. A second rater never opens the primary rater's labels.
- Inter-rater Cohen's kappa is the primary reliability measure; intra-rater re-labelling is optional. An LLM rater is only allowed under an `llm-` id, is disclosed, and never counts as human agreement.
- Protocol and dates: `docs/validation/README.md`.

## 10. Conflict resolution and escalation

1. Talk directly and privately first, within 48 hours of the concern.
2. If unresolved, bring it to the Scrum Master, who facilitates a conversation at the next check-in.
3. If still unresolved, the team votes; the majority decides, and the decision is recorded in the decision log.
4. Non-participation that persists for more than one sprint is raised with the instructor, with the metrics dashboard as evidence.

## 11. Academic integrity and AI use

- All AI assistance is logged in `ai-use-log.md` and verified by a human before merge; the reviewer checks that the log row exists.
- Sources and datasets are cited correctly, and the exact dataset snapshot is disclosed.
- Results, figures, and references are never fabricated. A reviewer may ask to see the command that produced any number.
- Author codes in the datasets stay anonymous. No deanonymization attempts, and no dataset content with personal data pasted into external tools.
- If an item in the dataset looks actively malicious, stop, note only its `file_sha`, and raise it with the instructor.

## 12. Decision making

- Topic: P-01 was selected on 2026-09-14 (ADR-0004). Any member may open a Decision needed issue to revisit it before Sprint 1 planning on Thu 2026-09-17.
- Everyday decisions: whoever owns the issue decides and documents it in the issue.
- Decisions affecting scope, method, or the research question: team agreement at a ceremony, recorded in the decision log and as an ADR.

## 13. Charter changes

Any member can propose a change through a pull request to this file. Changes need approval from all other members and a row in the decision log. The retrospective includes a standing item: "Does the charter still fit?"

## 14. Signatures

By adding your date and pull request number below, in your own pull request, you agree to this charter.

| Member | Date | Pull request |
|---|---|---|
| Leticia Aderhold | | |
| Jerad Dunne | | |
| Allie Hodges | | |
| Hina Kramer | | |

Each member signs by adding the date and their onboarding pull request number in their own pull request.

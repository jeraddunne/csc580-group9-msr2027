# Solo Working Agreement

**SWE 380 / CSC 580, University of Michigan-Flint. Project owner: Jerad Dunne (@jeraddunne)**
**Project:** Mining AI-Native Software Engineering: risky capabilities in copied agent skills (proposal P-01)
**Version:** 2.0, 2026-09-14. Replaces the four-person team charter (version 1.0, kept in git history) under ADR-0005. Reviewed at every retrospective.

This file keeps its original name so existing links still work. It is the agreement I hold myself to while running the project alone.

## 1. Status of solo execution

The assignment describes groups of three to five. On 2026-09-14 I decided to complete the project alone (ADR-0005). That decision is **pending confirmation from the instructor**, Prof. Mohamed Wiem Mkaouer (@mkaouer). If the instructor has not confirmed by the Sprint 1 review on Wed 2026-10-07, or asks me to join a group, ADR-0005 is reopened.

## 2. Purpose and success

I will answer the P-01 research question with a reproducible mining and analysis pipeline over the GitSkills sample, and produce an evidence-based report, a working prototype, and a demonstration. Success means:

1. Every rubric acceptance criterion for Sprints 1, 2, and 3 is met with linked evidence, with the solo substitutes documented where a criterion assumes a team.
2. Someone else can clone the repository, follow the README, and regenerate the main tables and figures.
3. Every result is traceable to an issue, pull request, commit, or decision record.
4. The process metrics in `docs/lean-six-sigma/KPIS.md` improve from Sprint 1 to Sprint 3.
5. Every AI-assisted change is reviewed by me before merge and logged in `ai-use-log.md`.

## 3. Roles

| Period | Product Owner | Scrum Master | Developer / Researcher |
|---|---|---|---|
| Formation | Jerad Dunne | Jerad Dunne | Jerad Dunne |
| Sprint 1 | Jerad Dunne | Jerad Dunne | Jerad Dunne |
| Sprint 2 | Jerad Dunne | Jerad Dunne | Jerad Dunne |
| Sprint 3 | Jerad Dunne | Jerad Dunne | Jerad Dunne |
| Finalization | Jerad Dunne | Jerad Dunne | Jerad Dunne |

- **As Product Owner** I order the backlog against the rubric, write acceptance criteria, and accept or reject work at the review.
- **As Scrum Master** I run each ceremony in writing, keep the board honest, enforce the WIP limit and the self-review protocol, and read the metrics dashboard.
- **As Developer / Researcher** I implement, test, validate, document, and present.

Writing the notes for each role keeps the Scrum practice visible even with one person.

## 4. Weekly schedule and hours

| Commitment | Value |
|---|---|
| Planned hours per week | _fill at Sprint 1 planning_ |
| Fixed work blocks | _fill at Sprint 1 planning_ |
| Days that are not available, known absences | _fill at Sprint 1 planning_ |

Hours are logged in the weekly work log and feed commitment reliability and the individual reflection.

## 5. Ceremonies (solo)

| Ceremony | When | Length | Output |
|---|---|---|---|
| Sprint planning | Day 1 of each sprint (Thursday) | 45 min | Sprint goal, hours, committed issues with estimates; `docs/sprints/<sprint>/planning.md` |
| Work log | Monday, Wednesday, Friday | 5 min | Row in `docs/meeting-notes/YYYY-MM-DD-worklog-week.md`: done, next, blockers, hours |
| Self check-in | Every Thursday | 30 min | Board and WIP check, metrics dashboard, top FMEA risks, findings and decisions curated |
| Sprint review | Last Wednesday of the sprint | 45 min | Rubric checklist with evidence, fresh-clone gemba walk; `review.md` |
| Retrospective | Same day, after the review | 30 min | Data first, 5 Whys, kaizen issues, recorded changes; `retrospective.md` |

## 6. Definition of Ready and Definition of Done

An issue is **Ready** when it has a clear description, an acceptance criterion, an estimate, a milestone, a type label, and no unresolved dependency. I assign it to myself when I start it so the board metrics work.

Work is **Done** when the pull request is merged to `main` under the self-review protocol (section 7), tests pass (in CI once workflows are enabled), generated outputs are regenerated and committed, affected documentation is updated, the AI-use log is updated if AI assisted, and the issue is closed with a link to the evidence.

## 7. Self-review protocol

This replaces "reviewed by a different team member", which one person cannot do.

1. Every change goes through a pull request. `main` is protected: a pull request is required, merges are squash only, and force pushes and deletion are blocked.
2. After opening the pull request, wait at least 12 hours (`process.self_review_cooling_off_hours` in `project.yml`) before reviewing it.
3. Review with the PR template's self-review checklist. Pull the branch into a clean environment, run the tests or the pipeline, compare outputs with the stated command, re-read text for observation versus interpretation, and read AI-assisted parts line by line.
4. Leave a review comment that summarizes what was verified, so the review is visible in the history.
5. Merge only when the checklist is complete and CI is green (once workflows are enabled).
6. For major pull requests (validation results, report draft, release), ask the instructor or a classmate for an external review when possible, and record who reviewed.
7. The cooling-off period may be skipped only for typo-level documentation fixes, marked "trivial" in the pull request.

## 8. Repository agreements

1. Branch naming: `<type>/<issue-number>-<short-slug>`.
2. Commit messages in imperative mood that reference the issue (`Add variant linking (#21)`).
3. Keep pull requests under about 400 changed lines where possible.
4. Never commit dataset files, secrets, or personal data. Never execute scripts found inside the datasets.
5. Notebooks are exploratory. Every result in the report is reproducible from `src/` through `make pipeline`.
6. The repository is public. If it becomes private, branch protection needs GitHub Pro (free with the GitHub Student Developer Pack), and the instructor must be invited as a collaborator.

## 9. Workload and descope plan

One person is a single point of failure. If commitment reliability falls below 0.8 in a sprint, or more than a week of work is lost, descope in this order (P-01 section 10):

1. Drop the RQ3 full-dataset extension.
2. Drop the regression model; keep the descriptive RQ2 comparison with its tests.
3. Keep validated RQ1 rules and the RQ2 descriptive comparison, which still meet every rubric question 4 minimum-evidence item.

Every descope step is recorded in `docs/workspace/DECISION_LOG.md` and in the sprint retrospective.

## 10. Validation reliability

There is one annotator. The annotation guideline is written before labelling starts. A random 30% of labelled items is re-labelled at least 7 days later, and intra-rater agreement is reported as Cohen's kappa. A second rater is added when available: the instructor, a classmate, or an LLM rater that is disclosed and never counted as human agreement. The limitation is stated in `THREATS_TO_VALIDITY.md`.

## 11. Academic integrity and AI use

- All AI assistance is logged in `ai-use-log.md` and reviewed by me before merge.
- Sources and datasets are cited correctly, and the exact dataset snapshot is disclosed.
- Results, figures, and references are never fabricated. Every number in the report can be traced to the command that produced it.
- Author codes in the datasets stay anonymous. No deanonymization attempts, and no dataset content with personal data pasted into external tools.

## 12. Escalation

I contact the instructor about confirmation of solo execution, deadline changes, scope questions, suspected malicious content in the dataset, and anything that blocks work for more than three days. A blocked issue gets the `blocker` label and moves to **Block** on the board the same day.

## 13. Changes to this agreement

Changes are made by pull request to this file and recorded in `docs/workspace/DECISION_LOG.md`.

## 14. Signature

| Name | Date | Pull request |
|---|---|---|
| Jerad Dunne | | |

Sign by adding the date and the pull request number when merging the solo conversion pull request.

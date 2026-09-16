# ADR-0005: Run the project as a solo project

- **Status:** Superseded by ADR-0006 (2026-09-15). Originally accepted on 2026-09-14, when Jerad Dunne confirmed that a solo project is permitted.
- **Date:** 2026-09-14
- **Deciders:** Jerad Dunne. Confirmation requested from the instructor, Prof. Mohamed Wiem Mkaouer (@mkaouer).
- **Confirmation:** stated by the student on 2026-09-14; attach the instructor's written confirmation here if one exists
- **Affects research question / method / scope:** yes (review and validation method, workload scope)

## Context

The assignment describes the project as work "in groups of three to five". On 2026-09-13 this repository was set up for a four-person Group 9, with a ranked-ballot topic vote, a work sign-up process, rotating Product Owner and Scrum Master roles, cross-member pull request review, two-annotator validation, and a contribution-balance KPI.

On 2026-09-14 Jerad Dunne decided to complete the project alone, using the repository, the process documents, and his proposal P-01 (issue #41) as the starting point. Several parts of the setup assume more than one person, and one rubric bullet cannot be met literally by a single person: "At least one pull request reviewed by a different team member than the author" (Sprint 2).

## Options considered

1. **Stay in the group of four.** Meets the stated group size and the cross-member review bullet. Depends on coordinating four schedules and on a topic vote that had not started.
2. **Run the project solo.** Full control of scope and schedule and no coordination overhead. Conflicts with the stated group size, has no second reviewer or annotator, and puts the whole workload on one person.
3. **Join or pair with another group.** Meets the group size. Loses the existing topic and repository work and adds schedule risk in formation week.

## Decision

Option 2, accepted on 2026-09-14 after the student confirmed that a solo project is permitted. The Scrum and Lean Six Sigma overlay (ADR-0001), the repository structure (ADR-0003), the sprint calendar and due dates, the findings and decision logs, and the project board plan stay. P-01 is the topic (ADR-0004).

Group practices are replaced as follows.

| Group practice | Solo substitute |
|---|---|
| Rotating Product Owner and Scrum Master | Jerad Dunne holds Product Owner, Scrum Master, and Developer/Researcher every sprint; ceremonies are kept and written down |
| Ranked-ballot topic vote (ADR-0002) | Sole member decision (ADR-0004); voting code and files kept, marked retired |
| Work sign-up form and assignment rules | Solo workstream plan in `docs/workspace/WORK_SIGNUP.md` |
| Pull request reviewed by a different member | Every change goes through a pull request; self-review after a cooling-off period of at least 12 hours using the PR template checklist; CI must pass once workflows are enabled; optional review from the instructor or a classmate on major PRs (validation results, report draft, release) |
| Two independent annotators | Intra-rater agreement: re-label a random 30% of items at least 7 days later and report Cohen's kappa; optional second rater (instructor, classmate, or an LLM rater clearly disclosed and marked as non-human) |
| Contribution-balance KPI and 48-hour peer review SLA | Retired; replaced by PR open-to-merge cycle time (target 48 hours) and self-review cooling-off compliance |
| Branch protection with one required approval | Pull request required, 0 required approvals, squash merges only, no force push or deletion |
| Async stand-ups by four members | Short work log on Monday, Wednesday, and Friday |

## Consequences

- **Positive:** faster decisions, one consistent style across code and report, no coordination cost, and the existing P-01 pilot carries straight into Sprint 1.
- **Rubric risk:** the group-size requirement and the cross-member review bullet. Mitigation: ask the instructor at the start of Sprint 1, document the substitute in every sprint review, and request an external review on at least one major pull request.
- **Review quality:** self-review catches fewer defects than peer review. Mitigation: the cooling-off period, the checklist, automated tests and lint, and a fresh-clone reproduction (gemba walk) at every sprint review.
- **Validation:** intra-rater agreement measures consistency, not independent agreement. It is reported as a limitation in `THREATS_TO_VALIDITY.md`, and a second rater is added when one is available.
- **Workload:** one person is a single point of failure. The descope order comes from P-01 section 10. First drop the RQ3 full-dataset extension. Then drop the regression model. Validated RQ1 rules plus the RQ2 descriptive comparison still meet every rubric question 4 minimum-evidence item.
- **Repository visibility:** if the repository is made private, branch protection needs GitHub Pro (free with the GitHub Student Developer Pack), and the instructor must be invited as a collaborator.
- **Follow-up:** email the instructor about solo execution; close group-only formation issues with a link to this record; update the process documents (done in the solo conversion pull request).

## Revisit trigger

Reopen this decision if the instructor has not confirmed solo execution by the Sprint 1 review on Wed 2026-10-07, or asks that the project be done in a group. The retired group process files are kept so they can be reinstated quickly.

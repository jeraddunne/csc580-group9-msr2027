# ADR-0001: Run the project with Scrum plus a Lean Six Sigma overlay

- **Status:** Accepted
- **Date:** 2026-09-13
- **Deciders:** Jerad Dunne (proposed); to be ratified by all members at the 2026-09-16 kickoff
- **Decision issue:** Formation issue "Team charter signed by all four members"
- **Affects research question / method / scope:** no (process only)

## Context

The assignment requires Scrum: three sprints, rotating Product Owner and Scrum Master roles, a visible backlog on GitHub Issues and Projects, planning, check-ins, reviews, retrospectives, and a repository that records decisions, blockers, completed work, and scope changes. The instructor provides an empty "Team-Planning" project template with the statuses Todo, In progress, Done, Block, Cancelled, an Iteration field, and an Estimate field.

The rubric also grades "Scrum practice: planning, reviews, retrospectives, and backlog evolution are visible and used to improve the work". Scrum alone says little about how to measure whether the process is improving. Lean Six Sigma provides that measurement and improvement discipline.

## Options considered

1. **Scrum only, using the template as is.** Meets the requirement. Retrospectives would rely on opinion rather than data; no defined way to show improvement.
2. **Scrum plus a Lean Six Sigma overlay.** Keep the instructor's board and ceremonies unchanged; add DMAIC tollgates mapped to sprints, a KPI catalogue with control charts computed automatically from GitHub, an FMEA risk register, a waste log, 5 Whys and A3 for root causes, and a kaizen backlog. More documents to maintain; the metrics script is extra engineering.
3. **Kanban with flow metrics.** Better flow visibility but does not satisfy the required sprint structure.

## Decision

Option 2. Scrum provides the cadence the rubric requires; the LSS overlay provides evidence of improvement. The overlay is deliberately lightweight: one automated weekly metrics PR, one FMEA review per planning, one data-first retrospective per sprint.

## Consequences

- Positive: retrospectives start from numbers; the "most important process improvement" required in the Sprint 3 retrospective will be backed by before-and-after data; contribution balance is visible early instead of at grading time.
- Negative / risks: documentation overhead; risk of tracking for its own sake. Mitigation: any LSS artifact nobody used in a sprint is dropped at the retrospective.
- Follow-up issues: automate weekly metrics; enable branch protection; adopt the 48-hour PR review SLA.

## Revisit trigger

If the Sprint 1 retrospective finds the overlay cost more than two hours per member per sprint without informing a decision, cut it to KPIs plus kaizen only.

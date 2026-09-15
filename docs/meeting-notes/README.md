# Meeting notes and work log

How to use: one Markdown file per ceremony or per work-log week. The project is solo (ADR-0005), so Jerad Dunne writes every file and opens a pull request within 24 hours (notes-only changes may be batched once a week). Decisions recorded here that change the question, method, scope, tooling, or process are copied into `docs/workspace/DECISION_LOG.md`, and into `docs/decisions/` as an ADR when significant.

## File naming

`YYYY-MM-DD-<type>.md`, where `<type>` is one of:

| Type | When | Template |
|---|---|---|
| `kickoff` | Solo Sprint 1 kickoff (2026-09-16) | `TEMPLATE-meeting.md` |
| `planning` | First Thursday of each sprint | `TEMPLATE-meeting.md` |
| `worklog-week` | One file per week, dated Monday; rows added Mon, Wed, Fri | `TEMPLATE-standup-week.md` (filename kept for link stability) |
| `checkin` | Mid-sprint Thursdays | `TEMPLATE-meeting.md` |
| `review` | Last Wednesday of the sprint (summary; full record in `docs/sprints/<sprint>/review.md`) | `TEMPLATE-meeting.md` |
| `retro` | Last Wednesday of the sprint (summary; full record in `docs/sprints/<sprint>/retrospective.md`) | `TEMPLATE-meeting.md` |

Examples: `2026-09-17-planning.md`, `2026-09-21-worklog-week.md`, `2026-09-24-checkin.md`.

## Rules

- Action items have a due date and become GitHub issues when they take more than 30 minutes.
- A blocker gets the `blocker` label on the related issue, and the card moves to Block on the board.
- Hours are logged honestly in the work log; they feed the Lean Six Sigma dashboard and the individual reflection.
- Communication with the instructor is summarized (date, topic, outcome), not pasted.
- Do not put personal contact details in notes.

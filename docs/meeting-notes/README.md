# Meeting notes

How to use: one Markdown file per meeting or per stand-up week. The Scrum Master for the sprint writes the notes (or delegates and checks them) and opens a PR within 24 hours; another member reviews it. Notes-only changes may be batched once a week. Decisions recorded here that change the question, method, scope, tooling, or process are copied into `docs/workspace/DECISION_LOG.md`, and into `docs/decisions/` as an ADR when significant.

## File naming

`YYYY-MM-DD-<type>.md`, where `<type>` is one of:

| Type | When | Template |
|---|---|---|
| `kickoff` | Group kickoff (2026-09-16) | `TEMPLATE-meeting.md` |
| `planning` | First Thursday of each sprint | `TEMPLATE-meeting.md` |
| `standup-week` | One file per week, dated Monday; each member adds rows Mon, Wed, Fri | `TEMPLATE-standup-week.md` |
| `checkin` | Mid-sprint Thursdays | `TEMPLATE-meeting.md` |
| `review` | Last Wednesday of the sprint (summary; full record in `docs/sprints/<sprint>/review.md`) | `TEMPLATE-meeting.md` |
| `retro` | Last Wednesday of the sprint (summary; full record in `docs/sprints/<sprint>/retrospective.md`) | `TEMPLATE-meeting.md` |

Examples: `2026-09-17-planning.md`, `2026-09-21-standup-week.md`, `2026-09-24-checkin.md`.

## Rules

- Attendance is recorded by name. Absences are not a problem; silence is. An absent member reads the notes and reacts on the PR within 48 hours.
- Action items have an owner and a due date and become GitHub issues when they take more than 30 minutes.
- Blockers raised in a stand-up get the `blocker` label on the related issue, and the card moves to Block on the board.
- Hours are logged honestly in the stand-up file; they feed the Lean Six Sigma dashboard and the individual reflections.
- Communication with the instructor is summarized (date, topic, outcome), not pasted.
- Do not put personal contact details in notes.

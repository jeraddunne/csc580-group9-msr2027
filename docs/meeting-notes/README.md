# Meeting notes

How to use: one Markdown file per meeting or per stand-up week. The Scrum Master for the sprint writes the notes (or delegates and checks them) and opens a PR within 24 hours. Decisions recorded here are copied into `docs/decisions/` as an ADR when they change the question, method, scope, tooling, or process.

## File naming

`YYYY-MM-DD-<type>.md`, where `<type>` is one of:

| Type | When | Template |
|---|---|---|
| `kickoff` | Formation kickoff (2026-09-16) | `TEMPLATE-meeting.md` |
| `planning` | First Thursday of each sprint | `TEMPLATE-meeting.md` |
| `standup-week` | One file per week, dated Monday; rows added Mon, Wed, Fri | `TEMPLATE-standup-week.md` |
| `checkin` | Mid-sprint Thursdays | `TEMPLATE-meeting.md` |
| `review` | Last Wednesday of the sprint (summary; full record in `docs/sprints/<sprint>/review.md`) | `TEMPLATE-meeting.md` |
| `retro` | Last Wednesday of the sprint (summary; full record in `docs/sprints/<sprint>/retrospective.md`) | `TEMPLATE-meeting.md` |

Examples: `2026-09-17-planning.md`, `2026-09-21-standup-week.md`, `2026-09-24-checkin.md`.

## Rules

- Attendance is recorded by name. Absences are not a problem; silence is. An absent member reads the notes and reacts with a thumbs-up on the PR within 48 hours.
- Action items must have an owner and a due date and are mirrored as GitHub issues when they take more than 30 minutes.
- Blockers raised in a stand-up get the `blocker` label on the related issue and move the card to Block on the board.
- Hours are logged honestly in the stand-up file; they feed the Lean Six Sigma dashboard and the individual reflection.
- Do not paste personal contact details into notes.

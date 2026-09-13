# Team

How to use: one profile per member (from `TEMPLATE-member-profile.md`), the role rotation, and the RACI. Update your own profile by pull request whenever your availability changes.

## Roster

| Member | GitHub | Profile | Onboarding issue |
|---|---|---|---|
| Leticia Aderhold | _pending_ | `leticia-aderhold.md` | _pending_ |
| Jerad Dunne | @jeraddunne | `jerad-dunne.md` | _pending_ |
| Allie Hodges | _pending_ | `allie-hodges.md` | _pending_ |
| Hina Kramer | _pending_ | `hina-kramer.md` | _pending_ |

## Role rotation

Proposed on 2026-09-13; confirm at the 2026-09-16 kickoff and update `project.yml` (`roles:`) if changed.

| Period | Product Owner | Scrum Master (also metrics owner) |
|---|---|---|
| Formation (Sep 10 to 16) | Jerad Dunne | Jerad Dunne |
| Sprint 1 (Sep 17 to Oct 7) | Jerad Dunne | Leticia Aderhold |
| Sprint 2 (Oct 8 to Oct 28) | Allie Hodges | Hina Kramer |
| Sprint 3 (Oct 29 to Nov 18) | Leticia Aderhold | Jerad Dunne |
| Finalization (Nov 30 to Dec 4) | Hina Kramer | Allie Hodges |

Rationale: every member holds each of the two roles at least once across the semester; the member who set up the repository holds Product Owner first so the initial backlog matches the rubric, then hands over.

## What each role does

See `TEAM_CHARTER.md` section 3 for the definitions and `RACI.md` for activity-level responsibility.

## Adding a member's GitHub handle

1. The member submits the onboarding issue.
2. The Scrum Master runs `python scripts/invite_team.py` after adding the handle to `project.yml`.
3. The member's first PR adds their profile here and their signature to the charter.

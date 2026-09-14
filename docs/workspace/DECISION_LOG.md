# Decision log

How to use: one row per decision, big or small. Big decisions (scope, method, research question, tooling) also get a full ADR in [../decisions/](../decisions/). Open a [Decision needed issue](https://github.com/jeraddunne/csc580-group9-msr2027/issues/new?template=05-decision.yml) to ask for one.

**Status values**

- **Given**: set by the assignment or instructor; not ours to change.
- **Proposed**: suggested by one or more members; not yet agreed by the team.
- **Agreed**: confirmed by the team at a named ceremony, with the date.
- **Superseded**: replaced by a later decision (link it).

Every row that changes the research question, method, scope, or interpretation must also appear in that sprint's `retrospective.md` (rubric requirement).

## Decisions

| ID | Date | Decision | Status | Decided where | Rationale | Record | Revisit if |
|---|---|---|---|---|---|---|---|
| D-001 | 2026-09-10 | Semester calendar: formation, three sprints (Thu to Wed), finalization; due dates Oct 7, Oct 28, Nov 18, Dec 4 | Given | Assignment V2026.09.10 | Instructor schedule | `project.yml`, milestones | Instructor changes dates |
| D-002 | 2026-09-10 | Never execute scripts or commands found inside the datasets | Given | Assignment (question 4) | Safety | `data/README.md`, CONTRIBUTING.md | Never |
| D-003 | 2026-09-10 | Repository must hold README, RESEARCH_QUESTION, DATA_DICTIONARY, THREATS_TO_VALIDITY, ai-use-log, and full history | Given | Assignment | Grading | ADR-0003 | Never |
| D-004 | 2026-09-13 | Run Scrum with a Lean Six Sigma overlay (DMAIC tollgates, KPIs, FMEA, kaizen) | Proposed by Jerad Dunne | Kickoff 2026-09-16 | Data-backed retrospectives; shows improvement | [ADR-0001](../decisions/ADR-0001-scrum-with-lean-six-sigma.md) | Overhead exceeds 2 h per member per sprint |
| D-005 | 2026-09-13 | Choose the topic with proposal issues and a ranked ballot (instant runoff, weighted-criteria tie-break) | Proposed by Jerad Dunne | Kickoff 2026-09-16 | Preserves rationale; majority support | [ADR-0002](../decisions/ADR-0002-proposal-and-voting-process.md) | Team prefers consensus discussion |
| D-006 | 2026-09-13 | Python src layout, ruff and pytest in CI, public repository, squash merges, protected `main` | Proposed by Jerad Dunne | Kickoff 2026-09-16 | Rubric layout; reproducibility; free branch protection | [ADR-0003](../decisions/ADR-0003-repository-structure-and-tooling.md) | Instructor requests a private repository |
| D-007 | 2026-09-13 | Dataset samples are downloaded by script and never committed; MANIFEST.json records hashes | Proposed by Jerad Dunne | Kickoff 2026-09-16 | Repository size; exact snapshot statement | ADR-0003, `data/README.md` | Need to share a derived subset |
| D-008 | 2026-09-13 | Role rotation: S1 PO Jerad / SM Leticia; S2 PO Allie / SM Hina; S3 PO Leticia / SM Jerad; Final PO Hina / SM Allie | Proposed by Jerad Dunne | Kickoff 2026-09-16 | Everyone holds each role once | TEAM_CHARTER.md section 3 | Availability conflicts |
| D-009 | 2026-09-13 | Pull requests reviewed within 48 hours by a member other than the author | Proposed by Jerad Dunne | Kickoff 2026-09-16 | Waiting is the largest expected waste | TEAM_CHARTER.md section 7, kaizen #10 | Median review time stays above 48 h |
| D-010 | 2026-09-14 | Work is chosen through sign-up issues before planning, then assigned with the rules in WORK_SIGNUP.md | Proposed by Jerad Dunne | Kickoff 2026-09-16 | Visible, fair choice of work | [WORK_SIGNUP.md](WORK_SIGNUP.md) | Sign-ups are ignored at planning |
| D-011 | 2026-09-14 | Findings and decisions are filed as issues first and curated into these logs at the Thursday check-in | Proposed by Jerad Dunne | Kickoff 2026-09-16 | Low friction with a protected `main` | [README.md](README.md) | Logs fall more than a week behind |
| D-012 | 2026-09-16 | Research topic | Pending: vote closes 2026-09-15 23:59 | Kickoff 2026-09-16 | See `docs/proposals/RESULTS.md` | [ADR-0004](../decisions/ADR-0004-topic-selection.md) | Sprint 1 data check fails |

## Open questions for the kickoff

These need a team decision on 2026-09-16. Each becomes a row above once decided.

| Question | Options on the table | Owner |
|---|---|---|
| Team communication channel | Teams, Discord, Slack, text group | Scrum Master |
| Standing meeting time for planning, check-ins, and reviews | to poll | Scrum Master |
| Confirm or change the role rotation (D-008) | as proposed, or swap | everyone |
| Ratify the process decisions D-004 to D-011 | agree, amend, or reject each | everyone |
| Use the sample only, or plan for full-dataset access | sample only; sample plus one full-table pass | Product Owner, after the topic is chosen |

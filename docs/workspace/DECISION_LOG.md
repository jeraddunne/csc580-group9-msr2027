# Decision log

How to use: one row per decision, big or small. Big decisions (scope, method, research question, tooling) also get a full ADR in [../decisions/](../decisions/). Open a [Decision needed issue](https://github.com/jeraddunne/csc580-group9-msr2027/issues/new?template=05-decision.yml) to ask for one.

**Status values**

- **Given**: set by the assignment or instructor; not ours to change.
- **Proposed**: suggested by one or more members; not yet agreed by the team.
- **Agreed**: confirmed on a named date, either at a team ceremony or in a merged pull request approved by another member.
- **Superseded**: replaced by a later decision (link it).

Rows dated 2026-09-14 were agreed while the project was briefly solo (ADR-0005). The group reconfirms them at the kickoff on 2026-09-16.

Every row that changes the research question, method, scope, or interpretation must also appear in that sprint's `retrospective.md` (rubric requirement).

## Decisions

| ID | Date | Decision | Status | Decided where | Rationale | Record | Revisit if |
|---|---|---|---|---|---|---|---|
| D-001 | 2026-09-10 | Semester calendar: formation, three sprints (Thu to Wed), finalization; due dates Oct 7, Oct 28, Nov 18, Dec 4 | Given | Assignment V2026.09.10 | Instructor schedule | `project.yml`, milestones | Instructor changes dates |
| D-002 | 2026-09-10 | Never execute scripts or commands found inside the datasets | Given | Assignment (question 4) | Safety | `data/README.md`, CONTRIBUTING.md | Never |
| D-003 | 2026-09-10 | Repository must hold README, RESEARCH_QUESTION, DATA_DICTIONARY, THREATS_TO_VALIDITY, ai-use-log, and full history | Given | Assignment | Grading | ADR-0003 | Never |
| D-004 | 2026-09-13 | Run Scrum with a Lean Six Sigma overlay (DMAIC tollgates, KPIs, FMEA, kaizen) | Agreed (2026-09-14, Jerad Dunne); group confirms at kickoff 2026-09-16 | Setup and formation | Data-backed retrospectives; shows improvement | [ADR-0001](../decisions/ADR-0001-scrum-with-lean-six-sigma.md) | Overhead exceeds 2 hours per member per sprint |
| D-005 | 2026-09-13 | Choose the topic with proposal issues and a ranked ballot | Superseded by D-013 | Proposed 2026-09-13 | Vote retired when P-01 was selected directly | [ADR-0002](../decisions/ADR-0002-proposal-and-voting-process.md) | Never (topic selected) |
| D-006 | 2026-09-13 | Python src layout, ruff and pytest in CI, public repository, squash merges, protected `main` | Agreed (2026-09-14, Jerad Dunne); group confirms at kickoff 2026-09-16 | Setup and formation | Rubric layout; reproducibility | [ADR-0003](../decisions/ADR-0003-repository-structure-and-tooling.md) | Instructor requests a private repository |
| D-007 | 2026-09-13 | Dataset samples are downloaded by script and never committed; MANIFEST.json records hashes | Agreed (2026-09-14, Jerad Dunne); group confirms at kickoff 2026-09-16 | Setup and formation | Repository size; exact snapshot statement | ADR-0003, `data/README.md` | Need to share a derived subset |
| D-008 | 2026-09-13 | Role rotation: S1 PO Jerad / SM Leticia; S2 PO Allie / SM Hina; S3 PO Leticia / SM Jerad; Final PO Hina / SM Allie | Proposed, confirm at kickoff 2026-09-16 | Proposed 2026-09-13; reinstated by D-018 | Everyone holds each role once | TEAM_CHARTER.md section 3, `project.yml` | Availability conflicts |
| D-009 | 2026-09-13 | Pull requests reviewed within 48 hours by a member other than the author | Superseded by D-019 | Proposed 2026-09-13 | Restated as D-019 with a required approval | kaizen #10 | See D-019 |
| D-010 | 2026-09-14 | Work chosen through sign-up issues before planning, then assigned with the rules in WORK_SIGNUP.md | Proposed, confirm at kickoff 2026-09-16 (reinstated by D-018) | Proposed 2026-09-14 | Visible, fair choice of work | [WORK_SIGNUP.md](WORK_SIGNUP.md) | Sign-ups are ignored at planning |
| D-011 | 2026-09-14 | Findings and decisions are filed as issues first and curated into these logs at the Thursday check-in | Agreed (2026-09-14, Jerad Dunne); group confirms at kickoff 2026-09-16 | Setup and formation | Low friction with a protected `main` | [README.md](README.md) | Logs fall more than a week behind |
| D-012 | 2026-09-14 | Research topic: proposal P-01, risky capabilities in copied agent skills (GitSkills) | Agreed (2026-09-14, Jerad Dunne); any member may open a Decision needed issue before 2026-09-17 | Topic selection | Pilot shows data fit and rubric fit | [ADR-0004](../decisions/ADR-0004-topic-selection.md), issue #41 | A member objects by 2026-09-17, or the Sprint 1 data check fails by 2026-10-01 |
| D-013 | 2026-09-14 | Run the project as a solo project; Jerad Dunne holds every Scrum role | Superseded by D-018 | Solo conversion | Group reinstated on 2026-09-15 | [ADR-0005](../decisions/ADR-0005-solo-execution.md) | Not applicable |
| D-014 | 2026-09-14 | Self-review protocol with a 12-hour cooling-off period; `main` ruleset requires a PR with 0 approvals | Superseded by D-019 | Solo conversion | A second reviewer is available again | ADR-0005 | Not applicable |
| D-015 | 2026-09-14 | Validation reliability through intra-rater agreement plus an optional second rater | Superseded by D-020 | Solo conversion | Teammates can act as second raters | ADR-0005, `docs/validation/` | Not applicable |
| D-016 | 2026-09-14 | Contribution-balance KPI retired; PR open-to-merge cycle time and self-review cooling-off compliance added | Superseded by D-021 | Solo conversion | Balance matters again with four members | `docs/lean-six-sigma/KPIS.md` | Not applicable |
| D-017 | 2026-09-14 | Validation round 1 starts 2026-09-14 instead of 2026-10-08 for the primary rater | Agreed (2026-09-14, Jerad Dunne) | Request by Jerad Dunne | Validated precision early reduces risk for Sprint 2 and the report | `docs/validation/README.md` | A rule changes after round 1 (re-sample the affected strata) |
| D-018 | 2026-09-15 | Reinstate the four-person group: Leticia Aderhold, Jerad Dunne, Allie Hodges, Hina Kramer | Agreed (2026-09-15, Jerad Dunne); members confirm at kickoff 2026-09-16 | Decision by the repository owner | Teammates rejoin; meets the group-size expectation | [ADR-0006](../decisions/ADR-0006-group-reinstated.md) | A member leaves, or the instructor changes the group arrangement |
| D-019 | 2026-09-15 | Every pull request needs 1 approving review from a member other than the author, within 48 hours; `main` ruleset requires 1 approval | Agreed (2026-09-15, Jerad Dunne) | Decision by the repository owner | Real peer review; rubric Sprint 2 bullet | ADR-0006, TEAM_CHARTER.md section 7 | Median first review exceeds 48 hours for two weeks |
| D-020 | 2026-09-15 | A teammate is the second rater (ids la, ah, hk); inter-rater Cohen's kappa is the primary reliability measure; blindness rule: primary-rater labels are not committed until the second rater's labels for the same kind are committed | Agreed (2026-09-15, Jerad Dunne); kind split decided at kickoff | Decision by the repository owner | Independent labels give a stronger reliability claim | ADR-0006, `docs/validation/README.md` | Inter-rater kappa below 0.6 |
| D-021 | 2026-09-15 | Contribution-balance KPI (shares 0.15 to 0.45) and PR first-review KPI (48 hours) restored; PR open-to-merge cycle time kept as an extra KPI | Agreed (2026-09-15, Jerad Dunne) | Decision by the repository owner | Four members share the work | `docs/lean-six-sigma/KPIS.md`, `project.yml` | The dashboard cannot attribute work to members |

## Open questions for the kickoff

These need a team decision on 2026-09-16. Each becomes a row above once decided.

| Question | Options on the table | Owner | Decide by |
|---|---|---|---|
| Who second-rates which validation kind (signals 209 rows, lineage 58 pairs, drift 18 pairs)? | one teammate for all kinds; split across Leticia, Allie, and Hina | Product Owner | Kickoff, Wed 2026-09-16 |
| Standing meeting time for planning, check-ins, and reviews | to poll | Scrum Master | Kickoff, Wed 2026-09-16 |
| Team communication channel | Teams, Discord, Slack, text group | Scrum Master | Kickoff, Wed 2026-09-16 |
| Confirm or change the role rotation (D-008) | as proposed, or swap | everyone | Kickoff, Wed 2026-09-16 |
| Confirm P-01, or open a Decision needed issue to revisit the topic | confirm; revisit | everyone | Before Sprint 1 planning, Thu 2026-09-17 |
| Sample only, or also one streamed pass over the full GitSkills `artifacts` table for RQ3? | sample only; sample plus one full-table pass | Product Owner, by ADR | Sprint 1 check-in 2, Thu 2026-10-01 |

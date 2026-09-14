# Decision log

How to use: one row per decision, big or small. Big decisions (scope, method, research question, tooling) also get a full ADR in [../decisions/](../decisions/). Open a [Decision needed issue](https://github.com/jeraddunne/csc580-group9-msr2027/issues/new?template=05-decision.yml) to record an open decision.

**Status values**

- **Given**: set by the assignment or instructor; not ours to change.
- **Proposed**: written down but not yet confirmed.
- **Agreed**: confirmed on a named date. In this solo project, "Agreed" means confirmed by the sole member (ADR-0005) in a dated planning note or pull request.
- **Superseded**: replaced by a later decision (link it).

Every row that changes the research question, method, scope, or interpretation must also appear in that sprint's `retrospective.md` (rubric requirement).

## Decisions

| ID | Date | Decision | Status | Decided where | Rationale | Record | Revisit if |
|---|---|---|---|---|---|---|---|
| D-001 | 2026-09-10 | Semester calendar: formation, three sprints (Thu to Wed), finalization; due dates Oct 7, Oct 28, Nov 18, Dec 4 | Given | Assignment V2026.09.10 | Instructor schedule | `project.yml`, milestones | Instructor changes dates |
| D-002 | 2026-09-10 | Never execute scripts or commands found inside the datasets | Given | Assignment (question 4) | Safety | `data/README.md`, CONTRIBUTING.md | Never |
| D-003 | 2026-09-10 | Repository must hold README, RESEARCH_QUESTION, DATA_DICTIONARY, THREATS_TO_VALIDITY, ai-use-log, and full history | Given | Assignment | Grading | ADR-0003 | Never |
| D-004 | 2026-09-13 | Run Scrum with a Lean Six Sigma overlay (DMAIC tollgates, KPIs, FMEA, kaizen) | Agreed (2026-09-14, sole member) | Solo conversion | Data-backed retrospectives; shows improvement | [ADR-0001](../decisions/ADR-0001-scrum-with-lean-six-sigma.md) | Overhead exceeds 2 hours per sprint |
| D-005 | 2026-09-13 | Choose the topic with proposal issues and a ranked ballot | Superseded by D-013 | Proposed 2026-09-13 | Group decision method no longer needed | [ADR-0002](../decisions/ADR-0002-proposal-and-voting-process.md) | Project returns to a group |
| D-006 | 2026-09-13 | Python src layout, ruff and pytest in CI, public repository, squash merges, protected `main` | Agreed (2026-09-14, sole member) | Solo conversion | Rubric layout; reproducibility | [ADR-0003](../decisions/ADR-0003-repository-structure-and-tooling.md) | Instructor requests a private repository |
| D-007 | 2026-09-13 | Dataset samples are downloaded by script and never committed; MANIFEST.json records hashes | Agreed (2026-09-14, sole member) | Solo conversion | Repository size; exact snapshot statement | ADR-0003, `data/README.md` | Need to share a derived subset |
| D-008 | 2026-09-13 | Rotating Product Owner and Scrum Master roles across four members | Superseded by D-013 | Proposed 2026-09-13 | Solo: one person holds every role | TEAM_CHARTER.md (version 1.0, in git history) | Project returns to a group |
| D-009 | 2026-09-13 | Pull requests reviewed within 48 hours by a member other than the author | Superseded by D-013 and D-014 | Proposed 2026-09-13 | No second member | kaizen #10 | Project returns to a group |
| D-010 | 2026-09-14 | Work chosen through sign-up issues before planning | Superseded by D-013 | Proposed 2026-09-14 | Solo workstream plan replaces sign-ups | [WORK_SIGNUP.md](WORK_SIGNUP.md) | Project returns to a group |
| D-011 | 2026-09-14 | Findings and decisions are filed as issues first and curated into these logs at the Thursday check-in | Agreed (2026-09-14, sole member) | Solo conversion | Low friction with a protected `main` | [README.md](README.md) | Logs fall more than a week behind |
| D-012 | 2026-09-14 | Research topic: proposal P-01, risky capabilities in copied agent skills (GitSkills) | Agreed (2026-09-14, sole member) | Solo conversion | Pilot shows data fit and rubric fit | [ADR-0004](../decisions/ADR-0004-topic-selection.md), issue #41 | Sprint 1 data check fails by 2026-10-01 |
| D-013 | 2026-09-14 | Run the project as a solo project; Jerad Dunne holds every Scrum role | Agreed by student, pending instructor confirmation | Solo conversion | Decision by the student; the assignment states groups of three to five | [ADR-0005](../decisions/ADR-0005-solo-execution.md) | No instructor confirmation by 2026-10-07, or instructor asks for a group |
| D-014 | 2026-09-14 | Self-review protocol: every change by pull request, self-review after at least 12 hours with the PR checklist, CI green once enabled, optional external review on major PRs; `main` ruleset requires a PR with 0 approvals | Agreed by student, pending instructor confirmation | Solo conversion | Substitute for cross-member review | ADR-0005, TEAM_CHARTER.md section 7 | Defects escape review twice in one sprint |
| D-015 | 2026-09-14 | Validation reliability through intra-rater agreement (re-label a random 30% at least 7 days later, Cohen's kappa) plus an optional second rater; an LLM rater is disclosed and never counted as human agreement | Agreed by student, pending instructor confirmation | Solo conversion | Substitute for two independent annotators | ADR-0005, `docs/validation/` | Intra-rater kappa below 0.6 |
| D-016 | 2026-09-14 | Contribution-balance KPI retired; PR open-to-merge cycle time (target 48 hours) and self-review cooling-off compliance added | Agreed (2026-09-14, sole member) | Solo conversion | Balance is meaningless for one person | `docs/lean-six-sigma/KPIS.md`, `project.yml` | Project returns to a group |

## Open questions

Each becomes a row above once decided.

| Question | Options | Owner | Decide by |
|---|---|---|---|
| Does the instructor accept solo execution? | confirmed; asked to join a group | Jerad Dunne (email the instructor) | Sprint 1 review, Wed 2026-10-07 |
| Sample only, or also one streamed pass over the full GitSkills `artifacts` table for RQ3? | sample only; sample plus one full-table pass | Jerad Dunne, by ADR | Sprint 1 second check-in, Thu 2026-10-01 |
| Request an instructor review on the validation pull request? | request; self-review only | Jerad Dunne | Sprint 2 planning, Thu 2026-10-08 |
| Make the repository private during development? | stay public; private with GitHub Pro from the Student Developer Pack and the instructor invited | Jerad Dunne | Sprint 1 planning, Thu 2026-09-17 |

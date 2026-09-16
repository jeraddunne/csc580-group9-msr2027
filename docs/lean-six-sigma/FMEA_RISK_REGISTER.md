# FMEA risk register

Failure Mode and Effects Analysis scores each risk on Severity (S), Occurrence (O), and Detection (D), each 1 to 10, and multiplies them into a Risk Priority Number (RPN = S x O x D, max 1000). Higher RPN means act sooner. Detection is scored so that 1 means the problem would be noticed immediately and 10 means it would only surface at grading.

**Review rule.** Read the top five RPN rows at every sprint planning. Any row with RPN >= 200 must have a named owner role and a trigger. Scores are updated at every sprint review; the change history records what moved.

**Group note (ADR-0006).** The four-person group was reinstated on 2026-09-15. Owner roles below follow the rotation in `project.yml`. Risks R05, R06, R11, and R12 were rewritten for the group, and R16 was replaced, on 2026-09-15.

## Scoring guide

| Score | Severity | Occurrence | Detection |
|---|---|---|---|
| 1 to 3 | Minor rework, no grade impact | Unlikely this semester | Caught the same day by CI, tests, or stand-ups |
| 4 to 6 | Sprint deliverable degraded | Could happen once | Caught within the sprint by review or check-in |
| 7 to 9 | Sprint deliverable missed | Likely at least once | Caught only at sprint review or later |
| 10 | Project fails or academic integrity issue | Expected without action | Not detectable before submission |

## Register

| ID | Failure mode | Effect | Cause | S | O | D | RPN | Mitigation | Owner role | Trigger | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R01 | The full 41 GB GitSkills SQLite is attempted instead of the 277 MB sample | Days lost to downloads and out-of-memory failures; pipeline not reproducible on a laptop | Ambition, unclear scope decision | 7 | 6 | 3 | 126 | Sample is the approved population by default; any full-dataset pass needs an ADR (Sprint 1) and runs as a separate streamed step | Product Owner | Any PR referencing the full dump | Open |
| R02 | SpecMine sample is non-representative (61 percent of repos have >= 100 stars vs 1.3 percent in the full corpus; 97.5 percent of specs first committed in 2026) | Findings overgeneralized if SpecMine is used | Sample was built to be PR-rich, not random | 7 | 9 | 4 | 252 | P-01 does not use SpecMine; if any SpecMine result is reported, frame it as "in this sample" and state the bias | Product Owner | Any SpecMine claim in the report | Open |
| R03 | GitHub code search is a lower bound (default branches only, files under 384 KB, active repos, forks only if more starred than parent) | Population statements are wrong | Dataset construction limits | 6 | 9 | 4 | 216 | Define the population as "files indexed by GitHub code search in July 2026"; list the limits in the threats section | Developers | Report draft review | Open |
| R04 | Commit history in GitSkills follows the current file path, so renames reset `first_commit_at` and `commit_count` | Variant ordering (RQ3) and age metrics biased | Dataset limitation | 6 | 7 | 5 | 210 | Document in the data dictionary; treat ordering as uncertain; inspect renamed cases in the validation sample | Developers | Any metric using `first_commit_at` or `commit_count` | Open |
| R05 | A member is unavailable for a week or more (illness, work, family) | Their sprint items stall; review and validation work waits | Life; four schedules | 6 | 6 | 3 | 108 | Every workstream has a lead and a support; stand-ups surface absence early; re-plan at the Thursday check-in; the Thanksgiving break is buffer | Scrum Master | Two missed stand-ups in a row by the same member | Open |
| R06 | Uneven contribution: one or two members do most of the work | Individual grades and learning suffer; burnout; rubric evidence of shared work is weak | Most of the repository was built by one member before the group was reinstated; unclear ownership | 7 | 7 | 3 | 147 | Work sign-up rules (`docs/workspace/WORK_SIGNUP.md`); contribution-balance KPI with band 0.15 to 0.45 read at every check-in; escalation path in `TEAM_CHARTER.md` section 10 | Scrum Master | Any member's contribution share outside the band at a check-in | Open |
| R07 | Scope creep after topic selection (a second question, a second dataset, a model not needed) | Nothing finishes; report is shallow | Enthusiasm, no Definition of Ready | 8 | 7 | 3 | 168 | New scope must be an issue approved at planning; `added_after_planning` reported per sprint | Product Owner | `added_after_planning` above 20 percent of committed items | Open |
| R08 | Pipeline does not run on a clean machine (missing dependency, hard-coded path, undocumented download step) | Sprint 3 and final acceptance criteria fail | Code is only run in its author's environment | 9 | 7 | 4 | 252 | CI runs tests from scratch; gemba walk at every sprint review from a fresh clone, by a member who did not write the README | Developers | CI failure or gemba walk failure | Open |
| R09 | A member executes scripts or commands bundled in dataset artifacts | Security incident, academic integrity issue; rubric explicitly forbids it | Curiosity, copy-paste while debugging | 10 | 3 | 8 | 240 | Dataset content is data, never code; loaders read `content` as text only; static analysis only; no `subprocess` on dataset content in `src/` (checked in review) | Scrum Master | Any PR that opens dataset content with anything other than a text reader | Open |
| R10 | AI-use log incomplete or disclosure missing from the report | Responsible AI criterion failed | Forgetting to log; unclear what counts | 8 | 6 | 6 | 288 | `ai-use-log.md` entry is a PR template checkbox and a reviewer checklist item; checked at each Thursday check-in; disclosure paragraph is a report section from Sprint 2 | Scrum Master | PR merged with the checkbox unticked | Open |
| R11 | Rater disagreement or loss of rater independence (low inter-rater kappa, or the second rater sees the primary rater's labels) | Validation cannot support the result; precision overstated or unreliable | Vague definitions; new raters with little practice; primary label files visible in the repository | 7 | 5 | 4 | 140 | Written guideline and practice items before labelling; blindness rule in `docs/validation/README.md`; second-rater PR contains only their own label file; adjudication in error analysis; kappa reported | Product Owner | Inter-rater kappa below 0.6, or a primary-rater label file changed before the second rater's file for that kind is committed | Open |
| R12 | Reviews are delayed, so PRs wait on the one required approval | Work piles up unmerged; merge conflicts; sprint items finish late | Four schedules; reviews treated as lower priority than own work | 5 | 6 | 3 | 90 | 48-hour review SLA; reviewer rotation; first-review KPI read at every check-in; Friday week summary lists PRs waiting more than 48 hours | Scrum Master | Median first-review turnaround above 48 hours for two weeks | Open |
| R13 | OneDrive sync conflicts with the git working tree (locked files, "conflicted copy" files, corrupted `.git`) | Lost commits, confusing diffs | The repository folder lives inside a synced OneDrive directory | 6 | 7 | 3 | 126 | Clone the repository outside OneDrive for daily work (for example `C:\dev\`); never commit files named `*-conflicted copy*` | Developers | Any file with "conflicted copy" in the name | Open |
| R14 | Thanksgiving gap (Nov 19 to Nov 29) between Sprint 3 and Finalization loses momentum | Finalization week is a scramble | Calendar | 6 | 8 | 2 | 96 | Sprint 3 review produces a finalization checklist with owners and dates before the break; one stand-up on Nov 25 | Scrum Master | Sprint 3 review without a finalization checklist | Open |
| R15 | Instructor adjusts sprint dates | Milestones, timeline, and metrics windows are wrong | Institutional calendar | 4 | 5 | 1 | 20 | Dates live in one place (`project.yml`); a change updates milestones via `scripts/bootstrap_github.py` and is recorded in the decision log | Scrum Master | Any date change announced in class | Open |
| R16 | Members onboard late in formation (invited 2026-09-15, one day before the kickoff) | Charter signatures, setup, and first contributions slip into Sprint 1; Sprint 1 capacity is overestimated | Group reinstated late in formation week (ADR-0006) | 6 | 6 | 3 | 108 | Onboarding path in `docs/GETTING_STARTED.md`; onboarding issue form; pairing during setup; Sprint 1 item S1-12; first week sized for ramp-up | Scrum Master | Any onboarding issue still open at Sprint 1 planning on 2026-09-17 | Open |

## Sorted by RPN

| Rank | ID | RPN | Failure mode |
|---|---|---|---|
| 1 | R10 | 288 | AI-use log incomplete |
| 2 | R02 | 252 | SpecMine sample non-representative |
| 2 | R08 | 252 | Pipeline not reproducible on a clean machine |
| 4 | R09 | 240 | Executing untrusted dataset scripts |
| 5 | R03 | 216 | Code search lower-bound population |
| 6 | R04 | 210 | Commit history follows current path |
| 7 | R07 | 168 | Scope creep after topic selection |
| 8 | R06 | 147 | Uneven contribution |
| 9 | R11 | 140 | Rater disagreement or loss of independence |
| 10 | R01 | 126 | Full 41 GB dataset attempted |
| 10 | R13 | 126 | OneDrive sync conflicts |
| 12 | R05 | 108 | Member unavailable |
| 12 | R16 | 108 | Members onboard late in formation |
| 14 | R14 | 96 | Thanksgiving gap |
| 15 | R12 | 90 | Review delays |
| 16 | R15 | 20 | Instructor adjusts dates |

## Change history

| Date | Sprint | Change |
|---|---|---|
| 2026-09-13 | Formation | Initial register with 15 risks |
| 2026-09-14 | Formation | Solo conversion (ADR-0005): R05 and R06 rewritten for a single point of failure and workload; R11 rewritten for single-annotator validation (RPN 168 to 210); R12 rewritten for self-review (RPN 80 to 120); R16 added for the rubric group requirement; R02 mitigation notes that P-01 does not use SpecMine |
| 2026-09-15 | Formation | Group reinstated (ADR-0006): R05 rewritten for member availability (RPN 80 to 108); R06 rewritten for uneven contribution (168 to 147); R11 rewritten for rater disagreement and independence with a teammate second rater (210 to 140); R12 rewritten for review delays (120 to 90); R16 replaced by late onboarding in formation (108); R03, R08, R09, and R14 wording updated for cross-member review and stand-ups |

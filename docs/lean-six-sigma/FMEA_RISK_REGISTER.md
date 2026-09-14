# FMEA risk register

Failure Mode and Effects Analysis scores each risk on Severity (S), Occurrence (O), and Detection (D), each 1 to 10, and multiplies them into a Risk Priority Number (RPN = S x O x D, max 1000). Higher RPN means act sooner. Detection is scored so that 1 means the problem would be noticed immediately and 10 means it would only surface at grading.

**Review rule.** Read the top five RPN rows at every sprint planning. Any row with RPN >= 200 must have a named owner role and a trigger. Scores are updated at every sprint review; the change history records what moved.

**Solo note (ADR-0005).** The project is run solo by Jerad Dunne, who holds every owner role below. Risks R05, R06, R11, and R12 were rewritten for one person on 2026-09-14, and R16 was added.

## Scoring guide

| Score | Severity | Occurrence | Detection |
|---|---|---|---|
| 1 to 3 | Minor rework, no grade impact | Unlikely this semester | Caught the same day by CI, tests, or the work log |
| 4 to 6 | Sprint deliverable degraded | Could happen once | Caught within the sprint by self-review or check-in |
| 7 to 9 | Sprint deliverable missed | Likely at least once | Caught only at sprint review or later |
| 10 | Project fails or academic integrity issue | Expected without action | Not detectable before submission |

## Register

| ID | Failure mode | Effect | Cause | S | O | D | RPN | Mitigation | Owner role | Trigger | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R01 | The full 41 GB GitSkills SQLite is attempted instead of the 277 MB sample | Days lost to downloads and out-of-memory failures; pipeline not reproducible on a laptop | Ambition, unclear scope decision | 7 | 6 | 3 | 126 | Sample is the approved population by default; any full-dataset pass needs an ADR (Sprint 1) and runs as a separate streamed step | Product Owner | Any PR referencing the full dump | Open |
| R02 | SpecMine sample is non-representative (61 percent of repos have >= 100 stars vs 1.3 percent in the full corpus; 97.5 percent of specs first committed in 2026) | Findings overgeneralized if SpecMine is used | Sample was built to be PR-rich, not random | 7 | 9 | 4 | 252 | P-01 does not use SpecMine; if any SpecMine result is reported, frame it as "in this sample" and state the bias | Product Owner | Any SpecMine claim in the report | Open |
| R03 | GitHub code search is a lower bound (default branches only, files under 384 KB, active repos, forks only if more starred than parent) | Population statements are wrong | Dataset construction limits | 6 | 9 | 4 | 216 | Define the population as "files indexed by GitHub code search in July 2026"; list the limits in the threats section | Developers | Report draft self-review | Open |
| R04 | Commit history in GitSkills follows the current file path, so renames reset `first_commit_at` and `commit_count` | Variant ordering (RQ3) and age metrics biased | Dataset limitation | 6 | 7 | 5 | 210 | Document in the data dictionary; treat ordering as uncertain; inspect renamed cases in the validation sample | Developers | Any metric using `first_commit_at` or `commit_count` | Open |
| R05 | The sole member is unavailable for a week or more (illness, work, family) | Sprint commitment missed with no backup person | Life; single point of failure | 8 | 5 | 2 | 80 | Descope order in `TEAM_CHARTER.md` section 9; use the Thanksgiving break as buffer; tell the instructor early | Scrum Master | Two missed work-log entries in a row | Open |
| R06 | Single-person workload exceeds available hours | Deliverables degraded or late; report rushed | One person holds every role and workstream | 8 | 7 | 3 | 168 | Hours plan in `docs/workspace/WORK_SIGNUP.md`; commitment reliability reviewed weekly; descope order applied early rather than late | Scrum Master | Commitment reliability below 0.8 in any sprint | Open |
| R07 | Scope creep after topic selection (a second question, a second dataset, a model not needed) | Nothing finishes; report is shallow | Enthusiasm, no Definition of Ready | 8 | 7 | 3 | 168 | New scope must be an issue approved at planning; `added_after_planning` reported per sprint | Product Owner | `added_after_planning` above 20 percent of committed items | Open |
| R08 | Pipeline does not run on a clean machine (missing dependency, hard-coded path, undocumented download step) | Sprint 3 and final acceptance criteria fail | Everything is run from the author's own environment | 9 | 7 | 4 | 252 | CI runs tests from scratch; gemba walk at every sprint review from a fresh clone in a clean environment, by a classmate if available | Developers | CI failure or gemba walk failure | Open |
| R09 | The author executes scripts or commands bundled in dataset artifacts | Security incident, academic integrity issue; rubric explicitly forbids it | Curiosity, copy-paste while debugging | 10 | 3 | 8 | 240 | Dataset content is data, never code; loaders read `content` as text only; static analysis only; no `subprocess` on dataset content in `src/` (checked in self-review) | Scrum Master | Any PR that opens dataset content with anything other than a text reader | Open |
| R10 | AI-use log incomplete or disclosure missing from the report | Responsible AI criterion failed | Forgetting to log; unclear what counts | 8 | 6 | 6 | 288 | `ai-use-log.md` entry is a PR template checkbox; checked at each Thursday check-in; disclosure paragraph is a report section from Sprint 2 | Scrum Master | PR merged with the checkbox unticked | Open |
| R11 | Single-annotator validation is unreliable or biased | Validation cannot support the result; precision overstated | No independent second annotator; vague definitions | 7 | 6 | 5 | 210 | Written guideline before labelling; pilot on 10 records; intra-rater re-label of a random 30% at least 7 days later with Cohen's kappa; second rater when available; limitation stated | Developers | Intra-rater kappa below 0.6 | Open |
| R12 | Self-review is rushed or skipped | Defects reach `main`; rework later | No second reviewer; deadline pressure | 5 | 6 | 4 | 120 | 12-hour cooling-off; PR self-review checklist and review comment; CI; external review on major PRs | Scrum Master | Any non-trivial PR merged less than 12 hours after opening | Open |
| R13 | OneDrive sync conflicts with the git working tree (locked files, "conflicted copy" files, corrupted `.git`) | Lost commits, confusing diffs | The repository folder lives inside a synced OneDrive directory | 6 | 7 | 3 | 126 | Clone the repository outside OneDrive for daily work (for example `C:\dev\`); never commit files named `*-conflicted copy*` | Developers | Any file with "conflicted copy" in the name | Open |
| R14 | Thanksgiving gap (Nov 19 to Nov 29) between Sprint 3 and Finalization loses momentum | Finalization week is a scramble | Calendar | 6 | 8 | 2 | 96 | Sprint 3 review produces a finalization checklist with dates before the break; one work-log entry on Nov 25 | Scrum Master | Sprint 3 review without a finalization checklist | Open |
| R15 | Instructor adjusts sprint dates | Milestones, timeline, and metrics windows are wrong | Institutional calendar | 4 | 5 | 1 | 20 | Dates live in one place (`project.yml`); a change updates milestones via `scripts/bootstrap_github.py` and is recorded in the decision log | Scrum Master | Any date change announced in class | Open |
| R16 | Instructor does not accept solo execution (the assignment describes groups of three to five) | Rework to join a group; rubric penalty; lost time | Solo decision made by the student (ADR-0005) | 9 | 4 | 3 | 108 | Ask the instructor at the Sprint 1 kickoff (2026-09-16); revisit ADR-0005 by 2026-10-07; keep the retired group process files so they can be reinstated quickly | Product Owner | No response by the Thursday check-in on 2026-09-24 (follow up), or a request to join a group | Open |

## Sorted by RPN

| Rank | ID | RPN | Failure mode |
|---|---|---|---|
| 1 | R10 | 288 | AI-use log incomplete |
| 2 | R02 | 252 | SpecMine sample non-representative |
| 2 | R08 | 252 | Pipeline not reproducible on a clean machine |
| 4 | R09 | 240 | Executing untrusted dataset scripts |
| 5 | R03 | 216 | Code search lower-bound population |
| 6 | R04 | 210 | Commit history follows current path |
| 6 | R11 | 210 | Single-annotator validation unreliable |
| 8 | R06 | 168 | Single-person workload |
| 8 | R07 | 168 | Scope creep after topic selection |
| 10 | R01 | 126 | Full 41 GB dataset attempted |
| 10 | R13 | 126 | OneDrive sync conflicts |
| 12 | R12 | 120 | Self-review rushed or skipped |
| 13 | R16 | 108 | Instructor does not accept solo execution |
| 14 | R14 | 96 | Thanksgiving gap |
| 15 | R05 | 80 | Sole member unavailable |
| 16 | R15 | 20 | Instructor adjusts dates |

## Change history

| Date | Sprint | Change |
|---|---|---|
| 2026-09-13 | Formation | Initial register with 15 risks |
| 2026-09-14 | Formation | Solo conversion (ADR-0005): R05 and R06 rewritten for a single point of failure and workload; R11 rewritten for single-annotator validation (RPN 168 to 210); R12 rewritten for self-review (RPN 80 to 120); R16 added for the rubric group requirement; R02 mitigation notes that P-01 does not use SpecMine |

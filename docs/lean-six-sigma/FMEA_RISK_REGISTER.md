# FMEA risk register

Failure Mode and Effects Analysis scores each risk on Severity (S), Occurrence (O), and Detection (D), each 1 to 10, and multiplies them into a Risk Priority Number (RPN = S x O x D, max 1000). Higher RPN means act sooner. Detection is scored so that 1 means we would notice immediately and 10 means we would only find out at grading.

**Review rule.** The Scrum Master reads the top five RPN rows at every sprint planning. Any row with RPN >= 200 must have a named owner role and a trigger. Scores are updated at every sprint review; the change column records the previous RPN.

## Scoring guide

| Score | Severity | Occurrence | Detection |
|---|---|---|---|
| 1 to 3 | Minor rework, no grade impact | Unlikely this semester | Caught the same day by CI, tests, or stand-up |
| 4 to 6 | Sprint deliverable degraded | Could happen once | Caught within the sprint by review or check-in |
| 7 to 9 | Sprint deliverable missed | Likely at least once | Caught only at sprint review or later |
| 10 | Project fails or academic integrity issue | Expected without action | Not detectable before submission |

## Register

| ID | Failure mode | Effect | Cause | S | O | D | RPN | Mitigation | Owner role | Trigger | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R01 | Team attempts the full 41 GB GitSkills SQLite instead of the 277 MB sample | Days lost to downloads and out-of-memory failures; pipeline not reproducible on laptops | Ambition, unclear scope decision | 7 | 6 | 3 | 126 | Sample is the approved population by default (ADR); any full-dataset query must be a separate issue with a justification and run on one machine | Product Owner | Any PR referencing the Zenodo full dump | Open |
| R02 | SpecMine sample is non-representative (61 percent of repos have >= 100 stars vs 1.3 percent in the full corpus; 97.5 percent of specs first committed in 2026) | Findings overgeneralized; external validity threat missed | Sample was built to be PR-rich, not random | 7 | 9 | 4 | 252 | State the sampling bias in `RESEARCH_QUESTION.md` and `THREATS_TO_VALIDITY.md`; frame results as "in this sample"; compare against full-corpus counts published in the dataset README where possible | Product Owner | Any claim in the report of the form "specs in general" | Open |
| R03 | GitHub code search is a lower bound (default branches only, files under 384 KB, active repos, forks only if more starred than parent) | Population statements are wrong; reviewer challenges | Dataset construction limits | 6 | 9 | 4 | 216 | Define the population as "files indexed by GitHub code search in July 2026"; list the limits in the threats section | Developers | Report draft review | Open |
| R04 | Commit history in GitSkills follows the current file path, so renames reset `first_commit_at` and `commit_count` | Age, churn, and staleness metrics biased | Dataset limitation | 6 | 7 | 5 | 210 | Document in the data dictionary; treat age metrics as lower bounds; manually inspect renamed cases in the validation sample | Developers | Any metric using `first_commit_at` or `commit_count` | Open |
| R05 | A member is unavailable for a week or more (illness, work, family) | Sprint commitment missed | Life | 6 | 6 | 2 | 72 | Charter: announce absences on the stand-up issue; every item has a backup owner; commitment reliability is reviewed weekly | Scrum Master | Two missed stand-ups in a row | Open |
| R06 | Uneven contribution (one member above 45 percent or below 15 percent) | Individual contribution grade at risk; resentment; single point of failure | Skill mismatch, unclear assignments | 7 | 6 | 3 | 126 | Contribution balance KPI weekly; rotate roles at sprint boundaries; pair on hard items | Scrum Master | Dashboard flag on any member | Open |
| R07 | Scope creep after the topic vote (adding a second question, a second dataset, a model nobody needs) | Nothing finishes; report is shallow | Enthusiasm, no Definition of Ready | 8 | 7 | 3 | 168 | Any new scope must be an issue with the `sprint-goal` label approved at planning; `added_after_planning` reported per sprint | Product Owner | `added_after_planning` above 20 percent of committed items | Open |
| R08 | Pipeline does not run on a clean machine (missing dependency, hard-coded path, undocumented download step) | Sprint 3 and final acceptance criteria fail | Everyone runs it from their own environment | 9 | 7 | 4 | 252 | CI runs the pipeline on the sample from scratch; gemba walk at every sprint review by a member who did not write the README | Developers | CI failure or gemba walk failure | Open |
| R09 | A member executes scripts or commands bundled in dataset artifacts | Security incident, academic integrity issue; rubric explicitly forbids it | Curiosity, copy-paste while debugging | 10 | 3 | 8 | 240 | Charter rule: dataset content is data, never code; loaders read `content` as text only; static analysis only; no `subprocess` on dataset content in `src/` (checked in code review) | Scrum Master | Any PR that opens dataset content with anything other than a text reader | Open |
| R10 | AI-use log incomplete or disclosure missing from the report | Responsible AI criterion failed | Forgetting to log; unclear what counts | 8 | 6 | 6 | 288 | `ai-use-log.md` entry is a PR template checkbox; the Scrum Master checks it at each Thursday check-in; disclosure paragraph is a report section from Sprint 2 | Scrum Master | PR merged with the checkbox unticked | Open |
| R11 | Manual validation annotators disagree (low agreement on the sample) | Validation cannot support the result | Vague operational definitions | 7 | 6 | 4 | 168 | Write the annotation protocol before annotating; pilot on 10 records; compute agreement (percent and Cohen kappa); revise definitions and re-annotate | Developers | Pilot agreement under 70 percent | Open |
| R12 | PRs sit unreviewed for days | Cycle time and merge time blow up; work piles up before the review | No reviewer assigned; no SLA | 5 | 8 | 2 | 80 | Reviewer assigned at PR open; 48 h SLA in charter; dashboard lists PRs older than 48 h | Scrum Master | `pr_first_review_hours` median above 48 | Open |
| R13 | OneDrive sync conflicts with the git working tree (locked files, duplicated "conflicted copy" files, corrupted `.git`) | Lost commits, confusing diffs | The repository folder lives inside a synced OneDrive directory | 6 | 7 | 3 | 126 | Clone the repository outside OneDrive for daily work (for example `C:\dev\`); never commit files named `*-conflicted copy*`; add the pattern to `.gitignore` | Each member | Any file with "conflicted copy" in the name | Open |
| R14 | Thanksgiving gap (Nov 19 to Nov 29) between Sprint 3 and Finalization loses momentum | Finalization week is a scramble | Calendar | 6 | 8 | 2 | 96 | Sprint 3 review produces a finalization checklist with owners and dates before the break; one async stand-up on Nov 25 | Scrum Master | Sprint 3 review without a finalization checklist | Open |
| R15 | Instructor adjusts sprint dates | Milestones, timeline, and metrics windows are wrong | Institutional calendar | 4 | 5 | 1 | 20 | Dates live in one place (`project.yml`); a change updates milestones via `scripts/bootstrap_github.py` and is recorded in an ADR | Scrum Master | Any date change announced in class | Open |

## Sorted by RPN

| Rank | ID | RPN | Failure mode |
|---|---|---|---|
| 1 | R10 | 288 | AI-use log incomplete |
| 2 | R02 | 252 | SpecMine sample non-representative |
| 2 | R08 | 252 | Pipeline not reproducible on a clean machine |
| 4 | R09 | 240 | Executing untrusted dataset scripts |
| 5 | R03 | 216 | Code search lower-bound population |
| 6 | R04 | 210 | Commit history follows current path |
| 7 | R07 | 168 | Scope creep after the vote |
| 7 | R11 | 168 | Annotator disagreement |
| 9 | R01 | 126 | Full 41 GB dataset attempted |
| 9 | R06 | 126 | Uneven contribution |
| 9 | R13 | 126 | OneDrive sync conflicts |
| 12 | R14 | 96 | Thanksgiving gap |
| 13 | R12 | 80 | Late PR reviews |
| 14 | R05 | 72 | Member unavailable |
| 15 | R15 | 20 | Instructor adjusts dates |

## Change history

| Date | Sprint | Change |
|---|---|---|
| 2026-09-13 | Formation | Initial register with 15 risks |

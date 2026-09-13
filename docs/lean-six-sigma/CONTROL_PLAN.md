# Control plan

The control plan is the Control phase of DMAIC. It says what we keep watching after the work is done, how, how often, and what we do when something drifts. Parts of it run every sprint (the gemba walk); all of it runs in Finalization (Nov 30 to Dec 4).

## Monitored items

| What is monitored | How (method, tool) | Frequency | Owner role | Reaction plan |
|---|---|---|---|---|
| Pipeline reproducibility | CI workflow runs tests and the pipeline on the sample from a clean runner; `reproducibility_check` in dashboard | Every push to `main` and weekly | Developers | Red CI blocks merges; fix within 24 h; if the fix is not obvious open a `bug` issue with `priority:high` |
| Fresh-clone reproduction (gemba walk) | A member who did not write the README clones into a new folder, follows only the README, regenerates the primary figures, and records the result below | Every sprint review and once in Finalization | Rotating (see table) | Any deviation is a README or script bug; fix before the tollgate is passed |
| Figure and table freshness | `make figures` (or `run_pipeline.sh`) regenerates every file in `figures/` and `results/`; git diff must be empty except timestamps | Sprint 3 review, Finalization | Developers | Stale figure means the report cites something the code no longer produces; regenerate and re-check the report text |
| Report claims traceable to results | Each result table or figure in the report names the script and output file that produced it | Sprint 3 review, Finalization | Product Owner | Untraceable claim is removed or regenerated |
| Threats to validity complete | `THREATS_TO_VALIDITY.md` has internal, construct, external, conclusion, reproducibility sections with at least one concrete threat each | Sprint 3 review | Product Owner | Missing section is a `rubric` issue |
| AI-use log complete | Every merged PR has the AI-use checkbox ticked or an entry in `ai-use-log.md` | Thursday check-in, Finalization | Scrum Master | Add the missing entry the same day |
| Process KPIs | `metrics/DASHBOARD.md` (weekly snapshot) | Weekly | Scrum Master | `warn` two weeks running triggers a 5 Whys |
| Release integrity | Tagged release exists; tag matches the commit the report cites; release notes list the artifacts | Sprint 3 review, Finalization | Scrum Master | Re-tag and update the report appendix |
| Repository access | Instructor and all members have access; repository is public or the instructor is a collaborator | Formation, Finalization | Scrum Master | Fix access immediately |
| Individual reflections | Four files in `docs/reflections/` | Finalization | Each member | Missing file is raised at the Dec 1 stand-up |

## Gemba walk procedure (reproducibility walk)

"Gemba" means the place where the work happens. Here it means: go to a clean machine and see whether the README is true.

1. Pick the walker: the member who has touched the README least this sprint (see rotation).
2. On a machine or folder without the repository: `git clone https://github.com/jeraddunne/csc580-group9-msr2027.git walk-<date>`.
3. Follow `README.md` from the top. Do not use any knowledge that is not in the README. Do not ask the author.
4. Stop at the first step that fails or is unclear. Record the step and the message.
5. If everything passes, confirm that the primary figure files exist and open.
6. Fill in the log row below and, for any failure, open an issue labeled `bug` and `rubric`.
7. Total time budget: 30 minutes. If it takes longer, that is itself a finding.

### Walker rotation

| Sprint review | Walker | Backup |
|---|---|---|
| Sprint 1 (Oct 7) | Member who did not write the README | Scrum Master |
| Sprint 2 (Oct 28) | Next member in alphabetical order | Product Owner |
| Sprint 3 (Nov 18) | Next member | Scrum Master |
| Finalization (Dec 2) | The remaining member | Any |

Fill in names at Sprint 1 planning once roles are assigned.

### Gemba walk log

| Date | Walker | Commit or tag | Result | Time taken | First failing step | Issue # |
|---|---|---|---|---|---|---|
| | | | | | | |

## Finalization week schedule (Nov 30 to Dec 4)

| Day | Activity | Control item |
|---|---|---|
| Mon Nov 30 | Stand-up; instructor feedback triaged into issues | Report claims, threats |
| Tue Dec 1 | Final gemba walk on the release candidate tag | Fresh-clone reproduction |
| Wed Dec 2 | Fix findings; regenerate figures; final metrics snapshot run manually | Figure freshness, KPIs |
| Thu Dec 3 | Tag final release; report PDF built; presentation rehearsal | Release integrity |
| Fri Dec 4 | Submit; reflections merged; repository access confirmed | Reflections, access |

## Handover

After submission the repository stays as the record. No further changes are made except to fix a reproduction failure reported by the instructor, which is done on a branch and released as a patch tag with a note in the release description.

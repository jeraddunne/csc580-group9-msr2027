# Individual contribution and reflection: Jerad Dunne (@jeraddunne)

Status: Working draft, 2026-11-11. Sprint 3 is ongoing.
Related to [issue #39](https://github.com/jeraddunne/csc580-group9-msr2027/issues/39).

## 1. Roles held

Roles follow [project.yml](../../project.yml) and the [team charter](../../TEAM_CHARTER.md).

| Period | Role | Main responsibility |
|---|---|---|
| Formation (Sep 10 to 16) | Product Owner and Scrum Master | Set up the repository, the CI, the issue forms, and the first analysis and validation kit |
| Sprint 1 (Sep 17 to Oct 7) | Product Owner | Backlog, requirements and spec, onboarding paths for members new to Git |
| Sprint 2 (Oct 8 to 28) | Product Owner | Round 1 labels for all three kinds, validation results in the report, the Sprint 2 review evidence |
| Sprint 3 (Oct 29 to Nov 18) | Scrum Master | Retrospective with the PR review audit, the threat areas, the final tool, and the round 2 re-rating |
| Finalization (Nov 30 to Dec 4) | Developer/Researcher | Not started |

## 2. Contribution summary

| Area | What I did | Evidence | Sprint |
|---|---|---|---|
| Project setup | Created the repository structure, CI, weekly Lean Six Sigma metrics, and issue forms. Set up the first analysis and the validation kit. | [#44][44], [#45][45], [#47][47] | Formation |
| Helping the team start with Git | Built a no-Git path (browser guide, guided tasks, Windows launchers) and a project guide web app, so members new to Git could contribute. Documented clean-environment reproduction. | [#70][70], [#72][72], [#74][74] | 1 |
| Requirements | Notebook elicitation and the research specification with executable acceptance tests. | [#55][55] | 1 |
| Validation and annotation | Primary rater `jd` for all three kinds: signals round 1 (209 rows), lineage (58 pairs), drift (18 pairs). Blind signals round 2 re-rating (69 rows) for the intra-rater check. | [#118][118], [#124][124], [#166][166] | 2, 3 |
| Labelling tools and formulas | Built the labelling studio and the Excel labelling workbook (status, reason, and pace formulas, and a work log). | [#81][81], [#86][86] | 1, 2 |
| Analysis and results | First validation scores, the ground-truth check of the ten known-positive skills, and the corrected FMEA ranking. | [#119][119], [#133][133], [#127][127] | 2 |
| Report sections written | Validation results (Table 2), intended use, the six threat areas, and the intra-rater result. | [#127][127], [#126][126], [#149][149], [#166][166] | 2, 3 |
| Final tool | skill-scan as a command line tool, a GitHub Action, and a VS Code extension. | [#151][151] | 3 |
| Process work | Sprint 1 baseline metrics, Sprint 2 review evidence, and the Sprint 3 retrospective with a PR review audit. | [#134][134], [#135][135], [#148][148] | 2, 3 |
| Code reviews given | Reviewed 17 teammate pull requests. | [search](https://github.com/jeraddunne/csc580-group9-msr2027/pulls?q=is%3Apr+reviewed-by%3Ajeraddunne+-author%3Ajeraddunne) | 1 to 3 |
| Error analysis review | Judged the two pending credential cases against the threat model: one context only, one a confirmed false negative. | [PR #162 comment](https://github.com/jeraddunne/csc580-group9-msr2027/pull/162#issuecomment-6804850737) | 3 |

Merged pull requests I authored: Formation 7, Sprint 1 11, Sprint 2 16, Sprint 3 3 (so far).

Hours: not totaled. The stand-up files on main hold one week (2026-09-28), so I have no recorded hours to report.

## 3. What I learned

- **Working in a Git project.** I learned to run a shared repository the way a team needs it: branches, pull requests, required reviews, CI, and issues that link to the work. Early in the project I helped teammates get started with the Git concepts, and I built a no-Git path so everyone could contribute while they learned.
- **Getting started takes time.** Setting the project up properly took longer than I expected: structure, CI, data access, the spec, and the onboarding guides all had to exist before the research work could move.
- **AI in the work process.** I used Claude Code to help update, close, and push pull requests and to build the formulas in the labelling workbook and the metrics. That helped set the project up properly. I made the decisions and did the labelling myself.
- **Changing formulas and processes as we learned.** As the team found different ways to track changes, we changed the formulas and processes with them. One example is the FMEA calculation, which mixed two populations until a review caught it. Another is the PR review audit, which measured whether merges waited for another member's approval.
- **Research reasoning.** A keyword match is not a capability. The scanner's signals need human labels before they mean anything, and a single rater needs an intra-rater check.

## 4. What I would change

- **About my own work.** In Sprint 1, eight merges went in without another member's approval, and all eight were mine ([#148][148]). I would wait for an approval from the start.
- **About how the team worked.** Share the Git onboarding earlier, so everyone could open pull requests from the first week.
- **About the project design if we started again.** Plan the second rater for signals from the start, not only an intra-rater check.

## 5. Honest self-assessment

| Question | Answer (1 to 5) | One sentence of evidence |
|---|---|---|
| I delivered what I committed to in sprint planning | _ | Round 1 labels for all three kinds and the Sprint 2 review evidence merged in Sprint 2; round 2 in Sprint 3 ([#166][166]). |
| My work was reviewed and I reviewed others' work | _ | 17 teammate PRs reviewed; from Sprint 2 on, every merge had another member's approval ([#148][148]). |
| I raised blockers early | _ | |
| My contributions are traceable in the repository | _ | Every row above links a PR or comment. |
| I understood the results well enough to present any part | _ | |

## 6. AI use statement

- **Tools used and for what:**
  - Claude Code (Claude Opus) for drafting code, documents, and PR text, building the labelling workbook formulas, and running the update, close, and push steps for pull requests.
  - Each use is logged in [ai-use-log.md](../../ai-use-log.md) under my name.
- **What I verified by hand and how:** test runs and CI on each PR, the numbers in the report against the results files, and the scores after each import.
- **What I did without AI assistance:**
  - All of my labels: signals rounds 1 and 2, lineage, and drift.
  - The verdicts on the known-positive cases.
  - The decisions on scope and process.

## 7. Signature

- Name: Jerad Dunne. Date: ____. I confirm this reflection is accurate and links only to my own work.

[44]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/44
[45]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/45
[47]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/47
[55]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/55
[70]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/70
[72]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/72
[74]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/74
[81]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/81
[86]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/86
[118]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/118
[119]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/119
[124]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/124
[126]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/126
[127]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/127
[133]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/133
[134]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/134
[135]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/135
[148]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/148
[149]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/149
[151]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/151
[166]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/166

# Individual contribution and reflection: Hina Kramer (@hinak786)

Status: Working draft, updated 2026-11-10. Sprint 3 is ongoing.
Related to [issue #39](https://github.com/jeraddunne/csc580-group9-msr2027/issues/39).

## 1. Roles held

Roles follow [project.yml](../../project.yml) and the [team charter](../../TEAM_CHARTER.md).

| Period | Role | Main responsibility or status |
|---|---|---|
| Formation (Sep 10–16) | Developer/Researcher in the recorded rotation | Participation details not yet documented here |
| Sprint 1 (Sep 17–Oct 7) | Developer/Researcher | Onboarding, guided reproduction, documentation, and peer review |
| Sprint 2 (Oct 8–28) | Scrum Master and Researcher | Process tracking, lineage second-rating, reproduction, and peer review |
| Sprint 3 (Oct 29–Nov 18) | Developer/Researcher | Report and PR reviews, evidence checks, and follow-up; ongoing |
| Finalization (Nov 30–Dec 4) | Product Owner in the planned rotation | Period has not started |

## 2. Contribution summary

| Area | What I did | Evidence | Sprint |
|---|---|---|---|
| Team documentation | Updated my profile and charter signature, started this reflection, and recorded my October 2 stand-up. | [PR #77][77], [PR #78][78], [PR #83][83] | 1 |
| Reproduction and testing | Used the Windows workflow with ChatGPT guidance. All 14 compared result files matched; my recorded local test run passed 166 tests with 96% coverage. | [PR #79][79] | 1 |
| Validation | Selected and submitted round 1 lineage labels for all 58 frozen sample pairs as rater `hk`. I chose the labels and supplied the observation in my uncertainty note. | [PR #121][121] | 2 |
| Fresh reproduction | Reproduced the analysis from a fresh ZIP snapshot on Windows 11 with Python 3.12.10. All 14 compared CSVs matched. Analysis took 2.1 minutes; recorded elapsed time was 71.6 minutes, including setup and pauses. | [PR #136][136] | 2 |
| Validation review | Reviewed the validity of the submitted drift-label file with Codex assistance while preserving the rater’s judgments. | [PR #90][90] | 2 |
| Calculation review | With Codex assistance, identified that the FMEA calculation mixed context-match counts with precision measured on high-risk matches. Requested a correction and regression test, then approved the corrected version after documented rechecks. | [PR #127][127] | 2 |
| Report review | Reviewed numerical claims and interpretation with Codex assistance, including the distinction between scanner signals and validated findings. Approved the revised report after the merge conflict was resolved. | [PR #144][144] | 3 |
| Regeneration review | Reviewed Make targets, source mapping, and AI-use disclosures. Requested restoration of an earlier log entry and correction of the PR description; recorded the follow-up checks. Full clean-checkout verification remains pending under #30. | [PR #153][153] | 3 |

Hours have not yet been totaled from the stand-up records. The reproduction session duration above is not a total contribution-hours figure.

## 3. What I learned

I practiced editing Markdown on a branch, committing changes, preparing pull requests, and following up on review feedback.

Reproducing the outputs helped me connect commands, environments, and evidence. I learned why the snapshot identifier, Python version, analysis runtime, and total elapsed time need to be recorded separately.

The validation work helped me distinguish scanner matches from human-validated findings. The FMEA review showed why the population used in a calculation must match the population used to measure precision.

I also learned that passing automated checks, receiving approval, and meeting an issue’s acceptance criteria are separate steps. Before-and-after process metrics show changes, but do not establish their cause by themselves.

## 4. What I would change

- Record evidence links and work time as I complete each task.
- Clarify conflicting deadlines and acceptance criteria earlier.
- Use a short walkthrough connecting each research question to its inputs, command, output, and limitations.

## 5. Honest self-assessment

Personal ratings remain pending my final review.

| Question | Rating (1–5) | Evidence to consider |
|---|---|---|
| I delivered what I committed to | Pending | Compare sprint commitments with the contribution table |
| My work was reviewed and I reviewed others’ work | Pending | [PR #121][121], [PR #136][136], and the linked reviews |
| I raised blockers early | Pending | Review the timing of concerns in [PR #127][127] and [PR #153][153] |
| My contributions are traceable | Pending | Evidence links in Section 2 |
| I understood the results well enough to present them | Pending | Confirm through presentation preparation and rehearsal |

## 6. AI use statement

ChatGPT/Codex assisted with Windows setup guidance, documentation drafting, GitHub workflow explanations, review preparation, source checks, and this update.

I selected the lineage labels and supplied my uncertainty observation. The assistance and material shared during that work are described in [PR #121][121].

I performed the recorded Windows reproduction runs locally. Checks executed by Codex are identified as such in the linked reviews.

This reflection and [ai-use-log.md](../../ai-use-log.md) must remain consistent. My personal accuracy review and teammate review of this update are pending.

## 7. Signature

Name: Hina Kramer

Final accuracy confirmation and signature date: pending.

[77]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/77
[78]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/78
[79]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/79
[83]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/83
[90]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/90
[121]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/121
[127]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/127
[136]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/136
[144]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/144
[153]: https://github.com/jeraddunne/csc580-group9-msr2027/pull/153

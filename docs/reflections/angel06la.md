# Individual contribution and reflection: Leticia Aderhold (@angel06la)

Working draft as of November 11, 2026. Sprint 3 is ongoing, and finalization work is not yet complete.

## 1. Roles held

| Period | Role | Main responsibility |
|---|---|---|
| Formation (Sep 10 to 16) | Developer/Researcher | Participated in project preparation and learning the repository workflow. |
| Sprint 1 (Sep 17 to Oct 7) | Developer/Researcher; proposed Scrum Master assignment to confirm | Supported documentation, project coordination, and understanding the research workflow. |
| Sprint 2 (Oct 8 to 28) | Developer/Researcher | Contributed validation labels, reproducibility checks, research documentation, and sprint evidence. |
| Sprint 3 (Oct 29 to Nov 18) | Developer/Researcher; proposed Product Owner assignment to confirm | Documented validation results and error examples, improved reproduction instructions, and tracked remaining acceptance gaps. |
| Finalization (Nov 30 to Dec 4) | Planned Developer/Researcher | Complete final documentation, presentation preparation, and reflection accuracy review. |

Role rotation is listed in [project.yml](../../project.yml); the proposed Scrum Master and Product Owner assignments need confirmation.

## 2. Contribution summary

| Area | What I did | Evidence | Sprint |
|---|---|---|---|
| Research framing | Contributed to documenting where existing static-analysis tools apply to the project. | [Applicability comparison](../research/APPLICABILITY.md), [#96](https://github.com/jeraddunne/csc580-group9-msr2027/issues/96) | 2 |
| Data acquisition and dictionary | Used the existing dataset for validation and reproduction; I do not claim primary responsibility for acquisition or dictionary implementation. | [Validation documentation](../validation/README.md) | 2–3 |
| Pipeline code | Added Make targets and report-table generation support rather than implementing the core scanner. | [PR #153](https://github.com/jeraddunne/csc580-group9-msr2027/pull/153) | 3 |
| Tests and reproduction | Reproduced committed outputs and checked generated files for differences, including a fresh-clone workflow. | [Sprint 2 review](../sprints/sprint-2/review.md), [#30](https://github.com/jeraddunne/csc580-group9-msr2027/issues/30) | 2–3 |
| Validation and annotation | Independently second-rated 18 drift pairs using rater ID `la` and helped inspect known-positive examples. | [PR #90](https://github.com/jeraddunne/csc580-group9-msr2027/pull/90), [#97](https://github.com/jeraddunne/csc580-group9-msr2027/issues/97) | 2 |
| Analysis, tables, figures | Documented worked false-positive examples and a Bash false negative; added four further case observations awaiting teammate classification review. | [PR #145](https://github.com/jeraddunne/csc580-group9-msr2027/pull/145), [PR #152](https://github.com/jeraddunne/csc580-group9-msr2027/pull/152), [PR #162](https://github.com/jeraddunne/csc580-group9-msr2027/pull/162) | 3 |
| Report sections written | Updated the report's validation summary and reporting status. | [PR #144](https://github.com/jeraddunne/csc580-group9-msr2027/pull/144), [PR #155](https://github.com/jeraddunne/csc580-group9-msr2027/pull/155) | 3 |
| Report sections reviewed | Checked reported results against committed outputs and identified unresolved interpretation requirements. | [#27](https://github.com/jeraddunne/csc580-group9-msr2027/issues/27) | 3 |
| Code reviews given | Formal review count and links still need auditing; authoring a PR or requesting review is not counted as reviewing another member's work. | Review history to confirm | All |
| Meeting notes, stand-ups, and process work | Updated sprint evidence and documented review-process comparisons. | [PR #94](https://github.com/jeraddunne/csc580-group9-msr2027/pull/94), [PR #141](https://github.com/jeraddunne/csc580-group9-msr2027/pull/141) | 2–3 |
| Presentation | Contributed presentation planning and supporting evidence; final delivery remains upcoming. | [PR #142](https://github.com/jeraddunne/csc580-group9-msr2027/pull/142), [#34](https://github.com/jeraddunne/csc580-group9-msr2027/issues/34) | 3 |

Approximate hours: not yet totaled. I will calculate Sprint 1, Sprint 2, Sprint 3, finalization, and total hours from the committed stand-up records.

## 3. What I learned

- **Mining software repositories:** Distinct content and occurrences measure different things. Duplicate copies affect reach, so the unit of analysis must be clear.
- **Research reasoning:** Scanner matches are observations, while claims about risk require interpretation and validation. Sample precision does not directly establish population prevalence.
- **Scrum and Lean Six Sigma:** Review records and acceptance criteria help identify unfinished work. Passing CI alone does not establish that a research requirement is satisfied.
- **Technical skills:** I developed experience with GitHub branches and pull requests, Python commands in PowerShell, CSV inspection, and reproducibility checks.

## 4. What I would change

- **My work:** Record evidence links, commands, and outcomes as I complete tasks instead of reconstructing them near a deadline.
- **Team workflow:** Agree earlier on ownership, reviewer responsibilities, and the meaning of acceptance criteria.
- **Project design:** Plan human-label validation and its connection to each research question before producing headline results.

## 5. Honest self-assessment

Ratings will be completed by me before submission.

| Question | Answer (1 to 5) | Evidence |
|---|---|---|
| I delivered what I committed to in sprint planning | To confirm | Linked contributions are documented above; some work remains ongoing. |
| My work was reviewed and I reviewed others' work | To confirm | My PRs received teammate feedback; my own formal review count needs verification. |
| I raised blockers early | To confirm | I documented unresolved classification and acceptance questions in #27 and PR #162. |
| My contributions are traceable in the repository | To confirm | The contribution table links to specific PRs, issues, and documents. |
| I understood the results well enough to present any part | To confirm | I can explain the validation and reproduction work; broader presentation readiness needs rehearsal. |

## 6. AI use statement

- **Tools and purpose:** I used ChatGPT for drafting, explaining commands, troubleshooting, and organizing evidence. This reflection also received ChatGPT assistance. These uses must be recorded consistently in [ai-use-log.md](../../ai-use-log.md).
- **Verification:** I ran commands locally, inspected their outputs, compared generated files, and checked source excerpts and committed results. Pending teammate judgments remain identified as pending.
- **Work without AI assistance:** I will identify specific independently completed activities before submission rather than assume that assisted work was unassisted.

## 7. Signature

Name: Leticia Aderhold  
Status: Working draft; personal accuracy confirmation pending.  
Final confirmation and date will be added after I verify this reflection and its evidence links.

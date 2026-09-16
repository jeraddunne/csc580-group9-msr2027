# Topic proposals and voting

> **Proposals and voting are closed.** Proposal P-01 was selected on 2026-09-14 ([ADR-0004](../decisions/ADR-0004-topic-selection.md)), while the project was briefly solo ([ADR-0005](../decisions/ADR-0005-solo-execution.md)). The four-person group was reinstated on 2026-09-15 ([ADR-0006](../decisions/ADR-0006-group-reinstated.md)), and P-01 remains selected. Any member may open a [Decision needed issue](https://github.com/jeraddunne/csc580-group9-msr2027/issues/new?template=05-decision.yml) to revisit the topic before Sprint 1 planning on Thu 2026-09-17. The ranked-ballot vote stays retired. The rest of this page is kept as the record of the original process.

## Selected proposal

| ID | Proposer | Title | Dataset | Based on rubric question | Document | Issue | Status |
|---|---|---|---|---|---|---|---|
| P-01 | Jerad Dunne | Risky capabilities in copied agent skills: prevalence, reach, and drift | GitSkills | 4 (security and supply chain) with 1 (reuse and propagation) | [P-01](P-01-jerad-dunne-skill-risk-propagation.md) | [#41](https://github.com/jeraddunne/csc580-group9-msr2027/issues/41) | Selected 2026-09-14 |

Fallback topic if P-01 proves infeasible in Sprint 1: rubric question 2 (skill quality indicators), reusing the scanner output as features.

## Original process (retired)

The sections below describe the group process planned on 2026-09-13 (ADR-0002, superseded by ADR-0005).

### Timeline (as planned)

| Step | Deadline | Who |
|---|---|---|
| Read `00-candidate-questions.md` and the dataset READMEs | 2026-09-13 to 09-14 | everyone |
| Submit proposals via the **Project proposal** issue form (at least one each) | 2026-09-14 23:59 | everyone |
| Read every proposal; ask clarifying questions as issue comments | 2026-09-15 | everyone |
| Cast a ballot (PR adding `votes/ballots/<handle>.yml`) | 2026-09-15 23:59 | everyone |
| Tally (`make tally`), confirm at kickoff, write ADR-0004, fill `RESEARCH_QUESTION.md` | 2026-09-16 | Scrum Master, Product Owner |

### How proposals were to be written

1. Open **Issues > New issue > Project proposal**. The form asks for the precise research question, unit of analysis, tables and columns, the rubric's required implementation component and minimum evidence, feasibility, risks, and four self-scores.
2. Prefer questions the **sample data** can answer. The full GitSkills dataset is 41 GB; using it is a decision, not a default.
3. A proposal can refine a rubric question or combine two, but must still meet the rubric's "Required implementation component" for its base question.
4. `TEMPLATE-proposal.md` is an offline drafting template.

### How the vote was to work

- **Ballot:** each voter ranks acceptable proposals (best first) and scores each on five weighted criteria from 1 to 5 (weights in `project.yml` under `proposals.criteria`): feasibility 0.30, data_fit 0.20, rubric_fit 0.20, interest 0.15, low_risk 0.15.
- **Winner:** instant runoff on the rankings; ties broken by the weighted-criteria score, then by Borda count.
- **Transparency:** `python scripts/tally_votes.py` computes the result and writes `RESULTS.md`. The code remains tested in `tests/test_voting.py`.

## Files

| File | Purpose |
|---|---|
| `00-candidate-questions.md` | The 15 rubric questions summarized with data-fit and feasibility notes |
| `P-01-jerad-dunne-skill-risk-propagation.md` | The selected proposal |
| `TEMPLATE-proposal.md` | Offline drafting template (retired process) |
| `votes/README.md`, `votes/TEMPLATE-ballot.yml` | Ballot instructions and format (retired) |
| `votes/ballots/` | Ballot folder (unused) |
| `RESULTS.md` | Output of `scripts/tally_votes.py` (no ballots were cast) |

# Voting

> **Retired (ADR-0005).** The project became solo on 2026-09-14 and proposal P-01 was selected without a vote (ADR-0004). This page is kept as the record of the original process.

How to use: one ballot per member, submitted as a pull request. The vote closes 2026-09-15 23:59.

## Steps

1. Read every open issue with the `proposal` label. Ask questions in the issue comments before voting.
2. Copy `TEMPLATE-ballot.yml` to `ballots/<your-github-handle>.yml` (lowercase handle, no `@`).
3. Fill in:
   - `ranking`: proposal issue numbers, best first. Leave out any proposal you consider unacceptable.
   - `scores`: for every proposal you ranked, a 1 to 5 score on each criterion (`feasibility`, `data_fit`, `rubric_fit`, `interest`, `low_risk`). 5 is best in every case (for `low_risk`, 5 means very low risk).
   - `comment`: optional, one or two lines on your reasoning.
4. Run `python scripts/tally_votes.py` locally to check your ballot parses (it prints problems).
5. Open a PR titled `vote: <handle>` on a branch `process/vote-<handle>`. The tally workflow comments the current standings on the PR. Another member merges it (do not merge your own ballot).

## Rules

- One ballot per member. A second file from the same voter is rejected by the tally.
- You may change your ballot with a follow-up PR before the deadline.
- Ballots are public inside the team. That is intentional: the rationale is part of the decision record.
- The Scrum Master runs the final tally at kickoff and commits `docs/proposals/RESULTS.md`.

## Counting method

Instant runoff on `ranking` (majority of active ballots wins; the candidate with fewest first preferences is eliminated each round). Ties are broken by the weighted-criteria score (weights in `project.yml`), then Borda count. The full algorithm is in `src/msr_pipeline/voting.py` and is unit-tested.

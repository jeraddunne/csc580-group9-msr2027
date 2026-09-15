# ADR-0002: Select the topic by proposal issues and a ranked ballot

- **Status:** Superseded by ADR-0005 (2026-09-14). The project became solo, so no vote was held; P-01 was selected directly (ADR-0004).
- **Date:** 2026-09-13
- **Deciders:** Jerad Dunne (proposed); ratified by use during Formation
- **Decision issue:** Formation issue "Topic proposals submitted"
- **Affects research question / method / scope:** yes (it determines the research question)

## Context

The topic is worth 10% on its own and shapes the remaining 90%. Four members must converge on one question in three days (proposals by Sep 14, vote by Sep 15, decision Sep 16). A show of hands would be fast but leaves no rationale in the repository, and the rubric asks that decisions be recorded.

## Options considered

1. **Discussion and consensus in a meeting.** Fast, but undocumented and vulnerable to the loudest voice.
2. **Simple plurality vote on proposal issues (thumbs-up reactions).** Documented, but a plurality can pick a topic most members find unacceptable, and reactions carry no reasoning.
3. **Proposal issue form plus a ranked ballot with a weighted decision matrix, tallied by script.** Proposals are structured (question, data fit, rubric fit, feasibility, risks, self-scores). Each member ranks acceptable proposals and scores them on weighted criteria. Instant runoff picks a majority-supported winner; the weighted score breaks ties and documents the rationale. Slightly more effort per voter.

## Decision

Option 3. The issue form is the single place a proposal lives; ballots are YAML files reviewed by PR; `scripts/tally_votes.py` computes the result and writes `docs/proposals/RESULTS.md`; ADR-0004 records the outcome. Criteria weights: feasibility 0.30, data_fit 0.20, rubric_fit 0.20, interest 0.15, low_risk 0.15, chosen to favour a question the team can finish and validate with the sample data.

## Consequences

- Positive: rationale preserved; losing proposals' risk sections feed the threats file; the method is reusable for later decisions (for example choosing a validation design).
- Negative / risks: with four voters, ties are likely; the tie-break chain (weighted score, then Borda) is deterministic and documented. If a member misses the deadline the vote proceeds with the ballots received.
- Follow-up issues: write ADR-0004 after the tally; fill `RESEARCH_QUESTION.md`.

## Revisit trigger

If Sprint 1 shows the winning topic is infeasible with the sample data, reopen with a `decision` issue; the runner-up in RESULTS.md is the default fallback.

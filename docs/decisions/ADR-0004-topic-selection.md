# ADR-0004: Topic selection

- **Status:** Accepted
- **Date:** 2026-09-14
- **Deciders:** Jerad Dunne (sole member, see ADR-0005)
- **Decision issue:** #41 (proposal P-01)
- **Affects research question / method / scope:** yes

## Context

ADR-0002 planned a ranked-ballot vote over proposal issues. When the project became a solo project on 2026-09-14 (ADR-0005), the vote was retired and the topic was chosen directly by the sole member.

## Options considered

Only P-01 was considered, because no other proposals were submitted before the project became solo.

| Proposal | Title | Proposer | Rubric base | Notes |
|---|---|---|---|---|
| P-01 (#41) | Risky capabilities in copied agent skills: prevalence, reach, and drift | Jerad Dunne | Question 4 (skill security and supply-chain risk) with the similarity method from question 1 | Pilot already runs end to end on the GitSkills sample |

## Decision

P-01 is selected. The research question, as stated in `docs/proposals/P-01-jerad-dunne-skill-risk-propagation.md` section 2:

> In the GitSkills July 2026 sample, how prevalent are skill instructions and bundled scripts that enable risk-relevant capabilities, do skills carrying them reach more repositories through verbatim copying, and do modified variants of the same skill add or remove those capabilities?

`RESEARCH_QUESTION.md` is completed from the proposal in Sprint 1.

## Consequences

- **Positive:** the data fit and the rubric fit are already demonstrated by the pilot; the scanner, rule file, and tests exist.
- **Negative / risks:** keyword signals may have low precision; RQ3 (variant drift) is thin in the sample; validation depends on a single annotator (ADR-0005). These risks are carried into `THREATS_TO_VALIDITY.md` and `docs/lean-six-sigma/FMEA_RISK_REGISTER.md`.
- **Fallback:** rubric question 2 (skill quality indicators), reusing the scanner output as quality features.
- **Follow-up issues:** complete `RESEARCH_QUESTION.md` (#12, #13); decide sample only versus a full-dataset pass by ADR in Sprint 1; build the validation kit (#23).

## Revisit trigger

The Sprint 1 acceptance criterion "the question is answerable with the selected data" is not met by the second check-in on Thu 2026-10-01.

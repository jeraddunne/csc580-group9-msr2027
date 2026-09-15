# ADR-0006: Reinstate the four-person group

- **Status:** Accepted on 2026-09-15 by Jerad Dunne. Members confirm at the kickoff on Wed 2026-09-16.
- **Date:** 2026-09-15
- **Deciders:** Jerad Dunne (repository owner); confirmation by Leticia Aderhold, Allie Hodges, and Hina Kramer at the kickoff
- **Supersedes:** ADR-0005 (run the project as a solo project)
- **Affects research question / method / scope:** yes (review practice, validation reliability design, workload)

## Context

The repository was set up on 2026-09-13 for a four-person Group 9. On 2026-09-14 it was converted to a solo project (ADR-0005), with solo substitutes for cross-member review, two-person validation, and the contribution-balance KPI. On 2026-09-15 Jerad Dunne decided that the original teammates are part of the group again. They were invited as collaborators with write access and given write access on the project board:

| Member | GitHub |
|---|---|
| Leticia Aderhold | @angel06la |
| Allie Hodges | @AllieHgs |
| Hina Kramer | @hinak786 |

The assignment describes groups of three to five, so a four-person group also removes the rubric risk recorded in ADR-0005.

## Decision

The project is a four-person group project again. Work already merged stays: topic P-01 (ADR-0004), the analysis pipeline, the validation kit and labelling pages, the report draft, the project board, and the Actions workflows.

| Solo substitute (ADR-0005) | Reinstated group practice |
|---|---|
| Jerad Dunne holds every Scrum role | Rotating Product Owner and Scrum Master (TEAM_CHARTER.md section 3), confirmed at the kickoff |
| Self-review after a 12-hour cooling-off period; 0 required approvals | Every pull request needs one approving review from a member other than the author, within 48 hours; the `main` ruleset requires 1 approval |
| Solo working agreement signed by Jerad Dunne | Working agreement version 2.0 for four members; every member signs in their own onboarding pull request |
| Intra-rater agreement as the main reliability measure | A teammate is the second rater; inter-rater Cohen's kappa is the primary reliability measure; intra-rater re-labelling is optional |
| Solo workstream plan | Work sign-up form and assignment rules (`docs/workspace/WORK_SIGNUP.md`) |
| Work log by one person | Async stand-ups by all four members |
| Contribution-balance and first-review KPIs retired | Both restored (share 0.15 to 0.45; first review within 48 hours); PR open-to-merge cycle time kept as an extra KPI |

### Validation specifics

- Rater ids: Jerad Dunne `jd` (primary), Leticia Aderhold `la`, Allie Hodges `ah`, Hina Kramer `hk`.
- The team decides at the kickoff who second-rates which kind: signals (209 label rows), lineage (58 pairs), drift (18 pairs). A split across the three teammates is allowed.
- **Blindness rule:** primary-rater label files are not committed until the second rater's labels for the same kind are committed, and the second rater never opens the primary rater's labels.
- Second-rater round 1 target: Fri 2026-10-16. Scoring by Tue 2026-10-27. Results at the Sprint 2 review on Wed 2026-10-28.
- Decision D-017 stands: Jerad Dunne's round 1 started on 2026-09-14.

### Topic

P-01 stays selected. Any member may open a Decision needed issue to revisit it before Sprint 1 planning on Thu 2026-09-17. If nobody does, the topic is confirmed.

## Consequences

- **Positive:** real peer review; independent validation labels; workload shared across four people; the rubric's group-size and cross-member review expectations are met directly.
- **Onboarding late in formation:** teammates join one day before the kickoff and must accept invitations, set up their machines, and sign the charter quickly. Mitigation: `docs/GETTING_STARTED.md` onboarding path and the onboarding issue form.
- **Review delays:** one required approval can stall merges. Mitigation: 48-hour review SLA, reviewer rotation, and the first-review KPI.
- **Uneven contribution:** Jerad Dunne built most of the initial repository. Mitigation: pull-based work sign-up and the contribution-balance KPI from Sprint 1 onward.
- **History:** ADR-0005, the solo signature in pull request #43, and the solo documents remain in git history.

## Revisit trigger

A member leaves the group, or the instructor changes the group arrangement.

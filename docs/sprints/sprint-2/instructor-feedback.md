# Instructor feedback on Sprint 1, and what Sprint 2 does about it

How to use: this page collects everything the instructor asked of Group 9 after Sprint 1, in one place, with the issue that answers each request. Read it before picking up Sprint 2 work. The Sprint 2 review's "Instructor feedback" table links here. Recorded 2026-10-16 by Jerad Dunne.

Sources: the instructor's written comment on the Sprint 1 submission in Canvas (posted 2026-10-14), his feedback video attached to that comment, and the in-class Sprint 1 feedback session on 2026-10-14 ("Project Feedback" Parts 1 and 2 in Canvas, Modules > Recordings). Grades and recording links are not copied into this public repository.

## 1. Written comment (verbatim)

> "This is a strong, implementation-oriented Sprint 1 foundation. I was just curious about the threat models and how you came up with these detection patterns. For Sprint 2, complete the validation study, finish the retrospective and team-process evidence, and define the final human-in-the-loop risk-review workflow that will use the scanner's results."

## 2. Feedback video

The video attached to the Canvas comment (6 minutes 12 seconds) has no captions, and downloading is disabled, so it is not summarised here yet. **Jerad Dunne: watch it and add any request that is not already in sections 1, 3, or 4 to the table in section 5.** Leticia Aderhold and Hina Kramer can watch it from the Sprint 1 submission in Canvas.

## 3. What he said about Group 9 in class (2026-10-14, Part 2)

- Group 9 was the group that "came with their own rules": we defined our own detection patterns, implemented them, and he was able to run them.
- He could not tell how the rules were developed. They "seem correct," but he needs the **rationale behind each rule and a reference for it**.
- What that means, in his words, is to do what SpotBugs and SonarSource do for every rule they ship: (1) a description of the problem, (2) an example of the bad pattern, and (3) the source it comes from, such as a CWE entry, a paper, a vendor rule catalog, or an incident.

## 4. What he said to every group (2026-10-14, Parts 1 and 2)

To the five groups building security checks for agent skills, including us:

- **Name the source of each detection rule**, or reuse an established tool. He suggested SpotBugs (its bug-pattern catalog gives a rationale and an example for every pattern) and SonarQube Community Edition (free, static, with a command line and an API). Using more than one tool and comparing their results is welcome.
- **Static analysis is the right approach for skills**: a skill does not have to run to be analysed, which is what makes questions about a whole dataset possible.
- **Do an applicability analysis.** Skills mix code and natural language, so established code rules may or may not transfer. Write down which rules apply to skills and why; that list becomes the acceptance criteria.
- **Start small, then scale.** Pick about ten skills that are known to contain the issues, use them as ground truth, check that the rules detect them, then scale up.

To all nine groups:

- **Motivate the artifact.** Show how it will be used, for example with a use case diagram or another model of the intended workflow. Most groups were missing this.
- **Report numbers.** A group that looks for security issues should have counts for those issues.
- **Testing, or at least acceptance criteria, for every task**, plus a definition of done on each task.
- **Follow the sprint template** and keep sprint planning, review cycles, and pull-request reviews going.
- **Report obstacles** (resource limits, things that did not work). They are part of the documentation.
- **Contributions per member** are optional, but he liked groups that listed who did what.
- **Keep the AI-use log current**, so he can see who did what and how AI was used.

## 5. What we do about each request

Owners follow the Sprint 2 planning (Product Owner Jerad Dunne, Scrum Master Hina Kramer). "Evidence" is where the result will be when the issue closes.

| # | Request | What we do | Owner | Issue | Evidence |
|---|---|---|---|---|---|
| F1 | Complete the validation study | Second raters for drift (`la`) and lineage (`hk`, D-024); primary labels for signals, lineage, and drift; score precision, miss rate, lineage precision, drift distribution, and kappa | Jerad Dunne, Hina Kramer, Leticia Aderhold | [I6], [I7], #90 | `results/validation_*.csv`; validation table in `report/draft.md` |
| F2 | Ground truth: about ten known-positive skills | Choose about ten skills known to contain a risky capability, chosen without looking at the rule patterns; report which ones the scanner detects | Jerad Dunne (selection checked by another member) | [I4] | `results/` table and a short write-up |
| F3 | Rationale and reference for each rule | One rule card per rule: problem, bad example, source, known false positives; a `references:` field in the rule file; a paragraph on how the threat model and severities were derived | Jerad Dunne | [I1] | `docs/research/RULE_CATALOG.md`, `rules/skill_risk_rules.yaml`, `docs/research/THREAT_MODEL.md` section 8 |
| F4 | Applicability of established rules (SpotBugs, SonarSource, others) | Table of established rules and tools: applies to SKILL.md text, to bundled scripts, or neither, and why; optionally one off-the-shelf analyser on the bundled scripts, compared with our rules | Jerad Dunne | [I3] | `docs/research/APPLICABILITY.md` |
| F5 | Human-in-the-loop risk-review workflow that uses the scanner's results | Use case diagram and swimlane activity diagram (draft in this pull request), then a report section | Jerad Dunne; reviewed by Hina Kramer and Leticia Aderhold | [I5] | `docs/research/REVIEW_WORKFLOW.md`; report figure |
| F6 | Retrospective and team-process evidence | Sprint 2 planning, review, and retrospective (#92, #93, #94); check-in notes; obstacles and contributions per member in the review | Hina Kramer, Leticia Aderhold | [I9], #26 | `docs/sprints/sprint-2/`, `docs/meeting-notes/` |
| F7 | Acceptance criteria and a definition of done on every task | Acceptance criteria column kept in the Sprint 2 backlog; a "Definition of done" line added to every open Sprint 2 issue | Hina Kramer | [I9] | Issues in the Sprint 2 milestone |
| F8 | Report obstacles | "Obstacles" section in the Sprint 2 review: a member left the course, one primary rater, the 14-day gap for intra-rater signals (round 2 moves to Sprint 3, [I8]), the failed metrics workflow ([I10]) | Hina Kramer | [I9] | `docs/sprints/sprint-2/review.md` |
| F9 | AI-use log current | Every member logs Sprint 2 AI use, or states that none was used | Everyone | [I11] | `ai-use-log.md` |
| F10 | Anything new in the feedback video | Watch the video and add rows here | Jerad Dunne | this page | this page |

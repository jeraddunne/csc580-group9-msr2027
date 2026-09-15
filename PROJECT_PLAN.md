# Project Plan

**SWE 380 / CSC 580, Group 9, Fall 2026**
**Version 3.0, 2026-09-15.** Living document, revised at every sprint retrospective; changes recorded in `docs/workspace/DECISION_LOG.md` and `docs/decisions/`. Version 1.0 (four-person plan, 2026-09-13) and version 2.0 (solo plan, 2026-09-14) are in git history.

## 1. Overview

| Item | Value |
|---|---|
| Project | Mining AI-Native Software Engineering: An MSR 2027 Challenge-Inspired Project |
| Topic | P-01: Risky capabilities in copied agent skills: prevalence, reach, and drift (ADR-0004, issue #41) |
| Sponsor / customer | Prof. Mohamed Wiem Mkaouer (instructor); secondary audience: MSR community |
| Team | Leticia Aderhold, Jerad Dunne, Allie Hodges, Hina Kramer (ADR-0006) |
| Method | Scrum (3 sprints of 3 weeks, plus formation and finalization) with a Lean Six Sigma overlay (DMAIC) |
| Dataset | GitSkills sample (MSR 2027 Mining Challenge, July 2026 snapshot) |
| Repository | https://github.com/jeraddunne/csc580-group9-msr2027 |
| Board | https://github.com/users/jeraddunne/projects/1 |
| Final deliverables | Research report, reproducible repository release, working prototype, final demonstration, one individual reflection per member |

### Objectives

1. Onboard all four members, sign the charter, confirm roles and the P-01 topic, and submit the topic brief by 2026-09-16.
2. Deliver a working, tested, reproducible pipeline that answers RQ1 to RQ3 with independently validated evidence by 2026-11-18.
3. Communicate method, evidence, results, limitations, and implications in a report and demonstration by 2026-12-04.
4. Make the process measurable and improving: every sprint's KPIs are reviewed, and at least one process improvement per sprint is implemented and verified.

## 2. Scope

**In scope:** the P-01 research question (RQ1 prevalence, RQ2 reach, RQ3 variant drift) on the GitSkills sample; a static rule-based scanner of SKILL.md text and bundled script text; near-duplicate variant linking; statistics and sensitivity checks; validation with a primary rater and a teammate second rater, reported as inter-rater agreement; a data dictionary; threats to validity; the report; the presentation; full Scrum and Lean Six Sigma records in GitHub.

**Out of scope:** submitting to MSR 2027; executing, importing, or fetching anything found in the dataset; naming repositories or accounts in outputs; the full 41 GB GitSkills dataset, unless an ADR in Sprint 1 approves one streamed pass over the `artifacts` table for RQ3; SpecMine analysis.

**Scope control:** any change to the research question, population, method, or deliverables needs a `decision` issue, team agreement at a ceremony, and an ADR, and is recorded in the sprint retrospective.

## 3. Deliverables and assessment mapping

| Rubric component | Weight | Due | Deliverable | Evidence location |
|---|---|---|---|---|
| Topic selection, research question, initial backlog | 10% | Sep 16 | Topic brief, `RESEARCH_QUESTION.md`, ADR-0004, ADR-0006, Sprint 1 backlog | `docs/sprints/00-formation/review.md`, issue #41, milestone "Sprint 1" |
| Sprint 1: research framing and data foundation | 20% | Oct 7 | Sprint 1 research-and-data package | `docs/sprints/sprint-1/review.md` |
| Sprint 2: implementation and validation | 20% | Oct 28 | Sprint 2 implementation-and-evidence package | `docs/sprints/sprint-2/review.md` |
| Sprint 3: analysis, integration, final report | 25% | Nov 18 | Complete draft, tagged release, demo plan | `docs/sprints/sprint-3/review.md`, release tag |
| Final demonstration and presentation | 20% | Nov 30 to Dec 4 | Presentation, live demo, final report, release v1.0.0 | `docs/PRESENTATION_PLAN.md`, GitHub release |
| Individual contribution and reflection | 5% | Dec 4 | One reflection per member | `docs/reflections/<handle>.md` |

## 4. Work breakdown structure

Each numbered item maps to a `rubric` issue created on 2026-09-13; bullets become sub-issues at sprint planning.

### 0. Formation (Sep 10 to Sep 16), Define

- 0.1 Repository, labels, milestones, protection, CI, project board (done 2026-09-13 to 2026-09-15)
- 0.2 Members accept invitations, complete onboarding issues, add profiles, and sign the charter in their own pull requests
- 0.3 Dataset inspection: GitSkills sample downloaded and profiled (done 2026-09-14, findings F-006 to F-012); each member runs `make data`
- 0.4 Topic decision (ADR-0004) confirmed by the group, or revisited by a Decision needed issue before 2026-09-17
- 0.5 Roles confirmed; second rater or raters chosen for each validation kind
- 0.6 `RESEARCH_QUESTION.md` reviewed; topic brief submitted; Sprint 1 backlog estimated; Sprint 1 work sign-ups filed

### 1. Sprint 1 (Sep 17 to Oct 7), Measure

- 1.1 Precise research question, motivation, contribution, competing explanation (#12)
- 1.2 Unit of analysis, population, sample, variables, outcome measures; `DATA_DICTIONARY.md` Part B (#13)
- 1.3 Acquisition instructions, inclusion rules, MANIFEST snapshot statement, verified by a second member (#14)
- 1.4 `python -m msr_pipeline analyze` and `make pipeline` running on the sample (#15)
- 1.5 At least one exploratory table or visualization generated by code (#16)
- 1.6 Repository practice: issues, milestones, branch protection, every member authors and reviews a merged pull request (#17)
- 1.7 Threat model; `THREATS_TO_VALIDITY.md` first pass; FMEA review; ADR on sample only versus a full-dataset pass (#18)
- 1.8 Baseline process metrics captured, including contribution balance (#19)
- 1.9 Sprint 1 review package and retrospective (#20)

### 2. Sprint 2 (Oct 8 to Oct 28), Analyze

- 2.1 Core implementation: scanner, variant linking, RQ2 statistics (#21)
- 2.2 Automated tests for parsing, matching, and metric functions (#22)
- 2.3 Validation: primary rater and second rater label round 1 independently from the guideline; blindness rule; `score` produces precision, recall, and inter-rater kappa (#23)
- 2.4 Preliminary results with reproducible tables and figures (#24)
- 2.5 Cross-member pull request reviews on every major change
- 2.6 Report update: background, method, implementation, preliminary results (#25)
- 2.7 Root-cause analysis on the largest Sprint 1 process problem; kaizen verified
- 2.8 Sprint 2 review package and retrospective recording changes to question, method, scope, or interpretation (#26)

### 3. Sprint 3 (Oct 29 to Nov 18), Improve

- 3.1 Final RQ1 to RQ3 results (#27)
- 3.2 Sensitivity checks: similarity threshold, severity cutoff, front-matter-valid subset, excluding the most copied contents (#28)
- 3.3 Error analysis of disagreements and inspected examples (#29)
- 3.4 Final figures and tables from the pipeline (#30)
- 3.5 Complete draft report with a safe-reporting section; observation and interpretation separated (#31)
- 3.6 Threats to validity, including rater agreement and sample limits (#32)
- 3.7 Documented release `v0.9.0-rc1` (#33)
- 3.8 Demonstration plan and presentation materials with a speaker for each segment (#34)
- 3.9 Retrospective naming the most important process improvement (#35)

### 4. Finalization (Nov 30 to Dec 4), Control

- 4.1 Respond to instructor feedback; final report; release v1.0.0 (#36, #37)
- 4.2 Fresh-machine reproduction by a member who did not write the README
- 4.3 Presentation and live demo; rehearsals (#38)
- 4.4 Individual reflections from all four members; AI-use log completeness check (#39, #40)
- 4.5 Control plan sign-off: every rubric checklist item verified with links

## 5. Schedule

| Period | Dates (Thu to Wed) | DMAIC | Planning | Check-ins | Review + Retro | Rubric due |
|---|---|---|---|---|---|---|
| Formation | Sep 10 to Sep 16 | Define | Sep 14 (topic), Sep 15 (group reinstated) | | Wed Sep 16 group kickoff | Sep 16 |
| Sprint 1 | Sep 17 to Oct 7 | Measure | Thu Sep 17 | Thu Sep 24, Thu Oct 1 | Wed Oct 7 | Oct 7 |
| Sprint 2 | Oct 8 to Oct 28 | Analyze | Thu Oct 8 | Thu Oct 15, Thu Oct 22 | Wed Oct 28 | Oct 28 |
| Sprint 3 | Oct 29 to Nov 18 | Improve | Thu Oct 29 | Thu Nov 5, Thu Nov 12 | Wed Nov 18 | Nov 18 |
| Break | Nov 19 to Nov 29 | | | (Thanksgiving Nov 26) | | |
| Finalization | Nov 30 to Dec 4 | Control | Mon Nov 30 | Wed Dec 2 | Fri Dec 4 | Dec 4 |

Written stand-ups every Monday, Wednesday, and Friday. Weekly metrics snapshot every Sunday (automated). If the instructor changes dates, update `project.yml` and re-run `scripts/bootstrap_github.py` to move milestone due dates.

## 6. Roles and responsibilities

Rotation (proposed, confirmed at the 2026-09-16 kickoff) is in `TEAM_CHARTER.md` section 3 and `project.yml`. Activity-level responsibilities are in `docs/team/RACI.md`. Standing rules: every member contributes technical and research work every sprint, every member reviews at least one pull request per week, and no member reviews their own pull request.

## 7. Process

Scrum ceremonies and the Lean Six Sigma overlay are defined in `docs/PROCESS.md` and `docs/lean-six-sigma/README.md`.

| DMAIC phase | Sprint | Tollgate question | Primary tools |
|---|---|---|---|
| Define | Formation | Is the problem, customer, and scope clear, and is the team set up? | Charter, SIPOC, CTQ tree, FMEA |
| Measure | Sprint 1 | Can the outcome and the process be measured reliably? | Data dictionary, MANIFEST, baseline KPIs, validation design |
| Analyze | Sprint 2 | What drives the result, and what drives delays? | Tests, inter-rater agreement, 5 Whys, control charts |
| Improve | Sprint 3 | Is the result robust, and has the process improved? | Sensitivity checks, error analysis, kaizen verification |
| Control | Finalization | Will it stay reproducible after the semester? | Control plan, release, README gemba walk |

## 8. Quality plan

| Quality attribute | Practice | Check |
|---|---|---|
| Correctness | Unit tests for every parsing, matching, and metric function; CI on every pull request | CI green and one approving review required to merge |
| Reproducibility | `make pipeline` from a clean environment; pinned dependencies; MANIFEST hashes | Gemba walk by a non-author at each review |
| Validity | Written annotation guideline; stratified validation sample; precision per rule; inter-rater Cohen's kappa with a teammate; blindness rule | Sprint 2 and Sprint 3 review checklists |
| Review | Approving review from a member other than the author within 48 hours; reviewer checklist | PR template; first-review KPI |
| Research reasoning | Variables and assumptions explicit; observation separated from interpretation; competing explanations | Reviewer checklist item |
| Documentation | README, data dictionary, threats file updated in the same pull request as the change | Definition of Done |
| Responsible AI | `ai-use-log.md` entries verified by a human before merge | PR template checkbox |
| Process quality | KPIs against targets in `project.yml`; run rules on control charts; contribution balance | Thursday check-in |

## 9. Risk management

The FMEA register in `docs/lean-six-sigma/FMEA_RISK_REGISTER.md` is reviewed at every planning and check-in. Top risks:

1. **Late onboarding in formation.** Three members join one day before the kickoff. Mitigation: onboarding path in `docs/GETTING_STARTED.md`, onboarding issue form, pairing during Sprint 1 setup.
2. **Uneven contribution.** Most of the initial repository was built by one member. Mitigation: pull-based work sign-up, contribution-balance KPI from Sprint 1, escalation path in the charter.
3. **Review delays with one required approval.** Mitigation: 48-hour review SLA, reviewer rotation, first-review KPI.
4. **Low precision of keyword signals.** Mitigation: validation before any claim; only validated precision is reported.
5. **Rater disagreement.** Mitigation: written guideline, practice items, blindness rule, adjudication in error analysis, kappa reported.
6. **Pipeline not reproducible elsewhere.** Mitigation: CI, gemba walk by a non-author at every review.
7. **RQ3 underpowered in the sample.** Mitigation: scoped to case studies; ADR in Sprint 1 on a full-dataset pass.

## 10. Communication plan

| Audience | What | Channel | Frequency | Owner |
|---|---|---|---|---|
| Team | Stand-ups | `docs/meeting-notes/` | Mon, Wed, Fri | each member |
| Team | Board, pull requests, issues, reviews | GitHub | continuous | all |
| Team | Planning, check-ins, review, retro | video call plus notes | weekly and per sprint | Scrum Master |
| Team | Quick coordination | team channel (chosen at kickoff) | as needed | all |
| Instructor | Topic brief | course submission | Sep 16 | Product Owner |
| Instructor | Sprint packages | repository link and course submission | Oct 7, Oct 28, Nov 18 | Product Owner |
| Instructor | Questions, date changes, suspected malicious dataset content | course channel | as needed | Scrum Master |

## 11. Change management

- **Backlog changes:** any member may add issues; the Product Owner orders them; the sprint commitment changes only at a check-in, with a note in the sprint planning file.
- **Research changes:** a `decision` issue, discussion, an ADR, and a line in the retrospective.
- **Process changes:** a `kaizen` issue with a measurable expected effect, verified at the next retrospective.
- **Charter changes:** a pull request approved by all other members and a row in the decision log.

## 12. Tooling

Python 3.11+, pandas, pyarrow, matplotlib, scipy, statsmodels, pytest, and ruff. GitHub Issues, Projects, and Actions; the GitHub CLI for scripts; pandoc for the report PDF. All tools are free and reproducible on Windows, macOS, and Linux.

## 13. Success metrics

- **Product:** all rubric acceptance criteria met with evidence; reproduction from a fresh clone by a non-author succeeds; precision per rule and inter-rater agreement reported.
- **Process (targets from `project.yml`):** commitment reliability at or above 0.8; median first review within 48 hours; first-time-right rate at or above 0.75; rework ratio at or below 0.15; every member's contribution share between 0.15 and 0.45; CI pass rate at or above 0.9; at least one verified kaizen per sprint.
- **Individual:** each member holds a Scrum role at least once, can explain every pipeline stage, and files a reflection with links to their contributions.

## 14. Topic decision

P-01 was selected on 2026-09-14 (ADR-0004). The ranked-ballot vote planned in ADR-0002 was not held. With the group reinstated (ADR-0006), any member may open a Decision needed issue to revisit the topic before Sprint 1 planning on 2026-09-17; otherwise P-01 is confirmed at the kickoff. Fallback: rubric question 2 (skill quality indicators), reusing the scanner output as features. Revisit trigger: the Sprint 1 criterion "the question is answerable with the selected data" is not met by Thu 2026-10-01.

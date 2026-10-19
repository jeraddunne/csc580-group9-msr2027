# Human-in-the-loop risk review: how the scanner is meant to be used

How to use: this page describes the intended use of the P-01 scanner: a person reviews a skill's high-risk findings before the skill is enabled. The instructor asked for it in the Sprint 1 feedback ("define the final human-in-the-loop risk-review workflow that will use the scanner's results"; see `docs/sprints/sprint-2/instructor-feedback.md`, F5). **Status: draft for team review (2026-10-16).** It is a design. The pipeline today scans the GitSkills sample in batch, and no single-skill review tool is built. Regenerate the diagrams with `python scripts/make_workflow_diagrams.py`.

## 1. Why a person stays in the loop

- A skill is "copied like code and read like instructions" (`THREAT_MODEL.md` section 1). Users usually do not read every skill before an agent uses it (section 2), and the agent acts on the skill with the user's permissions (boundary 3).
- A rule match is a signal, not a verdict: it does not mean the skill is malicious or that the agent will act on it (`THREAT_MODEL.md` section 6). Many matches are benign in context.
- So the scanner should not block or allow skills on its own. It narrows a skill down to the few lines worth a person's attention, and a person makes the decision.

## 2. Actors

| Actor | Role in the workflow |
|---|---|
| Developer | Proposes adding a skill to a repository or enabling it for an agent: a new skill, or a copy of one from elsewhere |
| CI pipeline («system») | Runs the scanner when a pull request adds or changes a skill |
| Security reviewer | Triages each high-risk finding and approves, blocks, or asks for a change |
| Skill author | Revises the skill when a change is requested |
| Rule maintainer | Turns false positives into rule-change proposals |

In a small team one person can hold several roles, but the reviewer should not be the developer who proposed the skill, the same separation the repository uses for pull-request review.

## 3. Use case diagram

![Use case diagram of the human-in-the-loop skill risk review](figures/review_workflow_use_case.svg)

| Use case | Actor | Notes |
|---|---|---|
| Propose or enable a skill | Developer | Always includes a scan («include») |
| Scan the skill | CI pipeline | Static only: SKILL.md and bundled scripts are read as text and matched against `rules/skill_risk_rules.yaml`. Nothing is executed, imported, or fetched |
| Read the scan report | Developer | Rule, category, severity, and the matched line for each finding |
| Triage each finding | Security reviewer | One label per finding, using the decision order in `docs/validation/ANNOTATION_GUIDELINE.md` |
| Approve, block, or request a change | Security reviewer | The reason is recorded with the labels |
| Revise the skill | Skill author | Extends the decision when a change is requested; the revised skill is scanned again |
| Propose a rule change | Rule maintainer | Extends triage when a finding is a false positive; follows the rule-change process in `docs/validation/README.md` |

## 4. Activity diagram

![Swimlane activity diagram of the human-in-the-loop skill risk review](figures/review_workflow_activity.svg)

1. The developer proposes a skill: a new one, or a changed copy of an existing one. A copy is scanned on its own; it does not inherit an earlier approval of a different copy. RQ3 shows why: copies of the same skill can differ in their high-risk categories (`results/rq3_summary.csv`).
2. The scanner reads SKILL.md and the bundled scripts and reports every rule match with its rule, category, and severity.
3. If no match has severity 6 or more (the threat model's "high risk"), the scan report is recorded and the skill can be enabled. This path is where the scanner's misses go.
4. Otherwise the reviewer labels each high-risk finding RISKY, BENIGN_CONTEXT, or NOT_PRESENT.
5. Any RISKY finding blocks the skill or sends it back to its author. The revised skill is scanned again.
6. With no RISKY finding, the reviewer approves and records the labels and the reason. In parallel, any false positive (NOT_PRESENT, or BENIGN_CONTEXT that the rule could have told apart) goes to the rule maintainer, who logs it with `python scripts/annotation_kit.py proposals` (`docs/validation/RULE_CHANGE_PROPOSALS.md`) and changes the rule by pull request with regression examples.

## 5. How the validation study measures this workflow

The triage labels are the validation labels, so the Sprint 2 validation numbers describe how this workflow would behave on the GitSkills sample.

| Validation result | What it says about the workflow |
|---|---|
| Strict precision per rule and category (`results/validation_precision_by_rule.csv`, `..._by_category.csv`) | The share of findings a reviewer would label RISKY. One minus it is the share of the reviewer's time spent clearing false alarms |
| Miss rate (`results/validation_recall.csv`) | How often a risky skill takes the no-signal path in step 3 and is enabled without review |
| Inter-rater kappa (`results/validation_agreement.csv`) | Whether two reviewers given the same guideline reach the same decision, that is, whether triage depends on who does it |
| Lineage precision and drift types (`results/validation_lineage.csv`, `results/validation_drift.csv`) | Whether "copies of the same skill" are really related, and what kind of change made a copy's risk differ: the case for rescanning every copy in step 1 |
| Severity sensitivity at cutoffs 5 and 7 (`results/sensitivity_summary.csv`) | How the reviewer's load changes if the step 3 threshold moves |

None of these numbers exists yet; they come from `python scripts/annotation_kit.py score` after the round 1 labels are committed (`docs/validation/README.md`).

## 6. Not built, and open questions

- **Not built:** a command that scans one skill folder and prints a report; storage for reviewer decisions; any enforcement in an agent runtime. The batch pipeline (`python -m msr_pipeline analyze`) is what exists.
- **Threshold.** Step 3 uses severity 6. Is the reviewer's load at 6 acceptable, or should the threshold move, given the sensitivity results?
- **Context rules.** Rules below severity 6 (for example R-SHL-001, a shell code block) never reach the reviewer. Should the report still show them as context?
- **Who reviews in a three-person team?** The proposal above mirrors pull-request review: never the person who proposed the skill.

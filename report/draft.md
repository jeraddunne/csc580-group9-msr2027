---
title: "Risky Capabilities in Copied Agent Skills: Prevalence, Reach, and Drift in GitSkills"
subtitle: "SWE 380 / CSC 580 Group Project, Group 9, University of Michigan-Flint"
author:
  - Leticia Aderhold
  - Jerad Dunne
  - Hina Kramer
date: "Draft, updated 2026-11-12"
bibliography: references.bib
link-citations: true
---

<!--
Status on 2026-11-09: round 1 validation is reported in Evaluation and validation
(Table 2). The Abstract, Discussion, and Conclusion distinguish scanner signals
from confirmed risky capabilities. Hina Kramer approved the round 1 report
revisions in PR #144. Signal intra-rater checking was completed on 2026-11-11 under issue #101.
-->

# Abstract

Agent skills contain natural-language instructions and bundled scripts that AI coding agents may follow with user permissions. This study applies a static, rule-based scanner to the GitSkills July 2026 sample of 12,965 distinct skill contents. High-risk rules match 8.9% of distinct contents and 11.2% of copy-weighted occurrences; these are signal frequencies, not confirmed-risk prevalence. Round 1 manual validation yields category-level strict precision from 0.20 to 1.00, with unscoped shell tool grants and `sudo` reaching the hypothesized 0.80 threshold as point estimates. Contents with high-risk signals average 2.87 copies against 2.23 for other contents, with a small rank-biserial effect size of 0.042. The association persists in a model with controls and across sensitivity scenarios, but does not establish causation or actual agent use. Among 18 variant pairs with differing high-risk categories, the primary rater identifies template updates, local adaptations, and hardening, with no capability additions. Sparse dates limit conclusions about the direction of drift. The findings support contextual human review of scanner findings. Signal repeat-labeling agreed on 61 of 69 rule matches (Cohen's kappa 0.839); evaluation of the proposed review workflow remains pending.

# Introduction

Agent skills were introduced as an open format in October 2025. By July 2026, public GitHub repositories held millions of SKILL.md files [@gitskills2027]. A skill is unusual as a software artifact. It is written mostly in natural language, a model decides at run time whether to load it, and nothing compiles or type-checks it. Skills also have no central registry. Developers reuse them by copying folders, and about half of all skill file occurrences in GitSkills are verbatim copies of another file [@gitskills2027].

Two lines of prior work make this reuse pattern a security question. Research on open-source supply chains shows that redistributed code is a practical attack path [@ohm2020]. Research on indirect prompt injection shows that text reaching a language model can direct it to act with the user's authority [@greshake2023]. A skill sits between these: it is copied like code and read like instructions. If a skill tells an agent to download and run a script, read credential files, or skip asking the user, every repository that copies it inherits that behaviour.

This study makes three contributions:

1. A reviewable rule set for risk-relevant capabilities in skills, with regression examples for every rule and a validation protocol that measures precision.
2. A prevalence and reach profile of those capabilities in the GitSkills sample, weighted both by distinct content and by copies.
3. A description of how near-duplicate variants of the same skill differ in those capabilities, scoped to what the sample can support.

The simpler explanation tested throughout is that keyword matches reflect documentation and template inheritance rather than capabilities that differ between skills.

# Research question and hypotheses or expectations

**Main question.** In the GitSkills July 2026 sample, how prevalent are skill instructions and bundled scripts that enable risk-relevant capabilities, do skills carrying them reach more repositories through verbatim copying, and do modified variants of the same skill add or remove those capabilities?

The main question has three sub-questions, each with one measure:

- **RQ1 Prevalence.** The share of distinct contents, and the share of copy-weighted occurrences, with each capability category.
- **RQ2 Reach.** Copies and distinct repositories per content, for contents with and without a high-risk capability.
- **RQ3 Drift.** Among near-duplicate variants sharing a front-matter name, how often high-risk capabilities differ, and in which direction when both commit dates exist.

**Operationalization.** The unit of analysis is one distinct skill content, identified by `artifacts.file_sha`, together with its copies. A capability category is present when at least one active rule in that category matches the content. It is *high risk* when a matching rule has severity 6 or more on a 1 to 10 scale. Full variable definitions are in `DATA_DICTIONARY.md` Part B.

**Expectations.**

- H1: at least one high-risk capability category reaches a validated strict precision of 0.8 or more.
- H2: the copy distribution of contents with a high-risk capability differs from that of contents without one. The null hypothesis is no difference.
- RQ3 is descriptive. The sample holds too few dated variant pairs for a directional test.

**Competing explanations.** Keyword matches may describe unsafe patterns rather than instruct them. Differences between variants may come from template updates rather than local changes. Widely copied setup and DevOps skills may use shell commands for ordinary reasons, which would link risk signals and reach without any causal story.

# Dataset and data preparation

**Dataset snapshot statement.** This study uses the GitSkills sample dataset, July 2026 snapshot, published for the MSR 2027 Mining Challenge. It was downloaded on 2026-09-14 from the dataset authors' GitHub sample repository at upstream commit `fff3df9`. The SQLite file `agent_skills_sample.db` has SHA-256 `683888c9...`, recorded in `data/samples/MANIFEST.json`.

**Scope.** The sample was drawn deterministically by the dataset authors: the 13,000 distinct contents with the lowest content hashes, together with every copy of each [@gitskills2027]. The analysis uses four tables. `artifacts` supplies content, front matter, copies, location, and commit history. `artifact_siblings` supplies bundled file text. `repos` supplies repository stars and language, and `mining_runs` supplies provenance only.

**Filtering.** The main population is distinct contents with fetched text, excluding symlink stubs, whose content is a single short path rather than instructions. A sensitivity subset keeps only contents with valid YAML front matter.

Table 1. Population flow. <!-- results/population_flow.csv -->

| Step | Distinct contents | Occurrences |
|---|---|---|
| All sample occurrences, all with fetched text | 13,000 | 29,786 |
| Excluded: symlink stubs | 35 | 107 |
| Main population | 12,965 | 29,679 |
| Sensitivity subset: valid front matter | 11,291 | 27,101 |

**Known limits.** GitHub code search indexes only default branches, files under 384 KB, and forks more starred than their parent, so the population is a lower bound [@gitskills2027]. Commit history exists for 3,010 of 29,786 sample occurrences and follows the file's current path. Sampling by content hash keeps every exact-copy group complete but splits families of modified variants.

**Ethics.** Author accounts in the dataset are replaced by one-way codes, and this study makes no attempt to reverse them. Dataset content is treated strictly as text: no script, command, or URL found in the data is executed or fetched. Committed outputs identify skills only by content hash and front-matter name, never by repository or account.

# Method and implementation

The pipeline runs with `python -m msr_pipeline analyze` (or `make pipeline`). It reads the SQLite sample read-only and writes CSV tables to `results/` and figures to `figures/`. The run of 2026-09-14 took 286 seconds on a laptop. <!-- results/ANALYSIS_MANIFEST.json -->

**Threat model.** The actors are the skill author, anyone who copies and edits the skill, the agent runtime that loads it, and the user whose permissions the agent holds. The assets are the user's files, credentials, repositories, and machine. Each rule category names a capability a skill can direct the agent to exercise with those permissions. The full model, including trust boundaries and the rationale for severity scores, is in `docs/research/THREAT_MODEL.md`.

**Detection rules.** `rules/skill_risk_rules.yaml` defines 19 rules in 12 categories. Twelve rules have severity 6 or more and count as high risk. The other seven are context rules that record ordinary capabilities: shell code blocks, network tooling, `allowed-tools` declarations, secret-named environment variables, dotenv reads, world-writable permissions, and executable bits. Each rule has an id, category, severity, patterns, status, source, and match and no-match examples enforced by the test suite. Rules apply to SKILL.md text and to bundled script files read as text.

**Variant linking (RQ3).** Two distinct contents are treated as variants of one skill when they share a normalised front-matter name and their word 5-shingle Jaccard similarity reaches a threshold. The main threshold is 0.5, with a sweep from 0.3 to 0.8. When both variants have a first-commit date, the older is compared against the newer. Sixteen names of Anthropic's published example skills are flagged as template families so that results can be reported without them. Some of those names are generic, such as `pdf` and `docx`, so the flag may also catch unrelated skills.

**Statistics (RQ1 and RQ2).** Prevalence shares carry Wilson 95% confidence intervals. Copy counts are compared between contents with and without a high-risk signal using a two-sided Mann-Whitney U test with a rank-biserial effect size. The analysis also reports bootstrap 95% confidence intervals (2,000 resamples, seed 580) for the difference in mean copies and in the share copied at least twice. A negative binomial (NB2) regression models copies minus one on high-risk presence. Its controls are log body length, bundled scripts, location class, log repository stars, and repository language; the baselines are the skills-directory location and Python. Controls come from the representative row and its repository, and missing stars count as zero. Categories with at least 30 contents are each tested against contents with no high-risk signal, with Holm-adjusted p-values.

**Robustness.** Headline metrics are recomputed under severity cutoffs of 5 and 7, for the front-matter-valid subset, without the ten most-copied contents, and without template families.

**Reproducibility.** The run records the dataset hash, the rule-file hash, package versions, and runtime in `results/ANALYSIS_MANIFEST.json`.

**Intended use.** The scanner is meant to support a person's decision, not to make it. `docs/research/REVIEW_WORKFLOW.md` describes the proposed workflow, shown in Figure 2. When a pull request adds or changes a skill, CI scans it. A reviewer who did not propose the skill labels each high-risk finding with the labels used in the validation study, then approves the skill, blocks it, or asks for a change; a revised skill is scanned again. An incomplete scan is read by hand rather than treated as clean, and a skill with no high-risk signal still needs the reviewer's approval, because no signal does not mean safe. Every set of labels goes to a rule maintainer, who turns false positives into rule-change proposals. Each validation result measures one step of this workflow: strict precision is the share of findings a reviewer would label risky, the miss rate is how often a risky skill takes the no-signal path, and inter-rater agreement shows whether two reviewers reach the same label. The batch analysis pipeline, skill-scan command line, GitHub Action, and VS Code tooling are implemented, as documented in `docs/TOOL.md`. The complete proposed human-review workflow has not been evaluated as a deployed review process.

![Figure 1. Proposed human-in-the-loop review of a skill, as a UML activity diagram with one swimlane per role. Drawn by `scripts/make_workflow_diagrams.py`.](../docs/research/figures/review_workflow_activity.svg)

# Evaluation and validation

**Automated tests.** The test suite covers every rule's documented examples, the scanner, variant linking and ordering, missing-value handling, the statistics helpers, and the validation scoring. It runs offline against small fixtures.

**Manual validation design.** Rule precision is measured on a stratified sample of 147 distinct contents: up to 10 per high-risk category plus 40 with no signal, drawn with seed 580. They yield 209 label rows, one per matched rule plus one per no-signal item. For each match, a rater assigns one of three labels. *Risky* means the capability is present and would act with user permissions in context. *Benign in context* means the capability is present but described, warned against, or clearly sandboxed. *Not present* means the rule matched text that does not grant the capability. Strict precision counts only *risky*; capability precision counts *risky* and *benign in context*. Both carry Wilson intervals. The no-signal items estimate how often a high-risk capability is missed.

A lineage sample of 58 variant pairs checks whether pairs really share a lineage: the 18 pairs whose high-risk categories differ, plus 40 random pairs. The 18 differing pairs are also classified as template update, local adaptation, hardening, capability addition, or unrelated. <!-- data/annotations/samples/SAMPLE_MANIFEST.json -->

**Reliability.** Jerad Dunne is the primary rater. Leticia Aderhold independently second-rates drift, and Hina Kramer independently second-rates lineage. Inter-rater agreement is measured using Cohen's kappa [@cohen1960]. Signals are labeled by Jerad alone, so their reliability is checked within one rater: he re-labeled a 30% subset (45 contents, 69 rule matches) at least 14 days after round 1, without viewing his round 1 labels. Optional repeat labeling uses a minimum interval of 14 days for lineage and seven days for drift. The blindness rule keeps primary and second-rater labels separate until their independent round 1 work is complete. Any additional LLM ratings are disclosed and reported separately from human agreement. The current protocol is documented in `docs/validation/README.md`.

**FMEA ranking.** Categories are ranked by severity (from the rule file), occurrence (validated prevalence: the share of contents that match a high-risk rule in the category, times capability precision), and detection (estimated miss rate), in the style of a failure mode and effects analysis. The ranking prioritises categories for review and is not a risk verdict.

**Validation results (round 1).** Table 2 gives precision for each high-risk capability from the primary rater's labels of the 169 rule matches in the signal sample. Strict precision ranges from 0.20 for dynamic code execution to 1.00 for unscoped shell tool grants; only those grants and `sudo` (0.80) reach 0.80. Capability precision, which also counts matches where the capability is present but benign in context, is 0.53 or higher in every category and 1.00 for hard-coded IP endpoints, download and execute, and tool grants. <!-- results/validation_precision_by_category.csv --> None of the 40 no-signal items was labelled as missing a high-risk capability: a miss rate of 0 (95% CI 0 to 0.088), which at the upper bound would be about 661 of the 7,540 no-signal contents. <!-- results/validation_recall.csv --> For drift, the primary and second rater agreed on 15 of 18 pairs (83.3%, Cohen's kappa 0.745). The primary rater classified 8 pairs as template updates, 8 as local adaptations, and 2 as hardening, and none as a capability addition. <!-- results/validation_agreement.csv, results/validation_drift.csv --> For lineage, the primary rater judged all 58 pairs to share a lineage (precision 1.00, 95% CI 0.94 to 1.00), and the two raters agreed on 57 of 58 pairs (98.3%). Cohen's kappa is 0 because the primary rater gave every pair the same label, so percent agreement is the lineage agreement figure. <!-- results/validation_lineage.csv, results/validation_agreement.csv --> Signals have one rater; in the intra-rater check, his round 2 labels agreed with round 1 on 61 of 69 rule matches, with Cohen's kappa 0.839. <!-- results/validation_agreement.csv --> In the FMEA ranking, download and execute ranks highest (RPN 54), followed by oversight bypass wording and unscoped shell tool grants (48 each). Occurrence counts only contents that match a high-risk rule in the category, because precision was measured on those matches; counting context-rule matches as well would put credential file paths and hard-coded IP endpoints at the top. With no misses in the sample, the detection score is 1 for every category, so the ranking reflects severity and occurrence only. <!-- results/fmea_category_ranking.csv -->

Table 2. Validation of high-risk signals, round 1 (primary rater). <!-- results/validation_precision_by_category.csv -->

| High-risk capability | Label rows | Risky / benign in context / not present | Strict precision (95% CI) | Capability precision (95% CI) |
|---|---|---|---|---|
| Unscoped shell tool grant | 18 | 18 / 0 / 0 | 1.00 (0.82 to 1.00) | 1.00 (0.82 to 1.00) |
| `sudo` | 25 | 20 / 4 / 1 | 0.80 (0.61 to 0.91) | 0.96 (0.80 to 0.99) |
| Download and execute | 15 | 10 / 5 / 0 | 0.67 (0.42 to 0.85) | 1.00 (0.80 to 1.00) |
| Persistence locations | 16 | 9 / 5 / 2 | 0.56 (0.33 to 0.77) | 0.88 (0.64 to 0.97) |
| Recursive forced delete or history rewrite | 21 | 10 / 10 / 1 | 0.48 (0.28 to 0.68) | 0.95 (0.77 to 0.99) |
| Oversight bypass wording | 13 | 6 / 4 / 3 | 0.46 (0.23 to 0.71) | 0.77 (0.50 to 0.92) |
| Request-capture or paste endpoint | 8 | 3 / 2 / 3 | 0.38 (0.14 to 0.69) | 0.63 (0.31 to 0.86) |
| Obfuscated payload decoding | 12 | 4 / 7 / 1 | 0.33 (0.14 to 0.61) | 0.92 (0.65 to 0.99) |
| Hard-coded IP endpoint | 11 | 3 / 8 / 0 | 0.27 (0.10 to 0.57) | 1.00 (0.74 to 1.00) |
| Credential file paths | 15 | 4 / 6 / 5 | 0.27 (0.11 to 0.52) | 0.67 (0.42 to 0.85) |
| Dynamic code execution | 15 | 3 / 5 / 7 | 0.20 (0.07 to 0.45) | 0.53 (0.30 to 0.75) |

**Known-positive check.** The October 27 ground-truth check on commit `8e2ce36` matched the expected category for all 10 selected known-positive skills, but only 5 matched an expected-category rule at severity 6 or above. The remaining 5 matched only context rules within their expected categories; their outcomes are pending under issue #132. One of the five is a rule miss: `R-TGR-001` reads only the line that holds the `allowed-tools` key, so it misses unscoped `Bash` written as a list item. A proposed rule for the list form (`R-TGR-003`, not active, D-027) matches 169 contents in the main population, 154 of them not already high risk. Activating it would move the high-risk share from 8.9% to 10.1%. None of those matches has been labelled, so the results below keep the rules frozen for round 1 (`results/proposed_rule_impact.csv`). See the [ground-truth results](../results/ground_truth_check.csv) and [selection and summary](../docs/validation/KNOWN_POSITIVES_SELECTION.md).

# Results

All results in this section are unvalidated keyword signals. They describe where the rules match, not confirmed capabilities.

**RQ1 Prevalence.** Of the 12,965 distinct contents in the main population, 1,159 match at least one high-risk rule: 8.9%, 95% CI 8.5% to 9.4%. Weighted by copies, 3,326 of 29,679 occurrences carry one, or 11.2%. Table 3 lists each high-risk capability. For persistence locations, `sudo`, and destructive commands, the copy-weighted share is about double the content share. Context rules match far more often: shell code blocks in 4,351 contents (33.6%), `allowed-tools` declarations in 1,282 (9.9%), secret-named environment variables in 938 (7.2%), and network tooling in 851 (6.6%). <!-- results/rq1_prevalence_by_rule.csv, results/rq1_prevalence_by_category.csv, figures/rq1_prevalence_by_category.png -->

Table 3. High-risk signals in the main population. <!-- results/rq1_prevalence_by_rule.csv; download-and-execute from results/rq1_prevalence_by_category.csv -->

| High-risk capability | Rule(s) | Distinct contents | Share (95% CI) | Occurrences | Copy-weighted share |
|---|---|---|---|---|---|
| Unscoped shell tool grant | R-TGR-001 | 511 | 3.9% (3.6 to 4.3) | 1,121 | 3.8% |
| Recursive forced delete or history rewrite | R-DST-001 | 173 | 1.3% (1.2 to 1.6) | 726 | 2.4% |
| `sudo` | R-PRV-001 | 140 | 1.1% (0.9 to 1.3) | 817 | 2.8% |
| Oversight bypass wording | R-OVR-001 | 109 | 0.8% (0.7 to 1.0) | 219 | 0.7% |
| Dynamic code execution | R-EXE-001 | 100 | 0.8% (0.6 to 0.9) | 347 | 1.2% |
| Persistence locations | R-PER-001 | 91 | 0.7% (0.6 to 0.9) | 512 | 1.7% |
| Download and execute | R-RCE-001, R-RCE-002 | 73 | 0.6% (0.5 to 0.7) | 170 | 0.6% |
| Credential file paths | R-CRD-001 | 65 | 0.5% (0.4 to 0.6) | 252 | 0.8% |
| Obfuscated payload decoding | R-OBF-001 | 27 | 0.2% (0.1 to 0.3) | 70 | 0.2% |
| Hard-coded IP endpoint | R-NET-002 | 21 | 0.2% (0.1 to 0.3) | 79 | 0.3% |
| Request-capture or paste endpoint | R-EXF-001 | 8 | 0.1% (0.0 to 0.1) | 10 | 0.03% |

**RQ2 Reach.** Contents with a high-risk signal average 2.87 copies against 2.23 for the other 11,806 contents. Both medians are 1. The high-risk group is copied more often at every threshold. It is copied at least twice in 29.3% of cases against 25.7%, at least five times in 10.1% against 7.6%, and at least ten times in 4.1% against 3.0%. It also appears in two or more repositories in 26.0% of cases against 21.6%.

The Mann-Whitney U test on copies gives p = 0.002 with a rank-biserial effect size of 0.042. On distinct repositories it gives p < 0.001 with an effect size of 0.047. The bootstrap difference in mean copies is 0.64 (95% CI 0.12 to 1.25), and in the share copied at least twice it is 3.7 percentage points (1.0 to 6.5). In the negative binomial model with controls, a high-risk signal has an incidence rate ratio of 1.41 (95% CI 1.20 to 1.66, p < 0.001, n = 12,965, dispersion alpha 5.82). Of the controls, the canonical `.claude/skills/` location has the largest association, with a ratio of 6.25 (5.46 to 7.16). Bundled scripts (0.94, 0.80 to 1.10) and repository stars (1.00 per log unit) show no clear association. Eight high-risk categories have at least 30 contents and were tested individually. None differs from the no-signal group after Holm adjustment; the smallest adjusted p-value is 0.096, for destructive commands. <!-- results/rq2_reach_summary.csv, results/rq2_mannwhitney.csv, results/rq2_bootstrap.csv, results/rq2_negbin.csv, results/rq2_category_tests.csv, figures/rq2_copies_by_group.png -->

**RQ3 Drift.** At the main similarity threshold of 0.5, there are 245 near-duplicate variant pairs across 141 front-matter names. Of these, 18 pairs in 6 names differ in their high-risk categories. Ten pairs have commit dates for both variants. In one of them the newer variant adds a high-risk category, an unscoped shell grant, and in none does it drop one. Without template families, 212 pairs remain and 9 differ, across 5 names. Nine of those pairs are dated, and none of them adds or drops a category. As the threshold rises from 0.3 to 0.8, lineage pairs fall from 332 to 137 and differing pairs from 34 to 7. <!-- results/rq3_summary.csv, results/rq3_threshold_sweep.csv, figures/rq3_threshold_sweep.png -->

**Bundled scripts.** Of the 1,326 skills whose bundled script text is available, 200 (15.1%) have at least one script matching a high-risk rule, covering 303 of 5,153 script files. The most common high-risk category in scripts is dynamic code execution, with 131 files, followed by destructive commands (68) and privilege elevation (31). <!-- results/scripts_summary.csv -->

**Robustness.** The high-risk share is 15.0% with a severity cutoff of 5, 2.7% with a cutoff of 7, and 9.5% in the valid front-matter subset. Across the six scenarios, mean copies in the high-risk group are 1.16 to 1.45 times those in the other group. The Mann-Whitney p-value on copies is 0.020 or lower in every scenario, and the rank-biserial effect size stays between 0.040 and 0.060. The smallest copy ratio, 1.16, comes from removing the ten most-copied contents. <!-- results/sensitivity_summary.csv -->

# Discussion

**What validation changes.** The 8.9% high-risk share measures rule matches, not the prevalence of confirmed risky capabilities. Round 1 validation shows why this distinction matters: strict precision ranges from 0.20 for dynamic code execution to 1.00 for unscoped shell tool grants. Capability precision also counts capabilities described in benign contexts, so it answers a different question from whether a finding is risky in context (Table 2). These category-level estimates cannot simply be multiplied by the overall 8.9% share: contents may match multiple categories, and the validation sample is stratified. <!-- Evidence: results/validation_precision_by_category.csv; results/rq1_prevalence_by_category.csv. -->

**H1 and uncertainty.** H1 is supported by the round 1 point estimates: unscoped shell tool grants reach strict precision 1.00 and `sudo` reaches 0.80. Their Wilson intervals remain important: 0.82 to 1.00 for tool grants and 0.61 to 0.91 for `sudo`. The tool-grant interval remains above 0.80, while the sudo interval includes values below it. These estimates apply to the labelled sample and do not establish precision across all skills. Signals were labelled by one rater. The completed intra-rater check found agreement on 61 of 69 rule matches, with Cohen's kappa 0.839. This measures consistency within that rater and does not replace independent signal labeling.

**Reach and competing explanations.** Contents with high-risk signals have a statistically detectable but small difference in copy distributions, consistent with H2 for the scanner-defined groups. The rank-biserial effect size of 0.042 indicates substantial overlap. The adjusted incidence rate ratio of 1.41 and sensitivity analyses support an association, but they do not show that risky capabilities cause copying. Skill purpose, location, popularity, and template inheritance remain competing explanations. The reach analysis groups contents by rule matches; validation does not turn it into a comparison of confirmed risky and confirmed benign contents. Copies measure the spread of identical content, not whether an agent loads or executes it. <!-- Evidence: results/rq2_mannwhitney.csv; results/rq2_negbin.csv; results/sensitivity_summary.csv; RESEARCH_SPEC.md RR-02. -->

**Variant drift.** The primary rater classified the 18 differing pairs as eight template updates, eight local adaptations, and two hardening changes, with no capability additions. This supports treating a difference in matched categories as a prompt for contextual inspection rather than proof of added risk. Drift agreement was 15 of 18 pairs, with Cohen's kappa 0.745, so interpretation still involves judgement. Only ten variant pairs have dates for both variants, and half of the differing pairs belong to one template family; the study therefore cannot establish a general direction of capability change through copying. <!-- Evidence: results/validation_drift.csv; results/validation_agreement.csv; results/rq3_summary.csv. -->

**Implications for review.** The results support using the scanner to prioritize human inspection. Tool grants and `sudo` have stronger strict-precision point estimates than broad dynamic-execution patterns, while benign-context matches show why an automatic rejection policy would need further evaluation. No misses were observed in 40 no-signal items, but the confidence interval extends to 0.088, so absence of a signal does not establish safety. Authors should explain capability scope, reviewers should inspect the surrounding instructions, and rule maintainers can use labelled false positives to propose improvements. These are implications of the findings; the proposed review workflow has not been evaluated as a deployed system. <!-- Evidence: results/validation_precision_by_category.csv; results/validation_recall.csv; docs/research/REVIEW_WORKFLOW.md. -->

# Threats to validity

The full register is in `THREATS_TO_VALIDITY.md`. The threats most specific to this study are summarised here [@wohlin2012; @kalliamvakou2014].

- **Construct.** A keyword match is not a capability, so precision is measured before any claim about risk. Severity scores are the authors' judgement, recorded with a rationale in the threat model and tested with alternative cutoffs.
- **Internal.** Popular setup and DevOps skills may both use shell commands and be copied widely. That can link signals and reach without a causal relationship, and the regression controls and sensitivity runs address it only partly. The strong association of the canonical location with copies shows that where a skill sits matters more than its content signals.
- **Lineage.** Pairing variants by name and text similarity can join unrelated skills with generic names, which is why lineage is checked manually. The template-family list also uses generic names.
- **Measurement.** Human labels carry rater bias. A written guideline and independent second ratings support the drift and lineage assessments, with inter-rater agreement reported separately. Signals were labelled by one person; repeat-labeling produced agreement on 61 of 69 rule matches, with Cohen's kappa 0.839. This measures consistency within that rater, not agreement between independent signal raters. Controls come from the representative row only, so other copies' repositories are ignored.
- **External.** The population is a lower bound on public default branches in July 2026. The sample's hash-based draw splits variant families, so drift results describe the sample only.
- **Conclusion.** Copy distributions are heavily skewed, so non-parametric tests, bootstrap intervals, and a count model are used together, and the Holm correction covers the per-category tests.
- **Reproducibility.** Results depend on the dataset snapshot and the rule file version, both recorded by hash for every run.

**The six areas the assignment names.**

- **Dataset bias.** The sample is the 13,000 lowest content hashes, about 0.7% of distinct contents, drawn from a population that GitHub code search limits to default branches, files under 384 KB and few forks, so it is a lower bound (E1, E2, P8).
- **Measurement error.** A keyword match is not a capability (P1). Human labels carry rater bias, which inter-rater agreement measures for drift and lineage and intra-rater agreement for signals (P6). The similarity threshold that defines reuse is swept from 0.3 to 0.8 (C2).
- **Confounding.** Popular setup and DevOps skills both use shell commands and are copied more, so signals and reach can move together without one causing the other (P3, I1).
- **Missing data.** 2,547 bundled script files have no text and were not scanned, against 5,153 that were (P10). Commit history covers every standard-location skill but only a size-stratified sample of the rest (I4). Rows without text are counted, not dropped (R2).
- **Reproducibility.** The dataset snapshot and the rule file are recorded by hash for every run (R1), sampling uses fixed seeds (R3), and release v0.9.0-rc1 was reproduced on a fresh GitHub runner and from a fresh clone on Windows: 14 of 14 result tables matched (R4, #33).
- **Generalizability.** The data is a July 2026 snapshot of formats that are still changing quickly (E4), and the drift results describe the hash-based sample only (E2).

# Related work and references

**Agent skills.** GitSkills is the first dataset of agent skills on GitHub. It retains every file occurrence with its content hash, which makes copy-based reuse directly measurable [@gitskills2027]. SpecMine, the companion MSR 2027 dataset, covers specification-driven development artifacts [@specmine2027].

**Software supply chains.** Ohm et al. review attacks that inject malicious code into open-source packages and redistribution channels [@ohm2020]. Skills lack a package manager, so their supply chain is the act of copying itself.

**Prompt injection.** Greshake et al. show that instructions reaching an LLM-integrated application through retrieved content can be executed with the user's authority [@greshake2023]. A copied skill is a trusted, persistent instance of that channel.

**Propagation.** Directed-graph epidemiological models describe how malicious code spreads across networks of hosts [@kephart1991]. This study borrows only the framing of exposure through copies, not a fitted epidemic model.

**Mining GitHub.** The perils of treating GitHub data as representative apply here, including forks and inactive or personal repositories [@kalliamvakou2014].

# Conclusion and future work

In the GitSkills July 2026 sample, 8.9% of 12,965 distinct skill contents matched at least one high-risk rule, rising to 11.2% when weighted by copies. These are signal frequencies, not estimates of confirmed risky capabilities: round 1 strict precision varied from 0.20 to 1.00 across categories, with unscoped shell tool grants and `sudo` meeting H1's 0.80 threshold as point estimates (Table 2). Contents with high-risk signals had a small association with greater copying, supporting H2 for the scanner-defined groups without establishing causation or actual agent use. Manual drift labels identified template updates, local adaptations, and hardening among the 18 differing pairs, while sparse dates and template concentration prevent a general claim about the direction of capability change. Together, these findings support contextual human review of scanner findings rather than automatic risk verdicts. <!-- Evidence: results/population_flow.csv; results/rq1_prevalence_by_rule.csv; results/validation_precision_by_category.csv; results/rq2_mannwhitney.csv; results/validation_drift.csv; results/rq3_summary.csv. -->

Future work includes expanding validation with raters outside the team and evaluating rule improvements against labelled false positives. Analysis of the full GitSkills dataset could increase coverage of variant families, although the availability and quality of dates would still need assessment. The implemented skill-scan command line, GitHub Action, and VS Code tooling are documented in `docs/TOOL.md`; their effectiveness with users and the effectiveness of the complete proposed human-review workflow require evaluation. Dynamic analysis in an isolated sandbox remains outside this study's scope.

# Artifact appendix

- **Repository.** https://github.com/jeraddunne/csc580-group9-msr2027. The release tag is to be set at the Sprint 3 review.
- **Setup and data.** Run `make setup`, then `make data`. The GitSkills sample downloads to `data/samples/` and is not redistributed.
- **Validation.** Run `python scripts/annotation_kit.py sample`, then `sheet --rater <id> --round 1`, label, then `score`. Label files live in `data/annotations/`, and reading packets are generated locally and never committed.
- **Pilot.** `python -m msr_pipeline risk-pilot` reproduces the proposal's pilot tables.
- **Data availability.** GitSkills full dataset: doi:10.5281/zenodo.21875637; sample: the dataset authors' GitHub repository. Dataset content is not redistributed in this repository.
- **Process.** The project was run as Scrum with a Lean Six Sigma overlay [@schwaber2020; @george2002], by a four-person team that became three when Allie Hodges left the course in Sprint 2 (D-025), with rotating Product Owner and Scrum Master roles (ADR-0006). The team's confirmed most important process improvement was assigning a reviewer when each pull request opens and waiting for approval from a team member other than the author before merging, as confirmed in issue #35. The team introduced this practice at the Sprint 1 retrospective as part of its 48-hour review target (kaizen #10). The share of pull requests merged without approval from another member fell from 8 of 21 (38.1%) in Sprint 1 to 0 of 36 (0%) in Sprint 2. See the [Sprint 3 retrospective, section 9](../docs/sprints/sprint-3/retrospective.md#9-most-important-process-improvement-this-semester-rubric-mandatory) and the [PR review audit](../docs/lean-six-sigma/metrics/pr_review_audit.csv).
- **AI-use disclosure.** AI assistance is logged in `ai-use-log.md`, including what was generated and how it was verified.

 ## Table and figure sources

Run `make figures`, `make validation-score`, `make workflow-diagrams`, and `make report-tables` in that order after setting up the repository and downloading the sample.

Every numbered table and every figure in this report is listed below with its generation target. The research sub-questions are an authored list, not a table, and hold no generated values.

| Report item | Source | Generation target |
|---|---|---|
| Table 1 — Population flow | `results/population_flow.csv` | `make figures`, then `make report-tables` |
| Table 2 — Validation of high-risk signals | `results/validation_precision_by_category.csv` | `make validation-score`, then `make report-tables` |
| Table 3 — High-risk signals | `results/rq1_prevalence_by_rule.csv`, `results/rq1_prevalence_by_category.csv`, and `results/population_flow.csv` | `make figures`, then `make report-tables` |
| Figure 1 — Review workflow activity diagram | `scripts/make_workflow_diagrams.py` | `make workflow-diagrams` |
| Supporting research plots | `figures/rq1_prevalence_by_category.png`, `figures/rq2_copies_by_group.png`, and `figures/rq3_threshold_sweep.png` | `make figures` |

# References

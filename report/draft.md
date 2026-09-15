---
title: "Risky Capabilities in Copied Agent Skills: Prevalence, Reach, and Drift in GitSkills"
subtitle: "SWE 380 / CSC 580 Project, University of Michigan-Flint (solo project, ADR-0005)"
author:
  - Jerad Dunne
date: "Draft, updated 2026-09-14"
bibliography: references.bib
link-citations: true
---

<!--
How to use: every section below is required by the assignment. Numbers come only from files produced by
`python -m msr_pipeline analyze` (run of 2026-09-14, results/ANALYSIS_MANIFEST.json) and, later,
`python scripts/annotation_kit.py score`. The file is named in a comment next to each result.

Convention: observation versus interpretation. Results reports only what the data shows. Discussion is
the only place for interpretation, causal language, and implications.

Status on 2026-09-14: framing, dataset, method, validation design, and unvalidated results are written.
No labels exist yet, so every statement about whether a signal is a real capability stays pending until
round 1 labelling in Sprint 2. Discussion and Conclusion are deliberately short until then.
-->

# Abstract

Agent skills are folders of natural-language instructions, often with bundled scripts, that AI coding agents load and follow with the permissions of the user. Developers reuse them by copying folders between repositories, with no package manager or verifier in between. This study builds a static, rule-based scanner for risk-relevant capabilities in skills and applies it to the GitSkills July 2026 sample of 12,965 distinct skill contents. In the sample, 8.9% of distinct contents match at least one high-risk rule, rising to 11.2% when weighted by copies. Contents with a high-risk signal are copied slightly more: 2.87 copies on average against 2.23, with a small effect size. The difference holds in a negative binomial model with controls and across six sensitivity scenarios. Variant pairs that differ in high-risk capabilities are rare, and half of them come from one widely copied template. All signals are unvalidated keyword matches until manual validation is complete. <!-- Numbers: results/population_flow.csv, results/rq1_prevalence_by_rule.csv, results/rq2_reach_summary.csv, results/rq2_mannwhitney.csv, results/rq2_negbin.csv, results/sensitivity_summary.csv, results/rq3_summary.csv. Add validated precision once results/validation_precision_by_category.csv exists. -->

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

| Sub-question | Measure |
|---|---|
| RQ1 Prevalence | Share of distinct contents, and share of copy-weighted occurrences, with each capability category |
| RQ2 Reach | Copies and distinct repositories per content, for contents with and without a high-risk capability |
| RQ3 Drift | Among near-duplicate variants sharing a front-matter name, how often high-risk capabilities differ, and in which direction when both commit dates exist |

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

<!-- Figure 1: Pipeline overview (load, scan, link variants, analyze, validate, report). To draw in Sprint 2. -->

# Evaluation and validation

**Automated tests.** The test suite covers every rule's documented examples, the scanner, variant linking and ordering, missing-value handling, the statistics helpers, and the validation scoring. It runs offline against small fixtures.

**Manual validation design.** Rule precision is measured on a stratified sample of 147 distinct contents: up to 10 per high-risk category plus 40 with no signal, drawn with seed 580. They yield 209 label rows, one per matched rule plus one per no-signal item. For each match, the annotator assigns one of three labels. *Risky* means the capability is present and would act with user permissions in context. *Benign in context* means the capability is present but described, warned against, or clearly sandboxed. *Not present* means the rule matched text that does not grant the capability. Strict precision counts only *risky*; capability precision counts *risky* and *benign in context*. Both carry Wilson intervals. The no-signal items estimate how often a high-risk capability is missed.

A lineage sample of 58 variant pairs checks whether pairs really share a lineage: the 18 pairs whose high-risk categories differ, plus 40 random pairs. The 18 differing pairs are also classified as template update, local adaptation, hardening, capability addition, or unrelated. <!-- data/annotations/samples/SAMPLE_MANIFEST.json -->

**Reliability.** This is a solo project, so there is one human annotator. Reliability is measured as intra-rater agreement. About 30% of items are re-labelled at least seven days after round one, blind to the first labels: 45 signal items, 18 lineage pairs, and 6 drift pairs. Cohen's kappa is reported [@cohen1960]. An optional second rater may be added. If an LLM is used as a second rater, it is disclosed and reported separately, never counted as human agreement. The guideline is in `docs/validation/ANNOTATION_GUIDELINE.md`.

**FMEA ranking.** Categories are ranked by severity (from the rule file), occurrence (validated prevalence), and detection (estimated miss rate), in the style of a failure mode and effects analysis. The ranking prioritises categories for review and is not a risk verdict.

<!-- Table 2: Validation results. Source: results/validation_precision_by_category.csv, results/validation_agreement.csv (python scripts/annotation_kit.py score). PENDING: no labels exist yet. -->

# Results

All results in this section are unvalidated keyword signals. They describe where the rules match, not confirmed capabilities.

**RQ1 Prevalence.** Of the 12,965 distinct contents in the main population, 1,159 match at least one high-risk rule: 8.9%, 95% CI 8.5% to 9.4%. Weighted by copies, 3,326 of 29,679 occurrences carry one, or 11.2%. Table 2 lists each high-risk capability. For persistence locations, `sudo`, and destructive commands, the copy-weighted share is about double the content share. Context rules match far more often: shell code blocks in 4,351 contents (33.6%), `allowed-tools` declarations in 1,282 (9.9%), secret-named environment variables in 938 (7.2%), and network tooling in 851 (6.6%). <!-- results/rq1_prevalence_by_rule.csv, results/rq1_prevalence_by_category.csv, figures/rq1_prevalence_by_category.png -->

Table 2. High-risk signals in the main population. <!-- results/rq1_prevalence_by_rule.csv; download-and-execute from results/rq1_prevalence_by_category.csv -->

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

<!-- Interpretation is limited until validation. Items below are framed as what the results allow and what they do not. -->

**What the results allow.** The reach difference is statistically clear but small. An effect size near 0.04 means that for a random pair of contents, one from each group, the ordering of their copy counts is close to a coin flip. The model-adjusted rate ratio of 1.41 and the stability across scenarios make an artefact of one threshold or one template family unlikely. The prevalence numbers bound how common each pattern is in the text of skills. They do not show how often an agent would act on it.

**What the results do not allow yet.** Without validated precision, the high-risk share could be substantially lower than 8.9% if many matches describe patterns rather than instruct them. The per-category tests do not survive correction, so the aggregate reach difference cannot be attributed to any single capability. RQ3 cannot say whether copying tends to add or remove capabilities: the sample holds only ten dated variant pairs, and half the differing pairs belong to one template.

<!-- PENDING after validation: compare validated precision with these shares; revisit H1; one manually inspected case study from results/rq3_differing_pairs.csv; implications for skill authors, installers, and linters. -->

# Threats to validity

The full register is in `THREATS_TO_VALIDITY.md`. The threats most specific to this study are summarised here [@wohlin2012; @kalliamvakou2014].

- **Construct.** A keyword match is not a capability, so precision is measured before any claim about risk. Severity scores are the author's judgement, recorded with a rationale in the threat model and tested with alternative cutoffs.
- **Internal.** Popular setup and DevOps skills may both use shell commands and be copied widely. That can link signals and reach without a causal relationship, and the regression controls and sensitivity runs address it only partly. The strong association of the canonical location with copies shows that where a skill sits matters more than its content signals.
- **Lineage.** Pairing variants by name and text similarity can join unrelated skills with generic names, which is why lineage is checked manually. The template-family list also uses generic names.
- **Measurement.** A single human annotator introduces personal bias, mitigated by a written guideline, blind re-labelling, and reported intra-rater kappa. Controls come from the representative row only, so other copies' repositories are ignored.
- **External.** The population is a lower bound on public default branches in July 2026. The sample's hash-based draw splits variant families, so drift results describe the sample only.
- **Conclusion.** Copy distributions are heavily skewed, so non-parametric tests, bootstrap intervals, and a count model are used together, and the Holm correction covers the per-category tests.
- **Reproducibility.** Results depend on the dataset snapshot and the rule file version, both recorded by hash for every run.

# Related work and references

**Agent skills.** GitSkills is the first dataset of agent skills on GitHub. It retains every file occurrence with its content hash, which makes copy-based reuse directly measurable [@gitskills2027]. SpecMine, the companion MSR 2027 dataset, covers specification-driven development artifacts [@specmine2027].

**Software supply chains.** Ohm et al. review attacks that inject malicious code into open-source packages and redistribution channels [@ohm2020]. Skills lack a package manager, so their supply chain is the act of copying itself.

**Prompt injection.** Greshake et al. show that instructions reaching an LLM-integrated application through retrieved content can be executed with the user's authority [@greshake2023]. A copied skill is a trusted, persistent instance of that channel.

**Propagation.** Directed-graph epidemiological models describe how malicious code spreads across networks of hosts [@kephart1991]. This study borrows only the framing of exposure through copies, not a fitted epidemic model.

**Mining GitHub.** The perils of treating GitHub data as representative apply here, including forks and inactive or personal repositories [@kalliamvakou2014].

# Conclusion and future work

<!-- PENDING after validation: three or four sentences on what was learned. -->

Future work that follows from the current results is clear. The full GitSkills dataset would supply enough dated variant families to test the direction of drift. More annotators would move reliability from intra-rater to inter-rater agreement. Dynamic analysis in an isolated sandbox is explicitly out of scope here. A linter for skill authors could turn the rule file into a practical tool.

# Artifact appendix

- **Repository.** https://github.com/jeraddunne/csc580-group9-msr2027. The release tag is to be set at the Sprint 3 review.
- **Setup and data.** Run `make setup`, then `make data`. The GitSkills sample downloads to `data/samples/` and is not redistributed.
- **Reproduce every table and figure.** Run `python -m msr_pipeline analyze` (286 seconds on the author's laptop).
- **Validation.** Run `python scripts/annotation_kit.py sample`, then `sheet --rater <id> --round 1`, label, then `score`. Label files live in `data/annotations/`, and reading packets are generated locally and never committed.
- **Pilot.** `python -m msr_pipeline risk-pilot` reproduces the proposal's pilot tables.
- **Data availability.** GitSkills full dataset: doi:10.5281/zenodo.21875637; sample: the dataset authors' GitHub repository. Dataset content is not redistributed in this repository.
- **Process.** The project was run as Scrum with a Lean Six Sigma overlay [@schwaber2020; @george2002], by one person holding every role (ADR-0005). The most important process improvement, with before-and-after numbers, is to be added at the Sprint 3 retrospective.
- **AI-use disclosure.** AI assistance is logged in `ai-use-log.md`, including what was generated and how it was verified.

# References

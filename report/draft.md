---
title: "<Working title>: <one-line description of the question>"
subtitle: "SWE 380 / CSC 580 Group Project, Group 9, University of Michigan-Flint"
author:
  - Leticia Aderhold
  - Jerad Dunne
  - Allie Hodges
  - Hina Kramer
date: "Draft, updated <YYYY-MM-DD>"
bibliography: references.bib
link-citations: true
---

<!--
How to use: every section below is required by the assignment. The HTML comments are guidance and are not rendered. Write prose, not bullets, in the final version. Every number must come from a file in results/ or figures/ produced by the pipeline; name the producing script in a comment next to it.

Convention: observation versus interpretation. The Results section reports only what the data shows (counts, distributions, statistics, examples). The Discussion section is the only place for interpretation, causal language, and implications. If a sentence contains "suggests", "indicates", "because", or "implies", it belongs in Discussion.

Dataset snapshot statement (required, copy into the Dataset section): "This study uses the <GitSkills / SpecMine> <sample / full> dataset, <version>, downloaded on <YYYY-MM-DD> from <Zenodo DOI / Hugging Face / GitHub URL>."
-->

# Abstract

<!--
- The question, the method, the main result, and the implication, in four or five sentences.
- Write last. Numbers here must match Results exactly.
-->

# Introduction

<!--
- Motivation: what observable software-engineering problem does this address in AI-native development?
- Context: MSR 2027 Mining Challenge, GitSkills [@gitskills2027] and SpecMine [@specmine2027].
- Contribution: one sentence per contribution (pipeline, evidence, validated finding).
- The competing or simpler explanation you will test against.
-->

# Research question and hypotheses or expectations

<!--
- The research question in one precise sentence (copy from RESEARCH_QUESTION.md).
- Operationalize: unit of analysis, population, sample, variables (independent, dependent, controls), outcome measures.
- State expectations or hypotheses and the competing explanation as testable statements.
-->

# Dataset and data preparation

<!--
- Source and scope: which dataset(s), which tables, which columns (see DATA_DICTIONARY.md).
- Dataset snapshot statement (see the top of this file).
- Sampling: how the analysed sample was chosen; why it is defensible; how it differs from the full corpus.
- Filtering: rows removed and why, with counts (Table 1: filtering funnel).
- Ethics: anonymised authors, no deanonymisation, licenses respected, no execution of untrusted scripts.
-->

<!-- Table 1: Filtering funnel. Source: results/<file>.csv, script: src/msr_pipeline/<module>.py -->

# Method and implementation

<!--
- Algorithms and tools: the core mining, extraction, similarity, classification, or traceability method.
- Pipeline stages with inputs and outputs (Figure 1).
- Baselines: the simpler method you compare against.
- Design decisions: cite ADRs in docs/decisions/ (for example thresholds, join strategy).
- Reproducibility: the exact command sequence (make pipeline) and runtime.
-->

<!-- Figure 1: Pipeline overview. figures/pipeline.png -->

# Evaluation and validation

<!--
- Test strategy: what the automated tests cover (tests/).
- Manual validation: sample size, sampling method, annotation protocol, number of annotators, agreement statistic (for example Cohen's kappa [@cohen1960]).
- Metrics: precision, recall, agreement, or whatever fits the method, with definitions.
- Error analysis: failure modes with counts and examples.
-->

<!-- Table 2: Validation results. Source: results/<file>.csv -->

# Results

<!--
- Observations only. Report each result with the number and the artifact it comes from.
- One paragraph per research sub-question or expectation.
- Robustness and sensitivity: what changed when thresholds or samples changed.
- Subgroup comparison where meaningful.
-->

<!-- Figure 2: Main result. figures/<name>.png, script: src/msr_pipeline/<module>.py -->
<!-- Table 3: Main result. results/<name>.csv -->
<!-- Table 4: Robustness check. results/<name>.csv -->

# Discussion

<!--
- Interpretation: what the results mean for the research question.
- Comparison with expectations and with the competing explanation.
- Implications for AI-native software engineering practice and research.
- Surprises and one manually inspected case study explaining an unexpected result.
-->

# Threats to validity

<!--
- Internal, construct, external, conclusion, and reproducibility threats [@wohlin2012].
- Address explicitly: dataset bias, measurement error, confounding, missing data, reproducibility, generalizability.
- Keep this consistent with THREATS_TO_VALIDITY.md (copy the final table).
- The perils of mining GitHub data apply here [@kalliamvakou2014].
-->

# Related work and references

<!--
- Relevant MSR, software engineering, mining, and AI-assisted development literature.
- The two dataset papers, and prior work on clones and reuse, specification quality, or authorship signals as appropriate.
- Only verified references from references.bib.
-->

# Conclusion and future work

<!--
- What was learned, in three or four sentences.
- What a larger study (full dataset, more annotators, additional sources) should do next.
-->

# Artifact appendix

<!--
- Repository URL and release tag.
- Commands to reproduce every table and figure, with expected runtime.
- Data availability: dataset DOIs, sample locations, what is not redistributed and why.
- Limitations of the artifact.
- Team roles per sprint and the process summary (Scrum with a Lean Six Sigma overlay [@schwaber2020; @george2002]); the most important process improvement with before and after numbers.
- AI-use disclosure consistent with ai-use-log.md.
-->

# References

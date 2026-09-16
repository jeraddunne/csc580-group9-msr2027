# Threats to validity

How to use: this is a living register, required by the assignment. The research question is fixed as proposal P-01 (`RESEARCH_QUESTION.md`), so rows are marked **Active: P-01** when they apply and **Not applicable** otherwise (kept for the record). Update the Status column at every sprint review (Sprint 1: identified; Sprint 2: mitigation designed; Sprint 3: mitigated, accepted, or open). The final report's threats section addresses, at minimum, dataset bias, measurement error, confounding, missing data, reproducibility, and generalizability.

Status values: Active: P-01 (with stage: identified, mitigation planned, mitigated, accepted, open), Not applicable. Question numbers (Q1 to Q15) refer to the assignment's proposed research questions. The project is run by the four-person Group 9 (ADR-0006). Rows with Jerad Dunne as Owner were assigned while one member held every role (ADR-0005); owners are reassigned at Sprint 1 planning.

## P-01 specific threats

| ID | Threat | Type | Mitigation | Evidence | Status |
|---|---|---|---|---|---|
| P1 | A keyword match is not a capability. Skills often quote unsafe patterns to warn against them, and documentation mentions commands it never runs | Construct | Validation labels separate risky in context, benign in context, and not present; only validated precision is reported as a property of a rule; headline results repeated at severity cutoffs 5 and 7 | `results/rq1_prevalence_by_rule.csv`, `results/sensitivity_summary.csv`, annotation kit outputs | Active: P-01, mitigation planned |
| P2 | Template inheritance. Variants of widely copied template skills differ because the template changed, not because copiers added capabilities | Internal | `is_template_family` flag; RQ3 reported with and without template families; sensitivity scenario excludes template families | `results/rq3_summary.csv`, `results/sensitivity_summary.csv` | Active: P-01, mitigation planned |
| P3 | Popularity and purpose confound. Setup, DevOps, and deployment skills need shell and network commands and are also copied more, so a reach difference may reflect purpose, not risk | Internal | NB2 regression with size, scripts, location, stars, and language controls; per-category tests with Holm adjustment; scenario excluding the 10 most-copied contents | `results/rq2_negbin.csv`, `results/rq2_category_tests.csv`, `results/sensitivity_summary.csv` | Active: P-01, mitigation planned |
| P4 | Lineage by name plus similarity can pair unrelated skills that share a generic name, and miss renamed descendants | Construct | Threshold sweep from 0.3 to 0.8; manual check of every differing pair at 0.5; results framed as same-name near-duplicates, not proven lineage | `results/rq3_threshold_sweep.csv`, `results/rq3_differing_pairs.csv` | Active: P-01, mitigation planned |
| P5 | Sparse history. Few variant pairs have first-commit dates for both variants, so the direction of drift is underpowered, and dates follow the current path (I3) | Conclusion | RQ3 is descriptive with case studies; no direction test is claimed; the count of ordered pairs is reported at every threshold | `results/rq3_threshold_sweep.csv` | Active: P-01, accepted (scoped) |
| P6 | Rater bias and disagreement. Labels reflect human judgement that can differ between raters, and a second rater who sees the primary labels is no longer independent | Construct / conclusion | Written guideline before labelling; a teammate second rater labels round 1 independently; blindness rule (primary-rater label files committed only after the second rater's file for the same kind); inter-rater Cohen's kappa reported per kind; optional intra-rater re-label of 30%; LLM labels reported separately and never merged into primary labels | annotation kit agreement output | Active: P-01, mitigation planned |
| P7 | Representative-row controls. Stars, language, and location come from the representative copy's repository, not from every repository holding a copy | Internal | Stated in the model note; secondary outcome `repos` counts all repositories; interpret controls as describing the representative only | `results/rq2_negbin.csv` (note column) | Active: P-01, accepted |
| P8 | Lower-bound population. Code search misses non-default branches, large files, and most forks, and the sample is 0.7% of distinct contents | External | Population stated as "skills discoverable by GitHub code search in July 2026"; no claims about all skills; prevalence reported with confidence intervals for the sample only | `results/population_flow.csv` | Active: P-01, accepted |

## Internal validity (could something other than our variables explain the result?)

| ID | Threat | Applies if we choose | Mitigation | Owner | Status |
|---|---|---|---|---|---|
| I1 | Confounding by repository popularity: stars, age, and activity correlate with almost every artifact property (reuse, edits, staleness) | Any question comparing groups (Q1, Q2, Q3, Q7, Q8, Q13, Q15) | Control for log stars in the NB2 model; see P3 | Jerad Dunne | Active: P-01, mitigation planned |
| I2 | Time-window censoring: artifacts created near the July 2026 snapshot have had less time to be copied, edited, or abandoned | Any lifecycle, churn, survival, or abandonment measure (Q1, Q3, Q10, Q14) | Reach (copies) is right-censored at the snapshot; history exists only for a subset, so no age control is possible for most contents. Stated as a limitation; if an age proxy is added later, rerun RQ2 with it | Jerad Dunne | Active: P-01, accepted |
| I3 | Commit history follows the file's current path in GitSkills: `first_commit_at` dates a rename, `commit_count` covers only the current path | GitSkills lifecycle, edit counts, or propagation timelines (Q1, Q2, Q3, Q14) | RQ3 ordering treats first-commit dates as lower bounds; see P5 | Jerad Dunne | Active: P-01, accepted |
| I4 | Which rows carry history in GitSkills: every standard-location skill plus a size-stratified sample of the rest (`history_fetched`) | Any analysis using GitSkills commit fields | Ordered pairs are counted and reported; see P5 | Jerad Dunne | Active: P-01, accepted |
| I5 | SpecMine commit histories can be truncated or errored (`commit_history_status`) | SpecMine lifecycle or traceability timing (Q9, Q10, Q12, Q14) | Not used | | Not applicable (P-01 uses GitSkills only) |

## Construct validity (do our measures capture what we claim?)

| ID | Threat | Applies if we choose | Mitigation | Owner | Status |
|---|---|---|---|---|---|
| C1 | Quality proxy is not quality: copy count, edit count, or survival may reflect visibility or templating rather than usefulness | Q2, Q8, Q15 | P-01 uses copies as reach, not as quality | | Not applicable |
| C2 | Similarity threshold defines "reuse" or "boilerplate": different thresholds give different populations | Q1, Q11 | Threshold sweep 0.3 to 0.8 (`results/rq3_threshold_sweep.csv`); see P4 | Jerad Dunne | Active: P-01, mitigation planned |
| C3 | "Stale", "abandoned", "complete", and "risky" are operational definitions we invent | Q3, Q4, Q7, Q10 | "Risky" is defined in `docs/research/THREAT_MODEL.md` before analysis; validated against labels from two independent raters with inter-rater kappa (P6) | Jerad Dunne | Active: P-01, mitigation planned |
| C4 | Authorship signals are heuristics, not ground truth; GitSkills author identities are one-way codes, bots keep logins | Q6, Q12 | Not used | | Not applicable |
| C5 | Tool attribution in SpecMine is by path fingerprint, not by verified tool use | Any SpecMine tool-family comparison (Q5, Q11, Q13) | Not used | | Not applicable |
| C6 | Text metrics (readability, length, headings) on Markdown may be distorted by code fences, front matter, and non-English content | Q2, Q5, Q11 | Only `body_chars` is used, as a control; rules run on the full text including code fences, by design | Jerad Dunne | Active: P-01, accepted |

## External validity (does the result generalize beyond our sample?)

| ID | Threat | Applies if we choose | Mitigation | Owner | Status |
|---|---|---|---|---|---|
| E1 | GitHub code search indexes default branches only, files under 384 KB, recently active repositories with fewer than 500,000 files, and forks only when more starred than the parent: GitSkills is a lower bound on the population | Any GitSkills question | See P8 | Jerad Dunne | Active: P-01, accepted |
| E2 | The GitSkills sample is the 13,000 lowest content hashes: uniform in practice but only about 0.7% of distinct contents | Any GitSkills question run on the sample | Report the sample fraction and confidence intervals; the sample splits variant families, which scopes RQ3 (P5) | Jerad Dunne | Active: P-01, accepted |
| E3 | The SpecMine sample of 500 repositories is deliberately non-representative | Any SpecMine question run on the sample | Not used | | Not applicable |
| E4 | Point-in-time snapshot (July 2026): the formats are young and adoption is still changing quickly | Any adoption or convergence question (Q5) | Findings framed as a July 2026 snapshot; no trend claims | Jerad Dunne | Active: P-01, accepted |
| E5 | Pre-format files: lowercase `skill.md` and similar names from as early as 2014 match the GitSkills filename query | Any GitSkills population definition | Front-matter-valid sensitivity subset (`results/sensitivity_summary.csv`) | Jerad Dunne | Active: P-01, mitigation planned |
| E6 | Joining GitSkills and SpecMine on repository names covers only the intersection, which is small and biased toward active repositories | Q13, Q14 | Not used | | Not applicable |

## Conclusion validity (are the statistics and inferences sound?)

| ID | Threat | Applies if we choose | Mitigation | Owner | Status |
|---|---|---|---|---|---|
| N1 | Verbatim duplicates inflate counts and break independence assumptions | Any GitSkills count or correlation | Analysis at the distinct-content level; copies are the outcome; copy-weighted shares reported separately | Jerad Dunne | Active: P-01, mitigated |
| N2 | Heavy-tailed distributions (copies, stars, sizes) make means misleading | Any quantitative comparison | Mann-Whitney U with rank-biserial effect size as the primary test; medians and share copied 2, 5, 10 or more; NB2 for counts; log1p transforms | Jerad Dunne | Active: P-01, mitigated |
| N3 | Multiple comparisons across many features or tool families inflate false positives | Q2, Q5, Q8, Q15 | One pre-stated primary comparison (H2); per-category tests Holm-adjusted (`results/rq2_category_tests.csv`) | Jerad Dunne | Active: P-01, mitigated |
| N4 | Correlation presented as causation | Q2, Q8, Q15 | Reach results are associations; report separates observation from interpretation; competing explanations in `RESEARCH_QUESTION.md` section 4 | Jerad Dunne | Active: P-01, mitigation planned |
| N5 | Small manual validation sample gives wide uncertainty on precision and agreement | Any validated classifier or detector | Stratified sample of about 150; precision with Wilson intervals; inter-rater kappa (P6) | Jerad Dunne | Active: P-01, mitigation planned |

## Reproducibility validity (can someone else get the same result?)

| ID | Threat | Applies if we choose | Mitigation | Owner | Status |
|---|---|---|---|---|---|
| R1 | Dataset version drift: Zenodo and Hugging Face releases may be updated after we download | All | `data/samples/MANIFEST.json` records sha256 and upstream commit; `results/ANALYSIS_MANIFEST.json` records the database hash, rule file hash, and package versions for every run | Jerad Dunne | Active: P-01, mitigated |
| R2 | Missing or oversized content: GitSkills `content_fetched` leaves rows without text | Any text analysis | Excluded rows counted in `results/population_flow.csv` | Jerad Dunne | Active: P-01, mitigated |
| R3 | Non-deterministic steps (random sampling, model training, unordered SQL results) change outputs between runs | Any sampling or modeling step | Bootstrap and validation sampling use seed 580; SQL ordered by `file_sha`; seed recorded in the manifest | Jerad Dunne | Active: P-01, mitigated |
| R4 | Environment differences (Python, pandas, scipy, statsmodels versions) change results or break the pipeline | All | Versions recorded in `results/ANALYSIS_MANIFEST.json`; offline tests; fresh-clone gemba walk each sprint; CI once workflows are enabled | Jerad Dunne | Active: P-01, mitigation planned |
| R5 | Symlink skills in GitSkills contain a path instead of instructions | Any GitSkills text analysis | Excluded by `skill_risk.is_symlink_stub`; count reported in `results/population_flow.csv` | Jerad Dunne | Active: P-01, mitigated |
| R6 | Safety: bundled scripts in GitSkills may be malicious; running them would be both a safety and an integrity risk | Q4 and any analysis of `artifact_siblings` | Static text analysis only; nothing is executed, imported, or fetched (loader and scanner docstrings, `data/README.md`) | Jerad Dunne | Active: P-01, mitigated |

## Ethics and responsible use

| ID | Threat | Mitigation | Status |
|---|---|---|---|
| X1 | Deanonymization of GitSkills author codes | Never attempt re-identification; aggregate reporting; no repository or account names in `results/` | Active: P-01, mitigated |
| X2 | License compliance when quoting skill content in the report | Quote minimally and only as needed for false-positive discussion; no runnable payloads; respect the repository license | Active: P-01, mitigation planned |
| X3 | AI-generated analysis or text presented without verification | Every AI-assisted artifact is logged in `ai-use-log.md` and reviewed by a member other than the author before merge | Active: P-01, mitigation planned |
| X4 | Reporting suspected malicious skills could harm maintainers or spread payloads | Report categories and rates only; if something appears actively malicious, stop and raise it with the instructor before any further step | Active: P-01, mitigation planned |

## Change log

| Date | Sprint | Change | By |
|---|---|---|---|
| 2026-09-13 | Formation | Initial register from the dataset documentation and the assignment | Group 9 |
| 2026-09-14 | Formation | Research question fixed as P-01; rows marked Active or Not applicable; P-01 threats P1 to P8 and X4 added; mitigations point to `python -m msr_pipeline analyze` outputs | Jerad Dunne |
| 2026-09-15 | Formation | Group reinstated (ADR-0006): P6 rewritten for rater disagreement and independence with a teammate second rater; C3 and N5 now cite inter-rater kappa; X3 requires review by another member; row owners to be reassigned at Sprint 1 planning | Jerad Dunne |

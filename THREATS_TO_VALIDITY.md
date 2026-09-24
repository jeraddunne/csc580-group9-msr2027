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
| P5 | Sparse history. Few variant pairs have first-commit dates for both variants, so the direction of drift is underpowered, and dates follow the current path (I3). History covers nearly every canonical skill but about 11% of the rest (NB-Q06, V11), so datable pairs lean canonical | Conclusion | RQ3 is descriptive with case studies; no direction test is claimed; ordered pairs are reported at every threshold and split by location (RR-03): at 0.5, 5 with both variants canonical, 5 with one, 0 with neither, and no threshold has a pair with neither, so every observable direction involves a canonical skill | `results/rq3_threshold_sweep.csv` | Active: P-01, accepted (scoped) |
| P6 | Rater bias and disagreement. Labels reflect human judgement that can differ between raters, and a second rater who sees the primary labels is no longer independent. Since D-022, only drift has a second rater; lineage and signals are labelled by one person | Construct / conclusion | Written guideline before labelling; drift: a teammate (`la`) labels round 1 independently under the blindness rule, and inter-rater kappa is reported; lineage and signals: the primary rater re-labels a 30% subset at least 14 days later without looking at round 1, and intra-rater kappa is reported and named as such. The report states that intra-rater agreement shows consistency, not that a second reader applies the guideline the same way | `docs/validation/README.md`, `results/validation_agreement.csv` (after scoring) | Active: P-01, mitigation planned |
| P7 | Representative-row controls. Stars, language, and location come from the representative copy's repository, not from every repository holding a copy | Internal | Stated in the model note; secondary outcome `repos` counts all repositories; interpret controls as describing the representative only | `results/rq2_negbin.csv` (note column) | Active: P-01, accepted |
| P8 | Lower-bound population. Code search misses non-default branches, large files, and most forks, and the sample is 0.7% of distinct contents | External | Population stated as "skills discoverable by GitHub code search in July 2026"; no claims about all skills; prevalence reported with confidence intervals for the sample only | `results/population_flow.csv` | Active: P-01, accepted |
| P9 | Reach is not use. No source establishes that a copy of a skill in a repository is ever loaded or run by an agent there (NB-Q15), so copy counts measure the spread of identical content, not exposure | Construct | "Reach" is defined as the spread of identical content (RR-02); the report never says risky skills are "used" more, which `make verify-spec` RR-02 checks in `report/draft.md` | `RESEARCH_SPEC.md` RR-02; `results/spec_verification.csv` | Active: P-01, mitigated |
| P10 | Unread bundled files. 2,547 script files carry no text (undocumented `content_fetched = 2`, V07), against 5,153 that were scanned; 1,755 representatives have truncated folder listings and 10 have none (V10). A file that cannot be read cannot show a signal | Construct / conclusion | Unread inputs are counted, never treated as clean (DR-04); script results are reported with and without the truncated-listing skills and described as lower bounds | `results/scripts_summary.csv` | Active: P-01, accepted (lower bound) |

## Internal validity (could something other than our variables explain the result?)

| ID | Threat | Applies if we choose | Mitigation | Owner | Status |
|---|---|---|---|---|---|
| I1 | Confounding by repository popularity: stars, age, and activity correlate with almost every artifact property (reuse, edits, staleness) | Any question comparing groups (Q1, Q2, Q3, Q7, Q8, Q13, Q15) | Control for log stars in the NB2 model; see P3 | Jerad Dunne | Active: P-01, mitigation planned |
| I2 | Time-window censoring: artifacts created near the July 2026 snapshot have had less time to be copied, edited, or abandoned | Any lifecycle, churn, survival, or abandonment measure (Q1, Q3, Q10, Q14) | Reach (copies) is right-censored at the snapshot; history exists only for a subset, so no age control is possible for most contents. Stated as a limitation; if an age proxy is added later, rerun RQ2 with it | Jerad Dunne | Active: P-01, accepted |
| I3 | Commit history follows the file's current path in GitSkills: `first_commit_at` dates a rename, `commit_count` covers only the current path (NB-Q06) | GitSkills lifecycle, edit counts, or propagation timelines (Q1, Q2, Q3, Q14) | RQ3 ordering treats first-commit dates as lower bounds; see P5 | Jerad Dunne | Active: P-01, accepted |
| I4 | Which rows carry history in GitSkills: every standard-location skill plus a size-stratified sample of the rest (`history_fetched`); in the sample, 3,010 of 13,000 representatives, about 11% of non-canonical ones (V11) | Any analysis using GitSkills commit fields | Ordered pairs are counted and split by location (RR-03); see P5 | Jerad Dunne | Active: P-01, accepted |
| I5 | SpecMine commit histories can be truncated or errored (`commit_history_status`) | SpecMine lifecycle or traceability timing (Q9, Q10, Q12, Q14) | Not used | | Not applicable (P-01 uses GitSkills only) |

## Construct validity (do our measures capture what we claim?)

| ID | Threat | Applies if we choose | Mitigation | Owner | Status |
|---|---|---|---|---|---|
| C1 | Quality proxy is not quality: copy count, edit count, or survival may reflect visibility or templating rather than usefulness | Q2, Q8, Q15 | P-01 uses copies as reach, not as quality | | Not applicable |
| C2 | Similarity threshold defines "reuse" or "boilerplate": different thresholds give different populations | Q1, Q11 | Threshold sweep 0.3 to 0.8 (`results/rq3_threshold_sweep.csv`); see P4 | Jerad Dunne | Active: P-01, mitigation planned |
| C3 | "Stale", "abandoned", "complete", "risky", and "script" are operational definitions we invent. No authoritative source defines what makes a skill instruction risky or what counts as a script (NB-Q14); the dataset's `has_scripts` and P-01's script extensions disagree for 57 representatives (V18) | Q3, Q4, Q7, Q10 | Both are stated as the team's constructs (RR-01): "risky" in `docs/research/THREAT_MODEL.md` and the rule file, "script" as `skill_risk.SCRIPT_EXTENSIONS`; validated against labels with the agreement design in P6; the report says which definition each number uses | Jerad Dunne | Active: P-01, mitigation planned |
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
| N5 | Small manual validation sample gives wide uncertainty on precision and agreement | Any validated classifier or detector | Stratified sample of about 150; precision with Wilson intervals; agreement as in P6 (inter-rater for drift, intra-rater for lineage and signals) | Jerad Dunne | Active: P-01, mitigation planned |

## Reproducibility validity (can someone else get the same result?)

| ID | Threat | Applies if we choose | Mitigation | Owner | Status |
|---|---|---|---|---|---|
| R1 | Dataset version drift: Zenodo and Hugging Face releases may be updated after we download | All | `data/samples/MANIFEST.json` records sha256 and upstream commit; `results/ANALYSIS_MANIFEST.json` records the database hash, rule file hash, and package versions for every run | Jerad Dunne | Active: P-01, mitigated |
| R2 | Missing or oversized content: GitSkills `content_fetched` leaves rows without text, and `content_sha_ok` may mark content that changed before fetch and was not recovered (NB-Q05a) | Any text analysis | Excluded rows counted in `results/population_flow.csv`, including the step `excluded_unrecovered_content` (0 in the sample); unread bundled files in P10 | Jerad Dunne | Active: P-01, mitigated |
| R3 | Non-deterministic steps (random sampling, model training, unordered SQL results) change outputs between runs | Any sampling or modeling step | Bootstrap and validation sampling use seed 580; SQL ordered by `file_sha`; seed recorded in the manifest | Jerad Dunne | Active: P-01, mitigated |
| R4 | Environment differences (Python, pandas, scipy, statsmodels versions) change results or break the pipeline | All | Versions recorded in `results/ANALYSIS_MANIFEST.json`; offline tests; fresh-clone gemba walk each sprint; CI once workflows are enabled | Jerad Dunne | Active: P-01, mitigation planned |
| R5 | Symlink skills in GitSkills contain a path instead of instructions | Any GitSkills text analysis | Excluded by `skill_risk.is_symlink_stub`; count reported in `results/population_flow.csv` | Jerad Dunne | Active: P-01, mitigated |
| R6 | Safety: bundled scripts in GitSkills may be malicious; running them would be both a safety and an integrity risk | Q4 and any analysis of `artifact_siblings` | Static text analysis only; nothing is executed, imported, or fetched (loader and scanner docstrings, `data/README.md`) | Jerad Dunne | Active: P-01, mitigated |

## Ethics and responsible use

| ID | Threat | Mitigation | Status |
|---|---|---|---|
| X1 | Deanonymization of GitSkills author codes | Never attempt re-identification; aggregate reporting; no repository or account names in `results/` (ER-02 scan). The sources disagree on how names in commit-message trailers were anonymised (the GitSkills preprint says keyed codes, the dataset card and sample README say a fixed marker); the data settles it (V15: fixed markers, no codes), and the report's data section says so | Active: P-01, mitigated |
| X2 | License compliance when quoting skill content in the report | Quote minimally and only as needed for false-positive discussion; no runnable payloads; respect the repository license | Active: P-01, mitigation planned |
| X3 | AI-generated analysis or text presented without verification | Every AI-assisted artifact is logged in `ai-use-log.md` and reviewed by a member other than the author before merge | Active: P-01, mitigation planned |
| X4 | Reporting suspected malicious skills could harm maintainers or spread payloads | Report categories and rates only; if something appears actively malicious, stop and raise it with the instructor before any further step | Active: P-01, mitigation planned |

## Change log

| Date | Sprint | Change | By |
|---|---|---|---|
| 2026-09-13 | Formation | Initial register from the dataset documentation and the assignment | Group 9 |
| 2026-09-14 | Formation | Research question fixed as P-01; rows marked Active or Not applicable; P-01 threats P1 to P8 and X4 added; mitigations point to `python -m msr_pipeline analyze` outputs | Jerad Dunne |
| 2026-09-15 | Formation | Group reinstated (ADR-0006): P6 rewritten for rater disagreement and independence with a teammate second rater; C3 and N5 now cite inter-rater kappa; X3 requires review by another member; row owners to be reassigned at Sprint 1 planning | Jerad Dunne |
| 2026-09-23 | Sprint 1 | Interview findings folded in (#60): P5, I3, I4 cite NB-Q06 and V11 and the RR-03 location split; P6, N5 follow D-022 (intra-rater agreement for lineage and signals); C3 adds "script" and NB-Q14; new P9 (reach is not use, NB-Q15) and P10 (unread bundled files, DR-04); R2 adds unrecovered content; X1 notes the anonymisation source conflict (V15) | Jerad Dunne, drafted with Claude Code |

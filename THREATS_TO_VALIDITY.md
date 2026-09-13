# Threats to validity

How to use: this is a living register, required by the assignment. Rows marked "applies if we choose ..." are pre-filled from the known limitations of the two challenge datasets; delete the rows that do not apply once the research question is fixed, and add project-specific rows. Update the Status column at every sprint review (Sprint 1: identified; Sprint 2: mitigation designed; Sprint 3: mitigated, accepted, or open). The final report's threats section addresses, at minimum, dataset bias, measurement error, confounding, missing data, reproducibility, and generalizability.

Status values: identified, mitigation planned, mitigated, accepted (with reason), open. Question numbers (Q1 to Q15) refer to the assignment's proposed research questions.

## Internal validity (could something other than our variables explain the result?)

| ID | Threat | Applies if we choose | Mitigation | Owner | Status |
|---|---|---|---|---|---|
| I1 | Confounding by repository popularity: stars, age, and activity correlate with almost every artifact property (reuse, edits, staleness) | Any question comparing groups (Q1, Q2, Q3, Q7, Q8, Q13, Q15) | Stratify or control for stars and repository age; report results within strata | | identified |
| I2 | Time-window censoring: artifacts created near the July 2026 snapshot have had less time to be copied, edited, or abandoned | Any lifecycle, churn, survival, or abandonment measure (Q1, Q3, Q10, Q14) | Restrict to artifacts older than a minimum age, or use survival methods that handle censoring; state the cutoff | | identified |
| I3 | Commit history follows the file's current path in GitSkills: `first_commit_at` dates a rename, `commit_count` covers only the current path | GitSkills lifecycle, edit counts, or propagation timelines (Q1, Q2, Q3, Q14) | Treat first-commit dates as lower bounds; flag files whose first commit is far later than repository creation | | identified |
| I4 | Which rows carry history in GitSkills: every standard-location skill plus a size-stratified sample of the rest (`history_fetched`) | Any analysis using GitSkills commit fields | Filter on `history_fetched = 1` and report how many rows are excluded | | identified |
| I5 | SpecMine commit histories can be truncated or errored (`commit_history_status`) | SpecMine lifecycle or traceability timing (Q9, Q10, Q12, Q14) | Exclude or separately report rows with status other than done; test sensitivity | | identified |

## Construct validity (do our measures capture what we claim?)

| ID | Threat | Applies if we choose | Mitigation | Owner | Status |
|---|---|---|---|---|---|
| C1 | Quality proxy is not quality: copy count, edit count, or survival may reflect visibility or templating rather than usefulness | Q2, Q8, Q15 | Define the proxy before analysis, justify it, and compare at least two proxies | | identified |
| C2 | Similarity threshold defines "reuse" or "boilerplate": different thresholds give different populations | Q1, Q11 | Report results at several thresholds; manually validate matches near the threshold | | identified |
| C3 | "Stale", "abandoned", "complete", and "risky" are operational definitions we invent | Q3, Q4, Q7, Q10 | Write the definition first, validate a labeled sample by two annotators, report agreement (kappa) | | identified |
| C4 | Authorship signals are heuristics, not ground truth; GitSkills author identities are one-way codes, bots keep logins | Q6, Q12 | Frame results as signals; never claim authorship; use bot logins and `author_type` only as partial evidence | | identified |
| C5 | Tool attribution in SpecMine is by path fingerprint, not by verified tool use | Any SpecMine tool-family comparison (Q5, Q11, Q13) | State the attribution method; spot-check a sample of attributions by hand | | identified |
| C6 | Text metrics (readability, length, headings) on Markdown may be distorted by code fences, front matter, and non-English content | Q2, Q5, Q11 | Strip front matter and code fences before measuring; report the `lang` distribution; exclude or separate non-English | | identified |

## External validity (does the result generalize beyond our sample?)

| ID | Threat | Applies if we choose | Mitigation | Owner | Status |
|---|---|---|---|---|---|
| E1 | GitHub code search indexes default branches only, files under 384 KB, recently active repositories with fewer than 500,000 files, and forks only when more starred than the parent: GitSkills is a lower bound on the population | Any GitSkills question | State the population as "skills discoverable by GitHub code search in July 2026"; do not generalize to all skills | | identified |
| E2 | The GitSkills sample is the 13,000 lowest content hashes: uniform in practice but only about 0.7% of distinct contents | Any GitSkills question run on the sample | Report the sample fraction; check that key distributions (location class, stars, language) match the published full-dataset figures | | identified |
| E3 | The SpecMine sample of 500 repositories is deliberately non-representative: 61% of repos have at least 100 stars versus 1.3% in the full corpus; 97.5% of specs were first committed in 2026 versus 92% | Any SpecMine question run on the sample | State this explicitly; if feasible, replicate one result on a random draw from the full Parquet release on Hugging Face | | identified |
| E4 | Point-in-time snapshot (July 2026): the formats are young and adoption is still changing quickly | Any adoption or convergence question (Q5) | Frame findings as a snapshot; avoid trend claims beyond the observed window | | identified |
| E5 | Pre-format files: lowercase `skill.md` and similar names from as early as 2014 match the GitSkills filename query | Any GitSkills population definition | Filter by `frontmatter_valid`, `location_class`, or first-commit date after October 2025, and report the effect | | identified |
| E6 | Joining GitSkills and SpecMine on repository names covers only the intersection, which is small and biased toward active repositories | Q13, Q14 | Report the intersection size and compare joined repos to each parent population | | identified |

## Conclusion validity (are the statistics and inferences sound?)

| ID | Threat | Applies if we choose | Mitigation | Owner | Status |
|---|---|---|---|---|---|
| N1 | Verbatim duplicates (50.5% of GitSkills occurrences) inflate counts and break independence assumptions | Any GitSkills count or correlation | Analyze at the distinct-content level (`dedup_primary = 1`) unless copies are the unit of analysis | | identified |
| N2 | Heavy-tailed distributions (copies, stars, sizes) make means misleading | Any quantitative comparison | Use medians, quantiles, log scales, and non-parametric tests; show distributions | | identified |
| N3 | Multiple comparisons across many features or tool families inflate false positives | Q2, Q5, Q8, Q15 | Pre-register the primary comparison; adjust p-values or report effect sizes with intervals | | identified |
| N4 | Correlation presented as causation | Q2, Q8, Q15 | Separate observation from interpretation; name confounders; test the competing explanation named in the report | | identified |
| N5 | Small manual validation sample gives wide uncertainty on precision and agreement | Any validated classifier or detector | Size the sample before labeling; report confidence intervals; two annotators with kappa | | identified |

## Reproducibility validity (can someone else get the same result?)

| ID | Threat | Applies if we choose | Mitigation | Owner | Status |
|---|---|---|---|---|---|
| R1 | Dataset version drift: Zenodo and Hugging Face releases may be updated after we download | All | Record the exact release, DOI, file checksums, and download date in `data/README.md`; pin the version in `scripts/download_samples.py` | | identified |
| R2 | Missing or oversized content: GitSkills `content_fetched`, SpecMine `content_fetch_status` (missing, toobig) leave rows without text | Any text analysis | Report counts excluded per status; never silently drop | | identified |
| R3 | Non-deterministic steps (random sampling, model training, unordered SQL results) change outputs between runs | Any sampling or modeling step | Fix random seeds; sort before sampling; record them in the config; compare two independent runs (Sprint 1 measurement-system check) | | identified |
| R4 | Environment differences (Python, pandas, pyarrow, sqlite versions) change results or break the pipeline | All | Pin versions in `requirements.txt`; CI runs the pipeline on the sample; fresh-clone gemba walk each sprint | | identified |
| R5 | Symlink skills in GitSkills contain a path instead of instructions | Any GitSkills text analysis | Detect and exclude rows whose content is a single path-like line; report the count | | identified |
| R6 | Safety: bundled scripts in GitSkills may be malicious; running them would be both a safety and an integrity risk | Q4 and any analysis of `artifact_siblings` | Static analysis only; never execute dataset scripts (assignment rule); document in the README | | identified |

## Ethics and responsible use

| ID | Threat | Mitigation | Status |
|---|---|---|---|
| X1 | Deanonymization of GitSkills author codes or linking SpecMine handles to private information | Never attempt re-identification; report aggregates; no personal data in the repository | identified |
| X2 | License compliance when quoting skill or spec content in the report | Quote minimally, cite the repository, respect the SPDX license recorded in the dataset | identified |
| X3 | AI-generated analysis or text presented without verification | Every AI-assisted artifact is logged in `ai-use-log.md` and verified by a member | identified |

## Change log

| Date | Sprint | Change | By |
|---|---|---|---|
| 2026-09-13 | Formation | Initial register from the dataset documentation and the assignment | Group 9 |

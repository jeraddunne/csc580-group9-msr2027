# Research specification: the implementation contract for P-01

Assignment Phase F. This file states what the P-01 pipeline and study **shall** do, precisely enough to test. Each requirement gives its source, rationale, acceptance test, and owner. The acceptance tests are executable where possible:

```bash
make verify-spec                             # every check except the slow one; writes results/spec_verification.csv
python scripts/verify_spec.py --determinism  # adds NFR-02: runs the analysis twice (about 8 minutes)
```

Scope is fixed by `RESEARCH_QUESTION.md` (P-01: prevalence, reach, and drift of risk-relevant capabilities in copied GitSkills skills). The requirements come from that document, the assignment and rubric, the tier-A dataset documentation, and the Phase B notebook interview (`elicitation/notebook-interview.md`), which added or changed nine of them.

## 1. How to read a requirement

| Field | Meaning |
|---|---|
| Requirement | One testable "shall" statement |
| Source | Where it comes from. `A1` to `A9` are the authoritative sources in `elicitation/notebook/SOURCE_REGISTER.md`; `NB-Q..` is an interview answer; `V..` is a data check in `elicitation/verification-checks.md`; file names are repository documents |
| Rationale | Why the study needs it |
| Acceptance test | The check that decides whether it is met. "`make verify-spec`" means `scripts/verify_spec.py` runs it |
| Owner | Who is responsible. Owners follow the current issue assignments and `docs/team/RACI.md`. A teammate named as owner is a proposal until they confirm it at the next Sprint 1 check-in |
| Status | **Implemented**, **In progress**, or **Planned**. A Planned requirement whose test fails is reported as PENDING, not FAIL |
| Trace | Code, tests, and issues |

Categories follow the assignment: research (RR), data (DR), functional (FR), nonfunctional (NFR), validation (VR), and ethical and safety (ER).

## 2. Research requirements

### RR-01 Unit of analysis and team-defined constructs

| Field | Value |
|---|---|
| Requirement | The study shall use one distinct skill content (`artifacts.file_sha`, represented by its `dedup_primary = 1` row) as the unit of analysis, treat its copies as an outcome, and state that "risk-relevant capability", "bundled script", and "variant" are P-01's operational definitions, not dataset fields. |
| Source | `RESEARCH_QUESTION.md` sec. 5; NB-Q01 (A2 App. A: "We do not assume that the representative is the original source"); NB-Q14 (no source defines a script or a risky instruction) |
| Rationale | Counting occurrences counts the same bytes many times (threat N1). Presenting our constructs as dataset facts would claim more than the data establishes. |
| Acceptance test | `results/population_flow.csv` step `all_occurrences` reports the database's distinct `file_sha` count (13,000) and occurrence count (29,786). `make verify-spec` RR-01. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `skill_risk.population_flags`, `analysis.population_flow`; `tests/test_analysis.py::test_population_flags_and_symlink_stub`; #13 |

### RR-02 Reach compared across two populations

| Field | Value |
|---|---|
| Requirement | The study shall compare `copies` and `repos` between contents with at least one high-risk signal and contents without one, reporting a two-sided Mann-Whitney U with the rank-biserial correlation, bootstrap intervals, and an NB2 incidence rate ratio with the documented controls. It shall describe reach as the spread of identical content across repositories, never as use or exposure. |
| Source | Assignment research-requirement example ("compare … across at least two repository populations"); `RESEARCH_QUESTION.md` sec. 7 H2; NB-Q07a (A9: every copy of a sampled content is kept); NB-Q15 (no source establishes that copies are loaded or run) |
| Rationale | Complete copy groups make reach measurable on the sample. Nothing records loading, so a claim about use would be unsupported. |
| Acceptance test | `rq2_mannwhitney.csv` has rows for `copies` and `repos` with both group sizes above zero and a p-value; `rq2_negbin.csv` has a `high_risk` term with an IRR (or a documented `not estimable` row); `report/draft.md` contains no "used more"-type claim. `make verify-spec` RR-02. |
| Owner | Jerad Dunne |
| Status | Implemented (numbers stay unvalidated until VR-01 and VR-02) |
| Trace | `analysis.rq2_mannwhitney`, `rq2_bootstrap`, `rq2_negbin`; `tests/test_analysis.py`; #21, #24, #27 |

### RR-03 Drift is descriptive and scoped

| Field | Value |
|---|---|
| Requirement | RQ3 shall report counts over same-name near-duplicate pairs at similarity thresholds 0.3 to 0.8, with and without template families, and the number of pairs that can be ordered by date at each threshold, broken down by location class. It shall not claim a test of direction. |
| Source | `RESEARCH_QUESTION.md` sec. 7; NB-Q06 (dates are lower bounds; history covers nearly every canonical skill but about 11% of the rest, V11); NB-Q07a (the lowest-hash sample splits variant families, V13) |
| Rationale | With fragmented families and dates concentrated in canonical skills, a direction test would be underpowered and biased toward one location. |
| Acceptance test | `rq3_threshold_sweep.csv` spans 0.3 to 0.8 with `ordered_pairs` and the per-location columns `ordered_pairs_canonical`, `ordered_pairs_mixed`, and `ordered_pairs_non_canonical`, which sum to `ordered_pairs` at every threshold; `rq3_summary.csv` has both scopes. `make verify-spec` RR-03. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `analysis.threshold_sweep`, `analysis.rq3_summary`; `tests/test_analysis.py::test_threshold_sweep_splits_ordered_pairs_by_location`; #21, #27, #59 |

### RR-04 Robustness of the headline results

| Field | Value |
|---|---|
| Requirement | The RQ1 and RQ2 headline results shall be repeated under six scenarios: main; severity cutoff 5; severity cutoff 7; front-matter-valid subset; excluding the 10 most-copied contents; excluding template families. |
| Source | `RESEARCH_QUESTION.md` sec. 7; `THREATS_TO_VALIDITY.md` P1 to P3 and E5; NB-Q02 (pre-format `skill.md` files are in the dataset) |
| Rationale | Keyword signals, popularity, templates, and pre-format files could each produce the headline result on their own. |
| Acceptance test | `sensitivity_summary.csv` has at least six scenario rows. `make verify-spec` RR-04. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `analysis.sensitivity_summary`; #28 |

## 3. Data requirements

### DR-01 Version identity of every result

| Field | Value |
|---|---|
| Requirement | Every result shall be traceable to its exact inputs: the GitSkills July 2026 snapshot, Zenodo version 1.0.0 (doi:10.5281/zenodo.21875637), computed on the official sample at `gitskills-sample` commit `fff3df9`, with the database SHA-256 recorded in `data/samples/MANIFEST.json` and `results/ANALYSIS_MANIFEST.json`, together with the rule-file SHA-256. Documentation shall not mislabel a dataset version. |
| Source | A1 Submission ("specify which snapshot/version … archived on Zenodo"); assignment data-requirement example (fields, filters, version, and sample behind each result); NB-Q03 |
| Rationale | The sample and the full release carry different identifiers, and the challenge expects dataset updates. The interview found `data/README.md` calling the SpecMine Zenodo release "v1.1" when Zenodo record 22102780 is version 1.0 (v1.1 is the GitHub sample); this change corrects it. |
| Acceptance test | The local database's SHA-256 equals both manifests; the rule file's SHA-256 equals `ANALYSIS_MANIFEST.json` (otherwise re-run `make pipeline`); the sample commit is `fff3df9`; `data/README.md` no longer labels the Zenodo SpecMine release v1.1. `make verify-spec` DR-01. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `scripts/download_samples.py`, `analysis.run_analysis` (manifest); #14 |

### DR-02 Every field, filter, and output documented

| Field | Value |
|---|---|
| Requirement | Every derived variable shall have a row in `DATA_DICTIONARY.md` Part B (source `table.column` and derivation), and every file in `results/` a row in Part C, updated in the same pull request that changes the code. |
| Source | Assignment data-requirement example; `DATA_DICTIONARY.md` conventions; `CONTRIBUTING.md` Definition of Done |
| Rationale | A number is only reproducible if its inputs and derivation are written down next to it. |
| Acceptance test | Every `results/*.csv` is named in `DATA_DICTIONARY.md` (`make verify-spec` DR-02); column agreement is FR-03. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `DATA_DICTIONARY.md` |

### DR-03 Population rules applied and counted

| Field | Value |
|---|---|
| Requirement | The pipeline shall apply inclusion rule 1 (representative text fetched and non-empty) and the symlink-stub exclusion, and write the count after each step to `population_flow.csv`. The front-matter-valid subset is a sensitivity scenario, never applied silently. |
| Source | `RESEARCH_QUESTION.md` sec. 5; NB-Q02 (A2 App. A: case variants and pre-format files are retained so researchers "can define and compare stricter inclusion criteria"); A9 Known limitations (symlinks) |
| Rationale | Each exclusion changes the denominator of every prevalence; readers must see how many contents each rule removed. |
| Acceptance test | The kept steps in `population_flow.csv` never increase, and `main_population` equals the analysis manifest's count (12,965). `make verify-spec` DR-03. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `skill_risk.is_symlink_stub`, `analysis.population_flow`; #13 |

### DR-04 Unreadable inputs counted, not dropped

| Field | Value |
|---|---|
| Requirement | The pipeline shall count, and report in `scripts_summary.csv`, the inputs it could not read: bundled script files without text (`content_fetched = 2` or null content), representatives with a truncated folder listing (`composition_truncated = 1`), representatives with no folder listing (`composition_fetched = 0`), and any representative whose `content_sha_ok` is neither 1 nor 2 (excluded). Script results shall be reported with and without the truncated subset. |
| Source | NB-Q04, NB-Q05, NB-Q05a; V07 (16,697 script-folder files carry `content_fetched = 2`, a value no source documents, and `skipped_reason` is never set), V09, V10 (1,755 representatives, 13.5%, have truncated listings) |
| Rationale | For those skills, script signals are lower bounds. A file the scanner could not read must not count as a clean file. |
| Acceptance test | `scripts_summary.csv` has the metrics `script_files_without_text`, `skills_with_truncated_listing`, `skills_without_folder_listing`, and `skills_with_unrecovered_content`, and the script totals again with the suffix `_excluding_truncated_listing`; `population_flow.csv` has the step `excluded_unrecovered_content`. `make verify-spec` DR-04. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `analysis.scripts_summary`, `skill_risk.unreadable_inputs`, `skill_risk.population_flags`; `tests/test_skill_risk.py::test_unreadable_inputs_are_counted`; #58 |

## 4. Functional requirements

### FR-01 Read-only loading

| Field | Value |
|---|---|
| Requirement | The pipeline shall open the GitSkills sample read-only through `msr_pipeline.load`, and stop with a download instruction when the sample is missing. |
| Source | NB-Q09 (A9 Quick start: "No server, no credentials; any SQLite client works"); `data/README.md` |
| Rationale | Read-only access protects the pinned input; a clear error replaces a stack trace for new members. |
| Acceptance test | `tests/test_load.py::test_query_gitskills` and `::test_missing_gitskills_raises_helpful_error` pass. `make verify-spec` FR-01. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `load.query_gitskills`, `load.load_gitskills`; #15 |

### FR-02 Reviewable rule file

| Field | Value |
|---|---|
| Requirement | Detection rules shall live in `rules/skill_risk_rules.yaml`, each with a stable id, category, severity from 1 to 10, patterns, status, source, and match and no-match examples. Only active rules run, and every example shall behave as stated. |
| Source | Rubric question 4 required component (rule-based scanner); NB-Q14 (no source defines "risky", so the rule file is the definition) |
| Rationale | A reviewer can read, challenge, and change a rule without reading code, and a changed rule cannot silently break its own examples. |
| Acceptance test | `tests/test_skill_risk.py::test_rule_examples` and `::test_rule_file_is_consistent` pass. `make verify-spec` FR-02. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `skill_risk.load_rules`, `rules_from_dict`; #15, #22 |

### FR-03 The pipeline writes the analysis tables

| Field | Value |
|---|---|
| Requirement | `make pipeline` shall scan every main-population representative and write the outputs listed in `results/ANALYSIS_MANIFEST.json` (14 CSV tables and 3 figures), each non-empty and with exactly the columns documented in `DATA_DICTIONARY.md` Part C. |
| Source | Assignment Phase F example (FR-03 with `make extract-structure`); README "Execution"; #15 |
| Rationale | The report may cite only numbers the pipeline regenerates, and readers rely on the data dictionary to interpret them. |
| Acceptance test | Given the pinned sample and the environment described in the README, the command `make pipeline` completes without manual edits and produces every listed output, non-empty, with the documented columns. `make verify-spec` FR-03 compares every output with Part C. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `analysis.run_analysis`; `tests/test_analysis.py::test_cli_analyze_writes_outputs` |

### FR-04 Bundled scripts scanned as text

| Field | Value |
|---|---|
| Requirement | The scanner shall apply the same rules to the text of bundled files whose names end in a P-01 script extension (`skill_risk.SCRIPT_EXTENSIONS`), for representatives only, and summarise the results in `scripts_summary.csv`. |
| Source | Rubric question 4 ("scripts"); NB-Q04 (folders are recorded for the representative only); NB-Q14 and V18 (`has_scripts` is undocumented and differs from P-01's rule for 57 skills) |
| Rationale | Instructions can defer the risky step to a bundled script, so scanning SKILL.md alone would miss it. |
| Acceptance test | `tests/test_skill_risk.py::test_scan_siblings_only_scripts` passes and `scripts_summary.csv` reports more than zero script files scanned. `make verify-spec` FR-04. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `skill_risk.scan_siblings`, `analysis.scripts_summary`; #21 |

### FR-05 Validation scoring

| Field | Value |
|---|---|
| Requirement | `python scripts/annotation_kit.py score` shall compute per-rule and per-category precision with Wilson 95% intervals, a recall estimate from the no-signal stratum, and Cohen's kappa between raters, and `import` shall refuse label files that break guideline 1.2 (a written reason for judgement-call labels). |
| Source | NB-Q10; `docs/validation/ANNOTATION_GUIDELINE.md`; PR #54 |
| Rationale | Validation numbers must come from a tested command, not a spreadsheet. |
| Acceptance test | `tests/test_validation.py::test_kit_end_to_end`, `::test_precision_by_rule_and_category`, and `::test_cohen_kappa_textbook_example` pass. `make verify-spec` FR-05. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `validation.py`, `scripts/annotation_kit.py`; #23 |

### FR-06 Variant linking

| Field | Value |
|---|---|
| Requirement | The pipeline shall pair representatives that share a lower-cased front-matter name and have word 5-shingle Jaccard similarity at or above the threshold, order a pair only when both variants have a `first_commit_at` date (older = a), and record the high-risk categories found only in a or only in b. |
| Source | NB-Q08 (the sources link byte-identical copies only; near-duplicate linking is ours to define); NB-Q06 (a date after a rename marks the rename) |
| Rationale | RQ3 needs a documented, testable notion of "the same skill, modified". |
| Acceptance test | `tests/test_skill_risk.py::test_family_pairs_direction_and_threshold` and `tests/test_analysis.py::test_threshold_sweep_is_monotone_and_counts_direction` pass. `make verify-spec` FR-06. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `skill_risk.family_pairs`, `shingles`, `jaccard`; #21 |

### FR-07 Elicitation notebook

| Field | Value |
|---|---|
| Requirement | `python -m msr_pipeline elicit` shall answer only from the pinned source pack, within the question's scope, quoting passages word for word with source, section or page, and line, and listing the question terms no passage contains. |
| Source | Assignment Phase B ("a bounded domain-information source, not … an oracle") |
| Rationale | Elicited facts must be traceable to a source before they become requirements. |
| Acceptance test | `tests/test_elicitation.py::test_scopes_restrict_tiers_and_datasets`, `::test_transcript_has_provenance_and_locators`, and `::test_interview_record_quotes_every_question_word_for_word` pass. `make verify-spec` FR-07. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `elicitation.py`, `scripts/build_notebook_sources.py`, `notebooks/01_elicitation_notebook.ipynb` |

## 5. Nonfunctional requirements

### NFR-01 Reproducible from a clean environment

| Field | Value |
|---|---|
| Requirement | From a fresh clone, `make setup && make data && make pipeline` shall complete without manual edits on Windows (Git Bash), macOS, or Linux with Python 3.11 or newer. Every documented install path (`pip install -e ".[dev]"` and `pip install -r requirements.txt`) shall admit the package versions that produced the committed results. |
| Source | Assignment nonfunctional example ("run from a clean environment"); A1 Open Science Policy (reproduction instructions); `THREATS_TO_VALIDITY.md` R4 |
| Rationale | A reviewer must be able to reproduce the results from the README alone. The verifier found `requirements.txt` capping `pandas<3` and `pyarrow<21` while the committed results were produced with pandas 3.0.5 (and CI installs pyarrow 25). This change corrects the bounds. |
| Acceptance test | Automated: the bounds in `requirements.txt` admit the versions recorded in `ANALYSIS_MANIFEST.json` and those CI installs (`make verify-spec` NFR-01). Manual: a member who did not write the README runs the commands on their own machine and records the row counts and one statistic (Sprint 1 item S1-10). |
| Owner | Scrum Master (Sprint 1: Leticia Aderhold, proposed) with a non-author member, per `docs/team/RACI.md` |
| Status | Implemented (the manual run, S1-10, is still open) |
| Trace | `Makefile`, `requirements.txt`, `pyproject.toml`; #19 |

### NFR-02 Deterministic outputs

| Field | Value |
|---|---|
| Requirement | Two runs of the analysis on the pinned sample, rules, and seed (580) shall produce byte-identical CSV outputs, and the committed results shall equal a fresh run. |
| Source | Assignment nonfunctional example ("deterministic outputs for the pinned sample"); `THREATS_TO_VALIDITY.md` R3 |
| Rationale | Non-determinism would make every reported number unverifiable. |
| Acceptance test | `python scripts/verify_spec.py --determinism` runs the analysis twice into temporary folders and compares the SHA-256 of every CSV with each other and with `results/`. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `analysis.run_analysis` (seeded bootstrap, SQL ordered by `file_sha`) |

### NFR-03 Offline tests on every pull request

| Field | Value |
|---|---|
| Requirement | `make test` shall pass without network access or downloaded data, and CI shall run lint and tests on every pull request. |
| Source | `CONTRIBUTING.md`; `PROJECT_PLAN.md` sec. 8 |
| Rationale | Reviewers need a fast signal that a change did not break parsing, matching, or statistics. |
| Acceptance test | `python -m pytest tests` passes (`make verify-spec` NFR-03) and CI is green on the pull request. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `tests/`, `.github/workflows/ci.yml` |

### NFR-04 Scale

| Field | Value |
|---|---|
| Requirement | The sample analysis shall finish within 15 minutes on a student laptop. Any pass over the full dataset (a 44,388,249,600-byte SQLite file) shall stream tables with filters (the Parquet mirror or DuckDB) instead of loading them whole, and requires an ADR first. |
| Source | NB-Q09 (A6 Parquet mirror; A1 How to Participate); A4 file size; `PROJECT_PLAN.md` sec. 2 |
| Rationale | Members work on laptops; the full release does not fit in memory. |
| Acceptance test | `runtime_seconds` in `ANALYSIS_MANIFEST.json` is under 900 (`make verify-spec` NFR-04); a full-dataset pass has a merged ADR (Sprint 1 item S1-13). |
| Owner | Jerad Dunne |
| Status | Implemented for the sample |
| Trace | `analysis.run_analysis`; S1-13 |

### NFR-05 Change control of this specification

| Field | Value |
|---|---|
| Requirement | Any change to the research question, scope, dataset, operational definitions, rules, or an acceptance test in this file shall start from a decision issue, be recorded in section 9 of this file and, for a scope change, an ADR, and reach `main` through a reviewed pull request with green CI. |
| Source | NB-Q11a (`PROJECT_PLAN.md` sec. 11; `CONTRIBUTING.md`) |
| Rationale | The contract is only useful if it changes deliberately and visibly. |
| Acceptance test | Manual, at each sprint review: every merged pull request that edits this file links an issue and appears in section 9. |
| Owner | Product Owner of the sprint (Sprint 1: Jerad Dunne) |
| Status | Implemented |
| Trace | section 9; `docs/workspace/DECISION_LOG.md` |

## 6. Validation requirements

### VR-01 Rule precision from a labelled sample

| Field | Value |
|---|---|
| Requirement | The precision of each active high-risk rule and category shall be estimated from the stratified validation sample (147 signal items and 40 no-signal items, seed 580), labelled under `docs/validation/ANNOTATION_GUIDELINE.md` as risky in context, benign in context, or not present, and reported with Wilson 95% intervals. A rule's precision is reported only once validated, and H1 is judged from it. |
| Source | Assignment validation example ("manually checked against an agreed sample and report precision, recall, agreement"); `RESEARCH_QUESTION.md` sec. 7 H1 and sec. 8; NB-Q10 |
| Rationale | A keyword match is not a capability (threat P1); without measured precision, prevalence numbers cannot be interpreted. |
| Acceptance test | `annotation_kit.py score` reports a precision row with an interval for every active high-risk rule in the sample. `make verify-spec` VR-01 reports BLOCKED until the round 1 signal labels are committed. |
| Owner | Jerad Dunne (primary rater `jd`) |
| Status | In progress (round 1 labelling due 2026-10-16) |
| Trace | `data/annotations/samples/`; `docs/validation/`; #23 |

### VR-02 Rater agreement for every label kind

| Field | Value |
|---|---|
| Requirement | Agreement shall be reported for every label kind. Drift: a teammate (`la`) labels round 1 independently under the blindness rule, and inter-rater Cohen's kappa is reported. Lineage and signals, which no teammate claimed (D-022): the primary rater labels the kit's 30% intra-rater subset again in round 2, at least 14 days after round 1 and without looking at it, and intra-rater kappa is reported and labelled as such. LLM labels, if any, are reported separately under an `llm-` id and never counted as human agreement. |
| Source | NB-Q10 (`TEAM_CHARTER.md` sec. 9); `THREATS_TO_VALIDITY.md` P6 |
| Rationale | One rater's labels measure one person's judgement, not the rule. Intra-rater kappa shows consistency, not that a second person reads the guideline the same way; the report states this limitation for lineage and signals. |
| Acceptance test | Label files exist for drift from `la` (round 1) and for lineage and signals from `jd` (round 2), and `score` reports kappa for each kind. `make verify-spec` VR-02. |
| Owner | Leticia Aderhold (`la`, drift) and Jerad Dunne (`jd`, lineage and signals); accountable: Jerad Dunne |
| Status | In progress (round 1 due 2026-10-16) |
| Trace | `validation.agreement`, `cohen_kappa`; #53; D-022 |

### VR-03 Lineage and drift validation

| Field | Value |
|---|---|
| Requirement | The 58 sampled lineage pairs and 18 drift pairs shall be labelled, with agreement as in VR-02 (drift by two raters, lineage by the primary rater twice), lineage precision shall be reported, and every differing pair at threshold 0.5 shall be checked by hand. |
| Source | `THREATS_TO_VALIDITY.md` P4; NB-Q08 (lineage is the team's construct) |
| Rationale | Name plus similarity can pair unrelated skills with generic names. |
| Acceptance test | Drift labels from `jd` and `la`; lineage labels from `jd` in rounds 1 and 2; `score` reports lineage precision and the drift distribution. `make verify-spec` VR-03. |
| Owner | Jerad Dunne (lineage), Leticia Aderhold (drift second rater); accountable: Jerad Dunne |
| Status | In progress (round 1 due 2026-10-16) |
| Trace | `validation.lineage_precision`, `drift_distribution`; #23 |

### VR-04 Elicited facts verified

| Field | Value |
|---|---|
| Requirement | Every important notebook answer shall carry a verification status (verified, partly verified, contradicted, or unverified) with the source locator or data check behind it. An answer without a citation is marked unverified and investigated independently. |
| Source | Assignment Phase B |
| Rationale | Requirements must not rest on unverified notebook output. The Google Notebook answers in prose and can overstate a source (five such cases were found), so its answers are verified the same way as the search notebook's. |
| Acceptance test | Every `NB-Q` block in `elicitation/google-notebook-interview.md` and `elicitation/notebook-interview.md` has a verification status (`make verify-spec` VR-04); the data checks regenerate with `python scripts/check_interview_claims.py`, and each Google answer carries the SHA-256 prefix the page reported (`elicitation/google-notebook/answers.json`). |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `elicitation/` |

## 7. Ethical and safety requirements

### ER-01 Licensing and quoting

| Field | Value |
|---|---|
| Requirement | The report shall quote skill text only in short excerpts needed for the false-positive discussion, never runnable payloads, and only from repositories whose license permits reuse; otherwise it describes the text. Dataset metadata is used under CC-BY-4.0 with attribution. |
| Source | A6 License (NB-Q13); V17 (7,734 of 13,000 representatives, 59.5%, come from repositories with no license or NOASSERTION); `THREATS_TO_VALIDITY.md` X2 |
| Rationale | Skill text keeps its origin repository's license; most of it has none. |
| Acceptance test | Manual, at the Sprint 3 review: the reviewer checks the repository license of every excerpt in the report. |
| Owner | Jerad Dunne (Product Owner for the report) |
| Status | Planned (applies once the report quotes examples) |
| Trace | `report/draft.md` |

### ER-02 No personal data, no deanonymisation

| Field | Value |
|---|---|
| Requirement | No generated output (`results/`, the elicitation data checks, the report) shall contain a repository name, account name, author code, or bot login from the dataset, and no step shall attempt to reverse or link author codes. |
| Source | A1 FAQ Q1 ("The share or use of personally identifiable information (PII) is strictly prohibited"); assignment ethical example ("shall not expose PII … or infer authorship as fact from weak signals"); NB-Q12 |
| Rationale | Author codes are stable across the dataset, so publishing them, or the repositories they sit in, invites linkage. |
| Acceptance test | `make verify-spec` ER-02 scans those files against every repository name, author code, and bot login in the sample: zero matches. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | all writers in `analysis.py` (aggregate outputs only) |

### ER-03 Never execute dataset content

| Field | Value |
|---|---|
| Requirement | No code path shall execute, import, evaluate, or fetch anything found in skill text or bundled files. Skills and scripts are parsed as text only. |
| Source | Rubric question 4 ("Students must not execute untrusted scripts from the dataset"); `data/README.md`; NB-Q13 (no tier-A source says running bundled scripts is safe); assignment ethical example ("execute untrusted scripts") |
| Rationale | Bundled scripts may be malicious, and running them would also contaminate the measurement. |
| Acceptance test | `make verify-spec` ER-03: a static scan of every module that reads the dataset finds no `eval`, `exec`, `subprocess`, `os.system`, import-by-name, or `pickle` call, except two allowlisted calls that never receive dataset content. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `src/msr_pipeline/`, `scripts/` |

### ER-04 Responsible reporting of risky skills

| Field | Value |
|---|---|
| Requirement | Results shall be reported as categories and rates, and a keyword match shall be called a signal, not a verdict. If a skill appears actively malicious, work on it stops and it is raised with the instructor before any further step. No individual repository is named as risky. |
| Source | `THREATS_TO_VALIDITY.md` X4; assignment ethical example ("infer … as fact from weak signals") |
| Rationale | A false accusation harms a maintainer; a published payload spreads it. |
| Acceptance test | Manual, at each sprint review. |
| Owner | Jerad Dunne |
| Status | Implemented |
| Trace | `docs/research/THREAT_MODEL.md` |

### ER-05 AI assistance disclosed and verified

| Field | Value |
|---|---|
| Requirement | Every AI-assisted artifact shall be logged in `ai-use-log.md` with the tool, purpose, location, and the human who verified it, in the same pull request. |
| Source | Rubric; `THREATS_TO_VALIDITY.md` X3 |
| Rationale | Readers must know which work was generated and who checked it. |
| Acceptance test | `ai-use-log.md` has the entry for this change (`make verify-spec` ER-05); the pull-request reviewer confirms the "Verified by" column names a human. |
| Owner | The author of each pull request |
| Status | Implemented |
| Trace | `ai-use-log.md` |

## 8. Traceability

| Requirement | Interview | Code | Tests or check | Issues |
|---|---|---|---|---|
| RR-01 | NB-Q01, NB-Q14 | `analysis.population_flow` | verify RR-01 | #13 |
| RR-02 | NB-Q07a, NB-Q15 | `analysis.rq2_*` | `test_analysis.py`; verify RR-02 | #21, #24, #27 |
| RR-03 | NB-Q06, NB-Q07a | `analysis.threshold_sweep` | verify RR-03 | #21, #27 |
| RR-04 | NB-Q02 | `analysis.sensitivity_summary` | verify RR-04 | #28 |
| DR-01 | NB-Q03 | `download_samples.py`, manifest | verify DR-01 | #14 |
| DR-02 | | `DATA_DICTIONARY.md` | verify DR-02 | #13 |
| DR-03 | NB-Q02 | `skill_risk.is_symlink_stub` | `test_population_flags_and_symlink_stub` | #13 |
| DR-04 | NB-Q04, NB-Q05, NB-Q05a | `analysis.scripts_summary` | verify DR-04 | proposed |
| FR-01 | NB-Q09 | `load.py` | `test_load.py` | #15 |
| FR-02 | NB-Q14 | `rules/skill_risk_rules.yaml` | `test_rule_examples` | #15, #22 |
| FR-03 | | `analysis.run_analysis` | verify FR-03 | #15 |
| FR-04 | NB-Q04, NB-Q14 | `skill_risk.scan_siblings` | `test_scan_siblings_only_scripts` | #21 |
| FR-05 | NB-Q10 | `validation.py` | `test_validation.py` | #23 |
| FR-06 | NB-Q06, NB-Q08 | `skill_risk.family_pairs` | `test_family_pairs_direction_and_threshold` | #21 |
| FR-07 | Phase B | `elicitation.py` | `test_elicitation.py` | |
| NFR-01 | | `requirements.txt`, `Makefile` | verify NFR-01; S1-10 | #19 |
| NFR-02 | | `analysis.run_analysis` | verify `--determinism` | |
| NFR-03 | | `tests/`, CI | verify NFR-03 | #22 |
| NFR-04 | NB-Q09 | | verify NFR-04 | S1-13 |
| NFR-05 | NB-Q11, NB-Q11a | | manual | |
| VR-01 | NB-Q10 | `annotation_kit.py` | verify VR-01 | #23 |
| VR-02 | NB-Q10 | `validation.agreement` | verify VR-02 | #53 |
| VR-03 | NB-Q08 | `validation.lineage_precision` | verify VR-03 | #23, #53 |
| VR-04 | all (both notebooks) | `elicitation/` | verify VR-04 | |
| ER-01 | NB-Q13 | | manual | #31 |
| ER-02 | NB-Q12 | aggregate writers | verify ER-02 | #31 |
| ER-03 | NB-Q13 | | verify ER-03 | |
| ER-04 | | | manual | #31 |
| ER-05 | | `ai-use-log.md` | verify ER-05 | #40 |

## 9. Verification status and change history

The latest `make verify-spec` result per requirement is in `results/spec_verification.csv`, and it is reported in the pull request that changes this file.

| Date | Change | Driven by | By |
|---|---|---|---|
| 2026-09-18 | First version: 29 requirements. From the interview: added DR-04 and the location breakdown in RR-03; sharpened RR-01, RR-02, DR-01, FR-04, FR-06, ER-01, and ER-02. Verification then corrected the SpecMine version label in `data/README.md` (DR-01) and the pandas and pyarrow bounds in `requirements.txt` (NFR-01) | Assignment Phase F; `elicitation/notebook-interview.md` | Jerad Dunne, drafted with Claude Code |
| 2026-09-23 | DR-04 implemented; its acceptance test also requires the unrecovered-content count, the script totals without truncated listings, and the population step, which the requirement already asked for. Status Planned to Implemented | #58 | Jerad Dunne, drafted with Claude Code |
| 2026-09-23 | VR-01 to VR-03: no teammate claimed lineage or signals, so those kinds use intra-rater agreement from a round 2 at least 14 days later; drift keeps inter-rater kappa with `la`. VR-02 renamed from "Independent second rater" | D-022 (#63), #53 | Jerad Dunne, drafted with Claude Code |
| 2026-09-23 | RR-03 implemented: ordered pairs split by location (both canonical, one, neither); the acceptance test names the three columns and requires them to sum to `ordered_pairs`. Status In progress to Implemented | #59 | Jerad Dunne, drafted with Claude Code |

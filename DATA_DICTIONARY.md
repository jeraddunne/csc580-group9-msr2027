# Data Dictionary

Three parts:

- **Part A** describes the source datasets as distributed (GitSkills and SpecMine).
- **Part B** defines the variables derived for the P-01 research question
  (`RESEARCH_QUESTION.md`).
- **Part C** lists the derived tables the pipeline writes to `results/`.

Every string is UTF-8; timestamps are ISO-8601 UTC unless stated. See
`data/README.md` for acquisition and provenance.

---

## Part A. Source datasets

### A.1 GitSkills (SQLite, July 2026 snapshot)

Four tables. The sample and the full dataset share the schema.

#### `artifacts` (one row per `SKILL.md` file occurrence)

| Column | Type | Meaning |
|---|---|---|
| `repo_full_name` | text | Repository `owner/name`. Part of the primary key. |
| `path` | text | File path inside the repository. Part of the primary key. |
| `filename` | text | Exact basename as returned by code search (case preserved). |
| `location_class` | text | `canonical` (`.claude/skills/<name>/SKILL.md`), `skills-dir` (under a `skills/` directory), or `other`. |
| `file_sha` | text | Git blob hash of the content. Identical hash means identical bytes; the natural key for "distinct content". |
| `discovered_at` | timestamp | When the collection run recorded the file. |
| `dedup_primary` | int (0/1) | 1 for the single representative of each distinct content. |
| `content` | text | Full file text. Representatives only. Read as data, never executed. |
| `content_fetched`, `content_sha_ok` | int | Retrieval bookkeeping; `content_sha_ok` = 1 when the bytes reproduce `file_sha`, 2 when repaired via the blob API. The preprint says the column also records the 42 representatives whose file changed before fetch and could not be recovered, but no source names that value (NB-Q05a); only 1 and 2 occur in the sample. Any other value is excluded from the main population and counted (DR-04). |
| `frontmatter_valid` | int (0/1) | Whether YAML front matter parsed. |
| `name`, `description` | text | Parsed front-matter fields. |
| `body_chars` | int | Length of the body after front matter. |
| `sibling_count`, `sibling_bytes` | int | Folder composition summary (representatives only). |
| `has_scripts`, `has_references` | int (0/1) | Whether the skill folder bundles scripts or reference docs. |
| `composition_fetched`, `composition_truncated` | int | Bookkeeping; `composition_fetched` = 0 means no folder listing (10 representatives in the sample); `composition_truncated` = 1 flags folders above the listing cap (1,755 representatives, 13.5%, V10). Bundled-script results are a lower bound for both; counted in `scripts_summary.csv` (DR-04). |
| `first_commit_at`, `last_commit_at`, `commit_count` | timestamp, timestamp, int | Commit history of the file at its **current** path (sampled rows only; a rename resets history). |
| `first_commit_author`, `last_commit_author` | text | Anonymised one-way author codes; bots keep their login. |
| `first_commit_author_type`, `last_commit_author_type` | text | `User`, `Bot`, `Organization`, or empty. |
| `first_commit_message`, `last_commit_message` | text | Commit messages with emails and personal names masked; AI assistant names in `Co-authored-by` trailers are kept. |
| `history_fetched` | int (0/1) | Whether commit history was collected for this row. |

#### `repos` (one row per repository)

| Column | Type | Meaning |
|---|---|---|
| `full_name` | text | `owner/name`; joins to `artifacts.repo_full_name`. |
| `owner` | text | Owner login. |
| `stars`, `forks` | int | Counts at collection time. |
| `is_fork` | int (0/1) | Fork flag (forks are indexed only when more starred than the parent). |
| `language` | text | Primary language reported by GitHub; may be null. |
| `license` | text | SPDX identifier or null. |
| `description` | text | Repository description, emails masked. |
| `created_at`, `pushed_at` | timestamp | Repository timestamps. |
| `metadata_fetched` | int (0/1) | Bookkeeping. |

#### `artifact_siblings` (files bundled with a representative skill)

| Column | Type | Meaning |
|---|---|---|
| `repo_full_name`, `artifact_path` | text | Join to `artifacts` (`repo_full_name`, `path`). |
| `entry_name` | text | Name of the sibling entry. |
| `entry_type` | text | `file` or `dir`. |
| `entry_size` | int | Bytes. |
| `entry_sha` | text | Git blob hash. |
| `content` | text | Text files up to 100 KB; null otherwise. Data only. |
| `content_fetched` | int (0/1/2) | Bookkeeping. 1 = text fetched. **2 is undocumented**: it marks 16,697 files with no text (V07), which the scanner cannot read; they are counted as `script_files_without_text` in `scripts_summary.csv`, never treated as clean (DR-04). |
| `skipped_reason` | text | Documented as `binary`, oversize, or folder above the listing cap, but **never set** in the sample (V07); use `content_fetched` and `artifacts.composition_truncated` instead. |

#### `mining_runs` (collection provenance)

One row per collection run: query, start and end timestamps, result count.

Known limits: GitHub code search indexes default branches only, files under
384 KB, recently active repositories with fewer than 500,000 files, and forks
only when more starred than the parent. The dataset is a lower bound on the
population. A small class of skills are symlinks whose content is the target path.

### A.2 SpecMine v1.1 (Parquet, July 2026 snapshot)

Thirteen Parquet tables plus two JSONL text files. The upstream
[`DATA_DICTIONARY.md`](https://github.com/shyamagarwal13/specmine-official/blob/HEAD/DATA_DICTIONARY.md)
(copied into `data/samples/specmine/` by the download script) lists every column;
the tables and columns below are the ones the pipeline uses.

#### `spec_files` (124 columns; one row per broad-census spec file)

| Column | Type | Meaning |
|---|---|---|
| `file_url_sha16` | char(16) | Primary key: digest of the file's GitHub blob URL. Joins to features, links, and text. |
| `file_url`, `file_path`, `file_name`, `file_sha` | text | Location and blob hash. |
| `repo_name` | text | `owner/repo`; join key to every other layer. |
| `owner_login`, `owner_type` | text | Owner login; `User` or `Organization`. |
| `repo_stars`, `repo_forks`, `repo_watchers`, `repo_open_issues`, `repo_size_kb` | int | Repository counts at capture. |
| `repo_language`, `repo_license_spdx_id`, `repo_topics` | text | Language, license, topics. |
| `repo_created_at`, `repo_updated_at`, `repo_pushed_at` | text | Repository timestamps. |
| `file_first_commit_at`, `file_last_commit_at` | text | First and most recent commit touching the file (adoption and activity signals). |
| `file_first_commit_author_login`, `file_last_commit_author_login`, `*_author_type` | text | Public handles and account types. |
| `file_total_commits` | int | Commits touching the file up to the crawl cutoff. |
| `commit_history_status` | text | `done`, `empty`, `error`, or `truncated`. |
| `spec_tool` | text | Attributed SDD tool or path bucket (17 named tools plus 4 path categories). |
| `spec_role` | text | Lifecycle role: `living`, `change_proposal`, `archived`, `feature`, `config`, `na`. |
| `file_content_sha`, `file_content_bytes`, `content_fetch_status` | text, int, text | Content hash (dedup key), size, and `done`/`missing`/`toobig`/`error`. |
| `feature_branch` | text | The `Feature Branch:` header value when present. |
| `n_linked_prs`, `n_linked_issues`, `n_sibling_docs`, `n_code_links` | int | Rolled-up typed references from `spec_links`. |
| `has_tasks`, `has_plan`, `has_proposal`, `has_design` | int (0/1) | Whether companion documents exist. |
| `not_spec_filter` | int | 0 for kept specs (only kept rows ship). |

#### `spec_content_features` (39 parsed features per spec)

| Column | Type | Meaning |
|---|---|---|
| `file_url_sha16` | char(16) | Join to `spec_files`. |
| `n_bytes`, `n_lines`, `n_words` | int | Size. |
| `n_headings`, `max_heading_depth` | int | Structure. |
| `n_code_fences`, `n_mermaid`, `n_tables`, `n_links`, `n_images` | int | Embedded elements. |
| `n_list_items`, `n_checkboxes`, `n_checked` | int | Task-list signals. |
| `n_shall`, `n_gherkin`, `n_scenario_blocks`, `n_delta_headers` | int | Requirement-language counts. |
| `n_needs_clarification`, `n_todo` | int | Open-work markers. |
| `has_ears`, `has_gherkin`, `has_user_story` | int (0/1) | Requirement form. |
| `has_requirements`, `has_acceptance_criteria`, `has_user_scenarios`, `has_non_goals`, `has_out_of_scope`, `has_overview`, `has_success_criteria`, `has_edge_cases`, `has_open_questions`, `has_dependencies`, `has_purpose`, `has_mandatory_marker` | int (0/1) | Section presence flags. |
| `is_tiny`, `has_unfilled_placeholder`, `has_lorem` | int (0/1) | Quality and abandonment signals. |
| `lang` | text | Detected language code. |
| `content_family` | text | Coarse content family. |

#### `spec_links` (typed spec-to-artifact references)

| Column | Type | Meaning |
|---|---|---|
| `spec_url_sha16` | char(16) | The spec the reference belongs to (FK to `spec_files`). |
| `rel` | text | Target type: `code`, `sibling`, `pr`, `ref`, `branch`, `issue`, `anchor`. |
| `target` | text | Referenced value (path, PR number, issue, branch, ...). |
| `provenance` | text | How it was found: `tasks`, `tree`, `commit_msg`, `branch_header`, `content`. |

#### `spec_file_commits` (per-file commit history; `--all-specmine`)

`file_url_sha16`, `repo_name`, `file_path`, `seq_from_oldest`, `commit_sha`,
`message`, `authored_at`, `author_login`, `author_type`, `committed_at`,
`committer_login`, `parents`, `verified`.

#### `pull_requests` and `pr_files`

`pull_requests`: union of the per-tool PR tables; one row per spec-touching
pull request with `tool`, repository, number, state and timestamps, and
`touches_code` (0/1). `pr_files`: one row per changed file with `is_spec` and
`is_code` flags. The shared PR identifier column is detected at load time.

#### Kiro and OpenSpec tables

`kiro_files` (requirements/design/tasks artefacts under `.kiro/specs/`, with
`kind`, `feature`, `file_content_sha`, `file_total_commits`), `kiro_repos`
(repository metadata), `kiro_file_commits`, `kiro_content_features` (same 39
features), `openspec_artifact_files` (proposals, designs, task lists),
`openspec_code_refs` (task-to-code references), `repo_trees` (git-tree
metadata references).

#### Text files

`specs.jsonl.gz` and `kiro_specs.jsonl.gz`: one JSON object per line with
`file_url_sha16`, `repo_name`, `file_path`, `spec_tool`, `spec_role`, and
`content` (raw Markdown). Join on `file_url_sha16`.

---

## Part B. Project variables (P-01)

One row per variable used in the P-01 analysis (`python -m msr_pipeline analyze`).
Update this table in the same pull request that changes the code computing the
variable. `RESEARCH_QUESTION.md` section 6 references these rows. Threat ids
(P1 to P8, N1, R5, and so on) refer to `THREATS_TO_VALIDITY.md`.

### B.1 Unit, population, and flags

| Variable | Definition | Type | Source (table.column) | Derivation | Unit | Notes / threats |
|---|---|---|---|---|---|---|
| `file_sha` | Unit of analysis: one distinct skill content | key | `artifacts.file_sha` on the row with `dedup_primary = 1` | as distributed | n/a | Copies are an outcome, not separate units (N1) |
| `has_content` | Representative text was fetched and is not empty | boolean | `artifacts.content` | stripped content is not empty | n/a | R2 |
| `is_symlink_stub` | Content is a symlink target path, not instructions | boolean | `artifacts.content` | `skill_risk.is_symlink_stub`: a single stripped line under 200 characters, only word characters, `.`, `/`, space, or `-`, and containing `/` or ending in `.md` | n/a | R5; counts in `results/population_flow.csv` |
| `content_recovered` | Representative content matches its hash | boolean | `artifacts.content_sha_ok` | value is 1 or 2 | n/a | DR-04; counts in `results/population_flow.csv` |
| `in_main_population` | Included in the main analysis | boolean | derived | `has_content` and `content_recovered` and not `is_symlink_stub` | n/a | |
| `frontmatter_valid` | YAML front matter parsed | boolean | `artifacts.frontmatter_valid` | value equals 1 (null counts as 0) | n/a | Sensitivity subset; E5 |

### B.2 Risk signals (independent variables)

| Variable | Definition | Type | Source (table.column) | Derivation | Unit | Notes / threats |
|---|---|---|---|---|---|---|
| `rule_ids` | Active rules whose patterns match the content | list, `;`-joined | `artifacts.content`, `rules/skill_risk_rules.yaml` | `skill_risk.scan_contents` | rule ids | Keyword signal, not capability (P1) |
| `categories` | Capability categories of all matching rules | list | derived from `rule_ids` | rule category lookup | category names | Includes context categories (SHELL, severity below 6) |
| `max_severity` | Highest severity among matching rules | integer 0 to 10 | derived from `rule_ids` | maximum rule severity; 0 when no rule matches | severity score | Severity scale in `docs/research/THREAT_MODEL.md` |
| `high_risk_categories` | Categories of matching rules with severity at or above the cutoff | list | derived from `rule_ids` | cutoff 6 (main); 5 and 7 via `analysis.with_severity_cutoff` | category names | Cutoff sensitivity in `results/sensitivity_summary.csv` |
| `high_risk` | At least one high-risk category | boolean | derived | `high_risk_categories` is not empty | n/a | Primary independent variable for RQ2 |
| script `rule_ids`, `high_risk` | Same signals for bundled script files | list, boolean | `artifact_siblings.content` (files with script extensions) | `skill_risk.scan_siblings` | n/a | Text only, never executed (R6) |

### B.3 Outcomes

| Variable | Definition | Type | Source (table.column) | Derivation | Unit | Notes / threats |
|---|---|---|---|---|---|---|
| `copies` | Occurrences sharing the `file_sha` | count, at least 1 | `artifacts` | row count by `file_sha` | occurrences | RQ1 weight; RQ2 outcome; the NB2 model uses `copies - 1` (additional copies); heavy-tailed (N2) |
| `repos` | Distinct repositories holding the `file_sha` | count, at least 1 | `artifacts.repo_full_name` | distinct count by `file_sha` | repositories | RQ2 secondary outcome; repository names are never written to outputs |
| `content_share`, `occurrence_share` | Share of distinct contents or of occurrences with a signal | proportion | derived | count divided by main-population contents or occurrences | proportion | Wilson 95% interval on `content_share` |

### B.4 Controls (RQ2 model)

| Variable | Definition | Type | Source (table.column) | Derivation | Unit | Notes / threats |
|---|---|---|---|---|---|---|
| `body_chars` | Body length after front matter | integer | `artifacts.body_chars` | `log1p` in the model | characters | |
| `has_scripts` | Folder bundles scripts | boolean | `artifacts.has_scripts` | null treated as 0 | n/a | 10 nulls in the sample |
| `location_class` | Canonical, skills-dir, or other | categorical | `artifacts.location_class` | dummy variables; the most frequent class is the baseline | n/a | |
| `stars` | Stars of the representative's repository | integer | `repos.stars` joined on `artifacts.repo_full_name` | `log1p`; null treated as 0 | stars | Representative row only (P7); I1 |
| `language` | Primary language of the representative's repository | categorical | `repos.language` | top 8 languages plus `other`; empty becomes `(none)`; the most frequent is the baseline | n/a | P7 |

### B.5 Variants (RQ3)

| Variable | Definition | Type | Source (table.column) | Derivation | Unit | Notes / threats |
|---|---|---|---|---|---|---|
| `family` | Front-matter name used to group variants | text | `artifacts.name` | lower-cased and trimmed; empty names excluded | n/a | Generic names can group unrelated skills (P4) |
| `similarity` | Lineage evidence between two variants | float 0 to 1 | `artifacts.content` | Jaccard similarity of hashed word 5-shingles (`skill_risk.shingles`, `jaccard`) | n/a | Pairs computed at 0.3, reported from 0.3 to 0.8, main threshold 0.5 (C2) |
| `ordered` | Both variants have first-commit dates and they differ | boolean | `artifacts.first_commit_at` | when true, `a` is the older variant | n/a | Sparse history (P5, I3, I4) |
| `only_in_a`, `only_in_b` | High-risk categories present only in variant a or only in b | list | derived | set difference of `high_risk_categories` | category names | When ordered, `only_in_b` means added in the newer variant |
| `differs` | The two variants' high-risk categories differ | boolean | derived | | n/a | |
| `is_template_family` | Family name is in the documented template list | boolean | derived | `analysis.TEMPLATE_FAMILIES` | n/a | Template inheritance (P2) |

### B.6 Validation

| Variable | Definition | Type | Source (table.column) | Derivation | Unit | Notes / threats |
|---|---|---|---|---|---|---|
| `validation_label` | Manual label for a sampled rule match | categorical: risky in context, benign in context, not present | label files produced with the annotation kit | guideline in `docs/validation/` | n/a | Primary rater plus a teammate second rater; inter-rater kappa, intra-rater kappa optional (P6, N5) |

Conventions:

- Names are `snake_case`; booleans are prefixed `is_`/`has_`; counts `n_`; rates end in `_rate`.
- Time windows are stated explicitly (snapshot July 2026; no right-censoring adjustment unless stated).
- Every derived variable is computed by a function in `src/msr_pipeline/` with a unit test.

---

## Part C. Derived tables written by the pipeline

Produced by `python -m msr_pipeline explore` into `results/` (CSV) and `figures/` (PNG).

| File | Grain | Columns | Produced by |
|---|---|---|---|
| `gitskills_location_summary.csv` | one row per `location_class` | `location_class`, `files`, `share` | `explore.gitskills_location_summary` |
| `gitskills_copy_distribution.csv` | one row per copy count | `copies`, `distinct_contents`, `share_of_contents` | `explore.gitskills_copy_distribution` |
| `gitskills_language_summary.csv` | one row per repository language (top 15) | `language`, `skills` | `explore.gitskills_language_summary` |
| `specmine_tool_summary.csv` | one row per `spec_tool` | `spec_tool`, `specs`, `repos`, `share` | `explore.specmine_tool_summary` |
| `specmine_feature_summary.csv` | one row per `has_*` flag (plus `is_tiny`) | `feature`, `specs_with_feature`, `share` | `explore.specmine_feature_summary` |
| `specmine_pr_code_cochange.csv` | one row per PR `tool` | `tool`, `spec_prs`, `spec_and_code_prs`, `cochange_rate` | `explore.specmine_pr_code_cochange` |

### Pilot tables for proposal P-01

Produced by `python -m msr_pipeline risk-pilot` from the GitSkills sample. Signals are unvalidated keyword matches from `rules/skill_risk_rules.yaml`. Outputs contain no repository names.

| File | Grain | Columns | Produced by |
|---|---|---|---|
| `pilot_skill_risk_rules.csv` | one row per rule, plus `ANY_HIGH_RISK` | `rule_id`, `category`, `severity`, `contents`, `content_share`, `occurrences`, `occurrence_share` | `skill_risk.rule_prevalence` |
| `pilot_skill_risk_categories.csv` | one row per capability category | `category`, `max_rule_severity`, `contents`, `content_share`, `occurrences`, `occurrence_share` | `skill_risk.category_prevalence` |
| `pilot_skill_risk_reach.csv` | two rows: with and without a high-risk signal | `group`, `contents`, `occurrences`, `mean_copies`, `median_copies`, `share_copied_2plus`, `share_cross_repo`, `max_copies` | `skill_risk.reach_by_risk` |
| `pilot_skill_risk_family_summary.csv` | one row per metric | `metric`, `value` | `skill_risk.family_summary` |
| `pilot_skill_risk_family_pairs.csv` | one row per near-duplicate pair sharing a front-matter name | `family`, `file_sha_a`, `file_sha_b`, `similarity`, `ordered`, `only_in_a`, `only_in_b`, `differs` | `skill_risk.family_pairs` |
| `pilot_skill_risk_siblings_summary.csv` | one row per metric | `metric`, `value` | `skill_risk.sibling_summary` |

Definitions: `contents` counts distinct `file_sha` values; `occurrences` counts every copy; a signal is *high risk* when a matching rule has severity 6 or more. In `family_pairs`, when `ordered` is true, `a` has the older `first_commit_at`, so `only_in_b` lists high-risk categories the newer variant added. The stratified validation sample is written to `results/tmp/` and is not committed.

### P-01 research analysis tables

Produced by `python -m msr_pipeline analyze` (module `analysis`) from the GitSkills sample, on the main population unless stated. Signals are keyword matches from `rules/skill_risk_rules.yaml`; precision is established separately by validation. Outputs contain no repository or account names. `ANALYSIS_MANIFEST.json` records the run: database and rule-file hashes, seed, package versions, row counts, and runtime.

| File | Grain | Columns | Produced by |
|---|---|---|---|
| `population_flow.csv` | one row per inclusion step | `step`, `description`, `distinct_contents`, `occurrences` | `analysis.population_flow` |
| `rq1_prevalence_by_rule.csv` | one row per rule, plus `ANY_HIGH_RISK` | `rule_id`, `category`, `severity`, `contents`, `content_share`, `occurrences`, `occurrence_share`, `content_ci_low`, `content_ci_high` | `analysis.rq1_tables` |
| `rq1_prevalence_by_category.csv` | one row per capability category | `category`, `max_rule_severity`, `contents`, `content_share`, `occurrences`, `occurrence_share`, `content_ci_low`, `content_ci_high`, `high_risk_contents`, `high_risk_share`, `high_risk_ci_low`, `high_risk_ci_high`, `high_risk_occurrences`, `high_risk_occurrence_share` (high-risk rules only) | `analysis.rq1_tables` |
| `rq2_reach_summary.csv` | two rows: with and without a high-risk signal | `group`, `contents`, `occurrences`, `mean_copies`, `median_copies`, `share_copied_2plus`, `share_copied_5plus`, `share_copied_10plus`, `share_cross_repo`, `max_copies` | `analysis.rq2_reach_summary` |
| `rq2_mannwhitney.csv` | one row per outcome (`copies`, `repos`) | `outcome`, `group`, `n_group`, `n_reference`, `median_group`, `median_reference`, `mean_group`, `mean_reference`, `u_statistic`, `p_value`, `rank_biserial`, `status` | `analysis.rq2_mannwhitney` |
| `rq2_bootstrap.csv` | one row per bootstrapped difference | `metric`, `estimate`, `ci_low`, `ci_high`, `n_boot`, `seed`, `status` | `analysis.rq2_bootstrap` |
| `rq2_negbin.csv` | one row per model term (including `alpha`), or one `not estimable` row | `term`, `coef`, `irr`, `irr_ci_low`, `irr_ci_high`, `p_value`, `n`, `status`, `note` | `analysis.rq2_negbin` |
| `rq2_category_tests.csv` | one row per high-risk category | `category`, `contents`, `reference_contents`, `tested`, `mean_copies`, `reference_mean_copies`, `u_statistic`, `p_value`, `rank_biserial`, `p_holm`, `significant_holm_05` | `analysis.rq2_category_tests` |
| `rq3_threshold_sweep.csv` | one row per similarity threshold (0.3 to 0.8) | `threshold`, `lineage_pairs`, `families`, `differing_pairs`, `families_with_differences`, `ordered_pairs`, `ordered_newer_adds`, `ordered_newer_drops` | `analysis.threshold_sweep` |
| `rq3_summary.csv` | two rows: all families, excluding template families (threshold 0.5) | `scope`, `threshold`, `lineage_pairs`, `families`, `differing_pairs`, `families_with_differences`, `ordered_pairs`, `ordered_newer_adds`, `ordered_newer_drops` | `analysis.rq3_summary` |
| `rq3_lineage_pairs.csv` | one row per same-name pair with similarity of at least 0.5 | `family`, `file_sha_a`, `file_sha_b`, `similarity`, `ordered`, `only_in_a`, `only_in_b`, `differs`, `is_template_family` | `skill_risk.family_pairs`, `analysis.mark_templates` |
| `rq3_differing_pairs.csv` | lineage pairs whose high-risk categories differ | same as `rq3_lineage_pairs.csv` | `analysis.run_analysis` |
| `scripts_summary.csv` | one row per metric | `metric`, `value` (script signals: `script_files_with_text`, `script_files_with_any_signal`, `script_files_with_high_risk_signal`, `skills_with_scanned_scripts`, `skills_with_high_risk_script`, `script_files_high_risk_<CATEGORY>`; unread inputs, DR-04: `script_files_without_text` counts script-extension files with null content or `content_fetched` = 2, then `skills_with_truncated_listing`, `skills_without_folder_listing`, `skills_with_unrecovered_content`; and the five script-signal totals again with the suffix `_excluding_truncated_listing`) | `analysis.scripts_summary` |
| `sensitivity_summary.csv` | one row per scenario (main; severity cutoff 5; cutoff 7; front-matter-valid subset; excluding the 10 most-copied contents; excluding template families) | `scenario`, `contents`, `high_risk_contents`, `high_risk_share`, `share_ci_low`, `share_ci_high`, `mean_copies_high_risk`, `mean_copies_other`, `mean_copies_ratio`, `mwu_p_copies`, `rank_biserial_copies` | `analysis.sensitivity_summary` |
| `ANALYSIS_MANIFEST.json` | one object per run | `generated_at`, `command`, `seed`, `gitskills_db`, `gitskills_db_sha256_from_manifest`, `rules_file`, `rules_file_sha256`, `rules_active`, `high_risk_severity_cutoff`, `main_similarity_threshold`, `row_counts`, `versions`, `outputs`, `runtime_seconds` | `analysis.run_analysis` |

Figures: `rq1_prevalence_by_category.png` (shares with 95% Wilson intervals), `rq2_copies_by_group.png` (share copied 2, 5, and 10 or more times by group), `rq3_threshold_sweep.png` (pair counts by threshold).

Statistical definitions: Wilson score intervals at 95%; Mann-Whitney U is two-sided, with rank-biserial correlation `2U / (n1 n2) - 1`, positive when the high-risk group tends to have more copies; the bootstrap uses 2,000 independent resamples per group with seed 580 and percentile intervals; NB2 is `statsmodels` discrete `NegativeBinomial` on `copies - 1`, reported as incidence rate ratios; per-category p-values use the Holm step-down adjustment.

### Specification verification

Produced by `python scripts/verify_spec.py` (`make verify-spec`) from the acceptance tests in `RESEARCH_SPEC.md`. It holds no dataset content.

| File | Grain | Columns | Produced by |
|---|---|---|---|
| `spec_verification.csv` | one row per requirement in `RESEARCH_SPEC.md` | `requirement`, `title`, `spec_status`, `result`, `evidence`, `checked_at` | `scripts/verify_spec.py` |

Each explore CSV has a same-named PNG bar chart in `figures/`; the pilot draws `pilot_skill_risk_categories.png`. Topic-specific tables
will be added here as the analysis grows; the rule is one row in this table
per file in `results/`.

# Data Dictionary

Three parts:

- **Part A** describes the source datasets as distributed (GitSkills and SpecMine).
- **Part B** defines the project variables we derive from them. It is a
  template until the topic vote closes and the research question is fixed.
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
| `content_fetched`, `content_sha_ok` | int | Retrieval bookkeeping; `content_sha_ok` = 1 when the bytes reproduce `file_sha`, 2 when repaired via the blob API. |
| `frontmatter_valid` | int (0/1) | Whether YAML front matter parsed. |
| `name`, `description` | text | Parsed front-matter fields. |
| `body_chars` | int | Length of the body after front matter. |
| `sibling_count`, `sibling_bytes` | int | Folder composition summary (representatives only). |
| `has_scripts`, `has_references` | int (0/1) | Whether the skill folder bundles scripts or reference docs. |
| `composition_fetched`, `composition_truncated` | int | Bookkeeping; `composition_truncated` = 1 flags folders above the listing cap. |
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
| `content_fetched` | int (0/1) | Bookkeeping. |
| `skipped_reason` | text | `binary`, oversize, or folder above the listing cap. |

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

## Part B. Project variables (fill in after the topic vote)

One row per variable used in the analysis. Update this table in the same pull
request that introduces the code computing the variable, and reference the
row from `RESEARCH_QUESTION.md`.

| Variable | Definition | Type | Source (table.column) | Derivation | Unit | Notes / threats |
|---|---|---|---|---|---|---|
| `unit_of_analysis` | TODO: e.g. one distinct skill content, one spec file, one repository | key | TODO | TODO | n/a | Decided in Sprint 1 planning |
| `population` | TODO: which rows are in scope (filters on location, front matter, tool, dates) | filter | TODO | TODO | n/a | Document exclusions and counts |
| `outcome_1` | TODO: primary outcome or quality proxy | numeric / boolean | TODO | TODO | TODO | Why this proxy is defensible |
| `predictor_1` | TODO | numeric / categorical | TODO | TODO | TODO | Measurement error |
| `predictor_2` | TODO | numeric / categorical | TODO | TODO | TODO | |
| `control_1` | TODO: e.g. repository stars, age, language | numeric | TODO | TODO | TODO | Confounding |
| `validation_label` | TODO: manual annotation label | categorical | `results/validation_sample.csv` | Manual protocol in `docs/` | n/a | Inter-rater agreement |

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

Each explore CSV has a same-named PNG bar chart in `figures/`; the pilot draws `pilot_skill_risk_categories.png`. Topic-specific tables
will be added here as the analysis grows; the rule is one row in this table
per file in `results/`.

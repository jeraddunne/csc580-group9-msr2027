# Candidate research questions

How to use: the 15 questions from the assignment (Part I), each with the rubric's required implementation component and minimum evidence, plus notes on which sample tables support it and a rough difficulty. The notes are a starting point for your proposal, not a verdict. Difficulty is 1 (straightforward) to 5 (hard to finish in 9 weeks).

Both samples are described in `data/README.md`. Key facts: the GitSkills sample is a 277 MB SQLite database with 29,786 skill file occurrences (13,000 distinct contents, 11,841 repositories, 3,010 commit histories). The SpecMine sample is Parquet from 500 repositories (28,583 specs, 5,335 pull requests, 261,032 traceability references, 39 parsed features per spec) and is deliberately biased toward starred, PR-rich repositories.

## A. GitSkills questions

### 1. Skill reuse and propagation

- **RQ:** How are GitSkills artifacts reused across repositories, and do copied skills evolve consistently after reuse?
- **Required implementation:** clone or similarity-detection pipeline grouping identical or near-duplicate skill contents, reconstructing repository and commit timeline, and identifying whether later copies preserve, remove, or introduce instructions, commands, network access, or bundled scripts.
- **Minimum evidence:** similarity method, validation sample, reuse distribution, at least three propagation patterns, interactive or exportable result table.
- **Sample support:** `artifacts.file_sha` gives exact copies for free (50.5% of files are verbatim copies); `content` exists for one representative per content group, so near-duplicate detection needs the representative texts only; `first_commit_at` gives timelines for the 3,010 history rows; `artifact_siblings` gives bundled scripts. Near-duplicate grouping across the 13,000 representatives is feasible with MinHash or normalized-token similarity.
- **Watch out:** history is sampled, so "later copy" ordering is only known for rows with `history_fetched = 1`. Define the propagation patterns before coding.
- **Difficulty:** 3.

### 2. Skill quality indicators

- **RQ:** Which measurable properties of a skill (length, readability, structural completeness, specificity, tool references, examples) are associated with reuse or subsequent maintenance?
- **Required implementation:** feature-extraction pipeline and a statistical or comparative analysis; a quality proxy defined before analysis (copy count, subsequent edits, survival, cross-repository reuse).
- **Minimum evidence:** feature definitions, reproducible extractor, quality-proxy justification, baseline comparisons, error or validity analysis.
- **Sample support:** copy count per `file_sha` and `commit_count` are ready-made proxies; features come from `content`, `frontmatter_valid`, `body_chars`, `sibling_count`, `has_scripts`, `has_references`. Very well supported by the sample.
- **Watch out:** correlation is not causation; template skills inflate copy counts (address as a competing explanation).
- **Difficulty:** 2.

### 3. Skill maintenance and staleness

- **RQ:** How often do skills become outdated relative to the tools, commands, or workflows they describe?
- **Required implementation:** staleness detector using version references, command patterns, dependency names, repository activity, or changes in related files; manual validation of stale and non-stale samples.
- **Minimum evidence:** operational definition of "stale", detection algorithm, validation protocol, confusion matrix or agreement results, failure-mode examples.
- **Sample support:** `content` for version and command patterns; `repos.pushed_at`, `last_commit_at`, `commit_count` for activity. External ground truth on tool versions is not in the dataset.
- **Watch out:** defining "stale" defensibly is the whole project; validation needs two annotators and an agreement statistic.
- **Difficulty:** 4.

### 4. Skill security and supply-chain risk

- **RQ:** Do modified or reused skills introduce command execution, file-system access, network access, or other risky behavior absent from an earlier version or source artifact?
- **Required implementation:** static analyzer or rule-based scanner for executable commands, URLs, scripts, file operations, credential-related instructions, and changes across skill versions.
- **Minimum evidence:** threat model, detection rules, annotated examples, false-positive discussion, safe reporting artifact. Never execute untrusted scripts.
- **Sample support:** `content` and `artifact_siblings.content` (text files up to 100 KB) support rule-based scanning; "changes across versions" needs near-duplicate pairs from question 1 or the two commit messages per file. Well supported.
- **Watch out:** responsible reporting (no naming of repositories as "malicious"); rules must be validated against annotated examples.
- **Difficulty:** 3.

### 5. Shared-format evolution

- **RQ:** Are GitSkills descriptions converging toward a shared structure, or do tool-specific and repository-specific conventions remain distinct?
- **Required implementation:** structural and linguistic analysis extracting headings, metadata patterns, imperative language, tool names, trigger descriptions; comparison across cohorts, tool families, or repository categories.
- **Minimum evidence:** taxonomy or schema, extraction implementation, comparison across at least two groups, convergence or divergence visualizations.
- **Sample support:** `location_class` (canonical, skills-dir, other), `frontmatter_valid`, `first_commit_at` for monthly cohorts, `content` for structure. Well supported.
- **Watch out:** cohorts by date only exist for history-sampled rows; define groups that the sample can populate.
- **Difficulty:** 2.

### 6. Human and agent authorship signals

- **RQ:** Can observable characteristics of a GitSkill distinguish likely human-authored, agent-assisted, and highly templated artifacts, without claiming certainty about authorship?
- **Required implementation:** cautious classification or clustering based on document structure, phrasing, commit metadata, revision patterns, or repository context; framed as a heuristic.
- **Minimum evidence:** feature rationale, labeling limitations, baseline model or rule set, error analysis, responsible interpretation.
- **Sample support:** `first_commit_author_type` (User, Bot), commit messages with AI co-author trailers preserved, copy counts for "templated". Labels are weak by design.
- **Watch out:** no ground truth; the report must be careful about claims. Good for teams strong in text features and ethics writing.
- **Difficulty:** 4.

## B. SpecMine questions

### 7. Specification completeness and implementation follow-through

- **RQ:** Which specification characteristics are associated with later implementation in the repository?
- **Required implementation:** parser or feature extractor for structure, placeholders, acceptance criteria, file references, task lists, traceability links; join with implementation or PR outcomes.
- **Minimum evidence:** operational definition of completeness, matching or traceability algorithm, comparison between implemented and unimplemented specs, at least one manually inspected case study.
- **Sample support:** `spec_content_features` already has 39 features (checkboxes, acceptance criteria, placeholders); `spec_links` gives typed references; `pull_requests` and `pr_files` give outcomes. Strongly supported; the sample was built for exactly this.
- **Watch out:** the sample is biased to PR-rich, starred repositories; state it. Define "implemented" precisely.
- **Difficulty:** 2.

### 8. Specification quality and follow-up fixes

- **RQ:** Do specifications with more explicit acceptance criteria, structured scenarios, or file references predict fewer downstream fixes?
- **Required implementation:** specification-quality scorer connected to later commits, PRs, issue closures, or fix-like changes; correlation versus causation distinguished.
- **Minimum evidence:** scoring rubric, implementation, outcome definition, baseline analysis, confounding discussion, reproducible results.
- **Sample support:** features as in question 7; "fix-like changes" must be derived from `spec_file_commits.message` and `pull_requests` titles with a keyword rule that needs validation.
- **Watch out:** confounders (repository size, activity); outcome definition drives everything.
- **Difficulty:** 3.

### 9. Spec-to-code traceability patterns

- **RQ:** Where does specification implementation occur: same PR, later PRs, across multiple changes, or not at all?
- **Required implementation:** temporal traceability analysis using spec references, changed files, commits, PRs, and typed links; at least three implementation patterns classified.
- **Minimum evidence:** traceability algorithm, pattern definitions, distribution of patterns, validation sample, visualization of spec-to-code paths.
- **Sample support:** `spec_links` (2.4 M typed refs in full, 261 K in sample), `pr_files` with `is_spec` flags, `pull_requests.touches_code`, commit timestamps. Strongly supported; the upstream `example.ipynb` already demonstrates the flagship join.
- **Watch out:** path matching between spec references and changed files needs normalization and a validated sample.
- **Difficulty:** 3.

### 10. Specification abandonment

- **RQ:** What predicts that a specification will be abandoned, left with placeholders, or left with incomplete tasks?
- **Required implementation:** abandonment indicators plus a classifier, survival analysis, or comparative model using spec structure, repository maturity, activity, tool family, or author context.
- **Minimum evidence:** abandonment definition, feature pipeline, baseline model, validation strategy, limitations about missing or censored history.
- **Sample support:** `has_unfilled_placeholder`, `n_checkboxes` vs `n_checked`, `n_todo`, `file_last_commit_at`, `repo_pushed_at`, `spec_tool`. Supported; censoring (snapshot July 2026) must be handled.
- **Watch out:** 97.5% of sample specs were first committed in 2026, so "abandoned" needs a careful time window.
- **Difficulty:** 3.

### 11. Template boilerplate versus project-specific content

- **RQ:** How much of a specification is reused template material versus project-specific content, and does the ratio differ by tool family or repository type?
- **Required implementation:** text-similarity or template-detection method, manual validation of representative examples, boilerplate ratio compared across at least two populations.
- **Minimum evidence:** similarity method, threshold rationale, validation sample, group comparisons, examples of misleading matches.
- **Sample support:** raw markdown in `specs.jsonl.gz` (50 MB) and `kiro_specs.jsonl.gz` (69 MB); `spec_tool` for tool family; `content_family` feature. Supported; needs the larger text files.
- **Watch out:** deciding what counts as template (shared across repositories vs known tool templates) is a design decision to document.
- **Difficulty:** 3.

### 12. Human-AI collaboration around specifications

- **RQ:** What evidence in repository history suggests specifications are collaboratively produced, revised, or operationalized by humans and AI tools?
- **Required implementation:** cautious evidence-extraction pipeline using commit messages, file structure, tool markers, revision patterns, or content signals; observed evidence explicitly separated from speculation.
- **Minimum evidence:** evidence taxonomy, extraction tool, manual validation, alternative explanations, responsible reporting framework.
- **Sample support:** `spec_file_commits` (message, author_type, committer), 780 K commits in full; AI co-author trailers and tool markers in messages. Supported.
- **Watch out:** like question 6, it is a signal-detection study; strong writing discipline required.
- **Difficulty:** 4.

## C. Combined or comparative questions

### 13. From specification to agent skill

- **RQ:** Do repositories that use specification-driven development also exhibit different patterns of GitSkill adoption, reuse, or maintenance?
- **Required implementation:** join or compare the two datasets using repository-level identifiers or carefully defined populations; comparative analysis beyond counts.
- **Minimum evidence:** join strategy or matching limitations, comparable variables, group comparison, robustness check, reproducible pipeline.
- **Sample support:** the join key is `repos.full_name` (GitSkills) to `spec_files.repo_name` (SpecMine). Overlap between the two samples is unknown until checked; do this check before proposing. If the overlap is tiny, the question is not feasible with samples alone.
- **Difficulty:** 4 (depends entirely on overlap).

### 14. AI-native artifact lifecycle comparison

- **RQ:** How do the lifecycle properties of GitSkills and specifications differ in creation, reuse, churn, abandonment, and maintenance?
- **Required implementation:** comparable lifecycle metrics computed for both artifact families; documented where the datasets are not directly comparable.
- **Minimum evidence:** metric definitions, pipeline, comparative visualizations, threats to validity, one case study explaining an unexpected result.
- **Sample support:** `first_commit_at`, `last_commit_at`, `commit_count` (GitSkills; sampled) vs `file_first_commit_at`, `file_last_commit_at`, `file_total_commits` (SpecMine). Supported without a join, which makes it safer than question 13.
- **Watch out:** the two samples were drawn differently; comparability must be argued explicitly.
- **Difficulty:** 3.

### 15. Predicting review or maintenance effort

- **RQ:** Can artifact characteristics predict whether a skill or specification will require substantial follow-up modification?
- **Required implementation:** baseline prediction model or rule-based ranking using artifact and repository features; predictive performance and practical interpretation reported.
- **Minimum evidence:** baseline, feature extraction, train/test design or validation method, performance metrics, error analysis, small demonstration interface or report generator.
- **Sample support:** outcome = `commit_count` (GitSkills) or `file_total_commits` (SpecMine) above a threshold; features from content and repository metadata. Supported; the demonstration interface adds engineering work.
- **Watch out:** leakage between features and outcome (for example, `last_commit_at`); needs a clean train/test split by repository.
- **Difficulty:** 3.

## Quick comparison

| # | Dataset | Sample support | Difficulty | Main risk |
|---|---|---|---|---|
| 1 | GitSkills | strong (exact copies), medium (near-dupes, timeline) | 3 | sampled history |
| 2 | GitSkills | strong | 2 | template confound |
| 3 | GitSkills | medium | 4 | defining stale |
| 4 | GitSkills | strong | 3 | responsible reporting |
| 5 | GitSkills | strong | 2 | cohort coverage |
| 6 | GitSkills | medium | 4 | no ground truth |
| 7 | SpecMine | strong | 2 | sample bias |
| 8 | SpecMine | medium | 3 | outcome definition |
| 9 | SpecMine | strong | 3 | path matching |
| 10 | SpecMine | strong | 3 | censoring |
| 11 | SpecMine | medium (needs text files) | 3 | template definition |
| 12 | SpecMine | medium | 4 | speculation control |
| 13 | Both | unknown until overlap checked | 4 | join size |
| 14 | Both | strong (no join needed) | 3 | comparability |
| 15 | Either | strong | 3 | leakage |

Check the overlap for question 13 with:

```bash
python -m msr_pipeline query --dataset gitskills --sql "SELECT full_name FROM repos" > /tmp/gs.txt
# compare with spec_files.repo_name from the SpecMine sample (see notebooks/00_sample_overview.ipynb)
```

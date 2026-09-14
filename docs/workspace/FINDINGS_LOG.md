# Findings log

How to use: the curated record of what we have found, each with the evidence to reproduce it. File new findings with the [Research finding form](https://github.com/jeraddunne/csc580-group9-msr2027/issues/new?template=08-research-finding.yml); the Scrum Master copies them here at the Thursday check-in.

**Conventions**

- The **Finding** column is an observation only. Interpretation goes in **Implication**.
- **Evidence** is a command, query, file, or citation that reproduces the finding.
- **Confidence**: *Reported by dataset authors*; *Measured by code, not yet re-checked*; *Re-checked by a second member*; *Hypothesis*.
- **Status**: *Open* (usable, not re-checked), *Confirmed* (re-checked by a second member), *Refuted* (wrong; keep the row and say why).
- Dataset findings state the snapshot. The GitSkills sample used below is `agent_skills_sample.db`, sha256 `683888c9...` (upstream commit `fff3df9`), recorded in `data/samples/MANIFEST.json` on 2026-09-14.
- Numbers marked *signal* come from keyword rules whose precision has not been validated. They count text patterns, not confirmed risky behaviour.

## Datasets: reported by the dataset authors

| ID | Date | Finding | Evidence | Confidence | Found by | Implication | Status |
|---|---|---|---|---|---|---|---|
| F-001 | 2026-09-13 | Full GitSkills: 3,797,117 SKILL.md occurrences, 1,877,981 distinct contents, 282,200 repositories, collected July 2026 | GitSkills sample README; arXiv:2608.10906 | Reported by dataset authors | Jerad Dunne | Population for any GitSkills question; the report must state the snapshot | Open |
| F-002 | 2026-09-13 | 50.5% of full-dataset occurrences are verbatim copies of another file; there is no package manager, so reuse happens by copying folders | GitSkills README; challenge page | Reported by dataset authors | Jerad Dunne | Copying is the propagation mechanism for questions 1 and 4 | Open |
| F-003 | 2026-09-13 | GitHub code search indexes default branches only, files under 384 KB, and forks only when more starred than the parent, so the dataset is a lower bound | GitSkills README, Known limitations | Reported by dataset authors | Jerad Dunne | External validity threat for every GitSkills question | Open |
| F-004 | 2026-09-13 | Commit history follows the file's current path and exists only for a sample (458,548 histories in the full dataset) | GitSkills README | Reported by dataset authors | Jerad Dunne | Time ordering is unavailable for most rows; renamed files have misleading first-commit dates | Open |
| F-005 | 2026-09-13 | The SpecMine sample is deliberately non-representative: 61% of its repositories have 100 or more stars versus 1.3% in the full corpus; 97.5% of sample specs were first committed in 2026 | SpecMine README, Sampling strategy | Reported by dataset authors | Jerad Dunne | Any SpecMine result from the sample must be framed as describing popular, PR-rich repositories | Open |

## Datasets: measured by us

| ID | Date | Finding | Evidence | Confidence | Found by | Implication | Status |
|---|---|---|---|---|---|---|---|
| F-006 | 2026-09-14 | The full GitSkills Parquet mirror is about 6.45 GB for `artifacts` (31 files), 6.96 GB for `artifact_siblings` (45 files), and 0.02 GB for `repos` | Hugging Face API: `https://huggingface.co/api/datasets/mvaccargiu/gitskills/tree/main?recursive=true` | Measured by code, not yet re-checked | Jerad Dunne | A streamed pass over the full `artifacts` table is possible on a laptop but is a deliberate decision, not a default | Open |
| F-007 | 2026-09-14 | GitSkills sample: 29,786 occurrences, 13,000 distinct contents, 11,841 repositories, 3,010 rows with commit history, 11,291 distinct contents with valid front matter, 1,326 distinct contents with bundled scripts | `python -m msr_pipeline query --sql "select count(*), count(distinct file_sha), count(distinct repo_full_name), sum(history_fetched) from artifacts"` | Measured by code, not yet re-checked | Jerad Dunne | Sample is large enough for prevalence work; history is sparse (about 10% of rows) | Open |
| F-008 | 2026-09-14 | In the sample, 16,786 of 29,786 occurrences (56.4%) are copies of another occurrence; 3,378 distinct contents have 2 or more copies, 2,854 of them across 2 or more repositories; the most copied content has 188 copies | same query tool; `results/gitskills_copy_distribution.csv` after `make explore` | Measured by code, not yet re-checked | Jerad Dunne | The sample reproduces the heavy copying reported for the full dataset (F-002) | Open |
| F-009 | 2026-09-14 | Location classes in the sample: 14,882 occurrences under a `skills/` directory, 12,539 elsewhere, 2,365 at the canonical `.claude/skills/` path | `results/gitskills_location_summary.csv` after `make explore` | Measured by code, not yet re-checked | Jerad Dunne | Most skills are not at the canonical path; population rules must say which locations count | Open |
| F-010 | 2026-09-14 | Among the 3,010 history rows, first-commit author types are User 2,545, empty 436, Bot 25, Organization 4; first commits range from 2025-04-14 to 2026-07-19 | `python -m msr_pipeline query --sql "select first_commit_author_type, count(*) from artifacts where history_fetched=1 group by 1"` | Measured by code, not yet re-checked | Jerad Dunne | Bot authorship is rare in the sample; some skill files predate the October 2025 specification | Open |
| F-011 | 2026-09-14 | 542 front-matter names have 2 or more distinct contents in the sample (1,631 variants). Of 3,517 same-name pairs, 245 are near-duplicates (word-shingle Jaccard of at least 0.5) across 141 names | `python -m msr_pipeline risk-pilot`; `results/pilot_skill_risk_family_summary.csv` | Measured by code, not yet re-checked | Jerad Dunne | Modified-copy analysis is possible in the sample, but lineage is a similarity assumption that needs validation | Open |
| F-012 | 2026-09-14 | Only 10 of the 245 near-duplicate pairs have commit dates for both variants | `results/pilot_skill_risk_family_summary.csv` | Measured by code, not yet re-checked | Jerad Dunne | "Did the newer copy add or remove X" is underpowered in the sample; direction needs history or the full dataset | Open |

## Proposal P-01 pilot: risk signals (unvalidated)

All rows come from `python -m msr_pipeline risk-pilot` with `rules/skill_risk_rules.yaml` as of 2026-09-14. Signals are keyword matches; precision is unknown until the validation sample is annotated.

| ID | Date | Finding | Evidence | Confidence | Found by | Implication | Status |
|---|---|---|---|---|---|---|---|
| F-013 | 2026-09-14 | 1,159 of 13,000 distinct contents (8.9%) match at least one high-risk signal rule (severity 6 or more); counting copies, 3,326 of 29,786 occurrences (11.2%) | `results/pilot_skill_risk_rules.csv`, row ANY_HIGH_RISK | Measured by code, not yet re-checked | Jerad Dunne | Copy-weighted exposure is higher than content-weighted prevalence | Open |
| F-014 | 2026-09-14 | Signal counts by rule, distinct contents: unscoped shell tool grant 511; destructive commands 173; sudo 140; oversight bypass wording 109; dynamic code execution 100; persistence locations 91; pipe-to-shell or PowerShell download-and-execute 73 (71 and 8 by rule, with overlap); credential file paths 65; obfuscation 27; hard-coded IP endpoints 21; request-capture or paste endpoints 8 | `results/pilot_skill_risk_rules.csv` | Measured by code, not yet re-checked | Jerad Dunne | Rare categories (exfiltration endpoints, obfuscation) are small enough to inspect by hand in full | Open |
| F-015 | 2026-09-14 | Contents with a high-risk signal average 2.87 copies (29.3% copied at least twice, 26.0% across repositories) versus 2.24 copies (25.7%, 21.6%) for the rest; both medians are 1 | `results/pilot_skill_risk_reach.csv` | Measured by code, not yet re-checked | Jerad Dunne | A descriptive difference only; no significance test or confound control yet | Open |
| F-016 | 2026-09-14 | 18 of the 245 near-duplicate pairs differ in their high-risk signal categories, spread over 6 names; the widely copied `skill-creator` template accounts for 9 of the 18 | `results/pilot_skill_risk_family_pairs.csv` (filter `differs`) | Measured by code, not yet re-checked | Jerad Dunne | Template updates are a competing explanation for drift | Open |
| F-017 | 2026-09-14 | Of the 1,326 skills whose bundled script text could be read, 200 (15.1%) have at least one script matching a high-risk rule (303 of 5,153 script files) | `results/pilot_skill_risk_siblings_summary.csv` | Measured by code, not yet re-checked | Jerad Dunne | Bundled scripts carry a higher signal rate than SKILL.md text; scanning them is required, never running them | Open |
| F-018 | 2026-09-14 | The full pilot run takes about 3 minutes on the proposer's laptop | `time python -m msr_pipeline risk-pilot` | Measured by code, not yet re-checked | Jerad Dunne | Fast enough to rerun at every sprint review | Open |

## Tooling and process

| ID | Date | Finding | Evidence | Confidence | Found by | Implication | Status |
|---|---|---|---|---|---|---|---|
| F-019 | 2026-09-13 | The instructor's Team-Planning board uses the statuses Todo, In progress, Done, Block, Cancelled, a WIP limit of 5 on Todo and In progress, and Iteration and Estimate fields | https://github.com/users/mkaouer/projects/5 (Backlog and Board views) | Measured by us, not yet re-checked | Jerad Dunne | Our board mirrors these fields (`scripts/setup_project_board.py`) | Open |
| F-020 | 2026-09-13 | Pushing workflow files and creating Projects boards require the `workflow` and `project` token scopes, which a default `gh auth login` token lacks | `gh auth status`; push rejection message | Measured by us | Jerad Dunne | Each member who runs setup scripts needs `gh auth refresh -s workflow,project,read:project` | Open |

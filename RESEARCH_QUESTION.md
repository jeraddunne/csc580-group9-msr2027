# Research Question

Status: **selected, 2026-09-14.** The project is carried out by Jerad Dunne alone (ADR-0005). The topic is proposal P-01 ([issue #41](https://github.com/jeraddunne/csc580-group9-msr2027/issues/41), [full proposal](docs/proposals/P-01-jerad-dunne-skill-risk-propagation.md)). The analysis runs with `python -m msr_pipeline analyze`.

## 1. Selected MSR-inspired topic

- Rubric question: **4. Skill security and supply-chain risk**, using the similarity method from **1. Skill reuse and propagation**
- Dataset: **GitSkills**, official sample of the July 2026 snapshot (`agent_skills_sample.db`, sha256 `683888c9...`, upstream commit `fff3df9`, recorded in `data/samples/MANIFEST.json`)
- Proposal: P-01, issue #41

## 2. Precise research question

> In the GitSkills July 2026 sample, how prevalent are skill instructions and bundled scripts that enable risk-relevant capabilities, do skills carrying them reach more repositories through verbatim copying, and do modified variants of the same skill add or remove those capabilities?

Risk-relevant capabilities are the categories in `docs/research/THREAT_MODEL.md`: remote code execution, oversight bypass, exfiltration endpoints, credential access, hard-coded network endpoints, persistence, obfuscation, destructive operations, privilege elevation, dynamic code execution, and unscoped shell tool grants.

Sub-questions:

1. **RQ1 Prevalence.** What share of distinct skill contents, and what share of copy-weighted occurrences, carry each capability category?
2. **RQ2 Reach.** Do contents with a high-risk capability have more copies and reach more repositories than contents without one, after controlling for size, bundled scripts, location, repository stars, and language?
3. **RQ3 Drift.** Among near-duplicate variants of the same skill, how often do high-risk capabilities differ, and in which direction when both variants have commit dates?

## 3. Motivation and expected contribution

Skills have no registry or package manager. Developers reuse them by copying folders, and no compiler or type checker verifies them (Destefanis et al., arXiv:2608.10906). An agent follows a skill with the user's tool permissions. A skill therefore combines two known risk paths: copied code in the software supply chain (Ohm et al., 2020) and instructions that direct an agent (Greshake et al., 2023).

**Expected contribution.** First, a reviewable, tested rule set for skill risk signals with measured precision. Second, a prevalence and reach profile of those signals in a real population. Third, a careful, limited description of how variants differ.

**What each result would mean.** High validated prevalence says copying skills needs review tooling. A positive reach difference says risky capabilities spread rather than stall. No difference says copying is indifferent to these capabilities. Low rule precision is also informative: it shows keyword scanning is not enough and quantifies why.

## 4. Competing or simpler explanations

The analysis must rule out or acknowledge each of these:

- **Keyword is not capability.** Skills often describe unsafe patterns to warn against them. Validation labels separate risky-in-context from benign-in-context.
- **Template inheritance.** Variants of widely copied template skills differ because the template changed, not because copiers added capabilities. RQ3 is reported with and without template families.
- **Popularity and purpose.** Setup, DevOps, and deployment skills need shell and network commands and are also popular, so reach differences may reflect purpose. RQ2 controls for size, scripts, location, stars, and language. Category-level tests show which capabilities drive any difference.
- **Sampling artefact.** The sample is drawn by lowest content hash, which splits variant families. RQ3 is scoped to case studies on the sample.

## 5. Unit of analysis, population, sample

| Item | Definition |
|---|---|
| Unit of analysis | One distinct skill content (`artifacts.file_sha`), represented by its row with `dedup_primary = 1`; its copies are an outcome |
| Population | SKILL.md files discoverable by GitHub code search on public default branches in July 2026. This is a lower bound on all skills (THREATS E1) |
| Sample | The official GitSkills sample: 13,000 distinct contents with all 29,786 occurrences |
| Inclusion rule 1 | Representative content was fetched and is not empty |
| Exclusion rule | **Symlink stub**: the stripped content is a single line under 200 characters, consists only of word characters, `.`, `/`, space, or `-`, and contains a `/` or ends in `.md`. Such content is a symlink target path, not instructions (`skill_risk.is_symlink_stub`) |
| Main population | Inclusion rule 1 and not a symlink stub |
| Sensitivity subset | Main population with `artifacts.frontmatter_valid = 1` |
| Bundled scripts | `artifact_siblings` rows with `entry_type = 'file'`, text content present, and a script extension (`.sh`, `.py`, `.js`, `.ts`, `.ps1`, and others in `skill_risk.SCRIPT_EXTENSIONS`) |

Counts at each step are written to `results/population_flow.csv`.

## 6. Variables and outcome measures

| Variable | Role | Definition | Source (table.column) |
|---|---|---|---|
| `rule_ids` | derived | Ids of active rules whose patterns match the content | `artifacts.content`, `rules/skill_risk_rules.yaml` |
| `high_risk` | independent | At least one matching rule with severity 6 or more | derived from `rule_ids` |
| `high_risk_categories` | independent | Categories of matching rules with severity 6 or more | derived from `rule_ids` |
| `copies` | dependent (RQ1 weight, RQ2) | Occurrences sharing the `file_sha` | count of `artifacts` rows by `file_sha` |
| `repos` | dependent (RQ2) | Distinct repositories holding the `file_sha` | distinct `artifacts.repo_full_name` by `file_sha` |
| `body_chars` | control | Body length after front matter | `artifacts.body_chars` |
| `has_scripts` | control | Folder bundles scripts | `artifacts.has_scripts` |
| `location_class` | control | canonical, skills-dir, or other | `artifacts.location_class` |
| `stars` | control | Stars of the representative's repository | `repos.stars` |
| `language` | control | Primary language of the representative's repository, top 8 plus other | `repos.language` |
| `family` | grouping (RQ3) | Lower-cased, trimmed front-matter name | `artifacts.name` |
| `similarity` | grouping (RQ3) | Word 5-shingle Jaccard similarity between two variants | derived from `artifacts.content` |
| `ordered`, `only_in_a`, `only_in_b` | dependent (RQ3) | Whether both variants have first-commit dates; high-risk categories only in the older (a) or newer (b) variant | `artifacts.first_commit_at` |
| `validation_label` | validation | Risky in context, benign in context, or not present | manual annotation (annotation kit) |

Full definitions are in `DATA_DICTIONARY.md` Part B.

## 7. Hypotheses and expectations

- **H1 (rules).** At least one high-risk category reaches validated precision of 0.8 or more. It is falsified if every high-risk category's precision is below 0.8 in the validation sample.
- **H2 (reach).** Contents with a high-risk signal have a different copy distribution from contents without one. The primary test is a two-sided Mann-Whitney U on `copies`, with the rank-biserial correlation as effect size. The confirmatory model is NB2 regression of `copies - 1` on `high_risk` plus controls, reported as an incidence rate ratio. **H0:** no difference in copy distributions (IRR confidence interval includes 1).
- **RQ3** is descriptive. The sample holds too few dated variant pairs to test direction, so results are counts plus manually classified case studies.
- Secondary per-category tests use Holm-adjusted p-values. All headline results are repeated under the sensitivity scenarios in `results/sensitivity_summary.csv`.

## 8. Required implementation component and minimum evidence

Rubric question 4, required implementation component: *"Implement a static analyzer or rule-based scanner for executable commands, URLs, scripts, file operations, credential-related instructions, and changes across skill versions."*

Minimum evidence: *"Threat model, detection rules, annotated examples, false-positive discussion, and a safe reporting artifact. Students must not execute untrusted scripts from the dataset."*

| Minimum evidence item | Artifact | Issues | Sprint |
|---|---|---|---|
| Threat model | `docs/research/THREAT_MODEL.md`; report section | #12, #18 | 1 |
| Detection rules | `rules/skill_risk_rules.yaml`, `src/msr_pipeline/skill_risk.py`, rule regression tests | #15, #21, #22 | 1 to 2 |
| Scanner on scripts and changes across versions | `scan_siblings`; RQ3 lineage pairs (`results/rq3_*.csv`) | #21 | 2 |
| Annotated examples | Validation sample, annotation guideline, labels, precision and intra-rater agreement | #23 | 2 |
| Preliminary and final results | `results/rq1_*`, `rq2_*`, `rq3_*`, figures | #16, #24, #27, #30 | 1 to 3 |
| False-positive discussion | Error analysis from validation labels | #29 | 3 |
| Robustness | `results/sensitivity_summary.csv`, threshold sweep, Holm-adjusted category tests | #28 | 3 |
| Safe reporting artifact | Aggregate tables with no repository or account names; report section on responsible reporting | #31, #32 | 3 |
| No execution of untrusted scripts | Static text analysis only (loader and scanner docstrings, `data/README.md`) | all | all |

Issue map: Sprint 1 issues #12 to #20, Sprint 2 issues #21 to #26, Sprint 3 issues #27 to #35.

### Validation design (solo)

The project has one member, so the two-annotator design in the proposal is replaced (ADR-0005):

1. A single annotator (Jerad Dunne) labels the stratified validation sample from a written guideline.
2. **Intra-rater reliability.** At least seven days later, a random 30% of the sample is re-labelled blind to the first labels. Cohen's kappa between the two passes is reported.
3. **Optional second rater.** If a classmate, the instructor, or a disclosed AI-assisted pass provides labels for a subset, inter-rater kappa is reported separately and the rater type is stated. AI-assisted labels are never merged into the primary labels.

## 9. Primary risks and threats

Full register: `THREATS_TO_VALIDITY.md` (rows marked "Active: P-01") and `docs/lean-six-sigma/FMEA_RISK_REGISTER.md`. The top three:

1. **Construct validity.** Keyword signals are not capabilities. Mitigation: validated precision per rule, and results reported at three severity cutoffs.
2. **Internal validity.** The popularity and purpose confound in reach. Mitigation: NB2 controls, per-category tests, and excluding the most-copied contents and template families.
3. **Conclusion validity.** A single annotator and sparse history for RQ3. Mitigation: intra-rater kappa, drift scoped to descriptive case studies, and the limitation stated in the report.

# P-01: Risky capabilities in copied agent skills: prevalence, reach, and drift

| Item | Value |
|---|---|
| Proposer | Jerad Dunne (@jeraddunne) |
| Based on | Rubric question 4, *Skill security and supply-chain risk*, using the similarity method from question 1, *Skill reuse and propagation* |
| Dataset | GitSkills sample, July 2026 snapshot (`agent_skills_sample.db`, sha256 `683888c9...`, upstream commit `fff3df9`) |
| Status | Submitted for the topic vote, 2026-09-14 |
| Pilot | `python -m msr_pipeline risk-pilot` (results in `results/pilot_skill_risk_*.csv`) |

## 1. Summary

Agent skills are copied between repositories by hand, and an agent follows a skill's instructions with whatever tools it has been granted. Nobody checks what a copied skill tells the agent to do, or whether a later copy changed it. This project would build a static, rule-based scanner for risk-relevant capabilities in SKILL.md files and their bundled scripts. It would validate the scanner against a manually annotated sample and use it to measure three things. First, how common those capabilities are. Second, whether skills carrying them spread further through copying. Third, whether modified variants of the same skill add or remove them. A one-day pilot on the sample shows the first two are well supported and the third is thin, so the design below treats drift as a scoped case study.

## 2. Research question

**Main question.** In the GitSkills July 2026 sample, how prevalent are skill instructions and bundled scripts that enable risk-relevant capabilities, do skills carrying them reach more repositories through verbatim copying, and do modified variants of the same skill add or remove those capabilities?

Risk-relevant capabilities: remote code execution, destructive operations, privilege elevation, credential access, unscoped shell tool grants, oversight bypass, dynamic code execution, persistence, obfuscation, and exfiltration endpoints.

| Sub-question | Measure |
|---|---|
| RQ1 Prevalence | Share of distinct contents, and share of copy-weighted occurrences, with each validated capability category |
| RQ2 Reach | Copies and repositories per content, compared between contents with and without a high-risk capability |
| RQ3 Drift | Among near-duplicate variants of the same skill, how often high-risk capabilities differ, and in which direction when both commit dates exist |

## 3. Motivation and expected contribution

The GitSkills authors note that skills "have no central registry or package manager; developers reuse them by copying folders between repositories", and that no compiler or type checker verifies them (Destefanis et al., arXiv:2608.10906). Software supply-chain research shows that copied and redistributed code is a common attack path (Ohm et al., 2020). Indirect prompt-injection research shows that instructions reaching an agent can direct it to act with the user's authority (Greshake et al., 2023). A skill combines both: it is copied like code and read like instructions.

**Contribution.** A reviewable, tested rule set for skill risk signals with measured precision. A prevalence and reach profile of those signals in a real population. A careful description of how variants differ. The rule file and scanner stay usable after the course.

**What results would mean.** High prevalence with high precision says skill copying needs review tooling. A reach difference says risky skills are not stalling, they are spreading. Low precision is also a result: it shows keyword scanning is not enough and quantifies why. That informs anyone building skill linters.

## 4. How my prior work feeds into this project

I am proposing this topic because it sits where several things I already work on meet. Each row below is a reusable input, not a claim that the work is done.

| My background or project | What it brings | Where it lands here |
|---|---|---|
| Security research on threat models for AI-agent integrations (a course term paper and conference submission covering prompt injection, privilege misuse through delegated tool access, and supply-chain compromise, mapped to NIST SP 800-53 controls) | A threat-model vocabulary for what an agent can be told to do and why it matters | The capability categories in `rules/skill_risk_rules.yaml`, the threat-model section of the report, and the severity scores |
| Research on how compromise propagates through networked systems using directed-graph epidemic models (Kephart and White, 1991) | A way to think about exposure as copies and reach, not just counts | RQ2: content-weighted versus copy-weighted exposure, reach comparisons, and the propagation framing in the discussion |
| ARI 510 team project, *DMAIC Planner*, where I own the annotation rubric; it uses reviewable YAML rule files with rule regression tests and never auto-activates model-proposed rules | A proven rule-file pattern and an annotation-rubric discipline | Rule file format (id, severity, status, source, examples), the rule regression tests in `tests/test_skill_risk.py`, and the annotation guideline for validation |
| Lean Six Sigma Black Belt; our project already runs a DMAIC and FMEA overlay | FMEA scoring and measurement-system thinking | Ranking capability categories by severity, occurrence, and detection (the same FMEA method we use for project risks); treating validation as a measurement-system analysis |
| Working information-system security role with RMF and NIST SP 800-53 | Practice in writing findings that are useful without being alarmist | The safe-reporting artifact: aggregate results, no repository names, no reproduction of risky payloads |
| Daily user and author of agent skills: 32 installed skills (3 installed by cloning public GitHub repositories) and 8 skills I wrote for my research workflow | First-hand knowledge of how skills are copied, edited, and trusted; a real calibration set | Dry run of the scanner on those skills (section 5.5) and examples for the annotation guideline |

## 5. Pilot evidence (measured 2026-09-14)

All numbers below come from `python -m msr_pipeline risk-pilot` on the sample (about 3 minutes). **They are unvalidated keyword signals.** They show what the data can support, not what is true about skill risk.

### 5.1 Prevalence of high-risk signals (RQ1)

| Signal (rule) | Distinct contents | Share of 13,000 | Copy-weighted occurrences | Share of 29,786 |
|---|---|---|---|---|
| Any high-risk signal (severity 6 or more) | 1,159 | 8.9% | 3,326 | 11.2% |
| Unscoped shell tool grant in front matter | 511 | 3.9% | 1,121 | 3.8% |
| Recursive forced delete or git history rewrite | 173 | 1.3% | 726 | 2.4% |
| `sudo` | 140 | 1.1% | 817 | 2.7% |
| Oversight bypass wording | 109 | 0.8% | 219 | 0.7% |
| Dynamic code execution | 100 | 0.8% | 347 | 1.2% |
| Persistence locations (cron, shell profiles, git hooks) | 91 | 0.7% | 512 | 1.7% |
| Download-and-execute (category REMOTE_CODE) | 73 | 0.6% | 170 | 0.6% |
| Credential file paths | 65 | 0.5% | 252 | 0.8% |
| Obfuscated payload decoding | 27 | 0.2% | 70 | 0.2% |
| Hard-coded IP endpoint | 21 | 0.2% | 79 | 0.3% |
| Request-capture or paste endpoints | 8 | 0.1% | 10 | 0.03% |

Context signals, not counted as high risk: shell code blocks in 4,351 contents (33.5%), an `allowed-tools` declaration in 1,282 (9.9%), secret-bearing environment variable names in 938 (7.2%), network tooling in 851 (6.5%).

Source: `results/pilot_skill_risk_rules.csv`, `results/pilot_skill_risk_categories.csv`, `figures/pilot_skill_risk_categories.png`.

### 5.2 Reach (RQ2)

| Group | Contents | Mean copies | Copied 2 or more times | Across 2 or more repositories | Max copies |
|---|---|---|---|---|---|
| High-risk signal | 1,159 | 2.87 | 29.3% | 26.0% | 171 |
| No high-risk signal | 11,841 | 2.24 | 25.7% | 21.6% | 188 |

Both medians are 1. This is a descriptive difference with no significance test and no confound control yet (section 7.4). Source: `results/pilot_skill_risk_reach.csv`.

### 5.3 Variants and drift (RQ3)

| Measure | Value |
|---|---|
| Front-matter names with 2 or more distinct contents | 542 (1,631 variants) |
| Same-name pairs examined | 3,517 |
| Near-duplicate pairs (word-shingle Jaccard of at least 0.5) | 245, across 141 names (median similarity 0.84) |
| Near-duplicate pairs whose high-risk categories differ | 18, across 6 names |
| ...of which from the widely copied `skill-creator` template | 9 |
| Near-duplicate pairs with commit dates for both variants | 10 |
| Dated pairs where the newer variant adds a high-risk category | 1 (unscoped shell grant) |

**What this means for the design.** Drift exists, but the sample holds too few dated variant pairs to estimate direction. Section 7.3 scopes RQ3 as case studies on the sample, with an optional full-dataset extension decided by ADR in Sprint 1. Source: `results/pilot_skill_risk_family_summary.csv`, `results/pilot_skill_risk_family_pairs.csv`.

### 5.4 Bundled scripts

Of 1,326 skills whose bundled script text is in the sample, 200 (15.1%) have at least one script matching a high-risk rule (303 of 5,153 script files). Scripts are read as text only. Source: `results/pilot_skill_risk_siblings_summary.csv`.

### 5.5 Calibration dry run on my own skills

The same rules on my locally installed skills (32 SKILL.md files, mostly third-party) flagged 7 with any signal and 1 with a high-risk signal, an unscoped shell grant. My 8 self-authored research skills flagged 4 with any signal and none with a high-risk signal. No bundled script in either set matched a high-risk rule. I know these skills, so they are a quick sanity check on false positives before annotation starts. Only aggregate counts are reported.

## 6. Study design

| Element | Definition | Source |
|---|---|---|
| Unit of analysis | One distinct skill content (`file_sha`) with its copies | `artifacts` |
| Population | SKILL.md files on public GitHub default branches, July 2026 (a lower bound, see F-003) | GitSkills |
| Sample | The 13,000 distinct contents in the official sample, drawn by lowest content hash, with all their copies | `artifacts` where `dedup_primary = 1` |
| Inclusion rules (Sprint 1 decision) | Content fetched; exclude symlink stubs (content is only a path); sensitivity run restricted to `frontmatter_valid = 1` | `artifacts.content`, `frontmatter_valid` |
| Independent variable | Validated capability categories present (binary per category, plus maximum severity) | derived by the scanner |
| Outcomes | RQ1 prevalence; RQ2 `copies` and `repos` per content; RQ3 category added, removed, or unchanged per variant pair | derived from `artifacts` |
| Controls for RQ2 | Location class, body length (`body_chars`), bundled scripts (`has_scripts`), repository stars and language | `artifacts`, `repos` |
| Lineage assumption | Same front-matter name and word-shingle Jaccard at or above a threshold (0.5 in the pilot; sensitivity from 0.3 to 0.8) | derived |
| Ordering | `first_commit_at` where both variants have history | `artifacts.first_commit_at` |

**Hypotheses.** H1: at least one high-risk category has validated precision of 0.8 or more. H2: contents with a validated high-risk capability have a different copy distribution from those without (two-sided; null is no difference). RQ3 has no hypothesis in the sample because it is underpowered (F-012).

## 7. Method and implementation

Pipeline stages map onto code that already exists as a pilot and would be hardened in Sprints 1 and 2.

| Stage | Module | Status |
|---|---|---|
| Load | `msr_pipeline.load` (SQLite, read-only) | exists |
| Extract | `msr_pipeline.skill_risk.scan_contents`, `scan_siblings`, `rules/skill_risk_rules.yaml` | pilot, 19 rules with regression examples |
| Link variants | `shingles`, `jaccard`, `family_pairs` | pilot |
| Analyze | `rule_prevalence`, `category_prevalence`, `reach_by_risk`, `family_summary` | pilot; statistics to add |
| Validate | `validation_sample` plus annotation guideline and agreement script | sample generator exists; guideline to write |
| Report | CSV tables, figures, safe-reporting summary | pilot tables exist |

### 7.1 Threat model

Actors: the skill author, anyone who copies and edits the skill, the agent that loads it, and the user whose permissions the agent holds. Assets: the user's files, credentials, repositories, and machine. The question for each capability is what the skill can cause the agent to do with those permissions. Each rule category is one such capability, with a severity score from 1 to 10 recorded in the rule file.

### 7.2 Detection rules

Rules live in `rules/skill_risk_rules.yaml`. Each rule has an id, category, severity, patterns, status (active, proposed, retired), source, and match and no-match examples enforced by tests. Error analysis can propose a rule change, but it only becomes active through a reviewed pull request that adds a regression example. This is the same governance pattern as my ARI 510 project.

### 7.3 Variant analysis (RQ3), scoped

On the sample: describe the 245 near-duplicate pairs, manually inspect every pair whose high-risk categories differ (18 in the pilot), and classify each difference as template update, local adaptation, hardening, or capability addition. This gives case studies with explicit limits.

Optional extension, decided by ADR in Sprint 1: one streamed pass over the full `artifacts` Parquet files (about 6.45 GB, F-006) to collect only the name families that already show differences in the sample. The pass would use `name`, `file_sha`, `content`, and history columns. It adds dated pairs without loading the whole dataset.

### 7.4 Statistics (RQ2)

Compare copy counts between groups with a Mann-Whitney U test and bootstrap confidence intervals for the difference in mean copies and in the share copied. Then fit a negative binomial regression of copies on validated capability presence with the controls in section 6. Report effect sizes, not only p-values. Sensitivity checks cover the similarity threshold, the severity cutoff, the front-matter-valid subset, and excluding the ten most copied contents.

### 7.5 Validation

- **Sample.** Stratified: up to 10 contents per high-risk category plus 40 with no signal, about 150 skills, fixed seed (`results/tmp/pilot_skill_risk_validation_sample.csv`).
- **Labels.** For each flagged rule: capability present and risky in context; present but benign in context (for example documentation of an unsafe pattern); or not actually present.
- **Protocol.** Two members label independently from a written guideline, then resolve disagreements. Report Cohen's kappa (Cohen, 1960) before resolution.
- **Metrics.** Precision per rule and category. Recall estimated from the no-signal stratum. Every rule change after annotation is re-measured.
- **FMEA ranking.** Severity from the rule file, occurrence from validated prevalence, detection from validated recall. The ranking is presented as a prioritisation aid, not a risk verdict.

## 8. Minimum evidence mapping

| Rubric minimum evidence (question 4) | Artifact | Sprint |
|---|---|---|
| Threat model | Report section and `docs/decisions/` ADR fixing the capability categories | 1 |
| Detection rules | `rules/skill_risk_rules.yaml` with regression tests | 1 to 2 |
| Annotated examples | Annotation guideline, labelled validation sample, kappa and precision tables | 2 |
| False-positive discussion | Error analysis with anonymised excerpts of the main false-positive patterns | 2 to 3 |
| Safe reporting artifact | Aggregate results tables and a report section with no repository names and no runnable payloads | 3 |
| Do not execute untrusted scripts | Static text scanning only; stated in `data/README.md` and the rule file | all |

Borrowed from question 1: similarity method (shingles and Jaccard) with a validation sample of lineage pairs, the reuse distribution (RQ2), and variant change patterns (RQ3 classification).

## 9. Sprint plan

| Sprint | Deliverables | Rubric bullets covered |
|---|---|---|
| Sprint 1 (Sep 17 to Oct 7) | Final research question and threat model; inclusion rules and data dictionary Part B; rule file v1 reviewed; scanner integrated in the pipeline with tests; prevalence table and figure regenerated; ADR on sample only versus full-dataset extension; top threats in THREATS_TO_VALIDITY.md | question, variables, acquisition, first pipeline, exploratory figure, risks |
| Sprint 2 (Oct 8 to Oct 28) | Annotation guideline; two-annotator validation with kappa; precision per rule; rule revisions via PR; reach statistics; RQ3 case-study classification; report method and preliminary results | core implementation, tests, validation design, preliminary results, reviewed PRs |
| Sprint 3 (Oct 29 to Nov 18) | Final prevalence, reach, and drift results; sensitivity checks; error analysis; FMEA ranking; safe-reporting section; release tag; demo | final results, robustness, error analysis, figures, threats, release, demo plan |
| Finalization (Nov 30 to Dec 4) | Respond to feedback; demo: scan a local skill folder and show the report | presentation |

Suggested workstreams, to be chosen through sign-ups and not assigned by me: W1 threat model and related work, W3 scanner and lineage code, W4 statistics, W5 annotation (needs two people), W7 figures, W8 report, W10 FMEA ranking.

## 10. Feasibility

- **Data fit.** Every variable in section 6 exists in the sample. RQ1 and RQ2 need nothing else. RQ3 is scoped to what the sample supports.
- **Compute.** The full pilot runs in about 3 minutes on a laptop, and the tests run offline.
- **Effort.** The hardest part is annotation: about 150 skills, two annotators, roughly 8 to 10 hours each over Sprint 2. Everything else extends existing pilot code.
- **Descope path.** If time runs short, drop the RQ3 extension first, then the regression model. RQ1 with validated rules plus the RQ2 descriptive comparison still meets every question 4 evidence item.

## 11. Risks and competing explanations

| Risk or competing explanation | Mitigation |
|---|---|
| A keyword match is not a capability (skills often describe unsafe patterns to warn against them) | Validation labels distinguish present-and-risky from present-but-benign; only validated precision is reported |
| Template inheritance explains variant differences (9 of 18 pilot differences are one template) | RQ3 classification includes "template update"; report results with and without template families |
| Popularity confound: popular DevOps or setup skills both use shell commands and get copied | Controls in the reach model; stratify by location class and repository stars |
| Sampling by content hash splits variant families, and history is sparse (10 dated pairs) | RQ3 scoped to case studies; optional full-dataset pass decided by ADR |
| Lineage by name and similarity can pair unrelated skills with generic names | Manual check of a sample of lineage pairs; threshold sensitivity |
| Population is a lower bound (default branches, file size, forks) | Stated in threats to validity; no population-level claims beyond the snapshot |
| Annotation disagreement | Written guideline, pilot round of 20, kappa reported before resolution |
| Safety and ethics | Never execute or fetch anything from the dataset; aggregate reporting; no repository or account names in outputs; if something appears actively malicious, stop and raise it with the instructor before any further step |

## 12. Ethics and responsible reporting

The dataset replaces author accounts with anonymised codes, and this project would not try to reverse them. Committed outputs contain no repository names and no runnable payloads. Findings describe categories and rates, not named projects. Scripts are treated strictly as text. AI assistance used in building the pilot and this document is logged in `ai-use-log.md`.

## 13. Self-scores

| Criterion | Score (1 to 5) | Reason |
|---|---|---|
| Feasibility | 4 | Pilot already runs end to end; annotation is the main effort |
| Data fit | 4 | RQ1 and RQ2 fully supported; RQ3 thin in the sample |
| Rubric fit | 5 | Every question 4 minimum evidence item maps to an artifact |
| Low risk | 3 | Validation effort and possible low precision; drift direction may stay inconclusive |

## 14. If the team picks a different topic

The scanner is a feature extractor. It fits question 2 (quality indicators, as risk features), question 3 (staleness, through command patterns), and question 15 (predicting maintenance effort). If none of those win, the pilot module can be removed by a decision record, or kept as a documented optional command.

## References

- G. Destefanis, D. Graziotin, M. Vaccargiu, M. Ortu. "GitSkills: A Dataset of Agent Skills on GitHub." MSR 2027 Mining Challenge. arXiv:2608.10906. doi:10.5281/zenodo.21875637.
- K. Greshake, S. Abdelnabi, S. Mishra, C. Endres, T. Holz, M. Fritz. "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection." AISec 2023. doi:10.1145/3605764.3623985.
- J. O. Kephart, S. R. White. "Directed-Graph Epidemiological Models of Computer Viruses." IEEE Symposium on Security and Privacy, 1991.
- M. Ohm, H. Plate, A. Sykosch, M. Meier. "Backstabber's Knife Collection: A Review of Open Source Software Supply Chain Attacks." DIMVA 2020.
- J. Cohen. "A Coefficient of Agreement for Nominal Scales." Educational and Psychological Measurement 20(1), 1960.

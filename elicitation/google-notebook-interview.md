# Facilitated elicitation: Google Notebook interview

Assignment Phase B. Group 9 interviewed a **Google Notebook** (Gemini Notebook, formerly NotebookLM) built for this study, treating it as a bounded domain-information source: not an oracle, and not a substitute for the dataset. Every important answer was checked against the source the notebook cited and, where it claims something about the data, against the GitSkills sample.

This is the primary Phase B record. The same questions were also put to the repository's own search notebook (`elicitation/notebook-interview.md`); the last field of each block compares the two, and section 6 summarises what that comparison showed.

## 1. Session record

| Item | Value |
|---|---|
| Notebook | "Group 9 · P-01 elicitation notebook (CSC 580 RE)", Google Gemini Notebook, account jeraddu@umich.edu |
| Link | <https://notebook.google.com/notebook/f6dac9ee-331e-498a-afe6-0b7b824602ef> |
| Sources | 24 files uploaded from the pinned pack: 11 authoritative (A1 to A9, preprints as original PDFs), 8 group (G1 to G8), 5 practitioner (P1 to P5). Register and hashes: `elicitation/notebook/SOURCE_REGISTER.md`, `SOURCES_MANIFEST.json`; rebuild with `python scripts/build_notebook_sources.py` |
| Chat configuration | Custom instructions set in **Configure chat**, kept in `elicitation/google-notebook/notebook-instructions.txt`: answer only from the sources, cite every factual sentence, prefer tier A for dataset facts, report disagreements, label inferences, say "Not established by the sources", never advise running dataset scripts or deanonymising authors |
| Interview date | 2026-09-19 |
| Questions | The 15 prepared questions in `elicitation/questions.yaml` plus the 3 follow-ups, asked word for word, in order, in one chat |
| Raw answers | `elicitation/google-notebook/answers.json`, each with a SHA-256 prefix taken from the page, so the text here is provably the notebook's own |
| Interviewers | Jerad Dunne, with Claude Code (Claude Opus 5) driving the browser and drafting the interpretations. Disclosed in `ai-use-log.md` |
| Review | Team interpretations are drafts until a second member reviews this file in the pull request |

## 2. Protocol

1. **One chat, in order, word for word.** Questions were never reworded. Where an answer was incomplete, the prepared follow-up (`NB-Q05a`, `NB-Q07a`, `NB-Q11a`) was asked as a new question.
2. **Capture.** Each answer was taken from the page with its citations. The notebook cites in two ways, and the difference matters:
   - **Grounded citations** (numbered chips that link to a source passage): only NB-Q01 and NB-Q02.
   - **Text citations** (the model writes "[A2, A9]" and a Sources list): every other answer. A text citation names a source but does not point at a passage, so the team had to locate the passage itself.
3. **Verify.** For each answer: open each cited source, find the passage, and decide whether it supports the claim; look for a source that disagrees; and for claims about the data, run the read-only checks in `elicitation/verification-checks.md` (V01 to V18, `python scripts/check_interview_claims.py`). Results are **Verified**, **Partly verified**, **Contradicted**, or **Unverified** (no citation, or the citation does not bear on the claim).
4. **Interpret.** Say what the answer means for P-01 and which `RESEARCH_SPEC.md` requirement it informs.

## 3. Interview record

Answers are quoted from `answers.json`. Long answers are excerpted at the sentences that carry the claim; "…" marks a cut. Two conventions inside a quotation: the notebook's inline citation markers (`[8]`, `[A2, Section II]`) are left out, because the "Source cited by notebook" field lists them; and the notebook's own double quotes appear as single quotes. Nothing else is changed, and the exact text of every answer, with its markers, is in `elicitation/google-notebook/answers.json` with the SHA-256 prefix the page reported.

### NB-Q01

| Field | Record |
|---|---|
| Question | What exactly does one row of the GitSkills `artifacts` table represent, and how should a study count distinct skills separately from copies? Which column marks the representative copy, and is the representative the original source of the content? |
| Notebook answer | "one row of the artifacts table represents a single discovered SKILL.md file occurrence at a specific repository and file path… To count distinct skills separately from verbatim copies, a study can count unique content hashes using the file_sha column or filter for representative rows where dedup_primary = 1… The representative is not assumed to be the original source of the content, as the dataset authors explicitly select one representative per content hash for enrichment using deterministic tie-breaking rules (preferring standard paths like .claude/skills/)." |
| Source cited by notebook | **Grounded**: A2 (Abstract, Section II, Table I, Appendix A), A6 (artifacts config features), A1 (Section "GitSkills"), A9 (Descriptive statistics, Example queries), G2 (Part A.1, data/README.md, FINDINGS_LOG.md) |
| Team interpretation | Confirms the unit of analysis in `RESEARCH_QUESTION.md` section 5: one distinct content (`file_sha`), represented by its `dedup_primary = 1` row, with copies as an outcome (RR-01, DR-02). Because the representative is not the origin, P-01 must not present the representative's repository as the source of a copied skill. |
| Follow-up or uncertainty | None. The 16 copies that also carry text (V03) are a documentation deviation that does not affect counting. |
| Verification | **Verified.** A2 Appendix A ("We do not assume that the representative is the original source"), A9 Schema (`dedup_primary` = 1), A6 Dataset Structure. Data: V01 (29,786 occurrences, 13,000 representatives, 13,000 distinct `file_sha`), V02 (no content has more than one representative). |
| Repo notebook | Same conclusion, from the same three passages. |

### NB-Q02

| Field | Record |
|---|---|
| Question | What population does GitSkills cover, and what does GitHub code search leave out? Does the dataset include files that are not Agent Skills in the October 2025 sense? |
| Notebook answer | "…it leaves out private repositories, non-default branches, files 384 KB or larger, recently active repositories containing 500,000 or more files, and forks unless they have more stars than their parent repository… The dataset does include files that are not agent skills in the October 2025 open specification sense… it retrieved case variants such as skill.md (54,289 files, 1.4% of GitSkills Zenodo 1.0.0), including files with first commits dating back to 2014… only 1,625,701 distinct contents (86.6%) carry valid YAML front matter". |
| Source cited by notebook | **Grounded**: A1 (Section "GitSkills"), A2 (Sections I and II, Appendix A), A4 (Description), A9 (Descriptive statistics, Known limitations, Before the format), A6 |
| Team interpretation | The population is a lower bound (DR-03; threats E1, P8), and pre-format files are inside it, which is why P-01 keeps a front-matter-valid sensitivity subset (RR-04). |
| Follow-up or uncertainty | Consider an exact-basename (`SKILL.md`) sensitivity filter as well as front-matter validity. |
| Verification | **Partly verified.** The counts and the case-variant statistics are exact (A2 Appendix A; A9). One claim is wrong: the sources say code search indexes "recently active repositories with fewer than 500,000 files", so repositories that are **not recently active** are excluded too. The notebook's phrasing keeps only the file-count half of that condition. Data: V04 (378 non-`SKILL.md` names, 1.27% of the sample), V05 (86.9% valid front matter in the sample). |
| Repo notebook | Returned the same limitation passage but never reached the second half of the question; the team found it in A2 page 3. The Google notebook answered both halves. |

### NB-Q03

| Field | Record |
|---|---|
| Question | How is the official GitSkills sample drawn, how does it relate to the full release, and which exact identifiers should a paper cite for the sample and for the full dataset? |
| Notebook answer | "…drawn deterministically by selecting the 13,000 distinct contents with the lowest content hashes along with all their associated occurrences [G2]… allowing SQL queries written for the sample to run unchanged on the full dataset… To cite the full dataset, a paper should reference the MSR 2027 challenge paper by Destefanis et al. (arXiv:2608.10906, DOI 10.48550/arXiv.2608.10906), the GitSkills Zenodo 1.0.0 release (Version DOI 10.5281/zenodo.21875637, Concept DOI 10.5281/zenodo.21875636), and the Hugging Face Parquet mirror… To cite the official sample… specify commit fff3df9 alongside the database file agent_skills_sample.db". |
| Source cited by notebook | Text only: A1 (Section "GitSkills", "Submission"), A2 (Section IV, Appendix A), A4 (Metadata, Description), A6 (Header, Citation), A9 (Header, Descriptive statistics), G1, G2 |
| Team interpretation | This is exactly what DR-01 requires: cite the Zenodo version DOI, the sample commit, and the database hash. It also separates the version DOI from the concept DOI, the distinction that made `data/README.md` mislabel the SpecMine release. |
| Follow-up or uncertainty | The notebook did not mention the file size discrepancy between sources (44 GB on A1 against 41 GB in A9; the Zenodo file is 44,388,249,600 bytes, which is both). Cite bytes. |
| Verification | **Verified.** Identifiers match A4 (record 21875637, version 1.0.0, concept DOI 10.5281/zenodo.21875636) and A9. Sampling rule matches A9 and the data: V06 (largest `file_sha` sits at 0.665% of the hash space, against the 0.692% the rule predicts). |
| Repo notebook | Found the sampling rule but not the identifiers; the team supplied them from A1, A4, and A9. The Google notebook produced them directly. |

### NB-Q04

| Field | Record |
|---|---|
| Question | How do `artifact_siblings` rows join to `artifacts`, which sibling rows carry text, and for which copies of a skill is folder composition recorded? |
| Notebook answer | "Rows in artifact_siblings join to artifacts using a composite key matching repository name and path… Folder composition is recorded exclusively for the single primary representative copy of each distinct skill (dedup_primary = 1)… full text is carried in the content column only for text files that fall under a size cap of up to 100 KB… Sibling rows for binary files, files exceeding the 100 KB size cap, or entries in folders above the listing cap do not carry text and record a skipped_reason instead". |
| Source cited by notebook | Text only: A2 (Section II, Table I, Appendix A), A6 (artifacts and artifact_siblings config features), A9 (artifact_siblings, Example queries), G2 (Part A.1) |
| Team interpretation | The join key and the representative-only rule are what `scan_siblings` implements (FR-04). Script signals therefore describe representatives, not every copy. |
| Follow-up or uncertainty | The last sentence repeats the documentation, and the documentation does not hold in the sample. The scanner must count files it could not read rather than treat them as clean (DR-04). |
| Verification | **Partly verified; contradicted by the data.** Join key, 100 KB cap, and representative-only composition are confirmed (A9 Schema; A6; A2 Section II). But V07: `skipped_reason` is empty on all 47,829 sibling rows, and 16,697 of the 16,768 text-less file rows instead carry `content_fetched = 2`, a value no source documents. V08: 13 sibling rows join a copy, not a representative, against "exclusively… representative". |
| Repo notebook | Returned the same two schema passages and the same documented-but-false `skipped_reason` claim. Both notebooks repeat the documentation; only the data check exposes it. |

### NB-Q05

| Field | Record |
|---|---|
| Question | What do `content_sha_ok`, `composition_truncated`, and `history_fetched` mean, and which values mark missing or unrecoverable data? |
| Notebook answer | "…a value of 1 indicates that the downloaded file bytes reproduce file_sha and 2 indicates the content was repaired via the GitHub blob API… composition_truncated… 1 flags that a representative skill folder exceeded the folder listing cap… history_fetched… covering 458,548 commit histories in the full GitSkills Zenodo 1.0.0 release and 3,010 in sample commit fff3df9… files deleted from GitHub between discovery and content retrieval (comprising 0.9% of distinct contents) were excluded… The specific numerical code for content_sha_ok representing failed or unrecoverable content retrieval is not established by the sources." |
| Source cited by notebook | Text only: A2 (Table I), A4 (Description), A6 (artifacts config features), A9 (How the data was collected), G2 (Part A.1, FINDINGS_LOG.md) |
| Team interpretation | The three columns are defined, and the notebook volunteered the gap about unrecoverable content, which is what the follow-up was for. For P-01, the truncated-listing flag is the consequential one: bundled-script signals are a lower bound for those skills (DR-04, FR-04). |
| Follow-up or uncertainty | It did not quantify truncation. The data does: 1,755 representatives, 13.5%, with a mean of 8.5 bundled files against 2.9 (V10). |
| Verification | **Partly verified.** Definitions and counts confirmed (A9 Schema; A2 Table I; V11 gives 3,010 in the sample). Missed A2 Appendix A, which reports 42 representatives whose original content could not be recovered and says `content_sha_ok` records it. Data: V09 (only values 1 and 2 occur in the sample). |
| Repo notebook | Also stopped at values 1 and 2, and also missed the 42-representative passage until the follow-up. |

### NB-Q05a

| Field | Record |
|---|---|
| Question | Which value of `content_sha_ok` records a representative whose file changed on GitHub before it was fetched and whose original content could not be recovered? |
| Notebook answer | "The sources do not define a value of content_sha_ok for a representative whose file changed on GitHub prior to retrieval and could not be recovered… Additionally, files deleted from GitHub between discovery and content retrieval—comprising 0.9% of distinct contents… were excluded from the dataset entirely rather than retained as incomplete records." Not established: "which value of content_sha_ok (if any exists) records a representative whose file changed on GitHub before it was fetched". |
| Source cited by notebook | Text only: A6 (artifacts config features), A9 (How the data was collected), G2 (Part A.1) |
| Team interpretation | The value is genuinely undocumented, so any full-dataset pass must exclude and count representatives whose value is neither 1 nor 2 (DR-04). The sample is unaffected. |
| Follow-up or uncertainty | The notebook answered "no such value is defined" without finding A2's statement that the column *does* record the case. The team's answer: A2 records the case but names no value. |
| Verification | **Verified** as not established, with an omission: A2 Appendix A ("For 42 representatives the file changed on GitHub between discovery and fetch and the original could not be recovered; content_sha_ok records this") was not cited. Data: V09. |
| Repo notebook | Better here: its second passage was exactly that A2 sentence. The search notebook found the passage; the Google notebook reasoned past it. |

### NB-Q06

| Field | Record |
|---|---|
| Question | What does `first_commit_at` represent for a renamed file, and which rows have commit history at all? |
| Notebook answer | "…first_commit_at records the timestamp when the file was renamed to its current path rather than its original creation date, because commit history tracks only the current path and resets upon a rename… **Inference:** Consequently, first_commit_at provides a lower bound on the true age of renamed skill files… Commit history is collected only for representative skill rows (dedup_primary = 1), specifically covering standard locations such as .claude/skills/ along with a size-stratified sample of other locations… Rows that possess commit history are marked… by history_fetched = 1." |
| Source cited by notebook | Text only: A2 (Section II, Table I, Appendix A), A4, A6, A9 (Known limitations), G2, G4 (Threats I3, I4) |
| Team interpretation | Dates are a lower bound and exist for only 23% of representatives, so RQ3's ordered pairs over-represent canonical skills (FR-06, RR-03; threats P5, I3, I4). |
| Follow-up or uncertainty | Report ordered-pair counts by location class (the RR-03 change). |
| Verification | **Verified.** A9 Known limitations; A2 Table I and Appendix A. Data: V11 (history on 1,755 of 1,762 canonical, 813 of 7,416 skills-dir, 442 of 3,822 other; none on copies; no dates without `history_fetched`). The inference was labelled as one, as the instructions require. |
| Repo notebook | Same passage, same conclusion. |

### NB-Q07

| Field | Record |
|---|---|
| Question | Our question asks whether skills with risk-relevant capabilities reach more repositories through verbatim copying, and whether modified variants add or remove those capabilities. Can the GitSkills sample support each part, and what in the sampling or history coverage limits it? |
| Notebook answer | "The GitSkills sample (commit fff3df9) fully supports evaluating whether skills with risk-relevant capabilities reach more repositories through verbatim copying (RQ2), as it retains all 29,786 file occurrences across 11,841 repositories… For modified variants (RQ3), the sample can identify near-duplicate variant pairs (245 pairs across 141 names…), but it is severely limited… the sample was selected deterministically using the 13,000 lowest content hashes, which splits variant families… leaving only 10 near-duplicate variant pairs with commit dates for both variants… supports statistical regression and reach models for RQ2, but restricts RQ3 to descriptive case studies." |
| Source cited by notebook | Text only: A2 (Sections I, II), A9, G1 (Sections 4, 5.3, 6, 7.3, 7.4), G2 (Part A.1, FINDINGS_LOG F-007, F-008, F-011, F-012), G4 (Threats E2, I3, I4, P5) |
| Team interpretation | The feasibility answer P-01 needs, and correctly sourced: the A-tier sources establish the sample's structure, while the judgement about RQ2 and RQ3 comes from the group's own analysis (RR-02, RR-03). |
| Follow-up or uncertainty | Lifting the RQ3 limit needs the Sprint 1 decision on one streamed full-dataset pass (S1-13). |
| Verification | **Verified.** Every number matches the cited findings: F-011 (245 near-duplicate pairs across 141 names), F-012 (only 10 with dates for both), F-007 (3,010 commit histories), F-008. Sample structure matches A9 and V12. |
| Repo notebook | Weak match: it returned the dataset authors' research directions but no feasibility answer, which is why the follow-up existed. The Google notebook answered it directly and with the right numbers. |

### NB-Q07a

| Field | Record |
|---|---|
| Question | When a distinct content is in the sample, does the sample keep every copy of it across repositories, and are variants of the same skill kept together? |
| Notebook answer | "Yes… the sample retains every verbatim copy of that content across all repositories… However, modified variants of the same skill—which carry different content hashes (file_sha) despite sharing a front-matter name—are not kept together in the sample… variant families are split across the sampling cutoff." |
| Source cited by notebook | Text only: A2 (Section I, Appendix A), A9, G1 (Section 4), G2, G4 (Threats E2, P5) |
| Team interpretation | RQ2 is fully supported on the sample; RQ3 stays descriptive (RR-02, RR-03). |
| Follow-up or uncertainty | None. |
| Verification | **Verified.** A9 "Sample vs full dataset"; data V02, V12 (3,378 contents with 2 or more copies, 2,854 across 2 or more repositories), V13 (542 names shared by 1,631 contents, so families are fragments). |
| Repo notebook | Same on copies; on variants it could only report that no source addresses them, and the team drew the conclusion. The Google notebook stated it outright, correctly. |

### NB-Q08

| Field | Record |
|---|---|
| Question | Do the sources describe any way to link modified (near-duplicate) copies of the same skill, or only byte-identical copies? |
| Notebook answer | "The official GitSkills dataset natively links only byte-identical copies using the git blob content hash (file_sha)… The authoritative dataset sources do not contain a pre-computed column or schema link for modified near-duplicate files… To link modified variants… Group 9's research design introduces a similarity heuristic… word 5-shingle Jaccard similarity… Group 9 explicitly notes that this name-and-similarity pairing is a derived research heuristic rather than a dataset ground truth". |
| Source cited by notebook | Text only: A2 (Section II), A6, A9, G1 (Sections 5.3, 6, 11), G2 (Part B.3, FINDINGS_LOG F-011), G4 (Threat P4), G8 (Module skill_risk) |
| Team interpretation | Lineage is the team's construct, so it must be defined, swept across thresholds, and validated (FR-06, VR-03), and never attributed to the dataset. |
| Follow-up or uncertainty | None. |
| Verification | **Verified.** A2 Section II (identical hashes mean identical bytes); no tier-A source describes near-duplicate linking (checked A1, A2, A4, A6, A9). Group heuristic matches G1 and `skill_risk.family_pairs`; 245 pairs across 141 names matches F-011. |
| Repo notebook | Same conclusion from the same A2 passage. |

### NB-Q09

| Field | Record |
|---|---|
| Question | What loading approach do the sources recommend for the sample and for the full dataset, and what example queries do they give? |
| Notebook answer | "For the official GitSkills sample (commit fff3df9, 277 MB SQLite database…), sources recommend executing direct SQL queries, whereas for the full GitSkills Zenodo 1.0.0 dataset (44,388,249,600 bytes… or Hugging Face Parquet mirror), sources recommend using filtered SQL queries or reading Parquet files with pandas, polars, DuckDB, or the Hugging Face datasets library… For SpecMine… without requiring a full load of the 14.7 GB uncompressed MySQL dump… (SELECT tool, COUNT(*) AS cochange_prs FROM 'data/pull_requests.parquet' WHERE touches_code = 1 GROUP BY tool ORDER BY cochange_prs DESC;)". |
| Source cited by notebook | Text only: A2 (Section IV), A3 (Sections III, V), A4, A6, A7 (Usage), A8a (Quick start), A8c (load.py), A9 (Header, Example queries), G2 |
| Team interpretation | Our loader opens the sample read-only through SQLite (FR-01); any full-dataset pass should stream the Parquet mirror rather than load 44 GB (NFR-04). |
| Follow-up or uncertainty | The tooling list is broader than the GitSkills sources support. Treat "pandas/polars for GitSkills" as the notebook's extrapolation, not a source recommendation. |
| Verification | **Partly verified.** Confirmed: 277 MB sample (A9), 44,388,249,600 bytes (A4), the GitSkills example queries (A9), SpecMine's 14.7 GB dump (A3), and the DuckDB query, which matches A8a word for word. **Unsupported:** "pandas, polars" for GitSkills. Neither word appears in A1, A2, A4, A6, or A9; polars appears only in the SpecMine preprint (A3) and DuckDB for GitSkills only in the group's `data/README.md`. The notebook carried SpecMine's tooling across to GitSkills. |
| Repo notebook | Returned the sampling passage and one example query but missed the loading instructions; the team added them. Both notebooks were incomplete here, in different ways. |

### NB-Q10

| Field | Record |
|---|---|
| Question | Under Group 9's validation protocol, how is a rule match labelled, who rates it, which agreement measure is reported, and what is the blindness rule? |
| Notebook answer | "…each sampled high-risk rule match is labelled as RISKY…, BENIGN_CONTEXT…, or NOT_PRESENT… performed independently by Jerad Dunne (jd) as the primary rater and at least one teammate—Leticia Aderhold (la), Allie Hodges (ah), or Hina Kramer (hk)—as a second rater… The primary agreement measure… is inter-rater Cohen's kappa alongside percent agreement… second raters never open another rater's label files, and the primary rater's filled label files… are committed… only after the second rater's label file for that kind has been committed." |
| Source cited by notebook | Text only: G1 (Section 7.5), G3 (validation README, ANNOTATION_GUIDELINE Sections 2.1 and 5), G4 (Threat P6), G6 (ADR-0006, TEAM_CHARTER Section 9), G7 |
| Team interpretation | This is VR-01 to VR-03 restated correctly, including the three label values that the repo notebook did not surface. |
| Follow-up or uncertainty | The second rater is still unassigned (issue #53), so kappa cannot be computed yet. |
| Verification | **Verified.** Label values match `docs/validation/ANNOTATION_GUIDELINE.md`; raters and blindness rule match `TEAM_CHARTER.md` section 9; "Cohen's kappa and percent agreement" matches `docs/validation/README.md`. |
| Repo notebook | Got raters, kappa, and the blindness rule but not the label values; the team looked those up. The Google notebook had them. |

### NB-Q11

| Field | Record |
|---|---|
| Question | According to Group 9's process documents, what has to happen before a change to a detection rule or to the research question reaches `main`? |
| Notebook answer | "For any change to reach main, Group 9 requires creating a pull request that receives at least one approving review from a team member other than the author and passes all automated CI checks… To change a detection rule, the author must update rules/skill_risk_rules.yaml, add match and no-match test examples enforced by the automated test suite, provide a written rationale… To change the research question, the team must reach agreement at a ceremony, record a decision row in docs/workspace/DECISION_LOG.md, and write an Architectural Decision Record (ADR)… any change to the research question, method, or scope must be explicitly recorded in that sprint's retrospective.md". |
| Source cited by notebook | Text only: G1, G3, G5, G6 (TEAM_CHARTER Sections 6 and 12, DECISION_LOG), G7 (CONTRIBUTING, decision issue form) |
| Team interpretation | Changes to `RESEARCH_SPEC.md` requirements follow the research-change rule: decision issue, ADR for scope changes, reviewed pull request with green CI (NFR-05). |
| Follow-up or uncertainty | It did not mention the recorded deviation: pull request #49 merged under an admin bypass with zero reviews (`docs/sprints/sprint-1/planning.md`). |
| Verification | **Verified.** Matches `CONTRIBUTING.md` (review by a non-author, squash-merge after one approval and green CI) and `PROJECT_PLAN.md` sections 2 and 11 (decision issue, agreement at a ceremony, ADR, retrospective line). |
| Repo notebook | **Failed this question**: it returned the research question itself, and the team had to ask a follow-up. This is the clearest win for the Google notebook. |

### NB-Q11a

| Field | Record |
|---|---|
| Question | What are the change management rules for research changes and process changes, and what review does every pull request need before it merges? |
| Notebook answer | "…research changes… team agreement recorded in docs/workspace/DECISION_LOG.md, an Architectural Decision Record (ADR)… and an explicit entry in that sprint's retrospective.md… Process changes are tracked as kaizen issues… logged in docs/lean-six-sigma/KAIZEN_BACKLOG.md… team charter modifications require approval from all other team members in a pull request… Before any pull request can be merged into main, it requires a green automated CI build and exactly one approving review from a team member other than the author." |
| Source cited by notebook | Text only: G1, G3, G5 (Sections 1, 2, 4, 6, 7, KAIZEN_BACKLOG), G6 (TEAM_CHARTER Sections 6, 12, 13, DECISION_LOG, ADR-0006), G7 |
| Team interpretation | Confirms NFR-05 and adds the charter rule (all members must approve a charter change). |
| Follow-up or uncertainty | "Exactly one" is the minimum, not a cap (`project.yml`: `min_reviewers: 1`). Same omission of the admin bypass. |
| Verification | **Verified.** `PROJECT_PLAN.md` section 11, `CONTRIBUTING.md`, `TEAM_CHARTER.md` sections 12 and 13, and `KAIZEN_BACKLOG.md`. |
| Repo notebook | Also correct here; the two agree. |

### NB-Q12

| Field | Record |
|---|---|
| Question | What anonymisation was applied to commit authors and commit messages, what was left unanonymised, and what must a study never do with author codes or personal data? |
| Notebook answer | "…commit author accounts were anonymised by replacing them with keyed one-way codes… In commit messages, personal names and email addresses were redacted… bot accounts retained their logins, AI assistant names in Co-authored-by trailers were preserved, and repository owner logins remained unanonymised… Studies are strictly prohibited from attempting to deanonymise author codes, reverse the one-way hash transformations, or link author codes to real-world identities… researchers must never publish personal data, include individual account/repository names in published outputs, or paste dataset content containing personal data into external AI tools". |
| Source cited by notebook | Text only: A2 (Section IV, Appendix A), A4, A6 (repos config features), G2 (data/README.md, Part A.1), G4 (Threat X1), G6 (TEAM_CHARTER Section 11), G7 |
| Team interpretation | ER-02: never reverse or link author codes, and never write repository names, account names, author codes, or bot logins to an output. The notebook's point that **repository owner logins are not anonymised** is a useful addition: the `repos` table names owners, so outputs must aggregate. |
| Follow-up or uncertainty | It states the prohibition but attributes part of it to A4, which does not contain one; the prohibition is in A1's FAQ ("The share or use of personally identifiable information (PII) is strictly prohibited") and in `data/README.md`. |
| Verification | **Partly verified.** Anonymisation facts confirmed (A2 Section IV; A6; A9; A4). Attribution error as above. It also did not report the disagreement between sources, although its instructions require that: A2 Appendix A says personal names in trailer lines were replaced with keyed codes, while A6 and A9 say a fixed marker. The data settles it: V15 (130 human co-author names appear as the fixed marker, none as a 16-character code); V14 (no email-like strings in 6,020 messages). |
| Repo notebook | Returned the same A6 and A9 passages and also did not flag the conflict; the team found it while verifying. Neither notebook applied the "report disagreements" rule. |

### NB-Q13

| Field | Record |
|---|---|
| Question | What license covers the GitSkills metadata and the skill `content` text, what does that mean for quoting skill text in a report, and is it safe to run the scripts bundled with skills? |
| Notebook answer | "The GitSkills metadata and dataset aggregation are released under the Creative Commons Attribution 4.0 International (CC-BY-4.0) license… the skill content text… remains governed by the individual origin repository's license recorded in repos.license… researchers must consult repos.license and quote text minimally only when necessary, excluding runnable payloads and personal data… It is strictly unsafe to run scripts bundled with skills, as skills and bundled files are copied without formal review and may contain untrusted or malicious commands… Group 9 rules therefore mandate treating all skill content purely as static text". |
| Source cited by notebook | Text only: A1 (Section "GitSkills"), A4 (License), A6 (License), G1, G2 (Licensing and ethics), G4 (Threats R6, R09, X2), G7 |
| Team interpretation | ER-01 and ER-03: quote short excerpts only, from permissively licensed repositories, never runnable payloads; never execute anything from the dataset. |
| Follow-up or uncertainty | The licensing consequence is bigger than the notebook says, and only the data shows it: 7,734 of 13,000 representatives (59.5%) come from repositories with no license or NOASSERTION (V17), so most skill text cannot be quoted at all. |
| Verification | **Partly verified.** Licensing confirmed (A6 License; A4 metadata `cc-by-4.0`). The group rules are correctly cited (FMEA R09; threats R6 and X2; `data/README.md`). But "strictly unsafe" is not a tier-A statement: A1 says only that skills can instruct agents to run commands and are copied without formal review. The notebook presented an inference as a sourced fact, against its instructions. |
| Repo notebook | Returned the same A6 License passage and the group's ethics rows, and also did not find a tier-A safety statement, because none exists. |

### NB-Q14

| Field | Record |
|---|---|
| Question | Do the sources define what counts as a "script" for `has_scripts`, or what makes a skill instruction risky or malicious? |
| Notebook answer | "…they do not state the specific file extensions or parsing criteria used to classify a file as a script… Group 9 operationalizes 'risk-relevant capabilities'… through a static scanner of 19 regular expression rules across 12 capability categories… classifying rules with severity 6 or higher… as high-risk signals… a rule match is merely a text signal… not a verdict that the instruction is malicious… Group 9's threat model explicitly excludes judging author intent". Not established: "the exact file extensions or criteria used by the GitSkills dataset authors… and any definition or criteria for determining whether an instruction is intentionally malicious." |
| Source cited by notebook | Text only: A2 (Table I, Section II), A6, G1 (Sections 6, 7, 8), G2, G3 (rules file), G4 (Threat P1) |
| Team interpretation | Both constructs are the team's own (FR-02, FR-04, RR-01), so they must be validated by annotation (VR-01) and never attributed to the dataset. |
| Follow-up or uncertainty | The two definitions nearly agree but not exactly: V18 shows 57 representatives with `has_scripts` = 0 that still contain a file with a P-01 script extension. The report must say which definition each number uses. |
| Verification | **Verified as not established.** No definition in A1, A2, A4, A6, or A9. The group figures are exact: 19 active rules and 12 categories (`rules/skill_risk_rules.yaml`; `ANALYSIS_MANIFEST.json` `rules_active` = 19), severity cutoff 6. |
| Repo notebook | Same conclusion; it returned the A6 and A2 passages that mention `has_scripts` without defining it. |

### NB-Q15

| Field | Record |
|---|---|
| Question | Do the sources establish that a copy of a skill in a repository is actually loaded or run by an agent there, so that a copy count measures use? |
| Notebook answer | "The sources do not establish that a copy of a skill in a repository is actually loaded or run by an agent, as the GitSkills dataset is a static repository corpus that does not track dynamic agent execution logs… an agent loads a skill probabilistically at run time when it compares a task against the skill's description… **Inference:** A high copy count demonstrates widespread folder copying or template distribution across repositories, but does not prove that an agent has ever executed the skill in practice." |
| Source cited by notebook | Text only: A1, A2 (Abstract, Section I), A4, A9, G1, G2, G4 (Threat C1) |
| Team interpretation | RR-02's interpretation boundary: reach is the spread of identical content, not use or exposure. The report must not say risky skills are "used more". |
| Follow-up or uncertainty | Its citation of threat C1 is loose: C1 is marked "Not applicable" for P-01 because copies are used as reach, not as a quality proxy. The substance is right. |
| Verification | **Verified as not established.** A2 Abstract and Section I describe probabilistic loading at run time; no source or column records that a skill was loaded. |
| Repo notebook | Same conclusion from the same A2 passages. |

## 4. Summary

| Result | Count | Questions |
|---|---:|---|
| Verified | 12 | Q01, Q03, Q05a, Q06, Q07, Q07a, Q08, Q10, Q11, Q11a, Q14, Q15 (Q05a, Q14, and Q15 verified as *not established*) |
| Partly verified | 6 | Q02, Q04, Q05, Q09, Q12, Q13 |
| Unverified | 0 | Every answer carried at least a text citation |
| Total | 18 | 15 prepared questions and 3 follow-ups |

One of the partly verified answers is also **contradicted by the data**: Q04 repeats the documented `skipped_reason` behaviour, which never occurs in the sample (V07), and claims folder composition is recorded exclusively for representatives, while 13 sibling rows join a copy (V08).

Where the notebook fell short of its own instructions:

1. **Grounded citations stopped after two answers.** Q01 and Q02 carry citation chips that link to passages; from Q03 on, the notebook wrote source lists as plain text. A text citation names a file but not a passage, so the team had to locate each one.
2. **One wrong restatement** (Q02: the code-search exclusion condition).
3. **One unsupported recommendation** (Q09: pandas and polars for GitSkills, which only the SpecMine preprint mentions).
4. **One inference presented as a sourced fact** (Q13: "strictly unsafe", attributed to A1).
5. **One attribution error and one missed conflict** (Q12: the prohibition attributed to A4; the A2-versus-A6/A9 disagreement about trailer names never reported, though rule 3 requires it).

What it did well: it never invented a number. Every figure checked out, including ones from the group's own findings log (245 pairs across 141 names; 10 dated pairs; 3,010 commit histories). It volunteered gaps, answered "not established" three times, and labelled its inferences.

## 5. What the interview changed in the requirements

Same as the repository interview, and nothing contradicts it (`RESEARCH_SPEC.md`):

| Finding | Requirement |
|---|---|
| Cite the Zenodo version DOI, concept DOI, sample commit, and file hash | DR-01 |
| `content_fetched = 2`, empty `skipped_reason`, and truncated listings leave bundled files unread | DR-04, FR-04 |
| The representative is not the origin; copies measure spread, not use | RR-01, RR-02 |
| The sample splits variant families; dated pairs are mostly canonical skills | RR-03, FR-06 |
| "Script", "risky", and "lineage" are the team's constructs | FR-02, FR-06, VR-01, VR-03 |
| Skill text keeps its origin repository's license; owner logins are not anonymised | ER-01, ER-02 |

## 6. The two notebooks compared

Both notebooks were given the same 24 sources and the same 18 questions.

| | Google Notebook | Repository search notebook |
|---|---|---|
| How it answers | Generates prose from the sources | Quotes the passages that match, verbatim |
| Citations | Grounded chips for 2 answers, text-only for 16 | A locator for every passage, always |
| Reproducible | No: the same question can produce different wording | Yes: same pack, same question, same answer |
| Answered the question asked | 17 of 18 | 15 of 18 (Q07 weak, Q09 incomplete, Q11 off target) |
| Errors found in verification | 5 (listed in section 4) | 0 of fact; its failures are misses, not mistakes |
| Best moments | Q11 change control, Q07 feasibility with exact numbers, Q10 label values | Q05a: found the A2 passage on the 42 unrecoverable representatives that Google reasoned past |

The two are complementary, and the difference is the point of Phase B: a generative notebook answers the question you asked but can quietly overstate a source, while a search notebook cannot overstate anything but will sometimes hand you the wrong passage. Neither replaces reading the source, and neither replaces the dataset: four of the findings that changed requirements came from the data checks (V07 to V18), which no notebook could have produced.

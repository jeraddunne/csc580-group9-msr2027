# ADR-0007: Move the analysis to the full GitSkills dataset

- **Status:** Proposed. The Product Owner chose option 4 on 2026-09-28. The record becomes Accepted when a member other than the author approves the pull request and it merges. The change to the research question also needs the instructor's approval (final submission checklist: "The selected question and dataset are approved").
- **Date:** 2026-09-28
- **Deciders:** Jerad Dunne (Product Owner); review by Leticia Aderhold; approval of the changed question by the instructor
- **Decision issue:** #67 (Sprint 1 planning item S1-13)
- **Affects research question / method / scope:** yes. The population of RQ1, RQ2, and RQ3 changes from the official sample to the full July 2026 release. Record it in the Sprint 1 retrospective.

## Context

**Why a decision is required now.** The proposal (P-01 section 7.3) left open whether to go beyond the official sample. Four documents make any full-dataset work conditional on an ADR in Sprint 1: `PROJECT_PLAN.md` section 2 (out of scope unless approved), `RESEARCH_SPEC.md` NFR-04 ("requires an ADR first"), FMEA risk R01 (RPN 126), and the open question in the decision log, due at check-in 2 on Thu 2026-10-01.

**What the sample gives today.** The sample is the 13,000 distinct contents with the lowest hashes, out of 1,877,981: a fraction f = 0.69%. RQ1 and RQ2 have enough rows in it, but every estimate describes a 0.69% slice. RQ3 is thin, because a pair of variants is in the sample only if both variants are, so the sample holds an expected f² = 0.0048% of the population's same-name pairs. From `results/rq3_summary.csv` and `results/rq3_threshold_sweep.csv` at similarity 0.5:

| Measure | Sample | Full dataset, extrapolated by 1/f² |
|---|---:|---:|
| Same-name near-duplicate pairs | 245 in 141 families | about 5 million |
| Pairs whose high-risk categories differ | 18 in 6 families | hundreds of thousands |
| Pairs with a first-commit date on both variants (ordered) | 10 | about 200,000 |
| Ordered pairs where the newer variant adds / drops a category | 1 / 0 | not estimable from 1 |

The extrapolations assume the hash sample is uniform with respect to content, as the sample README states. They are orders of magnitude, not measurements.

**What the full run costs.** Measured on 2026-09-28 on the Product Owner's laptop (16 logical cores, 15.6 GB RAM, 2.0 GB free at the time):

| Item | Measurement | How |
|---|---|---|
| Download, Parquet mirror | `artifacts` 6.45 GB (31 files), `artifact_siblings` 6.96 GB (45 files), `repos` 0.02 GB (1 file): 13.43 GB | Hugging Face API, dataset revision `ebab17454a7c236f8f26b183567f1a126f42e3f8` (last modified 2026-09-11); re-checks F-006 |
| Download, SQLite alternative | 44,388,249,600 bytes | Zenodo record 21875637 |
| SKILL.md text in memory | 93.4 MB for 12,965 sample contents; about 13.5 GB for the population | character count on the sample, scaled by 1/f |
| Bundled-script text in memory | 131.4 MB for 22,278 sample files; about 19 GB for the population | same |
| SKILL.md scan time | 67.9 s on the sample; about 164 minutes on one process | `skill_risk.scan_contents`, scaled by 1/f |
| Bundled-script scan time | 28.7 s on the sample; about 69 minutes on one process | `skill_risk.scan_siblings`, scaled by 1/f |
| Largest name families | `code-review` 37, `commit` 29, `skill-creator` 22 in the sample; about 5,300, 4,200, and 3,200 in the population | pipeline family key, scaled by 1/f |

Three consequences follow from the table. First, the text does not fit in memory, so `analysis.run_analysis`, which loads every representative's text into one DataFrame, cannot run unchanged; the build must stream (NFR-04 already requires this). Second, `skill_risk.family_pairs` skips any family with more than 200 variants, which in the population would drop `code-review`, `commit`, and `skill-creator`, the family that holds 9 of the 18 differing pairs in the sample; the pairing needs new code. Third, disk space is not a constraint (735 GB free), but the repository lives in a OneDrive-synced folder, so the data must go to an `MSR_DATA_DIR` outside it.

**Validation carries over.** The validation samples (147 signal items, 58 lineage pairs, 18 drift pairs) were drawn from the official sample. Because the sample is a hash-uniform subset of the population, an item drawn from it is a random draw from the population, so the precision and agreement estimates apply to the full dataset as long as the rules and the pair definition do not change. The new pairing code must therefore produce the same pairs as the exact method (see the build plan, step 4).

## Options considered

1. **Sample only.** RQ3 stays descriptive, as `RESEARCH_QUESTION.md` section 7 and RR-03 state.
   - Pros: no new code or data; the pipeline stays under 15 minutes (100.5 s in the last `ANALYSIS_MANIFEST.json`); frees time for validation.
   - Cons: every estimate describes 0.69% of the population; RQ3 cannot address the direction of drift.
2. **Sample plus one streamed pass over the full `artifacts` table, limited to the families that differ in the sample** (P-01 section 7.3).
   - Pros: smallest download (6.45 GB); adds dated pairs for those families.
   - Cons: selecting families because they differ means the result cannot estimate how often drift happens; `skill-creator` exceeds the family cap, so the pairing code must change anyway.
3. **RQ3 over the whole population; RQ1 and RQ2 stay on the sample.**
   - Pros: fixes the thinnest research question.
   - Cons: two populations in one report, and the stream, scan, and pairing work is nearly all of option 4's work.
4. **All three research questions on the full dataset, including bundled scripts.**
   - Pros: estimates describe the population instead of a 0.69% slice; RQ3 gains enough dated pairs to consider a test of direction; one population across the report; the validation samples still apply.
   - Cons: a new streamed build, a download of 13.43 GB, a run measured in hours rather than minutes, and a change to the research question that needs the instructor's approval.

The first draft of this record, written on 2026-09-28, recommended option 1 on workload grounds. The Product Owner chose option 4.

## Decision

**Option 4.** RQ1, RQ2, and RQ3 run on the full GitSkills July 2026 release, including the `artifact_siblings` table for bundled scripts. The official sample stays in the repository as the fast path for development, tests, CI, and a quick reproduction check.

Reasons:

- The question is about how risk-relevant capabilities spread through copying. The population answers that; a 0.69% slice only estimates it.
- RQ3 needs pairs, and the sample holds about 1 in 21,000 of them.
- The validation already done or planned on the sample applies to the full population, so the switch does not waste labelling effort.
- Every column the analysis uses exists in the full release with the same schema, and the download fits a laptop.

The research question becomes:

> In the GitSkills July 2026 release, how prevalent are skill instructions and bundled scripts that enable risk-relevant capabilities, do skills carrying them reach more repositories through verbatim copying, and do modified variants of the same skill add or remove those capabilities?

## Build plan

Each step is its own issue and pull request, with tests, in Sprint 2.

1. **Acquisition.** Extend `scripts/download_samples.py` with a `--full` mode that downloads the `artifacts`, `artifact_siblings`, and `repos` Parquet files from Hugging Face at the pinned revision above into `MSR_DATA_DIR` (outside OneDrive, for example `C:\msr-data`), verifies each file's size and SHA-256, and writes `MANIFEST_FULL.json`. It never executes anything from the data.
2. **Loader.** Give `load.query_gitskills` a DuckDB backend that exposes views named `artifacts`, `artifact_siblings`, and `repos` over the Parquet files, so the existing SQL runs unchanged. Text columns are read in record batches, never whole.
3. **Scan stage.** Scan SKILL.md text and bundled scripts batch by batch with parallel workers. Write a text-free scan table (`file_sha`, `rule_ids`, `high_risk_categories`, and the control variables) to Parquet, resumable per input file. Test: on the sample, the streamed scan equals `scan_contents` and `scan_siblings` row for row.
4. **Pairing.** Generate candidate pairs within each family with MinHash and locality-sensitive hashing, and keep a candidate only after an exact word-shingle Jaccard check. Test: on the sample, the new code finds exactly the 332 pairs the current code finds at a threshold of 0.3.
5. **Statistics stage.** Run RQ1 to RQ3 and the sensitivity checks on the text-free table (about 1.88 million rows). Check the runtime of the NB2 model and the bootstrap. With n near 1.9 million, almost every test is significant, so the report leads with effect sizes and confidence intervals (rank-biserial correlation, incidence rate ratio), as H2 already specifies.
6. **Commands and outputs.** `make pipeline` stays the sample run (CI, under 15 minutes, NFR-04). A new `make pipeline-full` runs steps 1 to 5 and writes to `results/full/` and `figures/full/`. `ANALYSIS_MANIFEST.json` records the dataset revision, runtime, and peak memory.

## Consequences

- **Positive:** population-level answers to all three research questions; RQ3 can move from case studies towards a direction analysis; one population throughout the report.
- **Negative / risks:**
  - The build and the full run compete for the same person's time as round 1 labelling (signals and lineage, due 2026-10-13) and round 2 (D-022).
  - A new user reproducing the primary results (Sprint 3 acceptance) now needs a 13.43 GB download and an hours-long run. The README must say so, and the fresh-machine reproduction (#37) must be planned for it.
  - The full run hits R01's failure modes (downloads, out-of-memory). R01 moves from "avoid" to "mitigate": streamed build, pinned revision, data outside OneDrive, resumable stages.
  - The dataset maintainers could update the mirror; the pinned revision and `MANIFEST_FULL.json` guard against that (THREATS R1).
- **Documents to update in the same pull request as the build, or before it:** `RESEARCH_QUESTION.md` (question wording, population, sample rows in section 5), `RESEARCH_SPEC.md` (NFR-04 adds the full run; requirement wording that says "sample"), `DATA_DICTIONARY.md`, `data/README.md` (acquisition of the full release), `PROJECT_PLAN.md` section 2, `THREATS_TO_VALIDITY.md` (E2 and P8 lose the sample fraction; P5 changes with the number of dated pairs; a note on significance at large n), `docs/lean-six-sigma/FMEA_RISK_REGISTER.md` (R01), `docs/workspace/FINDINGS_LOG.md` (F-006 re-checked; the measurements above), and the report.
- **Before the full run:** decide whether RQ3 gains a test of direction, and write it into `RESEARCH_QUESTION.md` section 7 before seeing full-dataset results.
- **Follow-up issues:** one per build step, milestone Sprint 2; #31 and #32 for the report and threats.

## Timeline and fallback

| Date | Milestone |
|---|---|
| Thu 2026-10-01 | This ADR merged; instructor informed and asked to approve the changed question |
| Wed 2026-10-07 | Sprint 1 review records the scope change; Sprint 1 pipeline evidence stays the sample run |
| Tue 2026-10-21 | Full run complete (build steps 1 to 6) |
| Wed 2026-10-28 | Sprint 2 review presents full-dataset preliminary results |

Fallback: if the full run is not complete by 2026-10-21, the Sprint 2 review presents the sample results as preliminary and the full run moves to Sprint 3.

## Revisit trigger

- The instructor does not approve the changed question or dataset: supersede this record and return to option 1.
- The full run is not complete by 2026-10-21: apply the fallback above; if it is still not complete by 2026-11-04, supersede this record with option 1 so Sprint 3 has stable results.
- The pairing test in step 4 does not reproduce the sample's pair set: fix the pairing before any full-dataset RQ3 result is reported.
- Peak memory of the full run exceeds what the laptop has free: reduce the batch size before changing scope.

# ADR-0007: Keep the official sample as the population for RQ1 to RQ3

- **Status:** Proposed. The Product Owner chose option 1 on 2026-09-28. The record becomes Accepted when a member other than the author approves the pull request and it merges.
- **Date:** 2026-09-28
- **Deciders:** Jerad Dunne (Product Owner); review by Leticia Aderhold, with comments from Hina Kramer
- **Decision issue:** #67 (Sprint 1 planning item S1-13)
- **Affects research question / method / scope:** yes (scope). The research question and population stay as they are; the full-dataset extension that P-01 left open is dropped for the course. Record it in the Sprint 1 retrospective.

## Context

**Why a decision is required now.** The proposal (P-01 section 7.3) left open whether to go beyond the official sample. Four documents make any full-dataset work conditional on an ADR in Sprint 1: `PROJECT_PLAN.md` section 2 (out of scope unless approved), `RESEARCH_SPEC.md` NFR-04 ("requires an ADR first"), FMEA risk R01 (RPN 126), and the open question in the decision log, due at check-in 2 on Thu 2026-10-01.

**What the assignment asks for.** The Sprint 1 acceptance criteria say "the pipeline runs on an approved sample", and Sprint 2's say "the core implementation runs end to end on the approved sample". The final submission checklist asks that "the selected question and dataset are approved". The research question, as approved, names the sample: "In the GitSkills July 2026 sample, ...".

**What the sample gives today.** The sample is the 13,000 distinct contents with the lowest hashes, out of 1,877,981: a fraction f = 0.69%. RQ1 and RQ2 have enough rows in it. RQ3 is thin, because a pair of variants is in the sample only if both variants are, so the sample holds an expected f² = 0.0048% of the population's same-name pairs. From `results/rq3_summary.csv` and `results/rq3_threshold_sweep.csv` at similarity 0.5:

| Measure | Sample | Full dataset, extrapolated by 1/f² |
|---|---:|---:|
| Same-name near-duplicate pairs | 245 in 141 families | about 5 million |
| Pairs whose high-risk categories differ | 18 in 6 families | hundreds of thousands |
| Pairs with a first-commit date on both variants (ordered) | 10 | about 200,000 |
| Ordered pairs where the newer variant adds / drops a category | 1 / 0 | not estimable from 1 |

The extrapolations assume the hash sample is uniform with respect to content, as the sample README states. They are orders of magnitude, not measurements.

**What a full-dataset run would cost.** Measured on 2026-09-28 on the Product Owner's laptop (16 logical cores, 15.6 GB RAM, 2.0 GB free at the time):

| Item | Measurement | How |
|---|---|---|
| Download, Parquet mirror | `artifacts` 6.45 GB (31 files), `artifact_siblings` 6.96 GB (45 files), `repos` 0.02 GB (1 file): 13.43 GB | Hugging Face API, dataset revision `ebab17454a7c236f8f26b183567f1a126f42e3f8` (last modified 2026-09-11); re-checks F-006 |
| Download, SQLite alternative | 44,388,249,600 bytes | Zenodo record 21875637 |
| SKILL.md text in memory | 93.4 MB for 12,965 sample contents; about 13.5 GB for the population | character count on the sample, scaled by 1/f |
| Bundled-script text in memory | 131.4 MB for 22,278 sample files; about 19 GB for the population | same |
| SKILL.md scan time | 67.9 s on the sample; about 164 minutes on one process | `skill_risk.scan_contents`, scaled by 1/f |
| Bundled-script scan time | 28.7 s on the sample; about 69 minutes on one process | `skill_risk.scan_siblings`, scaled by 1/f |
| Largest name families | `code-review` 37, `commit` 29, `skill-creator` 22 in the sample; about 5,300, 4,200, and 3,200 in the population | pipeline family key, scaled by 1/f |

The text does not fit in memory, so `analysis.run_analysis` cannot run unchanged on the full release, and `skill_risk.family_pairs` skips any family with more than 200 variants, which in the population would drop `skill-creator`, the family that holds 9 of the 18 differing pairs in the sample. A full run therefore needs a new streamed build, not just a bigger input file.

**People and dates.** Under D-022, Jerad Dunne is the only rater for lineage and signals: round 1 is due 2026-10-13, round 2 at least 14 days later, and scoring on 2026-10-27. Leticia Aderhold's drift labels are due 2026-10-16. Sprint 2 closes on 2026-10-28. P-01 section 10 says: "If time runs short, drop the RQ3 extension first."

## Options considered

1. **Sample only.** RQ3 stays descriptive, as `RESEARCH_QUESTION.md` section 7 and RR-03 state: counts at each threshold, with and without template families, ordered pairs split by location, and manually classified case studies.
   - Pros: meets every sprint acceptance criterion as written; the question and dataset stay as approved; no new code or data; the pipeline stays under 15 minutes (100.5 s in the last `ANALYSIS_MANIFEST.json`); the time goes to validation.
   - Cons: every estimate describes 0.69% of the population; RQ3 cannot address the direction of drift.
2. **Sample plus one streamed pass over the full `artifacts` table, limited to the families that differ in the sample** (P-01 section 7.3).
   - Pros: smallest download (6.45 GB); adds dated pairs for those families.
   - Cons: selecting families because they differ means the result cannot estimate how often drift happens; `skill-creator` exceeds the family cap, so the pairing code must change anyway.
3. **RQ3 over the whole population; RQ1 and RQ2 stay on the sample.**
   - Pros: fixes the thinnest research question.
   - Cons: two populations in one report, and the stream, scan, and pairing work is nearly all of option 4's work.
4. **All three research questions on the full dataset, including bundled scripts.**
   - Pros: estimates describe the population instead of a 0.69% slice; RQ3 gains enough dated pairs to consider a test of direction.
   - Cons: a new streamed build, a 13.43 GB download, a run measured in hours, and a changed research question that needs the instructor's approval again.

How the decision was reached, all on 2026-09-28: the first draft of this record recommended option 1; the Product Owner first chose option 4, then chose option 1 for the course and kept option 4 as future work (see below). Revised on 2026-10-06 after review: the future-work section now separates what the signal and pair validation would carry over (Leticia Aderhold), and Consequences records the template sensitivity of RQ3 (Hina Kramer).

## Decision

**Option 1.** RQ1, RQ2, and RQ3 use the official GitSkills sample only. No full-dataset pass is part of the course project.

Reasons:

- The sample meets the assignment: every sprint acceptance criterion is written against an approved sample, and the question as approved names it.
- A defensible full run needs a new streamed build and new pairing code, which competes with validation for the same person's time in Sprint 2.
- Validation gates every headline claim (H1, rule precision, agreement), so that is where the time goes.

## Consequences

- **Positive:** the population, the research question, and the pipeline stay as approved; the pipeline stays reproducible on a laptop in under 15 minutes; risk R01 is closed by decision rather than by vigilance.
- **Negative / risks:** RQ3 claims no drift rate and no direction. The report says so in Results and in Threats to validity (P5, E2), with the sample fraction and the pair extrapolation above.
- **RQ3 is sensitive to template families.** At threshold 0.5 (`results/rq3_summary.csv`), excluding template families halves the differing pairs from 18 to 9 (families with a difference: 6 to 5), and the only dated pair in which the newer variant adds a high-risk category disappears: 1 of 10 ordered pairs becomes 0 of 9. One template therefore carries both the largest share of the differences and the only directional observation, which is a further reason to keep RQ3 descriptive and to report it with and without template families.
- **Follow-up on acceptance:**
  - `docs/workspace/DECISION_LOG.md`: set D-023 to Agreed with the date.
  - `docs/lean-six-sigma/FMEA_RISK_REGISTER.md` R01: status "Closed by ADR-0007".
  - `RESEARCH_SPEC.md` NFR-04: add ADR-0007 to the trace.
  - `docs/workspace/FINDINGS_LOG.md`: mark F-006 re-checked on 2026-09-28, and add the measurements above as a finding.
  - Report: the future work below goes into "Conclusion and future work", and the RQ3 limitation into Threats to validity (#31, #32).
  - Sprint 1 retrospective: record this as a scope decision.

## Future work: what a full-dataset study would need

The report outline asks what a larger study should do next. This is the plan, kept here so the measurements are not lost.

**What the validation would and would not carry over.** The signal validation would carry over: the sample is a hash-uniform subset of the population, and each of the 147 signal items is drawn at random within its stratum, so the per-rule and per-category precision and the miss rate would still estimate the full release as long as the rules stay unchanged. The pair validation is not established to carry over in the same way. A pair is in the sample only when both of its variants are (roughly f², about 0.005% of population pairs); pairs that share a variant are not independent draws; the sample splits variant families (`elicitation/google-notebook-interview.md`); and the 18 drift pairs are every pair whose high-risk categories differ at threshold 0.5, not a random draw of pairs. The 58 lineage pairs and 18 drift pairs may therefore inform a full-dataset study, for example as worked examples and a first estimate of lineage precision, but whether their precision and agreement apply to the full release would need to be reassessed, ideally on pairs sampled from the full release, before any full-release claim about lineage or drift.

**Build steps.**

1. **Acquisition.** Download the `artifacts`, `artifact_siblings`, and `repos` Parquet files at the pinned revision above into an `MSR_DATA_DIR` outside any synced folder, verify size and SHA-256, and write a manifest. Never execute anything from the data.
2. **Loader.** A DuckDB backend for `load.query_gitskills` with views named `artifacts`, `artifact_siblings`, and `repos` over the Parquet files, so the existing SQL runs unchanged; text columns read in record batches.
3. **Scan stage.** Scan SKILL.md text and bundled scripts batch by batch with parallel workers, writing a text-free scan table to Parquet, resumable per input file. Test: on the sample, the streamed scan equals `scan_contents` and `scan_siblings` row for row.
4. **Pairing.** MinHash with locality-sensitive hashing for candidate pairs within each family, each candidate kept only after an exact word-shingle Jaccard check. Test: on the sample, it finds exactly the 332 pairs the current code finds at a threshold of 0.3.
5. **Statistics stage.** RQ1 to RQ3 on the text-free table of about 1.88 million rows, leading with effect sizes and confidence intervals, since nearly every test is significant at that size.
6. **Commands and outputs.** `make pipeline` stays the sample run; a separate `make pipeline-full` writes to `results/full/` and records the dataset revision, runtime, and peak memory.

Before a full run, decide whether RQ3 gains a test of direction, and write it into the research question before seeing full-dataset results.

## Revisit trigger

- The instructor asks for population-level results.
- The project continues after the course (for example, towards a Mining Challenge submission): open a new ADR for option 4 using the future-work plan above.
- Drift validation (`jd` and `la`) shows that most sample pairs are not the same skill: RQ3 then needs a redesign whatever the data source.

# Label-based reach comparison — issue #27

This analysis describes copy counts within the selected round 1 signal-validation sample. It does not estimate population prevalence.

## Reproduction

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe scripts\label_based_reach.py
```

Inputs:
- `data/annotations/signals_jd_r1.csv`
- Local database: `data/samples/agent_skills_sample.db`

Outputs:
- `results/label_based_reach.csv`
- `results/label_based_reach_metadata.json`

The metadata records the input checkout commit, input and script SHA-256 checksums, Python and pandas versions, and join checks. The database remains local.

## Method

Aggregate annotations once per `file_sha`. Classify contents by whether any recorded finding is RISKY, whether they have a NONE_PRESENT judgment, or whether they are flagged contents with no recorded RISKY finding.

Join these groups to copy counts calculated by the existing `copy_counts` function. Copies are the number of artifacts rows per `file_sha`, not the number of distinct repositories.

The script rejects missing content keys, duplicate annotation keys, duplicate copy-count keys, unmatched contents, and mixed NONE_PRESENT/other labels.

## Observed results — November 12, 2026

| Group | Contents | Mean copies | Median copies |
|---|---:|---:|---:|
| At least one recorded RISKY finding | 61 | 2.508197 | 1 |
| Flagged sample: no recorded RISKY finding | 46 | 2.695652 | 1 |
| No-signal sample: NONE_PRESENT judgment | 40 | 1.275000 | 1 |

The run matched all 147 distinct labeled contents from 209 annotation rows. Duplicate annotation keys, duplicate copy-count keys, and unmatched contents were all zero.

## Limitations and review status

- The sample was selected by signal category; its proportions are not population prevalence estimates.
- “No recorded RISKY finding” does not establish that a content is safe.
- Hina reported truncated-excerpt notes for 38 of the 40 NONE_PRESENT contents in issue #27.
- The descriptive means do not establish a causal relationship or statistical significance.
- Hina confirmed the group counts. Jerad reproduced the copy-count means on November 12, 2026, by rerunning the script (Windows, Python 3.12.10, pandas 3.0.5) and by a separate SQL recount; the regenerated CSV was byte-identical. The committed metadata file is from that rerun.
- Confirmation of how this analysis satisfies the RQ1/RQ2 validated-label requirement remains pending.

See [issue #27](https://github.com/jeraddunne/csc580-group9-msr2027/issues/27).

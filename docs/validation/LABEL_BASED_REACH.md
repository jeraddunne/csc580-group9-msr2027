\# Label-based reach comparison — issue #27



This analysis describes copy counts within the selected round 1 signal-validation sample. It does not estimate population prevalence.



\## Reproduction



Run from the repository root:



```powershell

.\\.venv\\Scripts\\python.exe scripts\\label\_based\_reach.py

```



Inputs:

\- `data/annotations/signals\_jd\_r1.csv`

\- Local database: `data/samples/agent\_skills\_sample.db`



Outputs:

\- `results/label\_based\_reach.csv`

\- `results/label\_based\_reach\_metadata.json`



The metadata records the input checkout commit, input and script SHA-256 checksums, Python and pandas versions, and join checks. The database remains local.



\## Method



Aggregate annotations once per `file\_sha`. Classify contents by whether any recorded finding is RISKY, whether they have a NONE\_PRESENT judgment, or whether they are flagged contents with no recorded RISKY finding.



Join these groups to copy counts calculated by the existing `copy\_counts` function. Copies are the number of artifacts rows per `file\_sha`, not the number of distinct repositories.



The script rejects missing content keys, duplicate annotation keys, duplicate copy-count keys, unmatched contents, and mixed NONE\_PRESENT/other labels.



\## Observed results — November 12, 2026



| Group | Contents | Mean copies | Median copies |

|---|---:|---:|---:|

| At least one recorded RISKY finding | 61 | 2.508197 | 1 |

| Flagged sample: no recorded RISKY finding | 46 | 2.695652 | 1 |

| No-signal sample: NONE\_PRESENT judgment | 40 | 1.275000 | 1 |



The run matched all 147 distinct labeled contents from 209 annotation rows. Duplicate annotation keys, duplicate copy-count keys, and unmatched contents were all zero.



\## Limitations and review status



\- The sample was selected by signal category; its proportions are not population prevalence estimates.

\- “No recorded RISKY finding” does not establish that a content is safe.

\- Hina reported truncated-excerpt notes for 38 of the 40 NONE\_PRESENT contents in issue #27.

\- The descriptive means do not establish a causal relationship or statistical significance.

\- Hina confirmed the group counts; independent reproduction of the copy-count means remains pending.

\- Confirmation of how this analysis satisfies the RQ1/RQ2 validated-label requirement remains pending.



See \[issue #27](https://github.com/jeraddunne/csc580-group9-msr2027/issues/27).


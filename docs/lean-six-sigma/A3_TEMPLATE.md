# A3 problem-solving template

An A3 is a one-page structured story of a problem and its fix. Use it when a retrospective action is bigger than a single `kaizen` issue: it changes how the team works, touches more than one sprint, or needs the whole team to agree. Save filled A3s as `docs/lean-six-sigma/a3/A3-NN-short-title.md` and link them from [KAIZEN_BACKLOG.md](KAIZEN_BACKLOG.md).

Keep it to one page. Numbers over adjectives.

```
# A3-NN: <title>

Owner role:            Date opened:            Sprint:
Status: Draft | Agreed | In progress | Verified | Closed

## 1. Background
Why this matters now. One paragraph. Link the rubric criterion or KPI affected.

## 2. Current condition
What is actually happening, with data.
- KPI and current value (from metrics/DASHBOARD.md):
- Sketch or table of the current process step:
- Waste log lines involved:

## 3. Goal
Measurable target and date.
- KPI:            From:            To:            By:

## 4. Root cause analysis
Link or paste the 5 Whys or fishbone (ROOT_CAUSE_TEMPLATE.md). State the root cause in one sentence.

## 5. Countermeasures
| # | Countermeasure | Addresses which cause | Owner role | Effort (S/M/L) |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |

## 6. Plan
| Step | Who | When | Kaizen issue # |
|---|---|---|---|
| | | | |

## 7. Follow-up
How and when we check that it worked.
- Check date:
- KPI value at check:
- Result: Worked | Partly | Did not work
- What we learned and what changes next:
```

## Worked example skeleton (do not treat as a real A3)

```
# A3-01: Make the pipeline reproducible on a clean machine

Owner role: Developers    Date opened: 2026-10-07    Sprint: Sprint 2
Status: Draft

## 1. Background
Rubric scope rule: "A new user should be able to install dependencies, run the pipeline, and reproduce the main tables or figures." FMEA R08 (RPN 252).

## 2. Current condition
- reproducibility_check: fail (CI could not find data/samples/agent_skills_sample.db)
- Pipeline runs on two of four laptops; the other two have different Python versions.
- Waste log 2026-10-05: 90 minutes lost debugging a hard-coded path.

## 3. Goal
- reproducibility_check: From fail To pass By 2026-10-14, and pass on every weekly snapshot after that.

## 4. Root cause analysis
Download step is manual and undocumented; paths are absolute; Python version unpinned.

## 5. Countermeasures
| 1 | scripts/download_samples.py with checksums | manual download | Developers | M |
| 2 | Paths from config.py relative to repo root | absolute paths | Developers | S |
| 3 | requires-python in pyproject and setup-python in CI | version drift | Developers | S |

## 6. Plan
| Write download script | member | Oct 9 | KZ-07 |
| Refactor paths | member | Oct 10 | KZ-08 |
| CI runs download + pipeline on sample | member | Oct 12 | KZ-09 |

## 7. Follow-up
Check date: 2026-10-19 (weekly snapshot). Result: pending.
```

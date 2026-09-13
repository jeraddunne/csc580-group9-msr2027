# Metrics dashboard

This folder holds the generated process metrics for the project. Nothing here is hand-edited; everything is produced by `scripts/lss_metrics.py`. The KPI definitions are in [../KPIS.md](../KPIS.md).

## Contents

| Path | What it is |
|---|---|
| `DASHBOARD.md` | Human-readable summary: sprint table, KPI vs target with status, contribution table, open blockers, run-rule signals, open PRs waiting for review |
| `history.csv` | One row per snapshot date with the headline KPI values; the source for trend questions at retrospectives |
| `snapshots/YYYY-MM-DD.json` | Full output of `summarize()` for that date, including every per-issue and per-PR data point used |
| `charts/cycle_time_xmr.png` | XmR chart of issue cycle time in closure order |
| `charts/pr_first_review_xmr.png` | XmR chart of PR first-review turnaround in PR creation order |

## How it is generated

**Automatically.** The workflow `.github/workflows/lss-metrics.yml` runs every Sunday at 06:00 UTC (and on demand from the Actions tab). It runs the script against this repository and opens a pull request on branch `metrics/weekly`. The Scrum Master reviews and merges it on Monday. The PR is labeled `type:process` and `kaizen`.

**Manually.**

```bash
pip install -e ".[dev]"
export GITHUB_TOKEN=<token with repo read access>     # PowerShell: $env:GITHUB_TOKEN = "<token>"
python scripts/lss_metrics.py --repo jeraddunne/csc580-group9-msr2027
```

Options:

| Flag | Meaning | Default |
|---|---|---|
| `--repo` | `owner/name` | `repo` in `project.yml` |
| `--out` | Output folder | `docs/lean-six-sigma/metrics` |
| `--since` | ISO date; ignore issues, PRs, runs, and commits created before it | formation start in `project.yml` |
| `--token` | GitHub token | `GITHUB_TOKEN` environment variable |
| `--offline-fixture` | Path to a JSON file with `issues`, `prs`, `reviews`, `runs`, `commits` in the normalized shape; no network access | none |

The fixture format is the same as what the script writes under `snapshots/*.json` in the `inputs` key, so a snapshot can be replayed offline.

## How to read the XmR charts

An XmR chart (individuals and moving range) shows one dot per item in time order with a centre line and two limits.

- **Centre line (X-bar).** The mean of all values.
- **Moving range (mR).** The absolute difference between each value and the previous one. mR-bar is the mean of those.
- **Upper natural process limit (UNPL).** X-bar + 2.66 x mR-bar.
- **Lower natural process limit (LNPL).** X-bar - 2.66 x mR-bar, floored at 0 because time cannot be negative.
- **Upper range limit (URL).** 3.267 x mR-bar, used on the moving range panel.

The limits are not targets. They describe what the process is currently capable of. The target (for example 5 days) is drawn as a dashed line so the team can see whether the process, as it is, can meet the target at all. If the whole band sits above the target, no amount of trying harder will fix it; the process has to change.

## Run rules (signals)

The script flags three patterns. Each becomes a row in the dashboard under "Signals" with the item numbers involved.

| Rule | Pattern | Meaning |
|---|---|---|
| `beyond_limits` | A single point above UNPL or below LNPL | Something unusual happened to that specific item; ask what |
| `eight_same_side` | Eight or more consecutive points on the same side of the centre line | The process has shifted; the centre line is no longer representative |
| `six_trending` | Six or more consecutive points each higher (or each lower) than the previous | A steady drift; find what is changing over time |

Reaction: a signal is discussed at the next Thursday check-in. If it repeats the following week, the Scrum Master opens a 5 Whys using [../ROOT_CAUSE_TEMPLATE.md](../ROOT_CAUSE_TEMPLATE.md).

With fewer than 6 points the chart is drawn without limits and no rules are evaluated; the dashboard says so.

## Status column

| Status | Meaning |
|---|---|
| ok | Value meets the target in `project.yml` |
| warn | Value misses the target |
| info | No target; trend only |
| nodata | Not enough data yet |

## First run

Before the first PR and closed issue exist, the dashboard will say "no data yet" for most rows. That is expected during Formation.

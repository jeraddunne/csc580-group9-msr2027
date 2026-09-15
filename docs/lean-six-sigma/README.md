# Lean Six Sigma overlay

Scrum gives this project its delivery cadence: three sprints, a backlog, planning, reviews, and retrospectives. Lean Six Sigma (LSS) adds a measurement and improvement discipline on top of that cadence. Scrum decides *what is shipped and when*. LSS decides *how to know the process is healthy and how to fix it when it is not*.

The rubric grades "Scrum practice" on whether planning, reviews, retrospectives, and backlog evolution are "visible and used to improve the work". LSS makes the "used to improve" part measurable rather than anecdotal. The project is run by the four-person Group 9 (ADR-0006); section "Group notes" lists what that means for the tools below.

## The two layers

| Layer | Owns | Cadence | Evidence |
|---|---|---|---|
| Scrum | Backlog, sprint goals, roles, ceremonies, Definition of Done | Sprint (3 weeks), weekly check-in, Mon/Wed/Fri stand-ups | GitHub Issues, Project board, `docs/sprints/` |
| Lean Six Sigma | KPIs, control charts, root-cause analysis, waste removal, risk register, tollgates | Weekly metrics snapshot, per-sprint tollgate, per-retro root cause | `docs/lean-six-sigma/`, `metrics/DASHBOARD.md`, `kaizen` issues |

## Where each LSS tool is used

| LSS tool | Scrum ceremony or artifact where it is used | File |
|---|---|---|
| DMAIC roadmap | Sprint boundaries (each sprint is one DMAIC phase with a tollgate) | [DMAIC.md](DMAIC.md) |
| SIPOC and CTQ tree | Formation and Sprint 1 planning (defines the pipeline and what quality means) | [SIPOC_AND_CTQ.md](SIPOC_AND_CTQ.md) |
| KPI catalogue | Thursday check-in, sprint review | [KPIS.md](KPIS.md) |
| XmR control charts and run rules | Thursday check-in | [metrics/README.md](metrics/README.md), `metrics/charts/` |
| Value stream map | Sprint 1 retrospective, revisited in Sprint 3 | [VALUE_STREAM_MAP.md](VALUE_STREAM_MAP.md) |
| DOWNTIME waste log | Any stand-up, formally reviewed at the retrospective | [WASTE_LOG.md](WASTE_LOG.md) |
| FMEA risk register | Sprint planning (review top RPN items), sprint review (update) | [FMEA_RISK_REGISTER.md](FMEA_RISK_REGISTER.md) |
| 5 Whys and fishbone | Retrospective, or whenever a control chart signals | [ROOT_CAUSE_TEMPLATE.md](ROOT_CAUSE_TEMPLATE.md) |
| A3 problem solving | Retrospective actions too big for one kaizen issue | [A3_TEMPLATE.md](A3_TEMPLATE.md) |
| Kaizen backlog | Retrospective output, tracked as `kaizen` issues | [KAIZEN_BACKLOG.md](KAIZEN_BACKLOG.md) |
| Control plan and gemba walk | Sprint review (reproducibility walk by a non-author), Finalization | [CONTROL_PLAN.md](CONTROL_PLAN.md) |

## Weekly rhythm

| Day | What happens | LSS input |
|---|---|---|
| Sunday 06:00 UTC | GitHub Actions runs the LSS metrics workflow and opens a PR on branch `metrics/weekly` | Fresh snapshot, dashboard, charts |
| Monday | Scrum Master reviews the metrics PR; another member approves and it is merged; stand-up | Dashboard status column |
| Wednesday | Stand-up | Waste log entries if any |
| Thursday | Team check-in and metrics review (15 minutes) | KPI table, run-rule signals, open blockers, contribution flags, top 3 FMEA risks |
| Friday | Stand-up; Scrum Master week summary | PRs waiting more than 48 hours for review |
| Last Wednesday of the sprint | Sprint review, then retrospective | Tollgate checklist, 5 Whys on the worst signal, kaizen items created |

## Group notes (ADR-0006)

| Element | Status | Notes |
|---|---|---|
| Contribution-balance KPI | Active; band [0.15, 0.45] in `project.yml` | Read at every check-in; a flag starts a rebalancing conversation |
| PR first-review turnaround | Active; target 48 hours | Matches the 48-hour review SLA in the charter |
| PR open-to-merge cycle time | Active as an extra KPI; target 96 hours | Kept from the short solo period because it shows where merged work waits |
| Cross-member review | Required; `main` needs one approving review from another member | First-time-right is read with the review comments |
| Stand-ups | Written by all four members on Monday, Wednesday, and Friday | `docs/meeting-notes/YYYY-MM-DD-standup-week.md` |
| Measurement system check | Two members run the pipeline independently on different machines | Sprint 1 item S1-10 |
| Rater agreement | Primary rater plus a teammate second rater; inter-rater Cohen's kappa | `docs/validation/README.md` |

Owner roles in these documents (Product Owner, Scrum Master, Developers) follow the rotation in `project.yml`.

## 10-minute quick start for a reader

1. Read [KPIS.md](KPIS.md). The summary table says what is measured and what good looks like.
2. Open `metrics/DASHBOARD.md`. If it says "no data yet", the first snapshot has not run.
3. Read [DMAIC.md](DMAIC.md) for the current sprint only. The tollgate checklist is what the sprint review checks.
4. Skim the top five rows of [FMEA_RISK_REGISTER.md](FMEA_RISK_REGISTER.md) sorted by RPN.
5. Look at [WASTE_LOG.md](WASTE_LOG.md) and [KAIZEN_BACKLOG.md](KAIZEN_BACKLOG.md) to see what slowed the work and what was changed.
6. To regenerate the dashboard locally:

```bash
pip install -e ".[dev]"
export GITHUB_TOKEN=<a token with repo read access>
python scripts/lss_metrics.py --repo jeraddunne/csc580-group9-msr2027
```

The output lands in `docs/lean-six-sigma/metrics/`. Commit it on a branch and open a PR labeled `type:process`.

## Rules of thumb

- Metrics are for the process, not for judging people. Their job is to show honestly where time went and whether changes helped.
- A control chart signal is a question, not a verdict. It triggers a 5 Whys, nothing else.
- Every retrospective produces at least one `kaizen` issue or an explicit note that none was needed.
- Targets in `project.yml` may be changed at a retrospective; record the change in `docs/workspace/DECISION_LOG.md`.

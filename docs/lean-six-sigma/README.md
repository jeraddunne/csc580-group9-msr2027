# Lean Six Sigma overlay for Group 9

Scrum gives this project its delivery cadence: three sprints, a backlog, planning, reviews, and retrospectives. Lean Six Sigma (LSS) gives it a measurement and improvement discipline on top of that cadence. Scrum decides *what we ship and when*. LSS decides *how we know the process is healthy and how we fix it when it is not*.

The rubric grades "Scrum practice" on whether planning, reviews, retrospectives, and backlog evolution are "visible and used to improve the work". LSS is how we make the "used to improve" part measurable rather than anecdotal.

## The two layers

| Layer | Owns | Cadence | Evidence |
|---|---|---|---|
| Scrum | Backlog, sprint goals, roles, ceremonies, Definition of Done | Sprint (3 weeks), weekly check-in, async stand-ups | GitHub Issues, Project board, `docs/sprints/` |
| Lean Six Sigma | KPIs, control charts, root-cause analysis, waste removal, risk register, tollgates | Weekly metrics snapshot, per-sprint tollgate, per-retro root cause | `docs/lean-six-sigma/`, `metrics/DASHBOARD.md`, `kaizen` issues |

## Where each LSS tool is used

| LSS tool | Scrum ceremony or artifact where it is used | File |
|---|---|---|
| DMAIC roadmap | Sprint boundaries (each sprint is one DMAIC phase with a tollgate) | [DMAIC.md](DMAIC.md) |
| SIPOC and CTQ tree | Formation and Sprint 1 planning (defines the pipeline and what quality means) | [SIPOC_AND_CTQ.md](SIPOC_AND_CTQ.md) |
| KPI catalogue | Thursday check-in, sprint review | [KPIS.md](KPIS.md) |
| XmR control charts and run rules | Thursday check-in (Scrum Master reads signals) | [metrics/README.md](metrics/README.md), `metrics/charts/` |
| Value stream map | Sprint 1 retrospective, revisited Sprint 3 | [VALUE_STREAM_MAP.md](VALUE_STREAM_MAP.md) |
| DOWNTIME waste log | Any stand-up, formally reviewed at retrospective | [WASTE_LOG.md](WASTE_LOG.md) |
| FMEA risk register | Sprint planning (review top RPN items), sprint review (update) | [FMEA_RISK_REGISTER.md](FMEA_RISK_REGISTER.md) |
| 5 Whys and fishbone | Retrospective, or whenever a control chart signals | [ROOT_CAUSE_TEMPLATE.md](ROOT_CAUSE_TEMPLATE.md) |
| A3 problem solving | Retrospective actions too big for one kaizen issue | [A3_TEMPLATE.md](A3_TEMPLATE.md) |
| Kaizen backlog | Retrospective output, tracked as `kaizen` issues | [KAIZEN_BACKLOG.md](KAIZEN_BACKLOG.md) |
| Control plan and gemba walk | Sprint review (reproducibility walk), Finalization | [CONTROL_PLAN.md](CONTROL_PLAN.md) |

## Weekly rhythm

| Day | What happens | LSS input |
|---|---|---|
| Sunday 06:00 UTC | GitHub Actions runs the LSS metrics workflow and opens a PR on branch `metrics/weekly` | Fresh snapshot, dashboard, charts |
| Monday | Scrum Master reviews and merges the metrics PR; async stand-up | Dashboard status column |
| Wednesday | Async stand-up | Waste log entries if any |
| Thursday | Mid-sprint check-in and metrics review (15 minutes) | KPI table, run-rule signals, open blockers, top 3 FMEA risks |
| Friday | Async stand-up | |
| Last Wednesday of sprint | Sprint review, then retrospective | Tollgate checklist, 5 Whys on the worst signal, kaizen items created |

Async stand-up format (posted as a comment on the sprint stand-up issue): done since last, doing next, blockers, any waste observed.

## 10-minute quick start for a new member

1. Read [KPIS.md](KPIS.md). You only need the first table. It tells you what we measure and what good looks like.
2. Open `metrics/DASHBOARD.md`. Find your row in the contribution table. If it says "no data yet", the first snapshot has not run.
3. Read [DMAIC.md](DMAIC.md) for the current sprint only. The tollgate checklist is what the sprint review will check.
4. Skim the top five rows of [FMEA_RISK_REGISTER.md](FMEA_RISK_REGISTER.md) sorted by RPN. Those are the risks to keep in mind when picking up work.
5. When something slows you down, add one line to [WASTE_LOG.md](WASTE_LOG.md). That is the whole obligation.
6. To regenerate the dashboard locally:

```bash
pip install -e ".[dev]"
export GITHUB_TOKEN=<a token with repo read access>
python scripts/lss_metrics.py --repo jeraddunne/csc580-group9-msr2027
```

The output lands in `docs/lean-six-sigma/metrics/`. Commit it on a branch and open a PR labeled `type:process`.

## Rules of thumb

- Metrics are for the process, not for grading people. The contribution balance KPI exists so the team can rebalance early, not so anyone can be blamed.
- A control chart signal is a question, not a verdict. It triggers a 5 Whys, nothing else.
- Every retrospective must produce at least one `kaizen` issue or an explicit note that none was needed.
- Targets in `project.yml` may be changed by team vote at a retrospective. Record the change in `docs/decisions/`.

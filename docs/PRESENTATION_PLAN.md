# Final demonstration and presentation plan

How to use: this is the plan for the 20% final demonstration on Fri 2026-12-04. Fill the speaker names by the Sprint 3 check-in on Thu 2026-11-12 (rehearsal 1). The rubric asks the demonstration to show the research question, pipeline, implementation, results, and limitations.

Target length: 12 to 15 minutes, then questions. Every member speaks. Every member must be able to answer questions about any part.

## Structure and timing

| # | Segment | Time | Content | Speaker | Backup speaker |
|---|---|---|---|---|---|
| 1 | Question and motivation | 1.5 min | The one-sentence research question, why it matters for AI-native software engineering, the competing explanation we tested | | |
| 2 | Data | 2 min | Dataset and exact snapshot (release, DOI, date), sample and why it is defensible, unit of analysis, key variables, one data-dictionary example | | |
| 3 | Pipeline, live | 3.5 min | Fresh clone or clean environment, `make pipeline`, show the stage outputs and the tests passing, name the core method | | |
| 4 | Results | 3 min | Main table, main figure, robustness or subgroup check; observations only, numbers read from generated artifacts | | |
| 5 | Interpretation and limitations | 2 min | What the evidence supports, what it does not, top three threats to validity, error analysis examples | | |
| 6 | Process story with Lean Six Sigma metrics | 2 min | Velocity and cycle time across sprints, the most important process improvement with before and after numbers, what the board and PR history show | | |
| 7 | Close | 0.5 min | One-sentence answer, one-sentence next step, release tag and repo URL | | |

Speaker rotation rule: no one speaks for two consecutive segments; the pipeline demo is driven by a member who did not write most of it (this proves reproducibility).

## Live demo checklist

- [ ] Laptop with the tagged release cloned fresh into an empty folder the morning of the talk.
- [ ] Dependencies installed and `make test` green before the session.
- [ ] Sample data present at the documented path; no network needed during the demo.
- [ ] Terminal font enlarged; commands typed from a visible cheat sheet, not memory.
- [ ] Output files opened directly from `results/` and `figures/` after the run.
- [ ] Timer visible to the speaker.

## Backup plan if the demo fails

1. Pre-recorded run: a screen recording of `make pipeline` and `make figures` on the tagged release, stored at `report/demo-recording.mp4` (or linked in the release notes). Recorded at rehearsal 3 on Thu 2026-12-03.
2. Static figures: the committed `figures/` PNGs and `results/` tables in the slides, with the producing script name on each slide.
3. Decision rule: if the live run has not produced the first output within 90 seconds, the speaker says "switching to the recorded run" and continues. No debugging on stage.

## Rehearsals

| Rehearsal | Date | Goal | Timed length | Fixes |
|---|---|---|---|---|
| 1 | Thu 2026-11-12 | Structure and speaker order; slides draft | | |
| 2 | Mon 2026-11-30 | Full run with live demo on a fresh clone | | |
| 3 | Thu 2026-12-03 | Final run; test the backup path; record the demo | | |

## Slide checklist

- [ ] Title slide: project title, Group 9, names, course, date, repository URL and release tag.
- [ ] Research question slide with the competing explanation.
- [ ] Data slide with snapshot statement and sample description.
- [ ] Pipeline diagram (stages, inputs, outputs, tests).
- [ ] Results slides: each figure or table captioned with the script that produced it.
- [ ] Robustness or subgroup slide.
- [ ] Limitations and threats slide.
- [ ] Process slide: KPI trend chart from `docs/lean-six-sigma/metrics/`.
- [ ] Most important process improvement slide with before and after numbers.
- [ ] AI-use disclosure line on the closing slide.
- [ ] Every number on a slide can be traced to a file in the repository.
- [ ] Slides exported to PDF and attached to the GitHub release.

## Likely questions to prepare

- Why this sample and not the full dataset? What would change with the full dataset?
- How do you know the extractor is correct? What was the inter-rater agreement?
- What is the simplest alternative explanation for your main result?
- Which decision would you change if you started again?
- What did each member do? (Answer from `docs/reflections/`.)

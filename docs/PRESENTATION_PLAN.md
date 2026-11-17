# Final demonstration and presentation plan

How to use: this is the plan for the 20% final demonstration on Fri 2026-12-04. The team confirms the speaker rotation at Sprint 3 planning (Thu 2026-10-29) and finalizes timings by the Sprint 3 check-in on Thu 2026-11-12 (rehearsal 1). The rubric asks the demonstration to show the research question, pipeline, implementation, results, and limitations.

Target length: 12 to 15 minutes, then questions. Every member presents at least one segment.

## Speaker assignments

| Speaker | Slides | Allocated time | Coverage |
|---|---|---|---|
| Jerad Dunne | 1–4, 7, 9, 10, 16, 22 | 5:20 | Research question, requirements, pipeline, labeling, and tool |
| Leticia Aderhold | 5, 6, 8, 11–14, 17, 18 | 5:35 | Analyzer comparison, plan, data, results, error analysis, and threats |
| Hina Kramer | 15, 19–21, 23–27 | 5:20 | Reproduction, process, review audit, demonstration, and closing |

Total allocated speaking time: 16 minutes 15 seconds. This exceeds the stated 12–15-minute target and requires adjustment or confirmation of the allowed duration.

Reproducibility is shown by running the demo from a fresh clone rather than a working copy.

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
| 1 | Thu 2026-11-12 | Full end-to-end demo from a fresh clone; draft slides, timing, and speaker hand-offs | | |
| 2 | Mon 2026-11-30 | Full run with live demo on a fresh clone | | |
| 3 | Thu 2026-12-03 | Final run; test the backup path; record the demo | | |

### Rehearsal evidence

Complete this record after each rehearsal.

| Date | Participants | Commit or release tag | Commands run | Outcome and output links | Duration | Problems and follow-up |
|---|---|---|---|---|---|---|
| 2026-11-16 | Attendance to be confirmed | Not yet recorded | Not yet recorded | First rehearsal occurred; end-to-end demonstration outcome and output links to be confirmed | Actual duration not yet recorded | Record problems, corrections, and follow-up with the team |

## Slide checklist

- [x] Title slide: project title, the three current member names (Jerad Dunne, Leticia Aderhold, and Hina Kramer), Group 9, course, date, repository URL and release tag.
- [x] Research question slide with the competing explanation.
- [x] Data slide with snapshot statement and sample description.
- [x] Pipeline diagram (stages, inputs, outputs, tests).
- [x] Results slides: each figure or table captioned with the script that produced it.
- [x] Robustness or subgroup slide.
- [x] Limitations and threats slide, including rater agreement.
- [x] Process slide: KPI trend chart from `docs/lean-six-sigma/metrics/`.
- [x] Most important process improvement slide with before and after numbers.
- [x] AI-use disclosure line on the closing slide.
- [x] Every number on a slide can be traced to a file in the repository.
- [x] Slides exported to PDF and attached to the GitHub release.

## Likely questions to prepare

- Why this sample and not the full dataset? What would change with the full dataset?
- How do you know the scanner is correct? What was the precision per rule and the inter-rater agreement?
- What is the simplest alternative explanation for the main result?
- How was the work divided, and how did reviews work across the team?
- Which decision would you change if you started again?

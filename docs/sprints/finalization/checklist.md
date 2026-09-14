# Finalization checklist (Control phase)

How to use: own this page from Mon 2026-11-30 to Fri 2026-12-04. Nothing is submitted until every box in sections 1 and 2 is checked. In this solo project (ADR-0005) Jerad Dunne verifies each item; where possible, a classmate or the instructor independently checks items 3, 4, and 6 from a fresh clone. The verifier column records who checked.

Product Owner and Scrum Master: Jerad Dunne. Weights: final demonstration and presentation 20%, individual contribution and reflection 5%.

## 1. Final submission checklist (verbatim from the assignment)

Before submission, verify that:

| # | Item | Verifier | Date | Evidence | Done |
|---|---|---|---|---|---|
| 1 | The selected question and dataset are approved. | | | Instructor message or approval note; solo execution confirmation (ADR-0005) | [ ] |
| 2 | The repository is accessible to the instructor. | | | @mkaouer listed as collaborator or repo is public | [ ] |
| 3 | The README provides setup and reproduction instructions. | | | `README.md` | [ ] |
| 4 | The main pipeline runs from a clean environment or documented container. | | | Fresh-clone run log (section 3) | [ ] |
| 5 | The repository contains the task backlog, issues, pull requests, reviews, decisions, tests, artifacts, and report materials. | | | Board, PR self-review comments, `docs/decisions/`, `tests/`, `results/`, `report/` | [ ] |
| 6 | The primary tables and figures can be regenerated. | | | `make figures` output matches release | [ ] |
| 7 | The report distinguishes results from interpretation. | | | Results vs Discussion sections | [ ] |
| 8 | The report includes threats to validity and limitations. | | | `THREATS_TO_VALIDITY.md` and report section | [ ] |
| 9 | The AI-use log (and disclosure) is complete. | | | `ai-use-log.md` | [ ] |
| 10 | Every member has documented an individual contribution and reflection. | | | `docs/reflections/jeraddunne.md` (solo: one file) | [ ] |

## 2. Release steps

| Step | Command or action | Done |
|---|---|---|
| Respond to Sprint 3 instructor feedback (log in section 5) | Issues labeled `rubric` closed | [ ] |
| Freeze `main`: only PRs labeled `rubric` or `bug` merge after Dec 1 | Note in the work log | [ ] |
| Regenerate all results and figures from a clean environment | `make clean && make pipeline && make figures` | [ ] |
| Build the report PDF | See `report/README.md` | [ ] |
| README verified on a fresh clone in a clean environment, by a classmate if available (section 3) | Follow README only | [ ] |
| Update the changelog section in the release notes | List commands, outputs, dataset snapshot | [ ] |
| Tag the release | `git tag -a v1.0.0 -m "Final submission" && git push origin v1.0.0` | [ ] |
| Create the GitHub release with attachments | `gh release create v1.0.0 report/final.pdf figures/*.png --title "v1.0.0 Final submission" --notes-file docs/sprints/finalization/release-notes.md` | [ ] |
| Verify the release page shows the PDF and figures | Open the release URL | [ ] |
| Complete `ai-use-log.md` and the disclosure paragraph in the report | Every AI-assisted PR has a row | [ ] |
| Submit the individual reflection | `docs/reflections/jeraddunne.md` merged | [ ] |
| Submit the final package to the instructor | Report PDF, repository URL and tag, presentation link | [ ] |

## 3. Fresh-clone verification log

| Field | Value |
|---|---|
| Who and environment | |
| Machine and OS | |
| Date | |
| Tag | v1.0.0 |
| Steps followed | |
| Time to primary result (minutes) | |
| Outputs matched release assets | yes / no |
| Problems found and fixed | |

## 4. Presentation rehearsal schedule

| Rehearsal | Date | Format | Timed length | Notes and fixes |
|---|---|---|---|---|
| 1 | Thu 2026-11-12 (Sprint 3 check-in 2) | Full run, slides draft | | |
| 2 | Mon 2026-11-30 | Full run with live demo, fresh clone | | |
| 3 | Thu 2026-12-03 | Final run, backup path tested (recording and static figures) | | |
| Final | Fri 2026-12-04 | Presentation | | |

See `docs/PRESENTATION_PLAN.md` for the structure and backup plan.

## 5. Response-to-feedback log

| Date received | From | Feedback | Response | Issue or PR # | Status |
|---|---|---|---|---|---|
| | | | | | |

## 6. Control plan sign-off

Confirm the checks in `docs/lean-six-sigma/CONTROL_PLAN.md` were run and record the final KPI snapshot from `docs/lean-six-sigma/metrics/DASHBOARD.md`.

| Name | Confirms sections 1 and 2 complete | Date |
|---|---|---|
| Jerad Dunne | [ ] | |
| External verifier (optional) | [ ] | |

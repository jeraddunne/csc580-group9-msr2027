# AI Use Log

The rubric requires that AI use is disclosed and that generated work is verified.
Add an entry whenever an AI tool (Claude, ChatGPT, Copilot, Cursor, etc.)
materially contributed to code, text, analysis, or design. Small autocomplete does not need an entry;
anything you would not have written the same way without the tool does.

Rules
- Log the entry in the same pull request as the work it describes.
- "Verified by" must name the human who read, ran, or tested the output before it was merged.
- Never paste dataset content containing personal data into an external AI tool.
- The final report's AI disclosure statement is generated from this log.

| Date | Member | Tool and model | What it was used for | Output location (file / PR / issue) | Verified by | How it was verified |
|---|---|---|---|---|---|---|
| 2026-09-13 | Jerad Dunne | Claude Code (Claude Fable 5.1) | Generated the initial repository scaffold: process documents, templates, issue forms, workflows, pipeline skeleton, Lean Six Sigma tracking layer, voting and metrics scripts. | Initial commit | Not yet verified (owner: Jerad Dunne) | Automated only: tests and lint passed when generated. A human read-through is still required. Corrected 2026-09-14; the original row claimed a human review that had not happened. |
| 2026-09-14 | Jerad Dunne | Claude Code (Claude Opus 5) | Built the team workspace (work sign-up, findings log, decision log, digest script, two issue forms); built the P-01 pilot scanner, rule file, and tests; ran the pilot on the GitSkills sample and recorded findings F-006 to F-018; drafted proposal P-01 and its issue text from the proposer's repositories and pilot results. | `docs/workspace/`, `docs/proposals/P-01-jerad-dunne-skill-risk-propagation.md`, `rules/`, `src/msr_pipeline/skill_risk.py`, `src/msr_pipeline/workspace.py`, tests, `results/pilot_skill_risk_*` | Jerad Dunne, for the proposal text and background statements (2026-09-14); code not yet human-reviewed | Automated: full test suite and ruff pass; every pilot number regenerates with `python -m msr_pipeline risk-pilot`. Proposal P-01 and its section 4 statements read and confirmed by Jerad Dunne on 2026-09-14. |
| 2026-09-14 | Jerad Dunne | Claude Code (Claude Opus 5) | Solo build: converted the process documents from a four-person group to a solo project (working agreement, decision records ADR-0004 and ADR-0005, decision log, sprint templates, KPIs, FMEA), built the P-01 analysis pipeline and statistics, the validation kit, and a report draft. | PRs for solo conversion, analysis, validation kit, report draft | Not yet verified (owner: Jerad Dunne) | Automated tests and lint pass; human review happens in each pull request before merge |

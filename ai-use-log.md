# AI Use Log

The rubric requires that AI use is disclosed and that generated work is verified.
Every member appends an entry whenever an AI tool (Claude, ChatGPT, Copilot, Cursor, etc.)
materially contributed to code, text, analysis, or design. Small autocomplete does not need an entry;
anything you would not have written the same way without the tool does.

Rules
- Log the entry in the same pull request as the work it describes.
- "Verified by" must name the human who read, ran, or tested the output before it was merged.
- Never paste dataset content containing personal data into an external AI tool.
- The final report's AI disclosure statement is generated from this log.

| Date | Member | Tool and model | What it was used for | Output location (file / PR / issue) | Verified by | How it was verified |
|---|---|---|---|---|---|---|
| 2026-09-13 | Jerad Dunne | Claude Code (Claude Fable 5.1) | Generated the initial repository scaffold: process documents, templates, issue forms, workflows, pipeline skeleton, Lean Six Sigma tracking layer, voting and metrics scripts. | Initial commit | Jerad Dunne | Read all documents, ran the test suite and lint locally, ran scripts against fixtures. |

# Report

How to use: `draft.md` is the living report. Every sprint improves it; the final submission is the integrated version, not three separate documents. Build the PDF with Pandoc.

## Files

| File | Purpose |
|---|---|
| `draft.md` | The report source. Section headings follow the assignment's report requirements. |
| `references.bib` | BibTeX references. Only entries that have been checked against the publisher, DOI, or arXiv page. |
| `final.pdf` | Built output for submission (generated, attach to the GitHub release). |

## Build

Requires Pandoc 3.x and a LaTeX engine (for example TinyTeX or MiKTeX) for PDF output.

```
cd report
pandoc draft.md --citeproc --bibliography references.bib -o final.pdf
```

Markdown or HTML output without LaTeX:

```
pandoc draft.md --citeproc --bibliography references.bib -o final.html
```

Optional: add `--csl ieee.csl` (download from the CSL repository) for IEEE-style citations; otherwise Pandoc uses Chicago author-date.

## Figures and tables

- Figures live in `../figures/` and are produced only by the pipeline (`make figures`). Reference them as `![Caption](../figures/<name>.png){#fig:<id>}`.
- Tables live in `../results/` as CSV. Paste them into the draft with a comment naming the producing script and commit, or generate Markdown tables with a script.
- Never hand-edit a figure or a number. If a number changes, rerun the pipeline and update the draft.

## Citations

Cite with `[@gitskills2027]` or `[@specmine2027]`. Add new entries to `references.bib` only after verifying them.

## Conventions

- Results section: observations only (what the data shows).
- Discussion section: interpretation (what we think it means, alternative explanations).
- State the exact dataset snapshot once in the Dataset section.
- Disclose AI use in the Artifact appendix, consistent with `../ai-use-log.md`.

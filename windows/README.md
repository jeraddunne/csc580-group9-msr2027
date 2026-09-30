# Windows launchers: run the project by double-clicking

These files let a member run the project on a Windows computer without git or typed commands. They work from a ZIP download of the repository. The full walkthrough is recipe 7 in [docs/NO_GIT_GUIDE.md](../docs/NO_GIT_GUIDE.md).

## Before the first run

1. Install Python 3.11 or newer from [python.org/downloads](https://www.python.org/downloads/). On the first installer screen, tick **Add python.exe to PATH**.
2. Download the project: on the repository page, green **Code** button, **Download ZIP**. Right-click the ZIP, **Extract All**, and extract to a folder outside OneDrive, for example `C:\dev\`.
3. Open the extracted folder, then this `windows` folder.

If Windows shows "Windows protected your PC", click **More info**, then **Run anyway**. The files are plain text; you can open any of them in Notepad to read exactly what it does.

## The files, in order

| File | When to use it | What it does | Changes |
|---|---|---|---|
| `1-set-up.bat` | Once, before anything else; again after downloading a newer ZIP | Finds Python, creates the private `.venv` folder, installs the project's packages, downloads the GitSkills sample (about 90 MB) | Adds `.venv` and `data/samples` inside the project folder only |
| `2-run-pipeline.bat` | Fresh-run check for a sprint review (S1-10, gemba walk) | Reruns the full analysis, compares every result file with the committed one (line endings ignored), and opens a report in Notepad | Writes `build/fresh_run/` only; `results/` is not changed |
| `3-open-labelling-page.bat` | Second raters, at the start of each labelling session | Asks your rater id and kind, builds your label sheet and reading packets, and opens your labelling page in the browser | Writes your sheet in `data/annotations/` if it does not exist yet, and pages in `data/annotations/work/` |
| `4-save-my-labels.bat` | Second raters, at the end of each session | Checks the CSV you downloaded from the labelling page and saves it as your label file. Drag the CSV onto this file; a name your browser changed, like `drift_la_r1 (1).csv`, is fine. If the download changes labels you saved before, it asks before replacing them | Updates your own label file in `data/annotations/` |

Every window says what it is doing, and stops with a message if something fails. If one fails, take a screenshot and post it as a comment on your task on GitHub.

## Common problems

| What you see | Why | What to do |
|---|---|---|
| "Windows protected your PC" | The file came from the internet | **More info**, then **Run anyway** |
| "Python 3.11 or newer was not found" | Python is missing, or was installed without the PATH option | Install it again from python.org and tick **Add python.exe to PATH** |
| "No such file or directory" during install, with a hint about long paths | Windows refuses file paths over 260 characters, and some packages have deep folders | Move the project folder to `C:\dev\`, delete the `.venv` folder inside it, and run `1-set-up.bat` again |
| The window closes at once | It was started from inside the ZIP | Extract the ZIP first (right-click, **Extract All**) |

## What the fresh-run report means

`2-run-pipeline.bat` exits with one of three results:

- **Every file matches.** Your computer produced the same numbers as the committed results. That is the measurement system check passing.
- **Some files differ.** The report lists which ones. Post the report on your task; a difference is a finding, not your mistake.
- **Something went wrong.** Usually the sample is missing (run `1-set-up.bat`) or the computer ran out of memory (close other programs and try again).

The same check from a terminal: `python scripts/fresh_run_check.py`.

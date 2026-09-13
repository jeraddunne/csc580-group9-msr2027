# Waste log (DOWNTIME)

Lean names eight kinds of waste with the acronym DOWNTIME. Below is what each one looks like in a student research-software project, followed by the running log. Anyone can add a line to the log at any time; the retrospective reviews it and turns recurring entries into `kaizen` issues.

## Waste categories adapted to this project

| Letter | Waste | What it looks like here | Example |
|---|---|---|---|
| D | Defects | Wrong output, broken pipeline, misread data field | A join on `repo_name` silently drops rows because of case differences |
| O | Overproduction | Building analysis nobody asked for, or before the question is settled | Writing a classifier before the operational definition of the outcome exists |
| W | Waiting | Work that sits idle | PR waits four days for a review; issue waits in Todo for a decision |
| N | Non-utilized talent | Skills not used, or one person doing everything | The member who knows statistics is writing README text while someone else struggles with a test design |
| T | Transportation | Moving artifacts between places by hand | Copying figures from a notebook into the report instead of generating them |
| I | Inventory | Too much work started, too many open branches, unmerged PRs | Three open PRs by one member, none reviewed |
| M | Motion | Hunting for information, switching tools | Searching chat history for the dataset download link that should be in `data/README.md` |
| E | Extra processing | Doing more than the acceptance criterion requires | Formatting a table beautifully that will be regenerated next sprint |

## How to log

- One line per observation. Be specific about the artifact (issue number, PR number, file).
- Impact: minutes or hours lost, or a defect count, in plain numbers.
- Countermeasure: what we will try. Leave blank if unknown; the retro fills it.
- Kaizen: the `kaizen` issue number once one exists.

## Running log

| Date | Sprint | Waste | Description | Impact | Countermeasure | Kaizen # |
|---|---|---|---|---|---|---|
| 2026-09-13 | Formation | Motion | Assignment schedule lives only in the PDF; members ask for dates in chat | ~10 min per member per week | Timeline copied into `project.yml` and `PROJECT_PLAN.md` | |
| 2026-09-13 | Formation | Waiting | Project board cannot be created by script until the GitHub token has the `project` scope | Board setup delayed | Documented in `scripts/setup_project_board.py`; owner runs `gh auth refresh -s project` | |
| | | | | | | |
| | | | | | | |

## Review procedure at the retrospective

1. Read every line added since the last retro.
2. Group lines by waste type. The type with the most lines or the largest impact gets a 5 Whys ([ROOT_CAUSE_TEMPLATE.md](ROOT_CAUSE_TEMPLATE.md)).
3. Create one `kaizen` issue per countermeasure the team agrees to try. Write the issue number back into the log.
4. Note the top waste type in the retrospective file under "Most important process improvement".

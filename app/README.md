# Group 9 Project Guide (team web app)

A web app for members who do not use git: the project in plain words with worked examples, the sprints and their deliverables, tasks with tickable steps, forms that change project documents, and reviews. It runs at <https://jeraddunne.github.io/csc580-group9-msr2027/app/>. Issue #69 started the no-git path; issue #73 is this app.

Everything a member does is saved on GitHub **under their own account**: the app signs in with each member's own GitHub key, so issues, comments, commits, pull requests, and reviews are theirs and count for the rubric. **Practice mode** lets anyone try every button as a team member; it reads the real project but only records changes in a practice log.

## What it does on GitHub

| In the app | On GitHub, as the signed-in member |
|---|---|
| Tick a step | Edits the issue body, `[ ]` to `[x]` (re-reads first; refuses if the step changed meanwhile) |
| Post comment, Mark done | A comment; Mark done also closes the issue |
| Take this task | Adds the member as assignee |
| Board status, New task | Sets the Projects board's Status, Sprint, Priority, Work type, Target date (needs the `project` scope) |
| New task | An issue in the guided-task format (`lib/tasks.js`, same headings as `.github/ISSUE_TEMPLATE/10-guided-task.yml`) |
| Documents forms | Branch from `main`, one commit changing one file, a pull request, a review request (`GitHub.proposeFileChange`) |
| Reviews | A pull request review: approve, request changes, or comment |

A form error (for example "already signed") is caught before anything is written.

## Sign-in and the key

Members create a classic personal access token with the `public_repo` and `project` scopes (the sign-in page links to GitHub's form with both ticked). The key is kept in the browser's `localStorage`, or `sessionStorage` when "Remember me" is off, and is sent only to `api.github.com`. A GitHub Pages site cannot keep a server secret, so a per-member key is the way a static page can act as the member. The repository is public, so `public_repo` is enough; `project` is only needed for the board.

## Layout

| Path | What |
|---|---|
| `index.html`, `app.css`, `app.js` | Shell, styles, router, session (signed in, practice, or signed out) |
| `views/` | One file per page: home, learn, sprints, tasks, newtask, documents, reviews, help, signin, practice |
| `lib/github.js` | GitHub REST and GraphQL client, including the branch, commit, and PR flow |
| `lib/practice.js` | Practice mode: same interface, writes go to a log |
| `lib/formulas.js` | The pipeline's formulas in JavaScript (Wilson, shingles and Jaccard, Mann-Whitney U and rank-biserial, Holm, Cohen's kappa, precision, IRR) |
| `lib/rules.js`, `data/rules.json` | The rule tester; `rules.json` is exported from `rules/skill_risk_rules.yaml` |
| `lib/tasks.js`, `lib/docs.js`, `lib/csv.js` | Pure helpers: checklists, task bodies, branch names, document edits, CSV reading |
| `content/project.js` | Team, links, phases, rubric deliverables (quoted from the assignment) mapped to issues, key dates |
| `vendor/preact-htm.module.js` | Preact and htm 3.1.1 standalone (MIT), vendored so there is no build step or CDN at run time |
| `tests/` | Node tests; `reference_values.json` holds answers computed by the Python pipeline |

## Run it locally

From the repository root, so that `../results/` resolves as it does on the site:

```bash
python -m http.server 8765 --bind 127.0.0.1
# open http://127.0.0.1:8765/app/   (practice: http://127.0.0.1:8765/app/?practice=AllieHgs)
```

## Tests

```bash
cd app && npm test          # or: node --test "tests/*.test.mjs"  (Node 22 or newer, no install)
python -m pytest tests/test_app_data.py
```

- `formulas.test.mjs`: every formula matches the pipeline's Python functions on the same inputs.
- `rules.test.mjs`: every rule's examples behave in JavaScript as in Python.
- `docs.test.mjs`: each document form on the repository's real files.
- `github.test.mjs`: the GitHub calls against a fake GitHub, including that practice mode never writes.
- `tests/test_app_data.py` (pytest): `app/data/rules.json` is current with the rule file.

## Changing it

- **Dates, rubric items, team:** edit `content/project.js`.
- **Rules changed:** run `python scripts/export_app_data.py` and commit `app/data/rules.json` (CI fails otherwise).
- **Reference answers:** if a pipeline formula changes, regenerate `tests/reference_values.json` from the Python functions and keep the JavaScript in step.
- **New document form:** a pure function in `lib/docs.js` with a test on the real file, then a form in `views/documents.js` that calls `proposeFileChange`.

# Working on the project without git

Everything a Group 9 member needs to do can be done in a web browser on github.com, signed in to your own GitHub account. You do not need git, a terminal, or any command. GitHub creates the branches and pull requests for you when you press the buttons below.

Your work counts only when it is done under your own account. Nobody else can sign the charter, review a pull request, or label items for you.

## Where to start

1. **Your tasks.** Open [issues assigned to you](https://github.com/jeraddunne/csc580-group9-msr2027/issues?q=is%3Aopen+assignee%3A%40me). Each **guided task** explains why it matters, how long it takes, and lists the steps as checkboxes. Tick each box as you finish the step.
2. **The documents.** Read them on the [project website](https://jeraddunne.github.io/csc580-group9-msr2027/), which has a menu and search. Every page there has an **Edit this page** button (the pencil icon) that takes you to recipe 4.
3. **Stuck?** Write a comment on your task in plain words (recipe 2). Say which step you are on and what you see on screen. That is always the right move, and it counts as participation.

## Words you will see

| Word | What it means for you |
|---|---|
| Repository (repo) | The project folder on GitHub: every document, the code, and the results |
| `main` | The approved version of the project. You never change it directly |
| Issue | A task or a question, with a comment thread. Guided tasks are issues |
| Pull request (PR) | A proposed change waiting for another member's review. GitHub opens one for you when you edit or upload a file |
| Branch | A private copy that holds your proposed change. GitHub makes it; you only type its name |
| Review | Another member reads your pull request and approves it or asks for a change |
| Merge | Adding an approved pull request to `main`. The Product Owner does this |
| Markdown (`.md`) | Plain text with a little formatting. `#` starts a heading, `-` starts a bullet, `**bold**` is bold |

## Recipes

### 1. Read a document

- On the [project website](https://jeraddunne.github.io/csc580-group9-msr2027/): use the menu on the left or the search box at the top.
- On GitHub: open the [repository](https://github.com/jeraddunne/csc580-group9-msr2027), click folders to open them, click a file to read it. Markdown files are shown formatted.

The most useful documents: `RESEARCH_QUESTION.md` (what we study), `docs/PROCESS.md` (how work moves), `docs/sprints/sprint-1/review.md` (what the Sprint 1 review needs), `docs/validation/ANNOTATION_GUIDELINE.md` (how to label).

### 2. Ask a question or leave a comment

1. Open the issue or pull request.
2. Scroll to the box at the bottom, **Add a comment**.
3. Type in plain words. To notify someone, type `@` and pick their name, for example `@jeraddunne`.
4. Click **Comment**.

### 3. Tick off a step in a guided task

Click the checkbox next to the step in the issue description. The tick saves by itself and everyone sees it. If the boxes cannot be clicked, you are not signed in, or you have not accepted the [repository invitation](https://github.com/jeraddunne/csc580-group9-msr2027/invitations) yet.

### 4. Change a file (edit text, fill in a table column, sign your name)

1. Open the file on GitHub, or click **Edit this page** on the website.
2. Click the **pencil icon** (Edit this file) at the top right of the file.
3. Make your change. Click the **Preview** tab to check how it will look.
4. Click the green **Commit changes...** button at the top right.
5. In the window that opens:
   - **Commit message**: say what you changed, for example `Sign the team charter`.
   - Choose **Create a new branch for this commit and start a pull request** (committing to `main` is blocked on purpose).
   - **Branch name**: type the kind of work, the issue number, and a few words, for example `docs/51-sign-charter`. Kinds: `docs`, `process`, `data`, `report`.
6. Click **Propose changes**.
7. On the next page, write in the description what you changed and why. Add a line `Closes #<issue number>` so the task closes when your change is merged.
8. Click **Create pull request**.
9. On the right side, click **Reviewers** and pick a member other than yourself.

**Filling in a table.** Tables in markdown look like this. Keep every `|`, and keep each row on one line:

```text
| Step | Content           | Time  | Presenter |
|------|-------------------|-------|-----------|
| 1    | Research question | 2 min | Your Name |
```

Type only between the `|` marks of the column you were asked to fill. Check the result in **Preview** before you commit.

### 5. Add (upload) a file

1. Open the folder the task names, for example `data/annotations/`.
2. Click **Add file** at the top right, then **Upload files**.
3. Drag the file into the page, or click **choose your files**.
4. Continue from step 5 of recipe 4 (commit message, new branch, **Propose changes**, **Create pull request**, reviewer).

Never upload dataset files (`.db`, `.parquet`), passwords, or personal information: this repository is public.

### 6. Download a file or the whole project to your computer

- **One file:** open it on GitHub and click the **Download raw file** icon (the downward arrow) in the bar above the file's text.
- **The whole project:** on the [repository](https://github.com/jeraddunne/csc580-group9-msr2027) front page, click the green **Code** button, then **Download ZIP**. Right-click the ZIP, choose **Extract All**, and extract it to a folder **outside OneDrive**, for example `C:\dev\`. OneDrive interferes with the files the project creates.

### 7. Run the project on your computer (Windows, no commands)

Use this for the fresh-clone check and for labelling.

1. Install Python once: from [python.org/downloads](https://www.python.org/downloads/), version 3.11 or newer. On the first installer screen, tick **Add python.exe to PATH**.
2. Download and extract the project (recipe 6).
3. Open the extracted folder, then the `windows` folder, and double-click the numbered files in order. [`windows/README.md`](../windows/README.md) explains each one. A black window opens, shows what it is doing, and tells you when it is finished.

### 8. Review another member's pull request

1. Open the [pull requests](https://github.com/jeraddunne/csc580-group9-msr2027/pulls) list and click the one that asks for your review.
2. Read the description, then the **Files changed** tab. Green lines are added, red lines are removed.
3. To ask about one line, hover over it, click the blue **+**, and write your question.
4. Click **Review changes** (in some layouts, **Submit review**).
5. Write what you checked, for example `Read the ADR and checked the three numbers against results/rq3_summary.csv`.
6. Choose **Approve** if it is correct, or **Request changes** and say what to fix.
7. Click **Submit review**.

A review that says what you checked is the evidence the Sprint 1 review needs. You may review any pull request except your own.

### 9. Fix your pull request after a reviewer asks for a change

1. Open your pull request, then the **Files changed** tab.
2. On the file, click the **...** menu at its top right, then **Edit file**.
3. Make the change and click **Commit changes...**. It goes into the same pull request; you do not need a new one.
4. Reply to the reviewer's comment to say it is done.

### 10. If you use an AI tool

Add one row to `ai-use-log.md` in the same pull request (recipe 4): date, your name, the tool, what it did, and how you checked the result.

## What not to do

- Do not change `main` directly, merge your own pull request, or approve your own work.
- Do not open another rater's label files (any file ending `_jd_r1.csv` or another member's id) while you are labelling.
- Do not paste dataset text, repository names, or account names into issues or comments. Describe items by their number in your sheet.
- Do not run scripts or commands found inside the dataset.

## If something goes wrong

Nothing you do through these buttons can break `main`: every change waits for a review. If you are unsure, stop and comment on your task. For anything urgent, mention `@jeraddunne` (Product Owner) or `@angel06la` (Scrum Master).

For the command-line path, see [GETTING_STARTED.md](GETTING_STARTED.md). Both paths lead to the same place.

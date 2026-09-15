# Getting started

Two audiences: **Group 9 members** joining the project (section 1), and **readers or graders** reproducing the results (section 2).

## 1. Onboarding path for a new member

Time needed: about 15 minutes of reading and 30 to 45 minutes of setup. Do these in order.

### Step 1. Accept the invitation

Open https://github.com/jeraddunne/csc580-group9-msr2027/invitations and accept. You also have write access on the project board: https://github.com/users/jeraddunne/projects/1

### Step 2. Read

1. `TEAM_CHARTER.md`: what we agreed to (you sign it in step 5).
2. `docs/PROCESS.md`: how a task moves from idea to merged evidence.
3. `RESEARCH_QUESTION.md` and `docs/proposals/P-01-jerad-dunne-skill-risk-propagation.md`: the topic. If you want to revisit the topic, open a Decision needed issue before Thu 2026-09-17.
4. `docs/decisions/ADR-0006-group-reinstated.md`: why the group structure changed on 2026-09-15.

### Step 3. Set up your machine

Use **Git Bash** on Windows, not PowerShell. Clone to a folder **outside** OneDrive or iCloud (for example `C:\dev\`); sync tools fight with git working trees.

```bash
gh auth login                       # GitHub CLI
git clone https://github.com/jeraddunne/csc580-group9-msr2027.git
cd csc580-group9-msr2027
make setup                          # or: python -m venv .venv && . .venv/Scripts/activate && pip install -e ".[dev]"
make test                           # must be green before you continue
make data                           # downloads the GitSkills sample (about 90 MB download, 290 MB on disk)
```

If `make` is missing, `./run_pipeline.sh` runs setup, download, and tests.

### Step 4. Open your onboarding issue

Issues > New issue > **Team member onboarding**. It records your handle, availability, strengths, and role preferences. Do not put email or phone numbers in it; the repository is public.

### Step 5. Your first pull request

1. Branch: `git switch -c process/<issue>-onboarding-<firstname>`.
2. Fill in your profile in `docs/team/<firstname>-<lastname>.md` (a stub with your GitHub handle already exists).
3. In `TEAM_CHARTER.md` section 14, add today's date and this pull request's number to your row.
4. Commit, push, and open a pull request with `Closes #<your onboarding issue>`.
5. Request a review from another member. You cannot merge until someone other than you approves.
6. Review one other member's onboarding pull request, so everyone practices both sides before real work starts.

### Step 6. If you are a second rater

At the kickoff the team decides who second-rates which validation kind. If that is you, follow `docs/validation/README.md` section "Second-rater workflow". In short, with your rater id (Leticia `la`, Allie `ah`, Hina `hk`):

```bash
python scripts/annotation_kit.py sheet --rater <id> --round 1
python scripts/annotation_kit.py ui --rater <id> --round 1     # open data/annotations/work/label_<kind>_<id>_r1.html
# label in the page, click Download CSV, then:
python scripts/annotation_kit.py import ~/Downloads/<kind>_<id>_r1.csv
```

Then open a pull request containing only your label file. Never open Jerad Dunne's (`jd`) label files; that keeps the agreement measure independent.

### Step 7. Every week after that

- File a Work sign-up before each sprint planning (`docs/workspace/WORK_SIGNUP.md`).
- Write your stand-up row on Monday, Wednesday, and Friday.
- Pull work from the board, keep WIP under the limit, open pull requests early, and review others within 48 hours.
- Log AI use in `ai-use-log.md` in the same pull request as the work.
- Come to the Thursday check-in having looked at `docs/lean-six-sigma/metrics/DASHBOARD.md`.

## 2. Reproducing or reviewing the results

Prerequisites: Git and Python 3.11 or newer.

```bash
git clone https://github.com/jeraddunne/csc580-group9-msr2027.git
cd csc580-group9-msr2027
make setup
make test
make data
make pipeline                       # P-01 analysis: results/rq*_*.csv, results/sensitivity_*.csv, figures/rq*_*.png
git status --short results figures   # expect no changes other than timestamps
```

The dataset snapshot used for committed results is recorded in `data/samples/MANIFEST.json`.

## 3. Where things are

| Need | Go to |
|---|---|
| What is due when | `docs/sprints/README.md` |
| The board | https://github.com/users/jeraddunne/projects/1 |
| Sign up for work, log a finding, see decisions | `docs/workspace/README.md` |
| How to write an issue or pull request | Issue forms and PR template |
| Validation guideline and second-rater protocol | `docs/validation/` |
| Process metrics | `docs/lean-six-sigma/metrics/DASHBOARD.md` |
| Meeting notes and stand-ups | `docs/meeting-notes/` |
| Report draft | `report/draft.md` |
| AI assistance and verification | `ai-use-log.md` |

## 4. Getting help

Ask in the team channel first; open a Blocker issue if you are stuck for more than a day. There is no penalty for asking; there is a penalty for silence (charter section 8).

# Getting Started (for Group 9 members)

Time needed: about 15 minutes of reading, then 30 minutes of setup.

## Day 1: read

1. The assignment PDF (in the course site) and the MSR 2027 Mining Challenge page: https://2027.msrconf.org/track/msr-2027-mining-challenge
2. `TEAM_CHARTER.md`: what we agreed to.
3. `docs/PROCESS.md`: how a task moves from idea to merged evidence.
4. `docs/proposals/00-candidate-questions.md`: the 15 rubric questions with feasibility notes.
5. `docs/lean-six-sigma/README.md`: why we track metrics and what happens with them.

## Day 1: do

1. **Accept the repository invitation** from GitHub (check email or https://github.com/notifications).
2. **Onboard:** open Issues > New issue > "Team member onboarding" and fill it in. This gives the team your handle, availability, and strengths.
3. **Set up your machine:**

   ```bash
   gh auth login                     # GitHub CLI, needed for scripts
   git clone https://github.com/jeraddunne/csc580-group9-msr2027.git
   cd csc580-group9-msr2027
   make setup                        # or: python -m venv .venv && . .venv/Scripts/activate && pip install -e ".[dev]"
   make test                         # must be green before you continue
   make data                         # downloads samples (about 230 MB)
   python -m msr_pipeline explore --dataset all
   ```

   Windows users: run these in **Git Bash**, not PowerShell. If `make` is missing, `./run_pipeline.sh` does the same steps.

   OneDrive users: clone to a folder **outside** OneDrive (for example `C:\dev\`). OneDrive sync fights with git working trees.

4. **Your first pull request:** copy `docs/team/TEMPLATE-member-profile.md` to `docs/team/<firstname>-<lastname>.md`, fill it in, add your signature row to `TEAM_CHARTER.md` section 13, and open a PR using the template. Ask another member to review. This is deliberately small so everyone practices the flow before real work starts.

## Day 2: propose and vote

1. Read the candidate questions and the two dataset READMEs (`data/README.md`).
2. Open Issues > New issue > "Project proposal". You may propose a rubric question as-is, a refinement, or an equivalent grounded in the datasets. One proposal per person minimum; two is better.
3. After proposals close (2026-09-14 23:59), read every proposal and cast your ballot: copy `docs/proposals/votes/TEMPLATE-ballot.yml` to `docs/proposals/votes/ballots/<your-github-handle>.yml`, fill in your ranking and criterion scores, and open a PR. The tally workflow comments the current standings on the PR.
4. The decision is recorded on 2026-09-16 at kickoff (`docs/meeting-notes/2026-09-16-kickoff.md`).

## Every week after that

- Write your stand-up lines on Monday, Wednesday, and Friday.
- Pull work from the board, keep WIP under the limit, open PRs early, review others within 48 hours.
- Log AI use in `ai-use-log.md` in the same PR as the work.
- Come to the Thursday check-in having looked at `docs/lean-six-sigma/metrics/DASHBOARD.md`.

## Where things are

| Need | Go to |
|---|---|
| What is due when | `docs/sprints/README.md` |
| The board | GitHub Projects tab of the repository |
| How to write an issue or PR | Issue forms and PR template (they guide you) |
| A decision we made | `docs/decisions/` |
| Meeting notes | `docs/meeting-notes/` |
| Risks and process metrics | `docs/lean-six-sigma/` |
| Report draft | `report/draft.md` |

## Getting help

Ask in the team channel first; open a `blocker` issue if you are stuck more than a day. There is no penalty for asking; there is a penalty for silence (charter section 8).

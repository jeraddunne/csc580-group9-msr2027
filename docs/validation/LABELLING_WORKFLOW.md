# Labelling workflow: from a blank sheet to a scored label file

How to use: follow this page from top to bottom the first time you label, then keep it as a checklist for every session. It covers the two ways to label (the labelling page and the Excel workbook), how to keep your work safe offline, what to record besides the label, and what the numbers are for. The labelling rules themselves are in [ANNOTATION_GUIDELINE.md](ANNOTATION_GUIDELINE.md); this page never overrides them.

## 1. Before the first session (about 20 minutes)

1. Read [ANNOTATION_GUIDELINE.md](ANNOTATION_GUIDELINE.md) once, fully. Pay attention to the safety rules (section 1), the decision order (section 2.2), and the reasons rule (section 5).
2. Build your sheets, reading packets, labelling pages, and workbook. Replace `jd` with your rater id.

```bash
python scripts/annotation_kit.py sheet --rater jd --round 1   # label sheets and reading packets
python scripts/annotation_kit.py ui --rater jd --round 1      # labelling pages (HTML)
python scripts/annotation_kit.py xlsx --rater jd --round 1    # labelling workbook (Excel)
```

Everything lands in `data/annotations/work/`, which git ignores, because the packets, pages, and workbook quote dataset text. Without a terminal on Windows, `windows/3-open-labelling-page.bat` builds and opens the page.

3. Choose how you will label each kind. Use one of the two for a kind at a time.

| | Labelling page (`label_<kind>_<rater>_r<round>.html`) | Labelling workbook (`labelling_<rater>_r<round>.xlsx`) |
|---|---|---|
| Best for | Reading: matched text highlighted, rule cards, a step-through of the decision order | Working in a table: filter, sort, see many rows at once |
| Offline | Yes: one self-contained file, no internet | Yes |
| Saves | Automatically, in the browser; Download CSV for a copy | Ctrl+S |
| Back into the project | `annotation_kit.py import <downloaded csv>` | `annotation_kit.py import data/annotations/work/labelling_<rater>_r<round>.xlsx` |
| Extra records | Time is tracked for you; confidence and what settled it are one click | Fill Date labelled, Minutes, Confidence, and What settled it yourself |

To switch from one to the other, import first. Then either rebuild the workbook from your imported labels (`annotation_kit.py xlsx ... --force`, which refuses while the workbook holds anything not yet imported), or open the page and click **Load CSV** with `data/annotations/<kind>_<rater>_r<round>.csv`.

## 2. Every session (30 to 40 minutes)

1. Open the page or the workbook. The page's briefing must be acknowledged before the first label.
2. Label in order: signals, then lineage, then drift. For each row:
   - read the text that matched (highlighted on the page; in the workbook's Matched text column, with the full packet one click away);
   - answer the decision order in your head, or with the page's **Help me decide**, which applies only your own answers;
   - choose the label;
   - if the label needs a reason (signals `NOT_PRESENT`, `BENIGN_CONTEXT`, `MISSED_RISKY`; lineage `NO`, `UNSURE`; drift `HARDENING`, `CAPABILITY_ADDITION`), write at least 15 characters of **evidence**, not a conclusion;
   - optionally record **what settled it** for a false positive, and your **confidence**.
3. Stop after 30 to 40 minutes. The page reminds you.
4. Save a copy outside the browser: **Download CSV** on the page (a banner appears after 10 unsaved labels or 30 minutes), or Ctrl+S in the workbook.
5. Import, so the labels are checked and kept in the project:

```bash
python scripts/annotation_kit.py import ~/Downloads/signals_jd_r1.csv
python scripts/annotation_kit.py import data/annotations/work/labelling_jd_r1.xlsx
python scripts/annotation_kit.py status
```

The import refuses a file with a missing reason, a missing category, an invalid label, or rows from another sample. It never overwrites a saved label with a different one unless you add `--replace`. Fix what it lists and import again.

6. Commit nothing yet unless the blindness rule allows it (section 5).

## 3. Working offline and keeping your work safe

- The labelling page holds every reading packet and makes no network requests, so it works with no connection. The workbook is a normal Excel file.
- The page saves in the browser for that file. Another browser, a private window, or a cleared browser starts empty, and so may a copy of the file in another folder. **Download CSV** is your backup; **Load CSV** puts it back, and it accepts only the page's own file name for that kind, rater, and round.
- The page's work log (Metrics, **Download work log**) keeps your active time, the time of each first label, label changes, confidence, and what settled each false positive. **Load CSV** restores it as well, and `annotation_kit.py import worklog_<kind>_<rater>_r<round>.csv` keeps it in `data/annotations/work/`.
- Never put dataset text, repository names, or account names in notes. Never copy an excerpt into a terminal or open a URL from one.

## 4. What gets recorded, and why

| Recorded | Where | Used for |
|---|---|---|
| Label and reason | Label file (`data/annotations/<kind>_<rater>_r<round>.csv`) | Precision, recall, lineage precision, drift distribution, kappa (`annotation_kit.py score`) |
| Missed category | Label file | Recall by category; FMEA detection score |
| What settled it (guideline 2.2 question 1 to 4, a 2.4 special case, or other) | Work log | Error analysis: whether a rule's false positives come from the pattern (questions 1 and 2) or from context it cannot see (questions 3 and 4); `RULE_CHANGE_PROPOSALS.md` |
| Confidence (sure, leaning, unsure) | Work log | Choosing manually inspected examples; expecting where round 2 or a second rater will disagree |
| First label date | Work log | Round 2 timing: each item can be relabelled 14 days (signals, lineage) or 7 days (drift) after it |
| Active minutes | Work log | Hours in stand-ups, the Sprint 2 retrospective, and individual reflections |

The work log never holds labels. It stays in `data/annotations/work/` until the rater decides to publish it with the finished label file.

## 5. When a kind is finished

1. Check **Metrics** on the page, or the **Metrics** sheet in the workbook. The results there unlock only when every row of the kind is labelled, because seeing running results while labelling can nudge the labels that follow. They are provisional; the official numbers come from `annotation_kit.py score`.
2. Review the items the page lists as worth a second look (label changed, unsure, under 20 seconds, escalate) without changing labels for the sake of a number.
3. Import a final time and run `python scripts/annotation_kit.py status`.
4. Commit by the blindness rule in [README.md](README.md): signals and lineage when complete (no second rater, D-022); drift only after the second rater's drift file is merged. Second raters open a pull request with only their own label file.
5. Write the two prose lines per rule in `RULE_CHANGE_PROPOSALS.md` after running `python scripts/annotation_kit.py proposals`.

## 6. Schedule

| Date | Step |
|---|---|
| Tue 2026-10-13 | Round 1 signals (209 rows) and lineage (58 pairs) complete, so round 2 fits before scoring |
| Fri 2026-10-16 | Round 1 drift (18 pairs) complete for both raters |
| 14 days after each item's round 1 label | Round 2 for that item (signals, lineage) |
| Tue 2026-10-27 | `annotation_kit.py score`, then the error analysis of disagreements and false positives |

Every day round 1 finishes earlier is a day more for round 2. Finishing round 1 on 2026-10-13 leaves round 2 for 2026-10-27, the scoring day itself.

## 7. Where the numbers go in the assignment

| Number | What it answers | Where it goes |
|---|---|---|
| Strict precision per category and rule, Wilson 95% | Are rule matches real, risky capabilities? Decides H1 | Sprint 2 validation sample and annotation protocol (#23); report: Evaluation and validation; VR-01 |
| Capability precision | Is the capability there at all? | Report: Evaluation and validation, Results (RQ1) |
| Miss rate, scaled to the 7,540 no-signal contents | What the scanner misses | Report: Evaluation and validation, Threats (measurement error); FMEA |
| What settled each false positive, per rule | Why rules misfire | Sprint 3 error analysis and manually inspected examples (#29); `RULE_CHANGE_PROPOSALS.md` |
| Lineage precision and share UNSURE | Are linked variants the same skill? | VR-03; report: Evaluation and validation |
| Drift change types | Why variants differ (RQ3) | Report: Results (RQ3), Discussion; VR-03 |
| Kappa (intra-rater for signals and lineage, inter-rater for drift) | Are the labels reliable? | VR-02; report: Evaluation and validation, Threats (conclusion validity) |
| Active time and sessions | What validation costs | Stand-ups, Sprint 2 retrospective (#26), individual reflection (#39) |

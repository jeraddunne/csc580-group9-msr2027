# Validation of the P-01 scanner

How to use: this page explains how the risk-signal scanner, the variant linking, and the drift classification are checked against human judgement. It lists the raters, the commands, the schedule, and where the numbers end up. The labelling rules are in [ANNOTATION_GUIDELINE.md](ANNOTATION_GUIDELINE.md).

## What is being validated

| Question | What a label says | Metric | Output |
|---|---|---|---|
| Are the rule matches real? | For each high-risk rule match on a sampled skill: RISKY, BENIGN_CONTEXT, or NOT_PRESENT | Strict precision (RISKY) and capability precision (RISKY or BENIGN_CONTEXT), per rule and per category, with Wilson 95% intervals | `results/validation_precision_by_rule.csv`, `results/validation_precision_by_category.csv` |
| What does the scanner miss? | For sampled skills with no rule match: NONE_PRESENT, or MISSED_RISKY with the missed category | Miss rate with a Wilson interval, scaled to the number of no-signal contents in the sample | `results/validation_recall.csv` |
| Are same-name variants really related? | For sampled near-duplicate pairs: YES, NO, or UNSURE | Lineage precision (YES among YES or NO) with an interval | `results/validation_lineage.csv` |
| Why do variants differ? | For every pair whose high-risk categories differ: TEMPLATE_UPDATE, LOCAL_ADAPTATION, HARDENING, CAPABILITY_ADDITION, or UNRELATED | Distribution of change types | `results/validation_drift.csv` |
| Are the labels reliable? | The same items labelled by two raters | Cohen's kappa and percent agreement: inter-rater between the primary rater and a teammate second rater (primary measure); intra-rater when the optional round 2 is done; human-vs-LLM reported separately | `results/validation_agreement.csv` |
| Which capability categories matter most? | Combines the above | FMEA ranking: RPN = severity x occurrence x detection | `results/fmea_category_ranking.csv` |

## Raters and reliability design (ADR-0006)

| Member | Rater id | Role |
|---|---|---|
| Jerad Dunne | `jd` | Primary rater for every kind |
| Leticia Aderhold | `la` | Second rater (kind assigned at the 2026-09-16 kickoff) |
| Allie Hodges | `ah` | Second rater (kind assigned at the 2026-09-16 kickoff) |
| Hina Kramer | `hk` | Second rater (kind assigned at the 2026-09-16 kickoff) |

The kickoff decides who second-rates which kind: signals (209 label rows), lineage (58 pairs), and drift (18 pairs). One teammate may take every kind, or the kinds may be split. The assignment is recorded in `docs/workspace/WORK_SIGNUP.md` section 6.

Reliability comes from four places:

1. **The guideline is written before labelling.** Labels follow a fixed decision order.
2. **Inter-rater agreement (primary measure).** The second rater labels round 1 of the same items independently. Cohen's kappa between the primary rater and the second rater is reported for each kind.
3. **Blindness rule.** The primary rater's filled label files for a kind are not committed until the second rater's labels for that kind are committed. The second rater never opens the primary rater's labels. On 2026-09-15 the committed `*_jd_r1.csv` files are the blank sheets created by the kit (0 labelled rows, pull request #45). The primary rater keeps filled labels local and checks `git status` before every commit so those files are not staged early.
4. **Optional intra-rater check.** A random 30% of items from each sample may be labelled again in round 2, at least 7 days after that item's round 1 label, in a shuffled order. That kappa is reported separately.

An LLM may be used as an additional rater only under a rater id starting with `llm-`. Its agreement is reported as `human-vs-llm`, it is disclosed in `ai-use-log.md`, and it is never counted as human agreement, never replaces the teammate second rater, and never supplies the primary labels.

The primary labels for precision, recall, lineage, and drift are a human's round 1 file, chosen by the kit as the one with the most labelled rows; `score` names the file it used.

## Commands

### Primary rater

```bash
# 1. Draw the samples (done once on 2026-09-14). Writes ID lists to data/annotations/samples/ (committed).
python scripts/annotation_kit.py sample

# 2. Create blank label sheets and reading packets for round 1.
#    Label CSVs go to data/annotations/; packets go to data/annotations/work/ (gitignored).
python scripts/annotation_kit.py sheet --rater jd --round 1
python scripts/annotation_kit.py ui --rater jd --round 1       # open data/annotations/work/label_signals_jd_r1.html
python scripts/annotation_kit.py import ~/Downloads/signals_jd_r1.csv   # after each session; do not commit yet

# 3. Check progress at any time.
python scripts/annotation_kit.py status

# 4. Optional round 2 (intra-rater subset only, shuffled).
python scripts/annotation_kit.py sheet --rater jd --round 2

# 5. Score everything that has been committed and labelled so far.
python scripts/annotation_kit.py score
```

### Second-rater workflow

Use your own rater id: Leticia `la`, Allie `ah`, Hina `hk`. The example uses signals; replace `signals` with `lineage` or `drift` for your assigned kind.

1. Accept the repository invitation.
2. Clone the repository outside OneDrive or iCloud: `git clone https://github.com/jeraddunne/csc580-group9-msr2027.git`.
3. Run `make setup`, then `make data`.
4. Read [ANNOTATION_GUIDELINE.md](ANNOTATION_GUIDELINE.md) once, fully.
5. Create your sheets and packets:

```bash
python scripts/annotation_kit.py sheet --rater <id> --round 1
python scripts/annotation_kit.py ui --rater <id> --round 1
```

6. Open `data/annotations/work/label_signals_<id>_r1.html` in a browser and label. Work in sessions of 30 to 40 minutes.
7. At the end of each session, click **Download CSV** in the page.
8. Import the download, which validates it and saves it to `data/annotations/signals_<id>_r1.csv`:

```bash
python scripts/annotation_kit.py import ~/Downloads/signals_<id>_r1.csv
```

9. When the kind is complete, open a pull request on a branch such as `data/<issue>-labels-signals-<id>` that contains **only** your label file. Another member reviews it for file validity only; nobody changes your labels.

Never open another rater's label files, including `*_jd_r1.csv`, and do not discuss specific items with the primary rater until both files for that kind are committed.

`sample` refuses to overwrite an existing sample, because new IDs would orphan existing labels. `sheet` never overwrites a label CSV that already exists; it only refreshes the reading packets. `score` exits with code 2 when a label file has problems; the problems are listed and invalid rows are left out.

## Sample sizes

The sample drawn on 2026-09-14 (seed 580, rule file sha256 recorded in `data/annotations/samples/SAMPLE_MANIFEST.json`):

| Sample | Items | Optional round 2 subset | Labelling effort per rater |
|---|---|---|---|
| Signals: flagged skills (up to 10 per high-risk category) plus no-signal skills | 147 items (40 with no signal), 209 label rows | 45 items | about 7 to 8 hours |
| Lineage: all differing pairs plus 40 random near-duplicate pairs | 58 pairs (18 differing, 40 random) | 18 pairs | about 2 hours |
| Drift: every pair whose high-risk categories differ | 18 pairs | 6 pairs | about 1.2 hours |

A flagged skill with several high-risk rule matches has one label row per matched rule. The sample was drawn from 13,000 distinct contents, of which 1,159 had a high-risk signal and 7,540 had no signal at all; the 7,540 is the population used to scale the recall estimate. Lineage and drift pairs were recomputed with `skill_risk.family_pairs` at a similarity threshold of 0.5 (245 lineage pairs, 18 differing).

## Schedule (Sprint 2)

| Dates | Step | Notes |
|---|---|---|
| Sun Sep 14 | Sample drawn and frozen; primary rater round 1 starts early (decision D-017) | The sample must not change after labelling starts |
| From Sep 14 | Primary rater labels round 1: signals, then lineage, then drift; runs `import` after each session | Filled primary files stay uncommitted (blindness rule) |
| Wed Sep 16 | Kickoff assigns second raters to kinds | `docs/workspace/WORK_SIGNUP.md` section 6 |
| From Thu Sep 17 | Second raters set up, read the guideline, and label round 1 | Plan the hours in each second rater's sprint capacity |
| Fri Oct 16 (target) | Second-rater label files committed, one pull request per file | Each pull request contains only that rater's label file |
| After each second-rater file is merged | Primary rater commits the filled file for the same kind | Never before the second rater's file for that kind |
| Optional, from Mon Sep 21 | Round 2 intra-rater labelling | Only label an item whose round 1 label is at least 7 days old; record the date in `notes` |
| By Tue Oct 27 | `score`, error analysis of rater disagreements and of NOT_PRESENT and BENIGN_CONTEXT cases, proposed rule changes | Rule changes follow the rule-file process: `status: proposed`, regression examples, pull request |
| Wed Oct 28 | Results presented in the Sprint 2 review | Precision, recall, inter-rater kappa, lineage precision, drift distribution, FMEA ranking |

Time estimate: about 3 minutes per signal item, 2 minutes per lineage pair, and 4 minutes per drift pair.

## After a rule change

Rules are frozen for scoring once round 1 starts. If error analysis leads to a rule change, the change is scored separately. Either re-scan and label a fresh small sample for the changed rule, or report precision for the old rule and the new rule side by side. Never silently re-score old labels against a new rule.

## Disagreements

After scoring, the two raters review every disagreement together and write the adjudicated reading in the error analysis. The original label files are never edited, because agreement must reflect independent labels.

## Safety

- Reading packets show indented excerpts with code fences disabled and a "Read only" banner. Never copy an excerpt into a terminal, and never open a URL from an excerpt.
- Nothing in the dataset is executed, imported, or fetched, in labelling or anywhere else.
- Committed files hold IDs, labels, and notes only. Packets with dataset text stay in `data/annotations/work/`, which git ignores.
- Notes must not name repositories or accounts.
- If an item looks actively malicious, stop, note only the `file_sha`, and raise it with the instructor before going further (TEAM_CHARTER.md section 11).

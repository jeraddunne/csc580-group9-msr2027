# Validation of the P-01 scanner

How to use: this page explains how the risk-signal scanner, the variant linking, and the drift classification are checked against human judgement. It lists the commands, the schedule, and where the numbers end up. The labelling rules are in [ANNOTATION_GUIDELINE.md](ANNOTATION_GUIDELINE.md).

## What is being validated

| Question | What a label says | Metric | Output |
|---|---|---|---|
| Are the rule matches real? | For each high-risk rule match on a sampled skill: RISKY, BENIGN_CONTEXT, or NOT_PRESENT | Strict precision (RISKY) and capability precision (RISKY or BENIGN_CONTEXT), per rule and per category, with Wilson 95% intervals | `results/validation_precision_by_rule.csv`, `results/validation_precision_by_category.csv` |
| What does the scanner miss? | For sampled skills with no rule match: NONE_PRESENT, or MISSED_RISKY with the missed category | Miss rate with a Wilson interval, scaled to the number of no-signal contents in the sample | `results/validation_recall.csv` |
| Are same-name variants really related? | For sampled near-duplicate pairs: YES, NO, or UNSURE | Lineage precision (YES among YES or NO) with an interval | `results/validation_lineage.csv` |
| Why do variants differ? | For every pair whose high-risk categories differ: TEMPLATE_UPDATE, LOCAL_ADAPTATION, HARDENING, CAPABILITY_ADDITION, or UNRELATED | Distribution of change types | `results/validation_drift.csv` |
| Are the labels reliable? | The same items labelled twice | Cohen's kappa and percent agreement (intra-rater; inter-rater when a second person labels; human-vs-LLM reported separately) | `results/validation_agreement.csv` |
| Which capability categories matter most? | Combines the above | FMEA ranking: RPN = severity x occurrence x detection | `results/fmea_category_ranking.csv` |

## Solo reliability design (ADR-0005)

There is one annotator, so reliability comes from three places:

1. **The guideline is written before labelling.** Labels follow a fixed decision order.
2. **Intra-rater agreement.** A random 30% of items from each sample is labelled again in round 2, at least 7 days after that item's round 1 label, in a shuffled order. Kappa between round 1 and round 2 is reported.
3. **Optional second rater.** The instructor or a classmate can label round 1 under their own rater id; this is reported as inter-rater agreement. An LLM may be used as an additional rater only under a rater id starting with `llm-`. Its agreement is reported as `human-vs-llm`, it is disclosed in `ai-use-log.md`, and it is never counted as human reliability or used as the primary labels.

The primary labels for precision, recall, lineage, and drift are always a human's round 1 file (the one with the most labelled rows).

## Commands

```bash
# 1. Draw the samples (once). Writes ID lists to data/annotations/samples/ (committed).
python scripts/annotation_kit.py sample

# 2. Create blank label sheets and reading packets for round 1.
#    Label CSVs go to data/annotations/ (committed); packets go to data/annotations/work/ (gitignored).
python scripts/annotation_kit.py sheet --rater jd --round 1
python scripts/annotation_kit.py ui --rater jd --round 1       # open data/annotations/work/label_signals_jd_r1.html
python scripts/annotation_kit.py import ~/Downloads/signals_jd_r1.csv   # after each session

# 3. Check progress at any time.
python scripts/annotation_kit.py status

# 4. Round 2 (intra-rater subset only, shuffled).
python scripts/annotation_kit.py sheet --rater jd --round 2

# 5. Score everything that has been labelled so far.
python scripts/annotation_kit.py score
```

`sample` refuses to overwrite an existing sample, because new IDs would orphan existing labels. `sheet` never overwrites a label CSV that already exists; it only refreshes the reading packets. `score` exits with code 2 when a label file has problems; the problems are listed and invalid rows are left out.

## Sample sizes

The sample drawn on 2026-09-14 (seed 580, rule file sha256 recorded in `data/annotations/samples/SAMPLE_MANIFEST.json`):

| Sample | Items | Round 2 subset |
|---|---|---|
| Signals: flagged skills (up to 10 per high-risk category) plus no-signal skills | 147 items (40 with no signal), 209 label rows | 45 items |
| Lineage: all differing pairs plus 40 random near-duplicate pairs | 58 pairs (18 differing, 40 random) | 18 pairs |
| Drift: every pair whose high-risk categories differ | 18 pairs | 6 pairs |

A flagged skill with several high-risk rule matches has one label row per matched rule. The sample was drawn from 13,000 distinct contents, of which 1,159 had a high-risk signal and 7,540 had no signal at all; the 7,540 is the population used to scale the recall estimate. Lineage and drift pairs were recomputed with `skill_risk.family_pairs` at a similarity threshold of 0.5 (245 lineage pairs, 18 differing).

## Schedule (Sprint 2)

| Dates | Step | Notes |
|---|---|---|
| Sun Sep 14 | Sample drawn and frozen; round 1 starts early (decision D-017) | The sample must not change after labelling starts |
| From Sep 14 | Round 1 labelling in the labelling page: signals, then lineage, then drift; run `import` after each session | An item's round 2 label can start 7 days after its round 1 label |
| From Mon Sep 21 | Round 2 intra-rater labelling | Only label an item whose round 1 label is at least 7 days old; record the date in `notes` |
| After round 2, and by Tue Oct 27 at the latest | `score`, error analysis of NOT_PRESENT and BENIGN_CONTEXT cases, proposed rule changes | Rule changes follow the rule-file process: `status: proposed`, regression examples, pull request |
| Wed Oct 28 | Results presented in the Sprint 2 review | Precision, recall, kappa, lineage precision, drift distribution, FMEA ranking |

Time estimate: about 3 minutes per signal item, 2 minutes per lineage pair, and 4 minutes per drift pair.

## After a rule change

Rules are frozen for scoring once round 1 starts. If error analysis leads to a rule change, the change is scored separately. Either re-scan and label a fresh small sample for the changed rule, or report precision for the old rule and the new rule side by side. Never silently re-score old labels against a new rule.

## Safety

- Reading packets show indented excerpts with code fences disabled and a "Read only" banner. Never copy an excerpt into a terminal, and never open a URL from an excerpt.
- Nothing in the dataset is executed, imported, or fetched, in labelling or anywhere else.
- Committed files hold IDs, labels, and notes only. Packets with dataset text stay in `data/annotations/work/`, which git ignores.
- Notes must not name repositories or accounts.
- If an item looks actively malicious, stop, note only the `file_sha`, and raise it with the instructor before going further (TEAM_CHARTER.md section 12).

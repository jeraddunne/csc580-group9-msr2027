# data/annotations/

How to use: manual labels for validating the P-01 scanner. Create files with `python scripts/annotation_kit.py`; labelling rules are in `docs/validation/ANNOTATION_GUIDELINE.md`.

## Layout

| Path | Contents | Committed |
|---|---|---|
| `samples/signals_sample.csv` | `file_sha`, `stratum`, `rule_ids` for the stratified signal sample | yes |
| `samples/lineage_sample.csv` | `file_sha_a`, `file_sha_b`, `similarity`, `source` (differing or random) | yes |
| `samples/drift_sample.csv` | `file_sha_a`, `file_sha_b`, `similarity`, `ordered`, `only_in_a`, `only_in_b` | yes |
| `samples/intra_rater_subset.csv` | `kind`, `item_id` (a `file_sha`, or `file_sha_a\|file_sha_b` for pairs) for round 2 | yes |
| `samples/SAMPLE_MANIFEST.json` | seed, parameters, rule-file sha256, dataset sha256, population counts, sample sizes | yes |
| `signals_<rater>_r<round>.csv` | `file_sha`, `rule_id`, `label`, `missed_category`, `notes` | yes |
| `lineage_<rater>_r<round>.csv` | `file_sha_a`, `file_sha_b`, `same_lineage`, `notes` | yes |
| `drift_<rater>_r<round>.csv` | `file_sha_a`, `file_sha_b`, `change_type`, `notes` | yes |
| `work/` | Reading packets with dataset excerpts, one Markdown file per item | **no** (gitignored) |

## Naming

- `<rater>`: a short lower-case id. Team ids are `jd` (Jerad Dunne, primary rater), `la` (Leticia Aderhold), `ah` (Allie Hodges), and `hk` (Hina Kramer). Ids starting with `llm-` mark a non-human rater.
- `<round>`: `1` for the first pass (every rater), `2` for the optional intra-rater re-label of the 30% subset.

## Rules

1. **Never overwrite or regenerate a label file.** `sheet` refuses to overwrite one that exists. Fix mistakes by editing the specific row, and explain the fix in `notes`.
2. **Never re-draw the sample after labelling starts.** `sample` refuses without `--force`.
3. **Only IDs, labels, and short notes are committed.** No dataset text, no repository or account names.
4. **Round 2 labels are independent.** Do not open round 1 files while labelling round 2.
5. Label values are upper case exactly as in the guideline. `python scripts/annotation_kit.py score` lists any invalid values.
6. **Blindness rule.** Do not commit primary-rater (`jd`) label files with labels for a kind until the second rater's labels for that kind are committed. The committed `*_jd_r1.csv` files are blank sheets. A second rater never opens another rater's label files.
7. **One rater per pull request.** A second rater's pull request contains only their own label file.

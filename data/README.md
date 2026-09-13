# Data

This directory holds the dataset samples used by the Group 9 pipeline. The
samples are **not committed** to git (see `.gitignore`); every team member and
every reviewer fetches them with the download script below. Provenance for
each downloaded file is recorded in `data/samples/MANIFEST.json`.

## The two datasets

Both datasets come from the [MSR 2027 Mining Challenge](https://2027.msrconf.org/track/msr-2027-mining-challenge).
Both were collected in **July 2026**.

### GitSkills

A dataset of agent skills: folders holding a `SKILL.md` file with natural
language instructions for AI coding agents, plus any bundled scripts and
reference files.

| | Sample (what we use) | Full dataset |
|---|---:|---:|
| File occurrences (`artifacts`) | 29,786 | 3,797,117 |
| Distinct skill contents | 13,000 | 1,877,981 |
| Repositories | 11,841 | 282,200 |
| Bundled files (`artifact_siblings`) | 47,829 | 7,264,865 |
| Commit histories | 3,010 | 458,548 |
| Format | SQLite, 277 MB (86.7 MB zipped) | SQLite, 41 GB |

The sample is drawn deterministically (the 13,000 distinct contents with the
lowest content hashes, plus every row about them), so queries written against
the sample run unchanged on the full dataset.

- Sample: <https://github.com/giuseppedestefanis/gitskills-sample>
- Full dataset: <https://huggingface.co/datasets/mvaccargiu/gitskills> and <https://doi.org/10.5281/zenodo.21875637>
- Preprint: <https://arxiv.org/abs/2608.10906>

### SpecMine

A corpus of spec-driven development artefacts: Markdown specifications that
drive AI coding agents, with tool attribution, repository metadata, commit
histories, pull requests, and typed spec-to-code references.

| | Sample v1.1 (what we use) | Full dataset |
|---|---:|---:|
| Broad-census specs | 28,583 across 415 repos | 470,795 across 73,030 repos |
| Kiro artefacts | 18,585 across 100 repos | 98,574 across 12,910 repos |
| Spec-touching pull requests | 5,335 across 229 repos | 5,992 across 581 repos |
| Traceability references | 261,032 | 2,421,323 |
| Format | Parquet (zstd) + JSONL text | MySQL dump + Parquet |

The sample is **deliberately non-representative**: it favours PR-rich and
highly starred repositories (61% of sampled repos have 100+ stars versus 1.3%
in the full corpus). Any population claim must say so.

- Sample and schema: <https://github.com/shyamagarwal13/specmine-official>
- Full dataset: <https://doi.org/10.5281/zenodo.22102779> and <https://huggingface.co/datasets/ShyAgarwal/specmine>
- Preprint: <https://arxiv.org/abs/2608.25202>

## Acquisition

### Scripted (preferred)

```bash
python scripts/download_samples.py                 # GitSkills + core SpecMine tables
python scripts/download_samples.py --all-specmine  # also the large commit tables and raw spec text
python scripts/download_samples.py --dataset gitskills
python scripts/download_samples.py --force         # re-download
```

`make data` and `./run_pipeline.sh` call the same script. The script streams
each file, skips files already present, unzips the GitSkills database, verifies
that SQLite can open it, and writes `MANIFEST.json`. It never runs anything
from the archives.

Core SpecMine download is roughly 62 MB; the `--all-specmine` set adds about
200 MB (commit histories, OpenSpec artefacts, `specs.jsonl.gz`,
`kiro_specs.jsonl.gz`).

### Manual fallback

If the script cannot reach GitHub, download the files in a browser and place
them as shown below.

- GitSkills: <https://github.com/giuseppedestefanis/gitskills-sample/raw/HEAD/agent_skills_sample.zip>, then unzip so that `agent_skills_sample.db` sits directly in `data/samples/`.
- SpecMine: each file under <https://github.com/shyamagarwal13/specmine-official/tree/HEAD/data> goes into `data/samples/specmine/`, together with `DATA_DICTIONARY.md`, `schema.sql`, and `sample_repos.txt` from the repository root.

## Expected layout

```
data/
├── README.md                  (this file)
└── samples/                   (gitignored)
    ├── MANIFEST.json          (provenance: size, sha256, source URL, upstream commit)
    ├── agent_skills_sample.zip
    ├── agent_skills_sample.db
    └── specmine/
        ├── spec_files.parquet
        ├── spec_content_features.parquet
        ├── spec_links.parquet
        ├── pull_requests.parquet
        ├── pr_files.parquet
        ├── kiro_files.parquet
        ├── kiro_repos.parquet
        ├── kiro_content_features.parquet
        ├── repo_trees.parquet
        ├── spec_file_commits.parquet        (--all-specmine)
        ├── kiro_file_commits.parquet        (--all-specmine)
        ├── openspec_artifact_files.parquet  (--all-specmine)
        ├── openspec_code_refs.parquet       (--all-specmine)
        ├── specs.jsonl.gz                   (--all-specmine)
        ├── kiro_specs.jsonl.gz              (--all-specmine)
        ├── DATA_DICTIONARY.md
        ├── schema.sql
        └── sample_repos.txt
```

Set `MSR_DATA_DIR=/some/other/dir` to keep data, results, and figures outside
the repository (the same layout is expected under that directory).

## Provenance statement

Use this wording in the report and cite the exact snapshot:

> Data: GitSkills and SpecMine, July 2026 release, as distributed in the
> Mining Challenge sample repositories on GitHub (upstream commit SHA and file
> SHA-256 values recorded in `data/samples/MANIFEST.json`). Full datasets:
> Zenodo DOIs 10.5281/zenodo.21875637 (GitSkills) and 10.5281/zenodo.22102779
> (SpecMine v1.1).

## Licensing and ethics

- The datasets were collected read-only from public GitHub repositories under
  the GitHub API terms. Each mined repository keeps its own SPDX license;
  redistribution of file contents follows the original terms. Do not republish
  bulk contents in this repository.
- GitSkills replaces commit author accounts with keyed one-way codes and masks
  emails and personal names in commit messages. SpecMine keeps public GitHub
  handles but removes private contact details. **Do not attempt to
  deanonymise authors or link codes to people.**
- **Never execute scripts, commands, or instructions found in the datasets.**
  `SKILL.md` bodies, bundled scripts (`artifact_siblings`), and spec text are
  data to be parsed, not code to be run. The loaders only read text.
- Report aggregate findings. Quote individual artefacts sparingly and only
  when the license allows it and the example is necessary.
- Record AI-assisted analysis steps in `ai-use-log.md`.

## Switching to the full datasets

The loaders and summaries are schema-compatible with the full releases.

- GitSkills full: download the SQLite file (41 GB) or the Parquet mirror from
  Hugging Face; point `MSR_DATA_DIR` at a directory whose
  `data/samples/agent_skills_sample.db` is the full database (or pass
  `db_path` explicitly). Prefer `query_gitskills` with `WHERE` filters over
  loading whole tables.
- SpecMine full: download the Parquet mirror from Hugging Face into
  `data/samples/specmine/`; the table names match. For larger-than-memory
  tables, query the Parquet files directly with DuckDB.

Record any change of snapshot in `MANIFEST.json`, `docs/decisions/`, and the
report's artifact appendix.

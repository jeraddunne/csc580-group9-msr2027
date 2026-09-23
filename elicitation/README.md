# Elicitation

Requirements elicitation for P-01 (assignment Phase B), and the notebook it was run against. The requirements it produced are in `RESEARCH_SPEC.md`.

The same 18 questions were put to two notebooks built on the same 24 sources: the **Google Notebook** (Gemini Notebook, account jeraddu@umich.edu), which is the primary Phase B record, and the **repository search notebook**, which quotes passages instead of generating prose and serves as a cross-check. Section 6 of the Google record compares them.

| File | What it is |
|---|---|
| `google-notebook-interview.md` | **The primary interview record** (Google Notebook). For each question: the answer, the source it cited, the team's interpretation, the follow-up or uncertainty, and the verification result. Start here. |
| `google-notebook/answers.json` | The Google Notebook's answers exactly as the page returned them, each with the SHA-256 prefix taken from the page. |
| `google-notebook/notebook-instructions.txt` | The custom chat instructions pasted into that notebook's **Configure chat**. |
| `notebook-interview.md` | The same interview against the repository's search notebook, with its own verification. |
| `questions.yaml` | The prepared questions: 15, plus 3 follow-ups asked after the first pass. |
| `notebook-transcript.md` | The notebook's full, verbatim answers. Generated; do not edit. |
| `verification-checks.md` | Read-only checks of the answers' data claims against the GitSkills sample (V01 to V18). Generated; do not edit. |
| `notebook/SOURCE_REGISTER.md`, `notebook/SOURCES_MANIFEST.json` | What the notebook knows: every source file with its tier, version, and SHA-256. Generated; do not edit. |

## The Google Notebook

Built at <https://notebook.google.com> in the account jeraddu@umich.edu, with the 24 files of the pinned source pack uploaded and the chat configured with `google-notebook/notebook-instructions.txt`. Rebuild it by running `python scripts/build_notebook_sources.py`, uploading every file in `build/notebook_sources/` except `SOURCES_MANIFEST.json` (upload the preprints as their PDFs, not their Markdown copies), and pasting the instructions into **Configure chat**.

## The repository search notebook

The group also built a notebook in this repository: `notebooks/01_elicitation_notebook.ipynb`, backed by `src/msr_pipeline/elicitation.py` and tested in `tests/test_elicitation.py`.

It is a **search notebook**. It splits the source pack into passages that keep their locator (source ID, file, section heading or PDF page, line), ranks them against a question with BM25, and answers with the best passages quoted word for word. It writes no text of its own, so it can only say what a source says. It can return passages that do not answer the question, which is why every answer is verified.

**Bounded by design.**

- It knows only the source pack. The dataset is not in it; the team uses the sample database to check answers, never as the notebook.
- Every question is asked in a **scope**, and dataset facts come only from the authoritative tier:

  | Scope | Searches |
  |---|---|
  | `gitskills` | A1, A2, A4, A6, A9 |
  | `specmine` | A1, A3, A5, A7, A8 |
  | `dataset` | every tier-A source |
  | `group` | tier G, Group 9's own documents |
  | `process` | tiers G and P |
  | `all` | everything |

- Each answer lists the question terms that no returned passage contains. That list is the notebook's way of saying what its sources may not establish.

**Source tiers.**

| Tier | Sources | Authority |
|---|---|---|
| A, authoritative | The nine sources the assignment names, at pinned versions: MSR 2027 challenge page, GitSkills and SpecMine preprints (arXiv v3, with page-marked text), Zenodo records, dataset cards, SpecMine GitHub mirror, GitSkills sample README | Facts about the datasets |
| G, group | This repository's documents, bundled by topic at the current commit: research design, data intake and dictionary, rules and validation, threats and the draft report, Scrum and Lean Six Sigma, project management and decisions, Git and work intake, pipeline API | What Group 9 decided and how it works |
| P, practitioner (optional) | One member's personal build method: phase gates, intake and policy rules, change control, testing, lessons learned | Process questions only |

## Reproduce

```bash
python scripts/build_notebook_sources.py        # build the pack into build/notebook_sources/ (add --practice-dir for tier P)
python -m msr_pipeline elicit                   # ask every question in questions.yaml; writes notebook-transcript.md
python -m msr_pipeline elicit --ask "What does history_fetched mark?" --scope gitskills
python scripts/check_interview_claims.py        # data checks V01 to V18; needs the sample (make data)
```

`make notebook-sources`, `make interview`, and `make interview-checks` run the same commands. Rebuild the pack only when a pinned version or a group document changes, and then re-run the interview: answers from different source packs are not comparable.

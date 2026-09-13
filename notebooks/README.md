# Notebooks

Notebooks are for exploration, sanity checks, and figure prototyping. They are
never the only source of a reported number.

## Rules

1. **Code that produces a reported table or figure lives in `src/msr_pipeline/`**
   with a test, and is run through the CLI or `run_pipeline.sh`. A notebook may
   call that code, but the notebook itself is not the reproducible path.
2. **Clear outputs before committing.** Use `jupyter nbconvert --clear-output --inplace <nb>`
   or the "Clear All Outputs" command. Large embedded outputs bloat the history
   and leak dataset content.
3. **Name notebooks `NN_topic.ipynb`** with a two-digit prefix in order of
   creation, for example `00_sample_overview.ipynb`, `01_skill_similarity_prototype.ipynb`.
4. **Load data through the package**, not with hand-written paths:

   ```python
   from msr_pipeline.load import load_gitskills, load_specmine
   ```

5. **Do not execute anything from the datasets.** Skill bodies, bundled scripts,
   and spec text are data.
6. When a notebook finding becomes a decision, record it in `docs/decisions/`
   and move the code into the package.

## Running

```bash
make setup                  # once
source .venv/Scripts/activate   # Windows Git Bash; use .venv/bin/activate elsewhere
jupyter lab notebooks/
```

# Release notes v1.0.0 (template)

How to use: fill before running `gh release create v1.0.0`. This text becomes the GitHub release body and is the artifact appendix summary.

## Summary

- Research question:
- One-sentence answer:
- Dataset snapshot used (release, DOI, download date):

## Reproduce the primary results

```
git clone https://github.com/jeraddunne/csc580-group9-msr2027.git
cd csc580-group9-msr2027
git checkout v1.0.0
pip install -r requirements.txt
python scripts/download_samples.py
make pipeline
make figures
```

Expected runtime: ___ minutes on a laptop. Primary outputs: `results/<table>.csv`, `figures/<figure>.png`.

## Attached assets

- `final.pdf`: final report
- `figures/*.png`: all report figures, regenerated from this tag
- `slides.pdf`: presentation

## Known limitations

- See `THREATS_TO_VALIDITY.md` and the report's threats section.

## Changes since v0.9.0-rc1

-

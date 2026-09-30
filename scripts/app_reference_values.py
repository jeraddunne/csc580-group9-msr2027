#!/usr/bin/env python
"""Answers from the pipeline's own functions, for the team app's formula tests.

The app (app/lib/formulas.js) re-implements the formulas it teaches in JavaScript;
app/tests/formulas.test.mjs checks them against these answers. Regenerate after changing a
formula in src/msr_pipeline/analysis.py, skill_risk.py, or validation.py:

    python scripts/app_reference_values.py
"""

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scipy.stats import mannwhitneyu  # noqa: E402

from msr_pipeline import analysis, skill_risk, validation  # noqa: E402

OUT = ROOT / "app" / "tests" / "reference_values.json"

out = {}
out["wilson"] = [
    {"k": k, "n": n, "ci": list(analysis.wilson_ci(k, n))}
    for k, n in [(1159, 12965), (0, 10), (10, 10), (3, 7), (511, 12965)]
]

group, reference = [1, 1, 2, 5, 9, 12], [1, 1, 1, 2, 3]
res = mannwhitneyu(group, reference, alternative="two-sided")
mw = analysis.mann_whitney(group, reference)
out["mann_whitney"] = {
    "group": group,
    "reference": reference,
    "u": float(res.statistic),
    "p": float(res.pvalue),
    "rank_biserial": mw["rank_biserial"],
}
g2, r2 = [3, 8, 9, 14, 20, 25, 31], [1, 2, 4, 6, 7, 10]
res2 = mannwhitneyu(g2, r2, alternative="two-sided", method="asymptotic")
out["mann_whitney_no_ties"] = {
    "group": g2,
    "reference": r2,
    "u": float(res2.statistic),
    "p": float(res2.pvalue),
}

out["holm"] = {
    "p": [0.01, 0.04, 0.03, 0.2, float("nan")],
    "adjusted": analysis.holm_adjust([0.01, 0.04, 0.03, 0.2, float("nan")]),
}

a = ["yes"] * 20 + ["no"] * 15 + ["yes"] * 5 + ["no"] * 10
b = ["yes"] * 20 + ["no"] * 15 + ["no"] * 5 + ["yes"] * 10
out["kappa"] = {
    "a": a,
    "b": b,
    "kappa": validation.cohen_kappa(a, b)[0],
    "agreement": validation.percent_agreement(a, b),
}
a3 = [
    "RISKY",
    "RISKY",
    "BENIGN_CONTEXT",
    "NOT_PRESENT",
    "RISKY",
    "BENIGN_CONTEXT",
    "BENIGN_CONTEXT",
    "RISKY",
]
b3 = [
    "RISKY",
    "BENIGN_CONTEXT",
    "BENIGN_CONTEXT",
    "NOT_PRESENT",
    "RISKY",
    "RISKY",
    "BENIGN_CONTEXT",
    "RISKY",
]
out["kappa3"] = {"a": a3, "b": b3, "kappa": validation.cohen_kappa(a3, b3)[0]}

p = validation._precision_row(12, 5, 3)
out["precision"] = {"risky": 12, "benign": 5, "not_present": 3, "row": p}

t1 = (
    "Run the install script to set up the tool. Then open the config file and add your "
    "project name before you start the server."
)
t2 = (
    "Run the install script to set up the tool. Then open the config file and add your "
    "team name before you start the local server."
)
t3 = "Short text"
out["jaccard"] = [
    {
        "a": t1,
        "b": t2,
        "similarity": skill_risk.jaccard(skill_risk.shingles(t1), skill_risk.shingles(t2)),
        "shingles_a": len(skill_risk.shingles(t1)),
    },
    {
        "a": t1,
        "b": t1,
        "similarity": skill_risk.jaccard(skill_risk.shingles(t1), skill_risk.shingles(t1)),
        "shingles_a": len(skill_risk.shingles(t1)),
    },
    {
        "a": t3,
        "b": "short TEXT!",
        "similarity": skill_risk.jaccard(
            skill_risk.shingles(t3), skill_risk.shingles("short TEXT!")
        ),
        "shingles_a": len(skill_risk.shingles(t3)),
    },
    {
        "a": "",
        "b": t1,
        "similarity": skill_risk.jaccard(skill_risk.shingles(""), skill_risk.shingles(t1)),
        "shingles_a": 0,
    },
]
out["irr"] = {"coef": 0.34438930675802715, "irr": math.exp(0.34438930675802715)}


def clean(x):
    if isinstance(x, float) and math.isnan(x):
        return None
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    return x


OUT.write_text(json.dumps(clean(out), indent=1) + "\n", encoding="utf-8", newline="\n")
print(f"wrote {OUT.relative_to(ROOT)}")

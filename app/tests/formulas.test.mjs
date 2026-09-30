// The app's formulas must give the same answers as the pipeline's Python functions.
// Expected values: app/tests/reference_values.json, produced by those Python functions.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  cohenKappa,
  holmAdjust,
  irr,
  jaccard,
  kappaFromTable,
  mannWhitney,
  precision,
  shingles,
  similarityDetail,
  wilsonCI,
} from "../lib/formulas.js";

const ref = JSON.parse(readFileSync(new URL("./reference_values.json", import.meta.url), "utf8"));
const close = (a, b, tol = 1e-9) => assert.ok(Math.abs(a - b) <= tol, `${a} vs ${b}`);

test("Wilson interval matches analysis.wilson_ci", () => {
  for (const { k, n, ci } of ref.wilson) {
    const [lo, hi] = wilsonCI(k, n);
    close(lo, ci[0]);
    close(hi, ci[1]);
  }
});

test("Mann-Whitney U, p-value, and rank-biserial match scipy and analysis.rank_biserial", () => {
  const m = ref.mann_whitney;
  const r = mannWhitney(m.group, m.reference);
  close(r.u, m.u);
  close(r.p, m.p, 1e-6);
  close(r.rankBiserial, m.rank_biserial);
  const m2 = ref.mann_whitney_no_ties;
  const r2 = mannWhitney(m2.group, m2.reference);
  close(r2.u, m2.u);
  close(r2.p, m2.p, 1e-6);
});

test("Holm adjustment matches analysis.holm_adjust, NaN stays NaN", () => {
  const p = ref.holm.p.map((x) => (x === null ? NaN : x));
  const got = holmAdjust(p);
  ref.holm.adjusted.forEach((want, i) => (want === null ? assert.ok(Number.isNaN(got[i])) : close(got[i], want)));
});

test("Cohen's kappa matches validation.cohen_kappa for two and three categories", () => {
  close(cohenKappa(ref.kappa.a, ref.kappa.b).kappa, ref.kappa.kappa);
  close(cohenKappa(ref.kappa3.a, ref.kappa3.b).kappa, ref.kappa3.kappa);
  assert.ok(Number.isNaN(kappaFromTable([[5, 0], [0, 0]]).kappa), "one category only is undefined");
});

test("precision matches validation._precision_row", () => {
  const { risky, benign, not_present: notPresent, row } = ref.precision;
  const p = precision(risky, benign, notPresent);
  close(p.strict, row.strict_precision);
  close(p.capability, row.capability_precision);
  close(p.strictCI[0], row.strict_ci_low);
  close(p.capabilityCI[1], row.capability_ci_high);
});

test("word 5-chunk similarity matches skill_risk.jaccard(shingles(a), shingles(b))", () => {
  for (const j of ref.jaccard) {
    close(jaccard(shingles(j.a), shingles(j.b)), j.similarity);
    assert.equal(shingles(j.a).size, j.shingles_a);
  }
  const d = similarityDetail(ref.jaccard[0].a, ref.jaccard[0].b);
  assert.equal(d.shared.length + d.onlyA.length, d.a.size);
  close(d.similarity, d.shared.length / d.union);
});

test("incidence rate ratio is exp(coefficient) as in analysis.rq2_negbin", () => {
  close(irr(ref.irr.coef), ref.irr.irr);
});

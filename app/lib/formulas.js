// The pipeline's formulas in JavaScript, for the app's worked examples.
// Each function mirrors a Python function named in its comment; app/tests/formulas.test.mjs
// checks them against answers computed by that Python code (app/tests/reference_values.json).

export const Z_95 = 1.959963984540054;

// analysis.wilson_ci / validation.wilson_ci: Wilson score interval for a proportion.
export function wilsonCI(successes, n, z = Z_95) {
  if (n <= 0) return [NaN, NaN];
  const p = successes / n;
  const z2 = z * z;
  const denom = 1 + z2 / n;
  const centre = (p + z2 / (2 * n)) / denom;
  const half = (z * Math.sqrt((p * (1 - p)) / n + z2 / (4 * n * n))) / denom;
  return [Math.max(0, centre - half), Math.min(1, centre + half)];
}

// skill_risk.shingles: lower-cased alphanumeric words, then every run of k words.
// The pipeline stores each run as a CRC32 number to save memory; the words are kept here
// so the example can show them. Set sizes and similarity are the same.
export function words(text) {
  return (text || "").toLowerCase().match(/[a-z0-9]+/g) || [];
}

export function shingles(text, k = 5) {
  const tokens = words(text);
  if (tokens.length === 0) return new Set();
  if (tokens.length < k) return new Set([tokens.join(" ")]);
  const out = new Set();
  for (let i = 0; i + k <= tokens.length; i += 1) out.add(tokens.slice(i, i + k).join(" "));
  return out;
}

// skill_risk.jaccard: shared chunks divided by all distinct chunks.
export function jaccard(a, b) {
  if (a.size === 0 || b.size === 0) return 0;
  let shared = 0;
  for (const x of a) if (b.has(x)) shared += 1;
  return shared / (a.size + b.size - shared);
}

export function similarityDetail(textA, textB, k = 5) {
  const a = shingles(textA, k);
  const b = shingles(textB, k);
  const shared = [...a].filter((x) => b.has(x));
  const onlyA = [...a].filter((x) => !b.has(x));
  const onlyB = [...b].filter((x) => !a.has(x));
  return { a, b, shared, onlyA, onlyB, union: a.size + b.size - shared.length, similarity: jaccard(a, b) };
}

// Ranks with ties given the average rank, as in scipy.stats.rankdata.
export function averageRanks(values) {
  const order = values.map((v, i) => [v, i]).sort((x, y) => x[0] - y[0]);
  const ranks = new Array(values.length);
  let i = 0;
  while (i < order.length) {
    let j = i;
    while (j + 1 < order.length && order[j + 1][0] === order[i][0]) j += 1;
    const avg = (i + j) / 2 + 1;
    for (let t = i; t <= j; t += 1) ranks[order[t][1]] = avg;
    i = j + 1;
  }
  return ranks;
}

function normalSf(z) {
  // Upper tail of the standard normal, via the complementary error function.
  return 0.5 * erfc(z / Math.SQRT2);
}

function erfc(x) {
  // Numerical Recipes erfc, relative error below 1.2e-7.
  const z = Math.abs(x);
  const t = 1 / (1 + 0.5 * z);
  const r =
    t *
    Math.exp(
      -z * z -
        1.26551223 +
        t *
          (1.00002368 +
            t *
              (0.37409196 +
                t *
                  (0.09678418 +
                    t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277))))))))
    );
  return x >= 0 ? r : 2 - r;
}

// analysis.mann_whitney (scipy mannwhitneyu, two-sided, normal approximation with tie and
// continuity corrections) and analysis.rank_biserial.
export function mannWhitney(group, reference) {
  const n1 = group.length;
  const n2 = reference.length;
  const all = [...group, ...reference];
  const ranks = averageRanks(all);
  const r1 = ranks.slice(0, n1).reduce((s, r) => s + r, 0);
  const u = r1 - (n1 * (n1 + 1)) / 2;
  const n = n1 + n2;
  const counts = new Map();
  for (const v of all) counts.set(v, (counts.get(v) || 0) + 1);
  let tie = 0;
  for (const t of counts.values()) tie += t ** 3 - t;
  const mu = (n1 * n2) / 2;
  const sigma = Math.sqrt(((n1 * n2) / 12) * (n + 1 - tie / (n * (n - 1))));
  const z = sigma > 0 ? (Math.abs(u - mu) - 0.5) / sigma : 0;
  const p = sigma > 0 ? Math.min(1, 2 * normalSf(Math.max(z, 0))) : 1;
  return { u, p, rankBiserial: (2 * u) / (n1 * n2) - 1, ranks, rankSumGroup: r1, n1, n2 };
}

// analysis.holm_adjust: Holm step-down adjusted p-values; NaN stays NaN.
export function holmAdjust(pValues) {
  const idx = pValues.map((p, i) => i).filter((i) => !Number.isNaN(pValues[i]));
  const order = [...idx].sort((a, b) => pValues[a] - pValues[b]);
  const m = order.length;
  const adjusted = pValues.map(() => NaN);
  let running = 0;
  order.forEach((i, rank) => {
    running = Math.max(running, Math.min(1, (m - rank) * pValues[i]));
    adjusted[i] = running;
  });
  return adjusted;
}

// validation.cohen_kappa: agreement beyond what chance would give.
export function cohenKappa(labelsA, labelsB) {
  if (labelsA.length !== labelsB.length) throw new Error("label lists must have the same length");
  const n = labelsA.length;
  if (n === 0) return { kappa: NaN, observed: NaN, expected: NaN, table: [], categories: [] };
  const categories = [...new Set([...labelsA, ...labelsB])].sort();
  const index = new Map(categories.map((c, i) => [c, i]));
  const table = categories.map(() => categories.map(() => 0));
  labelsA.forEach((a, i) => {
    table[index.get(a)][index.get(labelsB[i])] += 1;
  });
  return kappaFromTable(table, categories);
}

export function kappaFromTable(table, categories = []) {
  const n = table.flat().reduce((s, x) => s + x, 0);
  if (n === 0) return { kappa: NaN, observed: NaN, expected: NaN, table, categories };
  const rows = table.map((r) => r.reduce((s, x) => s + x, 0));
  const cols = table[0].map((_, j) => table.reduce((s, r) => s + r[j], 0));
  const observed = table.reduce((s, r, i) => s + r[i], 0) / n;
  const expected = rows.reduce((s, r, i) => s + r * cols[i], 0) / (n * n);
  const kappa = Math.abs(expected - 1) < 1e-12 ? NaN : (observed - expected) / (1 - expected);
  return { kappa, observed, expected, table, categories, rows, cols, n };
}

// A common reading of kappa (Landis and Koch, 1977), for plain-language labels.
export function kappaWords(kappa) {
  if (Number.isNaN(kappa)) return "undefined";
  if (kappa < 0) return "worse than chance";
  if (kappa <= 0.2) return "slight";
  if (kappa <= 0.4) return "fair";
  if (kappa <= 0.6) return "moderate";
  if (kappa <= 0.8) return "substantial";
  return "almost perfect";
}

// validation._precision_row: strict (risky only) and capability (risky or benign context).
// validation.wilson_ci uses z = 1.96, where analysis.wilson_ci uses the exact 1.959964;
// the difference is in the sixth decimal place.
export function precision(risky, benign, notPresent) {
  const n = risky + benign + notPresent;
  return {
    n,
    strict: n ? risky / n : NaN,
    strictCI: wilsonCI(risky, n, 1.96),
    capability: n ? (risky + benign) / n : NaN,
    capabilityCI: wilsonCI(risky + benign, n, 1.96),
  };
}

// analysis.rq2_negbin: a coefficient becomes an incidence rate ratio by exp().
export function irr(coef) {
  return Math.exp(coef);
}

export function percent(x, digits = 1) {
  return Number.isFinite(x) ? `${(100 * x).toFixed(digits)}%` : "n/a";
}

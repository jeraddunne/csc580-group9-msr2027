// The rule tester: the pipeline's active rules (app/data/rules.json, exported from
// rules/skill_risk_rules.yaml) run on text typed into the page. Text only; nothing runs.

export function compileRules(data) {
  return data.rules.map((r) => {
    const regexes = r.patterns.map((p) => new RegExp(p, r.flags));
    return { ...r, regexes, test: (text) => regexes.some((re) => re.test(text)) };
  });
}

// Which rules match, the highest severity, and whether that reaches the high-risk cutoff
// (severity 6 or more, as skill_risk.HIGH_RISK_SEVERITY).
export function scanText(text, rules, highRiskSeverity = 6) {
  const matches = rules
    .filter((r) => text && r.test(text))
    .map((r) => {
      const re = r.regexes.find((x) => x.test(text));
      const m = re ? new RegExp(re.source, re.flags.replace("g", "")).exec(text) : null;
      return { id: r.id, category: r.category, severity: r.severity, note: r.note, excerpt: m ? m[0] : "" };
    })
    .sort((a, b) => b.severity - a.severity);
  const maxSeverity = matches.reduce((s, m) => Math.max(s, m.severity), 0);
  return { matches, maxSeverity, highRisk: maxSeverity >= highRiskSeverity };
}

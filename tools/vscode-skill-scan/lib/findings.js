'use strict';
// Pure helpers for the Skill Scan extension: no VS Code API here, so `node --test` can check them.
// Input is the JSON report written by `skill-scan --format json` (schema_version 1).

const path = require('node:path');

const SCHEMA_VERSION = 1;
const SKILL_FILE_NAMES = new Set(['skill.md']);
const SCRIPT_EXTENSIONS = new Set([
  '.sh', '.bash', '.zsh', '.ps1', '.py', '.js', '.mjs', '.cjs', '.ts', '.rb', '.pl', '.bat', '.cmd',
]);
const RULE_CATALOG_URL =
  'https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/docs/research/RULE_CATALOG.md';

const OUTCOME_LABEL = {
  high_risk: 'High-risk signal',
  no_high_risk_signal: 'No high-risk signal',
  incomplete: 'Incomplete scan',
};

/** True for a SKILL.md, or a script that sits inside a folder holding a SKILL.md. */
function isSkillPath(filePath, exists, stopDir) {
  const base = path.basename(filePath).toLowerCase();
  if (SKILL_FILE_NAMES.has(base)) return true;
  if (!SCRIPT_EXTENSIONS.has(path.extname(base))) return false;
  let dir = path.dirname(filePath);
  const stop = stopDir ? path.resolve(stopDir) : null;
  for (;;) {
    if (exists(path.join(dir, 'SKILL.md')) || exists(path.join(dir, 'skill.md'))) return true;
    const parent = path.dirname(dir);
    if (parent === dir || (stop && path.resolve(dir) === stop)) return false;
    dir = parent;
  }
}

function checkReport(report) {
  if (!report || report.tool !== 'skill-scan') {
    throw new Error('not a skill-scan report');
  }
  if (report.schema_version !== SCHEMA_VERSION) {
    throw new Error(
      `skill-scan report schema ${report.schema_version}, extension expects ${SCHEMA_VERSION}`,
    );
  }
}

function message(finding, cutoff, unit) {
  const head = `${finding.rule_id} ${finding.title} (${finding.category}, severity ${finding.severity})`;
  const status = finding.high_risk
    ? 'High-risk signal: a reviewer labels it RISKY, BENIGN_CONTEXT or NOT_PRESENT.'
    : `Context match below severity ${cutoff}, not a finding to triage.`;
  const lines = [`${head}. ${status}`];
  if (finding.guidance) lines.push('', finding.guidance);
  if (unit && unit.outcome === 'incomplete') {
    lines.push('', 'This skill also has files that could not be scanned (incomplete scan).');
  }
  return lines.join('\n');
}

/**
 * Turn a report into diagnostic specs: one per finding, with 0-based ranges and an absolute file.
 * `cwd` is the folder the command ran in (report paths are relative to it).
 */
function toDiagnosticSpecs(report, cwd, options = {}) {
  checkReport(report);
  const showContext = options.showContext !== false;
  const cutoff = report.rules.cutoff;
  const specs = [];
  for (const unit of report.units) {
    const findings = unit.high_risk_findings.concat(showContext ? unit.context_matches : []);
    for (const f of findings) {
      specs.push({
        file: path.resolve(cwd, f.path),
        startLine: f.line - 1,
        startColumn: f.column - 1,
        endLine: f.end_line - 1,
        endColumn: Math.max(f.end_column - 1, 0),
        severity: f.high_risk ? 'warning' : 'information',
        message: message(f, cutoff, unit),
        code: f.rule_id,
        codeUrl: RULE_CATALOG_URL,
        source: 'skill-scan',
      });
    }
    for (const u of unit.unreadable) {
      specs.push({
        file: path.resolve(cwd, u.path),
        startLine: 0,
        startColumn: 0,
        endLine: 0,
        endColumn: 0,
        severity: 'warning',
        message:
          `Not scanned: ${u.reason}. The skill does not take the no-signal path; ` +
          'fix the file or read it by hand (review workflow step 3).',
        code: 'incomplete-scan',
        codeUrl: RULE_CATALOG_URL,
        source: 'skill-scan',
      });
    }
  }
  return specs;
}

/** Group specs by file, so each file gets one diagnostics list. */
function groupByFile(specs) {
  const byFile = new Map();
  for (const s of specs) {
    if (!byFile.has(s.file)) byFile.set(s.file, []);
    byFile.get(s.file).push(s);
  }
  return byFile;
}

/** Short status-bar text, for example "Skill scan: 1 high-risk, 1 incomplete". */
function statusText(report) {
  checkReport(report);
  const s = report.summary;
  if (s.units === 0) return 'Skill scan: nothing to scan';
  const parts = [];
  if (s.high_risk) parts.push(`${s.high_risk} high-risk`);
  if (s.incomplete) parts.push(`${s.incomplete} incomplete`);
  if (s.no_high_risk_signal) parts.push(`${s.no_high_risk_signal} no high-risk signal`);
  return `Skill scan: ${parts.join(', ')}`;
}

/** Arguments for the command line. */
function commandArgs(targets, settings = {}) {
  const args = [...targets, '--format', 'json'];
  if (settings.rulesPath) args.push('--rules', settings.rulesPath);
  if (Number.isInteger(settings.cutoff)) args.push('--cutoff', String(settings.cutoff));
  return args;
}

module.exports = {
  OUTCOME_LABEL,
  SCHEMA_VERSION,
  commandArgs,
  groupByFile,
  isSkillPath,
  statusText,
  toDiagnosticSpecs,
};

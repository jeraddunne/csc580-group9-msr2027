'use strict';
// Tests for lib/findings.js against a report the real command wrote
// (test/fixtures/report.json; tests/test_skill_scan.py checks that it is still current).

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const lib = require('../lib/findings');

const report = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures', 'report.json'), 'utf8'));
const cwd = path.resolve('/repo');

test('every finding becomes a 0-based diagnostic in an absolute file', () => {
  const specs = lib.toDiagnosticSpecs(report, cwd);
  const rce = specs.find((s) => s.code === 'R-RCE-001');
  assert.ok(rce, 'pipe-to-shell finding present');
  assert.equal(rce.file, path.resolve(cwd, 'examples/skill-scan/risky-installer/SKILL.md'));
  assert.equal(rce.startLine, 10); // line 11 in the report
  assert.equal(rce.startColumn, 0);
  assert.equal(rce.severity, 'warning');
  assert.match(rce.message, /RISKY, BENIGN_CONTEXT or NOT_PRESENT/);
  assert.match(rce.message, /pipes it straight into a shell/); // the rule's reviewer guidance
});

test('context matches are information, and can be hidden', () => {
  const all = lib.toDiagnosticSpecs(report, cwd);
  const shell = all.filter((s) => s.code === 'R-SHL-001');
  assert.ok(shell.length >= 1);
  assert.ok(shell.every((s) => s.severity === 'information'));
  const highOnly = lib.toDiagnosticSpecs(report, cwd, { showContext: false });
  assert.ok(highOnly.every((s) => s.code !== 'R-SHL-001'));
});

test('an unscannable file is flagged on its first line', () => {
  const specs = lib.toDiagnosticSpecs(report, cwd);
  const gap = specs.find((s) => s.code === 'incomplete-scan');
  assert.ok(gap);
  assert.equal(gap.file, path.resolve(cwd, 'examples/skill-scan/incomplete-scan/bin/helper.sh'));
  assert.equal(gap.startLine, 0);
  assert.match(gap.message, /binary content/);
});

test('specs group by file', () => {
  const byFile = lib.groupByFile(lib.toDiagnosticSpecs(report, cwd));
  const risky = byFile.get(path.resolve(cwd, 'examples/skill-scan/risky-installer/SKILL.md'));
  assert.ok(risky.length >= 2);
});

test('status text counts outcomes', () => {
  assert.equal(
    lib.statusText(report),
    'Skill scan: 1 high-risk, 1 incomplete, 2 no high-risk signal',
  );
});

test('a report from another schema is refused', () => {
  assert.throws(() => lib.toDiagnosticSpecs({ ...report, schema_version: 99 }, cwd), /schema 99/);
  assert.throws(() => lib.statusText({ tool: 'other' }), /not a skill-scan report/);
});

test('skill files and scripts inside skill folders are recognised', () => {
  const root = path.resolve('/w');
  const files = new Set([path.join(root, 'skills', 'a', 'SKILL.md')]);
  const exists = (p) => files.has(p);
  assert.ok(lib.isSkillPath(path.join(root, 'skills', 'a', 'SKILL.md'), exists, root));
  assert.ok(lib.isSkillPath(path.join(root, 'skills', 'a', 'scripts', 'run.sh'), exists, root));
  assert.ok(!lib.isSkillPath(path.join(root, 'skills', 'a', 'notes.txt'), exists, root));
  assert.ok(!lib.isSkillPath(path.join(root, 'tools', 'build.sh'), exists, root));
});

test('command arguments follow the settings', () => {
  assert.deepEqual(lib.commandArgs(['x']), ['x', '--format', 'json']);
  assert.deepEqual(lib.commandArgs(['x'], { rulesPath: 'r.yaml', cutoff: 7 }), [
    'x', '--format', 'json', '--rules', 'r.yaml', '--cutoff', '7',
  ]);
  assert.deepEqual(lib.commandArgs(['x'], { cutoff: null }), ['x', '--format', 'json']);
});

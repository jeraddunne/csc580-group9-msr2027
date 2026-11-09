'use strict';
// Skill Scan for VS Code (#150): runs `skill-scan --format json` on the skill of the file you
// open or save and shows the findings as diagnostics. The scanner, not this extension, decides
// what matches; the extension only displays the report. A rule match is a signal, not a verdict.

const vscode = require('vscode');
const fs = require('node:fs');
const path = require('node:path');
const { execFile } = require('node:child_process');
const lib = require('./lib/findings');

let collection;
let status;
let output;

function settings() {
  const c = vscode.workspace.getConfiguration('skillScan');
  return {
    command: c.get('command') || 'skill-scan',
    rulesPath: c.get('rulesPath') || '',
    cutoff: c.get('cutoff'),
    runOnSave: c.get('runOnSave'),
    runOnOpen: c.get('runOnOpen'),
    showContext: c.get('showContext'),
  };
}

function folderFor(uri) {
  const folder = vscode.workspace.getWorkspaceFolder(uri);
  return folder ? folder.uri.fsPath : path.dirname(uri.fsPath);
}

function isSkillDocument(doc) {
  if (doc.uri.scheme !== 'file') return false;
  return lib.isSkillPath(doc.uri.fsPath, fs.existsSync, folderFor(doc.uri));
}

function toDiagnostic(spec) {
  const range = new vscode.Range(spec.startLine, spec.startColumn, spec.endLine, spec.endColumn);
  const severity =
    spec.severity === 'warning'
      ? vscode.DiagnosticSeverity.Warning
      : vscode.DiagnosticSeverity.Information;
  const d = new vscode.Diagnostic(range, spec.message, severity);
  d.source = spec.source;
  d.code = { value: spec.code, target: vscode.Uri.parse(spec.codeUrl) };
  return d;
}

function run(targets, cwd) {
  const s = settings();
  const args = lib.commandArgs(targets, s);
  output.appendLine(`$ ${s.command} ${args.join(' ')}   (in ${cwd})`);
  status.text = '$(sync~spin) Skill scan';
  return new Promise((resolve) => {
    execFile(s.command, args, { cwd, maxBuffer: 20 * 1024 * 1024 }, (error, stdout, stderr) => {
      if (stderr) output.appendLine(stderr.trim());
      // Exit status 1 only means --fail-on was met; the report is still on stdout.
      if (error && (error.code === 'ENOENT' || error.code === 2 || !stdout)) {
        const hint =
          error.code === 'ENOENT'
            ? `"${s.command}" was not found. Install it (pip install -e . in the repository) or set skillScan.command.`
            : `skill-scan failed: ${stderr || error.message}`;
        vscode.window.showWarningMessage(hint);
        status.text = '$(warning) Skill scan: not run';
        return resolve(null);
      }
      let report;
      try {
        report = JSON.parse(stdout);
        apply(report, cwd, s);
      } catch (e) {
        vscode.window.showWarningMessage(`Skill scan: ${e.message}`);
        status.text = '$(warning) Skill scan: unreadable report';
        return resolve(null);
      }
      resolve(report);
    });
  });
}

function apply(report, cwd, s) {
  const specs = lib.toDiagnosticSpecs(report, cwd, { showContext: s.showContext });
  // Clear every scanned file first, so fixed findings disappear.
  for (const unit of report.units) {
    for (const f of unit.files_scanned) collection.delete(vscode.Uri.file(path.resolve(cwd, f)));
  }
  for (const [file, list] of lib.groupByFile(specs)) {
    collection.set(vscode.Uri.file(file), list.map(toDiagnostic));
  }
  status.text = `$(shield) ${lib.statusText(report)}`;
  status.tooltip = 'A rule match is a signal, not a verdict. Click to rescan this skill.';
  for (const unit of report.units) {
    output.appendLine(`${unit.path}: ${lib.OUTCOME_LABEL[unit.outcome]}. ${unit.next_step}`);
  }
}

async function scanDocument(doc) {
  if (!doc || !isSkillDocument(doc)) return;
  await run([doc.uri.fsPath], folderFor(doc.uri));
}

function activate(context) {
  collection = vscode.languages.createDiagnosticCollection('skill-scan');
  output = vscode.window.createOutputChannel('Skill Scan');
  status = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 50);
  status.command = 'skillScan.scanFile';
  status.text = '$(shield) Skill scan';
  status.show();

  context.subscriptions.push(
    collection,
    output,
    status,
    vscode.commands.registerCommand('skillScan.scanFile', () =>
      scanDocument(vscode.window.activeTextEditor && vscode.window.activeTextEditor.document),
    ),
    vscode.commands.registerCommand('skillScan.scanWorkspace', async () => {
      for (const folder of vscode.workspace.workspaceFolders || []) {
        await run([folder.uri.fsPath], folder.uri.fsPath);
      }
    }),
    vscode.commands.registerCommand('skillScan.clear', () => collection.clear()),
    vscode.workspace.onDidSaveTextDocument((doc) => {
      if (settings().runOnSave) scanDocument(doc);
    }),
    vscode.workspace.onDidOpenTextDocument((doc) => {
      if (settings().runOnOpen) scanDocument(doc);
    }),
  );

  if (settings().runOnOpen) {
    for (const editor of vscode.window.visibleTextEditors) scanDocument(editor.document);
  }
}

function deactivate() {}

module.exports = { activate, deactivate };

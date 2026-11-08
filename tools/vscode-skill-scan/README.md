# Skill Scan for VS Code

Shows the findings of `skill-scan` (CSC 580 Group 9, #150) while you edit an agent skill. When you open or save a `SKILL.md`, or a script inside a folder that holds one, the extension runs `skill-scan --format json` on that skill and shows:

- a **warning** on each high-risk signal (severity 6 or more): a reviewer labels it RISKY, BENIGN_CONTEXT or NOT_PRESENT;
- **information** on each context match below the cutoff (can be turned off);
- a **warning** on the first line of any bundled file that could not be scanned (incomplete scan).

Hover a finding to read the rule's reviewer guidance; the rule id links to the rule catalog. The status bar shows the skill's outcome; click it to rescan. A rule match is a signal, not a verdict. The full description of the tool is in [`docs/TOOL.md`](../../docs/TOOL.md).

## Requirements

The `skill-scan` command. In the repository:

```bash
python -m venv .venv && . .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e .
skill-scan --version
```

If VS Code does not find it on the PATH, set `skillScan.command` to the full path, for example `${workspaceFolder}/.venv/Scripts/skill-scan.exe` written out as an absolute path.

## Install

Pick one:

- **From this folder, no packaging:** copy the folder to your extensions folder as `csc580-group9.skill-scan-0.1.0` (`%USERPROFILE%\.vscode\extensions\` on Windows, `~/.vscode/extensions/` elsewhere) and reload VS Code.
- **As a .vsix:** `npx @vscode/vsce package` in this folder, then `code --install-extension skill-scan-0.1.0.vsix`.
- **To try it without installing:** open this folder in VS Code and press F5 (Run Extension). In the window that opens, open the repository and then `examples/skill-scan/risky-installer/SKILL.md`.

## Commands and settings

| Command | What it does |
|---|---|
| Skill Scan: Scan the skill of the current file | Scans the skill that holds the active file |
| Skill Scan: Scan every skill in the workspace | Scans each workspace folder |
| Skill Scan: Clear findings | Removes the diagnostics |

| Setting | Default | Meaning |
|---|---|---|
| `skillScan.command` | `skill-scan` | The command to run |
| `skillScan.rulesPath` | empty | Rule file; empty uses the command's default |
| `skillScan.cutoff` | empty | High-risk severity cutoff; empty uses the rule file's 6 |
| `skillScan.runOnOpen` / `skillScan.runOnSave` | on | When to scan |
| `skillScan.showContext` | on | Show context matches as information |

## Tests

```bash
npm test     # node --test on lib/findings.js, against a report the real command wrote
```

`test/fixtures/report.json` is the command's JSON output for `examples/skill-scan`. `tests/test_skill_scan.py` fails if the command's output and this fixture drift apart; regenerate it with `skill-scan examples/skill-scan --format json --output tools/vscode-skill-scan/test/fixtures/report.json` from the repository root.

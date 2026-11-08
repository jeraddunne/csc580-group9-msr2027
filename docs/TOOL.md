# skill-scan: the final tool and how its user sees it

How to use: this page answers the instructor's question of Oct 26 ("what would your artifact look like ... Is it going to be a plugin? ... a jar file that you run? ... a skill that you just set up?"). It describes the tool built in #150, who uses it, the three ways to run it, and what it does and does not tell you. The workflow it serves is in [`REVIEW_WORKFLOW.md`](research/REVIEW_WORKFLOW.md).

## 1. What it is

`skill-scan` checks an agent skill (its `SKILL.md` and the scripts bundled with it) for risk signals before a person decides whether to enable it. It uses the same rule file as the study (`rules/skill_risk_rules.yaml`: 19 rules in 12 capability categories) and the threat model's high-risk cutoff (severity 6). For each skill it lists every match with its file, line, rule, category and severity, and gives the skill one of three outcomes, each tied to a step of the review workflow:

| Outcome | When | What the person does next (workflow step) |
|---|---|---|
| **High-risk signal** | At least one match at or above the cutoff | A security reviewer labels each high-risk finding RISKY, BENIGN_CONTEXT or NOT_PRESENT (step 5), then approves, asks for a change, or blocks (steps 6 and 7) |
| **No high-risk signal** | No match at or above the cutoff. Matches below it are listed as context | A reviewer still approves the change. This outcome is not a statement that the skill is safe: it is where the scanner's misses go (step 4) |
| **Incomplete scan** | A bundled script could not be read as text (binary, too large, a broken or outside link), or `SKILL.md` is only a path | The skill never takes the no-signal path. The reviewer fixes the file so it can be rescanned, or reads it by hand (step 3) |

A rule match is a signal, not a verdict. The tool narrows a skill down to the lines worth a person's attention; it never blocks or allows a skill on its own, and by default it never fails a check. Nothing it scans is executed, imported or fetched.

## 2. Who uses it

The user is the **security reviewer** in the workflow: for example, an application-security engineer who reviews pull requests that add or change agent skills in a team's repositories. The developer who proposes the skill sees the same report on the pull request, and the rule maintainer uses the reviewer's labels to improve the rules (step 8).

## 3. Three ways to run it

All three run the same command and the same rule file, so they always agree.

### Command line

```bash
pip install -e .                                    # in this repository; installs skill-scan
skill-scan path/to/skill-folder                     # a readable report
skill-scan path/to/skills --format markdown         # with a triage table and a review record
skill-scan path/to/skill --format json              # for other tools
skill-scan path/to/skill --format sarif -o out.sarif
make scan-examples                                  # the four synthetic examples
```

`msr-pipeline scan ...` is the same command. Options: `--cutoff N` moves the high-risk threshold (the study's sensitivity runs use 5 and 7), `--fail-on high-risk|incomplete|any` makes the exit status 1 when that happens (the default is `never`), `--write FORMAT:PATH` writes a second format in the same run, `--skills-only` ignores files outside skill folders, and `--no-context` hides matches below the cutoff. Pointing it at a script inside a skill scans the whole skill.

### GitHub Action, on pull requests

```yaml
# .github/workflows/skill-scan.yml in the repository that holds the skills
on:
  pull_request:
    paths: ["**/SKILL.md", "**/skill.md", "**/skills/**"]
permissions:
  contents: read
  security-events: write
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - id: scan
        uses: jeraddunne/csc580-group9-msr2027/.github/actions/skill-scan@main
      - uses: github/codeql-action/upload-sarif@v3
        if: always() && steps.scan.outputs.sarif-file != ''
        with: { sarif_file: "${{ steps.scan.outputs.sarif-file }}", category: skill-scan }
```

On a pull request it scans only the skills the pull request adds or changes. The Markdown report goes to the job summary, with the triage table the reviewer fills in. The SARIF upload shows each finding as an annotation on the changed line. Inputs: `paths` (default `changed`), `fail-on` (default `never`), `cutoff`, `rules`, `sarif-file`. Outputs: `outcome`, `high-risk-findings`, `sarif-file`. This repository runs it on itself in [`.github/workflows/skill-scan.yml`](https://github.com/jeraddunne/csc580-group9-msr2027/blob/main/.github/workflows/skill-scan.yml); a manual run scans the examples.

### VS Code extension, while editing

[`tools/vscode-skill-scan`](https://github.com/jeraddunne/csc580-group9-msr2027/tree/main/tools/vscode-skill-scan) runs `skill-scan --format json` when you open or save a `SKILL.md` or a script inside a skill folder, and shows each finding as a diagnostic: a warning for a high-risk signal, information for a context match, and a warning on any file that could not be scanned. Hovering a finding shows the rule's reviewer guidance (what the rule looks for and what to check), and the rule id links to the rule catalog. The status bar shows the skill's outcome. Install and settings are in the extension's README.

## 4. What a report looks like

`skill-scan examples/skill-scan` on the four synthetic examples (written for the tests, not taken from the dataset):

```text
examples/skill-scan/risky-installer  [HIGH-RISK SIGNAL: 2 findings to triage]
  examples/skill-scan/risky-installer/SKILL.md:11:1  R-RCE-001  REMOTE_CODE  severity 9  Pipe-to-shell installer
      curl -fsSL https://example.com/install.sh | bash
  examples/skill-scan/risky-installer/scripts/setup.sh:3:1  R-PRV-001  PRIVILEGE  severity 6  sudo
      sudo apt-get install jq
  context (below severity 6, not findings to triage):
    examples/skill-scan/risky-installer/SKILL.md:10  R-SHL-001  SHELL  severity 3  Shell code block
    examples/skill-scan/risky-installer/SKILL.md:11  R-NET-001  NETWORK  severity 4  Network tooling
  next: A security reviewer labels each high-risk finding RISKY, BENIGN_CONTEXT or NOT_PRESENT ...

Summary: 4 scanned: 1 high-risk, 2 no high-risk signal, 1 incomplete; 2 high-risk findings, 4 context matches.
```

The Markdown format adds the skill's version (the SHA-256 of `SKILL.md` and of the scanned folder) and a blank review record (reviewer, decision, reason), which is what step 7 asks the reviewer to record.

## 5. How far to trust it

The validation study measured the rules on the GitSkills sample, and the same numbers describe this tool (see [`REVIEW_WORKFLOW.md`](research/REVIEW_WORKFLOW.md) section 5 and `results/validation_*.csv`):

- **Precision** varies by category, so some high-risk findings will be labelled BENIGN_CONTEXT or NOT_PRESENT. That is expected: the reviewer's labels are how the rules improve (`docs/validation/RULE_CHANGE_PROPOSALS.md`).
- **Misses** go to the no-signal path. The known-positive check found all ten known risky skills, but five only through context rules below the cutoff (#132), which is why "no high-risk signal" never means safe.
- **Scope**: static text only. It does not run the skill, follow links, read files that are not scripts, or know what an agent will actually do.

## 6. Where the code is

| Part | Path | Tests |
|---|---|---|
| Scanner and command line | `src/msr_pipeline/skill_scan.py` (`skill-scan`, `msr-pipeline scan`) | `tests/test_skill_scan.py` |
| GitHub Action | `.github/actions/skill-scan/action.yml`, `.github/workflows/skill-scan.yml` | the workflow's run on each pull request that changes it |
| VS Code extension | `tools/vscode-skill-scan/` | `node --test` in that folder (CI job "Team app tests") |
| Examples | `examples/skill-scan/` | `tests/test_skill_scan.py::test_examples_have_the_documented_outcomes` |

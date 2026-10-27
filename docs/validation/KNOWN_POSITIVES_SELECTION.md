# Known-positive skill selection — Issue #97

## Status and responsibilities

- Status: Leticia Aderhold completed full-document review of the original ten candidates on 2026-10-21. Two candidates were replaced on 2026-10-23; Leticia reviewed the source documents in DB Browser for SQLite, as recorded in ai-use-log.md. The revised selection contains ten candidates. Jerad Dunne ran the scanner check on 2026-10-27 with `make ground-truth` on commit 8e2ce36; the results are under Results below. Teammate review of the results remains pending.

## Selection method

The source is the supplied `agent_skills_sample.db`, using the
`artifacts` table and records whose filename is SKILL.md
(case-insensitive).

The original candidates were located using capability-related searches and reviewed in context against docs/research/THREAT_MODEL.md. The exact original search terms and SQL queries were not retained and cannot be verified. This creates a selection-bias limitation: the original searches may have favored wording detectable by the scanner. Full-document review confirms the cited capabilities but does not remove that bias. The two replacements selected on 2026-10-23 were found through ordered document reading without command-keyword filtering, as described below.

Codex assisted with database inspection, candidate identification,
and this draft. Scanner rule patterns, rules' `examples.match`
strings, and scanner results were not consulted.

This is a purposive capability sample, not a random sample or a
prevalence estimate. Legitimate maintenance actions can contain the
capabilities listed below; inclusion does not mean a skill is malicious.

The expected category column records a specific capability to check.
It is not an exhaustive annotation of every category in each skill.
Additional scanner categories must be reviewed separately.

On 2026-10-23, two candidates were replaced. One replacement addressed a validation-sample overlap; the other added a second candidate selected through ordered document reading. Sixteen stored SKILL.md documents were reviewed in repository-name and path order, without filtering their content for command keywords. Both replacements declare unscoped Bash tool access. After both replacements, the selection contained ten candidates, and the overlap check reported that no candidate is in a validation sample. No skill commands or scanner detection runs were executed during this review.

## Record identifiers

Candidate IDs are the first 16 hexadecimal characters of:

SHA-256(repo_full_name + newline + path)

The values come from the database exactly as stored. Repository names
are omitted from this document. Jerad can reproduce the identifiers
locally to retrieve the corresponding records.

Line numbers refer to the stored content split into lines.

## Candidates and expected capabilities

| ID | Skill path | Expected category | Evidence and rationale |
|---|---|---|---|
| f699537c00478727 | `.claude/skills/hyperframes-registry/SKILL.md` | NETWORK | Line 99 uses curl to retrieve the remote registry manifest. This enables outbound network access. |
| 46aa89b2bc8739e4 | `.claude/skills/managing-credentials/SKILL.md` | CREDENTIALS | Lines 51 and 69 retrieve and store provider credentials through the credential-management library. |
| 04a39183afa5b330 | `agent-skills/skills/launchd-cron-installer/SKILL.md` | PERSISTENCE | Lines 59–60 create a LaunchAgents plist and load the job with launchctl. Line 14 states that the arrangement survives reboots. |
| cb461d437eb8c5c0 | `skills/k5rs4n/api-cost-tracker/SKILL.md` | PERSISTENCE | Lines 209–210 instruct adding a recurring crontab entry that runs the budget check every six hours. |
| e7bc62332ad87df6 | `internal/skills/defaults/docx/SKILL.md` | PRIVILEGE | Lines 195, 197, and 198 install dependencies using sudo. This invokes elevated permissions for installation. |
| f12dc9a8c0ca8d37 | `skills/find-replace/SKILL.md` | TOOL_GRANT | Line 6 declares allowed-tools: "Bash" without a command restriction. This requests broad shell permission; actual enforcement depends on the host agent. The documented file replacements do not alone establish destructive behavior or malicious intent. |
| 99552d3ddeb0ce04 | `skills/eric-e2e-testing/SKILL.md` | DESTRUCTIVE | Line 29 recursively removes package-cache files using rm -rf. This is scoped container cleanup, but it still provides deletion capability. |
| 4bcf122319412600 | `skills/jeremylongshore/claude-code-plugins-plus-skills/attio-debug-bundle/SKILL.md` | CREDENTIALS | Lines 47–59 read ATTIO_API_KEY and use it in an Authorization header. |
| 0ecf482604f02042 | `SKILL.md` | TOOL_GRANT | Front matter lines 8–10 declare allowed-tools and include Bash without a command restriction. This requests broad shell permission; actual permission enforcement depends on the host agent. It does not establish malicious intent or execution. |
| e7d2878c01a255b3 | `.claude/skills/building-vulnerability-dashboard-with-defectdojo/SKILL.md` | NETWORK | Lines 140–150 upload a scan file to the configured DefectDojo API with curl. This is network transfer; it is not automatically EXFIL_ENDPOINT. |

## Source-excerpt review record

On 2026-10-20, Leticia Aderhold reviewed source passages presented in ChatGPT for all ten candidates and confirmed their proposed categories. The review covered the cited capability passages, not the complete skill documents. No commands from the skills were executed, and no scanner results were consulted.

## Full-document review record

On 2026-10-21, Leticia Aderhold reviewed the complete stored SKILL.md text for all ten candidates in DB Browser for SQLite and retained the listed expected categories without changes. Codex assisted with navigation and interpretation of the source evidence. The categories describe capabilities and do not establish malicious intent. No commands from the skills were executed, and no scanner results were consulted.

## Review before scanning

- [x] Leticia reviews each candidate's source text and expected capability.
- [x] Any selection changes are recorded before scanning.
- [x] The selection and expected categories are committed before scanning.
- [x] AI assistance is recorded in ai-use-log.md.
- [x] Validation-sample overlap check confirms zero overlap for the revised ten-candidate selection.
- [x] Jerad retrieves the selected records using the documented IDs.
- [x] Jerad runs the scanner using a committed, reproducible command.
- [x] A results CSV records expected categories, reported categories, hits, and misses.
- [x] Misses are documented in docs/validation/RULE_CHANGE_PROPOSALS.md or a new issue. No candidate was missed; the five detected only below the high-risk cutoff are tracked in #132.

## Results (2026-10-27)

Command: `make ground-truth` (`python scripts/ground_truth_check.py`) on commit 8e2ce36. Outputs: `results/ground_truth_check.csv` (one row per candidate) and `results/ground_truth_summary.csv` (one row per expected category, plus a total).

All ten candidates were found in the sample by their IDs, and for each one a rule of the expected category matched the SKILL.md text: 10 detected, 0 missed. Five were detected at high risk, meaning a matching rule of that category has severity 6 or more: both PERSISTENCE candidates, the PRIVILEGE and DESTRUCTIVE candidates, and one of the two TOOL_GRANT candidates. The other five matched only context rules below severity 6: both CREDENTIALS candidates (`R-CRD-002`, severity 5), both NETWORK candidates (`R-NET-001`, severity 4), and one TOOL_GRANT candidate (`R-TGR-002`, severity 1). In the review workflow (`docs/research/REVIEW_WORKFLOW.md`, step 4), those five would take the "no high-risk signal" path: their matches appear only in the context section of the scan report, and no finding would be triaged. Two candidates have bundled scripts; one candidate's scripts matched CREDENTIALS and NETWORK rules, and no category was reported for the other's.

What these five mean for the rules or for the severity cutoff is not decided here; it is tracked in #132.

| Expected category | Candidates | Detected | Detected at high risk | Missed |
|---|---:|---:|---:|---:|
| CREDENTIALS | 2 | 2 | 0 | 0 |
| DESTRUCTIVE | 1 | 1 | 1 | 0 |
| NETWORK | 2 | 2 | 0 | 0 |
| PERSISTENCE | 2 | 2 | 2 | 0 |
| PRIVILEGE | 1 | 1 | 1 | 0 |
| TOOL_GRANT | 2 | 2 | 1 | 0 |
| Total | 10 | 10 | 5 | 0 |

| ID | Expected category | Rules of that category that matched SKILL.md (severity) | Detected at high risk | Bundled scripts scanned | Categories in bundled scripts |
|---|---|---|---|---|---|
| f699537c00478727 | NETWORK | `R-NET-001` (4) | no | 0 | - |
| 46aa89b2bc8739e4 | CREDENTIALS | `R-CRD-002` (5) | no | 0 | - |
| 04a39183afa5b330 | PERSISTENCE | `R-PER-001` (7) | yes | 4 | - |
| cb461d437eb8c5c0 | PERSISTENCE | `R-PER-001` (7) | yes | 0 | - |
| e7bc62332ad87df6 | PRIVILEGE | `R-PRV-001` (6) | yes | 0 | - |
| f12dc9a8c0ca8d37 | TOOL_GRANT | `R-TGR-001` (6), `R-TGR-002` (1) | yes | 0 | - |
| 99552d3ddeb0ce04 | DESTRUCTIVE | `R-DST-001` (6) | yes | 0 | - |
| 4bcf122319412600 | CREDENTIALS | `R-CRD-002` (5) | no | 0 | - |
| 0ecf482604f02042 | TOOL_GRANT | `R-TGR-002` (1) | no | 0 | - |
| e7d2878c01a255b3 | NETWORK | `R-NET-001` (4) | no | 2 | CREDENTIALS; NETWORK |

## Limitations

The ten candidates cover six capability categories. They do not cover
every threat-model category and cannot establish overall scanner recall.

The expected categories have been confirmed by Leticia's full-document review for this targeted capability check. The comparison with scanner results is under Results; teammate review of it is pending.

"Detected" means a rule of the expected category matched somewhere in the SKILL.md text. The check does not confirm that the match is on the lines cited in the candidates table.

The selection-bias limitation under Selection method applies to the detection count: candidates found through capability-related searches may favour wording the rules match, so 10 of 10 detected may be optimistic.
Issue #97 remains open until scanning, scoring, review, and the other
acceptance criteria are complete.

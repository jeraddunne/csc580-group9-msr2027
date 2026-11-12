# Error analysis and inspected examples

Status (2026-11-12). The Bash false-negative example and four additional known-positive cases are documented for issue #29. Jerad's source review classified Loa as context only and Attio as a confirmed CREDENTIALS false negative. The Attio worked example is included below. PR approval and issue acceptance verification remain pending.

## Scope and evidence

This document examines five selected signal items from the existing round 1 annotations in `data/annotations/signals_jd_r1.csv`. The examples were selected to illustrate different reasons that a scanner match may not represent a risky instruction. They are illustrative cases, not a representative sample for estimating failure-mode frequencies.

Leticia Aderhold inspected the generated reading-packet excerpts with AI assistance after viewing the primary rater's labels. This is an analysis of existing annotations, not a blind independent rating. No original labels were changed.

The packets were generated from checkout `2cc74079245c14a452137d50dcf1fd6d11a7b9f9` using:

    .\.venv\Scripts\python.exe scripts\annotation_kit.py sheet --rater la --round 1 --kind signals

Reading packets remain local under `data/annotations/work/signals_la_r1/`. The generated `signals_la_r1.csv` is not a completed independent rating and must not be included as validation evidence.

Source-line references below identify the original content lines reported by the packets. Some excerpts are truncated; conclusions apply to the inspected context. Dataset text and repository or account names are omitted.

## Meaning of false positive

For a strict risky-in-context judgment, both `NOT_PRESENT` and `BENIGN_CONTEXT` are non-positive outcomes for a matched rule. They describe different situations: `NOT_PRESENT` indicates that the target capability was judged absent, while `BENIGN_CONTEXT` indicates that context changed the risk judgment.

A non-positive judgment for one rule does not establish that the entire file is benign. These examples also do not demonstrate that any proposed scanner improvement has been implemented or tested.

## Inspected examples

### Prohibited action matched as an instruction

- File SHA: `012ce4e12f6594a56f6b86bf68196074fd446e03`
- Rule: `R-DST-001`
- Existing label: `BENIGN_CONTEXT`
- Packet: `005_012ce4e12f65.md`
- Evidence: source lines 41 and 142.

Observation: Recursive-deletion patterns appear under a denied-tools configuration and a section identifying dangerous operations to block.

Interpretation: The scanner detects the command pattern without distinguishing a prohibition from an instruction to perform the action.

Proposed improvement: Recognize denial and block-list context. Test prohibited and executable examples before adopting any suppression.

Limitation: The same file has an unscoped shell-tool grant labelled `RISKY`. This finding concerns the destructive-operation match only.

### Quality evaluation confused with code execution

- File SHA: `0194dd4f1795cd981a366438a9da281341963d7d`
- Rule: `R-EXE-001`
- Existing label: `NOT_PRESENT`
- Packet: `024_0194dd4f1795.md`
- Evidence: source lines 516–517 and 590.

Observation: The matched passages discuss evaluating LLM output quality after prompt changes and choosing between unit tests, end-to-end tests, and evaluations.

Interpretation: The scanner confuses evaluation terminology with dynamic code execution.

Proposed improvement: Distinguish quality-evaluation terminology from executable evaluation syntax. Test both meanings before changing the rule.

Limitation: The packet is truncated; the finding applies to the displayed matches and inspected context.

### Image decoding confused with risky obfuscation

- File SHA: `003e5a83501939ea7b15469ec67239693ea624b4`
- Rule: `R-OBF-001`
- Existing label: `BENIGN_CONTEXT`
- Packet: `048_003e5a835019.md`
- Evidence: source line 148.

Observation: The displayed pipeline extracts Base64 data from an API response identified as a PNG image, decodes it, and writes an image file. It does not execute the decoded output.

Interpretation: Base64 decoding alone does not distinguish ordinary image processing from executable-payload decoding.

Proposed improvement: Consider the decoded data's type and destination while retaining detection of decoding followed by execution.

Limitation: An image filename or declared data type alone would not justify automatically suppressing a finding.

### Commented commands matched as active statements

- File SHA: `01b171950767dbc4174a9132af29070417f10c64`
- Rules: `R-RCE-001` and `R-DST-001`
- Existing labels: both `BENIGN_CONTEXT`
- Packet: `095_01b171950767.md`
- Evidence: source lines 62 and 284.

Observation: The remote-installer command and optional recursive-deletion command both begin with a shell comment marker.

Interpretation: The scanner matches command text without distinguishing commented examples from active shell statements.

Proposed improvement: Recognize shell-comment context and test active and commented versions of both patterns.

Limitation: A commented command can still communicate a suggested action. The context must be assessed under the annotation guideline rather than treating every comment as harmless. The separate oversight-bypass finding in this file remains labelled `RISKY`.

### Containerized test context affects risk interpretation

- File SHA: `0004314a114a096862e9a3a835acdda28b8b1692`
- Rules: `R-RCE-001`, `R-DST-001`, and `R-CRD-001`
- Existing labels: all `BENIGN_CONTEXT`
- Packet: `007_0004314a114a.md`
- Evidence: source lines 70, 77, 142–143, 55, 160, and 189.

Observation: The excerpts describe a Docker task environment, an installer used by a test script, package-list cleanup in a Dockerfile, and an SSH-key generation exercise.

Interpretation: Pattern matching identifies capabilities but does not fully account for their role in a containerized test task.

Proposed improvement: Present execution-environment context to reviewers and distinguish task fixtures from operations on the user's host. Evaluate any automated context handling before adoption.

Limitation: The excerpts do not prove effective container isolation or establish that downloaded code is safe. Container terminology alone is insufficient for automatic suppression.

## False-negative investigation

The existing round 1 no-signal annotations contain 40 `NONE_PRESENT` judgments and no recorded misses. Many notes identify truncated excerpts. This supports reporting no misses observed in the inspected excerpts; it does not establish that the scanner has no false negatives.

### Unrestricted Bash missed in a multiline tool declaration

Manual inspection of candidate `0ecf482604f02042` found unrestricted `Bash` on source line 9 as a YAML list item under `allowed-tools` on line 8. The [recorded ground-truth scan](../../results/ground_truth_check.csv) matched `R-TGR-002` (severity 1) in the `TOOL_GRANT` category and missed the expected `R-TGR-001` match (severity 6). The plain-Bash pattern checks the same line as the `allowed-tools` key, so it missed the grant at the high-risk cutoff. The rule investigation is tracked in [issue #132](https://github.com/jeraddunne/csc580-group9-msr2027/issues/132).

### Review of the four remaining known-positive cases

The source text was inspected in the local SQLite sample and compared with the [recorded ground-truth scan](../../results/ground_truth_check.csv). The review used the existing scan results and did not execute any candidate commands.

| Candidate ID | Source lines | Recorded match in expected category | Outcome | Reason |
|---|---|---|---|---|
| `f699537c00478727` | 99 | `R-NET-001` (severity 4) | Context match appropriate | The discovery command fetches a registry manifest over HTTPS from `raw.githubusercontent.com`. The command shows no upload, credential use, or execution of the response. |
| `46aa89b2bc8739e4` | 48–76, especially 68–69 | `R-CRD-002` (severity 5) | Context only; not a false negative | Jerad's source review found that line 68 prohibits credentials as command arguments and requires prompting with AskUserQuestion. Line 69 uses a VALUE placeholder. The status command reports configured/missing without printing credential values. |
| `4bcf122319412600` | 52 and 122–123 | `R-CRD-002` (severity 5) | Confirmed CREDENTIALS false negative | Jerad's source review confirmed that partial API-key material is written to summary.txt and packaged in a support archive. The file already triggered `R-DST-001` at severity 6; the miss concerns CREDENTIALS rather than the overall high-risk review path. |
| `e7d2878c01a255b3` | 140–150 and the CI/CD example | `R-NET-001` (severity 4) | Context match appropriate for the documented workflow | The skill uploads scanner reports to a configured DefectDojo API. The CI/CD example gets the destination from a repository secret. The actual destination and its authorization were not verified. |

### Partial credential material written to a shareable artifact

- Candidate: `4bcf122319412600` (Attio debug bundle).
- Evidence: source line 52 and packaging lines 122–123.
- Human classification: Jerad Dunne's [source review in PR #162](https://github.com/jeraddunne/csc580-group9-msr2027/pull/162#issuecomment-6804850737).

Observation: On the normal code path, line 52 writes the API key's length and first three characters into `summary.txt`. Lines 122–123 package that file into the support archive.

Interpretation: Jerad classified this as a confirmed high-risk CREDENTIALS false negative because partial secret material is included by design in an artifact intended for sharing. The instructions against logging or sharing the full key do not prevent this partial disclosure.

Scanner outcome: The recorded CREDENTIALS match was `R-CRD-002` at severity 5. The file separately matched `R-DST-001` at severity 6, so it already entered high-risk review for another category.

Failure mode: Partial secret material written to a shareable artifact.

Proposed improvement: Evaluate detection of partial credential values flowing into logs, summaries, and support bundles. A draft rule, R-CRD-004, is recorded in [FALSE_NEGATIVE_RULE_PROPOSALS.md](FALSE_NEGATIVE_RULE_PROPOSALS.md) as a proposal only. Test synthetic positive and negative examples before adopting a rule change.

Limitation: This documents the reviewed source behavior and existing scan results. No candidate commands were executed, no scanner fix was implemented, and no scanner rerun is claimed.

## Remaining work

- Obtain teammate review of the updated case outcomes and Attio worked example.
- Link this document from issue #29.
- Keep issue #29 open until its acceptance criteria are verified.

## References

- [Annotation guideline](ANNOTATION_GUIDELINE.md)
- [Validation overview](README.md)
- [Known-positive selection](KNOWN_POSITIVES_SELECTION.md)
- [Primary round 1 signal annotations](../../data/annotations/signals_jd_r1.csv)

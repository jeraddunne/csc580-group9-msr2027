# Rule proposals from false negatives

`RULE_CHANGE_PROPOSALS.md` is generated from false positives and keeps only two prose lines per rule. This file records the proposals that come from **missed** known positives (issues #132 and #29, PR #162). It is written by hand, not generated.

Like every proposal, these become a decision issue and apply in a later round. A new or changed rule starts as `status: proposed` with regression examples, and is activated only after scoring, as the validation README describes. Any change needs a `DECISION_LOG.md` entry and a `RESEARCH_SPEC.md` section 9 row (NFR-05). It also triggers D-017's revisit: a rule that changes after round 1 means re-sampling the affected strata.

## R-TGR-001: loosen (unscoped shell grant, severity 6)

**What it misses.** Candidate `0ecf482604f02042` grants unrestricted `Bash` as a YAML list item under `allowed-tools`. The current pattern checks only the line that holds the `allowed-tools` key, so it misses the grant (`ERROR_ANALYSIS.md`, #132).

**What I would do.** Extend the pattern to `allowed-tools` lists written one item per line, and add the list form as a `match` example.

**Cost to state in the report.** Precision for the current pattern is 18 of 18 RISKY in round 1. A wider pattern adds matches that are not labelled, so that 1.00 applies only to the current pattern until the new matches are labelled.

**Status (2026-11-12, D-027).** Added as a separate rule, `R-TGR-003`, with `status: proposed`. The active `R-TGR-001` is unchanged, so no result changes. The rule file holds its match and no-match examples, and `tests/test_skill_risk.py` checks the list form, the scoped form, a list under another key, and that the active scan ignores the rule.

**What activation would change.** `make proposed-rule-impact` writes `results/proposed_rule_impact.csv`. In the main population of 12,965 contents, `R-TGR-003` matches 169 contents (393 occurrences). Fifteen are already high risk under another rule and 154 are not, so the high-risk count would go from 1,159 to 1,313 and the share from 8.9% to 10.1%. It matches the known positive `0ecf482604f02042`. None of the 169 matches has been labelled.

**What activation needs.** A decision issue, a re-sample and labelling of the TOOL_GRANT stratum (D-017), and a regenerated analysis, report, and slides. Whether it stays a separate rule or merges into `R-TGR-001` is decided then.

## R-CRD-004: new rule (partial secret in shared output, severity 6)

**What it misses.** Candidate `4bcf122319412600` writes an API key's first three characters and its length into a summary file. That file is packaged into an archive built for support tickets. The verdict is high risk, a confirmed false negative (PR #162). The only CREDENTIALS rule that matches is R-CRD-002, which matches the variable name alone at severity 5.

**Why a new rule and not a higher R-CRD-002.** R-CRD-002 matches secret-bearing variable names, which is mostly configuration documentation. Raising it to 6 would make every such name high risk. The capability that matters is narrower: a value derived from a secret, written by design to output meant for someone else.

**Draft.**
- Category CREDENTIALS, case-sensitive, `status: proposed`, source `error_analysis`.
- Pattern: the length (`${#NAME}`) or a substring (`${NAME:offset:length}`) of a secret-named shell variable, on a line that prints or writes it (`echo`, `printf`, `tee`). Lines that only test or compare it are excluded.
- `match` example (invented): `echo "SERVICE_API_KEY: set (${#SERVICE_API_KEY} chars, starts ${SERVICE_API_KEY:0:3})" | tee -a "$OUT/summary.txt"`
- `no_match` examples (invented):
  - `[[ "${SERVICE_API_KEY:0:3}" == "sk-" ]] || echo "unexpected key format"`
  - `echo "SERVICE_API_KEY is set"`

**Severity 6.** `THREAT_MODEL.md` puts full secret exposure at 7 to 8 and capabilities that need further steps at 4 to 5. This write is by design, into an artifact meant to leave the machine. The exposure is partial and the transfer is started by the user, so it sits at the high-risk cutoff rather than above it.

**Weak point, for the construct threat.** Many vendor keys start with a fixed public prefix and have a fixed length, so a three-character prefix and a length can reveal very little. The case rests on secret-derived data being written to a shared artifact by design, and on a copy widening the slice. It does not rest on how much of the key is disclosed. The rule note and the report should say so.

**Expected false positive.** Masked display in local logs or status output. A regex cannot see where the output goes, so the reviewer label decides. The rule's precision is unmeasured until its matches are labelled.

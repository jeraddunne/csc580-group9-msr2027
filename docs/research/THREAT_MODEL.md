# Threat model for agent skills (P-01)

How to use: this document fixes what "risk-relevant capability" means for the project. The rule file `rules/skill_risk_rules.yaml` implements it, and the report's threat-model section is written from it. Change it only through a pull request that also updates the rule file and records the reason in `docs/workspace/DECISION_LOG.md`.

## 1. What a skill is, in security terms

A skill is a folder with a `SKILL.md` file of natural-language instructions, optionally with scripts and reference files. An agent loads it when it decides a task matches the skill's description. It then follows the instructions using whatever tools and permissions the agent already has. There is no package manager, no signature, and no compiler. Skills spread by people copying folders between repositories and editing them.

So a skill is **copied like code and read like instructions**. The threat model covers both halves.

## 2. Actors

| Actor | Role | Relevant behaviour |
|---|---|---|
| Skill author | Writes the original skill | May include commands, scripts, URLs, and tool grants, intentionally or by habit |
| Copier and editor | Copies the folder into another repository and may edit it | Can add, remove, or change capabilities; copies inherit whatever the source contained |
| Agent runtime | Loads the skill and acts on it | Executes tools (shell, file system, network) with the user's delegated permissions |
| User | Installs or clones the repository and runs the agent | Usually does not read every skill before the agent uses it |
| Third party (hostile author, compromised upstream) | Controls a skill that others copy | Can place instructions or scripts that act against the user |

## 3. Assets

- The user's files, source code, and repositories
- Credentials and secrets on the machine: SSH keys, cloud credentials, tokens, and dotenv files
- The integrity of the machine and development environment (startup files, schedulers, git hooks)
- The integrity of the user's oversight: the expectation that the agent asks before consequential actions

## 4. Trust boundaries

```
 [skill author] --copy--> [copier / editor] --commit--> [repository]
                                                       |
                                                 clone / install
                                                       v
 [user environment: files, keys, network]  <--tools--  [agent runtime] <--loads-- [SKILL.md + scripts]
```

1. **Author to copier.** Content crosses without review tooling. A change made here is inherited by every later copy.
2. **Repository to agent.** Instructions in the skill are treated as guidance for the agent, which blurs data and instructions (Greshake et al., 2023).
3. **Agent to user environment.** The agent's tool permissions turn instructions into actions on the assets above.

## 5. Capability categories, rules, and severities

A capability is something a skill can cause the agent, or a bundled script, to do across boundary 3. Each category maps to rules with a severity from 1 to 10, which is the FMEA severity score. **High risk** means at least one matching rule with severity 6 or more.

| Category | What it enables | Rules (severity) | Rationale for the top severity |
|---|---|---|---|
| REMOTE_CODE | Download and execute code in one step | R-RCE-001 pipe to shell (9), R-RCE-002 PowerShell download and execute (9) | Arbitrary code from a remote source runs with no review step |
| OVERSIGHT_BYPASS | Suppress confirmation or override prior instructions | R-OVR-001 (8) | Removes the user's last line of defence; the indirect prompt-injection pattern |
| EXFIL_ENDPOINT | Send data to request-capture, tunnel, or paste services | R-EXF-001 (8) | Typical destinations for moving data off the machine |
| CREDENTIALS | Read or handle secrets | R-CRD-001 credential file paths (8), R-CRD-002 secret variable names (5), R-CRD-003 dotenv reads (4) | Direct access to key files is severe; variable names are mostly configuration documentation |
| NETWORK | Outbound network access | R-NET-002 hard-coded IP endpoint (7), R-NET-001 network tooling (4) | A raw IP bypasses name-based review; general tooling is common and expected |
| PERSISTENCE | Changes that survive the session | R-PER-001 (7) | Startup files, schedulers, and git hooks keep acting after the agent stops |
| OBFUSCATION | Decode encoded payloads | R-OBF-001 (7) | Hides what will run from a human reader |
| DESTRUCTIVE | Delete, overwrite, or rewrite history | R-DST-001 (6) | Local damage that is hard to undo |
| PRIVILEGE | Elevate or widen permissions | R-PRV-001 sudo (6), R-PRV-002 world-writable (5), R-PRV-003 make executable (3) | Elevation widens every other capability |
| DYNAMIC_EXEC | Evaluate generated or remote code at run time | R-EXE-001 (6) | Behaviour is decided at run time, not visible in the text |
| TOOL_GRANT | Grant broad tools in front matter | R-TGR-001 unscoped shell grant (6), R-TGR-002 any allowed-tools declaration (1) | An unscoped shell grant removes a permission boundary; declaring tools at all usually narrows them |
| SHELL | Run shell commands | R-SHL-001 shell code block (3) | Very common and usually benign; context only |

### Severity scale

| Score | Meaning |
|---|---|
| 9 to 10 | Direct execution of code from outside the machine with no review step |
| 7 to 8 | Data can leave the machine, secrets are exposed, oversight is removed, or effects persist |
| 6 | Local damage, privilege elevation, run-time code evaluation, or a broad permission grant |
| 4 to 5 | A capability that needs further steps before it causes harm |
| 1 to 3 | Context that describes normal development work |

## 6. What a rule match does and does not mean

- A match means the text contains a pattern associated with the capability. It does **not** mean the skill is malicious, and it does not mean the agent will perform the action.
- Many matches are benign in context. A code-review skill may quote `eval(` as an example of what to avoid. A setup skill may legitimately use `sudo`.
- Validation (`docs/validation/`, built by the annotation kit) labels each sampled match as risky in context, benign in context, or not present. Only validated precision is reported as a property of the rules.

## 7. Out of scope

- **Runtime behaviour.** We do not run agents, skills, or scripts. We never execute, import, or fetch anything from the dataset.
- **Intent.** We do not judge whether an author meant harm.
- **Attribution.** We do not name repositories or accounts in outputs, and we do not try to reverse the dataset's anonymised author codes.
- **Vulnerability disclosure.** If something appears actively malicious, work stops on that item and it is raised with the instructor before any further step.
- **Other agent formats** (MCP servers, IDE rules files) and the full 41 GB dataset, unless a later decision record adds them.

## 8. How severities were assigned and will be reviewed

1. **Initial assignment (2026-09-14).** The proposer set severities using the scale above. The inputs were security threat-modeling practice for agent integrations and the capability's position relative to boundary 3.
2. **Sprint 2 review.** After the validation sample is labelled, each rule's precision and each category's severity are reviewed. A severity change needs a pull request with the reason, an updated rule example, and a note in the decision log.
3. **Sensitivity.** Every headline result is also reported at severity cutoffs 5 and 7 (`results/sensitivity_summary.csv`), so conclusions do not rest on one cutoff.
4. **FMEA ranking.** In Sprint 3, severity from this table is combined with occurrence (validated prevalence) and detection (validated recall) into a risk priority ranking of categories.

## References

- K. Greshake et al. "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection." AISec 2023. doi:10.1145/3605764.3623985.
- M. Ohm, H. Plate, A. Sykosch, M. Meier. "Backstabber's Knife Collection: A Review of Open Source Software Supply Chain Attacks." DIMVA 2020.
- G. Destefanis, D. Graziotin, M. Vaccargiu, M. Ortu. "GitSkills: A Dataset of Agent Skills on GitHub." MSR 2027 Mining Challenge. arXiv:2608.10906.

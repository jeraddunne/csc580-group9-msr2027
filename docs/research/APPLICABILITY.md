# Applicability of established static-analysis rules to agent skills

Related issue: #96  
Owner: Leticia Aderhold  
Status: Draft for review

## Purpose and scope

Agent skills combine natural-language instructions in SKILL.md with
optional bundled scripts. This analysis distinguishes tools that can
analyze executable code from approaches that can search instruction text.

The mappings below describe conceptual overlap, not equivalent detection
or measured accuracy. No external analyzer was run for this document.

## Applicability table

| Tool or rule family | SKILL.md text | Bundled scripts | Why and limitations | Project-rule overlap |
|---|---|---|---|---|
| SpotBugs | No direct analysis | Compiled Java bytecode only; not Python or shell scripts | SpotBugs analyzes Java class files. It cannot directly analyze Markdown instructions, Python source, or shell source. Its security-related bug patterns can inform a conceptual comparison where the same operation exists in Java. | Conceptual overlap with R-EXE-001 and R-SHL-001 for execution-related operations; not equivalent detectors. |
| SonarQube / SonarSource security rules and hotspots | No demonstrated semantic analysis of agent instructions | Applicable where the selected product, edition, analyzer, and language support the script | Security hotspots identify security-sensitive code for human review. Product and edition support must be checked before claiming a particular rule is available in Community Edition. A code hotspot does not establish malicious intent. | Execution-related rules can conceptually overlap R-EXE-001 and R-SHL-001; credential-related rules can overlap R-CRD-001 through R-CRD-003. Exact rule availability requires verification. |
| Semgrep | Custom generic-mode text matching is possible; this does not establish understanding of natural-language instructions | Language-aware rules apply to supported script languages | Generic mode can match text patterns in formats without a native parser. Language-aware analysis requires supported source code. Custom rules and their false positives must be validated. | Custom patterns could overlap R-RCE-001, R-RCE-002, R-OVR-001, R-EXE-001, and credential rules. This is potential overlap, not an existing-rule coverage claim. |
| Bandit | No direct Markdown analysis | Python scripts | Bandit parses Python into an abstract syntax tree and checks it with plugins. B307 concerns eval; B602 concerns subprocess execution with shell=True. Code blocks would need separate extraction before Python analysis. | B307, B602, and B605 conceptually overlap R-EXE-001: eval, subprocess calls with shell=True, and shell-starting calls such as os.system. R-SHL-001 is secondary shell-code context, not the primary B602 mapping.|
| ShellCheck | No direct analysis of prose | Supported shell scripts | ShellCheck checks shell code. SC2086 concerns quoting, word splitting, and globbing. SC2115 concerns guarding variables in potentially dangerous deletion paths. It does not flag every deletion or decide whether a cleanup operation is authorized. | SC2115 has partial conceptual overlap with R-DST-001. SC2086 provides shell-safety context but has no direct one-to-one project-rule equivalent. |
| CWE-78: OS Command Injection | Conceptual review only | Applicable as a weakness classification when untrusted input reaches an OS command unsafely | CWE is a taxonomy, not an executable analyzer. A shell command or shell code block alone does not prove command injection. | Related to R-SHL-001 and execution-related rules, but these capability indicators do not establish CWE-78. |
| CWE-95: Eval Injection | Conceptual review only | Relevant when insufficiently controlled input reaches dynamically evaluated code | A call to eval alone does not establish injection; input control and execution context must also be examined. | R-EXE-001; the rule catalog cites CWE-95 for eval and similar calls. |
| CWE-798: Hard-coded Credentials | Relevant only if actual hard-coded credentials appear; a variable name alone is insufficient | Relevant when scripts embed credentials | References to secret variable names, credential paths, or dotenv files do not by themselves establish hard-coded credentials. | Related to R-CRD-001 through R-CRD-003, with substantial differences in what constitutes a finding. |
| Remote code / CWE-494 | Conceptual review of download-and-execute instructions | Relevant to scripts that download and execute code without checking integrity | CWE-494 is a weakness classification, not an analyzer. No equivalent built-in detector has been verified for the tools compared here. Legitimate installers can match; review source, integrity checks, and execution context. | R-RCE-001 and R-RCE-002; catalog references include CWE-494, T1059.004 or T1059.001, and T1105. |
| Privilege / CWE-250 and CWE-732 | Conceptual review of sudo and permission-changing instructions | Relevant where scripts request unnecessary privileges or assign unsafe permissions | No equivalent built-in detector has been verified here. Using sudo or chmod alone does not establish a vulnerability; the required privilege, target resource, and permissions need review. | R-PRV-001 corresponds conceptually to CWE-250; R-PRV-002 to CWE-732 and T1222.002. R-PRV-003 records executable-permission context and cites T1222.002. |
| Exfiltration endpoints / ATT&CK | Endpoint names can be matched as text; intent requires review | Endpoint strings and transfer calls can be inspected, but no equivalent analyzer rule has been verified here | ATT&CK describes techniques rather than providing a code analyzer. A webhook, paste service, or tunnel may have legitimate uses; establish what data is sent, where, and with whose authorization. | R-EXF-001; catalog references are T1567.004, T1567.003, and T1572. R-NET-001 and R-NET-002 provide additional network context rather than proof of exfiltration. |
| TOOL_GRANT / OWASP LLM06:2025 | Review allowed-tools front matter and the scope of granted permissions | Script analysis alone does not establish the agent's tool permissions | No equivalent built-in rule in the compared code analyzers has been established for these skill permissions. OWASP Excessive Agency and platform documentation provide review guidance. An allowed-tools declaration alone is context, not proof of excessive permissions; support varies by agent. | R-TGR-001 identifies unscoped shell grants; R-TGR-002 records the presence of allowed-tools. |
| OVERSIGHT_BYPASS / OWASP LLM01:2025 | Review instructions that override earlier instructions, conceal actions, or suppress confirmation | Script analysis alone does not establish how an agent interprets skill instructions | No equivalent built-in rule in the compared code analyzers has been established for this instruction-level behavior. The catalog cites OWASP Prompt Injection and Greshake et al. (2023). Legitimate CI autonomy settings can match and require contextual review. | R-OVR-001; conceptual correspondence to indirect prompt injection, not evidence that an attack succeeded. |
| Persistence / ATT&CK | Review instructions that modify startup files, scheduled tasks, services, or hooks | Scripts can contain persistence-related commands, but no equivalent built-in analyzer rule has been verified here | ATT&CK supplies technique descriptions rather than an executable code analyzer. Legitimate setup operations can match. The catalog identifies git-hook persistence as a project-specific addition without an established reference. | R-PER-001; catalog references T1053.003, T1546.004, T1543.002, T1543.001, and T1547.001. |
| Obfuscation / ATT&CK | Review decoding commands and encoded content in context | Scripts can contain decoding operations, but no equivalent built-in analyzer rule has been verified here | ATT&CK T1027 and T1140 provide conceptual references. Decoding alone does not establish malicious intent; image and certificate handling are known false positives. | R-OBF-001; correspondence to encoded or obfuscated content and decoding before use. |

## SpotBugs limitation

SpotBugs analyzes Java bytecode. It cannot run directly on SKILL.md,
Python scripts, or shell scripts. Executing it on the Markdown file is
therefore not an appropriate comparison.

Execution and credential-handling concepts can still be compared with
security-related Java bug patterns, but conceptual similarity is not
evidence that SpotBugs detects the project's skill-text indicators.

## Interpretation

The project scanner records textual capability indicators across skill
instructions and available script content. Established code analyzers
can provide more language-specific checks for supported scripts.

These approaches answer different questions. A capability match does
not prove a vulnerability, malicious intent, or execution. A code
analyzer's absence of findings does not establish that natural-language
instructions are safe.

Markdown code-block extraction, if used later, must preserve source
identifiers and line mappings. Unsupported languages, missing script
content, parse failures, and skipped files must be reported separately.

## Optional empirical comparison

No empirical comparison has been performed.

If the team performs the optional comparison with Jerad Dunne:

1. Select an analyzer appropriate to the available script language.
2. Record its version, configuration, rule set, and sample snapshot.
3. Analyze source statically without executing dataset scripts.
4. Commit the command that generates the comparison CSV in results/.
5. Report analyzed files, skipped files, errors, and finding counts.
6. Review overlapping findings in context; raw counts alone do not
   establish which scanner is more accurate.

## SonarQube edition and language verification

On 2026-10-21, Leticia Aderhold checked the official SonarQube Community Build supported-language table and Python documentation.

- Python analysis is supported in Community Build.
- Shell and PowerShell are listed without support checkmarks in the Community Build column; their support is shown under Cloud and Server.
- This comparison therefore treats Community Build as applicable to bundled Python scripts, without claiming built-in Shell or PowerShell analysis.
- These pages do not establish semantic analysis of natural-language SKILL.md instructions or verify availability of every security rule mentioned above.
- This was a documentation review; no SonarQube analysis was run.

Sources:
- https://docs.sonarsource.com/sonarqube-community-build/analyzing-source-code/languages/overview
- https://docs.sonarsource.com/sonarqube-community-build/analyzing-source-code/languages/python
  
## References

- SpotBugs introduction:
  https://spotbugs.readthedocs.io/en/stable/introduction.html
- SonarSource security hotspot documentation:
  https://docs.sonarsource.com/sonarqube-server/2025.5/user-guide/security-hotspots
- Semgrep rule syntax and generic matching:
  https://semgrep.dev/docs/writing-rules/rule-ideas
- Bandit overview:
  https://bandit.readthedocs.io/en/1.8.5/index.html
- Bandit B602:
  https://bandit.readthedocs.io/en/1.4.0/plugins/subprocess_popen_with_shell_equals_true.html
- ShellCheck SC2086:
  https://www.shellcheck.net/wiki/SC2086
- ShellCheck SC2115:
  https://www.shellcheck.net/wiki/SC2115
- CWE-78:
  https://cwe.mitre.org/data/definitions/78.html
- CWE-95: https://cwe.mitre.org/data/definitions/95.html
- CWE-798:
  https://cwe.mitre.org/data/definitions/798.html
- Project rule catalog: [Rule cards and their references](RULE_CATALOG.md), reviewed for remote-code, privilege, and exfiltration mappings on 2026-10-22.
- Additional category mappings: [Rule catalog](RULE_CATALOG.md), cards R-TGR-001, R-TGR-002, R-OVR-001, R-PER-001, and R-OBF-001, including their linked OWASP, platform, research, and ATT&CK references.
  
## Review and completion checklist

- [x] Check project-rule mappings against the current rule cards in #95.
- [x] Reconcile CWE references with those used in #95.
- [x] Verify relevant SonarQube edition and language support.
- [x] Record AI assistance in ai-use-log.md in this PR.
- [x] Link this document from Sprint 2 instructor feedback and review.
- [ ] Obtain an approving review from another member.
- [x] Confirm required CI checks pass before merging.

# skill-scan examples

Synthetic skills written for the `skill-scan` tests and the demo (#150). None of them comes from the GitSkills dataset, and none of the commands in them should be run. Each one shows one outcome of the review workflow (`docs/research/REVIEW_WORKFLOW.md`):

| Folder | Expected outcome | Why |
|---|---|---|
| `risky-installer/` | High-risk signal | A pipe-to-shell installer in SKILL.md and `sudo` in a bundled script |
| `context-only/` | No high-risk signal, with context matches | A shell code block and an ordinary API call, both below severity 6 |
| `no-match/` | No high-risk signal, nothing matched | Plain writing instructions |
| `incomplete-scan/` | Incomplete scan | A bundled script that holds binary content, so it cannot be scanned as text |

```bash
skill-scan examples/skill-scan
```

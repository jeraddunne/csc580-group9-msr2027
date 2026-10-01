#!/usr/bin/env python
"""Export the risk rules for the team app's rule tester (app/data/rules.json).

The app runs in the browser and cannot read YAML, so this writes the active rules with
their patterns, flags, examples, and notes as JSON. tests/test_app_data.py fails when the
committed JSON is out of date with rules/skill_risk_rules.yaml.

Usage:
    python scripts/export_app_data.py          # write app/data/rules.json
    python scripts/export_app_data.py --check  # exit 1 if it is out of date
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from msr_pipeline.skill_risk import HIGH_RISK_SEVERITY, read_rule_file  # noqa: E402

OUT = ROOT / "app" / "data" / "rules.json"


def export() -> str:
    data = read_rule_file(ROOT / "rules" / "skill_risk_rules.yaml")
    rules = []
    for raw in data.get("rules") or []:
        if str(raw.get("status", "active")) != "active":
            continue
        examples = raw.get("examples") or {}
        rules.append(
            {
                "id": str(raw["id"]),
                "category": str(raw["category"]),
                "severity": int(raw["severity"]),
                "patterns": [str(p) for p in raw["patterns"]],
                # Python compiles with MULTILINE and, unless case_sensitive, IGNORECASE.
                "flags": "m" if raw.get("case_sensitive") else "mi",
                "match": [str(x) for x in examples.get("match") or []],
                "no_match": [str(x) for x in examples.get("no_match") or []],
                "note": str(raw.get("note", "")),
            }
        )
    payload = {
        "source": "rules/skill_risk_rules.yaml",
        "high_risk_severity": int(data.get("high_risk_severity", HIGH_RISK_SEVERITY)),
        "categories": data.get("categories") or {},
        "rules": rules,
    }
    return json.dumps(payload, indent=1, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="Exit 1 if the JSON is out of date.")
    args = parser.parse_args(argv)
    text = export()
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current.replace("\r\n", "\n") != text:
            print(f"{OUT.relative_to(ROOT)} is out of date; run scripts/export_app_data.py")
            return 1
        print(f"{OUT.relative_to(ROOT)} is up to date")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(json.loads(text)['rules'])} rules)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

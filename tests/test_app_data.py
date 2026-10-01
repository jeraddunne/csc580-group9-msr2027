"""The team app's rules.json must match rules/skill_risk_rules.yaml."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _export():
    spec = importlib.util.spec_from_file_location(
        "export_app_data", ROOT / "scripts" / "export_app_data.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_committed_rules_json_is_current():
    committed = (ROOT / "app" / "data" / "rules.json").read_text(encoding="utf-8")
    assert committed.replace("\r\n", "\n") == _export().export(), (
        "app/data/rules.json is out of date; run python scripts/export_app_data.py"
    )


def test_exported_examples_behave_as_in_python():
    data = json.loads(_export().export())
    assert data["rules"], "no active rules exported"
    for rule in data["rules"]:
        flags = re.MULTILINE | (re.IGNORECASE if "i" in rule["flags"] else 0)
        patterns = [re.compile(p, flags) for p in rule["patterns"]]
        for text in rule["match"]:
            assert any(p.search(text) for p in patterns), (rule["id"], text)
        for text in rule["no_match"]:
            assert not any(p.search(text) for p in patterns), (rule["id"], text)

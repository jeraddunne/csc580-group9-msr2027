"""Every rule has a rule card (#95), and docs/research/RULE_CATALOG.md matches the rule file."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from msr_pipeline.skill_risk import read_rule_file

ROOT = Path(__file__).resolve().parents[1]
DATA = read_rule_file(ROOT / "rules" / "skill_risk_rules.yaml")
ACTIVE = [r for r in DATA["rules"] if str(r.get("status", "active")) == "active"]


def _catalog():
    spec = importlib.util.spec_from_file_location(
        "make_rule_catalog", ROOT / "scripts" / "make_rule_catalog.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("raw", ACTIVE, ids=[r["id"] for r in ACTIVE])
def test_every_rule_has_a_card(raw):
    cat = _catalog()
    assert raw.get("title"), f"{raw['id']} needs a title"
    assert len(raw.get("description", "")) >= 80, f"{raw['id']} needs a problem description"
    refs = raw.get("references") or []
    assert refs, f"{raw['id']} needs at least one reference"
    for ref in refs:
        assert {"id", "title", "url", "kind", "relation"} <= ref.keys(), ref
        assert ref["url"].startswith("https://"), ref["url"]
        assert ref["kind"] in cat.KINDS, ref["kind"]


def test_catalog_page_is_up_to_date():
    cat = _catalog()
    page = (ROOT / "docs" / "research" / "RULE_CATALOG.md").read_text(encoding="utf-8")
    assert page.replace("\r\n", "\n") == cat.render(DATA), "run scripts/make_rule_catalog.py"


def test_examples_with_backticks_keep_their_fence():
    cat = _catalog()
    block = cat._fence("```bash\nnpm test\n```")
    assert block.startswith("````text\n") and block.endswith("\n````")
